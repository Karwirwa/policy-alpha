# Vertical Slice Validation (Milestone 2)

Purpose
-------
This document explains how the Milestone 2 vertical slice is validated using a
single real (sample) government document. The goal is to prove the core
pipeline: ingestion -> storage -> retrieval -> analysis interface (mock).
No AI or vector search is included in this milestone.

Pipeline
--------
1. sample-data/sample_infrastructure_bill.txt (plain text)
2. backend/scripts/ingest_sample.py
   - Parses the text deterministically and stores Document and DocumentChunk
     records. Links the Document to a GovernmentSource and Country.
   - Creates Company and Bill records (for the sample) and Mention links so
     retrieval can demonstrate mention resolution.
3. backend/scripts/query_sample.py
   - Retrieves the stored document and its chunks using RetrievalService.
   - Prints document metadata, chunks, detected companies and bills.
   - Calls the AnalysisService placeholder and prints the mocked response.

Expected Output (when run locally)
----------------------------------
Running ingest:
- ✓ Country created/found
- ✓ Source created/found
- ✓ Document stored
- ✓ Number of chunks: N

Running query:
- Title: <document title>
- Government Source: <source name>
- Publication Date: <date or None>
- Document Chunks: list of chunk positions and previews
- Detected Companies: list of companies (from mentions)
- Detected Bills: list of bills (from mentions)
- Mocked Analysis Result: <printed dict from AnalysisService.analyze_document>

Files Used
----------
- sample-data/sample_infrastructure_bill.txt
- backend/scripts/ingest_sample.py
- backend/scripts/query_sample.py
- backend/app/services/document_parser.py
- backend/app/services/document_ingestion.py
- backend/app/services/retrieval.py
- backend/app/services/analysis.py
- backend/app/models/entities.py

Success Criteria
----------------
- The sample document is persisted in the database.
- Document chunks are created and retrievable.
- Companies and bills mentioned in the sample are stored and retrievable via mentions.
- The AnalysisService placeholder executes and returns the mocked response.
- No runtime errors during ingestion or retrieval.

Future Improvements
-------------------
- Replace the AnalysisService placeholder with an LLM-backed implementation that
  uses retrieved chunks as evidence and returns structured findings (kept out
  of scope for this milestone).
- Improve deterministic entity extraction in the parser and/or add optional
  enrichment workers.
- Add automated integration tests that run the scripts against a test DB.

This validation demonstrates the architecture before any AI reasoning is added.
Preserving a clear separation between retrieval (database) and reasoning (AI)
keeps the system auditable, deterministic, and easier to evolve.
