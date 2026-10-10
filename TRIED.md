# Tried, and not yet

What has been run for real, and what has not: on a workspace, on GitHub, and on a laptop
with the real tools. This file is the one record of it. Each table is a run, with its
date, what it ran on and what it printed. Everything else a product does is held by the
tests, which generate products and reach no workspace ([RULES.md](RULES.md)).

A run is recorded here and nowhere else. Nothing under "Not yet" is written about as if
it had run.

## 2026-10-07 and 2026-10-08: a laptop and one workspace

The full answers, on one test workspace, from a laptop with a profile. Everything made
was removed afterwards. On 2026-10-07 the product was written by the
`databricks bundle init` template the repository began as. It is a copier template now
([DECISIONS.md](DECISIONS.md), 1).

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
| The job's `ingest` task | **not run**: that day it needed leeghwater from PyPI, where it is since 0.1.0 of 2026-10-08. This workspace's serverless compute refuses dlt's upload to storage, as leeghwater's own run showed, and that still stands |
| `mise install` and the tasks through mise itself | **not run** that day: the task commands were run by hand; mise would also have installed tools on this machine. `mise install`, `check` and `dev` held on a GitHub runner on 2026-10-10 (below) |
| caland from the `secrets` task | **not run**: it opens a page in a browser |
| The GitHub workflows | **not run** that day: the product was not a repository on GitHub. They held on 2026-10-10 (below) |

Found and fixed while trying:

- YAML reads `dbt build --vars '{raw_schema: …}'` as a mapping unless the command is
  quoted whole.
- dbt-databricks wants the host without its scheme.
- A `{{ config(...) }}` inside a SQL comment is read by dbt, and set the model to a
  view.
- `databricks auth env` is deprecated and prints a warning first, so the dbt sign-in
  goes through the SDK. `databricks auth token` only serves OAuth profiles.

## 2026-10-10: on GitHub, from a repository

One run, on one private repository made from the template at commit `95da290` with
`uvx copier copy --defaults`: the catalog `workspace`, a warehouse id, with dbt, lely,
caland and contracts. Nothing was edited by hand; `uv lock` added the lock file. The
repository had `DATABRICKS_HOST` and `WAREHOUSE_ID` as variables and `DATABRICKS_TOKEN`
as a secret, for the test workspace. Everything made was removed afterwards.

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

Found and fixed in this run: the product's `.gitignore` did not ignore `.env`
([DECISIONS.md](DECISIONS.md), 13).

## 2026-10-10: the contracts, on a laptop

With `datacontract-cli[duckdb,databricks]==1.2.4` through `uvx`. No workspace. Each line
is a command and what it printed last.

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

## 2026-10-10: a dlt schema from an input contract, on a laptop

For [#11](https://github.com/kostavo-oss/data-product-template/issues/11), with dlt 1.31.0 and leeghwater 0.1.0, into a local DuckDB file.

Where the freeze can stand. A pipeline made with `import_schema_path` reads
`<schema name>.schema.yaml` from that folder. Three places were tried, each with a row
that has one column too many:

| Where `freeze` stood | What dlt did |
|---|---|
| in the file, under `settings: schema_contract` | loaded the row and added the column: the file's settings are not kept |
| in the file, on the table: `schema_contract: freeze` | `Contract on columns with contract_mode=freeze is violated. Can't add table column note to table transactions because columns are frozen.` |
| on the run: `run(..., schema_contract="freeze")`, nothing in the file | the same refusal, and also `Can't add table other because tables are frozen` for a table the file does not have |

Then, each a command and what it printed last. `ingest run` is the product's own
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

## 2026-10-11: stevin in a product, on a laptop

For [#5](https://github.com/kostavo-oss/data-product-template/issues/5) and [#13](https://github.com/kostavo-oss/data-product-template/issues/13), with stevin 0.4.0a1 and lely 0.3.1 from PyPI, uv
0.11.15 and mise 2026.10.6. No workspace was reached: no plan, no apply, no deploy. Each
line is a command and what it printed. The products were generated with copier from the
working tree: dbt only, neither, stevin only (with lely, contracts and the examples, and
without all three), and both (the same two ways).

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

## Not yet

On a workspace:

- **The job's `ingest` task, end to end**, and with it the job itself, on a workspace
  whose serverless compute can reach its storage. [#4](https://github.com/kostavo-oss/data-product-template/issues/4)
- **caland from the `secrets` task.** It opens a page in a browser. [#4](https://github.com/kostavo-oss/data-product-template/issues/4)
- **The `prod` target.** Only the dev target has been deployed, from a laptop and from
  the workflows. [#20](https://github.com/kostavo-oss/data-product-template/issues/20)
- **The contracts in the job**: `check` as the job's first task, `test` as its last. And
  a test against the `databricks` server of a contract, from anywhere: the server
  entries are linted and their variables were seen to resolve on a DuckDB server, and
  the `physicalType` of each column is what Databricks is expected to report and has
  not been compared there. [#10](https://github.com/kostavo-oss/data-product-template/issues/10)
- **A load into Databricks with a dlt schema from a contract**, and the job's `ingest`
  task reading that schema from the wheel.
- **`stevin plan`, `apply` and `drift` on a product**, from the tasks or from the step.
  Nothing has shown that stevin resolves this bundle through the Databricks CLI, names
  the schemas as a development target deploys them, or makes `squares`. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **The SQL task.** The file's `IDENTIFIER(:catalog || …)` with named parameter markers,
  the task's `parameters` and the relative `file.path` are written from the Databricks
  documentation. The task has not run, and the bundle of a product with stevin has not
  been validated by the CLI. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **The `tables` step under lely**: `lely plan` and `lely apply` with it, and the `plan`
  and `apply` workflows of a product that has it. The step's words were seen by a
  stand-in only. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **With dbt: the tag and the grant on `numbers`**, the refusal on a new target before
  the job has run, and stevin telling dbt's table from its own. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **A grant taking effect**, on a table or on a schema. The grants in
  `resources/schemas.yml` are comments, and their spelling has not met a deploy.
- **The access examples applied**: the row filter filtering, the mapping table's rows,
  the tag on the column, and the policy masking it. stevin itself loaded a seed on a
  workspace on 2026-10-10, as its own docs say; no product has. [#13](https://github.com/kostavo-oss/data-product-template/issues/13)

On GitHub:

- **The CI gate for more than one case.** It refused a removed column on a pull request
  on 2026-10-10. A new version file and a compatible edit were seen to pass in a local
  repository only.

On a laptop:

- **The tasks through mise itself, other than `check` and `dev`.** Those two ran on a
  GitHub runner after `jdx/mise-action` installed the tools. For the others the command
  behind the task was run by hand, or by a workflow without mise. `mise install` of the
  pinned stevin was seen in a scratch place only. [#21](https://github.com/kostavo-oss/data-product-template/issues/21)
- **`copier update` on a product that takes stevin later.** The contract of a product
  without dbt moves from `numbers` to `squares` when stevin is switched on, and
  `contracts/**` is the product's own.
- **`dlt pipeline <name> abort-packages` answered from a script.** It asked and dropped
  nothing; `dlt.attach(...).abort_packages()` did.
