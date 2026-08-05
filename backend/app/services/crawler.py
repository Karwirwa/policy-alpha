import threading
import time
import logging
from datetime import datetime, timezone
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from app.connectors import KenyaConnector, USConnector, UKConnector, CanadaConnector
from app.connectors.models import GovernmentDocument
from app.repositories.crawl_repository import CrawlRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.services.evidence_builder import EvidenceIngestionService
from app.services.document_parser import EvidenceDocument
from app.models.crawl import CrawlRun

logger = logging.getLogger("Crawler")


class CrawlerJob:
    def __init__(self, country_code: Optional[str] = None):
        self.country_code = country_code
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.documents_found = 0
        self.new_documents = 0
        self.errors: List[str] = []
        self.status = "pending"


class CrawlerManager:
    """Orchestrates connector discovery and ingestion into the Evidence repository.

    Accepts a SQLAlchemy Session and optionally an EvidenceRepository instance. If an
    EvidenceRepository is provided it will be used for ingestion (useful for testing
    or for sharing a repository instance); otherwise a repository is constructed from
    the session.
    """

    def __init__(self, db: Session, evidence_repo: EvidenceRepository | None = None):
        self.db = db
        self.crawl_repo = CrawlRepository(db)
        # Allow injection of an EvidenceRepository for testability and reuse
        self.evidence_repo = evidence_repo or EvidenceRepository(db)
        self.ingestion_service = EvidenceIngestionService(self.evidence_repo)
        # connector instances (deterministic, no external network calls in placeholders)
        self.connectors = {
            "KEN": KenyaConnector(),
            "USA": USConnector(),
            "GBR": UKConnector(),
            "CAN": CanadaConnector(),
        }

    def _map_country_id(self, code: str) -> str:
        return f"country_{code.lower()}"

    def run_country(self, country_code: str) -> CrawlJob | dict:
        job = CrawlerJob(country_code=country_code)
        job.start_time = datetime.now(timezone.utc)
        job.status = "running"

        run = self.crawl_repo.create(
            CrawlRun(
                country_code=country_code,
                start_time=job.start_time,
                status=job.status,
            )
        )

        connector = self.connectors.get(country_code)
        if not connector:
            msg = f"No connector registered for country {country_code}"
            logger.error(msg)
            job.errors.append(msg)
            job.status = "failed"
            run.status = job.status
            run.end_time = datetime.now(timezone.utc)
            run.duration_seconds = (run.end_time - run.start_time).total_seconds()
            run.errors = {"errors": job.errors}
            self.crawl_repo.update(run)
            return {"error": msg}

        try:
            discovered = connector.discover()
        except Exception as e:
            logger.exception("Error during discovery for %s", country_code)
            job.errors.append(str(e))
            discovered = []

        job.documents_found = len(discovered)

        for doc in discovered:
            try:
                downloaded = connector.download(doc)
                parsed = connector.parse(downloaded)
                normalized = connector.normalize(parsed)

                ev_doc = EvidenceDocument(
                    document_id=normalized.document_id,
                    country_id=self._map_country_id(normalized.country_code),
                    raw_text=normalized.raw_content or "",
                    source_reference=normalized.source_url,
                    connector_name=normalized.connector_name,
                    title=normalized.title,
                    page_number=None,
                    section=None,
                    metadata=normalized.metadata,
                )

                created = self.ingestion_service.ingest(ev_doc)
                if created:
                    job.new_documents += 1
            except Exception as e:
                logger.exception("Failed to process document %s: %s", doc.document_id, e)
                job.errors.append(f"{doc.document_id}: {e}")

        job.end_time = datetime.now(timezone.utc)
        job.duration_seconds = (job.end_time - job.start_time).total_seconds()
        job.status = "completed" if not job.errors else "completed_with_errors"

        # update run record
        run.end_time = job.end_time
        run.duration_seconds = job.duration_seconds
        run.documents_found = job.documents_found
        run.new_documents = job.new_documents
        run.errors = {"errors": job.errors} if job.errors else None
        run.status = job.status
        self.crawl_repo.update(run)

        result = {
            "country_code": country_code,
            "documents_found": job.documents_found,
            "new_documents": job.new_documents,
            "errors": job.errors,
            "status": job.status,
            "duration_seconds": job.duration_seconds,
        }

        # return a deterministic, serializable result
        return result

    def run_manual(self, document: Union[GovernmentDocument, EvidenceDocument]) -> dict:
        """Ingest a single supplied document (manual submission).

        Accepts either a GovernmentDocument from a connector or an EvidenceDocument
        and ingests it into the EvidenceRepository while recording a CrawlRun.
        This method makes no external network calls and performs processing synchronously
        to remain deterministic and testable.
        """
        job = CrawlerJob(country_code=(getattr(document, "country_code", None) or getattr(document, "country_id", None)))
        job.start_time = datetime.now(timezone.utc)
        job.status = "running"

        run = self.crawl_repo.create(
            CrawlRun(
                country_code=(getattr(document, "country_code", None) or getattr(document, "country_id", None)),
                start_time=job.start_time,
                status=job.status,
            )
        )

        try:
            # If a GovernmentDocument was supplied, attempt to normalize it using
            # its connector if available; otherwise use provided raw_content.
            if isinstance(document, GovernmentDocument):
                connector = self.connectors.get(document.country_code)
                gov_doc = document
                try:
                    # Prefer to let connector perform parse/normalize if available
                    if connector:
                        downloaded = connector.download(gov_doc)
                        parsed = connector.parse(downloaded)
                        normalized = connector.normalize(parsed)
                    else:
                        normalized = gov_doc
                except Exception as e:
                    logger.exception("Error normalizing manual GovernmentDocument: %s", e)
                    # proceed with whatever content we have
                    normalized = gov_doc

                ev_doc = EvidenceDocument(
                    document_id=normalized.document_id,
                    country_id=self._map_country_id(normalized.country_code) if normalized.country_code else self._map_country_id("UNK"),
                    raw_text=normalized.raw_content or "",
                    source_reference=normalized.source_url,
                    connector_name=normalized.connector_name,
                    title=normalized.title,
                    page_number=None,
                    section=None,
                    metadata=normalized.metadata,
                )
            else:
                # Already an EvidenceDocument
                ev_doc = document

            created = None
            try:
                created = self.ingestion_service.ingest(ev_doc)
                if created:
                    job.new_documents = 1
            except Exception as e:
                logger.exception("Failed to ingest manual document %s: %s", getattr(ev_doc, "document_id", "<unknown>"), e)
                job.errors.append(str(e))

        except Exception as e:
            logger.exception("Unexpected error in run_manual: %s", e)
            job.errors.append(str(e))

        job.end_time = datetime.now(timezone.utc)
        job.duration_seconds = (job.end_time - job.start_time).total_seconds()
        job.status = "completed" if not job.errors else "completed_with_errors"

        run.end_time = job.end_time
        run.duration_seconds = job.duration_seconds
        run.documents_found = 1
        run.new_documents = job.new_documents
        run.errors = {"errors": job.errors} if job.errors else None
        run.status = job.status
        self.crawl_repo.update(run)

        return {
            "document_id": getattr(ev_doc, "document_id", None),
            "created": True if created else False,
            "errors": job.errors,
            "status": job.status,
            "duration_seconds": job.duration_seconds,
        }

    def run_full_crawl(self) -> List[dict]:
        results = []
        for code in list(self.connectors.keys()):
            results.append(self.run_country(code))
        return results


class CrawlerScheduler:
    """Simple in-process scheduler for periodic crawling."""

    def __init__(self, db: Session, interval_seconds: int = 86400):
        self.db = db
        self.manager = CrawlerManager(db)
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="CrawlerScheduler")
        self._thread.start()
        logger.info("CrawlerScheduler started with interval %s seconds", self.interval_seconds)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            logger.info("CrawlerScheduler executing full crawl")
            try:
                self.manager.run_full_crawl()
            except Exception:
                logger.exception("Error in scheduled crawl")
            # sleep until next run or until stopped
            stopped = self._stop_event.wait(self.interval_seconds)
            if stopped:
                break

    def run_single_country_now(self, country_code: str) -> dict:
        return self.manager.run_country(country_code)

    def run_once(self) -> List[dict]:
        return self.manager.run_full_crawl()
