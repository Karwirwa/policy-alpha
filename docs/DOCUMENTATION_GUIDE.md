# Documentation Guide

This repository uses a structured documentation model to support long-term software engineering, architecture work, and open collaboration. The documentation is organized into purpose-specific folders so that design decisions, implementation plans, research notes, and meeting outcomes can be maintained independently and referenced consistently.

## Documentation Folder Overview

### architecture/
Use this folder for durable design artifacts that describe how the system is intended to work. This includes high-level system architecture, AI architecture, database design, data pipelines, API structure, and diagrams. Documents in this folder should focus on the current or target system design rather than day-to-day discussion.

### decisions/
Use this folder for Architecture Decision Records (ADRs). These documents should capture significant technical decisions, why they were made, and any trade-offs or consequences. Examples include technology stack decisions and database selection decisions.

### research/
Use this folder for analysis that supports product and technical direction. This may include market research, government data source notes, investment research, AI research, papers, reference materials, lessons from external investigations, or experiments that inform future development.

### meeting-notes/
Use this folder for informal planning and discussion records. This includes design discussions, planning sessions, brainstorming notes, and future ideas that have not yet been formalized into architecture or implementation documents.

### milestones/
Use this folder for milestone planning documents. Each milestone document should eventually include the objective, scope, deliverables, acceptance criteria, out-of-scope items, and lessons learned. This folder is intended to help track project progress over time in a structured way.

## When to Create Each Type of Document

- Create an architecture document when you are defining or revising a system component, interface, data flow, or technical approach.
- Create a decision record when a significant technical choice is made or reconsidered.
- Create a research note when you are evaluating a technology, source, market trend, methodology, or external reference.
- Create a meeting note when a discussion helps shape the direction of the product but has not yet matured into formal documentation.
- Create a milestone document when a project phase or delivery goal is being planned, tracked, or reviewed.

## Documentation Maintenance Guidelines

- Keep documents concise, factual, and relevant to the intended audience.
- Prefer clear headings and short sections over long narrative prose.
- Update documents when the underlying design or decision changes.
- Do not duplicate information across folders when a single document can serve a broader purpose.
- Prefer linking to related documents rather than repeating the same content in multiple places.
- Preserve historical context when a design changes, especially in decision records and milestone notes.

## Contribution Expectations

Contributors should keep the repository documentation organized as the project grows by:

1. Placing documents in the most appropriate folder.
2. Using descriptive filenames that reflect the topic clearly.
3. Writing in a professional and neutral tone.
4. Keeping the documentation aligned with the current state of the codebase and project goals.
5. Updating related documents when architecture, milestones, or technical decisions evolve.

A well-maintained documentation set will make the project easier to understand, extend, and contribute to over time.
