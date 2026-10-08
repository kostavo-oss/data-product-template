# spec

What vierlingh has to do, and how we know that it does.

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
- The name is the writer's to propose; `vierlingh` was proposed and confirmed on 2026-10-08
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
| Discoverability | the Databricks way; registrable in a workspace's UI | `uvx copier copy gh:kostavo-oss/vierlingh`; nothing in the workspace |
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
  warehouse, a secret scope, and yes/no for dbt, lely and caland; `--data` answers them
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
  that survived. Only `.jinja` files are rendered; dbt's models, GitHub's workflows and
  mise's files are copied as they are, because their own syntaxes would clash.
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

## Still open

1. **The job's `ingest` task, end to end,** on a workspace whose serverless compute can
   reach its storage.
2. **A product as a GitHub repository,** to see the plan and apply workflows run.
3. **`mise install` on a clean machine,** to see the tools arrive as listed.
4. **A release**, after the above, on the owner's word.
