"""Unit tests for ``bin/lib/pip_requirements.py`` (Poetry constraints to pip lines)."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


_PATH_MODULE = Path(__file__).resolve().parents[2] / "bin" / "lib" / "pip_requirements.py"


def _load() -> ModuleType:
    """Load ``bin/lib/pip_requirements.py`` by path (``bin/lib`` is not a package).

    Returns
    -------
    ModuleType
            The imported module.
    """
    cls_spec = importlib.util.spec_from_file_location("pip_requirements", _PATH_MODULE)
    cls_module = importlib.util.module_from_spec(cls_spec)
    sys.modules["pip_requirements"] = cls_module
    cls_spec.loader.exec_module(cls_module)
    return cls_module


pipreq = _load()


@pytest.mark.parametrize(
    ("str_raw", "list_expected"),
    [
        ("1.4", [1, 4]),
        ("2.0.0rc1", [2, 0, 0]),
        (" 3.1.7 ", [3, 1, 7]),
        ("1.x.2", [1, 0, 2]),
    ],
)
def test_version_parts(str_raw: str, list_expected: list[int]) -> None:
    """Leading digits of each dot-separated part are kept, junk parts become zero."""
    assert pipreq.version_parts(str_raw) == list_expected


@pytest.mark.parametrize(
    ("str_raw", "str_expected"),
    [
        ("^1.2.3", ">=1.2.3,<2.0.0"),
        ("^0.2.3", ">=0.2.3,<0.3.0"),
        ("^0.0.3", ">=0.0.3,<0.0.4"),
        ("^1", ">=1,<2.0.0"),
        ("^0.2", ">=0.2,<0.3.0"),
        ("^0", ">=0,<1.0.0"),
        ("^0.0", ">=0.0,<0.1.0"),
        ("^0.0.0", ">=0.0.0,<0.0.1"),
        ("^1.2.0rc1", ">=1.2.0rc1,<2.0.0"),
    ],
)
def test_caret_to_range(str_raw: str, str_expected: str) -> None:
    """The upper bound sits on the left-most non-zero component."""
    assert pipreq.caret_to_range(str_raw) == str_expected


@pytest.mark.parametrize(
    ("str_raw", "str_expected"),
    [
        ("~1.2", ">=1.2,<1.3.0"),
        ("~1.2.3", ">=1.2.3,<1.3.0"),
        ("~1", ">=1,<2.0.0"),
        ("~0.4", ">=0.4,<0.5.0"),
    ],
)
def test_tilde_to_range(str_raw: str, str_expected: str) -> None:
    """The bound depends on how many components were written, not on their values."""
    assert pipreq.tilde_to_range(str_raw) == str_expected


@pytest.mark.parametrize(
    ("str_spec", "str_expected"),
    [
        ("*", ""),
        ("", ""),
        ("  ", ""),
        ("^1.2", ">=1.2,<2.0.0"),
        ("~1.2", ">=1.2,<1.3.0"),
        ("~=1.2", "~=1.2"),
        (">=1,<2", ">=1,<2"),
        (">=1", ">=1"),
        ("!=1.5", "!=1.5"),
        ("1.2.3", "==1.2.3"),
        ("1.2,<2", "==1.2,<2"),
    ],
)
def test_normalize_version_spec(str_spec: str, str_expected: str) -> None:
    """Each Poetry constraint form maps to its pip equivalent; ``~=`` is not a tilde."""
    assert pipreq.normalize_version_spec(str_spec) == str_expected


def test_build_requirement_skips_python_pseudo_dependency() -> None:
    """The ``python`` entry is a runtime constraint, never a pip requirement."""
    assert pipreq.build_requirement("Python", union_spec="^3.11") is None


def test_build_requirement_string_spec() -> None:
    """A bare string spec is name plus the normalised constraint."""
    assert pipreq.build_requirement("holidays", union_spec="^0.50") == "holidays>=0.50,<0.51.0"


def test_build_requirement_wildcard_has_no_constraint() -> None:
    """A ``*`` spec yields the bare name."""
    assert pipreq.build_requirement("pandas", union_spec="*") == "pandas"


def test_build_requirement_optional_table_is_skipped() -> None:
    """A table marked ``optional`` is dropped."""
    assert (
        pipreq.build_requirement("numpy", union_spec={"version": "^1", "optional": True}) is None
    )


def test_build_requirement_extras_version_and_markers() -> None:
    """Extras, version and markers compose in pip's order."""
    dict_spec = {"version": "^2.0", "extras": ["a", "b"], "markers": "sys_platform == 'linux'"}
    str_line = pipreq.build_requirement("lib", union_spec=dict_spec)
    assert str_line == "lib[a,b]>=2.0,<3.0.0 ; sys_platform == 'linux'"


def test_build_requirement_table_without_version() -> None:
    """A table with no version is the bare name."""
    assert pipreq.build_requirement("lib", union_spec={"extras": []}) == "lib"


@pytest.mark.parametrize("str_key", ["path", "git", "url"])
def test_build_requirement_rejects_unsupported_sources(str_key: str) -> None:
    """Path, git and url dependencies exit with a message naming the dependency."""
    with pytest.raises(SystemExit, match=f"lib -> {str_key}"):
        pipreq.build_requirement("lib", union_spec={str_key: "x"})


def test_build_requirement_rejects_unknown_shape() -> None:
    """A declaration that is neither string nor table exits non-zero."""
    with pytest.raises(SystemExit, match="Unsupported dependency format for lib"):
        pipreq.build_requirement("lib", union_spec=["^1"])


def test_pep621_main_group_reads_dependencies() -> None:
    """``main`` maps to ``dependencies`` and passes lines through untouched."""
    dict_project = {"dependencies": ["a>=1", "b"], "optional-dependencies": {"dev": ["c"]}}
    assert pipreq.pep621_requirements(dict_project, list_groups=["main"]) == ["a>=1", "b"]


def test_pep621_named_group_reads_optional_dependencies() -> None:
    """A non-main group maps to ``optional-dependencies``; main is excluded unless asked."""
    dict_project = {"dependencies": ["a"], "optional-dependencies": {"dev": ["c"]}}
    assert pipreq.pep621_requirements(dict_project, list_groups=["dev"]) == ["c"]


def test_pep621_combines_main_and_named_group_in_order() -> None:
    """Requested groups are concatenated, main first."""
    dict_project = {"dependencies": ["a"], "optional-dependencies": {"dev": ["c"]}}
    assert pipreq.pep621_requirements(dict_project, list_groups=["main", "dev"]) == ["a", "c"]


def test_pep621_missing_group_is_empty() -> None:
    """An unknown group contributes nothing instead of raising."""
    assert pipreq.pep621_requirements({"dependencies": ["a"]}, list_groups=["nope"]) == []


def test_poetry_main_group_normalises_and_skips_python() -> None:
    """Top-level dependencies are normalised and the ``python`` pin is dropped."""
    dict_poetry = {"dependencies": {"python": "^3.11", "pandas": "^2.1", "tzdata": "*"}}
    list_lines = pipreq.poetry_requirements(dict_poetry, list_groups=["main"])
    assert list_lines == ["pandas>=2.1,<3.0.0", "tzdata"]


def test_poetry_named_group_reads_group_table() -> None:
    """A named group reads ``[tool.poetry.group.<g>.dependencies]``."""
    dict_poetry = {
        "dependencies": {"pandas": "^2"},
        "group": {"dev": {"dependencies": {"pytest": "~8.1"}}},
    }
    assert pipreq.poetry_requirements(dict_poetry, list_groups=["dev"]) == ["pytest>=8.1,<8.2.0"]


def test_poetry_skips_optional_dependencies() -> None:
    """Optional tables never reach the output."""
    dict_poetry = {"dependencies": {"a": {"version": "^1", "optional": True}, "b": "1.0"}}
    assert pipreq.poetry_requirements(dict_poetry, list_groups=["main"]) == ["b==1.0"]


def test_poetry_missing_group_is_empty() -> None:
    """A group absent from the manifest yields nothing."""
    assert pipreq.poetry_requirements({"dependencies": {"a": "1"}}, list_groups=["dev"]) == []


def test_select_prefers_pep621_when_dependencies_declared() -> None:
    """Populated ``[project]`` wins over a Poetry table."""
    dict_pyproject = {
        "project": {"dependencies": ["a>=1"]},
        "tool": {"poetry": {"dependencies": {"b": "1"}}},
    }
    assert pipreq.select_requirements(dict_pyproject, list_groups=["main"]) == ["a>=1"]


def test_select_pep621_with_only_optional_dependencies() -> None:
    """A project carrying only optional-dependencies still takes the PEP 621 path."""
    dict_pyproject = {
        "project": {"optional-dependencies": {"dev": ["pytest"]}},
        "tool": {"poetry": {}},
    }
    assert pipreq.select_requirements(dict_pyproject, list_groups=["dev"]) == ["pytest"]


def test_select_falls_back_to_poetry_when_project_is_empty() -> None:
    """An empty ``[project]`` next to a populated Poetry table resolves through Poetry."""
    dict_pyproject = {
        "project": {"name": "x"},
        "tool": {"poetry": {"dependencies": {"b": "1"}}},
    }
    assert pipreq.select_requirements(dict_pyproject, list_groups=["main"]) == ["b==1"]


def test_select_with_no_layout_is_empty() -> None:
    """A manifest with neither layout yields nothing."""
    assert pipreq.select_requirements({}, list_groups=["main"]) == []


def _write_manifest(path_dir: Path, str_toml: str) -> None:
    """Write a ``pyproject.toml`` into ``path_dir``.

    Parameters
    ----------
    path_dir : Path
            Target directory.
    str_toml : str
            File content.
    """
    path_dir.joinpath("pyproject.toml").write_text(str_toml, encoding="utf-8")


def test_main_prints_deduplicated_lines_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Duplicate lines print once, first occurrence kept."""
    _write_manifest(tmp_path, '[project]\nname="x"\ndependencies=["a","b","a"]\n')
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("BX_GROUPS", raising=False)
    pipreq.main()
    assert capsys.readouterr().out == "a\nb\n"


def test_main_returns_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A resolved manifest exits 0."""
    _write_manifest(tmp_path, '[project]\nname="x"\ndependencies=["a"]\n')
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("BX_GROUPS", raising=False)
    assert pipreq.main() == 0


def test_main_reads_groups_from_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``BX_GROUPS`` is comma-separated and ignores empty entries."""
    _write_manifest(
        tmp_path,
        '[project]\nname="x"\ndependencies=["a"]\n[project.optional-dependencies]\ndev=["c"]\n',
    )
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("BX_GROUPS", "main,,dev")
    pipreq.main()
    assert capsys.readouterr().out == "a\nc\n"


def test_main_exits_naming_groups_when_nothing_resolves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A requested group with no requirements is an error, not an empty success."""
    _write_manifest(tmp_path, '[project]\nname="x"\ndependencies=["a"]\n')
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("BX_GROUPS", "docs")
    with pytest.raises(SystemExit, match="No requirements resolved for group"):
        pipreq.main()


def test_main_requires_project_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without ``PROJECT_ROOT`` the interface contract is broken and it raises."""
    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    with pytest.raises(KeyError):
        pipreq.main()
