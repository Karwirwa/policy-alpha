# Policy Alpha Domain Model Blueprint

## Purpose

Policy Alpha is an AI-native government intelligence platform designed to transform public government information into structured investment intelligence. The platform is intended to help investors, researchers, businesses, journalists, and analysts understand how government decisions create opportunities, risks, and strategic signals.

The platform is designed to be:

- Evidence-first
- Country-agnostic
- AI-assisted rather than AI-driven
- Retrieval-first
- Explainable
- Modular
- Incrementally extensible

Implementation will begin with Kenya, but the architecture is intentionally designed to support additional countries including Kenya, the United States, the United Kingdom, and Canada without requiring a redesign of the core platform.

## Core Architectural Principles

The following principles guide the domain model and platform design:

- AI is a reasoning engine, not a database.
- Retrieval before reasoning.
- Structured knowledge over raw documents.
- Evidence before recommendations.
- Deterministic validation for factual information.
- Stateless reasoning using reconstructed context.
- Country-independent domain model.
- Modular architecture with clear separation of responsibilities.
- Incremental implementation over premature complexity.
- Stable architecture over model-specific behavior.

## High-Level Platform Architecture

```text
Data Sources
    ↓
Country Connectors
    ↓
Ingestion
    ↓
Normalization
    ↓
Relational Database
    ↓
Vector Search
    ↓
Retrieval
    ↓
Context Builder
    ↓
LLM
    ↓
Validators
    ↓
Frontend
```

### Layer Responsibilities

- Data Sources: Public government datasets, official portals, filings, notices, and public records.
- Country Connectors: Country-specific adapters that collect and normalize information from local sources.
- Ingestion: Intake of raw data into the platform while preserving provenance.
- Normalization: Standardization of data into consistent structures and common concepts.
- Relational Database: Durable storage for structured entities, relationships, and audit history.
- Vector Search: Semantic retrieval support for documents and text segments.
- Retrieval: Selection of relevant context for analysis.
- Context Builder: Assembly of the evidence needed for reasoning.
- LLM: Interpretation, synthesis, and explanation of the retrieved context.
- Validators: Deterministic checks for factual consistency, grounding, and quality.
- Frontend: Presentation of insights, reports, alerts, and investigation workflows.

## Complete Domain Entity Catalogue

This catalogue defines the conceptual entities that the platform will eventually represent. It is intentionally architectural and does not prescribe implementation details.

### Core Governance and Public Sector Entities

- Country: A sovereign or jurisdictional entity that defines the policy and regulatory environment.
- GovernmentAgency: A public body such as a department, ministry, regulator, or authority.
- Budget: A government budget or fiscal plan.
- BudgetAllocation: A specific line item or allocation within a budget.
- Bill: A legislative proposal or law under consideration or enactment.
- BillClause: A specific section or clause of a bill.
- ProcurementTender: A public procurement opportunity or tender notice.
- ProcurementAward: A procurement contract or award notice.
- GovernmentProject: A public or infrastructure initiative connected to policy, procurement, or funding.

### Company and Market Entities

- Company: An organization that may be affected by government policies or opportunities.
- CompanyFinancial: Financial or corporate information associated with a company.
- Sector: A broad industry grouping such as energy, healthcare, transport, or defense.
- Industry: A more specific domain or sub-industry classification within a sector.
- Market: A market or economic context in which a company or industry operates.
- Exchange: A securities exchange or market venue relevant to a company.

### Intelligence and Research Entities

- InvestmentSignal: A structured signal indicating an event, opportunity, or risk with investment relevance.
- InvestmentThesis: A structured investment narrative or interpretation that connects evidence to a conclusion.
- Portfolio: A user-defined collection of tracked opportunities or positions.
- PortfolioHolding: A specific item or opportunity tracked within a portfolio.
- Watchlist: A personal or organizational collection of entities or signals to monitor.
- ResearchReport: A document or analysis package produced from platform data.
- NewsArticle: A public news document that may be relevant to policy or market activity.

### Data and Knowledge Entities

- GovernmentSource: A source of public information such as a portal, agency, database, or publication.
- Connector: A country-specific integration component that connects the platform to a source system.
- Document: A raw or normalized public document ingested into the platform.
- DocumentChunk: A logical section or chunk of a document used for retrieval and analysis.
- Embedding: A vector representation of text or content for semantic retrieval.

### User and Collaboration Entities

- User: An individual interacting with the platform.
- Organization: A team, firm, or institution using the platform.
- Notification: A communication or alert to the user about new developments.
- Alert: A threshold-based or rule-based notification event.
- AuditLog: A record of actions or changes for traceability and review.

### AI and Validation Entities

- AIAnalysis: A generated reasoning artifact produced by the platform.
- ValidationResult: A structured record of validation or evidence review.
- PromptTemplate: A reusable prompt definition for different AI tasks.
- Conversation: A user or workflow interaction history.
- RetrievedContext: A selected evidence bundle or context set used for reasoning.

### Relationship and Resolution Entities

- Mention: A reference to an entity detected within a document or signal.
- Relationship: A typed association between two entities.
- EntityResolution: A resolved identity or normalization decision for an entity.
- TimelineEvent: A chronological event representing an important milestone or change.

### Future Entities

The following entities are intentionally recognized as future extensions and should not be treated as immediate implementation priorities:

- KnowledgeGraph
- EventStream
- ForecastModel
- ScenarioModel
- AutonomousResearchAgent
- MultiAgentWorkflow
- AdvancedRiskModel
- CrossCountryBenchmark
- SemanticCluster

## Entity Relationships

The domain model should express relationships through a consistent conceptual structure rather than a single monolithic schema. The following relationships are expected:

```text
Country
 ├── Agencies
 ├── Budgets
 ├── Bills
 ├── Procurement
 ├── Projects
 └── Companies

Company
 ├── Receives Procurement Awards
 ├── Appears in Investment Signals
 ├── Appears in Research Reports
 ├── Is tracked in Portfolio Holdings
 └── Appears in Watchlists

Document
 ├── Contains Chunks
 ├── Has Embeddings
 ├── Mentions Companies
 ├── Mentions Agencies
 └── Supports AI Analysis

GovernmentProject
 ├── Relates to Budgets
 ├── Relates to Tenders
 ├── Relates to Awards
 └── Impacts Sectors

InvestmentSignal
 ├── Supports InvestmentThesis
 ├── Triggers Alerts
 ├── Relates to Companies
 └── Relates to Sectors
```

The relationships should preserve traceability from source evidence to final insight.

## Milestone Mapping

### Milestone 2 — Core Government Data
Entities introduced:
- Country
- GovernmentAgency
- GovernmentSource
- Document
- Connector
- GovernmentProject

### Milestone 3 — Company Intelligence
Entities introduced:
- Company
- CompanyFinancial
- Sector
- Industry
- Market
- Exchange

### Milestone 4 — Investment Intelligence
Entities introduced:
- InvestmentSignal
- InvestmentThesis
- TimelineEvent
- Relationship
- Mention

### Milestone 5 — Portfolio Monitoring
Entities introduced:
- Portfolio
- PortfolioHolding
- Watchlist
- Alert
- Notification

### Milestone 6 — AI Research
Entities introduced:
- AIAnalysis
- RetrievedContext
- PromptTemplate
- ValidationResult
- Conversation

### Milestone 7 — Multi-country Expansion
Entities introduced:
- Expanded connector and mapping structures
- Cross-country normalization concepts
- Country-specific source adapters

### Milestone 8 — Advanced Analytics
Entities introduced:
- Advanced forecasting and scenario entities
- Additional analytics artifacts
- More specialized signal types

## Country Connector Architecture

The platform should support country-specific integrations through a modular connector layer. A connector is responsible for adapting a country-specific source to the platform’s common domain model.

```text
Connector
    ↓
Government Source
    ↓
Parser
    ↓
Normalizer
    ↓
Database
    ↓
Vector Store
    ↓
Retriever
```

### Kenya examples
- Kenya Gazette
- PPRA
- National Treasury
- Parliament

### United States examples
- SAM.gov
- Congress.gov
- SEC EDGAR

### United Kingdom examples
- Contracts Finder
- Parliament

### Canada examples
- Open Government
- Parliament

Adding a new country should primarily require implementing new connectors and mappings rather than redesigning the database or the core domain model.

## Investment Intelligence Flow

The platform should support an end-to-end investment workflow that begins with public information and ends with actionable investor decision support.

```text
Government Budget
    ↓
Policy
    ↓
Tender
    ↓
Award
    ↓
Company
    ↓
Investment Thesis
    ↓
Portfolio Monitoring
    ↓
Alerts
    ↓
Investor Decision Support
```

### Stage Responsibilities

- Government Budget: Public spending plans and fiscal commitments.
- Policy: Legislative or regulatory direction that affects market conditions.
- Tender: Public procurement opportunities.
- Award: Final procurement awards and contract decisions.
- Company: Organizations affected by the preceding events.
- Investment Thesis: A structured interpretation of the evidence and potential implications.
- Portfolio Monitoring: Tracking of relevant signals against user interests.
- Alerts: Timely notifications about changing conditions.
- Investor Decision Support: The final user-facing insight or decision support workflow.

## Future AI Pipeline

The platform’s future AI architecture should operate on top of structured evidence and retrieval layers, not replace them.

```text
User Question
    ↓
Intent Detection
    ↓
Retriever
    ↓
Ranking
    ↓
Context Builder
    ↓
LLM
    ↓
Validators
    ↓
Confidence Scoring
    ↓
Response
```

### Component Responsibilities

- Intent Detection: Determine the user’s analytical objective.
- Retriever: Select relevant documents, entities, and signals.
- Ranking: Prioritize the most relevant evidence.
- Context Builder: Assemble a coherent and concise evidence bundle.
- LLM: Produce reasoning, summarization, or explanation over that evidence.
- Validators: Check for factual grounding and quality.
- Confidence Scoring: Estimate how strongly the answer is supported by evidence.
- Response: Deliver the final explanation or insight to the user.

## Design Decisions Deferred

The following decisions are intentionally deferred until later milestones:

- Knowledge Graph
- Multi-agent workflows
- Event-driven notifications
- Real-time streaming
- Graph databases
- Cross-country analytics
- Advanced forecasting
- Autonomous research agents

These topics are acknowledged as important future concerns, but they are not required for the current architectural foundation.

## Success Criteria

The domain model will be considered successful if it:

- supports multiple countries,
- remains modular,
- avoids vendor lock-in,
- separates reasoning from storage,
- scales incrementally,
- remains understandable for future contributors,
- and supports AI without depending on AI.

## Final Architecture Philosophy

Policy Alpha is not an LLM application. It is a government intelligence platform composed of structured data, retrieval systems, deterministic validation, and AI-assisted reasoning. The language model is only one component of a larger intelligence system whose primary goals are transparency, explainability, evidence-based analysis, and long-term maintainability.
