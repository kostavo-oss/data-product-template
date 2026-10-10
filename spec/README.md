# spec

What the data product template has to do, and how we know that it does.

Written and built on 2026-10-07, after the owner decided that starting a data product is a
bundle template's job and not a library command's, and asked for dlt and dbt together,
with lely and caland around it and mise tasks in front: "a showcase / really useful place
to start".

## Words

- The **template** is this repository: a Databricks Asset Bundle template.
- A **product** is what `databricks bundle init` writes from it: one data product, a bundle.
- The **halves** are dlt (lands the data, run by leeghwater) and dbt (shapes it).
- A **tool** is one of lely, caland, leeghwater: each optional except leeghwater, which
  the dlt half is written for.

## Decided

**By the owner, 2026-10-07:**

- A bundle template, not `leeghwater init`: "init can leave".
- dlt and dbt together: "an dab for dlt and dbt i think that is a nice combination".
- Also lely and caland, not stevin, with mise tasks: "maybe the template should also host
  lely but without steven but with caland with some nice mise tasks".
- The name is the writer's to propose; `vierlingh` was proposed and confirmed on 2026-10-08; renamed `data-product-template` on 2026-10-10 so the copier URL says what it is (the namesake stays in the README)
  ("Vierling is fine").

**By the writer, on the owner's "get started":**

- Every tool is optional and the product works without it: `databricks bundle deploy`
  without lely, `databricks secrets` without caland. A prompt per tool.
- The halves meet in three places and nowhere else: the schemas (bundle resources, names
  by reference), the job (`ingest` then `transform`), and the laptop tasks (the deployed
  names read back from the bundle). No shared code.
- dbt stays dbt and dlt stays dlt: each in its own folder with its own files, nothing
  wrapped.
- The laptop loop for dbt goes through a workspace (`--profile`); a local loop on DuckDB
  is not offered, because models written in Databricks SQL would not all run there.

## Copier, not `databricks bundle init`

Asked on 2026-10-07 whether copier would not be better than a bundle template, the writer
compared the two by building both; this is the second. The first is in the repository's
history (the first commit) and was what ran on the workspace.

| | `databricks bundle init` | copier |
|---|---|---|
| A product's updates | none: generated once, then on its own | `copier update` brings the wiring's next change; `_skip_if_exists` keeps the product's own files |
| Discoverability | the Databricks way; registrable in a workspace's UI | `uvx copier copy gh:kostavo-oss/data-product-template`; nothing in the workspace |
| What is rendered | every `.tmpl`, with Go's text/template: no loops to speak of, `missingkey=error`, and `{{ }}` that clashes with dbt's Jinja, GitHub's `${{ }}` and mise's own | only `.jinja` files, with Jinja: the clash is gone, conditional file names replace `{{ skip }}` |
| Generating | needs credentials configured, though nothing here asks the workspace; the Databricks CLI on the machine | Python only; tests run copier in-process |
| In the org | nothing else uses it | what every Kostavo tool is made from (`template-python`); one way of doing things |

The deciding line is the first: a template whose products cannot take its next change is
a one-time gift, and the wiring will change. The cost is the second line, paid with one
command in the README. *(the writer's evaluation; the owner agreed on 2026-10-08: "Copier is
fine")*

## Requirements

- **R1 — A product is one `copier copy` away, with or without a terminal, and takes the
  template's next change with `copier update`.** The questions are a name, a catalog, a
  warehouse, a secret scope, and yes/no for dbt, lely, caland and contracts; `--data` answers them
  without a terminal, and `.copier-answers.yml` in the product remembers them. What a
  product owns — its pipelines, models, README, dlt config — is never touched by an update.
- **R2 — The schemas are the bundle's.** `raw` and `raw_staging` always; `silver` with dbt.
  The job gets their deployed names by reference, so a target may prefix them and nothing
  in the code knows them.
- **R3 — One job, two tasks, in order.** `ingest`, a wheel task running the product's own
  `ingest run example` with the schemas, catalog, warehouse and scope as its words;
  `transform`, a dbt task after it, made by Databricks from `warehouse_id`, `catalog` and
  `schema` with no `profiles.yml` in the job, running `dbt build` with `raw_schema` as a
  variable.
- **R4 — dbt reads raw through `source('raw', ...)`** and the `raw_schema` variable, never
  a schema name. `dbt parse` runs with no workspace, against a `parse` target.
- **R5 — The same product runs from a laptop,** in three ways: `mise run dev` into a local
  DuckDB file with no workspace; `mise run ingest -- <pipeline>` into the dev target's
  deployed schemas, read back from `bundle summary`; `mise run transform`, dbt against the
  same schemas, signed in through the Databricks SDK with the same profile.
- **R6 — mise fronts everything.** `[tools]` brings python, uv, the Databricks CLI, and
  lely and caland when included; the tasks are `dev`, `check`, `fix`, `clean`, `deploy`,
  `job`, `doctor`, `ingest`, `transform` (dbt), `plan`/`apply`/`destroy` (lely), `secrets`
  (caland). A developer's own profile, warehouse and catalog live in `mise.local.toml`,
  not committed. `.mcp.json` gives a coding agent mise's MCP server.
- **R7 — lely, when included:** `lely.yml` with the bundle as its one step; GitHub
  workflows that plan on a pull request and apply the reviewed plan on merge, from lely's
  own guide.
- **R8 — caland, when included:** a `secrets` task that opens caland on the bundle's
  workspace, and the README pointing there beside the CLI command.
- **R9 — A rules page for agents, each rule with its reason** (`AGENTS.md`): make the
  pipeline with leeghwater, never a schema name in code, secrets through
  `dlt.secrets.value`, dbt through `source()`, run things through mise, read a run's first
  lines.
- **R10 — Nothing the template writes is read only.** The repository's tests generate the
  full and the bare answers, check what is and isn't there, lint the Python, parse every
  YAML, parse the dbt project, run the example into DuckDB, and look for template syntax
  that survived. Only `.jinja` files are rendered; dbt's models, GitHub's workflows that
  use `${{ }}` and mise's local file are copied as they are, because their own syntaxes
  would clash.
- **R12 — The secret scope is a step of the product's own.** When a scope is named,
  `ops/scope.py` is a lely step (`lely.step.Step`, lely 0.3) that makes it: the first step
  of `lely.yml`, feeding the bundle `${steps.scope.name}`; the job reads it as
  `${var.secret_scope}`; and on its own, `uv run ops/scope.py plan|apply|check -t dev
  --name <scope>` with no lely config. `mise run scope` runs it. A fresh target brings its
  scope with it, and the name is typed once. *(decided; run on the owner's test workspace on 2026-10-08, alone and
  under lely with the bundle)*
- **R11 — The product carries no trace of any team, platform or customer.**

## Tried on a workspace

On 2026-10-07, the full answers, on the owner's test workspace, from a laptop with a
profile. Everything made was removed afterwards.

| What | Held? |
|---|---|
| Generating the full and the bare answers (then with `bundle init` and dummy credentials; now with copier, in-process) | yes |
| The product's `check`: ruff, `ingest list`, `dbt parse` | yes |
| `mise run dev`'s command: the example into a local DuckDB file | yes |
| `bundle validate` and `bundle deploy` of the dev target: three schemas and the job, prefixed `dev_<user>_` | yes |
| `ops/names.py` reads the deployed names back from `bundle summary` | yes |
| The laptop ingest into the deployed raw schema | yes |
| dbt from the laptop against the deployed schemas, signed in through the SDK: model built, two tests pass | yes |
| The job's `transform` task on serverless, with the dbt task made from `warehouse_id`/`catalog`/`schema`: `squares` built from raw | yes — with the local leeghwater wheel added to the job's environment; leeghwater was not yet on PyPI (it is since 0.1.0, 2026-10-08) |
| lely `validate`, `plan` and `status` on the product | yes |
| `bundle destroy` | yes |
| The scope step (`ops/scope.py`) generated and run on its own, and under lely with the bundle | yes (2026-10-08, lely 0.3.0): `plan`, `apply` made the scope, `status` listed it, `lely plan -t dev` wired `secret_scope = … ← scope.name` into the bundle, `destroy` removed it |
| The job's `ingest` task | **not run**: it needs leeghwater from PyPI, and this workspace's serverless compute refuses dlt's upload to storage (known from leeghwater's own run) |
| `mise install` and the tasks through mise itself | **not run**: the task commands were run by hand; mise would also have installed tools on this machine |
| caland from the `secrets` task | **not run**: it opens a page in a browser |
| The GitHub workflows | **not run**: the product was not a repository on GitHub |

**Found and fixed while trying:** YAML reads `dbt build --vars '{raw_schema: …}'` as a
mapping unless the command is quoted whole; dbt-databricks wants the host without its
scheme; a `{{ config(...) }}` inside a SQL comment is read by dbt and set the model to a
view; `databricks auth env` is deprecated and prints a warning first, so the dbt sign-in
goes through the SDK instead; `databricks auth token` only serves OAuth profiles.

## Contracts between products

Added on 2026-10-10. The owner described the need on 2026-10-09: data mesh has its
standards and Databricks has no tooling for them, a product should say what it promises,
and a product that reads another should be able to do something useful with that promise.
A package of its own was specified first and then dropped. What is here instead is files,
tasks, a CI gate and one script.

### No package

The Data Contract CLI ([datacontract-cli](https://github.com/datacontract/datacontract-cli),
MIT) already does what the package would have done. From its
[changelog](https://raw.githubusercontent.com/datacontract/datacontract-cli/main/CHANGELOG.md):

- 1.1.2 (2026-08-26): the server type `duckdb`, to test the tables inside a DuckDB file;
  `dbt sync --dry-run`.
- 1.1.3 (2026-09-03): the `breaking` command.
- 1.2.0 (2026-09-08): ODCS v3.2.0; `${VAR}` and `${VAR:-default}` in server fields,
  filled from the environment.
- 1.2.4 (2026-10-06): the version the template names.

`lint`, `test`, `breaking`, `catalog` and `dbt sync` are its commands. What it does not
know is where a product keeps its files and which contract belongs to which port. That is
`ops/ports.py`, 276 lines with PyYAML as its one dependency, and it is the product's own
file once written.

### Decided

**Given to the writer as decided, 2026-10-10:**

- No contracts package. The template ships files, tasks, a CI gate and one small script.
- A question, `include_contracts`, on by default.
- The standards are Bitol's: ODPS v1.1.0 for the product file, ODCS v3.2.0 for a contract.
- The CLI is run as a pinned command (`uvx --from 'datacontract-cli[…]==…'`), not
  installed beside the product. The pin and the extras stand in one constant.
- A breaking change to an output contract is a new version and never an edit, and CI
  holds that line.
- A consumer keeps a snapshot of the producer's contract and checks against it: 0 fine,
  1 could not run, 2 refused.

**By the writer, while building:**

- **The layout.** `dataproduct.yaml` at the root; `contracts/output/<port>/v<N>.odcs.yaml`
  for a promise; `contracts/input/<port>/v<N>.odcs.yaml` for a snapshot. `N` is the major
  number of the port's `version`. A version is a file, not a folder: a port has one
  contract for each version and nothing else to keep beside it.
- **Ids are readable**: the product's `id` is its name, a contract's is `<product>.<port>`.
  ODPS suggests a UUID and requires only a string.
- **Which table the example contract describes.** With dbt, the model `squares`; without,
  the table `numbers` the example pipeline loads. Both were read from the template.
- **A dbt product's contract has one server, and no `contracts:test` task.** The owner's
  design gave every contract a `duckdb` server for the file a developer's run writes. A
  developer's run writes `numbers` only: the model is built on the workspace, because a
  local dbt loop on DuckDB is not offered (see Decided, above). A `duckdb` server for
  `squares` would name a table that is never there. So the contract of `squares` names
  the deployed table only, and the task that tests locally exists only without dbt. This
  is the one place where the design did not survive, and it leaves the default answers
  without a local test of the contract.
- **Names that differ per target are variables with a default**:
  `catalog: ${CATALOG:-main}`, `schema: ${SILVER:-<package>}` (or `${RAW:-<package>_raw}`).
  The CLI fills them from the environment. The defaults are the prod target's names;
  `CATALOG` is what `mise.local.toml` already sets, and `RAW` and `SILVER` are what
  `ops/names.py` already prints for a deployed target. Nothing new had to be invented.
- **Where an input port says its contract's address.** ODPS v1.1.0 gives a port
  `authoritativeDefinitions`, a list of `type` and `url`, and `type` is free text. The
  template uses it: `type: dataContract` is the producer's contract, `type: dataProduct`
  the producer's product file. `customProperties` was the fallback and was not needed.
  The address is a URL or a path from the product's folder. A path is not a URI in the
  strict sense: the schema marks `url` as `format: uri`, and a validator that enforces
  formats refuses a path. Validators do not enforce formats unless asked.
- **A port without `contractId` or `version` is refused**, with the reason. ODPS v1.1.0
  allows both to be left out; such a port names nothing to fetch and gives its snapshot
  no name.
- **What `breaking` exits with decides how the script reads it.** It exits 0 for no
  change and for a compatible one, and 1 for a breaking one. It also exits 1 for a file
  it cannot read. The script tells the two apart by the word `Details`, which the CLI
  prints above its table only when a comparison was made.
- **The script fetches, the CLI compares.** `pull`, `check` and `breaking` read both
  sides themselves (a URL, a path, `git show`) and hand the CLI two local files. One way
  of fetching, and equal bytes need no CLI at all.
- **`check` asks about the port's life first, then compares.** The design had it the
  other way round. A producer that withdraws a version usually removes its contract file
  too, and then "the producer no longer lists version 1.0.0" says more than "not found".
- **`lint` and `test` hand on the CLI's exit code**, which is 1 for a contract that
  fails and 1 for a server that cannot be reached. Only `check` and `breaking` use 2.
- **The CI gate needs no `${{ }}`.** The workflow reads the base branch from
  `GITHUB_BASE_REF`, which the runner sets, and checks out with `fetch-depth: 0` so that
  `origin/<base>` is there. `ci.yml` is now rendered, since the step is conditional.
- **`_skip_if_exists` names `dataproduct.yaml` and `contracts/**`, and not
  `ops/ports.py`.** The product file and the contracts are the product's own. The script
  is wiring, like the tasks and the workflows: `copier update` brings a newer pin of the
  CLI and a fix to a verb. A product that changed the script settles the difference
  then, as with any wiring.
- **Removing a version file is not judged.** The gate looks at files that exist. Taking a
  version away is the producer's last step after marking it deprecated, and whether it is
  time is not something a comparison can say.

### Requirements

- **R13 — A product says what it promises, and the promise is held.** With
  `include_contracts`: `dataproduct.yaml` (ODPS v1.1.0) lists the ports; every output port
  has a contract (ODCS v3.2.0) for the table the example really makes; `mise run check`
  lints the contracts; CI refuses a breaking edit to an existing version file and passes
  a new one; `ops/ports.py` has `lint`, `test`, `pull`, `check`, `breaking`, `catalog`
  and `dbt`, each behind a `contracts:*` task except `breaking` (CI's) and, with dbt,
  `test`. Without `include_contracts` none of it is written and nothing mentions it.

### Run

On 2026-10-10, on a laptop, with `datacontract-cli[duckdb,databricks]==1.2.4` through
`uvx`. No workspace. Each line is a command and what it printed last.

| What | Printed |
|---|---|
| `datacontract breaking` on a changed description, an added column, a `deprecated: true`, a changed server | `INFO` rows; exit 0 |
| `datacontract breaking` on a removed column, a changed type, an added `required: true` | `ERROR` rows; exit 1 |
| `datacontract breaking` with a file that is not there | `Error: The file '…' does not exist.`; exit 1 |
| `datacontract breaking` on the same file twice | `No changes.`; exit 0 |
| `ports.py lint`, with dbt and without | `Data contract is valid. Ran 1 checks.`; exit 0 |
| `ports.py test` after the example ran into DuckDB (without dbt) | `Data contract is valid. Ran 6 checks.`; exit 0 |
| `ports.py test` before the example ran | `Could not open the duckdb database at example.duckdb`; exit 1 |
| `ports.py test` with a column's type changed in the contract | `expected type 'string' but got 'integer'`; exit 1 |
| `ports.py test` with dbt (no `local` server) | `Server 'local' not found in data contract. Available servers: databricks`; exit 1 |
| a server's `schema: ${LOCAL_SCHEMA:-example_dataset}`, variable unset | `Ran 6 checks.`; exit 0: the default is used |
| the same with `LOCAL_SCHEMA=nowhere` | `No catalog + schema named "nowhere" found.`; exit 1: the environment wins |
| `datacontract test --server databricks` with no credentials | `Required configuration DATACONTRACT_DATABRICKS_SERVER_HOSTNAME is not set.`; exit 1 |
| `ports.py dbt --dry-run` on the generated dbt project | `Would sync 1 model: updated 1 YAML file.`; `schema.yml` unchanged |
| `ports.py dbt`, then `dbt parse` (dbt 1.12.5) | `Synced 1 model: updated 1 YAML file.`; parse exit 0; a second sync `updated 0 YAML files` |
| `ports.py catalog` | `Created site/contracts/index.html`; exit 0 |
| `ports.py breaking --base main`: untouched, a changed description | `…/v1.odcs.yaml: same`, `…: compatible`; exit 0 |
| the same after removing a column from `v1` | `a breaking change needs a new version, v2.odcs.yaml beside it`; exit 2 |
| the same with the column removed in a new `v2` instead | `…/v2.odcs.yaml: new`; exit 0 |
| `ports.py breaking --base "origin/$GITHUB_BASE_REF"`, as the workflow calls it, in a local repository | `…/v1.odcs.yaml: same`; exit 0 |
| `ports.py pull` from a producer in a folder beside, and over HTTP | `contracts/input/numbers/v1.odcs.yaml written, from http://127.0.0.1:…`; exit 0 |
| `ports.py check`: kept, deprecated, withdrawn, broken | `fine`; `warning: the producer marks version 1.0.0 deprecated`; `the producer no longer lists version 1.0.0` (exit 2); `no longer keeps what was pulled` (exit 2) |
| `ports.py check --server local`, a consumer testing the producer's DuckDB file | `Ran 6 checks.` then `numbers: fine`; exit 0 |
| `ports.py check` with the producer unreachable | `could not be read: <urlopen error [Errno 61] Connection refused>`; exit 1 |
| `ports.py pull` and `check` on a port without `contractId` | `the input port transactions has no contractId: there is nothing to fetch or test`; exit 2 |
| both generated `dataproduct.yaml` files, and the commented example port, against the ODPS v1.1.0 JSON schema | valid |
| every command of the product's `check` task, with dbt and without | exit 0 each |

`tests/test_contracts.py` runs most of this again on every change.

### Not yet

- **The contracts in the job**: `check` as the job's first task, `test` as its last, the
  results appended to a table. It needs a run on a workspace. The CLI can test inside a
  job on the cluster's own Spark session
  ([docs](https://docs.datacontract.com/testing/databricks.md)); how that sits beside dlt
  and dbt in a serverless environment is not known.
  [#10](https://github.com/kostavo-oss/data-product-template/issues/10)
- **A test against the `databricks` server**, from a laptop or anywhere. The server
  entries are linted and their variables were seen to resolve on a DuckDB server; no test
  has reached a workspace. The `physicalType` of each column (`bigint`, `double`) is what
  Databricks is expected to report and has not been compared there. Part of #10.
- **A dlt import schema from an input contract**, so that a pipeline refuses what the
  contract does not have. The CLI's `export custom` takes a template; whether a dlt
  import schema can carry `schema_contract: freeze` is not verified.
  [#11](https://github.com/kostavo-oss/data-product-template/issues/11)
- **The CI gate on GitHub.** The command the workflow runs was run in a local repository.
  The workflow itself has not run: no product is a repository on GitHub yet (Still open,
  2).
- **The `contracts:*` tasks through mise itself.** As with every other task, the commands
  were run by hand (Tried on a workspace, `mise install`).
- **A local test for a product with dbt.** It would take the model in DuckDB, which is
  the local dbt loop that was decided against.
- **A contract kept in a private repository.** `pull` and `check` fetch a URL without
  credentials. A path to a checkout beside the product works today.

## Still open

1. **The job's `ingest` task, end to end,** on a workspace whose serverless compute can
   reach its storage.
2. **A product as a GitHub repository,** to see the plan and apply workflows run.
3. **`mise install` on a clean machine,** to see the tools arrive as listed.
4. **A release**, after the above, on the owner's word.
