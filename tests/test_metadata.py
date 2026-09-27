from pathlib import Path

import pytest

from repo_learning.metadata import MetadataError, load_yaml_mapping, read_analysis


FIXTURES = Path(__file__).parent / "fixtures"


def test_read_analysis_returns_frontmatter_and_body() -> None:
    document = read_analysis(FIXTURES / "valid-report.md")

    assert document.metadata["canonical_id"] == "github.com/owner/repository"
    assert document.metadata["tags"] == ["ai-agents"]
    assert document.body.startswith("# Repository analysis")


def test_read_analysis_rejects_missing_closing_delimiter(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("---\nrepo: owner/repository\n# body\n", encoding="utf-8")

    with pytest.raises(MetadataError, match="closing frontmatter delimiter"):
        read_analysis(report)


def test_read_analysis_rejects_non_mapping_frontmatter(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("---\n- item\n---\n# body\n", encoding="utf-8")

    with pytest.raises(MetadataError, match="YAML mapping"):
        read_analysis(report)


def test_read_analysis_rejects_empty_markdown_body(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    report.write_text("---\nrepo: owner/repository\n---\n", encoding="utf-8")

    with pytest.raises(MetadataError, match="empty Markdown body"):
        read_analysis(report)


def test_load_yaml_mapping_includes_path_in_parse_error(tmp_path: Path) -> None:
    metadata = tmp_path / "broken.yaml"
    metadata.write_text("field: [unterminated\n", encoding="utf-8")

    with pytest.raises(MetadataError, match="broken.yaml"):
        load_yaml_mapping(metadata)

