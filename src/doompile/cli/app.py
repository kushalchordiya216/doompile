"""Top-level CLI entrypoint for Doompile."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pile",
        description="Doompile: turn saved resource chaos into curated learning paths.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        help="Subcommand placeholder for the phase-1 scaffold.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command != "status":
        parser.error(f"unknown command: {args.command}")

    print("Doompile CLI scaffold is ready. Next up: import, review, and learn commands.")
    return 0
