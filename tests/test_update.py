"""`copier update` in a product: the wiring moves, and what the product owns stays.

copier updates from one version of a template to the next, so the template is made a
git repository here, with a tag for each version, and the product is one too. No
network, no workspace.
"""

import shutil
import subprocess
from pathlib import Path

from conftest import FULL, files
from copier import run_copy, run_update

GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid"]
# What copier.yml names under `_skip_if_exists`, as the files of this product.
OWNED = (
    "README.md",
    ".dlt/config.toml",
    "src/",
    "dbt/models/",
    "dataproduct.yaml",
    "contracts/",
    "stevin/",
    "sql/",
)
WIRING = {
    "databricks.yml",
    "resources/schemas.yml",
    "resources/shop-data.job.yml",
    "mise.toml",
    "pyproject.toml",
    "lely.yml",
    "AGENTS.md",
    "ops/names.py",
    "ops/ports.py",
    "ops/scope.py",
    "dbt/dbt_project.yml",
    "dbt/profiles.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/plan.yml",
    ".github/workflows/apply.yml",
}
THEIRS = "# the template's next line"
MINE = "# the product's own line"


def git(folder: Path, *words: str) -> None:
    subprocess.run([*GIT, *words], cwd=folder, check=True, capture_output=True)


def commit(folder: Path, message: str, tag: str | None = None) -> None:
    git(folder, "add", ".")
    git(folder, "commit", "-q", "-m", message)
    if tag:
        git(folder, "tag", tag)


def test_an_update_moves_the_wiring_and_keeps_what_the_product_owns(template, tmp_path):
    # Holds GEN-6.
    source = Path(shutil.copytree(template, tmp_path / "template"))
    git(source, "init", "-q", "-b", "main")
    commit(source, "the first version", tag="v0.1.0")

    product = tmp_path / "shop-data"
    answers = {**FULL, "include_stevin": True}
    run_copy(str(source), str(product), data=answers, defaults=True, quiet=True)
    git(product, "init", "-q", "-b", "main")
    commit(product, "made from the template")
    owned = sorted(path for path in files(product) if path.startswith(OWNED))
    assert files(product) >= WIRING
    for path in owned:
        with (product / path).open("a") as file:
            file.write(f"\n{MINE}\n")
    commit(product, "the product's own work")
    mine = {path: (product / path).read_text() for path in owned}

    # The template's next version: a line more in every file it has.
    for file in (source / "template").rglob("*"):
        if file.is_file() and file.name not in (".gitkeep", ".mcp.json"):
            file.write_text(f"{file.read_text()}\n{THEIRS}\n")
    commit(source, "the next version", tag="v0.2.0")

    run_update(str(product), defaults=True, overwrite=True, quiet=True)

    assert "_commit: v0.2.0" in (product / ".copier-answers.yml").read_text()
    for path in owned:
        assert (product / path).read_text() == mine[path], f"{path} was touched"
    for path in sorted(WIRING):
        text = (product / path).read_text()
        assert THEIRS in text, f"{path} did not move"
        assert "<<<<<<<" not in text, f"{path} is left in conflict"
