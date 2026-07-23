# 0002: PostgreSQL over SQLite

## Status
Accepted

## Context
The project may grow to support multi-user workflows, stronger relational data, and production-style deployment needs.

## Decision
Choose PostgreSQL instead of SQLite for the primary database.

## Consequences
- Better support for concurrent access and data integrity
- More suitable for production and future scaling
- Slightly more setup complexity than SQLite
