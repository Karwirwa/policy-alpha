# Milestone 2 — Summary

What was built
--------------
- Minimal domain models (Country, GovernmentSource, Document, DocumentChunk,
  Company, Bill, Mention, AIAnalysis) using UUID primary keys and a shared
  TimestampMixin.
- Repository layer for Document, Company, and Bill with create/get/list/simple_search.
- Deterministic document parser that splits raw text into chunks and extracts
  basic metadata (title, counts).
- Ingestion service that persists documents and chunks and links to a
  GovernmentSource.
- Retrieval service that exposes SQL-based retrieval: get documents, chunks,
  companies and bills mentioned in a document.
- Analysis module that provides a placeholder interface (analyze_document,
  summarize_document, explain_company) and returns mocked outputs.
- Documentation describing the purpose, scope, workflow, and success criteria
  for the vertical slice.

What remains
------------
- AI integration (LLMs for analysis, summarization, evidence citation)
- Embeddings and vector search for semantic retrieval
- Background workers for asynchronous ingestion and enrichment
- Authentication and user-facing features
- Cross-country ingestion pipelines and external source connectors

Why AI was NOT added now
------------------------
The goal of Milestone 2 is to validate the architectural assumptions: that a
database-first pipeline with deterministic retrieval can support later
reasoning layers. Adding AI now would conflate retrieval and reasoning and
could hide architectural issues. Instead the project provides clear interfaces
where AI will be integrated in future milestones.

How this validates the architecture
-----------------------------------
- Database as source-of-truth: documents and chunks are persisted and
  retrievable deterministically.
- Retrieval-before-reasoning: services expose plain-SQL retrieval expected by
  future AI components.
- Clear integration points: AnalysisService and AIAnalysis model make it
  straightforward to swap in LLM-based reasoning later while keeping stored
  evidence references.

Next steps
----------
- Iterate on chunking and evidence citation formats.
- Add a minimal AI adaptor that consumes retrieved chunks and returns
  structured findings (kept behind a feature flag).
- Implement simple integration tests for ingestion -> retrieval -> analysis.
