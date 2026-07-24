# ADR 003: Backend Architecture

## Status
Accepted

## Context
Policy Alpha is still in the early foundation phase. The backend should remain intentionally small, clear, and easy to evolve.

## Decision
The backend architecture will currently follow a simple layered structure:

API Layer

↓

Services (future)

↓

Repositories (future)

↓

Database

## Responsibilities

### core
Shared settings, configuration, and foundational utilities.

### db
Database engine, session management, and shared database infrastructure.

### models
SQLAlchemy model definitions and shared ORM base behavior.

### api
FastAPI entrypoints and route wiring.

## Why this remains intentionally small
The project is deliberately avoiding premature abstraction. Services and repositories are not introduced until the application has a clearer need for them. This keeps the foundation approachable and prevents unnecessary complexity during Milestone 1.
