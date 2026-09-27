from __future__ import annotations

from pathlib import Path

import yaml

from repo_learning.validation import validate_library


FIXTURES = Path(__file__).parent / "fixtures"
ANALYSIS_PATH = Path("analyses/github/owner--repository/README.md")


def _entry(analysis_path: str = ANALYSIS_PATH.as_posix()) -> dict[str, object]:
    return {
        "canonical_id": "github.com/owner/repository",
        "repo": "owner/repository",
        "provider": "github",
        "url": "https://github.com/owner/repository",
        "aliases": ["git@github.com:owner/repository.git"],
        "upstream": None,
        "source_path": "sources/github/owner/repository",
        "analysis_path": analysis_path,
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
    entries: list[dict[str, object]] | None = None,
    tags: list[str] | None = None,
) -> Path:
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
            {"schema_version": 1, "repositories": entries if entries is not None else [_entry()]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    tag_names = tags or ["ai-agents"]
    (registry / "tags.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "tags": {
                    name: {"description": f"Description for {name}."}
                    for name in tag_names
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return report


def _codes(root: Path) -> list[str]:
    return [issue.code for issue in validate_library(root)]


def test_valid_registry_and_report_have_no_issues(tmp_path: Path) -> None:
    _make_library(tmp_path)

    assert validate_library(tmp_path) == []


def test_missing_required_frontmatter_is_reported(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(tmp_path, report_text=text.replace("confidence: high\n", ""))

    assert "metadata.missing_field" in _codes(tmp_path)


def test_canonical_id_must_match_url(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(
        tmp_path,
        report_text=text.replace(
            "canonical_id: github.com/owner/repository",
            "canonical_id: github.com/another/repository",
        ),
    )

    assert "identity.mismatch" in _codes(tmp_path)


def test_duplicate_canonical_id_and_commit_is_reported(tmp_path: Path) -> None:
    second_path = Path("analyses/github/owner--copy/README.md")
    _make_library(tmp_path, entries=[_entry(), _entry(second_path.as_posix())])
    second = tmp_path / second_path
    second.parent.mkdir(parents=True)
    second.write_text(
        (FIXTURES / "valid-report.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    assert "registry.duplicate_revision" in _codes(tmp_path)


def test_unknown_report_tag_is_reported(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(
        tmp_path,
        report_text=text.replace("  - ai-agents", "  - unknown-tag"),
    )

    assert "tag.unknown" in _codes(tmp_path)


def test_absolute_windows_path_is_not_portable(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(tmp_path, report_text=text + "\nLocal: `F:\\source\\repository`\n")

    assert "link.absolute" in _codes(tmp_path)


def test_file_url_is_not_portable(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(tmp_path, report_text=text + "\n[local](file:///f:/source/repo)\n")

    assert "link.absolute" in _codes(tmp_path)


def test_missing_evidence_category_is_reported(tmp_path: Path) -> None:
    text = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    _make_library(tmp_path, report_text=text.replace("## Inferences", "## Notes"))

    assert "evidence.missing_section" in _codes(tmp_path)


def test_missing_analysis_path_is_reported(tmp_path: Path) -> None:
    _make_library(tmp_path, entries=[_entry("analyses/github/missing/README.md")])

    assert "analysis.missing" in _codes(tmp_path)


def test_unregistered_analysis_is_reported(tmp_path: Path) -> None:
    _make_library(tmp_path, entries=[])

    assert "analysis.unregistered" in _codes(tmp_path)


