# `.github/` — CI and recurrent automation

Guidance for Claude Code and contributors working in this project's `.github/`.

## What ships by default

CI is **event-driven** — workflows triggered by `push`, `pull_request` and
`pull_request_target`, plus manual `workflow_dispatch` releases. Nothing here runs on a
clock. That is deliberate: a scheduled job runs whether or not anyone needs it, costs runner
minutes, and can fail silently long after the person who added it has moved on.

**Add a time-triggered job only when the project genuinely needs one, and write
down *why* in the workflow file.**

## What happens to a PR after it opens

Five repo-policy workflows act on a pull request. Each owns one purpose and one event, so no
two act on the same event for the same purpose. The logic lives in `bin/` and is tested by
`tests/integration/test_bin_scripts.py`; the workflow files only wire events to those scripts.

| Workflow | Event | Script | Purpose |
|----------|-------|--------|---------|
| `pr-title-conventional.yml` | `pull_request_target` open, edit, sync, reopen | `check_pr_policy.sh title` | Title is `type(scope)!: subject` |
| `pr-body-template.yml` | `pull_request_target` open, edit, sync, reopen | `check_pr_policy.sh body` | Body has every `## ` heading of `PULL_REQUEST_TEMPLATE.md` |
| `branch-has-issue.yml` | `pull_request_target` open, edit, sync, reopen, (un)assign | `check_pr_policy.sh branch\|assignee\|linked-issue` | Issue number in the branch, an assignee, a closing or open linked issue |
| `close-linked-issues.yml` | `pull_request` closed (merged into the default branch) | `close_linked_issues.sh` | Closes the issues the PR names |
| `dependabot-auto-merge.yml` | `pull_request_target` open, sync; `pull_request_review` | `dependabot_auto_merge.sh` | Arms (or disarms) auto-merge on Dependabot PRs |

Things that bite:

- **Self-assignment is a job of `branch-has-issue.yml`**, not a separate workflow. A separate
  `pr-self-assign.yml` raced the check on `opened`, and an assignment made with `GITHUB_TOKEN`
  never re-triggers workflows. The `check` job `needs:` the `assign` job, and the check reads
  assignees live from the API.
- **`pull_request_target` runs the base branch's workflow and scripts**, never the PR's: a PR
  cannot weaken its own checks, and a change to `bin/check_pr_policy.sh` takes effect only
  after it merges. The checkouts pin `ref: <base sha>` and `persist-credentials: false` for
  the same reason; never add a step that executes PR-head code in these workflows.
- **Closing keywords**: one per issue, no colon (`Closes #12`). `Closes: #12` and
  `Closes #12, #13` link but close nothing past the first. The PR must target the default
  branch. `close_linked_issues.sh` ignores keywords in code fences, inline code, HTML comments,
  quotes and negations ("does not close #8"), and a body `Refs #N` on the branch's own issue
  turns the branch-number closing off.
- **Exit codes of `check_pr_policy.sh`**: 1 is a policy violation, 2 a misconfiguration or an
  unreadable API (not the author's fault: re-run the job).
- **Dependabot and `release/*`/`renovate/*` branches are exempt** from the branch and
  linked-issue checks, and Dependabot PRs skip the title, body and assignee checks (a bot-typed
  author is excluded). Bot-authored PRs are likewise exempt from the work-ledger gate
  (`bin/check_backlog_ledger.py`), which is what keeps Dependabot PRs green without a ledger.
- **Auto-merge** needs the repository setting *Allow auto-merge* and branch protection with
  required checks (otherwise GitHub merges at once or refuses). A patch/minor bump arms
  `gh pr merge --auto --squash`, which merges once the required checks pass. A major bump is armed only after a trusted human review (`OWNER`, `MEMBER`,
  `COLLABORATOR`), or a review-bot listed in `.github/.review-bots.yaml` if the repo has one,
  on the exact head commit; a changes-requested review disarms it. Any commit on the PR that
  Dependabot did not author and sign disarms it.
- **Tracker choice**: `branch-has-issue.yml` reads the repository variables `PR_TRACKER`
  (`github` by default, or `linear` / `regex`), `PR_TRACKER_REGEX` and `PR_LINEAR_TEAM_KEYS`.

To change a policy, edit `bin/check_pr_policy.sh` (or the matching script) and its tests in the
same PR; change a workflow file only to rewire an event.

## Recurrent (scheduled) workflows

To run a workflow on a schedule, add an `on.schedule` trigger with a cron
expression:

```yaml
on:
  schedule:
    - cron: '0 3 * * 1'   # 03:00 UTC every Monday
  workflow_dispatch: {}    # also allow a manual run from the Actions tab
```

Gotchas that bite people:

- **Cron is UTC**, always — not your local timezone. Convert deliberately.
- **Minimum granularity is 5 minutes**; anything finer is rejected.
- **Runs can be delayed** (sometimes by many minutes) when GitHub's runner pool
  is busy — never rely on exact timing.
- **Scheduled workflows auto-disable after ~60 days of repository inactivity**
  (no pushes). They resume only when someone pushes or re-enables them.
- Always pair `schedule` with `workflow_dispatch` so you can trigger a run
  on demand without waiting for the next tick.

Common legitimate uses: nightly end-to-end tests, a scheduled CodeQL / security
scan, a stale-issue/PR bot, cache warming, scheduled data refresh.

## Dependency updates (Dependabot)

Dependabot version updates are a worked example of "recurrent automation". They
live in `.github/dependabot.yml`, and the `schedule.interval` key is
**mandatory** — there is no manual-only cadence. Pick one:

- `daily` — fast-moving app with active maintainers watching the PR queue.
- `weekly` — the typical default.
- `monthly` — low-churn project or a stable library.

This repo updates weekly: GitHub Actions (one grouped PR, with a 7-day cooldown so a freshly
published release is not adopted at once) and Poetry deps (`lockfile-only`, minor and patch
grouped, majors alone, pandas majors ignored). Each PR is assigned to the owner. See the header
of `dependabot.yml` for why `poetry.lock` is the thing being kept fresh.

### Want updates with no cadence?

Enable **Dependabot security updates** instead — they are *event-driven* (a PR
opens only when a CVE advisory matches a dependency), need **no**
`dependabot.yml`, and run on no schedule at all. Turn them on in
*Settings → Code security → Dependabot*, or via the API:

```bash
gh api -X PUT repos/{owner}/{repo}/vulnerability-alerts
gh api -X PUT repos/{owner}/{repo}/automated-security-fixes
```

## Publishing packages — prefer OIDC / trusted publishing over stored tokens

When a release workflow publishes a package to a registry, default to the registry's **OIDC /
trusted-publishing** flow — **never** a stored long-lived API token committed as a secret.
For PyPI / Test PyPI that is `pypa/gh-action-pypi-publish@release/v1` with no `password:`.

Rules:

- Set `permissions: id-token: write` on the publish job and bind it to a **GitHub Environment**
  (per-index, self-documenting: `release-pypi`, `release-test-pypi`).
- **Never commit a long-lived token.** Fall back to a short-lived scoped token **only** where the
  registry/CI lacks OIDC (trade-off: OIDC works only from CI — keep a token if you must publish
  from a laptop).
- The trusted publisher's claims (owner, repo, **exact workflow filename**, environment) and its
  registered project name must match the running workflow, or the upload fails with an opaque
  `invalid-publisher`. Register a *pending publisher* before the first release.

## Gate parity — every gate in BOTH pre-commit and CI

CI runs its gates as **explicit steps** in `tests.yaml`, not via `pre-commit run`, so adding a
hook to `.pre-commit-config.yaml` does **not** cover CI. Every lint/static/test gate must be
wired into **both** files, in the same change — otherwise a `--no-verify` commit or an
uninstalled hook slips straight past branch-protection CI (which runs the workflow, not local
hooks).

## Validating CI locally with `act`

`act` runs the workflow in a local Docker container — a fast loop for the legs it can run,
complementary to (not a replacement for) pushing so the full matrix runs on GitHub's runners.

- It only runs **Linux** — narrow every invocation with `--matrix os:ubuntu-latest`; let
  GitHub cover the `macos`/`windows` legs.
- Validate the **risky single leg**, not the whole matrix.
- **Docker Desktop on Linux** puts its socket at `~/.docker/desktop/docker.sock` — export
  `DOCKER_HOST=unix://$HOME/.docker/desktop/docker.sock` or `act` reports the daemon is down.
- The `pull_request_target` policy workflows read PR event fields: feed `act` an event file, or
  test the script directly (`BRANCH=feat/1-x bash bin/check_pr_policy.sh branch`).

## Blocked work

Work that cannot start because an upstream is unfinished carries the `state:blocked` label and a
`**Blocked by:**` line at the start of a body line, naming each blocker as `repo#N`, or as
`decision: <why>` when the blocker is a choice nobody has made yet.
`ISSUE_TEMPLATE/feature_or_fix.md` carries the line and an `issue-template-guard:` directive; a
tool that reads the directive rejects a `state:blocked` issue without the line. A `decision:`
blocker is never auto-cleared by a reconciler.

Use the native `blocked_by` relationship as an extra mirror for same-repo blockers; it cannot name
a blocker in another repository, so the body line is the record.
