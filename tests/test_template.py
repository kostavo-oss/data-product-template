"""What the template writes, for the full and the bare answers."""

import subprocess
import sys

import pytest
import yaml
from conftest import BARE, files, generate

OPTIONAL = {
    "dbt": {"dbt/dbt_project.yml", "dbt/profiles.yml", "dbt/models/squares.sql"},
    "lely": {"lely.yml", ".github/workflows/plan.yml", ".github/workflows/apply.yml"},
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
}


def test_the_full_answers_write_everything(full):
    written = files(full)

    assert written >= ALWAYS
    assert OPTIONAL["dbt"] <= written
    assert OPTIONAL["lely"] <= written
    assert {"src/shop_data/cli.py", "src/shop_data/pipelines/example.py"} <= written
    assert "resources/shop-data.job.yml" in written


def test_the_bare_answers_skip_what_was_not_wanted(bare):
    written = files(bare)

    assert written >= ALWAYS
    assert not (OPTIONAL["dbt"] & written)
    assert not (OPTIONAL["lely"] & written)
    assert "src/bare/cli.py" in written
    assert "secret_scopes" not in (bare / "src/bare/cli.py").read_text()
    assert "--secret-scope" not in (bare / "resources/bare.job.yml").read_text()
    assert "pipx:" not in (bare / "mise.toml").read_text()
    assert "transform" not in (bare / "mise.toml").read_text()


def test_no_template_syntax_survives(full, bare):
    """What has `{{` left is dbt's Jinja or GitHub's own, in files that are theirs."""
    theirs = ("dbt/", ".github/workflows/")
    for project in (full, bare):
        for path in files(project):
            if path.startswith(theirs):
                continue
            text = (project / path).read_text(errors="replace")
            assert "{{" not in text, f"{path} still has template syntax"
            assert "@@" not in text, path


def test_the_package_name_is_derived_from_the_project_name(full):
    assert (full / "src/shop_data").is_dir()
    assert 'name = "shop-data"' in (full / "pyproject.toml").read_text()
    assert 'ingest = "shop_data.cli:app"' in (full / "pyproject.toml").read_text()
    assert 'name: "shop_data"' in (full / "dbt/dbt_project.yml").read_text()


def test_the_job_is_told_the_bundles_schema_names_by_reference(full):
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
    assert words[-2:] == ["--secret-scope", "shop_data"]
    assert tasks["ingest"]["disable_auto_optimization"] is True

    dbt = tasks["transform"]["dbt_task"]
    assert tasks["transform"]["depends_on"] == [{"task_key": "ingest"}]
    assert dbt["schema"] == "${resources.schemas.silver.name}"
    assert dbt["warehouse_id"] == "${var.warehouse_id}"
    assert all(isinstance(command, str) for command in dbt["commands"])
    assert "raw_schema: ${resources.schemas.raw.name}" in dbt["commands"][1]


def test_the_schemas_are_bundle_resources(full, bare):
    schemas = yaml.safe_load((full / "resources/schemas.yml").read_text())
    assert set(schemas["resources"]["schemas"]) == {"raw", "raw_staging", "silver"}

    schemas = yaml.safe_load((bare / "resources/schemas.yml").read_text())
    assert set(schemas["resources"]["schemas"]) == {"raw", "raw_staging"}


def test_the_warehouse_has_a_default_only_when_one_was_given(full, bare):
    with_ = yaml.safe_load((full / "databricks.yml").read_text())["variables"]
    without = yaml.safe_load((bare / "databricks.yml").read_text())["variables"]

    assert with_["warehouse_id"]["default"] == "abc123"
    assert "default" not in without["warehouse_id"]
    assert with_["catalog"]["default"] == "main"


def test_every_yaml_file_parses(full):
    for path in files(full):
        if path.endswith((".yml", ".yaml")):
            yaml.safe_load((full / path).read_text())


def test_the_python_passes_the_linter(full, bare):
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
def test_a_name_that_cannot_be_a_project_is_refused(tmp_path, name):
    with pytest.raises(AssertionError, match="pattern|match|invalid|Error"):
        generate({**BARE, "project_name": name}, tmp_path)


def test_the_jinja_in_the_models_is_only_what_dbt_should_see(full):
    """dbt reads Jinja in comments too: a config() in a comment sets the config."""
    for path in (full / "dbt/models").glob("*.sql"):
        for line in path.read_text().splitlines():
            if line.lstrip().startswith("--"):
                assert "{{" not in line, f"{path.name}: Jinja in a comment"


def test_the_readme_explains_each_part_that_was_included(full, bare):
    full_readme = (full / "README.md").read_text()
    bare_readme = (bare / "README.md").read_text()

    for word in ("lely", "caland", "dbt", "mise run transform", "mise run plan"):
        assert word in full_readme
    for word in ("lely", "caland", "dbt", "transform", "mise run plan"):
        assert word not in bare_readme
    assert "names no scope yet" in bare_readme
    assert "names no scope yet" not in full_readme
