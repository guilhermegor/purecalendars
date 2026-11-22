# Ledger — #119 ruleset-strict-off

Branch: `fix/119-ruleset-strict-off` · Issue: #119 · Class: **ci**

## Goal

Port blueprintx#1283 (template PR blueprintx#1284): the `pr-quality-gate` ruleset runs with
`strict_required_status_checks_policy=false`, because strict mode pushed every open PR behind
base after each merge. The live ruleset was already switched off on 2026-11-21.

## Work

- [x] `bin/enable_repo_rules.sh` creates the ruleset with strict off
- [x] Both verify paths (ruleset and classic branch protection) require strict `false`

## Completed — kept as a record

Code-only change; no repo settings touched.
