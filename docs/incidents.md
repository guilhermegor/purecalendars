# **Incident Records**

What broke in this project, and what changed so it cannot break that way again. This page
keeps debugging knowledge inside the codebase instead of in git history and one person's
memory — the knowledge a team already paid for once should not have to be paid for twice.

> **See also:** [Usage](usage.md) · [Contributing](contributing.md) · [Changelog](changelog.md).

## Not an ADR, and not a lessons store

An **ADR** records a decision made *before* something went wrong. An incident record documents
one made *because* something already did — different trigger, different audience. If this
project adopts ADRs later, keep the two separate rather than merging them into one grab-bag.

This is also not a copy of a scaffolding tool's own "lessons learned" store. That kind of store
answers "what should every future generated project inherit" — this page answers "what bit
*this* codebase, and what did we do about it." Different audience, different lifetime.

## Published on purpose — redact before you write

This page ships in the published docs site, same as [Usage](usage.md). An incident can carry
production detail (a hostname, a query, a customer-facing symptom) that should not reach a
public site — redact or generalize it before committing the entry, the way an external
postmortem omits internal specifics. If this project's site is genuinely public and entries
cannot stay redacted, exclude `incidents.md` via `exclude_docs` in `mkdocs.yml` instead of
leaving it half-written.

## Format

Five fields, in this order. Keep each to a few sentences — the entry stops getting written the
day it takes an hour to fill in.

- **Symptom** — what was observed, not what was wrong.
- **How it was found** — the tool, command, or accident that surfaced it; "we were careful"
  does not belong here.
- **Root cause** — measured, not assumed.
- **The change** — what now makes this class of failure impossible, or loud instead of silent.
- **How we'd know it regressed** — the gate, test, or assertion that would catch it coming back.

---

No incidents recorded yet. Add the first entry below this line, newest first.
