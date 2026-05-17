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

The product is graph-shaped at the product level, but v1 should use a small relational schema in SQLite.

Do not add a graph database in v1.

Represent the graph through foreign keys and a small number of join tables:
- import items point to the saved evidence we imported
- resources point back to the import item they came from
- resources link to concepts through a join table
- learning paths point to goals
- learning path steps point to paths and optionally to a primary resource
- progress records point to the thing being tracked

For v1, do not split `ResourceCandidate` into a separate table yet.

Instead, use a single `resources` table with a `status` field such as:
- `candidate`
- `accepted`
- `rejected`

This keeps the weekend-project schema small while still leaving room to split the lifecycle later if needed.

## V1 Schema

This is the schema to build first.

### `import_runs`

- `id`
- `connector_kind`
- `source_path`
- `status`
- `connector_version`
- `total_items`
- `imported_items`
- `failed_items`
- `started_at`
- `completed_at`
- `error_message`

Purpose:
- one row per import execution
- used for summaries, debugging, and re-import history

### `import_items`

- `id`
- `import_run_id`
- `connector_kind`
- `connector_item_id`
- `item_kind`
- `source_url`
- `author_handle`
- `author_name`
- `content_text`
- `source_created_at`
- `saved_at`
- `review_state`
- `raw_payload_json`
- `source_signals_json`
- `created_at`
- `updated_at`

Purpose:
- the durable saved item we imported (e.g. a tweet bookmark)
- keeps the raw evidence and extracted source hints together

Notes:
- `raw_payload_json` stores the original raw connector payload
- `source_signals_json` stores extracted URLs, titles, and other deterministic clues for now
- unique key should be `(connector_kind, connector_item_id)`

### `import_item_media`

- `id`
- `import_item_id`
- `position`
- `media_type`
- `media_url`
- `thumbnail_url`
- `local_path`

Purpose:
- preserves screenshots, images, and video references attached to an import item

### `resources`

- `id`
- `source_import_item_id`
- `url`
- `normalized_url`
- `title`
- `title_hint`
- `resource_type`
- `status`
- `confidence`
- `derivation`
- `summary`
- `metadata_json`
- `created_at`
- `updated_at`

Purpose:
- stores both provisional and accepted resources
- the `status` field handles the candidate-to-confirmed lifecycle for now

Notes:
- `url` may be null for title-only or screenshot-derived provisional resources
- unique key should be `(source_import_item_id, normalized_url, derivation)` when `normalized_url` is present

### `concepts`

- `id`
- `name`
- `slug`
- `description`
- `parent_concept_id`
- `created_at`
- `updated_at`

Purpose:
- canonical concept/topic records used for organization and planning

### `concept_aliases`

- `id`
- `concept_id`
- `alias_text`
- `alias_slug`
- `source`
- `created_at`

Purpose:
- maps extracted strings (e.g. "RAG", "Retrieval-Augmented Generation", "RAG Pipelines") to a single canonical concept

Notes:
- alias matching in v1 is intentionally simple: exact or case-insensitive slug lookup
- context-dependent disambiguation (e.g. "vector" in AI vs. physics) is deferred

### `resource_concepts`

- `resource_id`
- `concept_id`
- `confidence`
- `is_primary`
- `created_at`

Purpose:
- join table linking resources to concepts

### `learning_goals`

- `id`
- `goal_text`
- `profile`
- `status`
- `created_at`
- `updated_at`

Purpose:
- stores user learning goals such as `learn compilers deeply enough to build a toy compiler`

### `learning_paths`

- `id`
- `goal_id`
- `title`
- `summary`
- `status`
- `created_at`
- `updated_at`

Purpose:
- one generated path for a goal and planning profile

### `learning_path_steps`

- `id`
- `path_id`
- `step_order`
- `phase_name`
- `title`
- `summary`
- `primary_resource_id`
- `alternatives_json`
- `exercise_text`
- `status`
- `created_at`
- `updated_at`

Purpose:
- the ordered units of work inside a learning path

Notes:
- `alternatives_json` can store a small list of alternative resource ids in v1 instead of needing another join table immediately

### `progress_records`

- `id`
- `subject_type`
- `subject_id`
- `state`
- `notes`
- `started_at`
- `completed_at`
- `updated_at`

Purpose:
- tracks progress against a resource, path, or path step

## Practical Graph Strategy

The graph we care about is:
- saved import items
- recovered resources
- concepts
- goals
- paths
- progress

The useful relationships are:
- import_item -> resource
- resource -> concept
- goal -> path
- path -> ordered step
- step -> primary resource
- progress -> any tracked subject

That is enough to support source recovery, curation, path generation, and progress tracking without introducing a graph database or a large edge-modeling system up front.

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

## Known Limitations and Planned Improvements

### Concept Alias Disambiguation

The `concept_aliases` table allows exact / case-insensitive matching of extracted strings to canonical concepts. This is intentionally simple for v1.

What is **not** yet implemented:
- **Fuzzy alias matching** ("retreival augemented generation" → "Retrieval-Augmented Generation")
- **Context-dependent disambiguation** (e.g. "vector" in AI vs. physics vs. security)
- **Semantic alias matching** via embeddings

These are well-known hard problems in the knowledge-graph / AI-memory ecosystem (see GraphRAG, Remembra, Rasputin). The planned escalation path is:

1. **v1**: exact/case-insensitive match, create new concepts eagerly, use review queue for duplicate merging
2. **v2**: co-occurrence context from the same bookmark batch to guess domain (AI vs. security)
3. **v3**: optional semantic embedding similarity for fuzzy alias resolution

This aligns with the product principle: *human review is a feature, not a failure*.

## Initial Implementation Goal

Phase 1 should leave the repository ready for the next implementation slice:
- define core interfaces
- create the SQLite schema
- implement Twitter import and normalization
