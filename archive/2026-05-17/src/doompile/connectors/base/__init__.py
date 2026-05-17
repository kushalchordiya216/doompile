"""Connector protocol and data transfer models.

All source connectors (Twitter bookmarks, Pocket, etc.) implement the
:class:`Connector` protocol defined here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


class ConnectorError(Exception):
    """Raised when a connector encounters a non-recoverable error."""


class ConnectorConfigError(ConnectorError):
    """Raised when a connector is misconfigured (missing auth, bad path, etc.)."""


@dataclass
class ImportItemMediaData:
    """Media attachment extracted from an import item."""

    position: int = 0
    media_type: str | None = None
    media_url: str | None = None
    thumbnail_url: str | None = None


@dataclass
class ImportItemData:
    """A single importable item produced by a connector.

    Carries everything needed to upsert a row into ``import_items`` and
    its related ``import_item_media`` table.
    """

    connector_item_id: str
    item_kind: str | None = None
    source_url: str | None = None
    author_handle: str | None = None
    author_name: str | None = None
    content_text: str | None = None
    source_created_at: datetime | None = None
    saved_at: datetime | None = None
    raw_payload_json: dict | None = None
    source_signals_json: dict | None = None
    media: list[ImportItemMediaData] = field(default_factory=list)


@dataclass
class ConnectorResult:
    """Batch result returned by a connector's ``ingest`` method."""

    connector_kind: str
    connector_version: str | None = None
    source_path: str | None = None
    total_items: int = 0
    items: list[ImportItemData] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class Connector(Protocol):
    """Interface all source connectors must implement.

    Usage::

        class TwitterBookmarksConnector:
            kind = "twitter_bookmarks"

            def ingest(self, source: str) -> ConnectorResult:
                ...
    """

    kind: str
    """Unique slug identifying this connector (e.g. ``"twitter_bookmarks"``)."""

    def ingest(self, source: str) -> ConnectorResult:
        """Parse *source* and return structured import data.

        *source* is connector-specific — typically a local file path
        for v1. Connectors that need remote API access should accept a
        config path or credentials in their ``__init__``.
        """
        ...
