# Evidence Intelligence Engine

## Purpose

The Evidence Intelligence Engine converts parsed government documents into structured evidence that can be linked to companies, agencies, projects, budgets, and procurement records. It is designed to support research workflows such as portfolio monitoring, keyword tracking, company intelligence, and investment thesis evaluation without providing investment advice.

## Architecture

The Evidence Engine is built as a deterministic extraction and normalization layer inside Policy Alpha. It uses the existing backend patterns for services, repositories, and database models rather than introducing new AI reasoning or learning components.

Architecture components:

- Document Parser: extracts title, summary, and normalized document fields from raw text.
- Entity Resolution Service: employs a resolver plugin registry to normalize and link company names, agencies, ministries, departments, projects, budgets, procurement notices, and countries.
- Metadata Extractor: tokenizes, normalizes, and deduplicates document keywords and detected entities into metadata fields.
- Evidence Extractor: converts parsed documents, metadata, and entity matches into normalized Evidence objects.
- Evidence Strength Calculator: computes a deterministic evidence strength score for evidence.
- Evidence Builder: orchestrates the pipeline without embedding business logic.
- Evidence Repository: persists evidence records, detects duplicate documents by hash, and exposes retrieval methods.
- Evidence API: read-only endpoints for retrieving structured evidence by company, agency, country, document, or keyword search.

## Responsibilities

The Evidence Engine is responsible for:

- ingesting raw government documents as evidence artifacts.
- extracting structured document attributes deterministically.
- converting document keywords into normalized metadata.
- resolving entity names to canonical IDs and names.
- detecting duplicate documents using deterministic document hashes.
- calculating deterministic evidence strength.
- recording provenance through `source_reference` and `extracted_at`.
- storing evidence in the structured database.
- exposing read-only retrieval APIs.

It is not responsible for investment advice, portfolio tracking, AI-generated summaries, watchlist alerts, or investment reasoning.

## Pipeline

```text
Document Source
    ↓
Document Parser
    ↓
Entity Resolution Service
    ↓
Metadata Extractor
    ↓
Evidence Extractor
    ↓
Evidence Strength Calculator
    ↓
Evidence Repository
    ↓
Database
    ↓
Evidence API
``` 

### Pipeline details

- - Document Parser: identifies the document title and summary and preserves raw text, page number, section, and source reference.
- Entity Resolution: performs exact, case-insensitive, and alias-based matching for companies, agencies, ministries, departments, projects, budgets, procurement notices, and countries.
- Evidence Extractor: converts parsed documents and entity matches into a normalized Evidence object.
- Evidence Strength Calculator: computes deterministic evidence strength scores using entity match quality, document completeness, source quality, and supporting references.
- Evidence Builder: orchestrates the pipeline without embedding business logic.
- Evidence Repository: implements persistent create and query operations for evidence.
## Evidence lifecycle

Evidence documents include a deterministic `document_hash`, optional `connector_name`, and extracted metadata fields such as `extracted_keywords`, `normalized_keywords`, and `detected_entities`.

The repository uses the document hash to detect duplicates and skip duplicate insertions.


Evidence flows through the following lifecycle:

1. A raw government document is represented as `EvidenceDocument` with source metadata.
2. The parser produces a normalized `ParsedDocument`.
3. The entity resolver maps text to canonical entity IDs and names.
4. The metadata extractor tokenizes and normalizes document keywords, removes duplicates, and records detected entities.
5. The evidence extractor generates a normalized `Evidence` object, includes metadata fields, and computes a deterministic document hash.
6. The evidence builder calculates evidence strength and sends the evidence to the repository.
7. The evidence repository skips insertion for duplicate `document_hash` values.
8. API clients retrieve evidence using read-only endpoints by company, agency, country, document, or keyword.

## Entity resolution strategy

Entity resolution is intentionally deterministic and rule-based and is implemented as a plugin architecture:

- Resolver plugins encapsulate entity-specific matching logic.
- A shared `ResolverRegistry` executes all registered resolvers.
- Future country connectors may register additional resolvers without modifying existing code.
- Exact match uses normalized text.
- Case-insensitive matching.
- Alias matching for common synonyms and variations.
- Document-level fallback from title to full raw text.

The resolver currently supports:

- companies (e.g. "Bamburi" → "Bamburi Cement PLC")
- agencies and ministries (e.g. "Ministry of Roads" → "State Department for Roads")
- departments (e.g. "Department of Roads" → "State Department for Roads")
- projects (e.g. "Tana River Irrigation Project")
- budget references and procurement notices.

Fuzzy matching, machine learning, and LLM-based entity inference are postponed for later milestones.

## Evidence strength scoring

The evidence strength is a deterministic composite of:

- Entity match quality (40%): average score of resolved entities.
- Document completeness (30%): normalized by raw text length, capped at 1.0.
- Linked entity count (20%): fraction of expected entity links present.
- Source quality (10%): full score for a populated source reference, half for missing source references.

The score is rounded to three decimal places and constrained to the range [0.0, 1.0].

## Future improvements

Future milestone work may include:

- richer entity alias catalogs and fuzzy matching.
- dedicated agency, company, project, and budget entity tables.
- advanced search beyond keyword matching.
- stronger provenance through raw document storage and versioning.
- end-to-end ingestion flows from country connectors and document services.
