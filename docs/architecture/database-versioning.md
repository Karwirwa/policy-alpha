# Database Versioning with Alembic

## Why migrations are important

Database migrations provide a controlled way to evolve the schema over time. They allow the project to change safely, keep changes reviewable, and preserve a reliable history of database evolution as the application grows.

## Why manual schema editing is discouraged

Editing the database schema directly is risky because it makes it difficult to track changes, reproduce them in other environments, or understand what happened during development. Alembic keeps schema changes explicit and auditable.

## How to create a migration

When the schema changes, create a new migration with Alembic:

```bash
alembic revision --autogenerate -m "Describe the change"
```

This generates a migration script based on the current SQLAlchemy metadata.

## How to upgrade

To apply the latest migrations to the database:

```bash
alembic upgrade head
```

## How to downgrade

To move the database back to a previous revision:

```bash
alembic downgrade <revision_id>
```

## How this supports future milestones

This migration foundation will support future milestones that introduce new domain models such as companies, sources, and government-related records. As those models are added, Alembic will allow the database to evolve in a stable and repeatable way.
