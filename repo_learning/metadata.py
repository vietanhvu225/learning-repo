"""Read analysis Markdown frontmatter and YAML registry files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class MetadataError(ValueError):
    """Raised when a library metadata file is malformed."""


@dataclass(frozen=True)
class AnalysisDocument:
    path: Path
    metadata: dict[str, Any]
    body: str


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML file whose root value must be a mapping."""

    try:
        content = path.read_text(encoding="utf-8-sig")
        loaded = yaml.safe_load(content)
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise MetadataError(f"Cannot read YAML mapping {path}: {error}") from error

    if not isinstance(loaded, dict):
        raise MetadataError(f"Expected a YAML mapping in {path}")
    return loaded


def read_analysis(path: Path) -> AnalysisDocument:
    """Read a Markdown report with a YAML frontmatter mapping."""

    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise MetadataError(f"Cannot read analysis {path}: {error}") from error

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise MetadataError(f"Analysis {path} is missing opening frontmatter delimiter")

    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise MetadataError(
            f"Analysis {path} is missing closing frontmatter delimiter"
        ) from error

    try:
        metadata = yaml.safe_load("\n".join(lines[1:closing_index]))
    except yaml.YAMLError as error:
        raise MetadataError(f"Cannot parse frontmatter in {path}: {error}") from error
    if not isinstance(metadata, dict):
        raise MetadataError(f"Expected a YAML mapping in frontmatter for {path}")

    body = "\n".join(lines[closing_index + 1 :]).strip()
    if not body:
        raise MetadataError(f"Analysis {path} has an empty Markdown body")

    return AnalysisDocument(path=path, metadata=metadata, body=body)

