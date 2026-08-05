# Knowledge Graph Roadmap

## Purpose

This document describes the relational preparation for a future Policy Alpha knowledge graph. The goal is to make the current Evidence Intelligence Engine explicitly reference canonical entities in the relational model while avoiding any graph database dependency.

## Relationship Model

The Evidence layer now acts as a bridge between parsed documents and canonical entities.

Entities involved:

- Evidence
- Document
- Country
- Agency
- Company
- Project
- Budget
- Tender

Each Evidence record contains nullable foreign keys to these canonical entities. This makes the data model ready for a graph-like representation without introducing a graph database.

### Evidence relationships

- Evidence → Document
- Evidence → Country
- Evidence → Agency
- Evidence → Company
- Evidence → Project
- Evidence → Budget
- Evidence → Tender

These relationships are represented in the relational schema by foreign key columns on `evidence`:

- `document_id` → `document.id`
- `country_id` → `country.id`
- `agency_id` → `agency.id`
- `company_id` → `company.id`
- `project_id` → `project.id`
- `budget_id` → `budget.id`
- `procurement_id` → `tender.id`

## Design Rationale

This preparation keeps the backend deterministic, testable, and production-oriented while making future migration to a graph architecture easier.

### Why relational preparation

- Preserves current SQL-based backend and APIs.
- Ensures canonical entities are first-class objects.
- Simplifies future translation to graph traversal semantics.
- Avoids premature commitment to a graph database implementation.

## Reasoning Flow

1. A document is parsed into evidence candidates.
2. Entity resolvers normalize and link each candidate to canonical entities.
3. The evidence extractor emits normalized evidence records with foreign keys.
4. The repository stores each evidence record in a relational database.

This flow creates a deterministic, traceable chain from raw document content to canonical entity associations.

## Future Graph Traversal Examples

The relational model supports graph-like queries in future designs. Example traversal patterns:

- Find all evidence for a company:
  - Company → Evidence
- Find all documents that mention a specific agency:
  - Agency → Evidence → Document
- Find all tenders linked to projects in a country:
  - Country → Evidence → Project → Tender
- Follow a document's provenance across entities:
  - Document → Evidence → {Company, Agency, Project, Budget, Tender}

## Next Steps

When moving toward a graph architecture, the existing foreign-key relationships can be mapped to nodes and edges:

- Node types: Document, Country, Agency, Company, Project, Budget, Tender, Evidence
- Edge types: `HAS_EVIDENCE`, `MENTIONS_COMPANY`, `MENTIONS_AGENCY`, `MENTIONS_PROJECT`, `MENTIONS_BUDGET`, `MENTIONS_TENDER`

This roadmap keeps the current implementation stable while documenting the future direction for canonical entity relationships.
