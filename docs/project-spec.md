# Project Specification

## Overview

Doompile is a CLI-first personal learning planner built on top of saved resources, with Twitter bookmarks as the first ingestion source.

The product should help a user move from a large pile of saved links, screenshots, and tweet bookmarks to a curated, reviewable, and actionable learning path.

## Core Problem

The user has many saved resources for topics they want to learn, but does not know:
- where to start
- which resources are foundational versus advanced
- which saved resources are actually relevant
- how to move from theory to hands-on practice
- what to study next once a path has started

## Product Goal

Given a goal like:

`I want to learn X with solid fundamentals and then build toy examples`

the system should:
- identify relevant resources from the saved corpus
- recover canonical source links where possible
- classify and curate those resources
- generate an opinionated learning path
- track progress over time

## Primary User Experience

The primary interface is a CLI.

Default executable name:
- `pile`

Core workflows:
- import resources
- review unresolved items
- ask for a learning path
- inspect a generated path
- track progress
- ask what to do next

Secondary interface:
- a thin dashboard later for progress, unresolved items, and active goals

## Product Principles

- Goal-first, not archive-first
- Source-first, not markdown-first
- High-quality curation over full automation
- Human review is a feature, not a failure
- Twitter-first in distribution, generic ingestion in architecture
- Explicit abstractions over framework lock-in
- Portable open-source repo with local SQLite default

## Scope For V1

- import raw Twitter bookmarks
- normalize hidden source signals from the Twitter export
- extract source candidates
- review and confirm canonical resources
- classify resources with AI assistance
- extract concepts and tags at a useful level
- generate learning paths with the `Veteran Builder` profile
- track progress states

## Not In V1

- full dashboard
- graph database
- semantic search as the primary user experience
- perfect OCR or transcription for everything
- tutoring assistant
- exhaustive archival of every source page

## Architecture Direction

The system should be built from explicit layers:
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

Twitter bookmarks are the first connector, not the permanent center of the architecture.

## Technical Decisions

- Language: Python
- Storage: SQLite
- CLI: Typer + Rich
- CLI executable: `pile`
- Schemas: Pydantic
- Tracing and evals: Langfuse
- AI integration: local `ModelRouter` abstraction
- PydanticAI may be used behind `ModelRouter`
- No LiteLLM
- No LangChain or LangGraph as core architecture
- No graph database in v1

## Data Model Direction

The product will be graph-shaped at the data model level, even if it is backed by relational storage.

Main entities:
- `BookmarkArtifact`
- `Resource`
- `ResourceCandidate`
- `Concept`
- `LearningGoal`
- `LearningPath`
- `LearningPathStep`
- `ProgressRecord`

## Planning Profile

Default planning profile: `Veteran Builder`

Biases:
- durable fundamentals
- theory connected to implementation
- real-world tradeoffs
- small number of high-signal resources
- early toy projects
- low cognitive load

## Twitter Bookmark Corpus Facts

Observed facts from the current export:
- 340 bookmarks total
- 234 contain `t.co` links in text
- 187 have media
- about 154 appear recoverable without OCR
- about 128 likely need media-based source recovery
- about 58 likely need text-only inference or manual review

Important implication:
- `bookmarks.json` contains nested source signals that are not preserved in `filtered_bookmarks.json`
- the raw export should remain the source of truth for ingestion

## Phase Plan

### Phase 1
- project scaffolding
- contributor guidance
- package layout
- project spec and memory files

### Phase 2
- Twitter import and normalization
- preserve hidden URL and article signals from the raw export

### Phase 3
- source candidate extraction
- candidate confidence scoring
- review queue

### Phase 4
- resource enrichment
- type, difficulty, role, summary, concepts

### Phase 5
- learning path generation
- path output grounded in the curated resource set

### Phase 6
- progress tracking

### Phase 7
- OCR and web search fallback for unresolved screenshot-heavy bookmarks

## Review Philosophy

Low-confidence automation should surface decisions rather than silently becoming truth.

The system should make it easy to:
- inspect candidate sources
- approve canonical resources
- correct concepts and tags
- swap or adjust learning path steps

## Initial Implementation Goal

Phase 1 should leave the repository ready for the next implementation slice:
- define core interfaces
- create the SQLite schema
- implement Twitter import and normalization
