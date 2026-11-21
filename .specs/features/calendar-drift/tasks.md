# calendar-drift-detector_20260801_121651

# Ledger — #12 calendar-drift-detector

Branch: `feat/12-calendar-drift-detector` · Issue: #12 · Class: **ci** (no `src/` diff → no release)

## Goal

Detect, weekly and automatically, when the offline calendars diverge from the pages their
publishers keep live. Equivalence was verified **once, by hand**, in PR #10 (ANBIMA 2001–2099:
empty symmetric difference). `tests/conftest.py` blocks sockets by design, so no test can ever
re-check it — a scheduled, non-blocking job is the complement to a network-blocked suite, not a
workaround for it. Divergence becomes one self-filing tracking issue, never a red required check.

Model to copy in shape: `filings-cvm/bin/check_contract_drift.py` +
`filings-cvm/.github/workflows/contract-drift.yaml` (that repo's issue #98).

**Shipped in PR #17 (`555277f`), issue #12 closed 2026-08-01.**

## Work

- [x] `bin/check_calendar_drift.py` — compare **dates only, never names** (B3 publishes an event
      feed with free-text wording) across the four pairs:
      `DatesBRB3`↔`DatesBRB3Web`, `DatesBRAnbima`↔`DatesBRAnbimaWeb`,
      `DatesBRFebraban`↔`DatesBRFebrabanWeb`, `DatesUSFederalHolidays`↔`DatesUSFederalHolidaysWeb`.
      `DatesUSNasdaq` is web-only — no offline twin, skip it.
- [x] Reuse the filings-cvm structure rather than reinventing it: `build_issue_body()` with a
      hidden `_ISSUE_MARKER`, `find_open_drift_issue()` matching on label + marker,
      `upsert_issue()` doing `GET issues?state=open&labels=…` then `PATCH` or `POST`, `_api()`
      over `GITHUB_TOKEN`, `main()` returning `0` unconditionally.
- [x] Known-exceptions allowlist as a module-level constant, each entry commented with its PR #10
      evidence so widening it is a deliberate edit:
      - B3 offline-only dates falling on a **weekend** (B3 omits them — no session to cancel);
      - the **2021 São Paulo** municipal/state dates (scrape-only; B3 stopped observing them).
- [x] Clamp the comparison span per pair — **implemented as a runtime derivation from the web
      side**, not a per-pair constant: `DatesBRB3Web` and `DatesBRAnbimaWeb` take no year range at
      all (they publish what they publish), so `clamp_to_web_span()` reads min/max year off the
      fetched set. A hard-coded span would rot the moment B3 publishes another year.
- [x] `.github/workflows/calendar-drift.yaml` — weekly `schedule` (`37 6 * * 1`) +
      `workflow_dispatch: {}`; `permissions: {contents: read, issues: write}`;
      `concurrency: {group: calendar-drift, cancel-in-progress: false}`;
      `poetry install --extras web` + `poetry run playwright install --with-deps chromium`.
- [x] Put the non-blocking rationale in the workflow header comment **and** the module docstring.
- [x] `tests/unit/test_check_calendar_drift.py` — **33 tests**, socket guard intact throughout (no
      `allow_network` anywhere). The tests written after their code were **mutation-checked**:
      disabling the weekend allowance, dropping Christmas Eve from the allowlist, removing the span
      clamp and making `main()` return 1 each turned exactly the intended test red, then restored.
- [x] Verify on the remote: run
      [30725271837](https://github.com/guilhermegor/purecalendars/actions/runs/30725271837) —
      `workflow_dispatch` on `main`, **cold runner, no cache**, all 10 steps green including the
      Chromium install. Output: `no calendar drift detected (0 source(s) could not be checked)` —
      all four pairs fetched live, zero divergence. Independently reconfirms PR #10's hand
      verification from a clean environment.

## Two bugs found by running it before shipping

Both were caught because the job was exercised against the real sources *before* merge, not after:

- [x] **The `*Web` classes cache by default.** A drift detector that reads a cache cannot detect
      drift — and a *partial* cache from an earlier failed fetch is reported **as** drift.
      Measured: 2 of 22 US dates served stale → **9 false positives**. Had it shipped, the first CI
      run would have filed fabricated findings and the natural "fix" would have been widening the
      allowlist, permanently blinding the job. Fixed with an `_uncached()` wrapper at the registry
      plus a test asserting it for every pair.
- [x] **Read failures opened the drift issue.** federalholidays.net timed out mid-testing, which
      showed an outage filing a "calendar drift" issue naming no drift — the cry-wolf that makes a
      drift job worse than nothing. `collect_drift()` now returns `(problems, errors)` separately;
      errors never open the issue, they only ride along in the body when one opens for real drift.

## Deferred (tracked here, not in this PR)

- **24 December — decided: allowlisted.** `b3_known_web_only()` excuses it for every year the
  source returns. B3 publishes it as a genuine closure in every year it falls on a weekday while
  `DatesBRB3` defaults to `bool_add_christmas_eve=False`, so unexcused the job would restate the
  same *known* disagreement every single week — noise that drowns the signal it exists to carry.
  The decision on the default itself stays open in `dehydrate-calendars_20260704_130854.md`.
- **The upsert's write half is unverified.** `POST` (open) and `PATCH` (update) never ran, because
  there was no drift to trigger them. The pure helpers are unit-tested and `_api()` was verified
  live on the `GET`, but the open-then-update pair is unproven. Symptom to watch on the first real
  drift: a finding in the logs with no issue opened. Recorded on issue #12 too.

## Not done, on purpose

- Flipping `bool_add_christmas_eve` — still open in
  `dehydrate-calendars_20260704_130854.md`. This job gives that decision more evidence; it does
  not resolve it.
- Making the check blocking, or moving it into the test suite. Both defeat the reason it exists.
- Fixing `PlaywrightScraper`'s 30 s cookie-popup timeout, surfaced by this job's first run and
  filed as **#18**. Out of scope here — the sweep degrades correctly (`could not check`, never
  drift); the timeout is latency and log noise, not incorrectness.

## Lesson captured

`drift-job-must-disable-the-client-cache` — BlueprintX store + README index +
`docs/blueprintx-lessons.md`. The general rule: **cache/retry/timeout policy is a property of the
caller's intent, not the client**; when a job reuses a production client for a purpose it was not
written for, audit every default it carries. Sibling of the existing
`probe-injects-fail-fast-retry-not-patient-production-policy` (same shape, one knob over).

**Completed — kept as a record.**

# ci-hygiene-drift-upsert_20260803_081325

# Ledger — #33 ci-hygiene-drift-upsert

Branch: `chore/33-ci-hygiene-drift-upsert` · Issue: #33 · Class: **ci** (no `src/` diff → no release)

## Goal

Close two items that were recorded as *deferred* in earlier ledgers with no issue of their own: the
dead win32 transform in `tests.yaml`, and the never-executed **write** half of the drift detector's
`upsert_issue`.

## Work

- [x] **Removed the win32 transform** from `tests.yaml`'s `Install Dependencies`. purecalendars declares
      no `pywin32` — verified: zero hits in `pyproject.toml`; the `win32` strings in `poetry.lock`
      are transitive wheel *filenames*, not declarations. The step now just installs. Left a comment
      saying why, so it is not "restored" as a template drift-fix later.
- [x] **Covered `upsert_issue`'s write half** with 5 tests driving a stubbed `_api`:
      - no open tracker → exactly **one POST** to `/issues` with title, body and label;
      - an existing tracker → **one PATCH** to `/issues/{n}` and **no POST** (the dedupe the #12
        ledger called the part most likely to be wrong);
      - the GET filters by `state=open` **and** the label;
      - the written body carries the marker `find_open_drift_issue` matches on — and that function
        is then run against the produced body, closing the loop between the two halves;
      - a "could not check" error still reaches the body.

## Why the existing tests did not already cover this

Every prior test does `monkeypatch.setattr(drift, "upsert_issue", …)` — it **replaces the function
being named**. That tests whether `main` *decides* to call it; the function's own body never runs.
Combined with there having been no real drift, the GET→PATCH-or-POST logic had executed **nowhere**:
not in production, not in CI, not in a test.

Generalisable: *a test that stubs the function in its own name is testing the caller, not the unit.*

## Verification

- [x] `poetry run pytest tests/unit/test_check_calendar_drift.py` → **38 passed** (33 + 5).
- [x] **Mutation-tested, because a test that cannot fail proves nothing** (see
      `every-gate-needs-a-should-fail-test`):
      - forcing `upsert_issue` to always POST → only
        `test_upsert_issue_updates_in_place_when_one_exists` fails. Exactly the intended detector.
      - dropping `_ISSUE_MARKER` from the body → the marker tests fail, including the loop-closing
        one.
      - source restored afterwards; `git diff` clean and the suite green again.
- [x] No network: `_api` is monkeypatched, so the `conftest.py` socket guard stays intact.

## Deferred (tracked here, not in this PR)

- **`release_pypi.yaml` and `release_test_pypi.yaml` carry the same dead win32 transform** — and
  something worse next to it, found while checking whether to remove it there too:

  ```
  if ! poetry check --lock; then
    rm -f poetry.lock
    poetry lock --no-cache
  ```

  That is the exact anti-pattern `tests.yaml` was deliberately fixed away from
  (`ci-lock-fail-loud-not-regenerate`): it **silently re-resolves every dependency** to the latest
  in-range version, producing a non-reproducible build — **in the release path**. Deliberately not
  touched here: the release workflows are the least-rehearsed code in the repo (the Test PyPI run
  does not share every step), so they deserve one considered PR rather than a drive-by edit inside a
  hygiene change. Filed separately.
  **RESOLVED 2026-08-03 as #39 / PR #40** — which also found that both release workflows carried all
  three of #19's cache defects on top of the regeneration fallback, and that the ledger gate crashed
  outright on Windows (cp1252 could not encode its status glyphs). No longer open work.

## Not done, on purpose

- Did not remove the transform from the two release workflows, for the reason above — removing it
  there means opening that file, and that file needs the lock-regeneration decision made at the same
  time.

**Completed — kept as a record.**
