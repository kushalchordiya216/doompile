"""Twitter bookmark import connector.

Parses the Twitter archive ``bookmarks.js`` / ``bookmarks.json`` export
format and produces :class:`doompile.connectors.base.ConnectorResult`.
"""

from __future__ import annotations

from doompile.connectors.base import Connector, ConnectorResult


class TwitterBookmarksConnector(Connector):
    """Connector that parses a Twitter bookmarks JSON export.

    Usage::

        connector = TwitterBookmarksConnector()
        result = connector.ingest("path/to/bookmarks.json")
    """

    kind = "twitter_bookmarks"

    def ingest(self, source: str) -> ConnectorResult:
        """Parse the Twitter bookmarks export at *source*.

        This stub raises :class:`NotImplementedError` until the real
        parser is implemented in Step 3.
        """
        msg = "TwitterBookmarksConnector.ingest is not yet implemented"
        raise NotImplementedError(msg)
