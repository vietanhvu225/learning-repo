from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from repo_learning.identity import IdentityError, normalize_repo_reference
from repo_learning.indexes import build_index_documents, write_index_documents
from repo_learning.metadata import MetadataError
from repo_learning.validation import validate_library


FIXTURES = Path(__file__).parent / "fixtures"
ANALYSIS_PATH = Path("analyses/github/owner--repository/README.md")


def _valid_entry() -> dict[str, object]:
    return {
        "canonical_id": "github.com/owner/repository",
        "repo": "owner/repository",
        "provider": "github",
        "url": "https://github.com/owner/repository",
        "aliases": [],
        "upstream": None,
        "source_path": "sources/github/owner/repository",
        "analysis_path": ANALYSIS_PATH.as_posix(),
        "analyzed_commit": "0123456789abcdef0123456789abcdef01234567",
        "analyzed_at": "2026-09-28",
        "analysis_version": 1,
        "status": "analyzed",
        "adoption": "watch",
        "confidence": "high",
        "tags": ["ai-agents"],
    }


def _make_library(
    root: Path,
    *,
    report_text: str | None = None,
    entry: dict[str, object] | None = None,
) -> None:
    report = root / ANALYSIS_PATH
    report.parent.mkdir(parents=True)
    report.write_text(
        report_text
        if report_text is not None
        else (FIXTURES / "valid-report.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    registry = root / "registry"
    registry.mkdir()
    (registry / "repositories.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": 1, "repositories": [entry or _valid_entry()]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (registry / "tags.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "tags": {"ai-agents": {"description": "AI agent workflows."}},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _codes(root: Path) -> list[str]:
    return [issue.code for issue in validate_library(root)]


def test_writer_rejects_destination_outside_managed_indexes(tmp_path: Path) -> None:
    root = tmp_path / "library"
    root.mkdir()
    victim = tmp_path / "victim.md"

    with pytest.raises(MetadataError, match="managed indexes"):
        write_index_documents(
            root,
            {Path("indexes/by-status/../../../victim.md"): "malicious\n"},
        )

    assert not victim.exists()


def test_index_builder_rejects_traversal_view_value(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["status"] = "../../../victim"
    _make_library(tmp_path, entry=entry)

    with pytest.raises(MetadataError, match="status"):
        build_index_documents(tmp_path)


def test_registry_unknown_tag_is_rejected_even_when_report_is_valid(
    tmp_path: Path,
) -> None:
    entry = _valid_entry()
    entry["tags"] = ["unknown-tag"]
    _make_library(tmp_path, entry=entry)

    assert "tag.unknown" in _codes(tmp_path)


def test_registry_alias_cannot_point_to_upstream(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["aliases"] = ["https://github.com/upstream/repository"]
    _make_library(tmp_path, entry=entry)

    assert "identity.alias_mismatch" in _codes(tmp_path)


def test_null_required_report_field_is_rejected(tmp_path: Path) -> None:
    report = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(tmp_path, report_text=report.replace("confidence: high", "confidence: null"))

    assert "metadata.invalid_field" in _codes(tmp_path)


def test_unhashable_registry_commit_becomes_an_issue(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["analyzed_commit"] = ["wrong-type"]
    _make_library(tmp_path, entry=entry)

    assert "registry.invalid_field" in _codes(tmp_path)


def test_project_template_satisfies_required_evidence_sections(tmp_path: Path) -> None:
    template = Path("templates/repository-analysis.md").read_text(encoding="utf-8-sig")
    report = template.replace("YYYY-MM-DD", "2026-09-28").replace(
        "full-commit-sha", "0123456789abcdef0123456789abcdef01234567"
    )
    _make_library(tmp_path, report_text=report)

    assert "evidence.missing_section" not in _codes(tmp_path)


@pytest.mark.parametrize(
    "reference",
    [
        "https://github.com/owner/repository/tree/main",
        "https://github.com/owner/repository/blob/main/README.md",
        "https://gitlab.com/group/repository/-/tree/main",
    ],
)
def test_browser_subpages_are_not_repository_identities(reference: str) -> None:
    with pytest.raises(IdentityError):
        normalize_repo_reference(reference)


@pytest.mark.parametrize(
    "injection",
    [
        "\nUNC: `\\\\server\\share\\source.md`\n",
        "local_source: F:/private/source\n",
        "attachment: file:///F:/private/source\n",
    ],
)
def test_local_paths_in_body_or_frontmatter_are_rejected(
    tmp_path: Path, injection: str
) -> None:
    report = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    if injection.startswith("\n"):
        report += injection
    else:
        report = report.replace("tags:\n", injection + "tags:\n", 1)
    _make_library(tmp_path, report_text=report)

    assert "link.absolute" in _codes(tmp_path)
