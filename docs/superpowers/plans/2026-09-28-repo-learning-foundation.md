# Repo Learning Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable, Git-backed repository-analysis library that is ready to ingest a list of repository URLs without duplicating prior analysis.

**Architecture:** Markdown reports remain the human-readable source of knowledge, while YAML registry and tag files provide deterministic identity and classification. A small Python package canonicalizes repository references, validates report contracts, and generates all index views; cloned repositories remain an ignored local cache under `sources/`.

**Tech Stack:** Python 3.11, PyYAML 6.x, pytest, Markdown, YAML, Git

**Spec:** `README.md`

## Global Constraints

- Keep cloned repositories under `sources/<provider>/<owner>/<repository>/` and never commit them.
- Track `sources/README.md` so the local-cache policy travels across computers.
- Use relative Markdown links only; generated files must not contain drive letters or `file://` URLs.
- Identify a repository by normalized `provider/owner/repository`, not by hashing the raw input URL.
- Treat a fork and its upstream as different canonical repositories; store upstream separately from aliases.
- Do not re-analyze the same canonical repository at the same commit.
- Every report must distinguish observed facts, project claims, inferences, and recommendations.
- Unknown tags fail validation until added to `registry/tags.yaml`.
- Do not run or install code from repositories being analyzed.
- Do not add SQLite, embeddings, vector search, or network-dependent automation in this version.

## Review Focus

- HTTPS, SSH, trailing `.git`, trailing slash, and local-path inputs for the same origin must resolve to one canonical ID; Task 2 tests each form.
- An upstream URL must not be treated as an alias of a fork; Task 2 tests separate identities.
- A report containing an absolute Windows path or `file://` link must fail validation; Task 3 tests both forms.
- Duplicate canonical ID plus commit and unknown tags must fail validation with actionable messages; Task 3 tests both cases.
- Index generation must be deterministic and must not modify analysis reports; Task 4 tests stable output and report immutability.

---

### Task 1: Portable library skeleton and metadata contracts

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `sources/README.md`
- Create: `registry/repositories.yaml`
- Create: `registry/tags.yaml`
- Create: `templates/repository-analysis.md`
- Create: `indexes/all-repositories.md`
- Create: `indexes/by-tag/README.md`
- Create: `indexes/by-status/README.md`
- Create: `indexes/by-adoption/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: approved structure and conventions in `README.md`; the existing `watch-skill` report.
- Produces: YAML schemas and report contract consumed by Tasks 2–4.

- [ ] **Step 1: Initialize local version control**

Run: `git init -b main`

Expected: the directory becomes a Git repository on branch `main`; no remote is configured.

- [ ] **Step 2: Define the sync boundary**

Create `.gitignore` so everything below `sources/` is ignored except `sources/README.md`; also ignore Python caches, pytest caches, virtual environments, `.env` files, and generated temporary files.

- [ ] **Step 3: Define the Python project**

Create `pyproject.toml` with Python `>=3.11`, runtime dependency `PyYAML>=6,<7`, test dependency `pytest>=8,<9`, and a `repo-learning` console entry point targeting `repo_learning.cli:main`.

- [ ] **Step 4: Define the registry and controlled tag vocabulary**

Create `registry/repositories.yaml` with a top-level `schema_version: 1` and `repositories: []`. Create `registry/tags.yaml` with `schema_version: 1` and entries for every tag already used by the `watch-skill` report, each containing a concise description.

- [ ] **Step 5: Define the evidence-first report template**

Create `templates/repository-analysis.md` with required frontmatter fields `repo`, `provider`, `canonical_id`, `url`, `aliases`, `upstream`, `analyzed_at`, `analyzed_commit`, `analysis_version`, `status`, `adoption`, `confidence`, and `tags`. Include fixed sections for summary, architecture, observed facts, project claims, inferences, strengths, risks, adoption ideas, decision, evidence map, and limitations.

- [ ] **Step 6: Create tracked index landing files and local-source guidance**

Add the four index landing files and `sources/README.md`. State that generated child index pages must not be manually edited and that source clones are disposable local cache.

- [ ] **Step 7: Update the root design document**

Extend `README.md` with canonical aliases, fork/upstream behavior, evidence classifications, adoption decisions, deterministic validation, and the future lessons/evals loop learned from `watch-skill`.

- [ ] **Step 8: Verify the static foundation**

Run: `git check-ignore sources/github/example/repo sources/README.md`

Expected: only `sources/github/example/repo` is reported as ignored.

- [ ] **Step 9: Commit**

```bash
git add .gitignore pyproject.toml README.md sources registry templates indexes
git commit -m "docs: establish repo learning library contracts"
```

### Task 2: Canonical repository identity

**Files:**
- Create: `repo_learning/__init__.py`
- Create: `repo_learning/identity.py`
- Create: `tests/test_identity.py`

**Interfaces:**
- Consumes: provider/owner/repository identity rules from Task 1.
- Produces: `RepoIdentity` and `normalize_repo_reference()` for validation and future URL ingestion.

- [ ] **Step 1: Write identity tests**

Add tests asserting that HTTPS, SSH, trailing slash, and trailing `.git` forms of `github.com/vietanhvu225/watch-skill` produce the same identity; a local clone resolves through its `origin`; malformed references raise `IdentityError`; and `github.com/oxbshw/watch-skill` remains distinct from the fork.

- [ ] **Step 2: Run the identity tests and verify failure**

Run: `python -m pytest tests/test_identity.py -v`

Expected: FAIL because `repo_learning.identity` does not exist.

- [ ] **Step 3: Implement the identity interface**

In `repo_learning/identity.py`, define:

```python
@dataclass(frozen=True)
class RepoIdentity:
    provider: str
    owner: str
    repository: str
    canonical_id: str
    canonical_url: str

class IdentityError(ValueError): ...

def normalize_repo_reference(value: str | Path) -> RepoIdentity: ...
```

Support GitHub and GitLab HTTPS/SSH URLs plus local Git worktrees with an `origin` remote. Normalize host and GitHub/GitLab owner/repository case to lowercase, remove trailing slash and `.git`, and never perform a network request.

- [ ] **Step 4: Run identity tests**

Run: `python -m pytest tests/test_identity.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add repo_learning tests/test_identity.py
git commit -m "feat: normalize repository identities"
```

### Task 3: Report and registry validation

**Files:**
- Create: `repo_learning/metadata.py`
- Create: `repo_learning/validation.py`
- Create: `tests/fixtures/valid-report.md`
- Create: `tests/test_metadata.py`
- Create: `tests/test_validation.py`

**Interfaces:**
- Consumes: `RepoIdentity` from Task 2 and YAML contracts from Task 1.
- Produces: frontmatter parsing, registry loading, and actionable validation issues for Task 4 and the CLI.

- [ ] **Step 1: Write frontmatter parsing tests**

Test a valid report, missing closing delimiter, non-mapping YAML, and an empty Markdown body.

- [ ] **Step 2: Run metadata tests and verify failure**

Run: `python -m pytest tests/test_metadata.py -v`

Expected: FAIL because `repo_learning.metadata` does not exist.

- [ ] **Step 3: Implement metadata parsing**

In `repo_learning/metadata.py`, define:

```python
class MetadataError(ValueError): ...

@dataclass(frozen=True)
class AnalysisDocument:
    path: Path
    metadata: dict[str, Any]
    body: str

def read_analysis(path: Path) -> AnalysisDocument: ...
def load_yaml_mapping(path: Path) -> dict[str, Any]: ...
```

Use `yaml.safe_load` and reject malformed or non-mapping metadata with path-specific errors.

- [ ] **Step 4: Run metadata tests**

Run: `python -m pytest tests/test_metadata.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Write validation tests**

Test required frontmatter, canonical ID consistency, duplicate canonical ID plus commit, unknown tag, absolute Windows path, `file://` URL, missing evidence categories, missing analysis path, and a valid registry/report pair.

- [ ] **Step 6: Run validation tests and verify failure**

Run: `python -m pytest tests/test_validation.py -v`

Expected: FAIL because `repo_learning.validation` does not exist.

- [ ] **Step 7: Implement validation interfaces**

In `repo_learning/validation.py`, define:

```python
@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    message: str

def validate_library(root: Path) -> list[Issue]: ...
```

Return stable codes and actionable messages; do not throw for user-correctable content problems. Validate reports listed in the registry and flag unregistered reports found under `analyses/`.

- [ ] **Step 8: Run validation tests**

Run: `python -m pytest tests/test_validation.py -v`

Expected: all tests PASS.

- [ ] **Step 9: Commit**

```bash
git add repo_learning tests
git commit -m "feat: validate analysis metadata and portability"
```

### Task 4: Deterministic index generation and first registered analysis

**Files:**
- Create: `repo_learning/indexes.py`
- Create: `repo_learning/cli.py`
- Create: `tests/test_indexes.py`
- Create: `tests/test_cli.py`
- Modify: `analyses/github/vietanhvu225--watch-skill/README.md`
- Modify: `registry/repositories.yaml`
- Modify: generated files below `indexes/`

**Interfaces:**
- Consumes: `read_analysis()` and `validate_library()` from Task 3.
- Produces: deterministic Markdown index documents and CLI commands `validate` and `generate-indexes`.

- [ ] **Step 1: Write index-generation tests**

Test deterministic ordering by canonical ID, relative links, one page per tag/status/adoption value, stale generated-page removal, unchanged report contents, and identical output across two runs.

- [ ] **Step 2: Run index tests and verify failure**

Run: `python -m pytest tests/test_indexes.py -v`

Expected: FAIL because `repo_learning.indexes` does not exist.

- [ ] **Step 3: Implement index generation**

In `repo_learning/indexes.py`, define:

```python
def build_index_documents(root: Path) -> dict[Path, str]: ...
def write_index_documents(root: Path, documents: Mapping[Path, str]) -> None: ...
```

Generate `all-repositories.md` and child pages under `by-tag/`, `by-status/`, and `by-adoption/`. Put a generated-file warning in every document and write only when content changes.

- [ ] **Step 4: Write CLI tests**

Test `validate` exit code `0` for a clean library and `1` with stable issue output for an invalid library; test `generate-indexes` refuses to write when validation fails.

- [ ] **Step 5: Implement the CLI**

In `repo_learning/cli.py`, define `main(argv: Sequence[str] | None = None) -> int` with subcommands `validate` and `generate-indexes`. Default the library root to the current directory and accept `--root PATH`.

- [ ] **Step 6: Normalize and register the existing `watch-skill` report**

Update its frontmatter to the Task 1 schema using canonical ID `github.com/vietanhvu225/watch-skill`, origin URL `https://github.com/vietanhvu225/watch-skill`, upstream `https://github.com/oxbshw/watch-skill`, commit `264afc2bfe1bd4c11c8cac973f4b13016270c9a2`, `analysis_version: 1`, `confidence: high`, and `adoption: experiment`. Register the report and its origin URL variants without treating upstream as an alias.

- [ ] **Step 7: Generate the indexes**

Run: `python -m repo_learning.cli generate-indexes --root .`

Expected: index pages list `watch-skill` once and use relative links.

- [ ] **Step 8: Run complete verification**

Run: `python -m pytest -v`

Expected: all tests PASS.

Run: `python -m repo_learning.cli validate --root .`

Expected: exit code `0` and a clean-library message.

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 9: Commit**

```bash
git add repo_learning tests analyses registry indexes
git commit -m "feat: generate indexes for registered analyses"
```


