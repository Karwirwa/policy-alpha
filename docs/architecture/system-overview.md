# Policy Alpha System Overview

## Vision

Policy Alpha is an evidence-first investment intelligence platform, not an AI chatbot. Its primary mission is to transform structured and unstructured government document disclosures into reliable, explainable evidence that powers investment analysis, portfolio monitoring, and company intelligence. The platform is designed to preserve provenance, maintain deterministic behavior, and keep complex reasoning separate from evidence extraction.

## Core Principles

- Country agnostic
  - The platform supports national document sources through a plugin-based connector layer.
  - New countries can be added without changing the core evidence engine.

- Evidence first
  - Evidence is the canonical knowledge object.
  - All downstream systems consume structured evidence rather than raw text or opaque predictions.

- Explainable AI
  - Evidence quality is computed deterministically and transparently.
  - Metadata and provenance are captured at every stage to support auditability.

- Modular architecture
  - Responsibilities are separated across connectors, parsers, resolvers, extractors, repositories, and APIs.
  - Each module has a single responsibility and can evolve independently.

- Plugin-based country expansion
  - Country connectors expose a standardized lifecycle and a shared canonical document model.
  - New connectors are added by implementing the connector interface, not by redesigning the core engine.

- Incremental intelligence
  - The platform builds intelligence gradually: document ingestion, evidence extraction, metadata enrichment, and relationship modeling occur before any AI-driven reasoning.
  - Future intelligence layers are added on top of an established evidence foundation.

## End-to-End System Flow

1. Government Sources
   - National gazettes, parliamentary records, budget announcements, procurement notices, and other public government disclosures.

2. Country Connectors
   - Plugin-based connectors discover, download, parse, and normalize government documents into a canonical `GovernmentDocument` model.
   - Connectors provide health reporting and metadata normalization without performing evidence generation.

3. Document Pipeline
   - The document pipeline parses raw document content into structured form.
   - It extracts titles, summaries, and normalized metadata while preserving source references.

4. Evidence Intelligence
   - The Evidence Engine resolves entities, extracts evidence records, calculates evidence strength, and detects duplicates.
   - Evidence becomes the canonical knowledge object stored with provenance in the database.

5. Knowledge Repository
   - Structured evidence is persisted in a repository that supports retrieval by document, company, agency, and keyword.
   - The repository is the source of truth for downstream intelligence.

6. Relationship Graph Layer
   - Evidence records reference canonical entities such as companies, agencies, projects, budgets, tenders, countries, and documents.
   - This relational model prepares the platform for future graph-based traversal and knowledge discovery.

7. Retrieval Engine
   - Consumers query the knowledge repository and evidence repository for relevant evidence records.
   - Retrieval is deterministic and based on structured entity links and normalized metadata.

8. Context Builder
   - A context builder assembles evidence, entity relationships, and metadata into a coherent package for reasoning.
   - It preserves provenance and maintains explainability.

9. AI Investment Engine
   - The AI Investment Engine consumes evidence-based context to support investment thesis evaluation and portfolio intelligence.
   - It does not generate evidence; it operates on evidence that has already been extracted and validated.

10. Investment Thesis
    - Structured evidence informs investment thesis development, risk assessment, and opportunity scoring.

11. Portfolio Intelligence
    - The platform monitors portfolio exposure, keyword signals, and entity relationships using evidence-derived insights.

12. Outcome Learning
    - Outcome learning captures real-world results and feedback to improve future evidence curation and intelligence workflows.

## Responsibilities of Each Layer

- Country Connectors
  - Own: document discovery, download, parsing, normalization, connector health reporting.
  - Do NOT own: evidence extraction, entity resolution, confidence or evidence strength scoring, portfolio reasoning.

- Document Pipeline
  - Own: parsing raw content, extracting titles and summaries, normalizing document metadata.
  - Do NOT own: entity resolution, evidence persistence, duplicate detection, intelligence reasoning.

- Evidence Intelligence
  - Own: entity resolution, evidence extraction, duplicate detection, evidence strength calculation, provenance capture.
  - Do NOT own: raw document collection, external connector integrations, AI-driven investment recommendations.

- Knowledge Repository
  - Own: storing structured evidence and normalized entity relationships.
  - Do NOT own: real-time alerting, external notifications, or decision automation.

- Relationship Graph Layer
  - Own: explicit links between evidence and canonical entities.
  - Do NOT own: graph database implementation in the current milestone.

- Retrieval Engine
  - Own: deterministic evidence lookup by entities, documents, and keywords.
  - Do NOT own: semantic search or large-scale AI retrieval at this stage.

- Context Builder
  - Own: packaging evidence and metadata into a coherent input for reasoning.
  - Do NOT own: evidence generation or raw document parsing.

- AI Investment Engine
  - Own: applying models and rules to evidence-derived context for investment intelligence.
  - Do NOT own: evidence extraction or source provenance.

## Future Expansion

- Additional countries
  - Add country connectors by implementing the standardized connector lifecycle and returning `GovernmentDocument` objects.
  - No core evidence engine changes are required.

- Additional connectors
  - Support new government sources by adding connector plugins and registering them with the connector package.
  - Health reporting and capability metadata ensure consistent operational visibility.

- Additional parsers
  - Introduce specialized document parsers that feed into the same document pipeline and evidence extractor.
  - Parsing improvements remain isolated from evidence persistence.

- Additional AI models
  - Add new reasoning layers on top of the canonical evidence repository.
  - Models consume evidence and context rather than raw text, preserving transparency and explainability.

## Guiding Rule

Every architectural decision should strengthen the evidence layer before adding intelligence.

This document is the north star for Policy Alpha contributors and is intended to ensure the platform remains evidence-first, explainable, and extendable as it grows.