# MEMORY.md

## Current Product Definition
Doompile is a CLI-first learning planner built on top of saved resources, starting with Twitter bookmarks.

The system should answer:
- What is this resource actually about?
- Where is the original source?
- What should I learn first?
- What should I learn next?
- What have I already completed?

## Confirmed Product Decisions
- CLI-first product
- Thin dashboard later
- Twitter-bookmarks-first positioning
- Generic connector architecture internally
- SQLite as v1 storage
- Langfuse as default tracing/evals backend
- Local `ModelRouter` abstraction
- PydanticAI may be used behind `ModelRouter`
- No LiteLLM
- No LangChain/LangGraph as core architecture
- High-quality curation with manual review
- Primary mode is committed study
- Output should be a proposed learning path, not a raw list
- Product name: `Doompile`
- CLI command name: `pile`

## Default Planning Profile
`Veteran Builder`

Preferences:
- fundamentals before novelty
- theory tied to implementation
- practical tradeoffs matter
- small number of strong resources
- early exercises and toy projects
- opinionated recommendation with limited alternatives

## Open Tasks
1. Define core interfaces:
   - Connector
   - ModelRouter
   - SearchProvider
   - OCRProvider
   - Tracer
2. Add a first real `pile` CLI app layout and command wiring
3. Design the SQLite schema
4. Implement Twitter import and normalization
5. Preserve important nested source signals from raw `bookmarks.json`
6. Implement source candidate extraction
7. Build review queue flow
8. Define resource enrichment pipeline
9. Define learning path generation inputs and outputs
10. Add progress tracking states
11. Add OCR and search fallback for unresolved media bookmarks

## Deferred Tasks
- Alembic migrations
- dashboard
- OCR provider selection
- search provider selection
- semantic search
- tutor layer
- graph visualization

## Important Data Facts
- `bookmarks.json` is the real source of truth
- `filtered_bookmarks.json` is too lossy for the final product
- corpus stats observed:
  - 340 bookmarks total
  - 234 contain `t.co` links
  - 187 contain media
  - about 154 recoverable without OCR
  - about 128 likely need media-based recovery
  - about 58 likely need text-only inference or manual review

## Important File Pointers
- `/Users/kushal/Workspace/KnowledgeBase/bookmarks.json`
- `/Users/kushal/Workspace/KnowledgeBase/filtered_bookmarks.json`
- `/Users/kushal/Workspace/KnowledgeBase/filter_bookmarks.py`
- `/Users/kushal/Workspace/KnowledgeBase/docs/project-spec.md`

## Notes For Future Implementation
- Twitter export stores useful outbound URLs in nested fields like note tweets, legacy entities, quoted tweet data, and article metadata.
- Do not treat tweet text alone as the source of truth.
- Resolve canonical resources before doing serious concept and path planning.
- Keep the architecture Twitter-first in messaging but connector-generic in code.
- The package namespace is `doompile` and the intended CLI command is `pile`.

## Questions Still Open
- Exact SQLite schema
- Exact search provider for OCR recovery
- Exact OCR or multimodal provider
- Whether concept normalization is rule-based first or model-assisted first
- Whether path generation uses only curated resources or can include external suggestions

## [2026-04-18] Update Protocol
- Prefix all future additions or edits in `MEMORY.md` with the date they were made.
- Record daily brainstorming, major decisions, and plan snapshots under `archive/YYYY-MM-DD.md`.

## [2026-04-18] Next Up
1. Define the core interfaces in `src/doompile/`:
   - `Connector`
   - `ModelRouter`
   - `SearchProvider`
   - `OCRProvider`
   - `Tracer`
2. Design the SQLite schema for the first durable storage layer.
3. Implement the first real Twitter import path, likely starting with `pile import twitter <path>`.
4. Preserve nested source signals from the raw Twitter export during normalization.
5. Build toward source candidate extraction immediately after import.
