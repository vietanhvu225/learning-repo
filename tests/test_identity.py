from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from repo_learning.identity import IdentityError, RepoIdentity, normalize_repo_reference


@pytest.mark.parametrize(
    "reference",
    [
        "https://github.com/VietAnhVu225/watch-skill",
        "https://github.com/vietanhvu225/watch-skill.git",
        "https://github.com/vietanhvu225/watch-skill/",
        "git@github.com:vietanhvu225/watch-skill.git",
        "ssh://git@github.com/vietanhvu225/watch-skill.git",
    ],
)
def test_github_url_variants_share_one_canonical_identity(reference: str) -> None:
    assert normalize_repo_reference(reference) == RepoIdentity(
        provider="github",
        owner="vietanhvu225",
        repository="watch-skill",
        canonical_id="github.com/vietanhvu225/watch-skill",
        canonical_url="https://github.com/vietanhvu225/watch-skill",
    )


def test_local_git_worktree_uses_its_origin_remote(tmp_path: Path) -> None:
    repository = tmp_path / "watch-skill"
    repository.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(repository)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "remote",
            "add",
            "origin",
            "git@github.com:VietAnhVu225/watch-skill.git",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert normalize_repo_reference(repository).canonical_id == (
        "github.com/vietanhvu225/watch-skill"
    )


@pytest.mark.parametrize(
    "reference",
    [
        "not-a-repository",
        "https://example.com/owner/repository",
        "https://github.com/owner",
        "git@github.com:missing-repository",
    ],
)
def test_malformed_or_unsupported_references_are_rejected(reference: str) -> None:
    with pytest.raises(IdentityError):
        normalize_repo_reference(reference)


def test_fork_and_upstream_keep_distinct_identities() -> None:
    fork = normalize_repo_reference("https://github.com/vietanhvu225/watch-skill")
    upstream = normalize_repo_reference("https://github.com/oxbshw/watch-skill")

    assert fork.canonical_id == "github.com/vietanhvu225/watch-skill"
    assert upstream.canonical_id == "github.com/oxbshw/watch-skill"
    assert fork != upstream


def test_gitlab_subgroup_is_preserved_in_owner() -> None:
    identity = normalize_repo_reference(
        "https://gitlab.com/Example/Platform/repository.git"
    )

    assert identity == RepoIdentity(
        provider="gitlab",
        owner="example/platform",
        repository="repository",
        canonical_id="gitlab.com/example/platform/repository",
        canonical_url="https://gitlab.com/example/platform/repository",
    )

