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
  warehouse, a secret scope, and yes/no for dbt, stevin, lely, caland and contracts; `--data` answers them
  without a terminal, and `.copier-answers.yml` in the product remembers them. What a
  product owns — its pipelines, models, README, dlt config — is never touched by an update.
- **R2 — The schemas are the bundle's.** `raw` and `raw_staging` always; `silver` with dbt
  or with stevin.
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
| `mise install` and the tasks through mise itself | **not run** that day: the task commands were run by hand; mise would also have installed tools on this machine. `mise install`, `check` and `dev` held on a GitHub runner on 2026-10-10 (below) |
| caland from the `secrets` task | **not run**: it opens a page in a browser |
| The GitHub workflows | **not run** that day: the product was not a repository on GitHub. They held on 2026-10-10 (below) |

**Found and fixed while trying:** YAML reads `dbt build --vars '{raw_schema: …}'` as a
mapping unless the command is quoted whole; dbt-databricks wants the host without its
scheme; a `{{ config(...) }}` inside a SQL comment is read by dbt and set the model to a
view; `databricks auth env` is deprecated and prints a warning first, so the dbt sign-in
goes through the SDK instead; `databricks auth token` only serves OAuth profiles.

### On GitHub, from a repository

On 2026-10-10, one run, on one private repository made from the template at commit
`95da290` with `uvx copier copy --defaults`: the catalog `workspace`, a warehouse id, with
dbt, lely, caland and contracts. Nothing was edited by hand; `uv lock` added the lock
file. The repository had `DATABRICKS_HOST` and `WAREHOUSE_ID` as variables and
`DATABRICKS_TOKEN` as a secret, for the test workspace. Everything made was removed
afterwards.

| What | Held? |
|---|---|
| `ci` on the first push to `main`, on a clean GitHub runner: `jdx/mise-action` installed the tools as listed, then `uv sync --locked`, `mise run check` (with the contracts lint) and `mise run dev` (the example into a local DuckDB file) | yes |
| `apply` on the first push to `main` | failed, as designed, at "Fetch the plan that was reviewed": `This commit came from no pull request: no plan was reviewed.` It is a red cross on a new product's first day; the product's README now says so |
| `plan` on a pull request: `lely plan -t dev -o plan.json --github` (lely 0.3.0), the plan posted as a comment on the pull request | yes: `4 changes · 1 run · 0 destructive`: create `jobs.data_product_proof`, `schemas.raw`, `schemas.raw_staging`, `schemas.silver`, and the upload of the bundle's files. `ci` passed on the same pull request |
| `apply` on the merge (squash): it found the pull request of the merge commit, downloaded the plan artifact made for its last commit, and ran `lely apply plan.json --yes --github -o result.json` | yes: the dev target was deployed to the test workspace from the reviewed plan, not from a new one |
| The CI gate on a second pull request that removed the column `root` from `contracts/output/squares/v1.odcs.yaml` | yes: `ci` failed at "No breaking change to a published contract" with exit code 2 and `contracts/output/squares/v1.odcs.yaml: a breaking change needs a new version, v2.odcs.yaml beside it: a published version is not edited.`, under the Data Contract CLI's table naming `schema.squares.properties.root` as removed. Closed without merging |
| Taking the target down, from a hand-started workflow that is the repository's own and not part of the template: `lely plan -t dev --destroy -o destroy.json`, then `lely destroy destroy.json -t dev --yes` | yes: `4 changes · 0 runs · 4 destructive`, the job and the three schemas deleted. Nothing was left on the workspace |
| The job itself (`mise run job`) | **not run**: its `ingest` task still cannot finish on the test workspace, whose serverless compute is refused the connection to the storage endpoint dlt uploads to |
| caland from the `secrets` task | **not run** |
| The `prod` target | **not run** |

**Found and fixed in this run:** the product's `.gitignore` did not ignore `.env`. The
Data Contract CLI loads a `.env` file, walking up the directories, and a developer puts a
token there. In the repository that file showed as untracked, one careless `git add` from
being published. `.env` and `.env.*` are now ignored.

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
`ops/ports.py`, 467 lines with PyYAML as its one dependency, and it is the product's own
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
  a new one; `ops/ports.py` has `lint`, `test`, `pull`, `check`, `breaking`, `catalog`,
  `edit`, `dbt` and `dlt`, each behind a `contracts:*` task except `breaking` (CI's) and, with
  dbt, `test`. `edit` opens an output contract in the Data Contract Editor, which the
  CLI serves from its own package on this machine; the template builds no editor. `dlt` writes a dlt schema from every input snapshot, with every table frozen (below). Without `include_contracts` none of it is written and nothing mentions it.

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
| `datacontract edit` with the extras the other verbs use | `Install the extra datacontract-cli[api] to use edit.` |
| `ports.py edit` (it adds the `api` extra) | `Data Contract Editor running at http://localhost:4243`; the page answers within seconds, its files from `/editor/` on the same address; Ctrl+C stops it |
| `ports.py edit transactions`, not an output port | `transactions is not an output port; there are: numbers`; exit 2 |
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

### A dlt schema from an input contract

Added on 2026-10-10, for
[#11](https://github.com/kostavo-oss/data-product-template/issues/11). Two things had not
been run. Both were, with dlt 1.31.0 and leeghwater 0.1.0, into a local DuckDB file.

**Can a schema file carry the freeze? Yes, on a table.** A pipeline made with
`import_schema_path` reads `<schema name>.schema.yaml` from that folder. Three places
for the contract were tried, each with a row that has one column too many:

| Where `freeze` stood | What dlt did |
|---|---|
| in the file, under `settings: schema_contract` | loaded the row and added the column: the file's settings are not kept |
| in the file, on the table: `schema_contract: freeze` | `Contract on columns with contract_mode=freeze is violated. Can't add table column note to table transactions because columns are frozen.` |
| on the run: `run(..., schema_contract="freeze")`, nothing in the file | the same refusal, and also `Can't add table other because tables are frozen` for a table the file does not have |

So the file carries it, table by table, and a pipeline needs one argument and no line on
its run.

**Can `export custom` write the file? It gets enough, and it is not used.**
`datacontract export custom <contract> --template <file>` hands the template
`data_contract`, with `schema_`, and on every property `name`, `logicalType`,
`physicalType`, `required` and `primaryKey`. A template that maps the types printed
`data_type: ` and nothing after it for a property without a type, and exited 0: a
template cannot refuse. The script would have to read the result back to find that. It
reads the contract itself instead, with the PyYAML it already has: one table of types,
one loop, and a refusal where the type is looked up. That is less than a template, a
call and a second reading.

**Decided by the writer:**

- **A verb of its own, `dlt`, behind `contracts:dlt`.** It reads the snapshots and
  fetches nothing, as `dbt` reads the output contracts. `pull` stays the one verb that
  asks the producer.
- **The file is `src/<package>/schemas/<port>.schema.yaml`.** It is inside the package,
  because a job runs the wheel and its working directory is not the product's folder. A
  pipeline names the folder from its own file:
  `SCHEMAS = Path(__file__).parent.parent / "schemas"`, then
  `leeghwater.create_pipeline("<port>", import_schema_path=SCHEMAS)`. leeghwater hands
  the argument to `dlt.pipeline` as it is. The file says in its first lines that it is
  written by the verb and not edited by hand.
- **The schema is named after the port.** dlt looks for the file by the schema's name,
  which is the pipeline's name, or the name of a `@dlt.source`. With another name dlt
  finds nothing, loads every row and writes `<name>.schema.yaml` of its own beside it.
  `schema_contract="freeze"` on the run turns that into a refusal, and the product's
  page on input ports says so.
- **dlt's own two tables are in the file, as dlt 1.31.0 writes them.** Without them dlt
  says `Schema must contain table _dlt_version`; without `previous_hashes` it fails on
  that key. The file says `engine_version: 11`, which dlt 1.30.0 also has, and a later
  dlt moves an older file forward itself. `settings` and `normalizers` are left out:
  dlt fills them in, and the schema dlt keeps after a load has both.
- **The types**: `string` text, `integer` bigint, `number` double, `boolean` bool,
  `date`, `timestamp` and `time` the same, `object` and `array` json. A `number` has no
  scale in ODCS. Any other `logicalType`, or none, is refused with the snapshot, the
  object and the property.
- **`nullable` is false for `required` and for `primaryKey`**, and `primary_key` is true
  for `primaryKey`.
- **A name dlt would change is refused.** dlt loads `paidAt` as `paid_at`. A schema with
  `paidAt` would freeze a column that never arrives, and refuse the one that does. The
  script has no dlt to ask for the other name, so it accepts only names dlt keeps: small
  letters, digits, single underscores, none at the end.

**Run**, each a command and what it printed last. `ingest run` is the product's own
command, with a pipeline that loads the rows it is given.

| What | Printed |
|---|---|
| a schema file with the contract's table only | `'previous_hashes'`, then with that key `Schema must contain table _dlt_version` |
| `datacontract export custom c.odcs.yaml --template dump.jinja` | every property with its `logicalType`, `required` and `primaryKey`; exit 0 |
| the same with a template that maps the types, on a property without one | `data_type: ` with nothing after it; exit 0 |
| `datacontract export c.odcs.yaml --format custom` | `--format needs to be omitted since v0.12.0`; exit 2 |
| `ports.py dlt` before a pull | `no snapshot at contracts/input/transactions/v1.odcs.yaml: run uv run ops/ports.py pull`; exit 1 |
| `ports.py dlt` after a pull, and again | `transactions: src/landed/schemas/transactions.schema.yaml written, from contracts/input/transactions/v1.odcs.yaml`; then `unchanged`; exit 0 |
| `ports.py dlt` with `logicalType: decimal`, and with none | `…: transactions.rate: dlt has no type for the logicalType decimal`; exit 2 |
| `ports.py dlt` with a property `paidAt` | `…: transactions.paidAt: dlt would load the name paidAt as another: …`; exit 2 |
| `ingest run` with a row of all nine types | exit 0; DuckDB has `VARCHAR`, `DOUBLE`, `BIGINT`, `BOOLEAN`, `DATE`, `TIMESTAMP WITH TIME ZONE`, `TIME`, `JSON`, `JSON`, and `NO` under null for the required column and the key |
| a row with a column `note` | `Can't add table column note to table transactions because columns are frozen`; exit 1 |
| a text in a `number`, a fraction in an `integer`, `yesterday` in a `date` | `Can't add variant column amount__v_text for table transactions because data_types are frozen`; exit 1 each |
| `null` in a required column | `Cannot coerce NULL in table transactions column count which is not nullable`; exit 1 |
| a row without the required column | DuckDB's `NOT NULL constraint failed: transactions.count`; exit 1 |
| an object the contract does not have, and a list | `Can't add table column extra__a …`; `Can't add table transactions__items because tables are frozen`; exit 1 |
| a pipeline with another name | exit 0, the row with `note` loaded, and `other.schema.yaml` written beside the schema |
| the same with `schema_contract="freeze"` on the run | `Can't add table transactions because tables are frozen`; exit 1 |
| the port's name and `schema_contract="freeze"` on the run | rows that keep the contract: exit 0; the row with `note`: exit 1 |
| a pipeline named otherwise running `@dlt.source(name="transactions")` | rows that keep the contract: exit 0; the row with `note`: exit 1 |
| rows that keep the contract, after a refused run with the same state | `Pending packages are left in the pipeline and will be re-tried on the next pipeline run`; exit 1 |
| `dlt pipeline transactions abort-packages` from a script | `Proceed? [y/N]:` and nothing dropped; `dlt.attach("transactions").abort_packages()` dropped them, and the next run exited 0 |
| `uv build --wheel`, then `unzip -l` | `landed/schemas/transactions.schema.yaml` is in the wheel |
| the wheel installed in another folder: `ingest run` there | rows that keep the contract: exit 0; the row with `note`: `columns are frozen`, exit 1 |

`tests/test_contracts.py` pulls from a producer in a folder beside, writes the schema,
loads rows that keep it, and sees dlt refuse a column the contract does not have, a text
in a number and an empty key. It also runs the three refusals of the verb.

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
- **Of the dlt schema** (the section above): a load into Databricks with it, and the
  job's `ingest` task reading it from the wheel. `physicalType` is not read, so a
  `number` is a double whatever its precision. A name dlt would change is refused, not
  written under dlt's name. The properties inside an `object` and the items of an `array`
  are one `json` column and are not held. Nothing says that a schema file is older than
  its snapshot: `pull` does not write it. `dlt pipeline <name> abort-packages` was not
  answered from a script.
- **The CI gate on GitHub, for more than one case.** It refused a removed column on a
  pull request on 2026-10-10 (Tried on a workspace, On GitHub). A new version file and a
  compatible edit were seen to pass in a local repository only.
- **The `contracts:*` tasks through mise itself.** The lint ran through mise as part of
  `mise run check`, on a GitHub runner on 2026-10-10. The other tasks' commands were run
  by hand.
- **A local test for a product with dbt.** It would take the model in DuckDB, which is
  the local dbt loop that was decided against.
- **A contract kept in a private repository.** `pull` and `check` fetch a URL without
  credentials. A path to a checkout beside the product works today.

## stevin in a product

Added on 2026-10-11, for
[#5](https://github.com/kostavo-oss/data-product-template/issues/5) and
[#13](https://github.com/kostavo-oss/data-product-template/issues/13). On 2026-10-07 the
owner left stevin out of the template; the portfolio review of 2026-10-08 gave it its
place: the product that does traditional SQL without dbt, and next to dbt the tables dbt
does not own. Everything in this section was built and run on a laptop. No workspace was
reached: no plan, no apply, no deploy. Both issues stay open for that half.

With stevin 0.4.0a1 and lely 0.3.1 from PyPI, uv 0.11.15, mise 2026.10.6.

### Decided

**Given to the writer as decided, 2026-10-11:**

- One question, `include_stevin`, off by default and independent of `include_dbt`. All
  four combinations generate a product: dbt only (as before), stevin only, both, neither.
- With stevin a product gets `stevin/`: the project file and the specs. stevin takes its
  targets and variables from the product's `databricks.yml`. There is no second list of
  targets, and the schemas stay the bundle's.
- Without dbt, `squares` is a stevin spec and a SQL task in the job fills it after
  `ingest`, from a `.sql` file that takes its schemas as parameters. With contracts the
  spec takes its shape from the contract (`from_contract`).
- With dbt, dbt builds `squares` as before, and a spec without column types puts a tag
  and a grant on the landed table `numbers`.
- stevin runs at a deploy and never in the job. The tasks are validate, plan, apply and
  drift; validate is part of `mise run check`, so `ci.yml` needs no change.
- A second question, `include_access_examples`, asked only with stevin, writes stevin's
  three access recipes as files under `stevin/security/`, with a page that names the
  placeholders and what stays hard.

**What did not hold, and what was done instead:**

- **lely's own `stevin` step cannot be used.** The design was a `stevin` step in
  `lely.yml` after `bundle`, so that one plan shows both. lely 0.3.1 has that step and
  says of it `Can't apply yet`: `lely apply` refuses the whole project (the run is
  below). Instead the product has a step of its own, `ops/tables.py`, a `lely.step.Program`
  that runs `stevin apply --target <target> --yes` after the bundle. lely's plan shows it
  as one run and not what it would change; `mise run tables:plan` shows that. So the
  table changes are not in the plan a pull request reviews. stevin stops by itself before
  a step that drops something.
- **With dbt, stevin is no step of the deploy at all.** Its one spec governs a table the
  job lands. On a new target that table is not there after the deploy, and stevin then
  stops: `… isn't there yet, and its spec only governs it — whoever owns it makes it
  first` (`stevin/planning.py`, read, not run). A step would fail every first deploy. So
  with dbt stevin runs from the tasks, after the job has run once. `lely.yml` gets the
  `tables` step only with stevin and without dbt.
- **`owned_elsewhere` cannot name a schema of the bundle.** The design was a pattern for
  the silver schema (dbt's) and one for the landing schema (dlt's). A key is read as three
  parts between dots, and `${resources.schemas.silver.name}` has dots of its own, so
  stevin refuses the key (the run is below). A schema's literal name would be wrong in a
  target that prefixes it. So the keys name tables, with `*` for the schema:
  `${catalog}.*.numbers: dlt` and `${catalog}.*.squares: dbt`. A new dbt model needs a
  line; the README and `AGENTS.md` say so.
- **Groups per schema is not a stevin spec here.** The schemas are the bundle's, and
  stevin's plan refuses a spec for a schema the bundle declares (`validate` does not: the
  run is below). So the grants stand in `resources/schemas.yml`, on `silver`, as
  comments, with the privileges spelled as a bundle spells them (`USE_SCHEMA`).
- **The access examples are written and not switched on.** Their specs name groups that
  no account has. Planned by default they would fail the first apply, and under lely the
  first deploy. So `stevin/stevin.yml` lists `tables` only, with `security` as a
  commented line, and `mise run check` validates the examples by path until then.
- **"Nothing mentions it" has one exception.** `.copier-answers.yml` records
  `include_stevin: false`, as it records every answer. Every other file of a product
  without stevin is the same, byte for byte, as before this change.

**By the writer, while building:**

- **stevin is a tool in `mise.toml`, pinned there and nowhere else:**
  `"pipx:stevin" = "0.4.0a1"`. Every stevin release so far is a pre-release. mise's
  `latest` finds no version for it; an exact version installs, through uv. The tasks and
  the step call `stevin` from the PATH. The tests read the pin from the product's
  `mise.toml` and run that version with `uvx`.
- **The tasks are `tables:validate`, `tables:plan`, `tables:apply` and `tables:drift`.**
  `plan`, `apply` and `destroy` are lely's. The three that reach a workspace set
  `BUNDLE_VAR_warehouse_id=$WAREHOUSE_ID`: stevin asks the Databricks CLI to resolve the
  bundle, and a bundle whose warehouse has no default does not resolve without it.
  `tables:apply` asks before it runs; only the step passes `--yes`.
- **The silver schema is the bundle's with dbt or with stevin**, and `ops/names.py`
  prints `SILVER` for both.
- **The output port is `squares` with dbt or with stevin.** Without dbt the table is
  filled on the workspace only, as a dbt model is. So its contract has the one
  `databricks` server, and the product has neither `contracts:test` nor `contracts:dbt`.
- **The SQL file uses named parameter markers:**
  `IDENTIFIER(:catalog || '.' || :silver_schema || '.squares')`. The job passes
  `catalog`, `raw_schema` and `silver_schema` by reference. `INSERT OVERWRITE` writes
  every row on every run, as dbt's table did. The file never makes the table.
- **The spec for `squares` adds clustering and a tag, and no grant.** A grant names a
  group, and a group that is not there fails the apply. A grant stands in the spec as a
  comment. With dbt the spec for `numbers` does name a group, `data_engineers`, as was
  decided: it is a placeholder, and that spec is applied by hand, after a plan was read.
- **No `history_schema`.** It would be a schema stevin makes, or a fourth one in the
  bundle. Without it an apply is not recorded and takes no lock; `stevin.yml` says so.
- **The examples live in the silver schema**: a mapping table, the row-filter function,
  and one example table that carries the filter and a column tagged `pii`. The policy
  that masks by tag is in the page, in Terraform and in SQL, as stevin's recipe has it.
  The template writes no `.tf` and no policy.
- **`_skip_if_exists` names `stevin/**` and `sql/**`.** The specs, the project file and
  the SQL are the product's own. The step, the tasks and the job are wiring.

### Requirements

- **R14 — With `include_stevin`, the tables and the access are specs.** `stevin/stevin.yml`
  names the bundle and no target. Without dbt: `stevin/tables/squares.yml`, from the
  contract when there is one; `sql/squares.sql`; a `transform` SQL task after `ingest`;
  and under lely a `tables` step after `bundle`. With dbt: `stevin/tables/numbers.yml`
  without column types, and `owned_elsewhere` naming `numbers` as dlt's and `squares` as
  dbt's. In both: the four `tables:*` tasks, `stevin validate` in `mise run check`, and
  the rules in `AGENTS.md`. Without `include_stevin` none of it is written.
- **R15 — With `include_access_examples`, an access model to start from.**
  `stevin/security/` has the three specs and a page; `resources/schemas.yml` has the
  schema grants as comments. The specs pass `stevin validate` and are planned only when
  the product lists the folder.

### Run

On 2026-10-11, on a laptop. Each line is a command and what it printed. The products were
generated with copier from the working tree: dbt only, neither, stevin only (with lely,
contracts and the examples, and without all three), and both (the same two ways).

| What | Printed |
|---|---|
| the two products without stevin, compared with what `main` generates | the same files with the same bytes, but for `include_stevin: false` in `.copier-answers.yml` |
| `mise exec pipx:stevin@0.4.0a1 -- stevin --version`, mise's own folders in a scratch place | `Installed 2 executables: deltaplan, stevin`, then `stevin 0.4.0a1`; exit 0 |
| the same with `pipx:stevin@latest` | `no versions found for pipx:stevin`; exit 1 |
| `uvx --from stevin==0.4.0a1 stevin --version` | `stevin 0.4.0a1`; exit 0 |
| `stevin validate -c stevin/stevin.yml`, stevin only, with the contract and without | `Not settled here: ${resources.schemas.silver.name}. …`, then `1 spec OK.`; exit 0 |
| the same with `-t prod` | `1 spec OK.`; exit 0 |
| the same, both, for the default target and for `prod` | `Not settled here: ${resources.schemas.raw.name}. …` and `1 spec OK.`; then `1 spec OK.`; exit 0 |
| the table from the contract compared with the table the spec declares, as stevin loads them | the same columns, types, key, comments and clustering |
| the spec with its contract removed | `stevin/tables/squares.yml:6:1: the data contract ../../contracts/output/squares/v1.odcs.yaml can't be read (No such file or directory)`; exit 1 |
| both, with `owned_elsewhere` left out | `warning: main.<product>_raw.numbers has no columns' types, so it governs a table another tool makes — nothing here says whose; the plan accepts it if the table is a dlt pipeline's, and otherwise asks you to name the owner in owned_elsewhere`; exit 0 |
| `owned_elsewhere` with the key `${catalog}.${resources.schemas.raw.name}.*` | `owned_elsewhere is keyed catalog.schema.table, with * for any part — e.g. ${catalog}.silver.* — not '${catalog}.${resources.schemas.raw.name}.*'`; exit 1 |
| both, with a spec for `squares` added | `error: main.<product>.squares is dbt's: put grants and tags in dbt's config, and use a schema-level policy for masks`; exit 1 |
| both, with column types in the spec for `numbers` | `error: … numbers is dlt's: leave the columns' types out to govern it (tags, grants, masks, a row filter), or take it out of owned_elsewhere`; exit 1 |
| `stevin validate -c stevin/stevin.yml -t dev stevin/security/*.yml`, and `-t prod` | `3 specs OK.`; exit 0 |
| the same without `-t` | `undefined variable ${catalog} (known: none defined for this target)`; exit 1: files named on the command line get no default target |
| the examples switched on in `stevin.yml`, default target and `prod` | `4 specs OK.`; exit 0 |
| the examples without `orders.yml` | `error: main.<product>.by_region is named by no column mask or row filter in this project: a function spec is only for a column mask or row filter; …`; exit 1 |
| a schema spec for the bundle's `silver`, `stevin validate -t prod` | `1 spec OK.`; exit 0: `validate` does not refuse it, the plan does (`stevin/planning.py`, read) |
| `lely steps` | `stevin  built-in`, `Tables, views, functions and grants, planned by stevin. Can't apply yet.`, `can    plan` |
| lely's own check before an apply (`lely.running.check_applies`), on a config with `uses: stevin` | ``Refused: Step `tables` uses `stevin`, which can plan and can't apply yet. Nothing was run.`` |
| `lely validate`, stevin only | `2 steps`, `tables  takes and gives nothing`; exit 0 (3 steps with a secret scope) |
| `uv run ops/tables.py --help` | the step's commands: `plan`, `apply`, `destroy`, `status`, `check`; exit 0 |
| the step's plan, held to lely's rules by `lely.testing.check_plan` | one change: `tables`, `run`, `runs stevin apply --config stevin/stevin.yml --target dev --yes` |
| the step's apply, with a stand-in for `stevin` first on the PATH | the stand-in was given `apply --config stevin/stevin.yml --target dev --yes`, in the product's folder, with `LELY_TARGET=dev` |
| the job of all six products, read as YAML | `ingest` then `transform`: a `sql_task` with `depends_on: ingest` without dbt, a `dbt_task` with dbt, and one task with neither |
| every command of each product's `check` task, in the four products with stevin, after `uv sync` | exit 0 each: ruff, the format check, `ingest list`, `dbt parse` with dbt, the contracts lint with contracts, `stevin validate` |

`tests/test_stevin.py` runs most of this again on every change.

### Not yet

All of it for one reason: it takes a workspace, and none was reached.

- **`stevin plan`, `apply` and `drift` on a product**, from the tasks or from the step.
  Nothing has shown that stevin resolves this bundle through the Databricks CLI, names
  the schemas as a development target deploys them, or makes `squares`.
- **The SQL task.** The file's `IDENTIFIER(:catalog || …)` with named parameter markers,
  the task's `parameters`, and the relative `file.path` are written from the Databricks
  documentation. The task has not run, and the bundle has not been validated by the CLI.
- **The `tables` step under lely on a workspace**: `lely plan` and `lely apply` with it,
  and the `plan` and `apply` workflows of a product that has it. The step's words were
  seen by a stand-in only.
- **The table changes in the reviewed plan.** That waits for lely's own `stevin` step,
  which is parked in lely.
- **With dbt: the tag and the grant on `numbers`**, the refusal on a new target before
  the job has run, and stevin telling dbt's table from its own on a workspace.
- **A grant taking effect**, on a table or on a schema. The grants in
  `resources/schemas.yml` are comments, and their spelling has not met a deploy.
- **The access examples applied**: the row filter filtering, the mapping table's seed
  (stevin's docs say no workspace has taken a seed from stevin yet), the tag on the
  column, and the policy masking it. Issue #13 is done when the row filter and the
  tagged table have been applied once.
- **A history schema**, and with it the lock against two applies at once.
- **`copier update` on a product that takes stevin later.** The contract of a product
  without dbt moves from `numbers` to `squares` when stevin is switched on, and
  `contracts/**` is the product's own.
- **The tasks through mise itself.** The commands behind them were run by hand, as
  before; `mise install` of the pinned stevin was seen in a scratch place only.

## Still open

1. **The job's `ingest` task, end to end,** on a workspace whose serverless compute can
   reach its storage. The job was not started in the run of 2026-10-10.
   [#4](https://github.com/kostavo-oss/data-product-template/issues/4)
2. **caland from the `secrets` task.**
3. **The `prod` target.** Only the dev target has been deployed, from a laptop and from
   the workflows.
4. **The tasks through mise, other than `check` and `dev`.** Those two ran on a GitHub
   runner after `jdx/mise-action` installed the tools; the others' commands were run by
   hand, or by the workflows without mise.
5. **stevin on a workspace**: every line under "stevin in a product", "Not yet".
   [#5](https://github.com/kostavo-oss/data-product-template/issues/5),
   [#13](https://github.com/kostavo-oss/data-product-template/issues/13)
6. **A release**, after the above, on the owner's word.

No longer open since 2026-10-10: a product as a GitHub repository, with the plan and
apply workflows run once (one repository, one pull request, one merge), and `mise install`
on a clean machine, seen on a GitHub runner.
