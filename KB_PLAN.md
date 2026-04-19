# Knowledge Base Development Plan

## 1. Vision
Build a local resource index from Twitter bookmarks that helps answer four questions:

- What is this resource actually about?
- Where is the original source?
- What have I already learned from it?
- What should I learn next?

This is not primarily an archive of tweet text or extracted markdown. It is a storage layer for a future learning assistant that will track progress, recommend next steps, and provide tutoring against a structured map of resources and concepts.

## 2. Desired Outcome
The KB should become a curated learning graph where each useful bookmark points to a source resource and carries enough structure to support discovery, planning, and progress tracking.

For each bookmark or derived resource, we want to capture:

- Original source link when it can be found
- Resource type: article, paper, talk, video, repo, thread, course, tool, demo
- Short description of what the source covers
- Tags and concepts
- Why it was bookmarked, if inferable
- Learning status: unread, queued, in progress, completed, revisitable
- Optional notes and takeaways
- Relationships to other resources, concepts, and learning paths

## 3. Product Requirements

### A. Core User Jobs
- Quickly find good resources to read or watch
- Organize resources by topic, depth, and format
- Track what has been consumed and learned
- Identify gaps in understanding
- Recommend what to study next based on prior progress

### B. Non-Goals For The First Iteration
- Perfect full-text archival of every external page
- Rich semantic search as the primary navigation model
- Complete media understanding for every screenshot or video
- Building the tutoring assistant itself

## 4. Design Principles
- Source-first: prefer linking to the original resource over storing a lossy local copy
- Structure over raw text: summaries, tags, concepts, and relationships matter more than verbatim extraction
- Loss-aware ingestion: screenshots, videos, and interactive pages often require source tracing instead of markdown conversion
- Iterative enrichment: start with a useful index, then add better resolution, tagging, and progress tracking
- Human-correctable: the system should allow later review and edits where automatic inference is imperfect

## 5. Data Model Direction
Graph-based indexing is a strong fit because the long-term problem is not just retrieval, but learning progression.

Potential node types:

- `Bookmark`: the original Twitter bookmark record
- `Resource`: the resolved thing worth learning from
- `Creator`: author, speaker, company, lab, channel
- `Topic`: broad areas like compilers, memory systems, inference, distributed systems
- `Concept`: finer-grained ideas like speculative decoding, KV cache compression, tail latency
- `LearningPath`: a user-defined or inferred sequence of resources
- `Note`: user notes, summaries, reflections
- `ProgressState`: current state of engagement with a resource or concept

Potential edge types:

- `BOOKMARK_POINTS_TO_RESOURCE`
- `RESOURCE_MENTIONS_TOPIC`
- `RESOURCE_TEACHES_CONCEPT`
- `RESOURCE_REFERENCES_RESOURCE`
- `CREATOR_PUBLISHED_RESOURCE`
- `RESOURCE_PREREQUISITE_FOR_RESOURCE`
- `RESOURCE_PART_OF_PATH`
- `USER_COMPLETED_RESOURCE`
- `USER_LEARNING_CONCEPT`
- `CONCEPT_PREREQUISITE_FOR_CONCEPT`

This gives us a better foundation than pure semantic search for answering questions like:

- Show me good next resources after the ones I finished on LLM inference
- What bookmarked items are really about memory systems?
- Which concepts keep recurring across resources I saved but have not studied?

Semantic search can still be added later as a secondary retrieval layer.

## 6. Ingestion Strategy

### A. Bookmark Simplification
Keep a filtered representation of each Twitter bookmark with only the fields useful for downstream processing.

Current useful fields:

- Bookmark id
- Timestamp
- Tweet URL
- Author handle
- Tweet text
- Media URLs
- Embedded Twitter article metadata when present

### B. Source Resolution
For each bookmark, try to identify the actual resource the bookmark refers to.

Resolution paths:

- Expand `t.co` links in tweet text
- Use Twitter article metadata when available
- Inspect media for clues that indicate a source page, title card, channel name, repo name, or article heading
- Infer likely source type from surrounding tweet text

The goal is not just extracting visible text, but answering: what is the canonical thing I should attach this bookmark to?

### C. Media Interpretation
Media should usually be treated as evidence, not as the final resource.

For screenshots and images:

- Extract visible text with OCR or a vision model
- Identify likely source clues such as title, site name, YouTube UI, GitHub repo name, paper title, or speaker name
- Attempt to resolve from those clues to a canonical URL or resource record

For videos:

- Capture direct media URL if needed
- Prefer identifying the underlying source resource: YouTube talk, course clip, conference talk, product demo, or Twitter-native video
- Only transcribe when it materially helps with classification or source identification

### D. Content Capture
Local extraction is optional and selective.

Useful cases:

- Text-heavy blog posts and papers where clean extraction is straightforward
- Small reference pages where offline text search is valuable

Lower-value cases:

- Video-heavy content
- Interactive demos
- Visual explainers where screenshots omit context

So the primary artifact should be structured metadata plus a canonical link, not markdown by default.

## 7. Storage Architecture Options

### A. Graph Store
Best match for the end goal.

Candidates to consider:

- SQLite-backed lightweight graph schema
- Postgres with relational tables plus graph-like joins
- Native graph database later if needed

Recommendation for now:

- Start with normal JSON or SQLite tables representing nodes and edges
- Keep the graph model explicit from day one
- Avoid committing early to heavy infrastructure

### B. Search Layer
Search is still useful, but should support the graph rather than define the whole product.

Possible layers:

- Keyword search over titles, summaries, tags, and notes
- Faceted browsing by topic, format, status, and creator
- Semantic search later over summaries and extracted text

### C. Human-Readable View
Useful, but secondary.

Options:

- Markdown exports for selected resources
- Simple generated HTML or local web UI
- CLI inspection tools for debugging ingestion and enrichment

## 8. Iterative Build Plan

### Phase 1. Normalize Bookmark Records
- Finalize the filtered bookmark schema
- Make sure media links, text, and Twitter metadata are preserved
- Add placeholders for later enrichment fields

### Phase 2. Resolve Source Resources
- Expand tweet links
- Classify likely source type
- Store candidate canonical URLs
- Mark confidence and unresolved cases

### Phase 3. Build The Core Graph
- Introduce node and edge records
- Create `Bookmark -> Resource` links
- Add initial topics, creators, and concepts
- Support manual correction for ambiguous mappings

### Phase 4. Add Learning State
- Track queue status, completion state, notes, and takeaways
- Support simple path building: learn later, read next, revisit
- Add prerequisite and related-resource edges where useful

### Phase 5. Improve Enrichment
- Use OCR or vision for screenshots that hide the real source
- Add summarization and tagging
- Extract concept-level links across resources

### Phase 6. Build Exploration Interface
- Browse by topic, concept, format, and status
- Show resource pages with source link, summary, tags, and related items
- Surface next-step recommendations from graph relationships and learning state

## 9. Open Questions To Flesh Out Next
- What minimum fields do we want on a `Resource` record?
- Do we want one canonical `Resource` for duplicate bookmarks that point to the same source?
- How much manual review are we willing to do for ambiguous screenshots?
- What learning states matter most in v1?
- Should topics and concepts be fully automatic at first, or human-curated with model suggestions?
- Do we want SQLite as the first storage format, or JSON files with an explicit graph schema?

## 10. Immediate Next Step
Before building more pipeline code, define the first stable schemas for:

- `FilteredBookmark`
- `Resource`
- `Creator`
- `Topic` or `Concept`
- `Edge`
- `LearningState`

Once those are fixed, we can implement the resolver around the data model instead of around a temporary file shape.
