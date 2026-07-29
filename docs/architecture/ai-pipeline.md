# Policy Alpha — AI Pipeline (Canonical)

This document describes the end-to-end AI pipeline for Policy Alpha. It is
intentionally staged: deterministic extraction and retrieval are separated from
AI reasoning. Each stage lists purpose, inputs, outputs, common failure modes,
validation approaches and possible future improvements.

Overall flow (high level):

Government Source
↓
Extraction
↓
Parsing
↓
Entity Resolution
↓
Evidence
↓
Retrieval
↓
Context Builder
↓
LLM
↓
Validators
↓
Investment Thesis
↓
Portfolio Monitoring

---

Stage: Government Source

Purpose

- Identify and register authoritative sources of government information
  (budgets, gazettes, procurement portals, parliamentary records, agency
  releases).

Inputs

- Source descriptors (URLs, metadata) supplied by country connectors or
  manual configuration.

Outputs

- Source metadata used by extractors and ingestion pipelines.
- Optionally: downloaded documents (PDFs, HTML, JSON).

Failure modes

- Source metadata is stale (URL moved, changed schema).
- Network availability or access restrictions.
- Duplicate or near-duplicate sources causing redundant ingestion.

Validation strategy

- Health checks for declared sources (periodic URL HEAD requests).
- Source metadata unit tests and schema validations.
- Manual audit of newly added sources before production use.

Future improvements

- Automated source discovery and sampling.
- Canonicalization and deduplication across sources.
- Connector-level adapters for paginated or API-backed sources.

---

Stage: Extraction

Purpose

- Convert raw files (PDF, HTML, Word) into structured plain text with basic
  layout signals (page numbers, headings, sections).
- Preserve provenance (source, page, byte offsets) for later evidence linking.

Inputs

- Raw documents fetched from Government Source stage (PDFs, HTML, JSON).

Outputs

- Extracted text objects: page ID, section heading (if detected), paragraph
  text, character offsets, and minimal structural metadata.

Failure modes

- Poorly scanned PDFs yield noisy OCR text.
- Complex layouts (tables, multi-column) may be flattened incorrectly.
- Lost page or heading information if extractor fails to detect structure.

Validation strategy

- Unit tests for extractor behavior against representative sample documents.
- Manual spot checks that page numbers, headings, and paragraphs align with
  the original document.
- Confidence scores for OCRed text and a fallback policy (skip/flag).

Future improvements

- Better OCR pipelines with language models and layout-aware tools.
- Table and figure extraction modules to preserve numeric evidence.
- Page/region-level image snippets for visual verification.

---

Stage: Parsing

Purpose

- Transform extracted text into domain objects (documents, chunks, candidate
  entities such as budgets, project names, numeric values).
- Keep parsing deterministic and rule-based in early milestones.

Inputs

- Extracted text objects from Extraction stage.

Outputs

- Parsed objects: DocumentChunk, Section, CandidateMention, numeric fields,
  and lightweight metadata used by downstream entity resolution.

Failure modes

- Over- or under-splitting content into chunks, causing context loss for
  entity resolution.
- Incorrect heuristics producing false candidate entities.

Validation strategy

- Golden-file tests: run parser on canonical doc samples and compare structured
  outputs.
- Unit tests for parsing rules and edge cases (headings, enumerations, tables).

Future improvements

- Rule-to-ML migration: retain determinism while adding learned detectors for
  headings and entities.
- Pluggable parsers per document type (budgets, laws, gazettes).

---

Stage: Entity Resolution

Purpose

- Normalize parsed mentions into canonical entities (Company, Agency, Project,
  Budget line items).
- Link mentions to existing database records where possible and create
  lightweight references when not.

Inputs

- Candidate mentions and parsed tokens from the Parser stage.
- Existing canonical entity tables (Company, Agency, Project).

Outputs

- DocumentMention (or Evidence) records linking a mention to a canonical
  entity (or a provisional placeholder) with a confidence score.

Failure modes

- Ambiguous names (e.g., acronyms, common nouns) lead to incorrect linking.
- Missing canonical entry for a genuine entity causes lost linkage.
- Over-linking (false positives) pollutes the knowledge base.

Validation strategy

- Manual spot checks of resolved mentions for seeded documents.
- Conservative matching rules in early milestones (exact or normalized
  substring matches) and explicit confidence values.
- Test cases for common ambiguous name patterns.

Future improvements

- Fuzzy matching, alias lists, and registry-backed lookups (company registry
  APIs).
- Human-in-the-loop validation flows for uncertain matches.
- Hybrid approaches that combine deterministic rules with ML rankers.

---

Stage: Evidence

Purpose

- Persist the canonical, provenance-rich pieces of information extracted from
  documents. Evidence is the atomic unit consumed by retrieval and later AI
  reasoning.

Inputs

- Resolved mentions and parsed chunks with page and section context.

Outputs

- Evidence records containing: source document reference, page, section,
  extracted_text, linked entity IDs, confidence, and timestamps.

Failure modes

- Evidence duplication from repeated ingestion of the same document.
- Missing provenance (lost page/section) reduces traceability for auditors.

Validation strategy

- Deduplication strategies at ingestion using checksums and source+date
  canonicalization.
- Schema validation and sample audits ensuring extracted_text preserves
  original context.

Future improvements

- Richer evidence types (tables, numeric extractions, structured budgets).
- Versioned evidence and change-tracking across document revisions.

---

Stage: Retrieval

Purpose

- Fast, reliable retrieval of evidence and supporting documents for downstream
  reasoning and user-facing queries.
- Provide predicates: by company, by document, by keyword, by project, by
  date.

Inputs

- Evidence records, Document records, and canonical entity tables.

Outputs

- Query results: lists of Evidence and Document objects with provenance and
  confidence for a given request.

Failure modes

- Missing indexes causing slow queries at scale.
- Incorrect joins causing incomplete or duplicate result sets.

Validation strategy

- Integration tests exercising common retrieval patterns (by company,
  by document, by date ranges).
- Performance profiling on representative datasets.

Future improvements

- Add vector search and semantic retrieval for improved recall.
- Caching strategies for hot queries and paginated endpoints.

---

Stage: Context Builder

Purpose

- Assemble a compact, relevant context bundle for an LLM given a query (for
  example, a company analysis). It picks the most relevant evidence and
  supporting documents, formats them deterministically, and includes strict
  provenance for each included fact.

Inputs

- Query (e.g., "Explain why Bamburi benefits"), retrieved Evidence, and
  optionally company/budget metadata.

Outputs

- A serialized context object: ordered evidentiary summaries, source citations,
  and any structured metadata the LLM will receive.

Failure modes

- Context length exceeding model limits (needs truncation strategies).
- Inclusion of irrelevant or low-confidence evidence diluting reasoning.

Validation strategy

- Unit tests verifying context formatting and citation correctness.
- Reproducible context bundles for given inputs (determinism tests).

Future improvements

- Learn-to-rank components to weight evidence for LLM consumption.
- Multi-stage context construction with query refinement strategies.

---

Stage: LLM (Reasoning)

Purpose

- Given deterministic context, the LLM produces human-friendly explanations,
  summaries, or candidate inferences. Importantly, the LLM should never be
  the sole source of truth; outputs require validators and provenance.

Inputs

- Context bundle from Context Builder and an instruction/prompt template.

Outputs

- Natural language explanation, summary, or candidate signals with inline
  citations pointing back to Evidence records.

Failure modes

- Hallucination: LLM invents facts not present in supplied evidence.
- Overconfident language that obscures underlying uncertainty.

Validation strategy

- Enforce citation-first prompts asking the model to only state facts present
  in the provided evidentiary context.
- Post-processing validators that verify every claim maps to a referenced
  Evidence ID.
- Baseline unit tests that compare canned contexts to expected canned
  outputs (for regression detection if prompts change).

Future improvements

- Model-agnostic prompt registry and assessment harness to track fidelity.
- Chain-of-evidence tooling that forces the LLM to output structured
  claim→evidence mappings.

---

Stage: Validators

Purpose

- Mechanically check LLM outputs against evidence and business rules to detect
  hallucinations, unsupported inferences, and formatting issues.

Inputs

- LLM outputs (text and structured claim mappings) and the original Evidence
  context used to generate them.

Outputs

- Validation report: pass/fail per claim, list of unmatched claims, and a
  confidence-adjusted summary for downstream consumption.

Failure modes

- Validators too strict causing false positives (rejecting acceptable outputs).
- Validators too lax failing to flag hallucinations.

Validation strategy

- Unit tests for validator logic with edge cases (paraphrased claims,
  numerical rounding differences).
- Human-in-the-loop review for borderline cases until validators reach
  sufficient maturity.

Future improvements

- Automated counterfactual checks and cross-source validation (does another
  document contradict the claim?).
- Statistical monitors tracking validator failure rates over time.

---

Stage: Investment Thesis

Purpose

- Capture structured investment hypotheses (title, assumptions, monitored
  companies/projects/keywords) and store a timeline of evidence that strengthens
  or weakens the thesis.

Inputs

- Validated LLM outputs and raw Evidence; user-defined thesis metadata.

Outputs

- Thesis records and linked Evidence events indicating supporting or
  contradicting signals over time.

Failure modes

- Poorly specified assumptions leading to meaningless monitoring results.
- Overfitting thesis signals to noisy evidence.

Validation strategy

- Require explicit assumptions and monitored signals when creating a thesis.
- Time-based validation that only uses evidence after a thesis creation date
  for scoring.

Future improvements

- Structured scoring models to quantify support/confidence for a thesis.
- Auto-suggested thesis updates based on recurring evidence patterns.

---

Stage: Portfolio Monitoring

Purpose

- Operationalize thesis and evidence streams to monitor a portfolio of
  companies for material changes relevant to investment decisions.

Inputs

- Thesis definitions, linked monitored companies, events derived from
  Evidence and Keyword matches, and external portfolio metadata.

Outputs

- Alerts or status summaries indicating whether monitored theses have been
  strengthened, weakened, or unchanged.

Failure modes

- Alert fatigue if monitoring is too sensitive to trivial evidence.
- Missing signals due to ingestion gaps or failed matchers.

Validation strategy

- Backtest monitoring rules on historical evidence to calibrate sensitivity.
- Set conservative defaults and require tuning per-portfolio.

Future improvements

- Sophisticated scoring and event aggregation logic.
- Integration with portfolio management surfaces (watchlists, dashboards).

---

Closing notes

- Deterministic first: Policy Alpha prioritizes deterministic extraction,
  parsing, and retrieval before introducing AI-driven reasoning.
- Evidence-first: Every claim or LLM output must link to specific Evidence
  records to maintain auditability.
- Incrementalism: Each stage is pluggable — better extractors, resolvers, and
  ranking models can be introduced without changing the canonical evidence
  model.

This document should serve as the canonical reference for implementers and
stakeholders. For design decisions and detailed component interfaces see the
individual architecture docs under docs/architecture/ (evidence-engine,
keyword-tracking, thesis-engine, country-connectors, capability-architecture).
