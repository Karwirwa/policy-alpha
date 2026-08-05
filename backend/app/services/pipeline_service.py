import os
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.pipeline_repository import PipelineRepository
from app.repositories.crawl_repository import CrawlRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.services.evidence_builder import EvidenceIngestionService, EvidenceBuilder
from app.services.opportunity_scoring import OpportunityScoringService
from app.connectors import KenyaConnector, USConnector, UKConnector, CanadaConnector
from app.models.document import Document
from app.models.processing import ProcessingJob
from app.services.document_parser import EvidenceDocument

logger = logging.getLogger("PipelineService")

# Store raw downloaded files under backend/data/raw/ (deterministic location)
RAW_STORAGE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
os.makedirs(RAW_STORAGE, exist_ok=True)


class ProcessingService:
    def __init__(self, db: Session, max_retries: int = 3):
        self.db = db
        self.repo = PipelineRepository(db)
        self.crawl_repo = CrawlRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.opp_repo = OpportunityRepository(db)
        self.ingestion = EvidenceIngestionService(self.evidence_repo)
        self.scorer = OpportunityScoringService(db)
        self.max_retries = max_retries
        # connector instances
        self.connectors = {
            "KEN": KenyaConnector(),
            "USA": USConnector(),
            "GBR": UKConnector(),
            "CAN": CanadaConnector(),
        }

    def _find_connector_for_document(self, document: Document):
        name = (document.connector_name or "").lower()
        if "kenya" in name or "kenya" in (document.source_reference or "").lower():
            return self.connectors.get("KEN")
        if "usa" in name or "us" in name or "federal" in (document.source_reference or "").lower():
            return self.connectors.get("USA")
        if "uk" in name or "govi" in (document.source_reference or "").lower() or "gov.uk" in (document.source_reference or ""):
            return self.connectors.get("GBR")
        if "canada" in name or "gc.ca" in (document.source_reference or "").lower():
            return self.connectors.get("CAN")
        # fallback: try to infer from document id
        if document.id and document.id.startswith("kenya"):
            return self.connectors.get("KEN")
        return None

    def _write_raw_file(self, document_id: str, content: str) -> str:
        safe_name = document_id.replace("/", "_")
        path = os.path.join(RAW_STORAGE, f"{safe_name}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path

    def process_document(self, document_id: str) -> ProcessingJob:
        # create job
        job = ProcessingJob(document_id=document_id, status="running", stage="download", start_time=datetime.now(timezone.utc))
        job = self.repo.create_job(job)

        try:
            # load document
            document = self.db.get(Document, document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found in DB")

            connector = self._find_connector_for_document(document)
            if not connector:
                raise ValueError(f"No connector found for document {document_id}")

            # Stage: download
            job.stage = "download"
            self.repo.update_job(job)
            gov_doc = connector.download(
                type("GDoc", (), {"document_id": document.id, "country_code": document.id.split("_")[0] if document.id else "", "source_url": document.source_reference, "document_type": "unknown", "language": "en", "connector_name": document.connector_name, "raw_content": ""})
            )

            # Stage: store raw file
            job.stage = "store_raw"
            self.repo.update_job(job)
            raw_content = gov_doc.raw_content or ""
            raw_path = self._write_raw_file(document_id, raw_content)

            # Stage: extract_text
            job.stage = "extract_text"
            self.repo.update_job(job)
            # For now assume raw_content is already text
            extracted_text = raw_content

            # Stage: extract_metadata (parse)
            job.stage = "extract_metadata"
            self.repo.update_job(job)
            parsed = connector.parse(gov_doc)

            # Stage: create_document (update DB record)
            job.stage = "create_document"
            self.repo.update_job(job)
            # update document metadata/description
            document.description = document.description or f"Ingested from {document.source_reference}"
            self.db.add(document)
            self.db.commit()

            # Stage: extract_evidence
            job.stage = "extract_evidence"
            self.repo.update_job(job)
            ev_doc = EvidenceDocument(
                document_id=document.id,
                country_id=document.id if document.id else "",
                raw_text=extracted_text,
                source_reference=document.source_reference,
                connector_name=document.connector_name,
                title=document.name,
                metadata=parsed.metadata if hasattr(parsed, "metadata") else {},
            )
            evidence = self.ingestion.ingest(ev_doc)

            # Stage: calculate_opportunity_scores
            job.stage = "calculate_scores"
            self.repo.update_job(job)
            if evidence and evidence.company_id:
                try:
                    opp, breakdowns = self.scorer.score_company(evidence.company_id)
                    # persist via OpportunityRepository
                    self.opp_repo.save_score(opp, breakdowns)
                except Exception as e:
                    logger.exception("Scoring failed for company %s: %s", evidence.company_id, e)

            # Stage: update_knowledge_graph (relationships already built during ingestion)
            job.stage = "update_knowledge_graph"
            self.repo.update_job(job)

            # finish
            job.status = "completed"
            job.stage = "done"
            job.end_time = datetime.now(timezone.utc)
            self.repo.update_job(job)
            return job

        except Exception as e:
            logger.exception("Processing failed for document %s: %s", document_id, e)
            job.error = {"error": str(e)}
            job.retries += 1
            job.status = "failed"
            job.end_time = datetime.now(timezone.utc)
            self.repo.update_job(job)
            return job

    def retry_job(self, job_id: int) -> ProcessingJob:
        job = self.repo.get_job(job_id)
        if not job:
            raise ValueError("Job not found")
        if job.retries >= self.max_retries:
            raise ValueError("Max retries exceeded")
        # Record that a retry is being attempted on the original job for observability
        try:
            job.retries = (job.retries or 0) + 1
        except Exception:
            job.retries = 1
        job.status = "retrying"
        job.error = None
        job.start_time = datetime.now(timezone.utc)
        self.repo.update_job(job)
        # Attempt processing again for the same document id (creates a fresh ProcessingJob)
        return self.process_document(job.document_id)
