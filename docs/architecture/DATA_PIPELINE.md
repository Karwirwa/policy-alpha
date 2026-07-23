# Data Pipeline

## Overview

The Policy Alpha data pipeline describes how government information is collected, structured, enriched, and transformed into investment intelligence. The pipeline is designed to support evidence-based analysis of policy, procurement, budgets, legislation, and public-sector activity, with the goal of turning raw government data into actionable research for investors, analysts, and researchers.

The architecture separates ingestion, normalization, storage, retrieval, reasoning, and validation so that each stage can evolve independently and remain auditable over time.

## End-to-End Pipeline

```text
Government Sources
    ↓
Scrapers / APIs
    ↓
Raw Data Storage
    ↓
Normalization
    ↓
Structured Database
    ↓
Embeddings
    ↓
Retrieval
    ↓
Context Builder
    ↓
LLM Reasoning
    ↓
Validation
    ↓
Investment Intelligence
    ↓
API
    ↓
Frontend
```

## 1. Government Sources

Government data enters the platform from a wide range of public and institutional sources. These sources include official publications, procurement portals, parliamentary records, budget documents, gazettes, press releases, and regulatory notices.

Examples include:

- Kenya Gazette
- National Treasury
- Parliament
- PPRA
- Company filings and public corporate disclosures

These sources provide the raw material for the platform's intelligence workflows. They are not merely data feeds; they are the foundation of the system's knowledge base.

## 2. Scrapers / APIs

The ingestion layer collects information from government sources through approved interfaces, including APIs where available and structured extraction processes where necessary. In some cases, the platform may rely on scrapers or other retrieval mechanisms to obtain public documents that are not available in machine-readable form.

This stage is responsible for acquiring content in a way that preserves source identity and original form. It is a critical boundary between the external information environment and the platform's internal knowledge layer.

## 3. Raw Data Storage

All collected content should be preserved in a raw data layer before it is transformed. Raw data storage is the system's historical record of what was observed, when it was observed, and from which source it originated.

This layer preserves:

- the original document or payload,
- source metadata,
- timestamps,
- provenance,
- and any content that may later be reprocessed or reinterpreted.

Raw storage is essential because public data may be incomplete, revised, or reissued. It enables traceability and supports future re-analysis when extraction rules or business logic improve.

## 4. Normalization

Normalization is the process of converting raw content into consistent, structured representations that can be stored, linked, and analyzed. This step separates the platform's understanding of content from the raw source artifact itself.

Normalization includes standardizing fields such as:

- document type,
- issuing agency,
- publication date,
- title,
- related entities,
- budget references,
- procurement status,
- legislative identifiers,
- and sector or project associations.

Normalization is intentionally separated from AI because it is a structured data preparation function. It should be deterministic, auditable, and independent of model interpretation. In contrast, AI is used later to interpret, summarize, compare, and synthesize information rather than to define the core data structure.

## 5. Structured Database

The normalized content is stored in the structured database, where it becomes part of the platform's persistent knowledge base. The database is the system of record for entities such as government documents, agencies, budgets, bills, procurement awards, tenders, projects, sectors, companies, signals, and related relationships.

This stage creates the durable foundation for:

- document retrieval,
- relationship analysis,
- timeline construction,
- signal generation,
- and user-facing research workflows.

## 6. Embeddings

After content has been normalized and stored, the platform generates embeddings for retrieval and semantic analysis. Embeddings are vector representations of documents or chunks of content that allow the system to find semantically similar material, even when the exact wording differs.

Embeddings are generated from normalized or processed content rather than from raw, unstructured source artifacts alone. This ensures that they reflect the structured understanding of the document while remaining useful for similarity search and contextual retrieval.

Embeddings support future capabilities such as semantic search, concept clustering, and related-document discovery. They are not a replacement for the structured database but a complementary retrieval layer.

## 7. Retrieval

Retrieval selects the most relevant information for a user's request or for a given analytical workflow. It may draw from structured database records, document metadata, and embedded content representations.

Retrieval is responsible for assembling the evidence set that will later be used for reasoning. The quality of this stage strongly influences the usefulness of downstream intelligence.

For example, a question about procurement opportunities may retrieve:

- related tenders,
- linked procurement awards,
- agency information,
- company records,
- and budget or project context.

## 8. Context Builder

The Context Builder combines retrieved evidence into a coherent input for reasoning. It assembles the necessary records, relationships, and supporting context into a concise structure that can be consumed by the reasoning layer.

Its purpose is not simply to gather data, but to shape the right evidence bundle for a specific task. A good context builder ensures that downstream reasoning is grounded in relevant and manageable information rather than flooded with noise.

## 9. LLM Reasoning

The LLM reasoning stage interprets the assembled context and produces an analysis, answer, or synthesis. This is where the platform turns evidence into a useful interpretation. However, it is not the source of truth; it is a reasoning engine operating over retrieved and validated context.

Examples of reasoning tasks include:

- summarizing policy developments,
- comparing several procurement opportunities,
- explaining implications for a sector,
- identifying investment-relevant themes,
- and generating research insights from connected evidence.

## 10. Validation

Validation ensures that the output is grounded, accurate, and appropriate for use. It checks whether the reasoning is supported by the retrieved evidence and whether the result meets required quality and structure expectations.

This stage is essential because government intelligence is often high-stakes and factual precision matters. Validation may involve deterministic checks, rules-based verification, source-grounding evaluation, and consistency checks against the underlying data.

## 11. Investment Intelligence

Investment intelligence is the output of the pipeline once evidence has been processed, validated, and interpreted. This stage creates the value that users ultimately consume. Examples include:

- policy impact summaries,
- signal generation,
- opportunity tracking,
- sector risk or opportunity assessments,
- and research-ready insights.

Investment signals are created when the platform detects a meaningful development that could matter to stakeholders. For example, a new tender, budget expansion, or legislative change may be translated into a structured signal that is associated with a company, sector, project, or policy domain.

## 12. API

The API exposes the platform's capabilities to downstream clients and user interfaces. It provides access to structured records, research outputs, signals, watchlists, and other intelligence products in a consistent and governed way.

## 13. Frontend

The frontend presents the intelligence to users in a usable and accessible form. It allows users to explore policy developments, inspect supporting evidence, review generated insights, and engage with personalized workflows such as watchlists and portfolio tracking.

## How Watchlists Receive Updates

Watchlists receive updates when new or changed information becomes relevant to a tracked entity, policy theme, sector, or source. The platform can evaluate new signals against existing watchlist criteria and notify users when an item becomes more relevant or materially changed.

This creates a workflow in which users do not need to repeatedly inspect the system manually. Instead, the platform surfaces changes that matter to their areas of interest.

## Why Raw Data Is Preserved

Raw data is preserved because public sources are often incomplete, revised, or noisy. A normalized and interpreted version of the data alone is not sufficient for long-term reliability. Retaining the original material preserves provenance, traceability, and the ability to reprocess information as extraction rules or analytical needs evolve.

## Why Normalization Is Separated from AI

Normalization is separated from AI because it is a deterministic and structural operation. It should convert raw information into stable, consistent records that the system can reason over. AI is then used later to interpret, compare, and synthesize those records. This separation improves maintainability, auditability, and transparency.

## Future Scalability

The pipeline is designed to scale from a focused research platform into a broader intelligence engine. Over time, the platform can add more sources, more enrichment rules, more specialized analysis services, and more advanced retrieval workflows without redesigning the core lifecycle.

Future scalability will come from:

- expanding the ingestion layer,
- adding more structured entities and relationships,
- enriching signal generation logic,
- increasing retrieval coverage,
- and introducing additional validation and observability layers.

The architecture is intended to support growth without collapsing the distinction between evidence, interpretation, and user-facing intelligence.
