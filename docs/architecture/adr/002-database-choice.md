# ADR 002: Database Choice

## Status
Accepted

## Context
Policy Alpha needs a reliable relational database foundation for structured government intelligence and future semantic search capabilities.

## Decision
Use PostgreSQL as the long-term production database, with SQLite used for local development during Milestone 1 and early iteration.

## Reasons
- PostgreSQL provides strong relational support and production readiness.
- SQLite is simple for local development and keeps early milestones lightweight.
- The architecture can later support embeddings and vector search without a large platform redesign.
- The database layer can be migrated with minimal disruption because the application is already designed around a shared abstraction.

## Rejected Alternatives
- Neo4j, because it would introduce a different data model and complexity that is not justified for the MVP.
- Multiple databases in the MVP, because that would increase operational and architectural complexity too early.
