# Vertical Slice MVP (Milestone 3)

Purpose
-------
This document describes the architecture and components for the first complete
vertical slice of Policy Alpha: a deterministic, database-first pipeline that
supports later AI reasoning.

Pipeline overview
-----------------
1. Parser: converts structured government data (JSON) into normalized domain payloads.
2. Repositories: simple CRUD access for Budget, Project, Company entities.
3. Retrieval: SQL-based retrieval service to fetch companies, projects and budgets.
4. Context Builder: assembles a compact, evidence-linked context for a company.
5. AI Service: receives built context and produces a grounded, evidence-citing analysis.
6. API: HTTP endpoint to request company analysis (POST /api/v1/analyze/company).

Why this design
----------------
- Separation of concerns: parsers, repositories, retrieval and reasoning are
  isolated to make auditing and testing straightforward.
- Database-first: all facts are persisted and retrieval is the single source of
  truth for downstream reasoning components.
- Pluggable AI: AI Service accepts context and returns deterministic outputs
  today; an LLM can be inserted later with minimal changes to surrounding
  components.

How this supports future features
---------------------------------
- RAG/embeddings/vector databases can be added inside the retrieval/context
  layer without changing the API contract used by the AI Service.
- Multi-country ingestion and connectors are parsers and seeders — they do
  not affect analysis or retrieval contracts.
- Background workers and event buses can be introduced to enrich data
  asynchronously while keeping the synchronous API behavior unchanged.

Components
----------
- app/services/parser_service.py — parse and validate JSON budget files.
- app/repositories/* — BudgetRepository, ProjectRepository, CompanyRepository.
- app/services/retrieval_service.py — SQL-based retrieval helpers.
- app/services/context_builder.py — assemble structured context for analysis.
- app/services/ai_service.py — deterministic, grounded analysis interface.
- app/api/analyze.py — API endpoint exposing company analysis.

Constraints followed
-------------------
No AI model calls, embeddings, vector DBs, notifications, background jobs, or
additional domain entities were added at this stage. The architecture is kept
simple to validate the end-to-end flow from government data to grounded
analysis output.
