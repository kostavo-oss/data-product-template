"""The template is tried, not read: every test generates a project with the CLI.

`bundle init` wants credentials configured even when no template helper asks the
workspace for anything; dummy ones do. A real workspace is never reached here.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

FULL = {
    "project_name": "shop-data",
    "catalog": "main",
    "warehouse_id": "abc123",
    "secret_scope": "shop_data",
    "include_dbt": "yes",
    "include_lely": "yes",
    "include_caland": "yes",
}
BARE = {
    "project_name": "bare",
    "catalog": "main",
    "warehouse_id": "",
    "secret_scope": "",
    "include_dbt": "no",
    "include_lely": "no",
    "include_caland": "no",
}


def databricks() -> str:
    found = os.environ.get("DATABRICKS_CLI") or shutil.which("databricks")
    if not found:
        pytest.skip("the Databricks CLI is not on the PATH (mise installs it)")
    return found


def generate(answers: dict[str, str], into: Path) -> Path:
    """Run `databricks bundle init` on this template and return the project's folder."""
    config = into / "answers.json"
    config.write_text(json.dumps(answers))
    done = subprocess.run(
        [
            databricks(),
            "bundle",
            "init",
            str(REPO),
            "--config-file",
            str(config),
            "--output-dir",
            str(into),
        ],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "DATABRICKS_HOST": "https://nowhere.invalid",
            "DATABRICKS_TOKEN": "dapi-none",
            "DATABRICKS_CONFIG_FILE": str(into / "no-such-config"),
        },
    )
    assert done.returncode == 0, done.stdout + done.stderr
    return into / answers["project_name"]


@pytest.fixture(scope="session")
def full(tmp_path_factory) -> Path:
    return generate(FULL, tmp_path_factory.mktemp("full"))


@pytest.fixture(scope="session")
def bare(tmp_path_factory) -> Path:
    return generate(BARE, tmp_path_factory.mktemp("bare"))


LEFT_BY_RUNS = (
    ".venv/",
    "dbt/target/",
    "dbt/logs/",
    "dbt/dbt_packages/",
    "example.duckdb",
)


def files(folder: Path) -> set[str]:
    """What the template wrote: not what a sync or a run left behind."""
    return {
        path
        for p in folder.rglob("*")
        if p.is_file()
        and not (path := p.relative_to(folder).as_posix()).startswith(LEFT_BY_RUNS)
    }
