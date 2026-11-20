"""Integration tests for the project's shared ``bin/`` shell seams.

Bash scripts have no conventional unit test, so this project maps the
tests-with-every-change rule onto shell like this:

- **Unit gate** = ``shellcheck --severity=warning --exclude=SC1091`` + ``bash -n``
  (run by ``bin/lint_shell.sh`` and the ``lint-shell`` pre-commit hook).
- **Integration** = invoke the script via ``subprocess`` and assert on observable
  behaviour (exit code, a created file/dir, a status line) — this module.

See ``tests/CLAUDE.md`` (Testing shell scripts) for the convention. Two seams are
covered: ``bin/poetry_exec.sh`` (the Poetry resolver wrapper every recipe routes
through) and ``bin/precommit.sh`` (hook install that must skip gracefully off a git
work tree instead of aborting ``init``). The repo-policy scripts (``check_pr_policy.sh``,
``close_linked_issues.sh``, ``dependabot_auto_merge.sh``) are exercised through their
source-guarded functions, so no network and no ``gh`` call is needed.
"""

import os
from pathlib import Path
import shutil
import subprocess

import pytest


# --------------------------
# Module Utilities
# --------------------------


def _bin_script(str_name: str) -> Path:
	"""Return the absolute path to a script under the repository's ``bin/``.

	Parameters
	----------
	str_name : str
		The script filename, e.g. ``poetry_exec.sh``.

	Returns
	-------
	pathlib.Path
		Absolute path to ``bin/<str_name>`` at the repository root.
	"""
	return Path(__file__).resolve().parents[2] / "bin" / str_name


def _run(
	str_script: str,
	*args: str,
	cwd: Path | None = None,
	dict_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
	"""Run a ``bin/`` script via bash and capture stdout/stderr separately.

	Parameters
	----------
	str_script : str
		The script filename under ``bin/``.
	args : str
		Arguments forwarded to the script.
	cwd : pathlib.Path or None, optional
		Working directory to run from; defaults to the current directory.
	dict_env : dict of {str: str} or None, optional
		Extra environment variables layered on top of the current environment; ``None``
		inherits the environment unchanged.

	Returns
	-------
	subprocess.CompletedProcess[str]
		The finished process with decoded ``stdout`` and ``stderr``.
	"""
	str_bash = shutil.which("bash") or "bash"
	# A pre-commit hook leaks ``GIT_INDEX_FILE`` (and friends) from the outer repository, which
	# makes a throwaway directory look like a work tree; drop them, then layer the caller's.
	dict_full_env = {
		**{
			str_key: str_val
			for str_key, str_val in os.environ.items()
			if not str_key.startswith("GIT_")
		},
		**(dict_env or {}),
	}
	# The argument vector is constant and trusted -- a resolved bash plus the repo's own
	# script -- with no untrusted input interpolated, so the bandit subprocess warning is
	# a false positive here.
	return subprocess.run(  # noqa: S603
		[str_bash, str(_bin_script(str_script)), *args],
		capture_output=True,
		text=True,
		check=False,
		cwd=str(cwd) if cwd is not None else None,
		env=dict_full_env,
	)


# --------------------------
# bin/poetry_exec.sh
# --------------------------


def test_poetry_exec_no_args_exits_with_usage_error() -> None:
	"""No arguments yields exit code 2 and a usage message routed to stderr."""
	cls_result = _run("poetry_exec.sh")

	assert cls_result.returncode == 2
	assert "Usage" in cls_result.stderr
	assert cls_result.stdout == ""


def test_poetry_exec_version_keeps_stdout_clean() -> None:
	"""``version -s`` returns only the version on stdout; chatter goes to stderr."""
	cls_result = _run("poetry_exec.sh", "version", "-s")
	if cls_result.returncode != 0:
		pytest.skip("Poetry could not be resolved -- offline/CI integration guard only")

	# stdout is exactly the project version -- no resolution chatter leaked in.
	str_version = cls_result.stdout.strip()
	assert str_version != ""
	assert "\n" not in str_version
	assert "Detected OS" not in cls_result.stdout

	# The resolution status the wrapper emits lands on stderr, not stdout.
	assert "Detected OS" in cls_result.stderr


# --------------------------
# bin/precommit.sh
# --------------------------


def test_precommit_skips_gracefully_off_git_tree(tmp_path: Path) -> None:
	"""Run outside a git work tree, the script skips without aborting or creating a repo.

	Parameters
	----------
	tmp_path : pathlib.Path
		Pytest-provided throwaway directory used as a non-git work tree.
	"""
	cls_result = _run("precommit.sh", cwd=tmp_path)

	# Skip-gracefully default -- init must still complete, so exit 0.
	assert cls_result.returncode == 0
	# No repository is fabricated; the template default never runs git init.
	assert not (tmp_path / ".git").exists()
	# The skip is announced, so a missing repo is visible, not silent.
	str_output = cls_result.stdout + cls_result.stderr
	assert "skipping pre-commit hooks" in str_output


def test_precommit_registers_safe_directory_for_shared_worktree(tmp_path: Path) -> None:
	"""A dubious-ownership work tree self-heals: the script registers a git safe.directory.

	Simulates a shared / network checkout owned by another user via
	``GIT_TEST_ASSUME_DIFFERENT_OWNER=1`` plus a throwaway global git config, then asserts the
	script registered the tree (git's own suggested path) instead of mis-detecting it as "no
	repo". The final hook-install step may fail offline (no Poetry), but the safe.directory
	write happens first in ``ensure_git_repo``, so the assertion holds regardless of exit code.

	Parameters
	----------
	tmp_path : pathlib.Path
		Pytest throwaway dir; a real git work tree is initialised inside it.
	"""
	str_git = shutil.which("git")
	if str_git is None:
		pytest.skip("git not available -- integration guard only")

	path_repo = tmp_path / "repo"
	path_repo.mkdir()
	path_home = tmp_path / "home"
	path_home.mkdir()
	path_global_cfg = path_home / ".gitconfig"
	# A real work tree; the throwaway HOME/config isolates the global safe.directory write.
	subprocess.run(  # noqa: S603
		[str_git, "init", "-q", str(path_repo)], check=True
	)

	dict_env = {
		"GIT_TEST_ASSUME_DIFFERENT_OWNER": "1",
		"GIT_CONFIG_GLOBAL": str(path_global_cfg),
		"HOME": str(path_home),
	}
	cls_result = _run("precommit.sh", cwd=path_repo, dict_env=dict_env)
	str_output = cls_result.stdout + cls_result.stderr
	if "dubious ownership" not in str_output and not path_global_cfg.exists():
		pytest.skip("git build does not honour GIT_TEST_ASSUME_DIFFERENT_OWNER -- guard only")

	# The throwaway global config now holds git's own suggested path, which proves the tree
	# resolved and init could keep going instead of the probe misreading it as absent.
	str_cfg = path_global_cfg.read_text(encoding="utf-8") if path_global_cfg.exists() else ""
	assert "safe" in str_cfg
	assert str(path_repo) in str_cfg or "%(prefix)" in str_cfg
	# The self-heal never fabricates a repo and never emits the "no git repo" skip.
	assert "No git repository here" not in str_output


# --------------------------
# bin/check_specs_structure.sh + bin/check_docs_boundary.sh
# --------------------------


def _write(path_file: Path, str_text: str = "x\n") -> None:
	"""Create a file, and any missing parent directories.

	Parameters
	----------
	path_file : pathlib.Path
		The file to create.
	str_text : str, optional
		The file's content.
	"""
	path_file.parent.mkdir(parents=True, exist_ok=True)
	path_file.write_text(str_text, encoding="utf-8")


def test_specs_structure_accepts_a_valid_tree(tmp_path: Path) -> None:
	"""A ``.specs/`` with its CLAUDE.md, a feature tracker and a flat ledger is clean."""
	_write(tmp_path / ".specs" / "CLAUDE.md")
	_write(tmp_path / ".specs" / "features" / "calendars" / "tasks.md", "- [x] done\n")
	_write(tmp_path / ".specs" / "backlog" / "a-topic_20260101_000000.md", "- [ ] todo\n")

	assert _run("check_specs_structure.sh", "--root", str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
	("str_rel", "str_text"),
	[
		(".specs/notes.md", "x\n"),
		(".specs/features/fix/tasks.md", "- [x] done\n"),
		(".specs/features/calendars/notes.md", "x\n"),
		(".specs/features/calendars/tasks.md", "- [?] unknown marker\n"),
		(".specs/backlog/BadName.md", "x\n"),
	],
)
def test_specs_structure_rejects_a_violation(tmp_path: Path, str_rel: str, str_text: str) -> None:
	"""Each layout rule fails: stray entry, type-named or empty feature, bad marker or name."""
	_write(tmp_path / ".specs" / "CLAUDE.md")
	_write(tmp_path / str_rel, str_text)

	assert _run("check_specs_structure.sh", "--root", str(tmp_path)).returncode == 1


@pytest.mark.parametrize("str_rel", ["docs/lessons-learned.md", "docs/design.md"])
def test_docs_boundary_rejects_working_material(tmp_path: Path, str_rel: str) -> None:
	"""A lessons store or a spec artifact under ``docs/`` fails the boundary gate."""
	_write(tmp_path / "docs" / "index.md")
	_write(tmp_path / str_rel)

	assert _run("check_docs_boundary.sh", "--root", str(tmp_path)).returncode == 1


def test_docs_boundary_accepts_published_pages(tmp_path: Path) -> None:
	"""Plain published pages pass."""
	_write(tmp_path / "docs" / "index.md")
	_write(tmp_path / "docs" / "api" / "reference.md")

	assert _run("check_docs_boundary.sh", "--root", str(tmp_path)).returncode == 0


def test_docs_boundary_rejects_a_backlog_directory(tmp_path: Path) -> None:
	"""The retired ledger home (a ``backlog`` folder under ``docs/``) fails the gate."""
	_write(tmp_path / "docs" / "index.md")
	_write(tmp_path / "docs" / "backlog" / "x_20260101_000000.md")

	assert _run("check_docs_boundary.sh", "--root", str(tmp_path)).returncode == 1


# --------------------------
# bin/check_pr_policy.sh + bin/close_linked_issues.sh + bin/dependabot_auto_merge.sh
# --------------------------


def _call(
	str_script: str,
	str_function: str,
	*args: str,
) -> subprocess.CompletedProcess[str]:
	"""Source a ``bin/`` script and call one of its functions, without running ``main``.

	The repo-policy scripts guard ``main`` behind ``BASH_SOURCE == $0``, so sourcing them
	is side-effect free and lets a test reach a function that needs no ``gh`` call.

	Parameters
	----------
	str_script : str
		The script filename under ``bin/``.
	str_function : str
		The shell function to call.
	args : str
		Arguments forwarded to the function. They travel in the environment, not on the
		command line: a lone ``[]`` argument reached Git Bash on Windows as an empty word.

	Returns
	-------
	subprocess.CompletedProcess[str]
		The finished process with decoded ``stdout`` and ``stderr``.
	"""
	str_bash = shutil.which("bash") or "bash"
	dict_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
	dict_env.update({f"CALL_ARG_{int_idx}": str_arg for int_idx, str_arg in enumerate(args)})
	str_call = " ".join([str_function, *(f'"$CALL_ARG_{i}"' for i in range(len(args)))])
	# Constant, trusted argv: the resolved bash, the repo's own script and a call line built
	# here from a function name written in this module -- the data stays in the environment.
	return subprocess.run(  # noqa: S603
		[
			str_bash,
			"-c",
			f'source "$1"; {str_call}',
			"_",
			str(_bin_script(str_script)),
		],
		capture_output=True,
		text=True,
		check=False,
		env=dict_env,
	)


@pytest.mark.parametrize(
	("str_branch", "int_expected"),
	[
		("feat/62-repo-policy", 0),
		("chore/7", 0),
		("dependabot/pip/ruff-0.5", 0),
		("release/1.2.0", 0),
		("feature-without-number", 1),
		("feat/no-number-here", 1),
	],
)
def test_pr_policy_branch_requires_an_issue_number(str_branch: str, int_expected: int) -> None:
	"""A branch passes with ``<type>/<N>-slug`` or an exempt prefix, and fails otherwise."""
	obj_result = _run("check_pr_policy.sh", "branch", dict_env={"BRANCH": str_branch})

	assert obj_result.returncode == int_expected


@pytest.mark.parametrize(
	("str_title", "int_expected"),
	[
		("ci: import the repo-policy workflows", 0),
		("feat(calendars)!: drop the old API", 0),
		("Add stuff", 1),
		("feat:missing space", 1),
		("unknown(scope): subject", 1),
	],
)
def test_pr_policy_title_requires_a_conventional_commit(str_title: str, int_expected: int) -> None:
	"""Only ``type(scope)!: subject`` with a known type is accepted."""
	obj_result = _run("check_pr_policy.sh", "title", dict_env={"TITLE": str_title})

	assert obj_result.returncode == int_expected


def test_pr_policy_body_requires_every_template_section(tmp_path: Path) -> None:
	"""A body missing a template ``## `` heading fails; a complete one passes."""
	path_template = tmp_path / "template.md"
	_write(path_template, "## Summary\n\n## Testing\n")

	obj_ok = _run(
		"check_pr_policy.sh",
		"body",
		dict_env={"BODY": "## Summary\nx\n## Testing\ny\n", "TEMPLATE": str(path_template)},
	)
	obj_missing = _run(
		"check_pr_policy.sh",
		"body",
		dict_env={"BODY": "## Summary\nx\n", "TEMPLATE": str(path_template)},
	)

	assert obj_ok.returncode == 0
	assert obj_missing.returncode == 1
	assert "Testing" in obj_missing.stderr


def test_pr_policy_body_matches_the_shipped_template() -> None:
	"""The shipped PR template, used verbatim as a body, satisfies its own check."""
	path_template = Path(__file__).resolve().parents[2] / ".github" / "PULL_REQUEST_TEMPLATE.md"

	obj_result = _run(
		"check_pr_policy.sh",
		"body",
		dict_env={
			"BODY": path_template.read_text(encoding="utf-8"),
			"TEMPLATE": str(path_template),
		},
	)

	assert obj_result.returncode == 0


@pytest.mark.parametrize(
	("str_assignees", "int_expected"),
	[("guilhermegor", 0), ("", 1), ("   ", 1)],
)
def test_pr_policy_assignee_requires_a_login(str_assignees: str, int_expected: int) -> None:
	"""An empty or blank assignee list fails the check."""
	obj_result = _run("check_pr_policy.sh", "assignee", dict_env={"ASSIGNEES": str_assignees})

	assert obj_result.returncode == int_expected


@pytest.mark.parametrize(
	("dict_env", "int_expected"),
	[
		({"BRANCH": "feat/9-x", "CLOSING_COUNT": "1"}, 0),
		({"BRANCH": "dependabot/pip/x", "CLOSING_COUNT": "0"}, 0),
		({"BRANCH": "docs/no-number", "CLOSING_COUNT": "0"}, 1),
		({"BRANCH": "x", "TITLE": "fix PROJ-12", "TRACKER": "linear"}, 0),
		({"BRANCH": "x", "TITLE": "fix PROJ-12", "TRACKER": "Linear"}, 0),
		({"BRANCH": "x", "TITLE": "PROJ-12", "TRACKER": "linear", "LINEAR_TEAM_KEYS": "Proj"}, 0),
		({"BRANCH": "x", "TITLE": "no key", "TRACKER": "linear", "LINEAR_TEAM_KEYS": "PROJ"}, 1),
		({"BRANCH": "x", "TITLE": "T-5", "TRACKER": "regex", "TRACKER_REGEX": "T-[0-9]+"}, 0),
		({"BRANCH": "x", "TITLE": "none", "TRACKER": "regex"}, 2),
		({"BRANCH": "x", "TITLE": "none", "TRACKER": "jira"}, 2),
	],
)
def test_pr_policy_linked_issue_by_tracker(dict_env: dict[str, str], int_expected: int) -> None:
	"""A closing reference satisfies GitHub; Linear and regex trackers read branch and title.

	Exit 2 marks a misconfiguration (unknown tracker, regex tracker without a regex) and is
	distinct from exit 1, a real policy violation.
	"""
	obj_result = _run("check_pr_policy.sh", "linked-issue", dict_env=dict_env)

	assert obj_result.returncode == int_expected


def test_pr_policy_unknown_subcommand_prints_usage() -> None:
	"""An unknown subcommand exits 2 with a usage line."""
	obj_result = _run("check_pr_policy.sh", "nope")

	assert obj_result.returncode == 2
	assert "usage:" in obj_result.stderr


@pytest.mark.parametrize(
	("str_branch", "str_body", "str_expected"),
	[
		("feat/12-add-x", "", "12"),
		("feat/12-add-x", "Closes #13", "12\n13"),
		("chore/5-y", "Fixes #5 and resolves #6", "5\n6"),
		("chore/5-y", "Refs #5", ""),
		("chore/5-y", "this does not close #8", "5"),
		("chore/5-y", "```\nCloses #9\n```\n<!-- Closes #10 -->\n> Closes #11", "5"),
		("release/1.0.0", "Closes #3", ""),
		("dependabot/pip/x", "Closes #3", ""),
		("docs/2026-11-note", "", ""),
	],
)
def test_close_linked_issues_resolves_the_issue_set(
	str_branch: str, str_body: str, str_expected: str
) -> None:
	"""Branch number plus closing keywords, minus negations, code, comments and quotes."""
	obj_result = _call("close_linked_issues.sh", "resolve_issues", str_branch, str_body)

	assert obj_result.returncode == 0
	assert obj_result.stdout.strip() == str_expected


@pytest.mark.skipif(shutil.which("jq") is None, reason="jq is required to classify updates")
@pytest.mark.parametrize(
	("str_json", "str_expected"),
	[
		('[{"updateType": "version-update:semver-patch"}]', "minor"),
		(
			'[{"updateType": "version-update:semver-minor"},'
			' {"updateType": "version-update:semver-patch"}]',
			"minor",
		),
		('[{"updateType": "version-update:semver-major"}]', "major"),
		(
			'[{"updateType": "version-update:semver-patch"},'
			' {"updateType": "version-update:semver-major"}]',
			"major",
		),
		("[]", "major"),
		("", "major"),
		("not json", "major"),
	],
)
def test_dependabot_auto_merge_classifies_the_update(str_json: str, str_expected: str) -> None:
	"""Only an all-patch/minor update is ``minor``; anything else, even junk, is ``major``."""
	obj_result = _call("dependabot_auto_merge.sh", "classify_update", str_json)

	assert obj_result.stdout.strip() == str_expected
