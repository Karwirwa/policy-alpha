# Database Architecture

## Database Philosophy

The long-term database architecture for Policy Alpha is built around a normalized relational model implemented in PostgreSQL and managed through SQLAlchemy and Alembic. PostgreSQL provides the reliability, extensibility, and relational capabilities required for a platform that must connect government data, organizational entities, and analytical outputs over time.

SQLAlchemy is the intended object-relational layer for modeling entities and relationships, while Alembic provides structured schema evolution as the platform grows. The database should remain normalized at the core so that entities, relationships, and auditability are preserved without excessive duplication.

The architecture also anticipates future support for semantic search and similarity-based retrieval. While vector support is not required in the initial milestone, the schema should be designed to accommodate future integration with pgvector or similar technologies without requiring a major redesign.

## Entity Relationship Overview

```text
Company
  ├── CompanySector
  ├── PortfolioHolding
  └── InvestmentSignal

GovernmentAgency
  └── GovernmentDocument

GovernmentDocument
  ├── Budget
  ├── Bill
  ├── ProcurementAward
  └── Tender

Source
  └── GovernmentDocument

Budget
  └── BudgetItem

Project
  └── ProcurementAward

Sector
  └── CompanySector

InvestmentSignal
  ├── Watchlist
  └── ResearchReport

User
  ├── Portfolio
  ├── ResearchReport
  ├── Notification
  └── Watchlist

Portfolio
  └── PortfolioHolding

Event
  └── Notification

Embedding
  └── GovernmentDocument / Company / ResearchReport / InvestmentSignal
```

## Entity Definitions

### Company
A Company represents an organization that may be affected by public policy, government spending, procurement activity, or legislative change. Companies are central to the platform because the system is ultimately designed to help users understand which firms may benefit from emerging government events.

### Source
A Source represents an external origin of government or public data, such as a department website, parliamentary record, procurement portal, budget publication, or regulatory feed. Sources provide provenance and traceability for the information ingested into the system.

### RawJobPosting (Future)
RawJobPosting is a future reusable ingestion model intended to capture semi-structured job posting data that may be relevant to policy and procurement activity. It is not part of the initial foundation, but it is important for future ingestion pipelines that need a consistent representation of externally sourced employment and organizational signals.

### GovernmentDocument
GovernmentDocument is the core document entity for public policy and government-related content. It may represent legislation, budget documents, procurement notices, agency reports, or other relevant materials. The entity provides a normalized anchor for documents that can be linked to agencies, sectors, projects, and signals.

### GovernmentAgency
GovernmentAgency represents a public body such as a ministry, department, regulator, or agency. Agencies are important because many government documents and funding decisions can be traced back to the institution that issued them.

### Budget
Budget represents a government budget document or fiscal plan. It provides a structured view of planned spending and is valuable for identifying sectors, departments, and investment-relevant themes.

### BudgetItem
BudgetItem is a granular line item within a Budget. It captures specific allocations, categories, or funding commitments that may signal future opportunities or shifts in public spending priorities.

### Bill
Bill represents a proposed or enacted piece of legislation. Bills are important because policy changes often originate in legislative action and may create downstream market or investment implications.

### ProcurementAward
ProcurementAward represents a formal procurement contract or award. It is a critical entity for identifying business opportunities, public spending flows, and the companies or projects affected by government purchasing.

### Tender
Tender represents a procurement opportunity that is available for bidding. Tenders are valuable because they often reveal upcoming spending priorities before the final contract is awarded.

### Project
Project represents a policy, infrastructure, or public initiative that may be connected to budgets, tenders, awards, or agencies. Projects are useful for connecting fragmented data into a more coherent narrative around government activity.

### Sector
Sector represents a vertical or industry grouping such as defense, energy, healthcare, transportation, or digital infrastructure. Sectors help users understand how policy and spending patterns affect specific markets.

### CompanySector
CompanySector captures the association between a company and one or more sectors. This entity allows the platform to model which industries a company operates in and how those sectors relate to policy signals.

### InvestmentSignal
InvestmentSignal is a structured representation of a notable event, trend, or opportunity derived from government data. It may represent a budget expansion, new procurement activity, a legislative change, or a material development that could influence investment interpretation.

### Watchlist
Watchlist is a user-defined collection of entities or signals that a user wants to monitor. It provides a personalized structure for tracking developments that may be relevant to a specific thesis or portfolio interest.

### Portfolio
Portfolio is a user-defined grouping of holdings and research interests. It supports the platform’s use case for investors or analysts managing a set of tracked opportunities.

### PortfolioHolding
PortfolioHolding links a portfolio to a company or opportunity that the user wants to track. It allows the platform to model a user’s current interest or exposure in a structured way.

### ResearchReport
ResearchReport is an analytical artifact created by the platform or a user. It captures insights, summaries, and interpretations that are grounded in underlying data and signaling events.

### User
User represents a person interacting with the platform. Users may create watchlists, portfolios, research notes, and notifications, and may be associated with different roles or permissions over time.

### Notification
Notification represents a system message or alert intended to inform a user of new events, updates, or changes relevant to their tracked interests.

### Event
Event is a chronological or temporal occurrence that can trigger a notification or signal. It might represent a new procurement award, legislative milestone, release of a budget document, or an updated policy development.

### Embedding
Embedding represents a vector representation of content for semantic search, similarity matching, or future retrieval enhancement. It is not part of the initial milestone, but it is essential for future support of semantic analysis and retrieval.

## Why Each Entity Exists

Each entity exists to support one or more core platform responsibilities:

- Companies and sectors help map the economic landscape affected by government activity.
- Government documents and agencies preserve the authoritative source context for policy and public data.
- Budgets, bills, tenders, and procurement awards connect public spending and legislative actions to concrete opportunities.
- Investment signals provide structured interpretations of relevant developments.
- Watchlists, portfolios, and holdings support personalized tracking and investor workflows.
- Research reports preserve analytical outputs and make them reusable.
- Users, notifications, and events support collaboration, personalization, and timely awareness.
- Embeddings support future semantic retrieval and machine-assisted discovery.

## Milestone Ownership

The database architecture should be implemented in stages so that the foundation remains manageable and extensible.

### Milestone 1: Foundation
The initial milestone should establish the core transactional and relational foundation. This includes the primary entities needed to support structured storage, provenance, and future extensibility. The core focus should be on the foundational relational model rather than advanced intelligence features.

### Future Milestones
The following entities are explicitly assigned to future milestones:

- RawJobPosting: future ingestion model for reusable, semi-structured data capture.
- Embedding: future semantic and retrieval enhancement support.
- Advanced signal enrichment workflows: future expansion of InvestmentSignal and ResearchReport capabilities.
- Notification and event-driven automation features: future experience and alerting enhancements.

This approach keeps Milestone 1 focused on the structural foundation while allowing advanced capabilities to be added as the platform matures.

## Indexing Strategy

The indexing strategy should prioritize fast lookup, provenance, and retrieval across relational data. The highest-value indexes should support:

- Lookup by document type, agency, and date.
- Relationship traversal between documents, companies, sectors, and signals.
- Filtering and ordering of time-based records such as events, tenders, and awards.
- Efficient access to user-defined watchlists and portfolios.

As the system grows, the indexing strategy should evolve to support analytical queries, temporal views, and retrieval workflows. Future semantic search will also require vector index support, but that is a later-stage enhancement rather than a foundational requirement.

## Why Raw Data Is Preserved

Raw data is preserved because public government information is often incomplete, inconsistent, or updated over time. A normalized schema alone is not sufficient for long-term reliability. Retaining original source content and provenance allows the platform to maintain traceability, support audits, and reconcile changes when documents are revised or reissued.

This preservation also creates a strong foundation for future analysis. If a later workflow needs to revisit the source material, compare revisions, or reprocess content with improved extraction logic, the original data remains available.

## Future Support for Vector Search

The database architecture should be designed to support vector-based retrieval in the future. This will be important for semantic search over policy documents, research content, company profiles, and other unstructured or semi-structured information. The schema should remain compatible with future integration of vector representations without forcing a redesign of the core relational model.

In the long term, vector search can complement traditional relational queries by enabling similarity-based retrieval and concept discovery. This is especially valuable for identifying connections between documents, signals, sectors, and investment themes that may not be obvious through explicit field-based relationships alone.

## Architectural Summary

Policy Alpha's database architecture is designed as a durable and extensible relational foundation for an AI-powered intelligence platform. It preserves provenance, supports structured analysis of government activity, and leaves room for future semantic retrieval and richer automation workflows. The design balances immediate clarity with long-term flexibility, ensuring that the system can evolve without undermining the integrity of its data model.

## Applying the evidence verification column in local SQLite

The milestone worktree does not currently include an Alembic configuration. After adding `verification_status` to the evidence model, update an existing SQLite database before running the application against it:

```powershell
sqlite3 path\to\policy_alpha.db "ALTER TABLE evidence ADD COLUMN verification_status VARCHAR(32) NOT NULL DEFAULT 'unverified';"
sqlite3 path\to\policy_alpha.db "CREATE INDEX IF NOT EXISTS ix_evidence_verification_status ON evidence (verification_status);"
```

Replace `path\to\policy_alpha.db` with the SQLite database configured for the worktree. The default is the worktree-root `policy_alpha.db`. New databases created from the SQLAlchemy metadata already include this column and index.
