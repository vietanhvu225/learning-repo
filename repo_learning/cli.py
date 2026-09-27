"""Command-line interface for validating and indexing the library."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .indexes import build_index_documents, write_index_documents
from .validation import Issue, validate_library


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="repo-learning")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "generate-indexes"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args(argv)
    root = arguments.root.resolve()

    issues = validate_library(root)
    if issues:
        _print_issues(root, issues)
        if arguments.command == "generate-indexes":
            print("Index generation refused: fix validation issues first.")
        return 1

    if arguments.command == "validate":
        print("Library validation passed.")
        return 0

    documents = build_index_documents(root)
    write_index_documents(root, documents)
    print(f"Generated {len(documents)} index documents.")
    return 0


def _print_issues(root: Path, issues: list[Issue]) -> None:
    for issue in issues:
        try:
            display_path = issue.path.resolve().relative_to(root).as_posix()
        except ValueError:
            display_path = str(issue.path)
        print(f"{issue.code} {display_path}: {issue.message}")


if __name__ == "__main__":
    raise SystemExit(main())
