# data-product-template

**A data product for Databricks, ready to start from.** A template for a Databricks Asset
Bundle: dlt lands the data, dbt shapes it, one job runs both, the schemas are the bundle's —
and the Kostavo tools around it, each optional: leeghwater runs the pipelines, lely deploys
with a reviewed plan, caland keeps the secrets, and every task is one `mise run` away.

> **Early.** A generated product has been deployed to a workspace, loaded from a laptop,
> and shaped by its dbt task on serverless; what was tried and what was not is in
> `spec/README.md`.

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
  resources/<product>.job.yml    ingest (wheel task) → transform (dbt task)
  src/<package>/pipelines/       dlt pipelines, run by leeghwater
  dbt/                           dbt models, reading raw through source('raw', ...)
  dataproduct.yaml, contracts/   the product's ports, and what each one promises
  ops/ports.py                   lint, test, pull and check the contracts
  lely.yml, .github/workflows/   plan on a pull request, apply on merge
  mise.toml, .mcp.json           every task; mise's MCP server for coding agents
  AGENTS.md                      the rules, each with its reason
```

The questions: a name, a catalog, a warehouse, a secret scope, and whether to include dbt,
lely, caland and contracts. `--data name=value` or a data file answers them without a terminal, and
`.copier-answers.yml` in the product remembers them.

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
mise run contracts:catalog    # the contracts as pages
mise run contracts:edit       # the output contract in an editor, on your own machine
mise run contracts:dbt        # columns and tests from the contracts into the dbt models
```

Without dbt the product gets `contracts:test` and with dbt `contracts:dbt`: a dbt model is
built on the workspace only, so there is no local copy of it to test.

**CI holds the promise.** On a pull request, every existing
`contracts/output/<port>/v<N>.odcs.yaml` is compared with the base branch. An edit that
breaks a reader (a column removed, a type changed) fails the job: a breaking change is a
new version file, `v<N+1>.odcs.yaml`. A new file always passes.

**A consumer checks before it reads.** `check` refuses when the producer broke the
contract or withdrew the version, and warns when the version is marked deprecated. It
exits 0 when fine, 1 when it could not run and 2 when it refuses.

The tasks run `ops/ports.py`, a script of the product's own. It runs the
[Data Contract CLI](https://github.com/datacontract/datacontract-cli) as a pinned command,
and needs no platform and no account. `contracts:edit` opens the CLI's own
[Data Contract Editor](https://github.com/datacontract/datacontract-editor): a form, a
diagram and the YAML side by side, served from your machine and saved to the file. The
files are in two open standards from
[Bitol](https://bitol.io), a Linux Foundation project: ODCS for a contract, ODPS for a
product. What is not built yet, running the checks inside the job, is in
`spec/README.md`.

## Why

The hard part of a data product on Databricks is not the source or the SQL; it is the
wiring between them. Schema names typed in three places and wrong in one target; a job
assembled by hand; a developer's run that doesn't match the job's; secrets pasted into
files. This template writes that wiring once: the schemas are bundle resources, the job
gets their deployed names by reference, dbt reads raw through a variable, the same
`ingest` command runs on a laptop and in the job, and a secret has one place to be.

Every tool around it is optional and the bundle works without it: `databricks bundle
deploy` needs no lely, `databricks secrets` needs no caland.

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
