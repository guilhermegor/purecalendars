"""Integration tests for the work-ledger gate's command-line behaviour.

``tests/unit/test_check_backlog_ledger.py`` covers the pure rule by calling ``check()`` directly.
That cannot reach the part this module exists for: the ``__main__`` block, where the **bot
exemption** lives and where the branch diff is resolved from git and the environment.

Why that needs its own test — the exemption is an early return placed **before** the base is
resolved or any path is classified, so it is correct for a bot PR touching *any* path. Nothing in
the unit suite pins that ordering: move the bot check after the path work and the exemption would
silently stop covering the one case it exists for — a Dependabot PR touching ``ci``/``src``, which
can never carry a ledger and would go permanently red.

Each case builds a throwaway git repo and invokes the script exactly as pre-commit and CI do. The
PR author reaches the gate through the ``GITHUB_EVENT_PATH`` payload, never ``GITHUB_ACTOR``.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


# --------------------------
# Module Utilities
# --------------------------


def _env_without_git_vars() -> dict[str, str]:
	"""Return the ambient environment minus every ``GIT_*`` variable.

	A pre-commit hook runs with ``GIT_INDEX_FILE`` (and friends) pointing at the *outer*
	repository. Inherited by a git call inside the throwaway repo, it makes ``git commit`` write
	to the wrong index and fail, so the suite went red only when run from the commit hook.

	Returns
	-------
	dict[str, str]
		A copy of ``os.environ`` without ``GIT_*`` keys.
	"""
	return {
		str_key: str_value
		for str_key, str_value in os.environ.items()
		if not str_key.startswith("GIT_")
	}


def _git(cls_repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
	"""Run a git command inside a throwaway repository.

	Parameters
	----------
	cls_repo : pathlib.Path
		Working directory for the command.
	*args : str
		Arguments after the ``git`` executable.

	Returns
	-------
	subprocess.CompletedProcess of str
		The completed process.
	"""
	str_git = shutil.which("git") or "git"
	# Trusted, constant argv built from test-local literals only — bandit S603.
	return subprocess.run(  # noqa: S603
		[str_git, *args],
		cwd=cls_repo,
		capture_output=True,
		text=True,
		check=True,
		env=_env_without_git_vars(),
	)


def _seed_repo(
	cls_repo: Path, str_changed_path: str, *, bool_with_default_branch: bool = True
) -> None:
	"""Create a repo with a base commit, then a feature branch that commits one change.

	The gate diffs against ``merge-base(<default branch>, HEAD)`` and treats "HEAD already is the
	base" as nothing to check, so the change must sit on a branch of its own.

	Parameters
	----------
	cls_repo : pathlib.Path
		Directory to initialise as a repository.
	str_changed_path : str
		Repo-relative path to create and commit on the feature branch.
	bool_with_default_branch : bool, optional
		When ``False`` the base commit is made on ``feature`` itself, leaving no ``main`` or
		``master`` for the gate to resolve a base from.
	"""
	str_first = "main" if bool_with_default_branch else "feature"
	_git(cls_repo, "init", "--quiet", f"--initial-branch={str_first}")
	_git(cls_repo, "config", "user.email", "test@example.com")
	_git(cls_repo, "config", "user.name", "test")
	_git(cls_repo, "config", "commit.gpgsign", "false")
	(cls_repo / "README.md").write_text("seed\n", encoding="utf-8")
	_git(cls_repo, "add", "README.md")
	_git(cls_repo, "commit", "--quiet", "-m", "chore: seed")
	if bool_with_default_branch:
		_git(cls_repo, "checkout", "--quiet", "-b", "feature")

	cls_target = cls_repo / str_changed_path
	cls_target.parent.mkdir(parents=True, exist_ok=True)
	cls_target.write_text("x = 1\n", encoding="utf-8")
	_git(cls_repo, "add", str_changed_path)
	_git(cls_repo, "commit", "--quiet", "-m", "feat: change")


def _run_gate(
	cls_repo: Path, str_author: str | None, str_io_encoding: str | None = None
) -> subprocess.CompletedProcess[str]:
	"""Invoke the gate the way pre-commit and CI do: no arguments, env-driven.

	Parameters
	----------
	cls_repo : pathlib.Path
		The throwaway repository to run inside.
	str_author : str or None
		PR author written into a ``GITHUB_EVENT_PATH`` payload; ``None`` sets no payload at all
		(a human, local run).
	str_io_encoding : str or None, optional
		Value for ``PYTHONIOENCODING``, used to reproduce a non-UTF-8 console such as Windows'
		cp1252 default. ``None`` leaves the interpreter default.

	Returns
	-------
	subprocess.CompletedProcess of str
		The completed process, for exit-code and message assertions.
	"""
	cls_script = Path(__file__).resolve().parents[2] / "bin" / "check_backlog_ledger.py"
	dict_env = _env_without_git_vars()
	# Cleared first so an ambient CI value cannot decide the outcome.
	for str_var in ("GITHUB_EVENT_PATH", "GITHUB_ACTOR", "GITHUB_BASE_REF"):
		dict_env.pop(str_var, None)
	if str_author is not None:
		cls_event = cls_repo.parent / f"{cls_repo.name}-event.json"
		cls_event.write_text(
			json.dumps({"pull_request": {"user": {"login": str_author}}}), encoding="utf-8"
		)
		dict_env["GITHUB_EVENT_PATH"] = str(cls_event)
	if str_io_encoding is not None:
		dict_env["PYTHONIOENCODING"] = str_io_encoding

	# `encoding="utf-8"` is required, not cosmetic: the gate forces UTF-8 on its own stdout, and
	# `text=True` alone would decode with the parent's locale encoding (cp1252 on Windows),
	# turning the glyphs into mojibake on the reading side after they were written correctly.
	#
	# Trusted, constant argv: the interpreter plus a repo-local script path — bandit S603.
	return subprocess.run(  # noqa: S603
		[sys.executable, str(cls_script)],
		cwd=cls_repo,
		capture_output=True,
		text=True,
		encoding="utf-8",
		check=False,
		env=dict_env,
	)


# --------------------------
# Tests
# --------------------------


@pytest.mark.parametrize(
	"str_changed_path", ["src/purecalendars/thing.py", ".github/workflows/x.yaml"]
)
def test_a_bot_pr_is_exempt_even_on_a_ledger_class_path(
	tmp_path: Path, str_changed_path: str
) -> None:
	"""THE case the exemption exists for: a bot PR touching src/ci, carrying no ledger.

	This is what could not be proven from a live Dependabot PR — the ones observed so far changed
	only ``poetry.lock`` (class ``deps``), which is exempt by path anyway. Here the path genuinely
	demands a ledger, so only the exemption can produce exit 0.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	str_changed_path : str
		A path whose risk class demands a ledger (``src`` and ``ci`` respectively).
	"""
	_seed_repo(tmp_path, str_changed_path)

	cls_proc = _run_gate(tmp_path, "dependabot[bot]")

	assert cls_proc.returncode == 0, cls_proc.stdout + cls_proc.stderr
	assert "authored by a bot" in cls_proc.stdout


def test_the_same_diff_from_a_human_fails(tmp_path: Path) -> None:
	"""The should-fail half: identical diff, human author, no ledger -> exit 1 with the reason.

	Without this the test above could pass because the gate examined nothing.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py")

	cls_proc = _run_gate(tmp_path, "octocat")

	assert cls_proc.returncode == 1, cls_proc.stdout + cls_proc.stderr
	assert "adds no work ledger" in cls_proc.stdout


def test_a_local_run_with_no_event_payload_stays_enforced(tmp_path: Path) -> None:
	"""No ``GITHUB_EVENT_PATH`` and no actor (a local pre-commit) exempts nobody.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py")

	cls_proc = _run_gate(tmp_path, None)

	assert cls_proc.returncode == 1, cls_proc.stdout + cls_proc.stderr


def test_the_bot_check_precedes_base_resolution(tmp_path: Path) -> None:
	"""Pin the ORDERING: the exemption must short-circuit before any git work happens.

	With no ``main`` or ``master`` the gate cannot resolve a base and a human run fails with that
	reason. The bot run must still exit 0 — the only way is for the author check to come first. If
	someone moved it after the base resolution, this fails while the coarser exit-code assertions
	above might still pass.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py", bool_with_default_branch=False)

	cls_bot = _run_gate(tmp_path, "dependabot[bot]")
	cls_human = _run_gate(tmp_path, "octocat")

	assert cls_bot.returncode == 0, cls_bot.stdout + cls_bot.stderr
	assert cls_human.returncode == 1
	assert "could not resolve a base" in cls_human.stdout


def test_a_human_pr_with_a_staged_ledger_passes(tmp_path: Path) -> None:
	"""Control case: the gate is satisfiable, not merely strict.

	The ledger is **staged, not committed**, mirroring how pre-commit invokes the gate.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py")
	cls_ledger = tmp_path / ".specs" / "backlog" / "a-topic_20260803_101010.md"
	cls_ledger.parent.mkdir(parents=True, exist_ok=True)
	cls_ledger.write_text(
		"# Ledger — #1 a-topic\n\n"
		"Branch: `fix/1-a-topic` · Issue: #1 · Class: **src**\n\n"
		"## Goal\n\ng\n\n## Work\n\n- [x] done\n",
		encoding="utf-8",
	)
	_git(tmp_path, "add", ".specs/backlog/a-topic_20260803_101010.md")

	cls_proc = _run_gate(tmp_path, "octocat")

	assert cls_proc.returncode == 0, cls_proc.stdout + cls_proc.stderr


def test_a_ledger_under_features_does_not_satisfy_the_gate(tmp_path: Path) -> None:
	"""Only a flat ``.specs/backlog/`` ledger counts; ``features/*/tasks.md`` does not.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py")
	cls_tasks = tmp_path / ".specs" / "features" / "a-topic" / "tasks.md"
	cls_tasks.parent.mkdir(parents=True, exist_ok=True)
	cls_tasks.write_text("- [x] done\n", encoding="utf-8")
	_git(tmp_path, "add", ".specs/features/a-topic/tasks.md")

	cls_proc = _run_gate(tmp_path, "octocat")

	assert cls_proc.returncode == 1, cls_proc.stdout + cls_proc.stderr


def test_the_gate_survives_a_non_utf8_console(tmp_path: Path) -> None:
	"""Regression: the status glyphs must not crash the gate on a cp1252 console.

	Windows defaults stdout to cp1252, which cannot encode them, so `print()` raised
	UnicodeEncodeError and the gate died before reporting anything — and since its pre-commit hook
	is ``always_run``, that broke **every** commit on a Windows checkout. It went unseen because
	the hook is normally run on Linux and the CI step is gated on Linux; the matrix caught it
	only once these tests existed.

	Forcing ``PYTHONIOENCODING`` reproduces it on any platform, so this no longer depends on the
	Windows leg to be caught.

	Parameters
	----------
	tmp_path : pathlib.Path
		pytest's per-test temporary directory.
	"""
	_seed_repo(tmp_path, "src/purecalendars/thing.py")

	cls_proc = _run_gate(tmp_path, "dependabot[bot]", str_io_encoding="cp1252")

	assert cls_proc.returncode == 0, cls_proc.stdout + cls_proc.stderr
	assert "UnicodeEncodeError" not in cls_proc.stderr
	assert "authored by a bot" in cls_proc.stdout
