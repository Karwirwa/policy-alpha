# Milestone 2 — Vertical Slice (End-to-End Intelligence Pipeline)

Purpose
-------
This document describes the goals and minimal design for Milestone 2: a
vertical slice that proves the Policy Alpha intelligence pipeline end-to-end:

Government Document -> Parser -> Structured Data -> Database -> Retrieval -> AI Explanation with Evidence

Scope
-----
The milestone intentionally implements only the smallest set of components
required to validate the architecture. The focus is on a functioning data
pipeline from raw government text to structured storage and deterministic
retrieval. No AI reasoning is included in this milestone — analysis interfaces
are present but return mocked data.

Workflow
--------
1. Ingest a raw government document (plain text) into the parser.
2. Parser splits the text into deterministic chunks and extracts basic
   metadata (title, counts).
3. Ingestion service persists the Document and DocumentChunk records and
   links the document to a GovernmentSource.
4. Retrieval service performs SQL-based retrieval of documents, chunks,
   companies, and bills.
5. Analysis module exposes an interface for AI-powered reasoning but returns
   mocked outputs for now. This demonstrates where AI will integrate and how
   evidence (chunk ids, offsets) will be supplied.

Entities (minimal)
------------------
- Country
- GovernmentSource
- Document
- DocumentChunk
- Company
- Bill
- Mention
- AIAnalysis (placeholder to store future AI outputs)

Why a vertical slice?
---------------------
Building a small, end-to-end pipeline avoids premature optimization and
feature bloat. Validating the flow from ingestion to retrieval ensures the
system's core architecture — database-first as the source of truth and
retrieval-before-reasoning — is sound before adding complexity such as
vector search, LLMs, background workers, multi-country ingestion, or
real-time notifications.

Success criteria
----------------
- Parser deterministically splits documents into chunks and returns structured data
- Database models persist documents and chunks with UUID primary keys
- Migrations can be generated and applied successfully
- Repositories and services provide create/read/list/search operations
- Retrieval returns chunks and linked entities without errors
- Analysis interface exists and returns mocked results

Out of scope
------------
Do NOT implement in this milestone:
- AI model integration (LLMs, embeddings)
- Vector database or approximate nearest neighbor search
- Background workers or task queues
- Authentication, notifications, portfolio/watchlist features
- External API integrations
- Knowledge graph or complex domain ontology

This milestone is intentionally small so subsequent milestones can safely
plug in more sophisticated reasoning and retrieval layers on top of a
validated, working pipeline.
