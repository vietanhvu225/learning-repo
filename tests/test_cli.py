from __future__ import annotations

from pathlib import Path

import yaml

from repo_learning.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def _make_library(root: Path, *, unknown_tag: bool = False) -> None:
    report_path = root / "analyses/github/owner--repository/README.md"
    report_path.parent.mkdir(parents=True)
    report = (FIXTURES / "valid-report.md").read_text(encoding="utf-8")
    if unknown_tag:
        report = report.replace("  - ai-agents", "  - unknown-tag")
    report_path.write_text(report, encoding="utf-8")

    registry = root / "registry"
    registry.mkdir()
    entry = {
        "canonical_id": "github.com/owner/repository",
        "repo": "owner/repository",
        "provider": "github",
        "url": "https://github.com/owner/repository",
        "aliases": [],
        "upstream": None,
        "source_path": "sources/github/owner/repository",
        "analysis_path": "analyses/github/owner--repository/README.md",
        "analyzed_commit": "0123456789abcdef0123456789abcdef01234567",
        "analyzed_at": "2026-09-28",
        "analysis_version": 1,
        "status": "analyzed",
        "adoption": "watch",
        "confidence": "high",
        "tags": ["unknown-tag" if unknown_tag else "ai-agents"],
    }
    (registry / "repositories.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": 1, "repositories": [entry]}, sort_keys=False
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


def test_validate_returns_zero_for_clean_library(
    tmp_path: Path, capsys: object
) -> None:
    _make_library(tmp_path)

    result = main(["validate", "--root", str(tmp_path)])

    assert result == 0
    assert "Library validation passed." in capsys.readouterr().out


def test_validate_returns_one_with_stable_issue_output(
    tmp_path: Path, capsys: object
) -> None:
    _make_library(tmp_path, unknown_tag=True)

    result = main(["validate", "--root", str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "tag.unknown" in output
    assert "Unknown tag: unknown-tag" in output


def test_generate_indexes_refuses_to_write_invalid_library(
    tmp_path: Path, capsys: object
) -> None:
    _make_library(tmp_path, unknown_tag=True)
    index = tmp_path / "indexes/all-repositories.md"
    index.parent.mkdir(parents=True)
    index.write_text("sentinel\n", encoding="utf-8")

    result = main(["generate-indexes", "--root", str(tmp_path)])

    assert result == 1
    assert index.read_text(encoding="utf-8") == "sentinel\n"
    assert "Index generation refused" in capsys.readouterr().out

