# Knowledge Graph Architecture

## Purpose

The knowledge graph architecture transforms Policy Alpha from an evidence repository into a relationship-driven intelligence platform. It does this using relational models and SQLAlchemy relationships rather than an external graph database. The graph layer makes entity connections explicit, deterministic, and available for traversal by downstream analytics and intelligence services.

## Architecture

The knowledge graph layer sits on top of the Evidence Engine and canonical entity models:

- Evidence records capture extracted facts from government documents.
- Canonical entities represent companies, agencies, projects, budgets, tenders, countries, and documents.
- Entity relationships encode deterministic connections between those entities.

The relationship engine is built using:

- canonical entity models with alias and descriptive metadata
- an `EntityRelationship` model for typed relationships
- a relationship builder that derives edges from evidence
- repositories for storing and querying relationships
- a graph service for traversing entity networks
- read-only APIs for graph exploration

## Relationship model

`EntityRelationship` stores typed links between entities:

- `source_entity_type`
- `source_entity_id`
- `relationship_type`
- `target_entity_type`
- `target_entity_id`
- `evidence_id`
- `confidence`
- `created_at`

Relationship types are implemented as a Python `Enum`:

- `AWARDED`
- `FUNDED_BY`
- `MANAGED_BY`
- `LOCATED_IN`
- `MENTIONS`
- `SUPPLIES`

These relationships are deterministic and grounded in evidence records. Duplicate relationships are prevented when the same source, target, type, and evidence are already present.

## Traversal examples

### Company network

`GET /api/v1/graph/company/{name}` returns a company node and its connected entities, such as:

- `AWARDED` → Tender
- `SUPPLIES` → Project

### Agency network

`GET /api/v1/graph/agency/{name}` returns an agency node and its connected entities, such as:

- `LOCATED_IN` → Country
- `MANAGED_BY` ← Budget

### Project network

`GET /api/v1/graph/project/{name}` returns a project node and its connected entities, such as:

- `MENTIONS` → Company

### Budget network

`GET /api/v1/graph/budget/{name}` returns a budget node and its connected entities, such as:

- `FUNDED_BY` ← Tender
- `MANAGED_BY` → Agency

Each graph response includes supporting evidence pointers so consumers can trace relationships back to the underlying source documents.

## Future expansion

The relationship architecture is designed for incremental growth:

- Add new relationship types by extending the `RelationshipType` enum.
- Add new deterministic relationship rules in the `RelationshipBuilder` without changing existing evidence extraction.
- Add new graph endpoints by extending the `GraphService` and API router.
- Add new canonical entity types by introducing models and updating the entity type mappings.

This approach keeps the evidence layer stable while enabling richer relationship intelligence on top of the same deterministic data foundation.
