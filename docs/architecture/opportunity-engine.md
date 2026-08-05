# Opportunity Intelligence Engine

## Purpose

The Opportunity Intelligence Engine deterministically scores companies using evidence already captured in the Policy Alpha knowledge graph. It is not an AI prediction system — it produces explainable, auditable recommendations based on deterministic rules and weighted factors.

## Scoring philosophy

- Deterministic: every score is computed by deterministic logic using the evidence graph and canonical entities.
- Explainable: each score includes a factor-by-factor breakdown and a human-readable explanation.
- Reproducible: the same evidence set produces the same score.
- Non-AI: no LLMs or machine learning are used in scoring.

## Factors

Current factors (weights):

- Government Mentions (20)
- Number of Supporting Documents (15)
- Average Evidence Confidence (15)
- Procurement Stage (20)
- Budget Presence (15)
- Evidence Freshness (10)
- Country Reliability Modifier (5)

Each factor is computed deterministically from evidence and relationships and normalized to a 0–100 scale before applying weights.

## Recommendation bands

- 90–100 Strong Buy
- 75–89 High Opportunity
- 60–74 Watch Closely
- 40–59 Neutral
- <40 Low Opportunity

## Explainability

Every score includes:

- A total score and confidence metric
- A breakdown for each factor (weight, raw score, explanation)
- A textual explanation summarizing the key drivers behind the score

## Future integration points

- Replace deterministic country reliability mapping with a maintained registry.
- Add budget size parsing into the evidence extractor to improve budget factor accuracy.
- Introduce optional ML models in a future milestone to propose alternative weighting schemes; ML models must consume evidence objects and remain auditable.

## API

- `GET /api/v1/opportunity/company/{company}` – compute and persist an opportunity score for the company and return the breakdown and explanation.
- `GET /api/v1/opportunity/top` – return top scored companies.

All responses return structured JSON with breakdowns and supporting evidence references.
