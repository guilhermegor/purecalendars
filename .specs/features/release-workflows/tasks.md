# dependabot-config_20260801_121652

# Ledger — #13 dependabot-config

Branch: `chore/13-dependabot-config` · Issue: #13 · Class: **ci** (no `src/` diff → no release)

## Goal

Give the repo dependency automation it currently lacks — there is no `.github/dependabot.yml`.
Both `filings-cvm` and `filings-b3` already converged on one tested configuration; porting it
yields grouped, predictable PRs instead of manual bumps nobody remembers.

## Work

- [x] `.github/dependabot.yml`, ported from `filings-cvm/.github/dependabot.yml`:
      - `pip` / `/` / weekly · `versioning-strategy: lockfile-only` (this repo commits
        `poetry.lock` and CI refuses to re-lock) · group `python-minor-patch` (`*`, minor+patch) ·
        `ignore` pandas major bumps · `open-pull-requests-limit: 5` ·
        `commit-message.prefix: chore(deps)`.
      - `github-actions` / `/` / weekly · group `github-actions` (`*`) ·
        `commit-message.prefix: chore(ci)`.
- [x] **No `labels:` key** — Dependabot posts an error comment when a referenced label does not
      exist (the reason filings-cvm dropped it; see its PR #79/#80). The rationale comment was
      adapted, not copied: filings-cvm keys auto-merge off `bin/pr_gate.py` path labels, a script
      purecalendars does not have, so here the only reason is Dependabot's missing-label error.
- [x] Carry over the explanatory header comments verbatim in spirit — they are why the settings
      survive review instead of being "simplified" away later.
- [x] Check the version floors first. **The plan's premise was wrong**: `pyproject.toml` declares
      `python = ">=3.10,<4.0"`, so **3.10 is the floor a grouped bump must not break**, not 3.9.
      `tests.yaml`'s matrix still lists `"3.9"` — see "Deferred" below.
- [ ] Verify: Dependabot parsed the file (repo → Insights → Dependency graph → Dependabot), and
      the first PR it opens is grouped and carries the `chore(deps)` / `chore(ci)` prefix.
      *(Post-merge — Dependabot only reads the file from the default branch.)*

## Also fixed here — `tests.yaml` could not have gated a single Dependabot PR

The floor check above pulled a thread that ended in a CI cache bug. **In scope, not deferred**:
`tests.yaml` is the gate this whole config depends on, and as written it was incapable of
reporting on a Dependabot PR at all. Shipping the config without this would have shipped a no-op.

### 1. The matrix lied about the floor

`["3.9", "3.10", "3.11", "3.12", "3.13"]` while `pyproject.toml` requires `>=3.10`. Now
`["3.10", "3.11", "3.12", "3.13", "3.14"]`, matching `filings-cvm`.

- `requirements.txt` (`poetry>=2.4 ; python_full_version >= "3.10"`) has no upper bound, so 3.14
  installs Poetry fine. Nothing else pins an upper Python bound.
- `classifiers` only claim `Programming Language :: Python :: 3` — no per-version claim to keep
  in sync, so they were left alone.

### 2. Why the below-floor 3.9 legs reported `success`

Verified, not guessed: on run 30725490428, **`Install Dependencies` is `skipped` on all 15 jobs**
— every leg hit the venv cache. The 3.9 legs never re-resolved the project, so nothing ever
raised the floor violation. Three coupled defects, all present in `filings-cvm` too (so this is a
template defect, not a purecalendars one):

- **The cache key hashed only `pyproject.toml`.** A `poetry.lock`-only change was therefore always
  a cache hit — and `versioning-strategy: lockfile-only` produces *exactly* lock-only diffs. Every
  Dependabot PR would have restored a stale `.venv`, skipped the install, and gone green while
  testing the pre-bump dependency set. Fixed: `hashFiles('poetry.lock', 'pyproject.toml')`.
- **`poetry.lock` was in the cache `path:`.** A restored cache overwrites the repo's committed
  lockfile, so `poetry check --lock` was validating a cache artifact rather than the tree. Fixed:
  `path: .venv` only — cache build outputs, never tracked source.
- **`poetry check --lock` lived inside the cache-guarded step**, so the fail-loud lock-sync gate
  never ran on a warm cache — disabled by the very condition that makes it cheap. Fixed: promoted
  to its own unconditional step, before the cache restore. Verified locally: `poetry check --lock`
  exits 0 against the unmodified `pyproject.toml`.

Moving the check before the win32-stripping transform also makes it check what a developer checks
locally, rather than a rewritten `pyproject.toml`.

## Deferred (tracked here, not in this PR)

- **The win32-stripping `python -c` transform in `Install Dependencies` is dead code here** —
  purecalendars has no `pywin32` dependency (`grep` finds zero matches in `pyproject.toml`), so the
  transform is a template leftover that copies, rewrites and restores `pyproject.toml` to no
  effect. Deleting it is a separate simplification, not a dependency-automation change.
- **`actions/cache@v3`** is two majors behind (`filings-cvm` is on `@v6`). Left alone on purpose:
  the `github-actions` group added in this PR is exactly what should propose that bump, and
  letting it do so is the first end-to-end proof the config works.

## Not done, on purpose

- Auto-merge for grouped patch PRs. Worth considering once the first few land and the grouping
  proves stable — not before there is any evidence about PR volume.

# explicit-release-assets_20260803_072454

# Ledger — #30 explicit-release-assets

Branch: `fix/30-explicit-release-assets` · Issue: #30 · Class: **ci** (no `src/` diff → no release)

## Goal

Name the release artifacts explicitly instead of globbing `dist/*`, **before** merging Dependabot's
#23, which bumps `softprops/action-gh-release` from `@v1` to `@v3`.

## Work

- [x] `files: dist/*` → `dist/*.whl` + `dist/*.tar.gz` in `release_pypi.yaml`.
- [x] Comment recording *why*, including that this step exists only in `release_pypi.yaml` so the
      Test PyPI rehearsal cannot catch a regression in it.
- [x] Left `dist/.keep` in place — it keeps the directory tracked, and `install_dist_locally`
      cleans `dist/*` rather than `dist/` precisely to preserve it.

## Why this is urgent rather than tidy-up

`dist/.keep` is tracked and **0 bytes**; GitHub rejects a 0-byte asset. `@v1` tolerated it —
proven by releases 1.0.0 and 1.0.1, both with exactly 2 assets and `draft=false`. **`@v3` uses a
different flow**: it creates the release as a *draft*, uploads, then promotes. A rejected asset
leaves `draft=true`, and **GitHub creates no tag for a draft**.

The failure order is what makes it expensive:

1. the `pypi` job publishes first — the version becomes public and **cannot be un-published**;
2. `Create GitHub Release` fails after that;
3. the run is red, with no tag and a draft release;
4. re-dispatching does **not** recover: the index rejects the duplicate version, so the run reddens
   again and the tag is still missing.

A missing tag is not cosmetic — `poetry-dynamic-versioning` derives the version from it, and the
next release's `git diff <tag>..HEAD` gate uses it as the base.

## Verification

- [x] Confirmed the trap is armed and not hypothetical: `files: dist/*` present at
      `release_pypi.yaml:226`, and `git cat-file -s HEAD:dist/.keep` → **0**.
- [x] Confirmed #23 is the trigger: its diff contains
      `softprops/action-gh-release@v1` → `@v3`.
- [x] Confirmed the rehearsal blind spot: `release_test_pypi.yaml` has no
      `Create GitHub Release` step, so `@v3` would run for the first time ever in production.
- [ ] Next real release: confirm the GitHub release carries exactly the wheel + tarball, is not a
      draft, and the tag exists.

## Deferred (tracked here, not in this PR)

- Nothing.

## Not done, on purpose

- **Did not delete `dist/.keep`.** It is what keeps `dist/` tracked; removing it would break
  `install_dist_locally`'s `rm -rf dist/*` idiom and is a bigger change than naming two globs.
- **Did not hold back #23.** Bumping the actions is wanted; the fix is to make the workflow correct
  under `@v3`, not to pin away from it.

# release-workflow-lock_20260803_172054

# Ledger — #39 release-workflow-lock

Branch: `fix/39-release-workflow-lock` · Issue: #39 · Class: **ci** (no `src/` diff → no release)

## Goal

Apply #19's `tests.yaml` fix to both release workflows, **remove the silent lock regeneration**, and
close the one thing left unproven about the ledger gate's bot exemption.

## Work

### The release workflows

Both `release_pypi.yaml` and `release_test_pypi.yaml` carried **all three** of #19's defects plus a
fourth unique to them:

- [x] Cache key → `hashFiles('poetry.lock', 'pyproject.toml')` (was manifest-only, so every
      lock-only change was a cache hit and the release built against a stale `.venv`).
- [x] Cache `path:` → `.venv` only (was also caching `poetry.lock`, so a restored cache could
      **overwrite the committed lockfile** before anything validated it).
- [x] `poetry check --lock` promoted to its own **unconditional** step, before the cache restore
      (inside the guarded step it never ran on a warm cache).
- [x] **Deleted the `rm -f poetry.lock; poetry lock --no-cache` fallback** — the exact inverse of
      `ci-lock-fail-loud-not-regenerate`, and worst of all in the release path: the lock governs the
      **build environment**, including `poetry-dynamic-versioning`, the plugin that stamps the
      version. Re-resolving it means publishing a wheel built with a toolchain nobody tested, and a
      published version cannot be un-published.
- [x] Removed the dead win32 transform (`pywin32` is not declared here — see #33), including the
      now-orphaned `mv pyproject.original.toml pyproject.toml` restore.
- [x] Kept the two files' install blocks **identical**, since a rehearsal only rehearses the steps
      the two workflows share.

### The bot exemption (correcting my own caveat)

- [x] **My caveat on #32 was over-cautious.** I recorded the ci/src case as "still unproven" because
      the observed Dependabot PRs touched only `poetry.lock` (class `deps`, exempt by path anyway).
      But the exemption is an early `sys.exit(0)` at `__main__` **before any path classification** —
      paths are never consulted on that branch. #25's log line therefore already proved the
      behaviour for every path class.
- [x] What was genuinely missing was a test **pinning that ordering**: nothing stopped someone
      moving the bot check after the path check, which would break the exemption for exactly the
      ci/src case. Added `tests/integration/test_ledger_gate_cli.py` — 5 tests driving the **real
      CLI** in a throwaway git repo, so the env wiring (`LEDGER_PR_AUTHOR` / `LEDGER_BASE_REF`) is
      exercised rather than assumed.

### A real Windows bug the new test found immediately

- [x] The first CI run of this PR **failed on Windows** — all 5 new cases, one cause:
      `UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-1`. Windows defaults
      stdout to cp1252, which cannot encode the `ℹ️`/`❌` status glyphs, so the gate **crashed before
      reporting anything**.
- [x] This is a bug in the **gate**, not in the test. And it is not cosmetic: the pre-commit hook is
      `always_run`, so **every commit on a Windows checkout** would have died. It stayed invisible
      because the hook is normally run on Linux and the CI step is gated on
      `runner.os == 'Linux'` — the integration test added here is the first thing that ever ran this
      script on Windows.
- [x] Fixed in `__main__` by forcing UTF-8 on `sys.stdout`/`sys.stderr` (keeping the house glyph
      style rather than stripping it). The test also passes `encoding="utf-8"` to `subprocess.run`,
      because `text=True` alone decodes with the *parent's* locale encoding — which would re-create
      the mismatch on the reading side after the child wrote correctly.
- [x] **Reproduced locally, properly.** A first attempt was vacuous — it copied the script out of
      `bin/`, so it died on the `pr_gate` sibling import before printing, and the "fixed" half ran in
      shape-only mode which prints nothing. Redone in place, no-arg mode, `PYTHONIOENCODING=cp1252`:
      pre-fix → **exit 1** with the exact CI error; fixed → **exit 0**, glyph printed, stderr empty.
- [x] Added `test_the_gate_survives_a_non_utf8_console`, which forces `PYTHONIOENCODING=cp1252` so
      this **Windows-only bug is now catchable on Linux**. Mutation-tested: removing the reconfigure
      breaks *only* that test.

### The gate's own diagnostic, fixed because it misled me

- [x] Writing this very ledger, I used `## Work — the release workflows`. The gate correctly
      rejected it but reported **"missing the `## Work` section"** — while the section was plainly
      on the page. That sends the reader hunting for the wrong problem; it cost a debug cycle here
      and had already cost one on the #26 ledger.
- [x] The check now detects the near-miss and says what is actually wrong:
      *"the heading `## Work — the release workflows` must be exactly `## Work` — move the qualifier
      into a `###` subsection below it."* Two tests cover it, including one asserting the plain
      "missing" case is **not** swallowed by the new branch.

## Verification

- [x] `poetry check --lock` → exit 0 on `main` **before** making the gate blocking, so the stricter
      gate cannot red a legitimate release.
- [x] `poetry run pytest tests/` → **369 passed** (360 + 4 new + a 2-case parametrise).
- [x] `ruff check` / `ruff format --check` / `yamllint` clean; both workflows parse as valid YAML.
- [x] **Mutation-tested the new tests** — each mutation caught by exactly the right test:

  | Mutation | Result |
  |---|---|
  | disable the bot exemption | the 2 exemption cases **and** the ordering test fail |
  | let path work run *before* the exemption | **only** the ordering test fails |

  Source restored afterwards; `git diff` clean, 5/5 green again.
- [ ] Next real release: confirm the promoted lock gate runs and the build still succeeds. This
      PR cannot exercise the release workflows — that is the point of the deferral note below.

## Deferred (tracked here, not in this PR)

- **The `dev`/`docs` group-exclusion logic in both release workflows is dead, and I left it alone.**
  It greps `[tool.poetry.group.dev]` while `pyproject.toml` declares
  `[tool.poetry.group.dev.dependencies]`, so the pattern never matches and the release always
  installs everything. I nearly "fixed" the grep, then checked what is inside the dev group:
  `build` (line 70) and `twine` (71). Fixing it would make `--without dev` strip them.
  **It would probably still work** — `Build Package` runs `python -m pip install --upgrade build`
  (self-installing) and publishing uses `pypa/gh-action-pypi-publish` via OIDC rather than twine —
  but "probably" is not a good enough basis for a change to the least-rehearsed code in the repo,
  and the only real cost today is wasted install time. Needs its own issue and its own release to
  verify.

## Not done, on purpose

- **No version bump.** Class `ci`: nothing under `src/`, so the wheel is byte-identical to 2.0.0.
  Publishing 2.0.1 for this would be the "minor-bump every merge" habit `s:release` exists to
  prevent, and it cannot be un-published.
- **Did not wait for a real Dependabot `ci` PR** to prove the exemption. That would have meant
  waiting a week for the next `github-actions` bump to confirm something the code order already
  guarantees; the integration test proves it deterministically and keeps proving it.

# release-python-minor-pin_20261119_140000

# Ledger — #81 release-python-minor-pin

Branch: `ci/81-release-python-minor-pin` · Issue: #81 · Class: **ci**

## Goal

Unblock the purecalendars 3.0.0 release. The Test PyPI run (44515729261) passed every test,
then failed in `setup_and_build`: setup-python has no 3.12.8 build for Ubuntu 26.04, which
`ubuntu-latest` now resolves to. No tag was created.

## Work

- [x] `release-pypi.yaml` and `release-test-pypi.yaml` pin `["3.12"]`, as the BlueprintX
      lib-minimal template already does. setup-python then resolves the newest 3.12 patch
      available for the runner image.
- [x] `tests/integration/test_ledger_gate_cli.py` drops inherited `GIT_*` variables before its
      nested git calls. From inside the pre-commit hook, `GIT_INDEX_FILE` pointed the throwaway
      repo's `git commit` at the outer index, so the suite failed only when run from the hook.
      It reproduces standalone with `GIT_INDEX_FILE=$PWD/.git/index`.

## Verification

- [x] `tests/integration/test_ledger_gate_cli.py` passes with `GIT_INDEX_FILE` set.
- [ ] Test PyPI 3.0.0 rerun green.
