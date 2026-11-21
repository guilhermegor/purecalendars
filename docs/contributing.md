# **Contributing**

Everything you need to develop, test, and release `purecalendars`.

> **See also:** [Usage](usage.md) · [API Reference](api/index.md) · the repository's
> [`CONTRIBUTING.md`](https://github.com/guilhermegor/purecalendars/blob/main/CONTRIBUTING.md) holds
> the authoritative branch/PR policy.

---

## Setting up for development

Clone the repo and bootstrap the environment. Every project command is a
[poe](https://poethepoet.natn.io/) task, run through `bash bin/poe_exec.sh <task>`: the wrapper
resolves `poe` from `.venv` first, so it works on the first run even when `bin/venv.sh` has just
installed Poetry somewhere that is not on `PATH` yet.

```bash
git clone https://github.com/guilhermegor/purecalendars.git
cd purecalendars
bash bin/venv.sh                # create the Poetry venv and install deps (poe included)
bash bin/poe_exec.sh init       # seed .env, install pre-commit hooks
```

`init` composes three steps you can also run individually: `ensure_env` (seed `.env` from
`.env.example`), `venv` (create the Poetry virtualenv and install **all** dependencies,
including the dev tools), and `precommit` (install the git hooks). Poetry is auto-installed if
missing.

Run `bash bin/poe_exec.sh --help` to list every task.

---

## Pre-commit hooks

`bash bin/poe_exec.sh init` installs the pre-commit hooks, which run automatically on every `git commit` and
**must pass before a commit is created**. They mirror the CI gate (see below), so a clean
local commit is a clean CI run. Run them on demand:

```bash
poetry run pre-commit run --all-files     # run every hook against the whole tree
```

If a formatting hook (e.g. `ruff format`) rewrites a file, the commit is aborted so you can
review and re-stage the change — that is expected, just `git add` and commit again.

The shell linters (`shellcheck`, `shfmt`) install automatically with the dev dependencies —
no extra step. `bash bin/poe_exec.sh install_shell_linters` exists only as an **optional** fallback for hosts
where the pip-vendored binaries can't execute; you normally never need it.

---

## Running tests

```bash
bash bin/poe_exec.sh unit_tests         # unit tests only
bash bin/poe_exec.sh integration_tests  # integration tests only
bash bin/poe_exec.sh test_cov           # unit tests + coverage report + badge
```

`purecalendars` does no I/O, so unit tests never touch a real network, DB, or filesystem.

### The network guard

This is **enforced, not merely expected**. `tests/conftest.py` installs an autouse fixture that
swaps the socket connection primitives (`socket.socket.connect` / `connect_ex` and
`socket.create_connection`), so a test that reaches the wire fails immediately:

```
NetworkAccessError: A test tried to reach the network (...). Mock the I/O boundary
(the download / HTTP seam) instead, or mark the test @pytest.mark.allow_network if
it truly must hit the wire.
```

If you see this, something in `purecalendars` started doing I/O — which the package must not do
(fetching belongs in `opendata-calendars`). Remove the I/O rather than work around the guard. A test that genuinely must hit the network opts out explicitly:

```python
@pytest.mark.allow_network
def test_something_that_really_needs_the_wire() -> None: ...
```

Why it is a guard and not a guideline: `purecalendars` is a `pure*` package — computation only, no
I/O. The guard turns that rule into a red test the moment network code creeps back in. Note that DNS resolution (`socket.getaddrinfo`) is deliberately **not** blocked: resolving an
address neither exfiltrates data nor triggers a ban, and blocking it would break code that
classifies an address before deciding whether to connect.

### The warning policy

`pytest.ini` turns `ResourceWarning`, `pytest.PytestUnraisableExceptionWarning` and
missing-docstring-parameter warnings into errors. `DeprecationWarning`, `FutureWarning` and
`UserWarning` are no longer blanket-ignored: only the narrow, named filters in `pytest.ini`
(PIL, matplotlib, beartype, numpy divide-by-zero) are silenced. Fix a new warning at its
source; add a filter only with a reason.

---

## Linting and formatting

```bash
bash bin/poe_exec.sh lint   # ruff + mypy + codespell + pydocstyle + docstrings + shell/sql/yaml
```

Ruff config lives in `ruff.toml`, the BlueprintX template's (line-length 99, 4-space
indent, double quotes, NumPy docstrings, preview mode on); read it for the active rule
families and the deviations. `bin/*.py` is linted and formatted like
`src/` and `tests/`. Findings whose fix would change a signature or test strictness
(`PLR6301`, `PLR2004`, `PT011`, ...) are baselined with an inline `# noqa`; remove one
when you touch that code and can fix it properly. Docstring parameter/return types **must match** the type hints textually
(`int | float`, not `Union[int, float]`) — the `check-docstrings` gate enforces this.

---

## Template provenance and drift

`purecalendars` was scaffolded from the BlueprintX `lib-minimal` template, and
`.blueprintx-provenance.yaml` records which one: the tier, the BlueprintX version and commit
(`blueprintx_commit`, the merge base for every comparison), the review-bot roster choice and
the scaffold date. The stamp pins BlueprintX `12e76053` (v0.12.2): it was chosen by
measurement as the commit whose template the vendored files match most (38 of the 47
comparable files byte for byte), not by date.

Two tools compare the project with a BlueprintX checkout. Both need one, passed as
`--blueprintx-root` or exported as `BLUEPRINTX_TEMPLATE_ROOT`, and both run as poe tasks from the project
root:

```bash
export BLUEPRINTX_TEMPLATE_ROOT=~/github/blueprintx   # or pass --blueprintx-root per call
bash bin/poe_exec.sh template_drift --root .          # report only; always exits 0
bash bin/poe_exec.sh template_update --root .         # dry run: lists what would change
```

`check_template_drift.py` classifies template-managed files as **missing** (the template ships
it, the project lacks it), **template changed since scaffold** (the project left it alone) or
**both changed** (the project edited it too). `template_update.py` is a dry run until
`--apply`, which switches to `chore/template-update-<short-sha>`, merges with `git merge-file`
and leaves the result uncommitted. Do not run `--apply` casually: it touches hundreds of files.

Known limits, recorded rather than fixed:

- It reports only files the template still ships. A file the template dropped (`docs/api.md`) is not reported as removed here, because the stamped commit
  predates the `--list-copies` dry run the removed-file check needs (the run prints
  `SKIPPED removed-file check`).
- Rendered files (`README.md`, `pyproject.toml`, `LICENSE`, `SECURITY.md`) and the `bin/ci/`
  copies are outside the comparison.
- The vendored package tree appears under the placeholder `src/project/...` in the template,
  not under `src/purecalendars/...`.
- The stamp keeps only the answers given at scaffold time (tier, roster choice, versions,
  commits); the other scaffold answers are not recorded.

A file the repository has since reformatted (`ruff format`, plus inline `# noqa` baselines)
differs from the template byte for byte, so it shows up as changed on both sides without a
real divergence.

---

## Building and verifying the wheel

**Run this before your final commit / opening a PR.** It builds the wheel, installs it into
the Poetry environment, and smoke-imports the package — catching packaging mistakes (a missing
`__init__`, an unshipped `_internal/` subpackage, a broken public import) that source-tree
tests never surface:

```bash
bash bin/poe_exec.sh install_dist_locally
```

A successful run prints `Package import works` followed by the version. If it fails, the wheel
is broken even when `unit_tests` is green — fix it before pushing.

---

## Opening a branch and pull request

1. **Branch off the default branch** — `main` is protected, so never commit to it directly.
   Use a descriptive `feat/…`, `fix/…`, `docs/…`, `chore/…` name:

    ```bash
    git checkout -b feat/my-change
    ```

2. **Verify locally** before pushing — the same gates CI runs:

    ```bash
    bash bin/poe_exec.sh unit_tests && bash bin/poe_exec.sh lint \
      && bash bin/poe_exec.sh install_dist_locally
    ```

3. **Open the PR.** GitHub pre-fills the
   [pull-request template](https://github.com/guilhermegor/purecalendars/blob/main/.github/PULL_REQUEST_TEMPLATE.md);
   fill in every section — **Description** (what / why / how), **Changes Made**
   (added / updated / fixed), **Testing** (manual + automated evidence), **Documentation**, and
   **Reviewer Focus**. Link the issue the work addresses.

### The CI gate — must be green before review

Every push and pull request triggers the **Run Tests** workflow
(`.github/workflows/tests.yaml`). A PR is only considered once **all** of these pass:

| Gate | What it checks |
|------|----------------|
| codespell | Spelling across the repo. |
| docstring consistency | `pydocstyle` (D412/D417) + `check_docstrings.py` — docstring types/raises match the signatures. |
| ruff | Lint + format (`ruff check src/ tests/`). |
| mypy | Static type check (`cd src && mypy .`). `ignore_missing_imports = False`: use a `types-*` stub where one exists, else add a `[mypy-<pkg>.*]` ignore section in `mypy.ini`. |
| shell / sql / yaml lint | Non-Python lint gates (mirrors the `lint` task). |
| unit + integration tests | The full pytest suites. |
| docs language | `check_docs_language.py` — the README, CONTRIBUTING and every docs page must be written in the locale `mkdocs.yml` declares (`theme.language: en`). Documentation here is US English. |

Because pre-commit mirrors these gates, a commit that passed your local hooks will pass CI.

---

## Publishing to PyPI (maintainers)

Two GitHub Actions workflows handle releases:

- **`release-test-pypi.yaml`** — publish to [Test PyPI](https://test.pypi.org) first.
- **`release-pypi.yaml`** — publish to [PyPI](https://pypi.org) and cut a GitHub release.

**There is no manual version bump.** The version is the **git tag** — `pyproject.toml` holds a
`0.0.0` placeholder and [poetry-dynamic-versioning](https://github.com/mtkennerly/poetry-dynamic-versioning)
stamps the real version at build time. To release, trigger the workflow from the **Actions** tab
(`workflow_dispatch`) with the version (e.g. `1.1.0`). The pipeline then:

1. **Runs the full test suite** (`tests.yaml`, full matrix) as a hard gate — publishing is
   blocked unless tests pass on exactly this commit.
2. Checks the version is greater than what is already published.
3. Tags the commit `v1.1.0`, builds with `python -m build` (dynamic versioning stamps `1.1.0`),
   and uploads via [OIDC **trusted publishing**](https://docs.pypi.org/trusted-publishers/) — no
   API token stored.
4. Cuts a GitHub release for the tag. (Test PyPI builds the same version via
   `POETRY_DYNAMIC_VERSIONING_BYPASS` without creating a tag.)

Configure once:

- A GitHub **Environment** per index (repository settings): `release-pypi` for PyPI,
  `release-test-pypi` for Test PyPI.
- A **trusted publisher** on each index (PyPI and Test PyPI), matching this repo exactly:
  owner `guilhermegor`, repo `purecalendars`, workflow filename `release-pypi.yaml` (environment
  `release-pypi`) and `release-test-pypi.yaml` (environment `release-test-pypi`). On a first-ever release use a
  [**pending publisher**](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
  (register it before the project exists). No `PYPI_TOKEN` / `TEST_PYPI_TOKEN` secret is needed.

Documentation is published separately — every push to `main` runs
`.github/workflows/docs.yaml`, which builds this site and deploys it to GitHub Pages.

## Changelog (maintainers)

`CHANGELOG.md` is generated from the conventional-commit history and the git tags, **never
committed to `main` by CI**. The published site's Changelog page is regenerated fresh on every
docs build (`docs.yaml` runs `cz changelog` before `mkdocs build`), and each release also gets
GitHub-generated release notes. This keeps branch protection intact and needs **no stored
secret** (no PAT, no bypass). The only discipline is writing `feat:` / `fix:` / etc. commit
messages; preview the changelog locally any time with `bash bin/poe_exec.sh changelog`.
