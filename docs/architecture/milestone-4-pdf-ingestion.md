# Milestone 4 — PDF Ingestion and Evidence Preservation

Purpose
-------
Milestone 4 extends the vertical slice to accept government PDF documents and
extract structured evidence (page, section, paragraph) which is persisted to
the database alongside domain entities. This preserves traceability and
supports grounded AI reasoning later.

Overview
--------
1. Document extractor (app/services/document_extractor.py)
   - Uses pdfplumber to read PDFs page-by-page
   - Heuristically detects headings and sections
   - Preserves page numbers and paragraph boundaries
2. Parser updates (app/services/parser_service.py)
   - Accepts extracted PDF structure and converts to budget/project payloads
   - Attaches evidence: page, section index, paragraph index for each extracted item
3. Database changes
   - Budget and Project entities now include evidence fields linking to the
     source Document and specific page/section/paragraph
   - These fields allow later analysis to cite exact locations in source PDFs
4. Ingest script (backend/scripts/ingest_pdf.py)
   - Extracts PDF -> prepares payload -> stores Document, Budget, Project
   - Adds evidence fields when inserting records

Why evidence matters
--------------------
Storing page/section/paragraph references lets the analysis layer answer
questions like "Why are you saying Bamburi benefits?" with precise citations
(e.g., "Page 47, 2026 Budget, Infrastructure Allocation: KES 18.5B"). This
turns the system from an AI demo into a professional intelligence platform.

Operational notes
-----------------
- The extractor is deterministic and contains no AI.
- For simplicity, the ingest script performs pragmatic ALTER TABLE statements
  to add evidence columns when missing. In production, these changes should be
  managed via Alembic migrations.
- pdfplumber is added to backend/requirements.txt; ensure the environment
  installs it before running ingest_pdf.py.

Next steps
----------
- Improve heading/section detection heuristics for different government
  document styles and languages.
- Add automated integration tests that ingest a known PDF and assert evidence
  fields and cited text snippets.
- Implement UI or API endpoints to fetch document excerpts by evidence
  pointers (document id, page, section, paragraph).

This milestone preserves the architecture rules: API -> Services -> Repositories -> Database.
AI is still a separate layer that consumes evidence-rich context built by the
context builder. The result is a traceable, auditable intelligence pipeline.
