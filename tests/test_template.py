"""What the template writes, for the full and the bare answers."""

import subprocess
import sys
import tomllib

import pytest
import yaml
from conftest import BARE, files, generate
from copier.errors import CopierError

OPTIONAL = {
    "dbt": {"dbt/dbt_project.yml", "dbt/profiles.yml", "dbt/models/squares.sql"},
    "lely": {"lely.yml", ".github/workflows/plan.yml", ".github/workflows/apply.yml"},
    "scope": {"ops/scope.py"},
}
ALWAYS = {
    "databricks.yml",
    "resources/schemas.yml",
    "pyproject.toml",
    "mise.toml",
    "mise.local.toml.example",
    ".mcp.json",
    "AGENTS.md",
    "README.md",
    ".dlt/config.toml",
    ".gitignore",
    "ops/names.py",
    "ops/dbt_env.py",
    ".github/workflows/ci.yml",
    ".copier-answers.yml",
}


def test_the_full_answers_write_everything(full):
    # Holds GEN-1.
    written = files(full)

    assert written >= ALWAYS
    assert OPTIONAL["dbt"] <= written
    assert OPTIONAL["lely"] <= written
    assert OPTIONAL["scope"] <= written
    assert {"src/shop_data/cli.py", "src/shop_data/pipelines/example.py"} <= written
    assert "resources/shop-data.job.yml" in written


def test_the_bare_answers_skip_what_was_not_wanted(bare):
    # Holds GEN-5, TSK-1, TSK-2, SEC-3.
    written = files(bare)

    assert written >= ALWAYS
    assert not (OPTIONAL["dbt"] & written)
    assert not (OPTIONAL["lely"] & written)
    assert not (OPTIONAL["scope"] & written)
    assert "src/bare/cli.py" in written
    assert "secret_scopes" not in (bare / "src/bare/cli.py").read_text()
    assert "--secret-scope" not in (bare / "resources/bare.job.yml").read_text()
    assert "pipx:" not in (bare / "mise.toml").read_text()
    assert "transform" not in (bare / "mise.toml").read_text()


def test_no_template_syntax_survives(full, bare):
    """What has `{{` left is dbt's Jinja or GitHub's own, in files that are theirs."""
    # Holds GEN-4.
    theirs = ("dbt/", ".github/workflows/")
    for project in (full, bare):
        for path in files(project):
            if path.startswith(theirs):
                continue
            text = (project / path).read_text(errors="replace")
            assert "{{" not in text, f"{path} still has template syntax"
            assert "@@" not in text, path


def test_the_package_name_is_derived_from_the_project_name(full):
    # Holds GEN-2, GEN-3, DLT-1.
    assert (full / "src/shop_data").is_dir()
    assert "package_name: shop_data" in (full / ".copier-answers.yml").read_text()
    assert 'name = "shop-data"' in (full / "pyproject.toml").read_text()
    assert 'ingest = "shop_data.cli:app"' in (full / "pyproject.toml").read_text()
    assert 'name: "shop_data"' in (full / "dbt/dbt_project.yml").read_text()


def test_the_job_is_told_the_bundles_schema_names_by_reference(full):
    # Holds BND-2, BND-3, BND-4, SEC-2.
    job = yaml.safe_load((full / "resources/shop-data.job.yml").read_text())
    tasks = {t["task_key"]: t for t in job["resources"]["jobs"]["shop_data"]["tasks"]}
    words = tasks["ingest"]["python_wheel_task"]["parameters"]

    assert words[:2] == ["run", "example"]
    assert words[words.index("--schema") + 1] == "${resources.schemas.raw.name}"
    assert (
        words[words.index("--staging-schema") + 1]
        == "${resources.schemas.raw_staging.name}"
    )
    assert words[words.index("--warehouse") + 1] == "${var.warehouse_id}"
    assert words[-2:] == ["--secret-scope", "${var.secret_scope}"]
    assert tasks["ingest"]["disable_auto_optimization"] is True

    dbt = tasks["transform"]["dbt_task"]
    assert tasks["transform"]["depends_on"] == [{"task_key": "ingest"}]
    assert dbt["schema"] == "${resources.schemas.silver.name}"
    assert dbt["warehouse_id"] == "${var.warehouse_id}"
    assert all(isinstance(command, str) for command in dbt["commands"])
    assert "raw_schema: ${resources.schemas.raw.name}" in dbt["commands"][1]


def test_the_schemas_are_bundle_resources(full, bare):
    # Holds BND-1.
    schemas = yaml.safe_load((full / "resources/schemas.yml").read_text())
    assert set(schemas["resources"]["schemas"]) == {"raw", "raw_staging", "silver"}

    schemas = yaml.safe_load((bare / "resources/schemas.yml").read_text())
    assert set(schemas["resources"]["schemas"]) == {"raw", "raw_staging"}


def test_the_warehouse_has_a_default_only_when_one_was_given(full, bare):
    # Holds BND-5.
    with_ = yaml.safe_load((full / "databricks.yml").read_text())["variables"]
    without = yaml.safe_load((bare / "databricks.yml").read_text())["variables"]

    assert with_["warehouse_id"]["default"] == "abc123"
    assert "default" not in without["warehouse_id"]
    assert with_["catalog"]["default"] == "main"


def test_every_yaml_file_parses(full):
    # Holds GEN-8.
    for path in files(full):
        if path.endswith((".yml", ".yaml")):
            yaml.safe_load((full / path).read_text())


def test_the_python_passes_the_linter(full, bare):
    # Holds GEN-8.
    for project in (full, bare):
        done = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "--isolated", str(project)],
            capture_output=True,
            text=True,
        )
        assert done.returncode == 0, done.stdout
        done = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "--isolated",
                str(project),
            ],
            capture_output=True,
            text=True,
        )
        assert done.returncode == 0, done.stdout


@pytest.mark.parametrize("name", ["1st", "my product", "x/y"])
def test_a_name_that_cannot_be_a_project_is_refused(template, tmp_path, name):
    # Holds GEN-3.
    with pytest.raises((CopierError, ValueError, OSError)):
        generate(template, {**BARE, "project_name": name}, tmp_path)


def test_the_jinja_in_the_models_is_only_what_dbt_should_see(full):
    """dbt reads Jinja in comments too: a config() in a comment sets the config."""
    # Holds DBT-3.
    for path in (full / "dbt/models").glob("*.sql"):
        for line in path.read_text().splitlines():
            if line.lstrip().startswith("--"):
                assert "{{" not in line, f"{path.name}: Jinja in a comment"


def test_the_readme_explains_each_part_that_was_included(full, bare):
    # Holds GEN-5, SEC-3, SEC-4, DOC-2.
    full_readme = (full / "README.md").read_text()
    bare_readme = (bare / "README.md").read_text()

    for word in ("lely", "caland", "dbt", "mise run transform", "mise run plan"):
        assert word in full_readme
    for word in ("lely", "caland", "dbt", "transform", "mise run plan"):
        assert word not in bare_readme
    assert "names no scope yet" in bare_readme
    assert "names no scope yet" not in full_readme
    assert "shows a failed `apply`" in full_readme
    assert "failed" not in bare_readme


def test_the_scope_is_a_step_before_the_bundle(full, bare):
    """The scope step feeds the bundle under lely, and the job reads the variable."""
    # Holds DEP-1, SEC-1, SEC-2, SEC-3.
    lely = yaml.safe_load((full / "lely.yml").read_text())
    steps = lely["steps"]
    assert [s["name"] for s in steps] == ["scope", "bundle"]
    assert steps[0]["uses"] == "./ops/scope.py:SecretScope"
    assert steps[0]["with"] == {"name": "shop_data"}
    assert steps[1]["with"]["vars"] == {"secret_scope": "${steps.scope.name}"}
    variables = yaml.safe_load((full / "databricks.yml").read_text())["variables"]
    assert variables["secret_scope"]["default"] == "shop_data"
    assert "SecretScope.main()" in (full / "ops/scope.py").read_text()
    assert "[tasks.scope]" in (full / "mise.toml").read_text()

    bare_variables = yaml.safe_load((bare / "databricks.yml").read_text())["variables"]
    assert "secret_scope" not in bare_variables


def test_git_ignores_a_file_of_credentials(full, bare, tmp_path):
    """Tools read a token from `.env`; one `git add` must not publish it."""
    # Holds TSK-5, SEC-5.
    for project in (full, bare):
        repository = tmp_path / project.name
        repository.mkdir()
        (repository / ".gitignore").write_text((project / ".gitignore").read_text())
        subprocess.run(["git", "init", "-q", str(repository)], check=True)

        for name in (".env", ".env.local", "mise.local.toml", ".dlt/secrets.toml"):
            done = subprocess.run(
                ["git", "check-ignore", "-q", name], cwd=repository, check=False
            )
            assert done.returncode == 0, f"{name} is not ignored"
        done = subprocess.run(
            ["git", "check-ignore", "-q", "mise.local.toml.example"],
            cwd=repository,
            check=False,
        )
        assert done.returncode == 1, "the example file is hidden"


def test_the_default_answers_write_a_product(template, tmp_path):
    """Every question has a default: a name is enough, and the rest is recorded."""
    # Holds GEN-1, GEN-2.
    project = generate(template, {"project_name": "defaults"}, tmp_path)
    answers = yaml.safe_load((project / ".copier-answers.yml").read_text())

    assert {name: answer for name, answer in answers.items() if name[0] != "_"} == {
        "project_name": "defaults",
        "package_name": "defaults",
        "catalog": "main",
        "warehouse_id": "",
        "secret_scope": "",
        "include_dbt": True,
        "include_stevin": False,
        "include_lely": True,
        "include_caland": True,
        "include_contracts": True,
    }
    assert files(project) >= ALWAYS | OPTIONAL["dbt"] | OPTIONAL["lely"]


def test_the_job_has_one_task_without_dbt_and_stevin(bare):
    # Holds BND-4.
    job = yaml.safe_load((bare / "resources/bare.job.yml").read_text())

    (task,) = job["resources"]["jobs"]["bare"]["tasks"]
    assert task["task_key"] == "ingest"


def test_the_targets_are_dev_and_prod(full, bare):
    # Holds BND-5.
    for project in (full, bare):
        targets = yaml.safe_load((project / "databricks.yml").read_text())["targets"]

        assert targets == {
            "dev": {"mode": "development", "default": True},
            "prod": {"mode": "production"},
        }


def test_the_wheel_carries_dlts_config_and_no_secrets(full):
    # Holds BND-6.
    wheel = tomllib.loads((full / "pyproject.toml").read_text())["tool"]["hatch"]["build"]

    assert wheel["targets"]["wheel"]["packages"] == ["src/shop_data"]
    assert wheel["targets"]["wheel"]["force-include"] == {
        ".dlt/config.toml": "shop_data/.dlt/config.toml"
    }
    assert not (full / ".dlt/secrets.toml").exists()


def test_mise_brings_the_tools_and_the_tasks_of_what_was_chosen(full, bare):
    # Holds TSK-1, TSK-2, TSK-3, SEC-4.
    always = {"dev", "check", "fix", "clean", "deploy", "job", "doctor", "ingest"}
    chosen = {"transform", "scope", "plan", "apply", "destroy", "secrets"}
    with_ = tomllib.loads((full / "mise.toml").read_text())
    without = tomllib.loads((bare / "mise.toml").read_text())

    assert set(without["tools"]) == {"python", "uv", "databricks-cli"}
    assert set(with_["tools"]) == set(without["tools"]) | {"pipx:lely", "pipx:caland"}
    assert set(without["tasks"]) == always
    assert {name for name in with_["tasks"] if ":" not in name} == always | chosen
    assert with_["tasks"]["secrets"]["run"] == "caland"
    assert with_["tasks"]["dev"]["run"] == "uv run ingest run example"

    gate = ["uv run ruff check .", "uv run ruff format --check .", "uv run ingest list"]
    assert without["tasks"]["check"]["run"] == gate
    assert with_["tasks"]["check"]["run"][:3] == gate
    assert with_["tasks"]["check"]["run"][3].startswith("uv run --group dev dbt parse ")
    for project in (full, bare):
        workflow = yaml.safe_load((project / ".github/workflows/ci.yml").read_text())
        runs = [step.get("run") for step in workflow["jobs"]["check"]["steps"]]
        assert runs.index("mise run check") < runs.index("mise run dev")
