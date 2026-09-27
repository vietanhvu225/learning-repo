"""Canonical repository identity without network access."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


SUPPORTED_HOSTS = {
    "github.com": "github",
    "gitlab.com": "gitlab",
}


class IdentityError(ValueError):
    """Raised when a repository reference cannot be normalized safely."""


@dataclass(frozen=True)
class RepoIdentity:
    provider: str
    owner: str
    repository: str
    canonical_id: str
    canonical_url: str


def normalize_repo_reference(value: str | Path) -> RepoIdentity:
    """Normalize a supported remote URL or local Git worktree."""

    reference = str(value).strip()
    if not reference:
        raise IdentityError("Repository reference is empty")

    local_path = Path(reference).expanduser()
    if local_path.exists():
        if not local_path.is_dir():
            raise IdentityError(f"Local repository path is not a directory: {local_path}")
        reference = _origin_for_path(local_path)

    host, repository_path = _split_remote(reference)
    host = host.lower().removeprefix("www.")
    provider = SUPPORTED_HOSTS.get(host)
    if provider is None:
        raise IdentityError(f"Unsupported repository host: {host}")

    clean_path = unquote(repository_path).strip().strip("/")
    if clean_path.lower().endswith(".git"):
        clean_path = clean_path[:-4]
    parts = [part for part in clean_path.split("/") if part]
    if len(parts) < 2 or any(part in {".", ".."} for part in parts):
        raise IdentityError(f"Repository URL must include owner and repository: {reference}")

    normalized_parts = [part.lower() for part in parts]
    owner = "/".join(normalized_parts[:-1])
    repository = normalized_parts[-1]
    canonical_path = f"{owner}/{repository}"
    return RepoIdentity(
        provider=provider,
        owner=owner,
        repository=repository,
        canonical_id=f"{host}/{canonical_path}",
        canonical_url=f"https://{host}/{canonical_path}",
    )


def _origin_for_path(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path.resolve()), "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
        check=False,
    )
    origin = result.stdout.strip()
    if result.returncode != 0 or not origin:
        raise IdentityError(f"Local Git repository has no origin remote: {path}")
    return origin


def _split_remote(reference: str) -> tuple[str, str]:
    scp_match = re.fullmatch(r"git@([^:]+):(.+)", reference)
    if scp_match:
        return scp_match.group(1), scp_match.group(2)

    parsed = urlsplit(reference)
    if parsed.scheme not in {"http", "https", "ssh", "git"} or not parsed.hostname:
        raise IdentityError(f"Unsupported repository reference: {reference}")
    return parsed.hostname, parsed.path

