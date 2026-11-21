"""Unit tests for the work-ledger gate (``bin/check_backlog_ledger.py``).

Two halves, both mirroring the BlueprintX template's gate: the pure logic (path
classification, ledger validation, the bot exemption read from the event payload) and the
base resolution in a CI-shaped checkout, where the gate must refuse to pass blind
(blueprintx#1069).
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest


_BIN = Path(__file__).resolve().parents[2] / "bin"


def _load(str_name: str) -> ModuleType:
    """Load a ``bin/`` script by path (``bin/`` is not a package).

    Parameters
    ----------
    str_name : str
            Module stem under ``bin/``.

    Returns
    -------
    ModuleType
            The imported module.
    """
    cls_spec = importlib.util.spec_from_file_location(str_name, _BIN / f"{str_name}.py")
    cls_module = importlib.util.module_from_spec(cls_spec)
    sys.modules[str_name] = cls_module
    cls_spec.loader.exec_module(cls_module)
    return cls_module


gate = _load("pr_gate")
ledger = _load("check_backlog_ledger")


@pytest.fixture(autouse=True)
def _neutral_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove the CI variables that change the gate's author, and the host's git state.

    A pre-commit hook runs with ``GIT_INDEX_FILE`` (and friends) pointing at the *outer*
    repository; inherited by a git call inside a throwaway repo it writes to the wrong index and
    fails, so every ``GIT_*`` variable is dropped before the fixture repos are built.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
            Used to clear and set the variables.
    """
    for str_key in [str_key for str_key in os.environ if str_key.startswith("GIT_")]:
        monkeypatch.delenv(str_key)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)


def _first_problem(list_problems: list[str]) -> str:
    """Return the first problem reported, asserting the list is not empty.

    "It fired at all" and "it said the right thing" are two claims (blueprintx#544). The
    first is a precondition of the second — indexing ``[0]`` of an empty list raises an
    ``IndexError`` that names neither the gate nor the input — so it is checked here and
    each test keeps the single assertion that names the behaviour.

    Parameters
    ----------
    list_problems : list of str
            Whatever the gate reported.

    Returns
    -------
    str
            The first problem.
    """
    assert list_problems, "the gate reported nothing at all"
    return list_problems[0]


@pytest.mark.parametrize("str_path", ["src/model/loader.py", "bin/venv.sh"])
def test_ledger_required_for_src_and_ci(str_path: str) -> None:
    """A branch touching src/ or ci paths must carry a ledger."""
    assert ledger.needs_ledger([str_path], cls_gate=gate) is True


@pytest.mark.parametrize(
    "str_path",
    ["docs/usage.md", "poetry.lock", "tests/unit/test_x.py", ".specs/features/x/design.md"],
)
def test_ledger_not_required_for_routine_classes(str_path: str) -> None:
    """docs/deps/tests-only branches are routine — a ledger there would be noise."""
    assert ledger.needs_ledger([str_path], cls_gate=gate) is False


_LIST_MIXED_BRANCH = ["bin/venv.sh", "tests/unit/test_x.py"]


def test_the_whole_list_view_collapses_a_mixed_branch_to_tests() -> None:
    """The collapse is real — this is why the whole-list view cannot be the one asked."""
    assert gate.classify_risk(_LIST_MIXED_BRANCH) == "tests"


def test_membership_is_asked_per_path_not_over_the_whole_list() -> None:
    """The regression this guards: a mixed branch must NOT escape the ledger requirement."""
    assert ledger.needs_ledger(_LIST_MIXED_BRANCH, cls_gate=gate) is True


def test_a_valid_ledger_satisfies_the_branch() -> None:
    """A correctly named ledger clears the requirement."""
    list_files = ["src/a.py", ".specs/backlog/my-topic_20260720_101500.md"]
    assert ledger.find_ledger_problems(list_files) == []


def test_missing_ledger_is_reported() -> None:
    """A src-touching branch with no ledger fails, and the message says what to create."""
    assert "Create .specs/backlog/<kebab-topic>_YYYYMMDD_HHMMSS.md" in _first_problem(
        ledger.find_ledger_problems(["src/a.py"])
    )


def test_ledger_name_must_be_kebab_plus_timestamp() -> None:
    """A misnamed ledger is rejected — the timestamped kebab name is the convention."""
    assert ".specs/backlog/<kebab-topic>_YYYYMMDD_HHMMSS.md" in _first_problem(
        ledger.find_ledger_problems(["src/a.py", ".specs/backlog/BadName.md"])
    )


def test_gitkeep_is_not_reported_as_a_misnamed_ledger() -> None:
    """Only ``.md`` paths are ledgers, so the scaffold's ``.gitkeep`` never trips the name rule."""
    list_problems = ledger.find_ledger_problems(["src/a.py", ".specs/backlog/.gitkeep"])
    assert not any("name must match" in str_problem for str_problem in list_problems)


def test_crlf_ledger_with_a_closed_fence_keeps_its_real_checkboxes(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A CRLF checkout must not turn every closed fence into an unclosed one."""
    str_rel = ".specs/backlog/crlf_20260101_000000.md"
    path_ledger = tmp_path / str_rel
    path_ledger.parent.mkdir(parents=True)
    path_ledger.write_bytes(b"# t\r\n\r\n```\r\nexample\r\n```\r\n\r\n- [ ] real\r\n")
    monkeypatch.chdir(tmp_path)
    assert ledger.find_ledger_problems([str_rel]) == []


@pytest.mark.parametrize(
    "str_fenced",
    [
        "```\n- [ ] example\n```\n",
        "```\n- [ ] example\n````\n",
        "~~~\n- [ ] example\n~~~~\n",
        "```\n- [ ] example\n",
    ],
)
def test_checkbox_inside_a_code_fence_does_not_count(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch, str_fenced: str
) -> None:
    """The specs gate skips fenced blocks, closers may be longer; an example-only ledger fails."""
    str_rel = ".specs/backlog/fenced_20260101_000000.md"
    path_ledger = tmp_path / str_rel
    path_ledger.parent.mkdir(parents=True)
    path_ledger.write_text(f"# t\n\n{str_fenced}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert "outside a code fence" in _first_problem(ledger.find_ledger_problems([str_rel]))


@pytest.mark.parametrize(
    "str_line", ["- [ ] todo", "- [x] done", "- [~] feat/a doing", "+ [ ] plus"]
)
def test_checkbox_grammar_accepts_the_specs_markers(str_line: str) -> None:
    """The ledger gate accepts the same markers check_specs_structure.sh does."""
    assert ledger.CHECKBOX_RE.search(str_line)


@pytest.mark.parametrize(
    "str_line",
    ["- [X] upper", "- [] empty", "- [?] unknown", "- plain", "- [~]", "- [~] doing", "- [~]\t"],
)
def test_checkbox_grammar_rejects_what_the_specs_gate_rejects(str_line: str) -> None:
    """NEGATIVE CONTROL: a marker the specs gate rejects does not count as a checkbox."""
    assert not ledger.CHECKBOX_RE.search(str_line)


@pytest.mark.parametrize("str_login", ["dependabot[bot]", "github-actions[bot]", "renovate[bot]"])
def test_bot_login_is_exempt(str_login: str) -> None:
    """GitHub's own ``[bot]`` suffix identifies the author, with no allow-list to rot."""
    assert ledger.is_bot_author(str_login) is True


@pytest.mark.parametrize("str_login", ["octocat", "robotics-team", "dependabot"])
def test_human_login_is_not_exempt(str_login: str) -> None:
    """NEGATIVE CONTROL: the gate still fires for humans, including bot-ish names."""
    assert ledger.is_bot_author(str_login) is False


def test_unresolved_author_is_treated_as_human() -> None:
    """An author that cannot be resolved must fail CLOSED, never exempt."""
    assert ledger.is_bot_author("") is False


def _write_event(path_dir: Path, *, dict_payload: dict) -> str:
    """Write a GitHub event payload to disk and return its path.

    Parameters
    ----------
    path_dir : pathlib.Path
            Directory to write the payload into.
    dict_payload : dict
            The event body, e.g. ``{"pull_request": {"user": {"login": "x"}}}``.

    Returns
    -------
    str
            Path to the written JSON file.
    """
    path_event = path_dir / "event.json"
    path_event.write_text(json.dumps(dict_payload), encoding="utf-8")
    return str(path_event)


def test_pr_author_comes_from_the_payload_never_the_actor(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⚠️ The trap: ``GITHUB_ACTOR`` is whoever TRIGGERED the run, not the PR author.

    Keying on the actor makes the exemption die the moment a human touches the bot's PR
    (update-branch, re-run, fixup) — so the very act of unblocking it defeats the fix, and
    each retry reads as "the fix doesn't work". This pins the author as authoritative even
    when a human is the actor.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest throwaway dir holding the event payload.
    monkeypatch : pytest.MonkeyPatch
            Used to set the GitHub Actions environment variables.
    """
    str_event = _write_event(
        tmp_path, dict_payload={"pull_request": {"user": {"login": "dependabot[bot]"}}}
    )
    monkeypatch.setenv("GITHUB_EVENT_PATH", str_event)
    monkeypatch.setenv("GITHUB_ACTOR", "a-human-who-clicked-rerun")

    assert ledger.pr_author_login() == "dependabot[bot]"


def test_human_authored_pr_is_not_exempt_even_when_a_bot_is_the_actor(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other direction: a bot triggering a human's PR must not exempt it."""
    str_event = _write_event(
        tmp_path, dict_payload={"pull_request": {"user": {"login": "octocat"}}}
    )
    monkeypatch.setenv("GITHUB_EVENT_PATH", str_event)
    monkeypatch.setenv("GITHUB_ACTOR", "github-actions[bot]")

    assert ledger.is_bot_author(ledger.pr_author_login()) is False


def test_a_push_run_has_no_pr_author_and_stays_enforced(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Inside a workflow run the payload is the ONLY authority — never the actor.

    A push payload carries no ``pull_request`` object, so there is no author, and the gate must
    stay enforced rather than fall back to a possibly-bot actor.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest throwaway dir holding the event payload.
    monkeypatch : pytest.MonkeyPatch
            Used to set the GitHub Actions environment variables.
    """
    str_event = _write_event(tmp_path, dict_payload={"ref": "refs/heads/main"})
    monkeypatch.setenv("GITHUB_EVENT_PATH", str_event)
    monkeypatch.setenv("GITHUB_ACTOR", "dependabot[bot]")

    assert ledger.is_bot_author(ledger.pr_author_login()) is False


def test_a_missing_event_file_exempts_nobody(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GITHUB_EVENT_PATH set but the file absent must fail CLOSED, not fall back to the actor.

    This is the narrow hole an earlier revision left: the missing-file branch skipped the
    payload entirely and returned ``GITHUB_ACTOR``, so a bot re-running or auto-merging a
    human's PR would have exempted it — the exact defect keying on the author exists to avoid.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest throwaway dir; the payload path deliberately points at nothing.
    monkeypatch : pytest.MonkeyPatch
            Used to set the GitHub Actions environment variables.
    """
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(tmp_path / "does_not_exist.json"))
    monkeypatch.setenv("GITHUB_ACTOR", "dependabot[bot]")

    assert ledger.is_bot_author(ledger.pr_author_login()) is False


def test_a_missing_event_file_resolves_to_no_author_at_all(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The MECHANISM behind the test above: the resolver returns "", never the actor.

    Split from its sibling rather than dropped (blueprintx#544). The two are genuinely
    different claims — "nobody is exempted" is the behaviour, and "the resolver returns the
    empty string" is why. Keeping only the first would let a resolver that returned some
    other non-bot login pass while the real defect (falling back to ``GITHUB_ACTOR``) went
    unnamed.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest throwaway dir; the payload path deliberately points at nothing.
    monkeypatch : pytest.MonkeyPatch
            Used to set the GitHub Actions environment variables.
    """
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(tmp_path / "does_not_exist.json"))
    monkeypatch.setenv("GITHUB_ACTOR", "dependabot[bot]")

    assert ledger.pr_author_login() == ""


def test_unreadable_payload_exempts_nobody(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A corrupt payload must fail closed rather than exempt the whole run."""
    path_event = tmp_path / "event.json"
    path_event.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path_event))
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)

    assert ledger.is_bot_author(ledger.pr_author_login()) is False


def test_local_run_has_no_author_and_stays_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    """Off CI (a local pre-commit) nothing is exempt — the gate behaves exactly as before."""
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)

    assert ledger.is_bot_author(ledger.pr_author_login()) is False


def _git_in(path_repo: Path, *args: str) -> str:
    """Run ``git`` inside a throwaway repo and return its stripped stdout.

    Parameters
    ----------
    path_repo : pathlib.Path
            The repository to run in.
    *args : str
            Arguments after ``git``.

    Returns
    -------
    str
            Captured stdout, stripped.
    """
    cls_proc = subprocess.run(  # noqa: S603
        ["git", "-C", str(path_repo), *args],  # noqa: S607
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return cls_proc.stdout.strip()


def _init_identity(path_repo: Path) -> None:
    """Give a throwaway repo a committer identity and switch signing off.

    Parameters
    ----------
    path_repo : pathlib.Path
            The repository to configure.
    """
    _git_in(path_repo, "config", "user.email", "t@example.com")
    _git_in(path_repo, "config", "user.name", "t")
    _git_in(path_repo, "config", "commit.gpgsign", "false")


def _commit_file(path_repo: Path, *, str_name: str) -> None:
    """Write one file and commit it.

    Parameters
    ----------
    path_repo : pathlib.Path
            The repository to commit in.
    str_name : str
            Repository-relative path of the file to create.
    """
    path_file = path_repo / str_name
    path_file.parent.mkdir(parents=True, exist_ok=True)
    path_file.write_text(str_name, encoding="utf-8")
    _git_in(path_repo, "add", str_name)
    _git_in(path_repo, "commit", "-q", "-m", f"add {str_name}")


@pytest.fixture
def path_origin(tmp_path: Path) -> Path:
    """Return a bare remote holding ``main``, ``develop`` and a ``feature`` that edits ``src/``.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest-provided scratch directory.

    Returns
    -------
    pathlib.Path
            The bare remote.
    """
    path_seed = tmp_path / "seed"
    path_seed.mkdir()
    _git_in(path_seed, "init", "-q", "--initial-branch=main")
    _init_identity(path_seed)
    _commit_file(path_seed, str_name="README.md")
    _git_in(path_seed, "branch", "develop")
    _git_in(path_seed, "checkout", "-q", "-b", "feature")
    _commit_file(path_seed, str_name="src/mod.py")
    path_remote = tmp_path / "origin.git"
    _git_in(tmp_path, "init", "-q", "--bare", str(path_remote))
    _git_in(path_seed, "push", "-q", str(path_remote), "main", "develop", "feature")
    return path_remote


@pytest.fixture
def path_ci(tmp_path: Path, *, path_origin: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Return a checkout shaped like ``actions/checkout``: detached, no local branch, no HEAD ref.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest-provided scratch directory.
    path_origin : pathlib.Path
            The bare remote to fetch from.
    monkeypatch : pytest.MonkeyPatch
            Used to run the gate inside the checkout.

    Returns
    -------
    pathlib.Path
            The checkout, ``HEAD`` detached at ``origin/feature``.
    """
    path_checkout = tmp_path / "ci"
    path_checkout.mkdir()
    _git_in(path_checkout, "init", "-q")
    _init_identity(path_checkout)
    _git_in(path_checkout, "remote", "add", "origin", str(path_origin))
    _git_in(path_checkout, "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*")
    _git_in(path_checkout, "checkout", "-q", "--detach", "origin/feature")
    monkeypatch.chdir(path_checkout)
    return path_checkout


@pytest.fixture
def path_ci_merge(path_ci: Path) -> Path:
    """Return the real ``pull_request`` checkout: ``HEAD`` on the merge of the PR into its base.

    Parameters
    ----------
    path_ci : pathlib.Path
            The detached checkout at ``origin/feature``.

    Returns
    -------
    pathlib.Path
            The checkout, ``HEAD`` detached at a merge commit whose parents are ``origin/main``
            and ``origin/feature`` (what ``refs/pull/N/merge`` is).
    """
    _git_in(path_ci, "checkout", "-q", "--detach", "origin/main")
    _git_in(path_ci, "merge", "-q", "--no-ff", "-m", "merge", "origin/feature")
    return path_ci


@pytest.fixture
def path_no_default(tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Return a repo with commits on ``feature`` and no branch the gate can call the default.

    Parameters
    ----------
    tmp_path : pathlib.Path
            Pytest-provided scratch directory.
    monkeypatch : pytest.MonkeyPatch
            Used to run the gate inside the repo.

    Returns
    -------
    pathlib.Path
            The repository.
    """
    path_repo = tmp_path / "nodefault"
    path_repo.mkdir()
    _git_in(path_repo, "init", "-q", "--initial-branch=feature")
    _init_identity(path_repo)
    _commit_file(path_repo, str_name="README.md")
    _commit_file(path_repo, str_name="src/mod.py")
    monkeypatch.chdir(path_repo)
    return path_repo


def test_main_ci_checkout_without_local_main_demands_a_ledger(path_ci: Path) -> None:
    """The CI shape is where the gate matters, so src/ changes there must still be refused."""
    assert ledger.main() == 1


def test_main_ci_checkout_names_the_missing_ledger(
    path_ci: Path, *, capsys: pytest.CaptureFixture[str]
) -> None:
    """The refusal in a CI checkout is the ledger message, not silence."""
    ledger.main()
    assert "adds no work ledger" in capsys.readouterr().out


def test_default_branch_ci_checkout_resolves_the_remote_tracking_ref(path_ci: Path) -> None:
    """With no local ``main`` and no ``origin/HEAD``, the usable ref is ``origin/main``."""
    assert ledger.default_branch() == "origin/main"


def test_default_branch_prefers_the_pull_request_base_ref(
    path_ci: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A PR targeting ``develop`` is diffed against ``origin/develop``, not ``origin/main``."""
    monkeypatch.setenv("GITHUB_BASE_REF", "develop")
    assert ledger.default_branch() == "origin/develop"


def test_default_branch_refuses_to_fall_back_from_an_unresolvable_base_ref(
    path_ci: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A known PR base that was not fetched must not be swapped for another branch."""
    monkeypatch.setenv("GITHUB_BASE_REF", "does-not-exist")
    assert ledger.default_branch() == ""


def test_main_unresolvable_pull_request_base_fails(
    path_ci: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A narrow fetch that lacks the PR base is reported, never judged against ``origin/main``.

    HEAD sits at ``origin/main`` so a silent fallback would read "HEAD is the base" and pass.
    """
    _git_in(path_ci, "checkout", "-q", "--detach", "origin/main")
    monkeypatch.setenv("GITHUB_BASE_REF", "does-not-exist")
    assert ledger.main() == 1


def test_main_unresolvable_base_on_a_feature_branch_fails(path_no_default: Path) -> None:
    """No resolvable base on a branch with commits is a failure, never a silent pass."""
    assert ledger.main() == 1


def test_main_unresolvable_base_says_it_could_not_resolve(
    path_no_default: Path, *, capsys: pytest.CaptureFixture[str]
) -> None:
    """The failure names the cause so the reader is not left guessing."""
    ledger.main()
    assert "could not resolve a base" in capsys.readouterr().out


def test_main_pull_request_merge_commit_demands_a_ledger(path_ci_merge: Path) -> None:
    """The ``refs/pull/N/merge`` shape is the one the workflow really checks out."""
    assert ledger.main() == 1


def test_main_unresolvable_base_names_a_local_remedy(
    path_no_default: Path, *, capsys: pytest.CaptureFixture[str]
) -> None:
    """A developer with no CI to reconfigure is told to fetch or create the default branch."""
    ledger.main()
    assert "git fetch origin" in capsys.readouterr().out


def test_fixture_repos_ignore_the_host_global_git_config(path_ci: Path) -> None:
    """A developer's global ``core.hooksPath`` or templates must not reach the fixture repos."""
    assert _git_in(path_ci, "config", "--global", "--list") == ""


def test_main_on_the_default_branch_is_still_a_no_op(path_ci: Path) -> None:
    """The control: HEAD at ``origin/main`` has nothing to diff and passes."""
    _git_in(path_ci, "checkout", "-q", "--detach", "origin/main")
    assert ledger.main() == 0


def test_main_repository_without_commits_is_a_no_op(
    tmp_path: Path, *, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The first commit of a new repo has no HEAD to compare, and must not be refused."""
    path_empty = tmp_path / "empty"
    path_empty.mkdir()
    _git_in(path_empty, "init", "-q")
    monkeypatch.chdir(path_empty)
    assert ledger.main() == 0
