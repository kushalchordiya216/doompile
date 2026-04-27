"""SQLAlchemy table definitions for Doompile v1 schema."""

from datetime import UTC, datetime
from typing import Self

from sqlalchemy import (
    JSON,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class SchemaVersion(Base):
    """Tracks the current database schema version for ad-hoc migrations.

    A single-row table used to coordinate manual schema upgrades before
    Alembic is adopted.
    """

    __tablename__ = "schema_version"

    version: Mapped[int] = mapped_column(primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(default=_utc_now)


class ImportRun(Base):
    """One row per import execution.

    Records a single run of a connector (e.g. ``pile import twitter
    /path/to/bookmarks.json``).  Used for summaries, debugging, and
    re-import history.
    """

    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    connector_kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Connector slug, e.g. 'twitter_bookmarks'.",
    )
    source_path: Mapped[str | None] = mapped_column(
        String(500),
        comment="Filesystem path to the raw file fed to the connector (e.g. bookmarks.json).",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Lifecycle state: pending, running, completed, failed.",
    )
    connector_version: Mapped[str | None] = mapped_column(
        String(50),
        comment="Version of the connector/parser that produced this run.",
    )
    total_items: Mapped[int] = mapped_column(default=0)
    imported_items: Mapped[int] = mapped_column(default=0)
    failed_items: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime] = mapped_column(default=_utc_now)
    completed_at: Mapped[datetime | None] = mapped_column()
    error_message: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list["ImportItem"]] = relationship(back_populates="import_run")


class ImportItem(Base):
    """A single imported record from a connector.

    Represents *what the user actually saved* — a tweet bookmark, a
    Pocket item, etc. — not the canonical destination resource.

    Keeping the raw connector payload (`raw_payload_json`) is
    intentional: Twitter exports hide canonical URLs in nested fields
    (legacy entities, quoted tweets, article metadata) that are lost
    during flattening.  Re-imports also need a stable natural key
    (`connector_kind` + `connector_item_id`) for deterministic upserts.
    """

    __tablename__ = "import_items"
    __table_args__ = (
        UniqueConstraint(
            "connector_kind",
            "connector_item_id",
            name="uq_import_items_connector",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    import_run_id: Mapped[int] = mapped_column(
        ForeignKey("import_runs.id"),
        nullable=False,
        comment="Back-reference to the import run that created this item.",
    )
    connector_kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Connector slug, e.g. 'twitter_bookmarks'.",
    )
    connector_item_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Stable identifier assigned by the source platform (e.g. tweet id).",
    )
    item_kind: Mapped[str | None] = mapped_column(
        String(30),
        comment="Connector-specific subtype, e.g. 'tweet', 'retweet', 'note_tweet'.",
    )
    source_url: Mapped[str | None] = mapped_column(
        String(2048),
        comment="Platform permalink to the saved item itself, not the canonical resource.",
    )
    author_handle: Mapped[str | None] = mapped_column(String(100))
    author_name: Mapped[str | None] = mapped_column(String(200))
    content_text: Mapped[str | None] = mapped_column(
        Text,
        comment="Text body of the imported item (e.g. tweet text), not the destination page.",
    )
    source_created_at: Mapped[datetime | None] = mapped_column(
        comment="When the item was originally created on the source platform.",
    )
    saved_at: Mapped[datetime | None] = mapped_column(
        comment="When the user saved/bookmarked the item.",
    )
    review_state: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="Queue state for source-recovery review: pending, resolved, needs_review.",
    )
    raw_payload_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Original connector payload verbatim, used for re-processing and debugging.",
    )
    source_signals_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Deterministically extracted URLs, titles, and other clues from the raw payload.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    import_run: Mapped["ImportRun"] = relationship(back_populates="items")
    resources: Mapped[list["Resource"]] = relationship(back_populates="source_item")
    media: Mapped[list["ImportItemMedia"]] = relationship(back_populates="item")


class ImportItemMedia(Base):
    """Media attachments (images, screenshots, video) linked to an import item."""

    __tablename__ = "import_item_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    import_item_id: Mapped[int] = mapped_column(
        ForeignKey("import_items.id"),
        nullable=False,
        comment="Parent import item that owns this media.",
    )
    position: Mapped[int] = mapped_column(default=0)
    media_type: Mapped[str | None] = mapped_column(String(30))
    media_url: Mapped[str | None] = mapped_column(String(2048))
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048))
    local_path: Mapped[str | None] = mapped_column(
        String(500),
        comment="Filesystem path to a downloaded/cached copy for OCR or local preview.",
    )

    item: Mapped["ImportItem"] = relationship(back_populates="media")


class Resource(Base):
    """A canonical resource extracted from one or more import items.

    Represents the thing the user actually wants to learn: a blog post,
    a paper, a GitHub repository, etc.  Lifecycle is managed through
    `status` (`candidate` → `accepted` / `rejected`).
    """

    __tablename__ = "resources"
    __table_args__ = (
        Index(
            "ix_resources_source",
            "source_import_item_id",
            "normalized_url",
            "derivation",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_import_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_items.id"),
        comment="The import item from which this resource was derived.",
    )
    url: Mapped[str | None] = mapped_column(
        String(2048),
        comment="Resolved canonical URL, when available.",
    )
    normalized_url: Mapped[str | None] = mapped_column(
        String(2048),
        comment="URL after scheme-stripping, trailing-slash removal, etc.",
    )
    title: Mapped[str | None] = mapped_column(
        String(500),
        comment="Canonical title of the resource.",
    )
    title_hint: Mapped[str | None] = mapped_column(
        String(500),
        comment="Inferred title from signals when a canonical title is not yet resolved.",
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        comment="Broad category: article, paper, video, course, tool, etc.",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="candidate",
        comment="Lifecycle: candidate, accepted, rejected.",
    )
    confidence: Mapped[float | None] = mapped_column(
        comment="Model or heuristic confidence that this is the correct canonical resource.",
    )
    derivation: Mapped[str | None] = mapped_column(
        String(50),
        comment="How the resource was produced, e.g. 'expanded_link', 'ocr', 'inferred'.",
    )
    summary: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        comment="Unstructured extra fields (difficulty hints, duration estimates, etc.).",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    source_item: Mapped["ImportItem | None"] = relationship(back_populates="resources")
    concepts: Mapped[list["ResourceConcept"]] = relationship(back_populates="resource")
    path_steps: Mapped[list["LearningPathStep"]] = relationship(back_populates="primary_resource")


class Concept(Base):
    """Canonical topic or concept used to organise resources and build paths."""

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        comment="URL-safe identifier used in CLI references and dashboards.",
    )
    description: Mapped[str | None] = mapped_column(Text)
    parent_concept_id: Mapped[int | None] = mapped_column(
        ForeignKey("concepts.id"),
        comment="Parent concept for building a topic hierarchy (acyclic tree).",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    parent: Mapped[Self | None] = relationship(
        "Concept",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list[Self]] = relationship(back_populates="parent")
    resources: Mapped[list["ResourceConcept"]] = relationship(back_populates="concept")
    aliases: Mapped[list["ConceptAlias"]] = relationship(back_populates="concept")


class ConceptAlias(Base):
    """Alternative names for a concept.

    Allows the system to map extracted strings like ``RAG``,
    ``Retrieval-Augmented Generation``, or ``RAG Pipelines`` back to a
    single canonical :class:`Concept`.

    Matching in v1 is intentionally simple (exact / case-insensitive
    slug lookup).  Fuzzy or context-aware disambiguation is deferred.
    """

    __tablename__ = "concept_aliases"
    __table_args__ = (
        UniqueConstraint(
            "alias_slug",
            name="uq_concept_aliases_slug",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id"),
        nullable=False,
        comment="Canonical concept this alias points to.",
    )
    alias_text: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Human-readable alias, e.g. 'RAG Pipelines'.",
    )
    alias_slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="URL-safe alias, e.g. 'rag-pipelines'.",
    )
    source: Mapped[str | None] = mapped_column(
        String(50),
        comment="How the alias was created: ai_extracted, user_added, common_variant.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)

    concept: Mapped["Concept"] = relationship(back_populates="aliases")


class ResourceConcept(Base):
    """Join table linking resources to concepts."""

    __tablename__ = "resource_concepts"

    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.id"),
        primary_key=True,
    )
    concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id"),
        primary_key=True,
    )
    confidence: Mapped[float | None] = mapped_column(
        comment="Model confidence that this concept applies to the resource.",
    )
    is_primary: Mapped[bool] = mapped_column(
        default=False,
        comment="Whether this is the dominant topic for the resource.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)

    resource: Mapped["Resource"] = relationship(back_populates="concepts")
    concept: Mapped["Concept"] = relationship(back_populates="resources")


class LearningGoal(Base):
    """A high-level learning objective stated by the user.

    Example: *"learn compilers deeply enough to build a toy compiler"*.
    """

    __tablename__ = "learning_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Free-form description of what the user wants to learn.",
    )
    profile: Mapped[str] = mapped_column(
        String(50),
        default="veteran_builder",
        comment="Planning profile slug that biases path generation (e.g. veteran_builder).",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        comment="Lifecycle: active, paused, completed, archived.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    paths: Mapped[list["LearningPath"]] = relationship(back_populates="goal")


class LearningPath(Base):
    """One generated learning path for a goal and planning profile.

    A goal may have multiple path versions over time; the application
    layer should identify which one is currently active.
    """

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(
        ForeignKey("learning_goals.id"),
        nullable=False,
        comment="The learning goal this path serves.",
    )
    title: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="Lifecycle: draft, published, superseded.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    goal: Mapped["LearningGoal"] = relationship(back_populates="paths")
    steps: Mapped[list["LearningPathStep"]] = relationship(
        back_populates="path",
        order_by="LearningPathStep.step_order",
    )


class LearningPathStep(Base):
    """An ordered unit of work inside a learning path.

    Each step points to a primary resource and may list alternative
    resource ids in `alternatives_json`.
    """

    __tablename__ = "learning_path_steps"
    __table_args__ = (
        Index(
            "ix_steps_path_order",
            "path_id",
            "step_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    path_id: Mapped[int] = mapped_column(
        ForeignKey("learning_paths.id"),
        nullable=False,
        comment="Parent learning path.",
    )
    step_order: Mapped[int] = mapped_column(
        nullable=False,
        comment="Zero-based position within the path.",
    )
    phase_name: Mapped[str | None] = mapped_column(
        String(100),
        comment="Optional grouping label, e.g. 'Fundamentals', 'Project'.",
    )
    title: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    primary_resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("resources.id"),
        comment="The main resource to study for this step.",
    )
    alternatives_json: Mapped[list[int] | None] = mapped_column(
        JSON,
        comment="List of alternative resource ids the user may swap in.",
    )
    exercise_text: Mapped[str | None] = mapped_column(
        Text,
        comment="Suggested hands-on exercise or toy project tied to this step.",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="Lifecycle: pending, in_progress, completed, skipped.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)

    path: Mapped["LearningPath"] = relationship(back_populates="steps")
    primary_resource: Mapped["Resource | None"] = relationship(back_populates="path_steps")


class ProgressRecord(Base):
    """Tracks user progress against a resource, path, or path step.

    ``subject_type`` + ``subject_id`` form a polymorphic pointer to the
    entity being tracked.
    """

    __tablename__ = "progress_records"
    __table_args__ = (
        UniqueConstraint(
            "subject_type",
            "subject_id",
            name="uq_progress_subject",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Entity kind being tracked: resource, learning_path, learning_path_step.",
    )
    subject_id: Mapped[int] = mapped_column(
        nullable=False,
        comment="Row id of the entity being tracked.",
    )
    state: Mapped[str] = mapped_column(
        String(20),
        default="not_started",
        comment="Progress state: not_started, in_progress, completed, paused, abandoned.",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        comment="Free-form user notes about this progress entry.",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        comment="When the user began work on this subject.",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        comment="When the user marked this subject complete.",
    )
    created_at: Mapped[datetime] = mapped_column(default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=_utc_now, onupdate=_utc_now)
