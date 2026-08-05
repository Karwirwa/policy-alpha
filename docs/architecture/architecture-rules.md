# Architecture Rules

This document defines the architectural rules that every future contribution to Policy Alpha must follow. It is an engineering handbook for maintaining a clean, deterministic, evidence-first platform.

## Rules

1. Connectors never create Evidence.
   - Connectors discover, download, parse, and normalize government documents only.
   - Evidence creation is the responsibility of the Evidence Engine.

2. Parsers never access the database.
   - Parsers transform raw document content into structured metadata and document objects.
   - Database persistence is handled by repositories and services downstream.

3. AI never reads raw documents directly.
   - AI layers consume evidence and metadata, not raw text or connector payloads.
   - Raw content remains behind the evidence extraction and document pipeline.

4. All AI reasoning must originate from Evidence objects.
   - Evidence is the canonical knowledge unit for downstream intelligence and reasoning.
   - Any inference, scoring, or recommendation must be based on structured evidence data.

5. Repositories contain no business logic.
   - Repositories are data access layers only.
   - They should not perform entity resolution, scoring, or transformation behavior.

6. Services never communicate directly with external APIs unless they are connectors.
   - Only connector implementations may reach outside the platform.
   - Services must remain internal and deterministic unless routed through a connector.

7. Country-specific behavior belongs only inside connector implementations.
   - Country logic, source-specific parsing, and API integration live in connector modules.
   - Core engine code must remain country-agnostic.

8. Every new feature must fit an existing architectural layer before introducing a new one.
   - Prefer extending existing layers rather than adding new abstractions.
   - If a new layer is required, document its responsibility clearly.

9. Knowledge should always be deterministic before becoming intelligent.
   - Evidence extraction, entity resolution, scoring, and metadata normalization must be deterministic.
   - AI reasoning may be added later, but only on top of a stable evidence foundation.

10. Architecture documentation must be updated whenever a new subsystem is introduced.
   - New connectors, services, repositories, or AI components require corresponding documentation updates.
   - Documentation is part of the feature deliverable.

## Guidance for Contributors

When planning a change:

- Identify which layer owns the responsibility.
- Confirm the change preserves the evidence-first flow.
- Avoid crossing boundaries between connectors, parsers, services, repositories, and AI reasoning.
- Document new subsystems before or alongside implementation.

These rules are intended to keep Policy Alpha maintainable, auditable, and aligned with its evidence-first mission.