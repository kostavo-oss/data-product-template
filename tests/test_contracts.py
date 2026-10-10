"""The contracts a product gets, and `ops/ports.py`, run.

Needs uv, and the network the first time: `ops/ports.py` runs the Data Contract CLI with
`uvx`, at the version it names. No workspace is reached.
"""

import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml
from conftest import BARE, FULL, files, generate

CONTRACTS = {"dataproduct.yaml", "ops/ports.py", "contracts/input/README.md"}
SQUARES = "contracts/output/squares/v1.odcs.yaml"
NUMBERS = "contracts/output/numbers/v1.odcs.yaml"
GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid"]
# The second column of the contract the example pipeline's table gets.
SQUARE = (
    "      - name: square\n"
    "        description: The number times itself.\n"
    "        logicalType: integer\n"
    "        physicalType: bigint\n"
)
_left_by_runs = shutil.ignore_patterns(".venv", "*.duckdb", "site", "target", "logs")

PRODUCER = {
    "apiVersion": "v1.1.0",
    "kind": "DataProduct",
    "id": "payments",
    "outputPorts": [
        {
            "name": "transactions",
            "version": "1.0.0",
            "contractId": "payments.transactions",
        }
    ],
}
PRODUCERS_CONTRACT = {
    "apiVersion": "v3.2.0",
    "kind": "DataContract",
    "id": "payments.transactions",
    "version": "1.0.0",
    "status": "active",
    "schema": [
        {
            "name": "transactions",
            "properties": [
                {"name": "id", "logicalType": "string", "required": True},
                {"name": "amount", "logicalType": "number"},
            ],
        }
    ],
}
INPUT_PORT = {
    "name": "transactions",
    "version": "1.0.0",
    "contractId": "payments.transactions",
    "authoritativeDefinitions": [
        {
            "type": "dataContract",
            "url": "../payments/contracts/output/transactions/v1.odcs.yaml",
        },
        {"type": "dataProduct", "url": "../payments/dataproduct.yaml"},
    ],
}
SNAPSHOT = "contracts/input/transactions/v1.odcs.yaml"
SCHEMA = "src/landed/schemas/transactions.schema.yaml"
# The line contracts/input/README.md gives a pipeline, in a pipeline.
TAKES_THE_SCHEMA = (
    'leeghwater.create_pipeline("transactions", import_schema_path=SCHEMAS)'
)
PIPELINE = f'''"""Loads the input port transactions: the rows it is given, as JSON."""

import json
from pathlib import Path

import dlt
import leeghwater
from leeghwater import pipeline

SCHEMAS = Path(__file__).parent.parent / "schemas"


@dlt.resource
def transactions(rows: str):
    yield from json.loads(rows)


@pipeline
def payments(rows: str = "[]"):
    p = {TAKES_THE_SCHEMA}
    return leeghwater.run(p, transactions(rows))
'''


def uv() -> str:
    found = shutil.which("uv")
    if not found:
        pytest.skip("uv is not on the PATH")
    return found


def ports(project: Path, *words: str, env: dict[str, str] | None = None):
    """`uv run ops/ports.py <words>` in a product."""
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    return subprocess.run(
        [uv(), "run", "ops/ports.py", *words],
        cwd=project,
        capture_output=True,
        text=True,
        env={**environment, **(env or {})},
    )


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{path.name} has no {old!r}"
    path.write_text(text.replace(old, new))


@pytest.fixture(scope="session")
def landed(template, tmp_path_factory) -> Path:
    """Contracts without dbt: the output port is the table the example pipeline loads."""
    answers = {**BARE, "project_name": "landed", "include_contracts": True}
    return generate(template, answers, tmp_path_factory.mktemp("landed"))


@pytest.fixture(scope="session")
def plain(template, tmp_path_factory) -> Path:
    """dbt and the tools, without contracts."""
    answers = {**FULL, "project_name": "plain", "include_contracts": False}
    return generate(template, answers, tmp_path_factory.mktemp("plain"))


@pytest.fixture
def copy(landed, tmp_path) -> Path:
    """A product of its own to change, beside which a producer can stand."""
    return Path(shutil.copytree(landed, tmp_path / "landed", ignore=_left_by_runs))


# ── what is written ──────────────────────────────────────────────────────────


def test_contracts_are_written_with_and_without_dbt(full, landed):
    # Holds CON-1.
    assert files(full) >= CONTRACTS | {SQUARES}
    assert NUMBERS not in files(full)
    assert files(landed) >= CONTRACTS | {NUMBERS}
    assert SQUARES not in files(landed)


def test_nothing_of_contracts_is_written_when_not_wanted(bare, plain):
    # Holds GEN-5, DOC-1.
    for project in (bare, plain):
        written = files(project)
        assert not (CONTRACTS & written)
        assert not [path for path in written if path.startswith("contracts/")]
        for path in ("mise.toml", "README.md", "AGENTS.md", ".github/workflows/ci.yml"):
            assert "contract" not in (project / path).read_text().lower(), path
        assert "fetch-depth" not in (project / ".github/workflows/ci.yml").read_text()


def test_each_output_port_names_the_contract_beside_it(full, landed):
    # Holds CON-1.
    for project, path in ((full, SQUARES), (landed, NUMBERS)):
        product = yaml.safe_load((project / "dataproduct.yaml").read_text())
        contract = yaml.safe_load((project / path).read_text())

        assert product["apiVersion"] == "v1.1.0"
        assert product["kind"] == "DataProduct"
        assert product["id"] == project.name
        (port,) = product["outputPorts"]
        assert port["name"] == contract["schema"][0]["name"] == Path(path).parent.name
        assert port["contractId"] == contract["id"]
        assert port["version"] == contract["version"] == "1.0.0"
        assert contract["apiVersion"] == "v3.2.0"
        assert "inputPorts" not in product


def test_the_contract_describes_what_the_example_makes(full, landed):
    """The columns of the dbt model, and of the table the pipeline loads."""
    # Holds CON-2.

    def columns(contract: Path) -> list[str]:
        schema = yaml.safe_load(contract.read_text())["schema"][0]
        return [column["name"] for column in schema["properties"]]

    model = (full / "dbt/models/squares.sql").read_text()
    assert columns(full / SQUARES) == ["id", "square", "root"]
    for column in ("id,", "square,", "as root"):
        assert column in model
    assert columns(landed / NUMBERS) == ["id", "square"]
    assert (
        '{"id": n, "square": n * n}'
        in (landed / "src/landed/pipelines/example.py").read_text()
    )


def test_the_servers_are_the_local_file_and_the_deployed_table(full, landed):
    # Holds CON-3.
    servers = yaml.safe_load((landed / NUMBERS).read_text())["servers"]
    assert [(s["server"], s["type"]) for s in servers] == [
        ("local", "duckdb"),
        ("databricks", "databricks"),
    ]
    assert servers[0]["database"] == "example.duckdb"
    assert servers[1]["catalog"] == "${CATALOG:-main}"
    assert servers[1]["schema"] == "${RAW:-landed_raw}"

    # A dbt model is built on the workspace only: there is no local copy to name.
    (server,) = yaml.safe_load((full / SQUARES).read_text())["servers"]
    assert (server["type"], server["schema"]) == ("databricks", "${SILVER:-shop_data}")


def test_the_tasks_are_there_for_what_was_included(full, landed):
    # Holds TSK-3, CON-4.
    with_dbt = tomllib.loads((full / "mise.toml").read_text())["tasks"]
    without = tomllib.loads((landed / "mise.toml").read_text())["tasks"]
    always = {"lint", "pull", "check", "dlt", "catalog", "edit"}

    assert {t[10:] for t in with_dbt if t.startswith("contracts:")} == always | {"dbt"}
    assert {t[10:] for t in without if t.startswith("contracts:")} == always | {"test"}
    for tasks in (with_dbt, without):
        assert "uv run ops/ports.py lint" in tasks["check"]["run"]
        for name in always:
            assert tasks[f"contracts:{name}"]["run"] == f"uv run ops/ports.py {name}"


def test_ci_compares_the_contracts_with_the_base_branch(full):
    # Holds GEN-4, CON-5.
    workflow = yaml.safe_load((full / ".github/workflows/ci.yml").read_text())
    steps = workflow["jobs"]["check"]["steps"]
    (gate,) = [step for step in steps if "breaking" in step.get("run", "")]

    assert gate["run"] == 'uv run ops/ports.py breaking --base "origin/$GITHUB_BASE_REF"'
    assert gate["if"] == "github.event_name == 'pull_request'"
    assert steps[0]["with"]["fetch-depth"] == 0
    assert "${{" not in (full / ".github/workflows/ci.yml").read_text()


# ── ports.py, run ────────────────────────────────────────────────────────────


def test_lint_passes_on_what_was_written(full, landed):
    # Holds CON-6.
    for project in (full, landed):
        done = ports(project, "lint")

        assert done.returncode == 0, done.stdout + done.stderr
        assert "Data contract is valid" in done.stdout


def test_lint_refuses_an_output_port_whose_contract_is_missing(copy):
    # Holds CON-6.
    (copy / NUMBERS).unlink()

    done = ports(copy, "lint")

    assert done.returncode == 2
    assert f"the output port numbers has no contract: {NUMBERS}" in done.stderr


def test_edit_opens_a_promise_of_this_product_and_nothing_else(copy):
    """The editor itself is a server and a browser; what is tested is what it is given."""
    # Holds CON-8.
    done = ports(copy, "edit", "transactions")

    assert done.returncode == 2
    assert "transactions is not an output port; there are: numbers" in done.stderr


def test_the_loaded_table_keeps_its_contract(landed, tmp_path):
    """The example pipeline into a local DuckDB file, then the contract against it."""
    # Holds CON-7.
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    environment["DLT_DATA_DIR"] = str(tmp_path)
    synced = subprocess.run([uv(), "sync"], cwd=landed, capture_output=True, text=True)
    if synced.returncode != 0:
        pytest.skip(f"the project could not be synced here: {synced.stderr[-400:]}")
    loaded = subprocess.run(
        [uv(), "run", "ingest", "run", "example", "--count", "3"],
        cwd=landed,
        capture_output=True,
        text=True,
        env=environment,
    )
    assert loaded.returncode == 0, loaded.stderr

    done = ports(landed, "test")

    assert done.returncode == 0, done.stdout + done.stderr
    assert "Server: local (type=duckdb" in done.stdout
    assert "Data contract is valid" in done.stdout
    assert "Ran 6 checks" in done.stdout


def test_dbt_gets_its_columns_from_the_contract(full, tmp_path):
    # Holds CON-9.
    project = Path(shutil.copytree(full, tmp_path / "full", ignore=_left_by_runs))
    schema = project / "dbt/models/schema.yml"
    before = schema.read_text()

    dry = ports(project, "dbt", "--dry-run")
    assert dry.returncode == 0, dry.stdout + dry.stderr
    assert "Would sync 1 model" in dry.stdout
    assert schema.read_text() == before

    done = ports(project, "dbt")
    assert done.returncode == 0, done.stdout + done.stderr
    (model,) = yaml.safe_load(schema.read_text())["models"]
    assert [column["name"] for column in model["columns"]] == ["id", "square", "root"]
    assert model["columns"][2]["data_type"] == "DOUBLE"


# ── the producer's gate: no breaking edit to a published version ─────────────


@pytest.fixture
def committed(copy) -> Path:
    """The product as a repository with one commit on `main`, on a branch of its own."""
    for words in (
        ["init", "-q", "-b", "main"],
        ["add", "."],
        ["commit", "-q", "-m", "the first version"],
        ["checkout", "-q", "-b", "change"],
    ):
        subprocess.run([*GIT, *words], cwd=copy, check=True, capture_output=True)
    return copy


def test_a_compatible_edit_passes_the_gate(committed):
    # Holds CON-5.
    edit(committed / NUMBERS, "The number times itself.", "The number, squared.")

    done = ports(committed, "breaking", "--base", "main")

    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NUMBERS}: compatible" in done.stdout


def test_a_breaking_edit_to_v1_is_refused(committed):
    # Holds CON-5.
    edit(committed / NUMBERS, SQUARE, "")

    done = ports(committed, "breaking", "--base", "main")

    assert done.returncode == 2, done.stdout + done.stderr
    assert (
        f"{NUMBERS}: a breaking change needs a new version, v2.odcs.yaml beside it"
        in done.stderr
    )


def test_a_new_version_passes_the_gate(committed):
    # Holds CON-5.
    second = committed / "contracts/output/numbers/v2.odcs.yaml"
    shutil.copy(committed / NUMBERS, second)
    edit(second, "version: 1.0.0", "version: 2.0.0")
    edit(second, SQUARE, "")

    done = ports(committed, "breaking", "--base", "main")

    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NUMBERS}: same" in done.stdout
    assert "contracts/output/numbers/v2.odcs.yaml: new" in done.stdout


def test_a_base_git_does_not_know_is_not_a_pass(committed):
    # Holds CON-5.
    done = ports(committed, "breaking", "--base", "origin/main")

    assert done.returncode == 1
    assert "git does not know origin/main here" in done.stderr


# ── the consumer's gate: is what is read still what was pulled ───────────────


@pytest.fixture
def consumer(copy) -> Path:
    """The product reading `transactions` from a producer in a folder beside it."""
    producer = copy.parent / "payments"
    (producer / "contracts/output/transactions").mkdir(parents=True)
    write(producer / "dataproduct.yaml", PRODUCER)
    write(producer / "contracts/output/transactions/v1.odcs.yaml", PRODUCERS_CONTRACT)
    reads(copy, INPUT_PORT)
    return copy


def write(path: Path, document: dict) -> None:
    path.write_text(yaml.safe_dump(document, sort_keys=False))


def reads(product: Path, port: dict) -> None:
    document = yaml.safe_load((product / "dataproduct.yaml").read_text())
    write(product / "dataproduct.yaml", {**document, "inputPorts": [port]})


def test_pull_keeps_the_producers_contract_as_a_snapshot(consumer):
    # Holds CON-10.
    theirs = consumer.parent / "payments/contracts/output/transactions/v1.odcs.yaml"
    snapshot = consumer / "contracts/input/transactions/v1.odcs.yaml"

    done = ports(consumer, "pull")

    assert done.returncode == 0, done.stdout + done.stderr
    assert snapshot.read_bytes() == theirs.read_bytes()
    assert "contracts/input/transactions/v1.odcs.yaml written" in done.stdout
    assert "unchanged" in ports(consumer, "pull").stdout
    assert ports(consumer, "lint").returncode == 0


def test_check_before_a_pull_says_to_pull(consumer):
    # Holds CON-11.
    done = ports(consumer, "check")

    assert done.returncode == 1
    assert "transactions: no snapshot at contracts/input/transactions/v1.odcs.yaml" in (
        done.stderr
    )
    assert "run `uv run ops/ports.py pull`" in done.stderr


def test_check_is_fine_while_the_producer_keeps_its_promise(consumer):
    # Holds CON-11.
    ports(consumer, "pull")

    done = ports(consumer, "check")

    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.strip() == "transactions: fine"


def test_check_warns_when_the_version_is_deprecated(consumer):
    # Holds CON-11.
    ports(consumer, "pull")
    port = {**PRODUCER["outputPorts"][0], "deprecated": True}
    write(
        consumer.parent / "payments/dataproduct.yaml", {**PRODUCER, "outputPorts": [port]}
    )

    done = ports(consumer, "check")

    assert done.returncode == 0, done.stdout + done.stderr
    assert "warning: the producer marks version 1.0.0 deprecated" in done.stdout
    assert "transactions: fine" in done.stdout


def test_check_refuses_when_the_version_is_gone(consumer):
    # Holds CON-11.
    ports(consumer, "pull")
    port = {**PRODUCER["outputPorts"][0], "version": "2.0.0"}
    write(
        consumer.parent / "payments/dataproduct.yaml", {**PRODUCER, "outputPorts": [port]}
    )

    done = ports(consumer, "check")

    assert done.returncode == 2, done.stdout + done.stderr
    assert "transactions: the producer no longer lists version 1.0.0" in done.stderr


def test_check_refuses_when_the_producer_broke_the_contract(consumer):
    # Holds CON-11.
    ports(consumer, "pull")
    only_id = PRODUCERS_CONTRACT["schema"][0]["properties"][:1]
    schema = {"name": "transactions", "properties": only_id}
    write(
        consumer.parent / "payments/contracts/output/transactions/v1.odcs.yaml",
        {**PRODUCERS_CONTRACT, "schema": [schema]},
    )

    done = ports(consumer, "check")

    assert done.returncode == 2, done.stdout + done.stderr
    assert "no longer keeps what was pulled" in done.stderr
    assert "Removed property amount" in done.stdout


def test_check_warns_when_the_producer_changed_the_contract_compatibly(consumer):
    # Holds CON-11.
    ports(consumer, "pull")
    write(
        consumer.parent / "payments/contracts/output/transactions/v1.odcs.yaml",
        {**PRODUCERS_CONTRACT, "name": "transactions"},
    )

    done = ports(consumer, "check")

    assert done.returncode == 0, done.stdout + done.stderr
    assert "warning: the producer changed the contract" in done.stdout


def test_a_port_without_a_contract_is_refused_with_the_reason(consumer):
    # Holds CON-12.
    reads(consumer, {k: v for k, v in INPUT_PORT.items() if k != "contractId"})

    for verb in ("pull", "check"):
        done = ports(consumer, verb)

        assert done.returncode == 2, verb
        assert "the input port transactions has no contractId" in done.stderr
        assert "there is nothing to fetch or test" in done.stderr


def test_a_port_without_a_version_is_refused_with_the_reason(consumer):
    # Holds CON-12.
    reads(consumer, {k: v for k, v in INPUT_PORT.items() if k != "version"})

    done = ports(consumer, "pull")

    assert done.returncode == 2
    assert "the input port transactions has no version" in done.stderr


def test_pull_refuses_a_file_that_is_another_contract(consumer):
    # Holds CON-10.
    reads(consumer, {**INPUT_PORT, "contractId": "payments.refunds"})

    done = ports(consumer, "pull")

    assert done.returncode == 2
    assert "is not the contract payments.refunds" in done.stderr


# ── a dlt schema from an input contract ──────────────────────────────────────


def produces(consumer: Path, *properties: dict) -> None:
    """The producer's contract, with these properties instead of its own."""
    schema = {"name": "transactions", "properties": list(properties)}
    write(
        consumer.parent / "payments/contracts/output/transactions/v1.odcs.yaml",
        {**PRODUCERS_CONTRACT, "schema": [schema]},
    )


def test_dlt_writes_a_schema_from_the_snapshot(consumer):
    # Holds CON-13.
    produces(
        consumer,
        {"name": "id", "logicalType": "string", "primaryKey": True},
        {"name": "amount", "logicalType": "number"},
        {"name": "count", "logicalType": "integer", "required": True},
        {"name": "paid", "logicalType": "boolean"},
        {"name": "paid_on", "logicalType": "date"},
        {"name": "paid_at", "logicalType": "timestamp"},
        {"name": "at_time", "logicalType": "time"},
        {"name": "buyer", "logicalType": "object"},
        {"name": "tags", "logicalType": "array"},
    )
    ports(consumer, "pull")

    done = ports(consumer, "dlt")

    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.strip() == f"transactions: {SCHEMA} written, from {SNAPSHOT}"
    assert "Not edited by hand" in (consumer / SCHEMA).read_text()
    schema = yaml.safe_load((consumer / SCHEMA).read_text())
    assert schema["name"] == "transactions"
    assert set(schema["tables"]) == {"_dlt_version", "_dlt_loads", "transactions"}
    table = schema["tables"]["transactions"]
    assert table["schema_contract"] == "freeze"
    assert table["columns"]["id"] == {
        "data_type": "text",
        "nullable": False,
        "primary_key": True,
    }
    assert table["columns"]["count"] == {"data_type": "bigint", "nullable": False}
    assert {name: column["data_type"] for name, column in table["columns"].items()} == {
        "id": "text",
        "amount": "double",
        "count": "bigint",
        "paid": "bool",
        "paid_on": "date",
        "paid_at": "timestamp",
        "at_time": "time",
        "buyer": "json",
        "tags": "json",
    }
    assert f"{SCHEMA} unchanged" in ports(consumer, "dlt").stdout


def test_dlt_before_a_pull_says_to_pull(consumer):
    # Holds CON-13.
    done = ports(consumer, "dlt")

    assert done.returncode == 1
    assert f"no snapshot at {SNAPSHOT}: run `uv run ops/ports.py pull`" in done.stderr


@pytest.mark.parametrize(
    ("column", "sentence"),
    [
        (
            {"name": "rate", "logicalType": "decimal"},
            "transactions.rate: dlt has no type for the logicalType decimal",
        ),
        (
            {"name": "rate"},
            "transactions.rate: dlt has no type for the logicalType None",
        ),
        (
            {"name": "paidAt", "logicalType": "timestamp"},
            "transactions.paidAt: dlt would load the name paidAt as another",
        ),
    ],
)
def test_dlt_refuses_what_it_cannot_say_in_a_schema(consumer, column, sentence):
    # Holds CON-14.
    produces(consumer, {"name": "id", "logicalType": "string"}, column)
    ports(consumer, "pull")

    done = ports(consumer, "dlt")

    assert done.returncode == 2, done.stdout + done.stderr
    assert f"{SNAPSHOT}: {sentence}" in done.stderr
    assert not (consumer / SCHEMA).exists()


def test_a_pipeline_refuses_what_the_contract_does_not_have(consumer, tmp_path):
    """Pulled, written as a schema, and kept by dlt on a load into a local DuckDB file."""
    # Holds CON-15.
    assert (
        "import_schema_path=SCHEMAS)"
        in (consumer / "contracts/input/README.md").read_text()
    )
    assert ports(consumer, "pull").returncode == 0
    assert ports(consumer, "dlt").returncode == 0
    (consumer / "src/landed/pipelines/payments.py").write_text(PIPELINE)
    environment = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    synced = subprocess.run([uv(), "sync"], cwd=consumer, capture_output=True, text=True)
    if synced.returncode != 0:
        pytest.skip(f"the project could not be synced here: {synced.stderr[-400:]}")

    def load(rows: str, state: str) -> subprocess.CompletedProcess:
        # A state folder for each run: dlt tries a refused load again on the next run.
        return subprocess.run(
            [uv(), "run", "ingest", "run", "payments", "--rows", rows],
            cwd=consumer,
            capture_output=True,
            text=True,
            env={**environment, "DLT_DATA_DIR": str(tmp_path / state)},
        )

    def loaded() -> str:
        query = "select id, amount from transactions_dataset.transactions order by id"
        file = "duckdb.connect('transactions.duckdb')"
        script = f"import duckdb; print({file}.sql({query!r}).fetchall())"
        said = subprocess.run(
            [uv(), "run", "python", "-c", script],
            cwd=consumer,
            capture_output=True,
            text=True,
            env=environment,
        )
        return said.stdout.strip()

    kept = load('[{"id": "a", "amount": 1.5}, {"id": "b", "amount": 2}]', "kept")
    assert kept.returncode == 0, kept.stdout + kept.stderr
    assert loaded() == "[('a', 1.5), ('b', 2.0)]"

    more = load('[{"id": "c", "amount": 3.0, "note": "not in the contract"}]', "more")
    assert more.returncode != 0
    assert (
        "Can't add table column `note` to table `transactions` because `columns` are"
        " frozen" in more.stdout + more.stderr
    )

    other = load('[{"id": "d", "amount": "a lot"}]', "other")
    assert other.returncode != 0
    assert "because `data_types` are frozen" in other.stdout + other.stderr

    empty = load('[{"id": null, "amount": 1.0}]', "empty")
    assert empty.returncode != 0
    assert "column `id` which is not nullable" in empty.stdout + empty.stderr

    assert loaded() == "[('a', 1.5), ('b', 2.0)]"
    # dlt wrote no schema of its own: the pipeline's name was the port's.
    assert [p.name for p in (consumer / SCHEMA).parent.iterdir()] == [Path(SCHEMA).name]
