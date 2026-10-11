"""Every optional part stays optional: a part that was not chosen leaves nothing.

A product is generated for every combination of the yes/no questions, each with a secret
scope and without one, in-process and with no network. Each is then searched, file by
file and line by line, for the names of the parts it left out. A mention that is right is
in `ALLOWED`, with its reason, and nowhere else.
"""

import itertools
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml
from conftest import files, generate

# The parts, in the order `copier.yml` asks for them. The access examples are a part of
# stevin: they are asked only with it.
PARTS = ("dbt", "stevin", "access_examples", "lely", "caland", "contracts")

# What names a part: in a path or on a line, whatever the case.
NAMES = {
    "dbt": r"dbt",
    "stevin": r"stevin|tables:(?:validate|plan|apply|drift)|ops/tables\.py",
    "access_examples": r"security|by_region|region_members|access (?:model|example)",
    "lely": r"lely",
    "caland": r"caland",
    "contracts": r"contract|odcs|dataproduct|ports\.py|\bsite\b",
}

# A mention of a part that was left out, and is right: the part, the file, what the line
# looks like, and why.
ALLOWED = (
    (
        "lely",
        "ops/scope.py",
        r'^# dependencies = \["lely>=[0-9.]+"\]$|^from lely\.\w+ import ',
        "the scope script is written with lely's step library, which uv brings for that"
        " one script: the product has no lely.yml, no lely task and no lely to install",
    ),
)

# The tasks and the tools each part brings to `mise.toml`, beside the ones every product
# has. `scope` comes with a secret scope, which is not a yes/no question.
ALWAYS = {"dev", "check", "fix", "clean", "deploy", "job", "doctor", "ingest"}
CONTRACTS = {"lint", "pull", "check", "dlt", "catalog", "edit"}
TOOLS = {"lely": "pipx:lely", "stevin": "pipx:stevin", "caland": "pipx:caland"}


def chosen(*parts: str, scope: bool = True) -> dict:
    """The answers for a product with these parts and no other."""
    assert "access_examples" not in parts or "stevin" in parts
    answers = {
        "project_name": "shop-data",
        "catalog": "main",
        "warehouse_id": "",
        "secret_scope": "shop_data" if scope else "",
    }
    return answers | {f"include_{part}": part in parts for part in PARTS}


def parts_of(answers: dict) -> set[str]:
    return {part for part in PARTS if answers[f"include_{part}"]}


def every_combination() -> list[dict]:
    """All 48 combinations of the parts, each with a secret scope and without: 96."""
    found = []
    for size in range(len(PARTS) + 1):
        for parts in itertools.combinations(PARTS, size):
            if "access_examples" in parts and "stevin" not in parts:
                continue
            found += [chosen(*parts, scope=True), chosen(*parts, scope=False)]
    return found


def label(answers: dict) -> str:
    parts = "+".join(part for part in PARTS if answers[f"include_{part}"]) or "nothing"
    return parts + ("" if answers["secret_scope"] else ", no scope")


COMBINATIONS = every_combination()


@pytest.fixture(scope="session")
def products(template, tmp_path_factory) -> dict[str, tuple[dict, Path]]:
    """Every combination, generated once."""
    into = tmp_path_factory.mktemp("parts")
    found = {}
    for number, answers in enumerate(COMBINATIONS):
        folder = into / str(number)
        folder.mkdir()
        found[label(answers)] = (answers, generate(template, answers, folder))
    return found


def mentions(product: Path, part: str) -> list[str]:
    """Where a product names a part: `path` for a file, `path:line: text` for a line.
    `.copier-answers.yml` records every answer, and is not looked at."""
    name = re.compile(NAMES[part], re.IGNORECASE)
    allowed = [(path, re.compile(line)) for of, path, line, _ in ALLOWED if of == part]
    found = []
    for path in sorted(files(product) - {".copier-answers.yml"}):
        if name.search(path):
            found.append(path)
        text = (product / path).read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            if not name.search(line):
                continue
            if any(path == where and right.search(line) for where, right in allowed):
                continue
            found.append(f"{path}:{number}: {line.strip()}")
    return found


def test_the_combinations_are_all_of_them():
    """All-yes, all-no, each part alone and each part left out are among them."""
    labels = {label(answers) for answers in COMBINATIONS}

    assert len(labels) == len(COMBINATIONS) == 96
    assert {"nothing", "nothing, no scope", "+".join(PARTS)} <= labels
    for part in ("dbt", "stevin", "lely", "caland", "contracts"):
        assert part in labels
        assert any(parts_of(a) == set(PARTS) - {part} for a in COMBINATIONS) or (
            part == "stevin"
        )
    assert "stevin+access_examples" in labels
    assert "+".join(p for p in PARTS if p not in ("stevin", "access_examples")) in labels
    assert "+".join(p for p in PARTS if p != "access_examples") in labels


@pytest.mark.parametrize("answers", COMBINATIONS, ids=label)
def test_a_part_that_was_not_chosen_leaves_nothing(products, answers):
    """No file of it, and no line that names it, in any file of the product."""
    # Holds GEN-5.
    _, product = products[label(answers)]

    for part in PARTS:
        if part in parts_of(answers):
            continue
        assert mentions(product, part) == [], f"{part} was not chosen"
    if not answers["secret_scope"]:
        assert "ops/scope.py" not in files(product)
    if "lely" not in parts_of(answers):
        assert not (product / "lely.yml").exists()


@pytest.mark.parametrize("answers", COMBINATIONS, ids=label)
def test_the_tasks_and_the_tools_are_those_of_the_parts_chosen(products, answers):
    """`mise.toml` has a task or a tool for a part that was chosen, and for no other."""
    # Holds GEN-5.
    _, product = products[label(answers)]
    parts = parts_of(answers)
    mise = tomllib.loads((product / "mise.toml").read_text())

    tasks = set(ALWAYS)
    if answers["secret_scope"]:
        tasks |= {"scope"}
    if "dbt" in parts:
        tasks |= {"transform"}
    if "lely" in parts:
        tasks |= {"plan", "apply", "destroy"}
    if "caland" in parts:
        tasks |= {"secrets"}
    if "stevin" in parts:
        tasks |= {f"tables:{verb}" for verb in ("validate", "plan", "apply", "drift")}
    if "contracts" in parts:
        tasks |= {f"contracts:{verb}" for verb in CONTRACTS}
        if "dbt" in parts:
            tasks |= {"contracts:dbt"}
        elif "stevin" not in parts:
            tasks |= {"contracts:test"}
    assert set(mise["tasks"]) == tasks

    tools = {"python", "uv", "databricks-cli"}
    tools |= {tool for part, tool in TOOLS.items() if part in parts}
    assert set(mise["tools"]) == tools

    workflows = {path for path in files(product) if path.startswith(".github/")}
    lely = {".github/workflows/plan.yml", ".github/workflows/apply.yml"}
    assert workflows == {".github/workflows/ci.yml"} | (
        lely if "lely" in parts else set()
    )
    for path in sorted(workflows):
        yaml.safe_load((product / path).read_text())


def test_the_search_finds_a_part_that_is_named(products, tmp_path):
    """The search bites: a line, a file and a line beside an allowed one are found."""
    _, bare = products["nothing"]
    product = Path(shutil.copytree(bare, tmp_path / "product"))
    assert mentions(product, "lely") == []

    (product / "README.md").write_text("Deployed with Lely.\n")
    (product / "dbt").mkdir()
    (product / "dbt" / "x.sql").write_text("select 1\n")
    with (product / "ops/scope.py").open("a") as script:
        script.write("# see lely.yml\n")

    assert mentions(product, "dbt") == ["dbt/x.sql"]
    assert mentions(product, "caland") == []
    assert [found.split(": ", 1)[1] for found in mentions(product, "lely")] == [
        "Deployed with Lely.",
        "# see lely.yml",
    ]


# ── the gate, run: with everything and with nothing ──────────────────────────


@pytest.mark.parametrize("which", ["+".join(PARTS), "nothing, no scope"])
def test_the_gate_passes_with_everything_and_with_nothing(products, which, tmp_path):
    """Every command of the product's `check` task exits 0, with no workspace. stevin is
    run with `uvx` at the version the product pins, as `mise install` would bring it."""
    # Holds GEN-5.
    uv = shutil.which("uv")
    if not uv:
        pytest.skip("uv is not on the PATH")
    answers, generated = products[which]
    product = Path(shutil.copytree(generated, tmp_path / "product"))
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    environment["TARGET"] = "dev"
    done = subprocess.run([uv, "sync"], cwd=product, capture_output=True, text=True)
    if done.returncode != 0:
        pytest.skip(f"the product could not be synced here: {done.stderr[-400:]}")
    mise = tomllib.loads((product / "mise.toml").read_text())

    commands = mise["tasks"]["check"]["run"]
    assert len(commands) == 3 + sum(
        part in parts_of(answers) for part in ("dbt", "contracts", "stevin")
    ) + ("access_examples" in parts_of(answers))
    for command in commands:
        if command.startswith("stevin "):
            pin = mise["tools"]["pipx:stevin"]
            command = f"uv tool run --from stevin=={pin} {command}"
        done = subprocess.run(
            command,
            cwd=product,
            shell=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert done.returncode == 0, f"{command}\n{done.stdout}\n{done.stderr}"
