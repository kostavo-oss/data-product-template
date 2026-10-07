"""The template is tried, not read: every test generates a product with copier.

The template is copied without its `.git` first, so what is tested is the working tree,
committed or not. No workspace is reached anywhere here.
"""

import shutil
from pathlib import Path

import pytest
from copier import run_copy

REPO = Path(__file__).resolve().parent.parent

FULL = {
    "project_name": "shop-data",
    "catalog": "main",
    "warehouse_id": "abc123",
    "secret_scope": "shop_data",
    "include_dbt": True,
    "include_lely": True,
    "include_caland": True,
}
BARE = {
    "project_name": "bare",
    "catalog": "main",
    "warehouse_id": "",
    "secret_scope": "",
    "include_dbt": False,
    "include_lely": False,
    "include_caland": False,
}


@pytest.fixture(scope="session")
def template(tmp_path_factory) -> Path:
    """This working tree, as copier sees a template that is not a git repository."""
    copy = tmp_path_factory.mktemp("template") / "vierlingh"
    shutil.copytree(
        REPO,
        copy,
        ignore=shutil.ignore_patterns(".git", ".venv", ".pytest_cache", "tests"),
    )
    return copy


def generate(template: Path, answers: dict, into: Path) -> Path:
    """Run copier on the template and return the product's folder."""
    product = into / answers["project_name"]
    run_copy(str(template), str(product), data=answers, defaults=True, quiet=True)
    return product


@pytest.fixture(scope="session")
def full(template, tmp_path_factory) -> Path:
    return generate(template, FULL, tmp_path_factory.mktemp("full"))


@pytest.fixture(scope="session")
def bare(template, tmp_path_factory) -> Path:
    return generate(template, BARE, tmp_path_factory.mktemp("bare"))


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
