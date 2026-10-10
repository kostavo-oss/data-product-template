# data-product-template

**A data product for Databricks, ready to start from.** A
[copier](https://copier.readthedocs.io) template that writes a Databricks Asset Bundle:
dlt lands the data, dbt shapes it, one job runs both, the schemas are the bundle's.
leeghwater runs the pipelines. The other Kostavo tools are around it, each optional:
stevin keeps the tables and the access, lely deploys with a reviewed plan, caland keeps
the secrets. Every task is one `mise run` away.

> **Early.** A generated product has been deployed to a workspace, loaded from a laptop,
> and shaped by its dbt task on serverless. In one run, on one repository, the GitHub
> workflows planned on a pull request and applied the reviewed plan on merge. The job's
> `ingest` task has not finished on a workspace yet, and nothing of stevin has been
> applied to one. [TRIED.md](TRIED.md) has every run and what has not been run.

```sh
uvx copier copy gh:kostavo-oss/data-product-template my-product
cd my-product
mise install && uv sync
mise run dev        # the example pipeline, here, into a local DuckDB file
mise run deploy     # the dev target on your workspace
mise run job        # the job: ingest, then transform
```

Later, in the product, `uvx copier update` brings the template's next change — to the
bundle, the job, the tasks and the workflows, never to your pipelines, models,
contracts or README.

## What you get

```
<product>/
  databricks.yml                 variables catalog and warehouse_id; targets dev and prod
  resources/schemas.yml          raw, raw_staging, silver — made by the bundle
  resources/<product>.job.yml    ingest (wheel task) → transform (dbt task, or a SQL task)
  src/<package>/pipelines/       dlt pipelines, run by leeghwater
  dbt/                           dbt models, reading raw through source('raw', ...)
  stevin/, sql/                  with stevin: the tables as specs, and the SQL that fills them
  dataproduct.yaml, contracts/   the product's ports, and what each one promises
  ops/ports.py                   lint, test, pull and check the contracts
  lely.yml, .github/workflows/   plan on a pull request, apply on merge
  mise.toml, .mcp.json           every task; mise's MCP server for coding agents
  AGENTS.md                      the rules, each with its reason
```

The questions: a name, a catalog, a warehouse, a secret scope, and whether to include dbt,
stevin, lely, caland and contracts. dbt and stevin are apart: a product may have either,
both or neither. `--data name=value` or a data file answers the questions without a
terminal, and `.copier-answers.yml` in the product remembers them.

Each of those parts is optional, and the product works without it:
`databricks bundle deploy` needs no lely, `databricks secrets` needs no caland.

What must be true of a product is in [RULES.md](RULES.md), one numbered rule each, with
the tests that hold it. Why it is so is in [DECISIONS.md](DECISIONS.md).

## Tables and access, with stevin

[stevin](https://kostavo-oss.github.io/tools/stevin/) plans and applies the Unity Catalog
tables and the access that a transformation tool does not own. It is off by default
(`include_stevin`), and it does one of two things.

**Without dbt, it is the product that does traditional SQL.** The table `squares` is a
spec in `stevin/tables/`. stevin makes and migrates it at a deploy, and a SQL task in the
job fills it after `ingest`, from a `.sql` file that takes its schemas as parameters. With
contracts, the spec takes the table's shape from the contract.

**Next to dbt, it keeps what dbt does not own.** dbt builds `squares` as before. A spec
without column types puts a tag and a grant on the table dlt lands, and
`stevin/stevin.yml` says which tables are dbt's, so that a spec for one is refused.

```sh
mise run tables:validate    # the specs, with no workspace; part of `mise run check`
mise run tables:plan        # what would change on the dev target
mise run tables:apply       # the plan, shown, and run after a yes
mise run tables:drift       # does the target still match the specs
```

stevin takes its targets and variables from the product's `databricks.yml`, and the
schemas stay the bundle's. With `include_access_examples` the product also gets
`stevin/security/`: stevin's three
[access recipes](https://kostavo-oss.github.io/tools/stevin/access-recipes/) as files to
edit, with a page that says which names are placeholders. The rules are STV-1 to STV-9
and ACC-1 to ACC-5 in [RULES.md](RULES.md). None of this has been applied to a workspace
yet ([TRIED.md](TRIED.md)), and under lely the table changes are not in the plan a pull
request reviews
([#19](https://github.com/kostavo-oss/data-product-template/issues/19)).

## Contracts between products

A product says what it promises. `dataproduct.yaml` lists its ports, and every output port
names a contract: a file with the table's columns, their types, and which are never empty.
The template writes one for the table its example really makes. A product that reads
another product's table lists it as an input port and keeps the producer's contract as a
snapshot.

```sh
mise run contracts:lint       # every contract is valid; part of `mise run check`
mise run contracts:test       # the output contracts against the local DuckDB file
mise run contracts:pull       # fetch the input ports' contracts, as snapshots
mise run contracts:check      # is what is read still what was pulled
mise run contracts:dlt        # a dlt schema from each snapshot, for a pipeline to keep
mise run contracts:catalog    # the contracts as pages
mise run contracts:edit       # the output contract in an editor, on your own machine
mise run contracts:dbt        # columns and tests from the contracts into the dbt models
```

Without dbt the product gets `contracts:test` and with dbt `contracts:dbt`: a dbt model is
built on the workspace only, so there is no local copy of it to test. The same holds for
the table a SQL task fills, so a product with stevin and no dbt gets neither.

**CI holds the promise** (CON-5). On a pull request, every existing
`contracts/output/<port>/v<N>.odcs.yaml` is compared with the base branch. An edit that
breaks a reader (a column removed, a type changed) fails the job: a breaking change is a
new version file, `v<N+1>.odcs.yaml`. A new file always passes.

**A pipeline keeps what it reads** (CON-13 to CON-15). `contracts:dlt` writes a dlt schema
from every snapshot into `src/<package>/schemas/<port>.schema.yaml`, with every table
frozen. A pipeline named after the port takes it with one argument,
`leeghwater.create_pipeline("<port>", import_schema_path=SCHEMAS)`, and its run fails on a
row with a column the contract does not have. `contracts/input/README.md` in the product
has the rest.

**A consumer checks before it reads** (CON-11). `check` refuses when the producer broke
the contract or withdrew the version, and warns when the version is marked deprecated.

The tasks run `ops/ports.py`, a script of the product's own. It runs the
[Data Contract CLI](https://github.com/datacontract/datacontract-cli) as a pinned command,
and needs no platform and no account. `contracts:edit` opens the CLI's own
[Data Contract Editor](https://github.com/datacontract/datacontract-editor): a form, a
diagram and the YAML side by side, served from your machine and saved to the file. The
files are in two open standards from
[Bitol](https://bitol.io), a Linux Foundation project: ODCS for a contract, ODPS for a
product. Running the checks inside the job is not built yet:
[#10](https://github.com/kostavo-oss/data-product-template/issues/10).

## Why

The hard part of a data product on Databricks is not the source or the SQL; it is the
wiring between them. Schema names typed in three places and wrong in one target; a job
assembled by hand; a developer's run that doesn't match the job's; secrets pasted into
files. This template writes that wiring once: the schemas are bundle resources, the job
gets their deployed names by reference, dbt reads raw through a variable, the same
`ingest` command runs on a laptop and in the job, and a secret has one place to be.

## Named after

Andries Vierlingh (c. 1507–1579), dike master of Brabant, wrote the *Tractaet van
Dyckagie*: the first handbook of how dikes are built, for those who come after. A template
is a handbook you can run.

## Where it fits

data-product-template is where a product that uses the [Kostavo tools](https://github.com/kostavo-oss/tools) starts: small tools for the ugly gaps on Databricks, one gap each.
Kostavo is the company behind them: it builds [a governance platform for Databricks workspaces](https://kostavo.com), and the template and the tools are complete without it.

Community project, not affiliated with or endorsed by Databricks, dltHub or dbt Labs.

## License

Apache-2.0.
