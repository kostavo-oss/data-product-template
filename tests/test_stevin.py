"""stevin in a product: the four combinations of dbt and stevin, and the access examples.

Needs uv, and the network the first time: `stevin validate` and `lely validate` are run
with `uvx`, stevin at the version the product's `mise.toml` pins. Both are offline
commands. No workspace is reached: nothing here plans or applies.
"""

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml
from conftest import BARE, FULL, files, generate

STEVIN = {
    "stevin/stevin.yml",
    "stevin/tables/squares.yml",
    "stevin/tables/numbers.yml",
    "sql/squares.sql",
    "ops/tables.py",
}
EXAMPLES = {
    "stevin/security/README.md",
    "stevin/security/region_members.yml",
    "stevin/security/by_region.yml",
    "stevin/security/orders.yml",
}
SQUARES = "contracts/output/squares/v1.odcs.yaml"
TASKS = {"tables:validate", "tables:plan", "tables:apply", "tables:drift"}
# What `stevin validate` says of a target in development mode: the bundle's CLI gives a
# schema its deployed name, and `validate` asks nothing. It is a note, not a finding.
NOT_SETTLED = "Not settled here: ${resources.schemas."
# A stand-in for the stevin command: it writes down the words it was given.
STAND_IN = '#!/bin/sh\necho "$* in $(basename "$PWD") for $LELY_TARGET" > "$SAID"\n'
RUN_THE_STEP = """
import sys
from pathlib import Path

sys.path.insert(0, "ops")
from lely.testing import check_plan, context
from tables import Tables

ctx = context(None, target="dev", name="tables", root=Path.cwd())
plan = check_plan(Tables(), ctx)
print([(change.key, change.action, change.summary) for change in plan.changes])
Tables().apply(ctx, plan)
"""


def uv() -> str:
    found = shutil.which("uv")
    if not found:
        pytest.skip("uv is not on the PATH")
    return found


def run(project: Path, *words: str, env: dict[str, str] | None = None):
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    return subprocess.run(
        list(words),
        cwd=project,
        capture_output=True,
        text=True,
        env={**environment, **(env or {})},
    )


def stevin(project: Path, *words: str):
    """`stevin <words>` in a product, at the version its mise.toml pins."""
    pin = tomllib.loads((project / "mise.toml").read_text())["tools"]["pipx:stevin"]
    return run(project, uv(), "tool", "run", "--from", f"stevin=={pin}", "stevin", *words)


def validate(project: Path, *words: str):
    return stevin(project, "validate", "-c", "stevin/stevin.yml", *words)


def tasks_of(project: Path) -> list[dict]:
    job = yaml.safe_load(next((project / "resources").glob("*.job.yml")).read_text())
    (only,) = job["resources"]["jobs"].values()
    return only["tasks"]


@pytest.fixture(scope="session")
def sql(template, tmp_path_factory) -> Path:
    """stevin and no dbt, with everything else: the product that does traditional SQL."""
    answers = {
        **FULL,
        "project_name": "sql-shop",
        "include_dbt": False,
        "include_stevin": True,
        "include_access_examples": True,
    }
    return generate(template, answers, tmp_path_factory.mktemp("sql"))


@pytest.fixture(scope="session")
def sql_bare(template, tmp_path_factory) -> Path:
    """stevin and nothing else: no dbt, no lely, no contracts, no access examples."""
    answers = {**BARE, "project_name": "sql-bare", "include_stevin": True}
    return generate(template, answers, tmp_path_factory.mktemp("sql_bare"))


@pytest.fixture(scope="session")
def both(template, tmp_path_factory) -> Path:
    """stevin next to dbt, with everything else."""
    answers = {
        **FULL,
        "project_name": "both-shop",
        "include_stevin": True,
        "include_access_examples": True,
    }
    return generate(template, answers, tmp_path_factory.mktemp("both"))


@pytest.fixture(scope="session")
def both_bare(template, tmp_path_factory) -> Path:
    """stevin next to dbt, and nothing else."""
    answers = {
        **BARE,
        "project_name": "both-bare",
        "include_dbt": True,
        "include_stevin": True,
    }
    return generate(template, answers, tmp_path_factory.mktemp("both_bare"))


@pytest.fixture(scope="session")
def with_stevin(sql, sql_bare, both, both_bare) -> tuple[Path, ...]:
    return (sql, sql_bare, both, both_bare)


# ── what is written ──────────────────────────────────────────────────────────


def test_the_four_combinations_write_what_each_needs(full, bare, sql, both):
    """dbt only, neither, stevin only, and both."""
    # Holds STV-1.
    assert not [path for path in files(full) if path.startswith(("stevin/", "sql/"))]
    assert not [path for path in files(bare) if path.startswith(("stevin/", "sql/"))]
    assert "dbt/models/squares.sql" in files(full)

    assert files(sql) & STEVIN == STEVIN - {"stevin/tables/numbers.yml"}
    assert not [path for path in files(sql) if path.startswith("dbt/")]

    assert files(both) & STEVIN == {"stevin/stevin.yml", "stevin/tables/numbers.yml"}
    assert "dbt/models/squares.sql" in files(both)


def test_without_stevin_nothing_mentions_it(full, bare):
    """The answers file records the answer, as it does for every question."""
    # Holds GEN-2, GEN-5.
    for project in (full, bare):
        for path in files(project) - {".copier-answers.yml"}:
            text = (project / path).read_text(errors="replace").lower()
            assert "stevin" not in text, path
            assert "tables:plan" not in text, path
        assert not (files(project) & (STEVIN | EXAMPLES))
        answers = yaml.safe_load((project / ".copier-answers.yml").read_text())
        assert answers["include_stevin"] is False
        assert "include_access_examples" not in answers


def test_the_access_examples_are_asked_only_with_stevin(template, tmp_path):
    # Holds GEN-2, ACC-1.
    answers = {**BARE, "project_name": "asked", "include_access_examples": True}
    project = generate(template, answers, tmp_path)

    assert not [path for path in files(project) if path.startswith("stevin/")]
    assert "grants:" not in (project / "resources/schemas.yml").read_text()


def test_the_access_examples_are_written_only_when_wanted(sql, both, sql_bare, both_bare):
    # Holds ACC-1.
    for project in (sql, both):
        assert files(project) >= EXAMPLES
    for project in (sql_bare, both_bare):
        assert not (files(project) & EXAMPLES)
        assert "security" not in (project / "stevin/stevin.yml").read_text()
        assert "security" not in (project / "mise.toml").read_text()
        assert "grants:" not in (project / "resources/schemas.yml").read_text()


def test_no_template_syntax_survives_and_every_yaml_file_parses(with_stevin):
    # Holds GEN-4, GEN-8.
    for project in with_stevin:
        for path in files(project):
            if path.startswith(("dbt/", ".github/workflows/")):
                continue
            text = (project / path).read_text(errors="replace")
            assert "{{" not in text, f"{path} still has template syntax"
            assert "{%" not in text, f"{path} still has template syntax"
            if path.endswith((".yml", ".yaml")):
                yaml.safe_load(text)


def test_the_python_passes_the_linter(with_stevin):
    # Holds GEN-8.
    for project in with_stevin:
        for words in (["check"], ["format", "--check"]):
            done = subprocess.run(
                [sys.executable, "-m", "ruff", *words, "--isolated", str(project)],
                capture_output=True,
                text=True,
            )
            assert done.returncode == 0, done.stdout


# ── the bundle: the schema, the job ──────────────────────────────────────────


def test_the_silver_schema_is_the_bundles_with_dbt_or_stevin(with_stevin):
    # Holds BND-1, STV-2.
    for project in with_stevin:
        schemas = yaml.safe_load((project / "resources/schemas.yml").read_text())
        assert set(schemas["resources"]["schemas"]) == {"raw", "raw_staging", "silver"}
        assert '("SILVER", "silver")' in (project / "ops/names.py").read_text()


def test_without_dbt_the_job_fills_the_table_with_a_sql_task_after_ingest(sql, sql_bare):
    # Holds STV-4.
    for project in (sql, sql_bare):
        ingest, transform = tasks_of(project)

        assert (ingest["task_key"], transform["task_key"]) == ("ingest", "transform")
        assert transform["depends_on"] == [{"task_key": "ingest"}]
        task = transform["sql_task"]
        assert task["warehouse_id"] == "${var.warehouse_id}"
        assert (project / "resources" / task["file"]["path"]).resolve() == (
            project / "sql/squares.sql"
        )
        assert task["parameters"] == {
            "catalog": "${var.catalog}",
            "raw_schema": "${resources.schemas.raw.name}",
            "silver_schema": "${resources.schemas.silver.name}",
        }


def test_with_dbt_the_job_has_no_sql_task(both, both_bare):
    # Holds BND-4.
    for project in (both, both_bare):
        ingest, transform = tasks_of(project)

        assert "sql_task" not in transform
        assert transform["dbt_task"]["schema"] == "${resources.schemas.silver.name}"
        assert not (project / "sql").exists()


def test_the_sql_names_no_schema_and_takes_every_name_as_a_parameter(sql, sql_bare):
    # Holds STV-4.
    for project in (sql, sql_bare):
        package = project.name.replace("-", "_")
        lines = (project / "sql/squares.sql").read_text().splitlines()
        code = "\n".join(line for line in lines if not line.lstrip().startswith("--"))
        parameters = tasks_of(project)[1]["sql_task"]["parameters"]

        for name in ("main", package, f"{package}_raw", "dev_", "${"):
            assert name not in code, name
        assert "IDENTIFIER(:catalog || '.' || :silver_schema || '.squares')" in code
        assert "IDENTIFIER(:catalog || '.' || :raw_schema || '.numbers')" in code
        # Every marker in the file is a parameter of the task, and the other way round.
        words = code.replace("(", " ").replace(")", " ").split()
        assert {w[1:] for w in words if w.startswith(":")} == set(parameters)
        # It fills the table and never makes it: that is stevin's.
        assert code.startswith("INSERT OVERWRITE")
        assert "CREATE" not in code.upper()


# ── the specs, checked by stevin itself ──────────────────────────────────────


def test_stevin_takes_its_targets_from_the_bundle(with_stevin):
    # Holds STV-2.
    for project in with_stevin:
        config = yaml.safe_load((project / "stevin/stevin.yml").read_text())

        assert config["bundle"] == "../databricks.yml"
        assert (project / "stevin" / config["bundle"]).resolve().exists()
        assert config["specs"] == ["tables"]
        assert "targets" not in config
        assert "schemas" not in config
        for path in (project / "stevin").rglob("*.yml"):
            assert "schema:" not in path.read_text(), f"{path.name} declares a schema"


def test_the_specs_validate_for_both_targets(with_stevin):
    # Holds STV-6.
    for project in with_stevin:
        default = validate(project)
        assert default.returncode == 0, default.stdout + default.stderr
        assert "1 spec OK." in default.stdout
        # The default target is in development mode: its schemas' names are the CLI's.
        assert NOT_SETTLED in default.stdout + default.stderr

        prod = validate(project, "-t", "prod")
        assert prod.returncode == 0, prod.stdout + prod.stderr
        assert prod.stdout.strip() == "1 spec OK."
        assert "warning" not in (default.stdout + default.stderr + prod.stderr).lower()


def test_without_dbt_the_table_is_declared_and_its_shape_is_said_once(sql, sql_bare):
    # Holds STV-3.
    from_contract = yaml.safe_load((sql / "stevin/tables/squares.yml").read_text())
    declared = yaml.safe_load((sql_bare / "stevin/tables/squares.yml").read_text())
    table = "${catalog}.${resources.schemas.silver.name}.squares"

    # With contracts the shape is the contract's, and the spec says none of it.
    assert from_contract["table"] == declared["table"] == table
    assert from_contract["from_contract"] == "../../" + SQUARES
    assert (sql / "stevin/tables" / from_contract["from_contract"]).resolve().exists()
    assert not ({"columns", "constraints", "comment"} & set(from_contract))
    # Without, the spec declares what the contract would have said.
    contract = yaml.safe_load((sql / SQUARES).read_text())["schema"][0]
    assert "from_contract" not in declared
    assert [(c["name"], c["type"]) for c in declared["columns"]] == [
        (p["name"], p["physicalType"]) for p in contract["properties"]
    ]
    assert [c.get("comment") for c in declared["columns"]] == [
        p["description"] for p in contract["properties"]
    ]
    assert declared["columns"][0]["nullable"] is False
    assert declared["constraints"] == [{"primary_key": ["id"]}]
    assert declared["comment"] == contract["description"]
    for spec in (from_contract, declared):
        assert spec["cluster_by"] == ["id"]
        assert "grants" not in spec


def test_the_contract_of_squares_is_there_with_stevin_and_no_dbt(sql):
    # Holds CON-2, CON-3, CON-4.
    product = yaml.safe_load((sql / "dataproduct.yaml").read_text())
    contract = yaml.safe_load((sql / SQUARES).read_text())
    tasks = tomllib.loads((sql / "mise.toml").read_text())["tasks"]

    (port,) = product["outputPorts"]
    assert (port["name"], port["contractId"]) == ("squares", "sql-shop.squares")
    assert contract["id"] == "sql-shop.squares"
    assert [p["name"] for p in contract["schema"][0]["properties"]] == [
        "id",
        "square",
        "root",
    ]
    (server,) = contract["servers"]
    assert (server["type"], server["schema"]) == ("databricks", "${SILVER:-sql_shop}")
    assert "contracts/output/numbers/v1.odcs.yaml" not in files(sql)
    # The table is filled on the workspace only: no local test, and no dbt to write to.
    assert "contracts:test" not in tasks
    assert "contracts:dbt" not in tasks
    assert "dbt" not in (sql / SQUARES).read_text()

    done = run(sql, uv(), "run", "ops/ports.py", "lint")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Data contract is valid" in done.stdout


def test_a_spec_whose_contract_is_gone_is_refused(sql, tmp_path):
    # Holds STV-3.
    project = Path(shutil.copytree(sql, tmp_path / "sql"))
    (project / SQUARES).unlink()

    done = validate(project)

    assert done.returncode == 1
    assert "squares.yml" in done.stdout + done.stderr
    assert "v1.odcs.yaml" in done.stdout + done.stderr


def test_with_dbt_stevin_governs_the_landed_table_and_leaves_dbts_alone(both, tmp_path):
    # Holds STV-5.
    config = yaml.safe_load((both / "stevin/stevin.yml").read_text())
    spec = yaml.safe_load((both / "stevin/tables/numbers.yml").read_text())

    assert config["owned_elsewhere"] == {
        "${catalog}.*.numbers": "dlt",
        "${catalog}.*.squares": "dbt",
    }
    assert spec["table"] == "${catalog}.${resources.schemas.raw.name}.numbers"
    # A tag and a grant, and nothing of the shape: that is dlt's.
    assert set(spec) == {"table", "tags", "grants"}
    assert spec["grants"] == [{"principal": "data_engineers", "privileges": ["SELECT"]}]

    # A spec for the table dbt builds is refused, by name.
    project = Path(shutil.copytree(both, tmp_path / "both"))
    (project / "stevin/tables/squares.yml").write_text(
        "table: ${catalog}.${resources.schemas.silver.name}.squares\n"
        "columns:\n  - {name: id, type: bigint}\n"
    )
    for words in ((), ("-t", "prod")):
        done = validate(project, *words)
        assert done.returncode == 1, done.stdout + done.stderr
        assert "squares is dbt's" in done.stdout + done.stderr


def test_the_governing_spec_warns_when_nothing_names_the_owner(both, tmp_path):
    """Why `owned_elsewhere` names the landed table: `validate` sees no workspace."""
    # Holds STV-5.
    project = Path(shutil.copytree(both, tmp_path / "both"))
    config = project / "stevin/stevin.yml"
    config.write_text(config.read_text().replace("  ${catalog}.*.numbers: dlt\n", ""))

    done = validate(project, "-t", "prod")

    assert done.returncode == 0, done.stdout + done.stderr
    assert "warning: main.both_shop_raw.numbers has no columns' types" in (
        done.stdout + done.stderr
    ).replace("\n", " ")


# ── where stevin runs: the tasks, and the step of the deploy ─────────────────


def test_the_tasks_are_there_and_stevin_is_pinned_in_one_place(with_stevin):
    # Holds STV-7.
    for project in with_stevin:
        mise = tomllib.loads((project / "mise.toml").read_text())
        tasks = mise["tasks"]

        assert mise["tools"]["pipx:stevin"] == "0.4.0a1"
        assert {name for name in tasks if name.startswith("tables:")} == TASKS
        assert tasks["tables:validate"]["run"] == "stevin validate -c stevin/stevin.yml"
        assert "stevin validate -c stevin/stevin.yml" in tasks["check"]["run"]
        for verb in ("plan", "apply", "drift"):
            command = tasks[f"tables:{verb}"]["run"]
            assert f"stevin {verb} -c stevin/stevin.yml -t $TARGET" in command
            assert command.startswith("BUNDLE_VAR_warehouse_id=$WAREHOUSE_ID ")
        # Applying from a task asks first: consent is not in the command.
        assert "--yes" not in tasks["tables:apply"]["run"]
        pinned = [
            path
            for path in files(project)
            if "0.4.0a1" in (project / path).read_text(errors="replace")
        ]
        assert pinned == ["mise.toml"]


def test_ci_checks_the_specs_through_the_check_task(with_stevin):
    # Holds TSK-3.
    for project in with_stevin:
        workflow = (project / ".github/workflows/ci.yml").read_text()
        assert "mise run check" in workflow
        assert "stevin" not in workflow


def test_without_dbt_the_tables_are_a_step_after_the_bundle(sql, sql_bare):
    # Holds DEP-1, STV-8.
    steps = yaml.safe_load((sql / "lely.yml").read_text())["steps"]

    assert [step["name"] for step in steps] == ["scope", "bundle", "tables"]
    assert steps[2] == {"name": "tables", "uses": "./ops/tables.py:Tables"}
    # Not lely's own `stevin` step: lely 0.3 can plan with it and refuses to apply.
    assert "uses: stevin" not in (sql / "lely.yml").read_text()
    # Without lely there is no step and no file for one: the tasks are what there is.
    assert not (sql_bare / "lely.yml").exists()
    assert not (sql_bare / "ops/tables.py").exists()


def test_with_dbt_stevin_is_no_step_of_the_deploy(both):
    """Its spec governs a table the job lands, which a new target does not have yet."""
    # Holds DEP-1, STV-9.
    steps = yaml.safe_load((both / "lely.yml").read_text())["steps"]

    assert [step["name"] for step in steps] == ["scope", "bundle"]
    assert not (both / "ops/tables.py").exists()
    assert "after the job has run once" in (both / "README.md").read_text()


def test_lely_takes_the_config_with_the_tables_step(sql):
    # Holds STV-8.
    done = run(sql, uv(), "tool", "run", "--from", "lely>=0.3", "lely", "validate")

    assert done.returncode == 0, done.stdout + done.stderr
    assert "3 steps" in done.stdout
    assert "tables  takes and gives nothing" in done.stdout


def test_the_tables_step_runs_stevin_apply_for_the_target(sql, tmp_path):
    """Held to lely's rules for a plan, then applied with a stand-in for stevin."""
    # Holds STV-8.
    stand_in = tmp_path / "bin" / "stevin"
    stand_in.parent.mkdir()
    stand_in.write_text(STAND_IN)
    stand_in.chmod(0o755)
    said = tmp_path / "said"

    done = run(
        sql,
        *(uv(), "run", "--no-project", "--with", "lely>=0.3", "python", "-c"),
        RUN_THE_STEP,
        env={
            "PATH": f"{stand_in.parent}{os.pathsep}{os.environ['PATH']}",
            "SAID": str(said),
        },
    )

    assert done.returncode == 0, done.stdout + done.stderr
    words = "stevin apply --config stevin/stevin.yml --target dev --yes"
    assert f"('tables', 'run', 'runs {words}')" in done.stdout
    assert said.read_text().strip() == f"{words[7:]} in sql-shop for dev"


# ── the access examples ──────────────────────────────────────────────────────


def test_the_access_examples_are_checked_and_not_planned_until_switched_on(sql, both):
    # Holds ACC-2.
    for project in (sql, both):
        checks = tomllib.loads((project / "mise.toml").read_text())["tasks"]["check"]
        config = (project / "stevin/stevin.yml").read_text()

        assert (
            "stevin validate -c stevin/stevin.yml -t $TARGET stevin/security/*.yml"
            in checks["run"]
        )
        assert yaml.safe_load(config)["specs"] == ["tables"]
        assert "  # - security\n" in config


def test_the_access_examples_validate_on_their_own_and_switched_on(sql, both, tmp_path):
    # Holds ACC-2.
    for project in (sql, both):
        specs = sorted(
            path.relative_to(project).as_posix()
            for path in (project / "stevin/security").glob("*.yml")
        )
        for target in ("dev", "prod"):
            alone = validate(project, "-t", target, *specs)
            assert alone.returncode == 0, alone.stdout + alone.stderr
            assert "3 specs OK." in alone.stdout
            assert "warning" not in (alone.stdout + alone.stderr).lower()

        on = Path(shutil.copytree(project, tmp_path / project.name))
        config = on / "stevin/stevin.yml"
        config.write_text(
            config.read_text().replace("  # - security\n", "  - security\n")
        )
        assert yaml.safe_load(config.read_text())["specs"] == ["tables", "security"]
        for words in ((), ("-t", "prod")):
            done = validate(on, *words)
            assert done.returncode == 0, done.stdout + done.stderr
            assert "4 specs OK." in done.stdout
            assert "warning" not in (done.stdout + done.stderr).lower()


def test_the_row_filter_is_a_function_the_example_table_names(sql):
    # Holds ACC-3.
    security = sql / "stevin/security"
    members = yaml.safe_load((security / "region_members.yml").read_text())
    function = yaml.safe_load((security / "by_region.yml").read_text())
    orders = yaml.safe_load((security / "orders.yml").read_text())
    silver = "${catalog}.${resources.schemas.silver.name}"

    assert members["table"] == f"{silver}.region_members"
    assert {row["group_name"] for row in members["seed"]} == {"sales_emea", "sales_apac"}
    assert function["function"] == f"{silver}.by_region"
    assert "is_account_group_member(m.group_name)" in function["body"]
    assert f"{silver}.region_members" in function["body"]
    assert orders["row_filter"] == {
        "function": function["function"],
        "columns": ["region"],
    }
    tagged = [c["name"] for c in orders["columns"] if c.get("tags") == {"pii": "email"}]
    assert tagged == ["customer_email"]


def test_a_function_no_filter_names_is_refused(sql, tmp_path):
    """The function spec is valid only because the example table names it."""
    # Holds ACC-3.
    project = Path(shutil.copytree(sql, tmp_path / "sql"))
    (project / "stevin/security/orders.yml").unlink()
    specs = ["stevin/security/by_region.yml", "stevin/security/region_members.yml"]

    done = validate(project, "-t", "prod", *specs)

    assert done.returncode == 1
    assert "is named by no column mask or row filter" in (
        done.stdout + done.stderr
    ).replace("\n", " ")


def test_the_schema_grants_stand_in_the_bundle_as_comments(sql, both, sql_bare):
    """The schemas are the bundle's, so groups per schema is not a stevin spec."""
    # Holds ACC-4.
    for project in (sql, both):
        path = project / "resources/schemas.yml"
        as_written = yaml.safe_load(path.read_text())["resources"]["schemas"]
        assert "grants" not in as_written["silver"]

        lines = path.read_text().splitlines()
        start = lines.index("      # grants:")
        on = [line.replace("# ", "", 1) for line in lines[start:]]
        switched = yaml.safe_load("\n".join(lines[:start] + on))
        assert switched["resources"]["schemas"]["silver"]["grants"] == [
            {
                "principal": "data_engineers",
                "privileges": ["USE_SCHEMA", "CREATE_TABLE", "MODIFY", "SELECT"],
            },
            {"principal": "analysts", "privileges": ["USE_SCHEMA", "SELECT"]},
        ]
        assert not list((project / "stevin").rglob("_schema.yml"))


def test_the_readme_of_the_examples_names_every_placeholder_first(sql, both):
    # Holds ACC-5.
    for project in (sql, both):
        readme = (project / "stevin/security/README.md").read_text()
        top = readme.split("## Switching it on")[0]
        specs = "".join(
            path.read_text() for path in (project / "stevin/security").glob("*.yml")
        )
        schemas = (project / "resources/schemas.yml").read_text()

        for group in ("sales_emea", "sales_apac", "sales_leads"):
            assert f"`{group}`" in top
            assert group in specs
        for group in ("data_engineers", "analysts"):
            assert f"`{group}`" in top
            assert group in schemas
        assert "`pii`" in top
        for hard in (
            "identity provider",
            "governed tag",
            "slow row filter",
            "as another",
        ):
            assert hard in top.replace("\n", " "), hard
        # The policy is shown twice and written by neither stevin nor the template.
        assert "databricks_policy_info" in readme
        assert "CREATE POLICY mask_pii" in readme
        assert "stevin never writes a policy" in readme.replace("\n", " ")
        assert not list((project / "stevin").rglob("*.tf"))
        assert not list((project / "stevin").rglob("*.sql"))


# ── the pages ────────────────────────────────────────────────────────────────


def test_the_rules_for_agents_come_with_stevin(sql, both):
    # Holds DOC-1.
    without_dbt = (sql / "AGENTS.md").read_text().replace("\n ", "")
    with_dbt = (both / "AGENTS.md").read_text().replace("\n ", "")

    for rules in (without_dbt, with_dbt):
        assert "is changed through its spec in `stevin/`, never by hand" in rules
        assert "A schema is the bundle's, and takes no stevin spec." in rules
    assert "Never a schema name or a catalog in a `.sql` file." in without_dbt
    assert "A table dbt builds takes no stevin spec" in with_dbt
    assert "go in dbt's config" in with_dbt
    assert "`.sql` file in `sql/`" not in with_dbt


def test_the_readme_has_the_tasks_and_the_order_of_a_first_run(sql, sql_bare, both):
    # Holds DOC-2.
    for project in (sql, sql_bare, both):
        readme = (project / "README.md").read_text()
        for task in TASKS:
            assert f"mise run {task}" in readme
        assert "## Tables and access: stevin" in readme
        assert "What is not stevin's." in readme

    for project in (sql, sql_bare):
        readme = (project / "README.md").read_text()
        order = [
            readme.index(f"mise run {t}  ") for t in ("deploy", "tables:apply", "job")
        ]
        assert order == sorted(order)
    readme = (both / "README.md").read_text()
    order = [readme.index(f"mise run {t}  ") for t in ("deploy", "job", "tables:apply")]
    assert order == sorted(order)
