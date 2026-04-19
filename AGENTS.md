# AGENTS.md

## Purpose
This repository builds Doompile, a CLI-first personal learning planner from saved resources, starting with Twitter bookmarks.

The system should help a user:
- recover useful resources from noisy saved artifacts
- organize those resources into topics and concepts
- generate opinionated learning paths
- track progress over time

## Product Framing
This is not primarily a bookmark archive or markdown mirror.

It is:
- source-first
- goal-first
- reviewable
- learning-oriented

Twitter bookmarks are the first connector and main distribution story, but the architecture must remain generic enough to support other resource sources later.

## Engineering Principles
- Keep abstractions explicit and small.
- Prefer simple Python services over framework-heavy orchestration.
- Use typed schemas for all structured AI outputs.
- Preserve raw evidence from imported sources.
- Treat screenshots and media as clues to recover canonical resources.
- Build for human review where confidence is low.
- Avoid hidden framework coupling.
- Keep the app portable and easy to clone.

## Modern Python Standards
- Use modern Python best practices and modern tooling by default.
- Prefer the Astral ecosystem where it fits well.
- Use `uv` for environment and package management.
- Use `ty` for type checking and LSP-oriented type workflows.
- Use `ruff` for linting and formatting.
- Run formatting and linting before every commit.
- Favor strong typing throughout the codebase.
- Avoid `Any` and `Unknown`-style escape hatches unless there is a clear, documented need.
- Prefer explicit data models and validated boundaries over loosely typed dict plumbing.
- Keep functions small, composable, and easy to test.

## Git And Delivery Workflow
- Prefer trunk-based development.
- Do not create unnecessary branches.
- Make small commits and commit often.
- Prefer rebasing over merging when syncing branches.
- Keep changes narrow and reviewable.
- Avoid large refactors mixed with feature work unless explicitly required.

## Observability
- Treat observability as a first-class feature, not a later add-on.
- Add logs, traces, and structured context where they materially improve debugging and operations.
- Use structured logging via `structlog`.
- Logs should make it easy to identify:
  - where an event happened
  - when it happened
  - what happened
  - what relevant context existed
- LLM tracing is especially important and should be built in from the start.
- AI-assisted operations should be observable enough to debug:
  - model choice
  - task type
  - prompt version
  - latency
  - retries
  - fallback behavior
  - structured output validation failures
- Prefer consistent event names and stable logging fields.

## Core Architecture
The system should be organized around these layers:
- connectors
- ingestion
- resolution
- review
- resources
- concepts
- planning
- progress
- ai
- tracing

## AI Guidelines
- Do not let any external framework define the application architecture.
- All model calls should go through the local `ModelRouter` abstraction.
- PydanticAI may be used internally behind `ModelRouter`.
- Keep provider adapters replaceable.
- Prefer structured outputs over freeform text whenever possible.
- Trace AI-assisted operations via the tracing layer.
- Design so hosted APIs and local models can both fit later.

## Review Philosophy
Low-confidence outputs should not be silently trusted.
The system should make it easy to:
- inspect candidate sources
- approve canonical resources
- correct concepts/tags
- adjust learning paths

## Planning Profile
Default planning profile:
`Veteran Builder`

Biases:
- durable fundamentals
- practical understanding
- real-world tradeoffs
- small number of high-signal resources
- early toy projects
- low cognitive load

## Non-Goals For Early Development
- perfect automation
- full graph visualization
- large framework lock-in
- exhaustive scraping of every source
- building the tutoring assistant before the storage/planning layer is solid
