# christmas-eve-default_20260803_093846

# Ledger — #35 christmas-eve-default

Branch: `fix/35-christmas-eve-default` · Issue: #35 · Class: **src** (ships in the wheel → release)

## Goal

Default `DatesBRB3.bool_add_christmas_eve` to `True`, so the offline calendar agrees with the
exchange it models. Closes the decision left open in the 1.0.0 ledger.

## Semantics, confirmed in the code before changing anything

`True` **makes 24 December a holiday** — `holidays_to_add` appends
`("Vespera de Natal", get_christmas_eve(year))` to the non-trading-day list. So `True` is the value
that matches B3, which publishes the date as a closure. Verified, not assumed.

## Work

- [x] `src/wwdates/br/b3.py`: default → `True`; parameter docstring rewritten, including the
      weekend caveat and how to restore the old behaviour.
- [x] `bin/check_calendar_drift.py`: **removed** the Christmas Eve entry from `b3_known_web_only`,
      keeping the 2021 São Paulo group. Docstring rewritten — it asserted
      `DatesBRB3 defaults to bool_add_christmas_eve=False`, which this change makes false.
- [x] `tests/unit/test_calendar_br.py`: `test_b3_christmas_eve_is_opt_in` → `..._is_opt_out`, with
      the assertions inverted and a guard asserting the chosen year's 24 Dec is a **weekday** (on a
      weekend year the test would pass for the wrong reason).
- [x] `tests/unit/test_check_calendar_drift.py`: the test asserting the excuse now asserts its
      **absence**, with the reason. Dropped the span-following test — `set_web` is unused now.
- [x] `docs/api.md` (a **published** page): the example showed `False`, and the prose framed the
      flag as opt-in. Both corrected, plus a "Changed in 1.1" note telling anyone relying on the old
      behaviour to pass `False` explicitly.
- [x] Marked the decision resolved in `dehydrate-calendars_20260704_130854.md` additively.

## Why the excuse had to go, not just be left harmless

`b3_known_web_only` excused 24 Dec in the **web-only** direction *because* the offline side omitted
it. With both sides agreeing, the entry excuses a non-difference — and that is worse than dead code:
if B3 ever stopped publishing 24 December on a weekday while the offline calendar still added it,
the excuse would **hide exactly the divergence the job exists to catch**.

## Verified drift-safe before touching the default

The `br.b3` pair already sets `bool_offline_only_weekend_ok=True`, so:

| Year shape | After the flip | Handled by |
|---|---|---|
| 24 Dec on a weekday | present on both sides → not a difference | nothing needed |
| 24 Dec on a weekend | offline-only (B3 omits weekends — no session to cancel) | the existing weekend rule |

So no new allowlist entry is required, in either direction.

## Verification

- [x] `poetry run pytest tests/unit/` → **360 passed**.
- [x] **Behaviour demonstrated end to end**, offline: for 2026-12-24 (a **Thursday**, so the
      meaningful case) — `DatesBRB3().is_working_day(...)` → **False** (was `True`);
      `DatesBRB3(bool_add_christmas_eve=False).is_working_day(...)` → `True`; and the holiday list
      names it `Vespera de Natal`.
- [ ] After release: the weekly drift job should report **no** Christmas Eve divergence for the
      published span — the first run where the removed excuse is not covering for the default.

## Deferred (tracked here, not in this PR)

- **`get_christmas_eve` returns `date(year, 12, 24)` with no weekday check.** Harmless for
  working-day arithmetic (a weekend is already non-working) but it puts a "holiday" in the list for
  a year like 2022, where 24 Dec is a Saturday and B3 lists nothing. Out of scope: it is a separate
  question about whether the offline set should mirror B3's omissions exactly.

## Not done, on purpose

- **Did not decide the version bump here.** This changes computed results for any consumer calling
  `DatesBRB3()` — settlement dates, working-day counts. It is arguably a `fix` (the old default
  disagreed with the source of truth) and arguably breaking (the old default was observable API
  behaviour). That call belongs to the release step, with the diff in hand.

# version-note-2-0_20260803_094950

# Ledger — #37 version-note-2-0

Branch: `docs/37-version-note-2-0` · Issue: #37 · Class: **src** (docstring only, no behaviour change)

## Goal

Correct three version strings written in #35/#36 **before** the version was decided. They said
`1.1` / `pre-1.1`; the release is **2.0.0**, so as written the published API reference would point
users at a version that never ships.

## Work

- [x] `docs/api.md` — `!!! note "Changed in 1.1"` → `"Changed in 2.0"`, and `pre-1.1 behaviour` →
      `pre-2.0 behaviour`.
- [x] `src/wwdates/br/b3.py` — `pre-1.1 behaviour` → `pre-2.0 behaviour` in the parameter docstring.
- [x] Confirmed no other `1.1` reference survives in either file, and that the **`1.0.1`** mention
      stays — that one names a real released version and is correct.

## Why this had to land before the release, not after

`docs/api.md` is a **published** page and the docstring ships **inside the wheel**. Publishing 2.0.0
with these strings means the 2.0.0 API reference tells a reader to pass `False` to get "the pre-1.1
behaviour" — a version that will never exist. After a publish the wheel is immutable: fixing it would
cost a 2.0.1 released purely for prose.

This is the `changing-a-default-means-removing-its-compensations` lesson applied to my own writing:
I wrote a version number before the decision existed, so the number became a stale assertion the
moment the decision was taken. The general form — **never write a not-yet-decided version into
shipped text** — is why the ledger for #35 deliberately left the bump undecided but the docs did not.

## Verification

- [x] `poetry run pytest tests/unit/` — 360 passed (docstring-only change, nothing behavioural).
- [x] `poetry run mkdocs build --strict` — clean; `docs/api.md` is a published page.
- [x] `ruff` / `ruff format --check` / `mypy` — clean.
- [x] Grepped both files: zero remaining `1.1` / `pre-1` references.

## Deferred (tracked here, not in this PR)

- Nothing.

## Not done, on purpose

- Did not touch the `1.0.1` reference — it correctly names the last release in which the old default
  applied.
- Did not add the version to more places. The changelog is generated from tags by `cz changelog`, so
  the `!` / `BREAKING CHANGE:` trailer on #36 already carries the breaking notice without any
  hand-written version string.

**Completed — kept as a record.**
