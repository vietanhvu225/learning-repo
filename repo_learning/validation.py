"""Validate repository-analysis metadata, identity, and portability."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterator

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
REQUIRED_REGISTRY_FIELDS = REQUIRED_FIELDS | {"source_path", "analysis_path"}
REQUIRED_EVIDENCE_SECTIONS = (
    "Observed in code",
    "Claimed by project",
    "Inferences",
    "Recommendations",
)
STATUS_VALUES = {"queued", "analyzing", "analyzed", "needs-review", "applied", "archived"}
ADOPTION_VALUES = {"adopt-now", "experiment", "watch", "reject"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
PROVIDER_VALUES = {"github", "gitlab"}
NONEMPTY_STRING_FIELDS = {
    "repo",
    "provider",
    "canonical_id",
    "url",
    "analyzed_commit",
    "status",
    "adoption",
    "confidence",
    "source_path",
    "analysis_path",
}
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
UNC_PATH = re.compile(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+")
COMMIT_SHA = re.compile(r"[0-9a-fA-F]{40}(?:[0-9a-fA-F]{24})?\Z")


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
    revision_keys: list[tuple[str, str]] = []
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

        issues.extend(_validate_registry_entry(entry, repository_registry, known_tags))
        canonical_id = entry.get("canonical_id")
        commit = entry.get("analyzed_commit")
        if isinstance(canonical_id, str) and isinstance(commit, str):
            revision_keys.append((canonical_id, commit))

        raw_analysis_path = entry.get("analysis_path")
        if not isinstance(raw_analysis_path, str) or not raw_analysis_path.strip():
            continue
        relative_path = Path(raw_analysis_path)
        analysis_path = (root / relative_path).resolve()
        if relative_path.is_absolute() or not analysis_path.is_relative_to(root):
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

    duplicate_keys = {
        key for key, count in Counter(revision_keys).items() if count > 1
    }
    for canonical_id, commit in sorted(duplicate_keys):
        issues.append(
            Issue(
                "registry.duplicate_revision",
                repository_registry,
                f"Duplicate analysis for {canonical_id} at commit {commit}",
            )
        )

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


def _validate_registry_entry(
    entry: dict[str, Any], path: Path, known_tags: set[str]
) -> list[Issue]:
    issues = _validate_fields(entry, REQUIRED_REGISTRY_FIELDS, "registry", path)
    issues.extend(_validate_identity(entry, "registry", path))
    issues.extend(_validate_tags(entry.get("tags"), known_tags, path))
    return issues


def _validate_document(
    document: AnalysisDocument,
    registry_entry: dict[str, Any],
    known_tags: set[str],
) -> list[Issue]:
    metadata = document.metadata
    issues = _validate_fields(metadata, REQUIRED_FIELDS, "metadata", document.path)
    issues.extend(_validate_identity(metadata, "metadata", document.path))
    issues.extend(_validate_tags(metadata.get("tags"), known_tags, document.path))

    for field in sorted(REQUIRED_FIELDS):
        if field not in metadata or field not in registry_entry:
            continue
        if _comparable(metadata[field]) != _comparable(registry_entry[field]):
            issues.append(
                Issue(
                    "registry.report_mismatch",
                    document.path,
                    f"Registry {field} does not match report frontmatter",
                )
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

    portable_values = [document.body, *_iter_strings(metadata)]
    if any(_contains_local_reference(value) for value in portable_values):
        issues.append(
            Issue(
                "link.absolute",
                document.path,
                "Report contains an absolute local path, UNC path, or file:// URL",
            )
        )
    return issues


def _validate_fields(
    data: dict[str, Any], required: set[str], prefix: str, path: Path
) -> list[Issue]:
    issues: list[Issue] = []
    for field in sorted(required - data.keys()):
        issues.append(
            Issue(
                f"{prefix}.missing_field",
                path,
                f"Missing required field: {field}",
            )
        )
    for field in sorted(required & data.keys()):
        error = _field_error(field, data[field])
        if error:
            issues.append(Issue(f"{prefix}.invalid_field", path, error))
    return issues


def _field_error(field: str, value: Any) -> str | None:
    if field in NONEMPTY_STRING_FIELDS and (
        not isinstance(value, str) or not value.strip()
    ):
        return f"{field} must be a non-empty string"
    if field == "provider" and isinstance(value, str) and value not in PROVIDER_VALUES:
        return f"provider must be one of {sorted(PROVIDER_VALUES)}"
    if field == "analyzed_commit" and isinstance(value, str) and not COMMIT_SHA.fullmatch(value):
        return "analyzed_commit must be a full 40- or 64-character hexadecimal SHA"
    if field == "analysis_version" and (
        not isinstance(value, int) or isinstance(value, bool) or value < 1
    ):
        return "analysis_version must be a positive integer"
    if field == "analyzed_at":
        if isinstance(value, date):
            return None
        if not isinstance(value, str) or not value.strip():
            return "analyzed_at must be an ISO date"
        try:
            date.fromisoformat(value)
        except ValueError:
            return "analyzed_at must be an ISO date"
    if field in {"aliases", "tags"} and (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        return f"{field} must be a list of non-empty strings"
    if field == "upstream" and value is not None and (
        not isinstance(value, str) or not value.strip()
    ):
        return "upstream must be null or a non-empty string"
    if field == "status" and isinstance(value, str) and value not in STATUS_VALUES:
        return f"status must be one of {sorted(STATUS_VALUES)}"
    if field == "adoption" and isinstance(value, str) and value not in ADOPTION_VALUES:
        return f"adoption must be one of {sorted(ADOPTION_VALUES)}"
    if field == "confidence" and isinstance(value, str) and value not in CONFIDENCE_VALUES:
        return f"confidence must be one of {sorted(CONFIDENCE_VALUES)}"
    return None


def _validate_identity(data: dict[str, Any], prefix: str, path: Path) -> list[Issue]:
    issues: list[Issue] = []
    url = data.get("url")
    canonical_id = data.get("canonical_id")
    if isinstance(url, str) and isinstance(canonical_id, str):
        try:
            normalized = normalize_repo_reference(url)
        except IdentityError as error:
            issues.append(Issue("identity.invalid", path, str(error)))
        else:
            if canonical_id != normalized.canonical_id:
                issues.append(
                    Issue(
                        "identity.mismatch",
                        path,
                        f"canonical_id {canonical_id!r} does not match URL identity {normalized.canonical_id!r}",
                    )
                )
            provider = data.get("provider")
            if isinstance(provider, str) and provider != normalized.provider:
                issues.append(
                    Issue(
                        f"{prefix}.invalid_field",
                        path,
                        f"provider {provider!r} does not match URL provider {normalized.provider!r}",
                    )
                )

    aliases = data.get("aliases")
    if isinstance(aliases, list) and isinstance(canonical_id, str):
        for alias in aliases:
            if not isinstance(alias, str):
                continue
            try:
                alias_identity = normalize_repo_reference(alias)
            except IdentityError as error:
                issues.append(Issue("identity.invalid_alias", path, str(error)))
                continue
            if alias_identity.canonical_id != canonical_id:
                issues.append(
                    Issue(
                        "identity.alias_mismatch",
                        path,
                        f"Alias points to another repository: {alias}",
                    )
                )

    upstream = data.get("upstream")
    if isinstance(upstream, str):
        try:
            normalize_repo_reference(upstream)
        except IdentityError as error:
            issues.append(Issue("identity.invalid_upstream", path, str(error)))
    return issues


def _validate_tags(value: Any, known_tags: set[str], path: Path) -> list[Issue]:
    if not isinstance(value, list) or not all(isinstance(tag, str) for tag in value):
        return []
    return [
        Issue("tag.unknown", path, f"Unknown tag: {tag}")
        for tag in sorted(set(value) - known_tags)
    ]


def _iter_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _iter_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_strings(nested)


def _contains_local_reference(value: str) -> bool:
    return bool(
        re.search(r"(?i)file://", value)
        or WINDOWS_ABSOLUTE_PATH.search(value)
        or UNC_PATH.search(value)
    )


def _comparable(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return tuple(value)
    return value
