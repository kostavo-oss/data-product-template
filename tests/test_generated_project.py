"""The generated project, run: its own `check`, and the example pipeline into DuckDB.

Needs uv. leeghwater comes from PyPI, or from the wheel LEEGHWATER_WHEEL names, to try a
leeghwater change before it is released.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def uv() -> str:
    found = shutil.which("uv")
    if not found:
        pytest.skip("uv is not on the PATH")
    return found


@pytest.fixture(scope="session")
def synced(full: Path) -> Path:
    wheel = os.environ.get("LEEGHWATER_WHEEL")
    if wheel:
        with (full / "pyproject.toml").open("a") as pyproject:
            pyproject.write(f'\n[tool.uv.sources]\nleeghwater = {{ path = "{wheel}" }}\n')
    done = subprocess.run([uv(), "sync"], cwd=full, capture_output=True, text=True)
    if done.returncode != 0:
        pytest.skip(f"the project could not be synced here: {done.stderr[-400:]}")
    return full


def _run(project: Path, *words: str, env: dict[str, str] | None = None):
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    cli = os.environ.get("DATABRICKS_CLI")
    if cli:
        environment["PATH"] = str(Path(cli).parent) + os.pathsep + environment["PATH"]
    return subprocess.run(
        [uv(), "run", *words],
        cwd=project,
        capture_output=True,
        text=True,
        env={**environment, **(env or {})},
    )


def test_the_pipelines_import_and_are_listed(synced):
    # Holds DLT-1.
    done = _run(synced, "ingest", "list")

    assert done.returncode == 0, done.stderr
    assert "example" in done.stdout


def test_dbt_parses_the_models(synced):
    # Holds DBT-1, DBT-2.
    done = _run(
        synced,
        "--group",
        "dev",
        "dbt",
        "parse",
        "--project-dir",
        "dbt",
        "--profiles-dir",
        "dbt",
        "--target",
        "parse",
        "--vars",
        "{raw_schema: parse}",
    )

    assert done.returncode == 0, done.stdout + done.stderr


def test_dbt_resolves_the_example_model_as_a_table(synced):
    # Holds DBT-2, DBT-3.
    done = _run(
        synced,
        "--group",
        "dev",
        "dbt",
        "ls",
        "--project-dir",
        "dbt",
        "--profiles-dir",
        "dbt",
        "--target",
        "parse",
        "--vars",
        "{raw_schema: parse}",
        "--resource-type",
        "model",
        "--output",
        "json",
    )

    assert done.returncode == 0, done.stdout + done.stderr
    assert '"materialized": "table"' in done.stdout


def test_the_example_runs_here_into_duckdb(synced, tmp_path):
    # Holds DLT-2.
    done = _run(
        synced,
        "ingest",
        "run",
        "example",
        "--count",
        "3",
        env={"DLT_DATA_DIR": str(tmp_path)},
    )

    assert done.returncode == 0, done.stderr
    assert "done    numbers" in done.stdout
    assert (synced / "example.duckdb").exists()


def test_the_names_script_says_what_is_missing(synced):
    # Holds TSK-4.
    done = _run(
        synced,
        "python",
        "ops/names.py",
        env={"DATABRICKS_HOST": "https://nowhere.invalid", "DATABRICKS_TOKEN": "none"},
    )

    assert done.returncode == 1
    assert ("deploy the target first" in done.stderr) or ("mise install" in done.stderr)


def test_the_scope_step_runs_on_its_own(full: Path):
    """`uv run ops/scope.py --help` resolves lely from PyPI (0.3 or newer) and shows the
    step's commands: the step is a command of its own before any workspace is reached."""
    # Holds SEC-1.
    done = subprocess.run(
        [uv(), "run", "ops/scope.py", "--help"], cwd=full, capture_output=True, text=True
    )

    assert done.returncode == 0, done.stderr[-600:]
    for command in ("plan", "apply", "destroy", "status", "check"):
        assert command in done.stdout
