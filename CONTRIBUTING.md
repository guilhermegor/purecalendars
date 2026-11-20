# Contribution Guidelines

Thank you for considering contributing to our project! Please take a moment to review these guidelines to ensure a smooth collaboration.

## Development Conventions

### Variable Naming Standards

We use the following standardized variable naming conventions:

| Variable        | Description |
|-----------------|-------------|
| `int_cddr`      | Integer calendar days redemption period (funding to delivery) |
| `int_wddr`      | Integer working days redemption period (funding to delivery) |
| `int_cddt`      | Integer calendar days total investment period (funding to maturity) |
| `int_wddt`      | Integer working days total investment period (funding to maturity) |
| `int_cddm`      | Integer calendar days per month (convention: 30) |
| `int_wddm`      | Integer working days per month (convention: 22) |
| `int_cddy`      | Integer calendar days per year (convention: 365) |
| `int_wddy`      | Integer working days per year (convention: 252) |
| `int_cd_bef`    | Integer calendar days before (convention: 1) |
| `int_wd_bef`    | Integer working days before (convention: 1) |
| `int_cd_aft`    | Integer calendar days after (convention: 1) |
| `int_wd_aft`    | Integer working days after (convention: 1) |
| `int_cd_cap`    | Integer calendar days capitalization |
| `int_wd_cap`    | Integer working days capitalization |
| `int_nper_cd`   | Integer number of periods (calendar days) |
| `int_nper_wd`   | Integer number of periods (working days) |
| `float_pv`      | Present value of instrument notional (negative for purchasing, positive for selling) |
| `float_fv`      | Future value of instrument notional (negative for purchasing, positive for selling) |
| `float_notional`| Priced value from contract in absolute terms |
| `float_position_value`| Accounting current market value, for taxing purposes |
| `float_acquisition_basis`| Accounting cost basis, for taxing purposes |
| `float_size`    | Size of instrument contract |
| `float_xcg`     | Exchange value for instrument pricing |
| `float_qty`     | Quantity of instruments (positive for purchasing, negative for selling) |
| `date_ref`        | Reference date |
| `date_xpt`        | Maturity date |
| `date_rdm`        | Redemption date |
| `date_start`        | Start date |
| `date_end`        | End date |
| `date_current` | Current date, for iteration puroposes|
| `int_n_smp`     | Number of samples |
| `int_max_retries` | Maximum number of retries |

## Branching Strategy

### Branch Naming Convention

All branches must follow the pattern: `<purpose>/<issue-number>-<slug>`. The issue number is
required: the `Branch has issue` check fails a PR whose branch carries none (`release/*`,
`dependabot/*` and `renovate/*` branches are exempt).

**Available purposes:**

| Purpose         | Format                      | When to Use |
|-----------------|-----------------------------|-------------|
| Feature         | `feature/<name>` or `feat/<name>` | New functionality |
| Bugfix          | `bugfix/<description>` or `fix/<description>` | Bug resolution |
| Hotfix          | `hotfix/<description>` | Critical production fixes |
| Release         | `release/<version>` | Version preparation |
| Documentation   | `docs/<description>` | Documentation updates |
| Refactor        | `refactor/<description>` | Code improvements |
| Chore           | `chore/<description>` | Project maintenance tasks |

**Examples:**
- `feat/12-user-authentication`
- `fix/34-login-validation-issue`
- `docs/56-update-api-reference`

## Commit Message Standards

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification: `<type>/<scope>`

**Available types:**

| Type       | Purpose |
|------------|---------|
| `build`    | Build system or dependency changes |
| `ci`       | CI configuration changes |
| `docs`     | Documentation updates |
| `feat`     | New features |
| `fix`      | Bug fixes |
| `perf`     | Performance improvements |
| `refactor` | Code restructuring |
| `style`    | Formatting changes |
| `test`     | Test additions/modifications |
| `chore`    | Maintenance tasks |
| `revert`   | Reverting changes |
| `bump`     | Version updates |

**Examples:**
- `feat(auth): implement OAuth2 integration`
- `fix(calculations): correct rounding errors in tax computation`
- `docs(readme): add installation instructions`

## Development Setup

1. **Dependency Management**:
   - Use Poetry (version specified in `requirements.txt`)
   - Avoid adding redundant libraries - check `pyproject.toml` first
   - Run `poetry install` to set up the development environment

2. **Pre-commit Hooks**:
   - Install with `bash bin/poe_exec.sh precommit`
   - This enables automatic:
     - Code linting
     - Formatting
     - Security vulnerability scanning
     - Large file detection
     - Secret key detection

3. **Testing Framework**:
   - Maintain the standard file structure:
     - Implementation: `src/<feat_name>.py`
     - Tests: `tests/test_<feat_name>.py`
   - Run comprehensive validation with: `bash bin/poe_exec.sh test_feat <feat_name>`
        - This command executes:
            - **Ruff**: Linting, formatting, and flagging deprecated Python features
            - **Codespell**: Spelling verification in comments and docstrings
            - **Automated tests**: All test cases matching the project's testing standards
   - Ensure 100% test coverage for critical components
   - Run tests locally before pushing changes

4. **Test-Driven Development**:
   - Write tests before implementation when possible
   - Include normal operations, edge cases, error conditions, type validation, and checks for examples in docstrings
   - Maintain test fixtures for complex scenarios
   - Recommended to use UNIT_TEST_TEMPLATE.md for AI generation of unit tests, in order to implement test-driven development best practices and follow project standards

5. **Template Provenance and Drift**:
   - `.blueprintx-provenance.yaml` stamps the BlueprintX template this project came from
     (`lib-minimal`, commit `12e76053`)
   - Compare with a BlueprintX checkout (`--blueprintx-root`, or `BLUEPRINTX_TEMPLATE_ROOT`):
     - `bash bin/poe_exec.sh template_drift --root .` reports missing, template-changed and
       both-changed files; it always exits 0
     - `bash bin/poe_exec.sh template_update --root .` is a dry run; do not pass `--apply` casually
   - Known limits: only files the template still ships are reported (not `poe_tasks.toml`,
     `docs/api.md`); rendered files and `bin/ci/` copies are outside the
     comparison; the vendored tree appears under the placeholder `src/project/...`; the
     stamp keeps only the answers given at scaffold time
   - Details: `docs/contributing.md`, section "Template provenance and drift"

6. **Agent Guidance Files** (for AI coding assistants and human readers alike):
   - `AGENTS.md`: this repository's layout, architecture, conventions, work trackers and
     release process (single source; other agents must be told to read it)
   - `PRINCIPLES.md`: single-responsibility and function-design rules
   - `.claude/CLAUDE.md`: naming, boundary and tooling conventions shared by every BlueprintX
     project (Claude Code loads it on its own)
   - `CLAUDE.md` (root): a bridge that imports `AGENTS.md` and `PRINCIPLES.md`; edit
     `AGENTS.md`, not the bridge
   - Directory-level `AGENTS.md` / `CLAUDE.md` pairs (`tests/`, `src/.../_internal/`) follow the
     same rule; `docs/CLAUDE.md` and `bin/CLAUDE.md` hold their guidance directly
   - `.greptile/`: configuration for the Greptile review bot

## Pull Request Process

1. **Create an Issue First**:
   - Check existing issues at [GitHub Issues](https://github.com/guilhermegor/purecalendars/issues)
   - Open a new issue if none exists for your work

2. **Opening a PR**:
   - Fill out the PR template completely
   - Include:
     - Detailed description
     - Changes made
     - Testing performed
     - Documentation updates
     - Any technical debt created
   - Put one closing keyword per issue in the body, with no colon (`Closes #12`, then
     `Closes #13` on its own line); `Closes: #12` and `Closes #12, #13` do not close what
     follows the first item

3. **What happens after the PR opens**: these workflows run on the PR itself, none of them
   needs a command from you (full detail in `.github/CLAUDE.md`).

   | Workflow | Runs on | What it does |
   |----------|---------|--------------|
   | `PR title conventional` | open, edit, push | Fails unless the title is `type(scope): subject` |
   | `PR body template` | open, edit, push | Fails unless every `## ` heading of `.github/PULL_REQUEST_TEMPLATE.md` is in the body |
   | `Branch has issue` | open, edit, push, (un)assign | Assigns the author when nobody is assigned, then fails unless the branch carries an issue number, the PR has an assignee and it closes (or its branch names) an open issue |
   | `Close linked issues` | merge into `main` | Closes each issue named by a closing keyword or the branch number, with the comment `Delivered in #<PR>` |
   | `Dependabot auto-merge` | Dependabot PRs | Arms squash auto-merge for patch and minor bumps; a major bump waits for a trusted review of the head commit |

   The first three are checks: red means fix the title, body or branch (an edit re-runs
   them). Dependabot and `release/*` branches skip them. Exit code 2 from a check is an API
   or configuration error, not a policy violation: re-run the job.

4. **Code Review**:
   - Expect constructive feedback
   - Address all review comments
   - Update documentation as needed
   - Keep commits logically organized

5. **Merge Approval**:
   - Requires at least one approval
   - All tests must pass
   - Code coverage should not decrease
   - Documentation must be updated

## Docs and Hygiene Guards

Each runs in pre-commit and CI; run one by hand with the command shown.

- `check_docs_sections.py`: the docs nav holds the canonical pages (`python3 bin/check_docs_sections.py`).
- `check_docs_gap.py`: every `docs/` page is in the `mkdocs.yml` nav (`python3 bin/check_docs_gap.py --root .`, needs `pathspec` and `pyyaml`).
- `check_docs_code_refs.py`: imports cited in docs and README resolve against `src/` (`python3 bin/check_docs_code_refs.py`).
- `check_identifier_masking.py`: no masked CPF/CNPJ compared in `.py`/`.sql` (`python3 bin/check_identifier_masking.py`).
- `check_secrets.sh`: gitleaks over the tree and history (`bash bin/check_secrets.sh`); false positives go in `.gitleaks.toml`.
- `check_description_sync.sh`: one description across `pyproject.toml`, `mkdocs.yml` and GitHub About (`bash bin/check_description_sync.sh`).
- `check_clean_index.sh`: pre-push only; refuses a push while staged work sits in the index (`bash bin/check_clean_index.sh`).

## Best Practices

- **Keep branches focused** - one feature/bugfix per branch
- **Make small, frequent commits** - easier to review
- **Write descriptive commit messages** - explain why, not just what
- **Update documentation** - when adding new features
- **Follow existing patterns** - maintain consistency
- **Communicate early** - if you're stuck or need clarification

We appreciate your contributions and look forward to collaborating with you!
