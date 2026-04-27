"""Top-level CLI entrypoint for Doompile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from doompile.db.session import create_tables
from doompile.db.session.connection import get_db_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pile",
        description="Doompile: turn saved resource chaos into curated learning paths.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "init-db",
        help="Initialize the SQLite database with the v1 schema",
    )

    subparsers.add_parser(
        "status",
        help="Show current status",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        db_path = get_db_path()
        print(f"Creating database at: {db_path}")
        create_tables()
        print("Database created successfully.")
        return 0

    if args.command == "status":
        print("Doompile CLI scaffold is ready. Next up: import, review, and learn commands.")
        return 0

    parser.print_help()
    return 1
