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

## 2026-10-11: every combination of the parts, on a laptop

For [#18](https://github.com/kostavo-oss/data-product-template/issues/18), with copier
9, in-process, from the working tree. No workspace and no network.

| What | Held? |
|---|---|
| Generating all 48 combinations of dbt, stevin (with and without the access examples), lely, caland and contracts, each with a secret scope and without: 96 products | yes |
| Searching every file of each for the names of the parts it left out, `.copier-answers.yml` aside | found, before the fix: dbt's folders and `site/` in `.gitignore` and in the `clean` task, `ops/dbt_env.py`, a comment about dbt in `pyproject.toml`, the `dbt` verb in `ops/ports.py`, and `lely.yml` named in `README.md`, `AGENTS.md` and `ops/scope.py` of a product with a secret scope and without lely. After it: nothing, but the import of lely's library in that `ops/scope.py` |
| The product with every part, compared with what `main` generates | the same files with the same bytes |
| Every command of the `check` task, in the product with every part and in the one with none, after `uv sync` | exit 0 each |

`tests/test_parts.py` runs this again on every change.

## 2026-10-11: the tasks through mise, on a laptop

For [#21](https://github.com/kostavo-oss/data-product-template/issues/21), with mise
2026.10.6. Four products were generated from the working tree into a
scratch folder: every part (`all-yes`), no part (`all-no`), contracts only (`landed`),
and every part but dbt (`sql`). mise ran with a home folder of its own, empty at the
start: no global mise config, no Databricks profile, no dlt state. `mise install`
brought python 3.12.15, uv 0.13.0, the Databricks CLI 1.20.0, lely 0.3.0, stevin 0.4.0a1
and caland 0.7.1, then `uv sync` ran. No workspace was reached.

Each task of the product with every part, and `contracts:test`, which only a product
without dbt and stevin has:

| Task | Through `mise run` |
|---|---|
| `dev` | ran offline on 2026-10-11: exit 0, `example.duckdb` written; `mise run dev -- --count 3` passed the words on |
| `check` | ran offline on 2026-10-11: exit 0 in all four products, and again after `contracts:dbt` and with a `mise.local.toml` |
| `fix` | ran offline on 2026-10-11: exit 0, `12 files left unchanged` |
| `clean` | ran offline on 2026-10-11: exit 0, `example.duckdb` and `site/` gone |
| `contracts:lint` | ran offline on 2026-10-11: `Data contract is valid. Ran 1 checks.`; exit 0 |
| `contracts:test` | ran offline on 2026-10-11, in `landed` after `dev`: `Ran 6 checks.`; exit 0 |
| `contracts:pull`, `contracts:check`, `contracts:dlt` | ran offline on 2026-10-11: exit 0 and nothing printed, because the product has no input port. With a port they have run from the tests only, not through mise |
| `contracts:catalog` | ran offline on 2026-10-11: `Created site/contracts/index.html`; exit 0 |
| `contracts:dbt` | ran offline on 2026-10-11: exit 0, and `check` passed after it |
| `contracts:edit` | ran offline on 2026-10-11: the page answered 200 at `http://localhost:4243` with the title `v1.odcs.yaml - Data Contract Editor`, and an interrupt stopped it |
| `tables:validate` | ran offline on 2026-10-11: `1 spec OK.`; exit 0, in `all-yes` and in `sql` |
| `deploy`, `job` | needs a workspace and has not run. mise resolves it: `mise run <task> -- --help` printed the Databricks CLI's usage, exit 0 |
| `scope` | needs a workspace and has not run. `mise run scope -- --help` printed `Usage: scope.py apply [OPTIONS]`, exit 0 |
| `doctor` | needs a workspace and has not run. `mise run doctor -- --help` printed `Usage: ingest doctor [OPTIONS]`, exit 0 |
| `ingest`, `transform` | needs a workspace and has not run. `mise run <task> -- example` with a profile that does not exist stopped at `No deployed names to read: deploy the target first (mise run deploy).`, exit 1. The profile it named was the one from `mise.local.toml` |
| `tables:plan`, `tables:apply`, `tables:drift` | needs a workspace and has not run. `-- --help` printed stevin's usage for the verb, exit 0 |
| `plan`, `apply`, `destroy` | needs a workspace and has not run. `-- --help` printed lely's usage for the verb, exit 0 |
| `secrets` | needs a workspace and has not run. `mise run secrets -- --help` printed caland's usage, exit 0 |

Found while trying:

- `ingest` and `transform` went on after `ops/names.py` failed: `eval "$(...)"` does
  not stop a script when the command inside fails. `ingest` then ended on
  `RAW: unbound variable`, and `transform` ran `ops/dbt_env.py` too and ended on its
  traceback. Fixed: the output is read first and then taken, and the task ends on the
  script's own words.
- A second product on the same laptop loads its example into the first one's
  `example.duckdb`: dlt keeps a pipeline's state by its name, with the folder it first
  ran in. `contracts:test` then fails in the second product. Not fixed:
  [#24](https://github.com/kostavo-oss/data-product-template/issues/24). For the runs
  above the state was removed between products.
- mise's `latest` brought lely 0.3.0 while PyPI had 0.3.1 since the evening before:
  `1 newer pipx:lely release hidden by minimum_release_age`. A release is not what
  `mise install` brings on its first day.

## 2026-10-11: the first release, on GitHub

The tag `v0.1.0` was made on `main` at `388a580` and pushed on 2026-10-11
([#22](https://github.com/kostavo-oss/data-product-template/issues/22)).

| What | Held? |
|---|---|
| `uvx copier copy --defaults gh:kostavo-oss/data-product-template <folder>`, with copier 9.18.2 and no `--vcs-ref` | yes: the product was written from the tag, and `.copier-answers.yml` has `_commit: v0.1.0` and `_src_path: gh:kostavo-oss/data-product-template` |

## 2026-10-11: lely's own step for the tables, and the pins, on a laptop

For [#19](https://github.com/kostavo-oss/data-product-template/issues/19), with lely
0.4.0 and stevin 0.4.0a2 from PyPI, both released that day, uv 0.11.15 and mise
2026.10.6. No workspace was reached: no plan, no apply, no deploy. The products were
generated with copier from the working tree. mise ran with a home folder of its own,
empty at the start.

| What | Printed |
|---|---|
| `mise latest pipx:lely`, a few minutes after lely 0.4.0 was on PyPI | `0.3.0`, and `2 newer pipx:lely releases hidden by minimum_release_age` |
| `mise latest pipx:lely@0.4` | nothing: a prefix finds no hidden release either |
| `mise settings ls --all`, in the empty home | no `minimum_release_age` is set: it is mise's own default. `minimum_release_age_excludes` is `[]` |
| `mise install` in a product with every part, and in one with every part but dbt | exit 0: python 3.12.15, uv 0.13.0, the Databricks CLI 1.20.0, **lely 0.4.0**, **stevin 0.4.0a2**, caland 0.7.1 (`latest`; 0.7.3 was a few hours old) |
| `uv sync` in both | exit 0; the lock file has leeghwater 0.2.1, dlt 1.31.0 and duckdb 1.5.6 |
| `lely --version`, `stevin --version`, `caland --version`, through `mise exec` | `lely 0.4.0`, `stevin 0.4.0a2`, `caland 0.7.1` |
| `lely validate`, every part but dbt | `3 steps`, `tables  takes and gives nothing`; exit 0 (2 steps with dbt, where stevin is no step) |
| `lely steps` | `stevin  built-in`, `Tables, views, functions and grants, planned and applied by stevin.`, `can    plan, apply, list`; exit 0 |
| `stevin validate -c stevin/stevin.yml`, in both, for the default target and for `prod` | `Not settled here: ${resources.schemas.raw.name}, ${resources.schemas.silver.name}. …` and `1 spec OK.`; then `1 spec OK.`; exit 0, no warning |
| `mise run check` in both | exit 0, with `1 spec OK.` and `3 specs OK.` for the access examples |
| `mise run plan`, `apply`, `destroy`, `tables:plan`, `tables:apply`, each with `-- --help` | the tool's usage for the verb; exit 0 each. None has run |
| with dbt and no access examples, a spec for a new table `other` in `silver` | `error: main.<product>.other is dbt's: put grants and tags in dbt's config, and use a schema-level policy for masks`; exit 1 |
| the same for the default target | the same refusal, with the schema shown as `resources_schemas_silver_name`: `validate` does not ask what a development target deploys it as |
| with dbt and the access examples, `owned_elsewhere` with `${catalog}.${resources.schemas.silver.name}.*: dbt` | `stevin/security/orders.yml: error: main.<product>.orders is dbt's …`, the same for `region_members`, `2 problems in 3 specs.`; exit 1. So that product names dbt's tables one by one ([DECISIONS.md](DECISIONS.md), 24) |
| the same product as the template writes it, the examples named on their own and switched on | `3 specs OK.`; `4 specs OK.`; exit 0 |

`tests/test_stevin.py` runs the validations again on every change, with lely and stevin
at the versions the product pins.

## 2026-10-11: two products on one laptop

For [#24](https://github.com/kostavo-oss/data-product-template/issues/24), with mise
2026.10.6, leeghwater 0.2.1, dlt 1.31.0 and duckdb 1.5.6. Two products were generated
from the working tree, `first-shop` and `second-shop`, each with contracts only. mise
ran with one home folder for both, empty at the start: no dlt state. No workspace.

| What | Printed |
|---|---|
| `mise run dev` in `first-shop` | `first run    yes: this pipeline had no state before`; exit 0; `first_shop_example.duckdb` in its folder |
| `mise run dev` in `second-shop`, straight after | the same line; exit 0; `second_shop_example.duckdb` in its folder, and the first product's file kept its time |
| `ls ~/.dlt/pipelines` | `first_shop_example`, `second_shop_example` |
| `mise run contracts:test` in `second-shop`, then in `first-shop` | `Server: local (type=duckdb, database=second_shop_example.duckdb, …`, `Data contract is valid. Ran 6 checks.`; exit 0 each |
| `mise run check` in `first-shop` | exit 0 |
| a product made from `v0.1.0` and updated, untouched, in a home folder of its own: `mise run dev`, `contracts:test`, `check` | exit 0 each; it still loads into `example.duckdb` |
| the same product with the pipeline and the contract's `local` server renamed by hand: `mise run dev`, `contracts:test` | `first run    yes`; `old_shop_example.duckdb` beside `example.duckdb`; `Ran 6 checks.`; exit 0 each |

`tests/test_generated_project.py` generates two products and runs this again on every
change. With the old name that test fails.

## 2026-10-11: an update from 0.1.0 to 0.2.0, on a laptop

With copier 9.18.2 and mise 2026.10.6. The template was a local clone of this
repository with the tag `v0.1.0` as it is, and a temporary tag `v0.2.0` on what the
release holds. Six products were made from `v0.1.0`, committed, and updated with
`uvx copier update --defaults`: every part but dbt, every part, contracts only, the
default answers, no part, and dbt with stevin and nothing else. No workspace.

| What | Held? |
|---|---|
| The update, in all six | exit 0, `_commit: v0.2.0`, no conflict and no `.rej` file |
| What it changed | `AGENTS.md` in all six; `mise.toml` where there is lely or stevin; `lely.yml` in the product with the `tables` step, where it also removed `ops/tables.py`. Nothing under `src/`, `contracts/` or `stevin/` |
| `mise install` after it | lely 0.4.0 and stevin 0.4.0a2 where the product has them |
| `mise run check` and `mise run dev` after it, in all six | exit 0 each; the example still loads into `example.duckdb` |
| `lely validate` after it | exit 0: `3 steps` with the `tables` step, `2 steps` with dbt |
| `stevin validate` for `prod` with the `owned_elsewhere` lines of 0.1.0, under stevin 0.4.0a2 | `1 spec OK.`; exit 0 |

## 2026-10-11, later: lely 0.4.1 and stevin 0.4.0a3, on a laptop

For [#27](https://github.com/kostavo-oss/data-product-template/issues/27). Both were
released that afternoon, and the pins moved to them: with them the `tables` step waits
on a target that is new, where the plan failed. The runs of the two sections above were
made again with these versions, mise in a new and empty home folder. No workspace.

| What | Printed |
|---|---|
| `mise install` in a product with every part, and in one with every part but dbt | exit 0: **lely 0.4.1**, **stevin 0.4.0a3**, caland 0.7.1, python 3.12.15, uv 0.13.0, the Databricks CLI 1.20.0 |
| `uv sync` in both | exit 0; leeghwater 0.2.1, dlt 1.31.0, duckdb 1.5.6 |
| `lely --version`, `stevin --version`, through `mise exec` | `lely 0.4.1`, `stevin 0.4.0a3` |
| `lely validate` | exit 0: `3 steps` without dbt (`scope`, `bundle`, `tables`), `2 steps` with dbt |
| `lely steps` | exit 0; the `stevin` step `can    plan, apply, list` |
| `stevin validate -c stevin/stevin.yml`, default target and `prod`, in both | `1 spec OK.`; exit 0 each, no warning |
| `mise run check` in both | exit 0 |
| The steps of `lely.yml`, read in five generated products | without dbt: `bundle`, `tables`, with `scope` first when a scope was named. With dbt, and without stevin: `bundle`, with `scope` first. No step runs the job |
| `copier update` from `v0.1.0`, the six products of the section above | exit 0 each, no conflict; it now moves `.github/workflows/apply.yml` too, where there is lely |
| `mise install`, `mise run check`, `mise run dev` and `lely validate` after the update | exit 0 each; lely 0.4.1 and stevin 0.4.0a3 where the product has them |
| `stevin validate -t prod` with the `owned_elsewhere` lines of 0.1.0, under stevin 0.4.0a3 | `1 spec OK.`; exit 0 |

## 2026-10-11: loosened access at the contract gate, on a laptop

With `datacontract-cli[duckdb,databricks]==1.2.4` through `uvx`, in a local git
repository made from a product without dbt. No workspace, and nothing on GitHub. The
contract of `numbers` was first given classifications and tags, on a nested property and
in an array too, and two roles, and committed on `main`: ODCS v3.2.0, and `ports.py lint`
called it valid. Then `v1.odcs.yaml` was edited on a branch.

| What | Printed |
|---|---|
| `datacontract breaking` on a lowered and a removed classification, removed tags, an added role, a raised access | `[ 10 Info ]`, every row `INFO`; exit 0 |
| `datacontract breaking --help` and `changelog --help` | no option for a format a script reads |
| `ports.py breaking --base main` on those edits | `…/v1.odcs.yaml: compatible` on stdout; on stderr one line each, such as `contracts/output/numbers/v1.odcs.yaml: numbers.id: classification restricted -> public`, `…: numbers.buyer.email: classification confidential -> none`, `…: numbers.lines.items.sku: classification internal -> PUBLIC`, `…: numbers.id: tag pii -> none`, `…: the contract: tag region:eu -> region:us`, `…: role analysts: access read -> write`, `…: role everyone: no such role -> access read`, then the sentence naming the label; exit 2 |
| the same with a classification changed from `Secret` to `internal` | `…: numbers.square: classification Secret -> internal`; exit 2 |
| the same with `--access-reviewed` | the same lines on stdout as `…/v1.odcs.yaml: reviewed: numbers.id: classification restricted -> public`; nothing on stderr; exit 0 |
| `--access-reviewed` with a column removed as well | `a breaking change needs a new version, v2.odcs.yaml beside it`; exit 2 |
| a raised classification, an added tag, a removed role, a lowered access | `…/v1.odcs.yaml: compatible`; nothing on stderr; exit 0 |
| the script of the workflow's step, by bash with a stand-in for `uv`, `ACCESS_REVIEWED` set to `true`, to `false` and to nothing | the flag is passed for `true` only |

`tests/test_contracts.py` runs this again on every change. The label itself is under
"Not yet".

## Not yet

On a workspace:

- **The job's `ingest` task, end to end**, and with it the job itself, on a workspace
  whose serverless compute can reach its storage. [#4](https://github.com/kostavo-oss/data-product-template/issues/4)
- **caland from the `secrets` task.** It opens a page in a browser. [#4](https://github.com/kostavo-oss/data-product-template/issues/4)
- **The tasks that reach a workspace, through mise**: `deploy`, `job`, `scope`,
  `doctor`, `ingest`, `transform`, `tables:plan`, `tables:apply`, `tables:drift`, `plan`,
  `apply`, `destroy` and `secrets`. mise resolves each and its command line parses
  (above); none has run. Whether `plan`, `apply` and `destroy` work for a product whose
  `warehouse_id` has no default is not known: they pass no warehouse to the bundle.
  [#21](https://github.com/kostavo-oss/data-product-template/issues/21)
- **The `prod` target.** Only the dev target has been deployed, from a laptop and from
  the workflows. [#20](https://github.com/kostavo-oss/data-product-template/issues/20)
- **The contracts in the job**: `check` as the job's first task, `test` as its last. And
  a test against the `databricks` server of a contract, from anywhere: the server
  entries are linted and their variables were seen to resolve on a DuckDB server, and
  the `physicalType` of each column is what Databricks is expected to report and has
  not been compared there. [#10](https://github.com/kostavo-oss/data-product-template/issues/10)
- **A load into Databricks with a dlt schema from a contract**, and the job's `ingest`
  task reading that schema from the wheel.
- **The job's first run after a pipeline was renamed** in a product that had already
  loaded under the old name. To dlt the new name is a new pipeline.
- **`stevin plan`, `apply` and `drift` on a product**, from the tasks or from the step.
  Nothing has shown that stevin resolves this bundle through the Databricks CLI, names
  the schemas as a development target deploys them, or makes `squares`. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **The SQL task.** The file's `IDENTIFIER(:catalog || …)` with named parameter markers,
  the task's `parameters` and the relative `file.path` are written from the Databricks
  documentation. The task has not run, and the bundle of a product with stevin has not
  been validated by the CLI. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **The `tables` step under lely**: `lely plan` and `lely apply` with lely's own `stevin`
  step, and the `plan` and `apply` workflows of a product that has it. lely has taken
  the config and named what the step can do; nothing has planned. lely's own docs say
  the step has not run on a workspace or against the real `stevin` command.
  [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **The first deploy of a target that is new**, with the `tables` step: all of it.
  stevin 0.4.0a3 ends its plan with exit code 5 when a table's schema is the bundle's
  and is not there yet, and lely 0.4.1 then shows the step as waiting. What follows is
  what lely's docs say and its tests show against stand-ins. No workspace has seen any
  of it, from this template or from lely: at a terminal, one `lely apply` that deploys
  the bundle, then plans the tables and asks; through the workflows, a first plan with
  the tables waiting, a first `apply` that deploys the bundle and ends red with exit
  code 2 at the tables, and a second pull request whose plan lists the tables and whose
  merge makes them.
  [#27](https://github.com/kostavo-oss/data-product-template/issues/27)
- **With dbt, `tables:plan` before the job has run once.** stevin 0.4.0a3 is said to end
  with exit code 5 and name `numbers` as dlt's and not there yet. Not seen.
  [#27](https://github.com/kostavo-oss/data-product-template/issues/27)
- **A schema named by reference in `owned_elsewhere`, on a development target.**
  `validate` takes the key and does not settle it. That `stevin plan` reads
  `${resources.schemas.<key>.name}` as the prefixed name a development target deploys
  has not been seen from a product.
  [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **With dbt: the tag and the grant on `numbers`**, the refusal on a new target before
  the job has run, and stevin telling dbt's table from its own. [#5](https://github.com/kostavo-oss/data-product-template/issues/5)
- **A grant taking effect**, on a table or on a schema. The grants in
  `resources/schemas.yml` are comments, and their spelling has not met a deploy.
- **The access examples applied**: the row filter filtering, the mapping table's rows,
  the tag on the column, and the policy masking it. stevin itself loaded a seed on a
  workspace on 2026-10-10, as its own docs say; no product has. [#13](https://github.com/kostavo-oss/data-product-template/issues/13)

On GitHub:

- **An update from one release to the next, taken from GitHub.** The repository has one
  tag. That copier leaves a pre-release and what `main` has since, and updates a product
  from one tag to the next, was seen with a template in a local git repository only.
- **The CI gate for more than one case.** It refused a removed column on a pull request
  on 2026-10-10. A new version file and a compatible edit were seen to pass in a local
  repository only.
- **The label `access-reviewed`, on a pull request.** That GitHub's expression is `true`
  with the label and `false` without, that putting the label on or taking it off starts
  `ci` again, and that the step then fails without it and passes with it: none of it has
  run on GitHub. The step's script ran under bash on a laptop, with the variable set by
  hand. [#31](https://github.com/kostavo-oss/data-product-template/issues/31)

On a laptop:

- **The contracts tasks with an input port, through mise**: `contracts:pull`,
  `contracts:check` and `contracts:dlt` ran through mise on a product that reads
  nothing. [#21](https://github.com/kostavo-oss/data-product-template/issues/21)
- **Two products on one laptop that load the same input port.** A pipeline that keeps
  an input contract is named after the port, so they share dlt's state as two examples
  did. [#28](https://github.com/kostavo-oss/data-product-template/issues/28)
- **The access check on a contract of ODCS 3.0.2 or 3.1.0.** The three fields it reads
  are the same in those schemas; only 3.2.0 contracts were run.
- **`copier update` on a product that takes stevin later.** The contract of a product
  without dbt moves from `numbers` to `squares` when stevin is switched on, and
  `contracts/**` is the product's own.
- **`dlt pipeline <name> abort-packages` answered from a script.** It asked and dropped
  nothing; `dlt.attach(...).abort_packages()` did.
