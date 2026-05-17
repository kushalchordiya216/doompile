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

## [2026-04-27] Completed
- Schema design finalized and implemented in `src/doompile/db/models/tables.py`
- All models renamed for clarity (`Artifact` → `ImportItem`, etc.)
- Added `concept_aliases`, `connector_version`, media `local_path`, step order indexes, field comments
- Fixed `datetime.utcnow` deprecation
- Added `init-db` CLI subcommand
- All files pass `ruff check` and `ty check`
- PR #1 opened with all schema and documentation changes

## [2026-04-27] Next Up — Full Roadmap to Usable CLI

Below is the complete step-by-step sequence from the current state to the point where you can run `pile` to learn and track progress.

### Step 0: Merge Foundation (now)
- [ ] Review and merge PR #1 (`feature/schema-and-docs-refinement`)
- [ ] Verify `pile init-db` creates `~/.doompile/doompile.db` correctly

### Step 1: Core Interfaces (1–2 sessions)
- [ ] `Connector` protocol — `ingest(path) → list[ImportItem]`
- [ ] `ModelRouter` abstraction — unified LLM call interface with provider adapters
- [ ] `Tracer` abstraction — Langfuse integration for structured logging and LLM tracing
- [ ] Register these in `src/doompile/{connectors,ai,tracing}/`

### Step 2: SQLite Schema + Repositories (1 session)
- [ ] Merge `tables.py` (done in PR #1)
- [ ] Add basic repositories / query helpers for:
  - `ImportRun`, `ImportItem`, `ImportItemMedia`
  - `Resource`, `Concept`, `ConceptAlias`
  - `LearningGoal`, `LearningPath`, `LearningPathStep`
  - `ProgressRecord`

### Step 3: Twitter Import + Normalization (2–3 sessions)
- [ ] Implement `TwitterBookmarksConnector`
- [ ] Parse `bookmarks.json` (the full 164K-line source of truth)
- [ ] Extract hidden source signals:
  - `note_tweet` inline URLs
  - `legacy.entities.urls` t.co expansions
  - `quoted_status` and `retweeted_status` nested links
  - `article` metadata (title, description, URL)
- [ ] CLI command: `pile import twitter <path>`
- [ ] Store normalized results in `import_items`, `import_item_media`, `import_runs`
- [ ] Reimports must upsert by `(connector_kind, connector_item_id)` and create new `ImportRun` rows

### Step 4: Source Candidate Extraction (2–3 sessions)
- [ ] Build candidate extraction from normalized import items
- [ ] Implement `ResourceCandidate` logic inside `resources` table with `status = candidate`
- [ ] Derivation strategies:
  - direct URL from tweet text/entities
  - URL from quoted/retweeted tweet
  - article link from Twitter article metadata
  - media bookmark (flag for later OCR)
- [ ] Confidence scoring (rule-based for v1, deterministic, no LLM)
- [ ] CLI command: `pile resolve` (batch candidate extraction)

### Step 5: Review Queue (2 sessions)
- [ ] Build review queue for low-confidence candidates
- [ ] CLI command: `pile review` — interactive TUI or prompt-driven review
- [ ] Actions per item:
  - accept candidate → `status = accepted`
  - reject candidate → `status = rejected`
  - edit URL/title manually
  - skip for now
- [ ] Review must be resumable (store review state on `ImportItem` or `Resource`)

### Step 6: Resource Enrichment (3–4 sessions)
- [ ] For each accepted resource, fetch or infer metadata
- [ ] Fields to populate:
  - `resource_type`: article, video, course, paper, repo, thread, book, unknown
  - `title` (fallback to `title_hint` if fetch fails)
  - `summary` (AI-generated, one paragraph)
  - `difficulty` and `role` (AI-assisted, but human-reviewable)
- [ ] Extract concepts from resource content/summary
- [ ] Match concepts to `concepts` table via `concept_aliases` (exact/case-insensitive)
- [ ] Create new concepts eagerly when no alias match
- [ ] Populate `resource_concepts` join table
- [ ] CLI command: `pile enrich [--resource-id <id> | --all]`

### Step 7: Learning Path Generation (2–3 sessions)
- [ ] CLI command: `pile plan "<goal text>"`
- [ ] Planning profile: `Veteran Builder` (opinionated, fundamentals-first, small set of strong resources)
- [ ] Inputs:
  - user goal text
  - accepted + enriched resources matching relevant concepts
  - difficulty/role signals
- [ ] Output: `LearningPath` + ordered `LearningPathStep`s
- [ ] Each step links to a primary resource and optionally suggests alternatives
- [ ] Include exercise/toy-project prompts per step where possible
- [ ] Store paths in `learning_paths`, `learning_path_steps`
- [ ] CLI command: `pile paths` to list active paths, `pile path <id>` to inspect

### Step 8: Progress Tracking (2 sessions)
- [ ] CLI command: `pile start <path_id>` — mark path as active
- [ ] CLI command: `pile done <step_id>` — mark step completed
- [ ] CLI command: `pile progress` — show active paths and completion stats
- [ ] CLI command: `pile next` — suggest the next uncompleted step from the active path
- [ ] Store progress in `progress_records` (subject_type: path, step, resource)
- [ ] Support notes on progress entries (e.g. "read half, will finish tomorrow")

### Step 9: Polish + Fallbacks (2–3 sessions)
- [ ] Add `pile stats` — corpus summary (total bookmarks, recovered resources, active paths, completion rate)
- [ ] Implement OCR fallback for media-heavy bookmarks (Phase 7 from spec)
- [ ] Implement web search fallback for unresolved screenshots
- [ ] Add `--dry-run` to `pile import` and `pile enrich`
- [ ] Improve error messages and logging
- [ ] Add `pile config` to show/set DB path, planning profile, model provider

### Step 10: First Real Learning Loop (1 session)
- [ ] End-to-end test with real bookmarks:
  1. `pile init-db`
  2. `pile import twitter bookmarks.json`
  3. `pile resolve`
  4. `pile review` (accept/reject candidates)
  5. `pile enrich --all`
  6. `pile plan "learn enough compilers to build a toy compiler"`
  7. `pile start <path_id>`
  8. `pile next`
  9. `pile done <step_id>`
  10. `pile progress`
- [ ] Fix any critical UX or data bugs found during end-to-end

### Completion Criteria
You can confidently run:
```bash
pile import twitter bookmarks.json
pile resolve && pile review
pile enrich --all
pile plan "learn distributed systems"
pile start <path_id>
pile next   # tells you what to study
pile done   # marks completion
pile progress
```

At this point the product is **minimally usable for personal learning and progress tracking**.

## [2026-04-27] Deferred Beyond Usable CLI
- Alembic migrations (schema is still evolving)
- Dashboard/web UI
- Semantic search and vector store
- Tutoring assistant / Q&A layer
- Graph visualization
- Fuzzy alias disambiguation (exact match only for v1)
- Social/sharing features
- Multi-user support

