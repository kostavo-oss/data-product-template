# vierlingh

**A data product for Databricks, ready to start from.** A template for a Databricks Asset
Bundle: dlt lands the data, dbt shapes it, one job runs both, the schemas are the bundle's —
and the Kostavo tools around it, each optional: leeghwater runs the pipelines, lely deploys
with a reviewed plan, caland keeps the secrets, and every task is one `mise run` away.

> **Early.** A generated product has been deployed to a workspace, loaded from a laptop,
> and shaped by its dbt task on serverless; what was tried and what was not is in
> `spec/README.md`.

```sh
uvx copier copy gh:kostavo-oss/vierlingh my-product
cd my-product
mise install && uv sync
mise run dev        # the example pipeline, here, into a local DuckDB file
mise run deploy     # the dev target on your workspace
mise run job        # the job: ingest, then transform
```

Later, in the product, `uvx copier update` brings the template's next change — to the
bundle, the job, the tasks and the workflows, never to your pipelines, models or README.

## What you get

```
<product>/
  databricks.yml                 variables catalog and warehouse_id; targets dev and prod
  resources/schemas.yml          raw, raw_staging, silver — made by the bundle
  resources/<product>.job.yml    ingest (wheel task) → transform (dbt task)
  src/<package>/pipelines/       dlt pipelines, run by leeghwater
  dbt/                           dbt models, reading raw through source('raw', ...)
  lely.yml, .github/workflows/   plan on a pull request, apply on merge
  mise.toml, .mcp.json           every task; mise's MCP server for coding agents
  AGENTS.md                      the rules, each with its reason
```

The questions: a name, a catalog, a warehouse, a secret scope, and whether to include dbt,
lely and caland. `--data name=value` or a data file answers them without a terminal, and
`.copier-answers.yml` in the product remembers them.

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

> **Terraform for your platform, Asset Bundles for your code, stevin for your data model —
> and lely to deploy them as one.**

vierlingh is one of the [Kostavo tools](https://github.com/kostavo-oss) for Databricks: the
bundle you start from.

Community project, not affiliated with or endorsed by Databricks, dltHub or dbt Labs.

## License

Apache-2.0.
