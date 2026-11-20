# dehydrate-calendars_20260704_130854

# Ledger — #1 dehydrate-calendars

Branch: `feat/dehydrate-calendars` · Issue: #1 · Class: **src** (shipped in 1.0.0)

<!-- #1 is PR #1, not an issue: this branch predates the /issue workflow, so no issue was ever
     filed. GitHub numbers issues and PRs in one sequence, so #1 resolves to the right artifact.
     Headings below were migrated to the standard shape by #15; no content line was changed. -->

## Goal

Branch-scoped record of what was done and what remains, so knowledge survives across sessions.
Tracked in git but **excluded from the published docs site** (`exclude_docs` in `mkdocs.yml`).

> Scope note: this is **project/branch state** — distinct from the generalizable BlueprintX
> lessons captured in `docs/blueprintx-lessons.md` (git-ignored) and the global store
> `~/.claude/memory/lessons/`. Lessons = reusable, scaffold-backportable; this backlog =
> what happened on *this* branch and what is still open.

## Work

- [x] Dehydrated the BR/US holiday calendars from `stpstone` into `purecalendars`, laid out as
  `purecalendars.<country>.<provider>` (one public class per module).
- [x] Split the 8-class calendar mixin chain into one file per class under
  `_internal/utils/calendars/`; cache + vendored helpers (parsers, webdriver_tools) under
  `_internal/utils/`.
- [x] ANBIMA read routes through `tabular_reader` + a `FileContract` (never raw `pd.read_excel`);
  extended `read_table` with headerless-Excel support.
- [x] Reused the repo's own `typing` chassis (discarded stpstone's duplicate); broke the
  cache→calendar circular import; swapped `CreateLog`→`LogEmitter`, `PickleFiles`→stdlib pickle.
- [x] **US federal holidays reworked into two classes:** `DatesUSFederalHolidays` (offline, via the
  `holidays` package, applies the §6103 observed-day rule — emits statutory + observed) and
  `DatesUSFederalHolidaysWeb` (the Playwright live scrape).
- [x] **Playwright is now an optional `web` extra** (`pip install "purecalendars[web]"` +
  `playwright install chromium`); base install is browser-free; the Web class raises a clear
  `ImportError` when the extra is absent.
- [x] **`LogEmitter`**: no logger → print to screen; logger → route to it (restored stpstone
  convenience).
- [x] Public API: country subpackages re-export providers; `__version__` via `importlib.metadata`;
  removed the `main.py` placeholder and dead `run` target.
- [x] Tooling: `install_dist_locally` (Makefile + tasks.sh); docs-deploy workflow (`docs.yaml`);
  changelog regenerated at release time via `make changelog` (see the changelog decision below).
- [x] Docs: Home, Usage, Examples, API Reference, FAQ, Contributing, Changelog; logo on README +
  docs homepage; tagline → "Global calendar system."; version-badge CSS; sidebar-title hidden.
  **SUPERSEDED 2026-08-02 by #14 / PR #21:** the version-badge CSS and the whole version-pill
  stack (`overrides/main.html`, `mkdocs_hooks.py`, `docs/javascripts/header-version.js`) were
  **deleted** — the logo now sits in the top bar via Material's native `theme.logo`/`theme.favicon`,
  and the only surviving rule is the sidebar-title one, in `docs/stylesheets/extra.css`. Do not
  read this line as describing the current docs setup.
- [x] Optimized the logo PNGs (were 715 KB / 4.9 MB → ~116 KB / 163 KB) to pass the large-file hook.
- [x] **`add_holidays()` fixed across all providers.** Two bugs, both provider-only (the abc facade
  masked them): (1) providers skip `super().__init__()` → `_added_holidays` was never
  initialised (`AttributeError`); (2) providers override `holidays()`, shadowing the mixin
  merge, so injected holidays never reached `holidays()` / the working-day set. Reworked to a
  **source-hook**: providers now implement `_source_holidays()`, and a single inherited
  `holidays()` (in `DateManipulation`) appends the runtime additions. `_added_holidays` is
  lazily initialised via `_get_added_holidays()`, independent of `__init__`. Regression test
  `test_nasdaq_add_holidays_merges_into_provider` added.
- [x] **Rich-by-default screen logging.** New `LogsEmitter(LogEmitter)` (`_internal/utils/
  logs_emitter.py`) delegates to `logs.py`'s `CreateLog`; wired as `CacheManager`'s default sink,
  so with no logger injected the screen line is now
  `YYYY-MM-DD,HH:MM:SS.mmm INFO {Class} [method] msg` (was bare `[INFO] msg`); inject a logger to
  route there instead. Fixed a latent `logs.py` bug: the caller-context stack-walker used a
  `startswith` skip-set (`"utils.typing"`) that never matched the package-qualified module names —
  switched to last-dotted-component matching so `{Class}` resolves. Base `LogEmitter` stays
  minimal/injectable. Regression test + blueprintx lesson (`rich-default-log-emitter`) captured.
- [x] Version bumped to `0.1.0`. All gates green (ruff, mypy, docstring, 279 tests, mkdocs strict,
  wheel build). PR **#1** open against `main`.

## Open / to-do
- [x] **Changelog moved off CI-push-to-protected-main (no PAT, no bypass).** Deleted
      `changelog.yaml` (it pushed to protected `main`, forcing a `CHANGELOG_TOKEN` PAT +
      branch-protection bypass — the same long-lived secret just removed from PyPI). `CHANGELOG.md`
      is now regenerated from tags by `cz changelog` at **docs-build time** (`docs.yaml`), never
      committed to `main`; `make changelog` remains for local preview. Docs, Makefile + tasks.sh
      updated; blueprintx lesson `changelog-no-ci-push-to-protected-main` captured. **No maintainer
      setup required.**
- [x] **Release pipeline hardened: real test gate + tag-driven dynamic versioning.**
      (1) Dropped the self-attested `tests_passed` input; both release workflows now `needs:` a
      `run_tests` job (full-matrix `tests.yaml`), so publish is gated on tests actually passing.
      (2) Version is now the **git tag** via `poetry-dynamic-versioning`: `pyproject` holds a
      `0.0.0` stub, the release workflow tags `vX.Y.Z` and builds with `python -m build` (Test PyPI
      uses `POETRY_DYNAMIC_VERSIONING_BYPASS`). Deleted `make bump_version` (now offline-only).
      Locally verified: tag→`purecalendars-9.9.8`, bypass→`9.9.9`, no-tag→dev version; `install_dist_
      locally` green. Two blueprintx lessons captured (`release-gate-runs-tests-not-attestation`,
      `versioning-origin-dependent-tag-driven-online`). Split into two revertable commits.
- [x] **PyPI publishing switched to OIDC trusted publishing** (own commit for easy rollback).
      Both release workflows now publish via `pypa/gh-action-pypi-publish@release/v1` under the
      existing `id-token: write` / `environment: release` — no `PYPI_TOKEN` / `TEST_PYPI_TOKEN`
      secret. Docs (`contributing.md`, `CLAUDE.md`) updated; blueprintx lesson
      `pypi-oidc-trusted-publishing` captured. **Maintainer action:** register a trusted publisher
      on **both** pypi.org and test.pypi.org (owner `guilhermegor`, repo `purecalendars`, the workflow
      filename, environment `release`); use a *pending publisher* for the first release. Roll back
      this commit to return to token-based publishing if OIDC misbehaves.
- [x] **Orphan assets deleted:** removed `assets/logo_lorem_ipsum.png` and
      `assets/logo_purecalendars_description.png`; only `logo_purecalendars_no_description.png` (the sole
      referenced variant) remains.
- [x] **Placeholder-version ripple fixed** in the docs badge + local smoke. `mkdocs_hooks.py` now
      derives the masthead version from `git describe --tags --always` (falls back to pyproject
      then `?`) instead of the `0.0.0` stub — verified badge renders `v6d445f3` now / `v0.2.0` on a
      tag. `install_dist_locally` (Makefile + tasks.sh) reports the built wheel's real version
      (e.g. `purecalendars-0.0.0.post15.dev0+6d445f3`) rather than the editable `0.0.0`. `docs_server`
      needed no change (it feeds through the same hook). Lesson updated with the ripple note.
- [x] **`docs.yaml` proven on the remote:** ran green and the site is **live** at
      https://guilhermegor.github.io/purecalendars/ (HTTP 200). Root cause of the initial 404 was Pages
      never being enabled (`gh-deploy` publishes the branch but can't enable serving) — fixed by
      enabling Pages this session. (Being migrated to a self-enabling Actions deploy in PR #5.)
- [x] **BR calendars are offline-first (issue #7), and `DatesBRB3Web` now really scrapes B3.**
      All three BR providers gained the two-class shape the US side already used: offline class
      = default, `*Web` class = the publisher's live page. **The offline source is
      `holidays.B3`, not `holidays.Brazil`** — the issue proposed the latter, but it is the
      statutory-only set and omits Carnaval (Mon+Tue) and Corpus Christi, so it would have
      silently marked Carnaval a working day. Equivalence was verified **before** switching the
      default: over ANBIMA's full published span (2001–2099) the offline set and the fetched
      workbook have an **empty symmetric difference**; FEBRABAN matches too (checked live for
      2025–2026 — the years its endpoint serves). B3 = that set plus the last working day of
      each year, computed locally.
      **`DatesBRB3Web` was rewritten** (per review: it fetched ANBIMA, never B3) to scrape B3's
      own trading calendar. That page is an event feed, so closures are identified by B3's own
      wording (`"não haverá negociação"`), never by event name — US holidays listed for
      reference, `Câmara de Câmbio` notes and reduced-hours sessions all correctly stay working
      days. It reconciles exactly against the offline class: every offline-only date is a
      weekend (B3 omits those — no session to cancel), and the only scrape-only dates are 2021's
      São Paulo municipal/state holidays, which B3 stopped observing afterwards.
      **Two latent cache bugs fixed at the root:** `cache_df` keys ignored the constructor args
      that change the frame, so `DatesBRB3Web(bool_add_christmas_eve=True)` was served the
      no-Christmas-Eve cache and two `DatesBRFebrabanWeb` instances with different year ranges
      collided. The decorator already supported callable keys — only its `key: str` annotation
      blocked them. Also removed two stale `type: ignore[override]` comments that mypy had been
      flagging on `main`.
- [x] **Decide `bool_add_christmas_eve`'s default.** B3's own page publishes 24 December as a
      genuine closure ("não haverá negociação") in every year it falls on a weekday (2021, 2024,
      2025, 2026), which means the offline class's `bool_add_christmas_eve=False` default
      disagrees with the exchange. Left unchanged — flipping it is a behaviour change beyond
      issue #7's scope — but it is now evidence-backed, not a matter of taste.
      **RESOLVED 2026-08-03 by #35: flipped to `True`.** The evidence above was the whole
      argument; what remained was the decision, which is now taken. The drift job's Christmas Eve
      excuse was removed in the same change — with both sides agreeing there is nothing to excuse,
      and keeping it would have suppressed real signal.
- [x] **OIDC `release_*` workflows proven live on the remote (2026-08-01).** Both trusted
      publishers were corrected to the per-index environments (`release_test_pypi` /
      `release_pypi`) and both workflows published end-to-end with no stored token, during the
      `1.0.0` release: Test PyPI run 30696472307 (18/18 jobs green) and PyPI run 30696729122
      (20/20 jobs green, twine uploaded both artifacts with attestations). Tag `v1.0.0` exists and
      the GitHub release is not a draft. Install-verified from both indices
      (`purecalendars.__version__ == "1.0.0"` in a clean venv).
      Earlier failure mode, now resolved: Test PyPI returned `invalid-publisher` while the
      publisher env was the generic `release`.

**Completed — kept as a record.**

# cookie-popup-probe_20260802_081029

# Ledger — #18 cookie-popup-probe

Branch: `fix/18-cookie-popup-probe` · Issue: #18 · Class: **src** (ships in the wheel → release)

## Goal

`PlaywrightScraper._handle_cookie_popup` blocked for a hard-coded **30 s per page** on a site that
has no consent banner at all, and logged the routine outcome at `error`. Make the absent-banner
case cheap and quiet, while keeping a genuinely unclickable banner loud.

## Work

- [x] Confirm the premise before changing anything. `federalholidays.net` HTML contains **zero**
      `accept` / `cookie` / `consent` / `onetrust` / `cookiebot` matches, so `text=Accept All`
      could never match and the full 30 s was paid on every navigation. Also confirmed
      `us/federal_holidays_web.py` is the **only** module in the package that drives Playwright —
      the BR sources do not — so a single English selector is sufficient and no i18n work is in
      scope.
- [x] Probe before clicking. `_handle_cookie_popup` now waits for the banner with a short bounded
      budget and returns early when it does not appear. Both call sites (`navigate()` and the
      json-steps runner, neither of which passes an argument) get the fix without changing.
- [x] Split the two outcomes that were previously one `except`:
      - banner absent → `info`, "No cookie consent banner found; nothing to accept". The normal
        case, not a failure.
      - banner present but the click fails → `error`. A real problem, still loud.
- [x] Replace the magic numbers with named module constants, matching the file's existing
      `_WEB_EXTRA_HINT` convention: `_COOKIE_ACCEPT_SELECTOR`, `_COOKIE_PROBE_TIMEOUT_MS`
      (**1 000**), `_DEFAULT_TIMEOUT_MS` (**30 000**).
- [x] Fix the docstring that claimed `3000ms` while the code said `30_000` — it now documents the
      probe budget and states explicitly that it is *not* the page-load timeout.
- [x] Fix `int_default_timeout: int = 10`. Ten milliseconds feeds `page.goto`, so any caller
      relying on the default could not load a page at all; the sole real call site
      (`federal_holidays_web.py:134`) only worked because it passes `5000` explicitly. Now
      defaults to `_DEFAULT_TIMEOUT_MS`, matching Playwright's own `set_default_timeout` default,
      so the seam behaves like the library it wraps.
- [x] `timeout=` is still honoured, so a source whose banner is injected late can widen the probe
      without touching the seam.
- [x] Tests: `tests/unit/test_playwright_wd.py` — **new file, the module had no tests at all**.
      8 tests over fake locators, so nothing launches a browser and the `conftest.py` socket guard
      stays intact.

## Verification

- `poetry run pytest tests/unit/` → **321 passed** (313 before + 8 new).
- `ruff check` / `ruff format --check` / `mypy` / `pydocstyle` → all clean.
- **Measured end-to-end against the live page** (outside the test suite, which cannot open a
  socket), scraping 2026:

  | | Elapsed | Rows |
  |---|---|---|
  | Pre-fix budget (30 000 ms probe) | **34.83 s** | 11 |
  | This fix (1 000 ms probe) | **6.38 s** | 11 |

  Identical output, **28.4 s saved per page**. The US web source sweeps `year-1 … year` by default
  (2 pages), so the weekly drift job saves **~57 s per US sweep** — matching the estimate on the
  issue.

## Deferred (tracked here, not in this PR)

- The `visible=True` branch of `selector_exists` calls `locator.first.is_visible()`, which ignores
  the `timeout` argument entirely — an instant check wearing a timeout parameter. Not touched
  here because other callers depend on current behaviour, and the cookie probe deliberately does
  not use that helper (see below).

## Not done, on purpose

- **Did not reuse `selector_exists()` for the probe**, even though the issue suggested it. It logs
  a `warning` whenever the selector is missing, which is precisely the mis-levelled noise this fix
  exists to remove — routing the probe through it would have reintroduced the defect one severity
  lower. The probe instead calls `locator.wait_for(state="visible", …)` directly, which is the same
  primitive `selector_exists` uses, and keeps the absent case at `info`.
- **Did not flip `bool_accept_cookies` to `False`** or delete the cookie handling. No page this
  library scrapes has a banner, so both were on the table; keeping it on at ~1 s preserves the
  vendored seam's usefulness for a future source that does show one.
- **Did not widen the selector** beyond `text=Accept All`. A single English string is correct for
  the only Playwright-driven source in the package; widening it should be a deliberate edit made
  when a non-English source is actually added, not speculative matching now.

**Completed — kept as a record.**
