"""Validate repository-analysis metadata, identity, and portability."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .identity import IdentityError, normalize_repo_reference
from .metadata import AnalysisDocument, MetadataError, load_yaml_mapping, read_analysis


REQUIRED_FIELDS = {
    "repo",
    "provider",
    "canonical_id",
    "url",
    "aliases",
    "upstream",
    "analyzed_at",
    "analyzed_commit",
    "analysis_version",
    "status",
    "adoption",
    "confidence",
    "tags",
}
REQUIRED_EVIDENCE_SECTIONS = (
    "Observed in code",
    "Claimed by project",
    "Inferences",
    "Recommendations",
)
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    message: str


def validate_library(root: Path) -> list[Issue]:
    """Return every actionable library issue without raising for content errors."""

    root = root.resolve()
    issues: list[Issue] = []
    repository_registry = root / "registry" / "repositories.yaml"
    tag_registry = root / "registry" / "tags.yaml"

    repositories = _load_list(repository_registry, "repositories", issues)
    tags_mapping = _load_mapping(tag_registry, "tags", issues)
    known_tags = set(tags_mapping)

    revision_keys = [
        (entry.get("canonical_id"), entry.get("analyzed_commit"))
        for entry in repositories
        if isinstance(entry, dict)
    ]
    duplicate_keys = {
        key
        for key, count in Counter(revision_keys).items()
        if count > 1 and all(key)
    }
    for canonical_id, commit in sorted(duplicate_keys):
        issues.append(
            Issue(
                "registry.duplicate_revision",
                repository_registry,
                f"Duplicate analysis for {canonical_id} at commit {commit}",
            )
        )

    registered_paths: set[str] = set()
    for entry in repositories:
        if not isinstance(entry, dict):
            issues.append(
                Issue(
                    "registry.invalid_entry",
                    repository_registry,
                    "Every repositories entry must be a YAML mapping",
                )
            )
            continue
        raw_analysis_path = entry.get("analysis_path")
        if not isinstance(raw_analysis_path, str) or not raw_analysis_path.strip():
            issues.append(
                Issue(
                    "registry.missing_field",
                    repository_registry,
                    "Repository entry is missing analysis_path",
                )
            )
            continue

        relative_path = Path(raw_analysis_path)
        analysis_path = (root / relative_path).resolve()
        if not analysis_path.is_relative_to(root):
            issues.append(
                Issue(
                    "registry.unsafe_path",
                    repository_registry,
                    f"analysis_path escapes the library root: {raw_analysis_path}",
                )
            )
            continue
        registered_paths.add(relative_path.as_posix())
        if not analysis_path.is_file():
            issues.append(
                Issue(
                    "analysis.missing",
                    analysis_path,
                    f"Registered analysis does not exist: {raw_analysis_path}",
                )
            )
            continue

        try:
            document = read_analysis(analysis_path)
        except MetadataError as error:
            issues.append(Issue("metadata.invalid", analysis_path, str(error)))
            continue
        issues.extend(_validate_document(document, entry, known_tags))

    analyses_root = root / "analyses"
    if analyses_root.exists():
        for report in sorted(analyses_root.glob("*/*/README.md")):
            relative = report.relative_to(root).as_posix()
            if relative not in registered_paths:
                issues.append(
                    Issue(
                        "analysis.unregistered",
                        report,
                        f"Analysis is not listed in the registry: {relative}",
                    )
                )

    return sorted(issues, key=lambda issue: (issue.code, str(issue.path), issue.message))


def _load_list(path: Path, key: str, issues: list[Issue]) -> list[Any]:
    data = _load_registry(path, issues)
    value = data.get(key, [])
    if not isinstance(value, list):
        issues.append(Issue("registry.invalid_shape", path, f"{key} must be a list"))
        return []
    return value


def _load_mapping(path: Path, key: str, issues: list[Issue]) -> dict[str, Any]:
    data = _load_registry(path, issues)
    value = data.get(key, {})
    if not isinstance(value, dict):
        issues.append(Issue("registry.invalid_shape", path, f"{key} must be a mapping"))
        return {}
    return value


def _load_registry(path: Path, issues: list[Issue]) -> dict[str, Any]:
    try:
        return load_yaml_mapping(path)
    except MetadataError as error:
        issues.append(Issue("registry.invalid", path, str(error)))
        return {}


def _validate_document(
    document: AnalysisDocument,
    registry_entry: dict[str, Any],
    known_tags: set[str],
) -> list[Issue]:
    metadata = document.metadata
    issues: list[Issue] = []
    for field in sorted(REQUIRED_FIELDS - metadata.keys()):
        issues.append(
            Issue(
                "metadata.missing_field",
                document.path,
                f"Missing required frontmatter field: {field}",
            )
        )

    url = metadata.get("url")
    canonical_id = metadata.get("canonical_id")
    if isinstance(url, str) and isinstance(canonical_id, str):
        try:
            normalized = normalize_repo_reference(url)
        except IdentityError as error:
            issues.append(Issue("identity.invalid", document.path, str(error)))
        else:
            if canonical_id != normalized.canonical_id:
                issues.append(
                    Issue(
                        "identity.mismatch",
                        document.path,
                        f"canonical_id {canonical_id!r} does not match URL identity {normalized.canonical_id!r}",
                    )
                )

    if canonical_id and registry_entry.get("canonical_id") != canonical_id:
        issues.append(
            Issue(
                "registry.report_mismatch",
                document.path,
                "Registry canonical_id does not match report frontmatter",
            )
        )
    if metadata.get("analyzed_commit") and (
        registry_entry.get("analyzed_commit") != metadata.get("analyzed_commit")
    ):
        issues.append(
            Issue(
                "registry.report_mismatch",
                document.path,
                "Registry analyzed_commit does not match report frontmatter",
            )
        )

    aliases = metadata.get("aliases")
    if aliases is not None and not isinstance(aliases, list):
        issues.append(
            Issue("metadata.invalid_field", document.path, "aliases must be a list")
        )
    elif isinstance(aliases, list) and isinstance(canonical_id, str):
        for alias in aliases:
            try:
                alias_identity = normalize_repo_reference(str(alias))
            except IdentityError as error:
                issues.append(Issue("identity.invalid_alias", document.path, str(error)))
                continue
            if alias_identity.canonical_id != canonical_id:
                issues.append(
                    Issue(
                        "identity.alias_mismatch",
                        document.path,
                        f"Alias points to another repository: {alias}",
                    )
                )

    report_tags = metadata.get("tags", [])
    if not isinstance(report_tags, list):
        issues.append(Issue("metadata.invalid_field", document.path, "tags must be a list"))
    else:
        for tag in sorted(set(map(str, report_tags)) - known_tags):
            issues.append(
                Issue("tag.unknown", document.path, f"Unknown tag: {tag}")
            )

    for section in REQUIRED_EVIDENCE_SECTIONS:
        if not re.search(
            rf"(?im)^#{{2,6}}\s+{re.escape(section)}\s*$", document.body
        ):
            issues.append(
                Issue(
                    "evidence.missing_section",
                    document.path,
                    f"Missing evidence section: {section}",
                )
            )

    if re.search(r"(?i)file://", document.body) or WINDOWS_ABSOLUTE_PATH.search(
        document.body
    ):
        issues.append(
            Issue(
                "link.absolute",
                document.path,
                "Report contains an absolute local path or file:// URL",
            )
        )

    return issues

