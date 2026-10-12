# Changelog

What changes for a product, release by release. A release is a tag on `main`,
`v<version>`, and its date is the tag's. `uvx copier update` in a product moves it from
the release it was made from to the newest one.

## [Unreleased]

## [0.3.0]

- With contracts, the gate on a pull request refuses an edit to a contract that is out
  when it loosens access, which the Data Contract CLI lets through: a classification
  lowered or taken away, a tag removed, a role added, a role's access raised. It names
  the file and the field and ends with exit code 2. The pull request passes once someone
  gives it the label `access-reviewed`: `ci` then runs again and prints the same lines
  as reviewed. At a terminal that is `uv run ops/ports.py breaking --base main
  --access-reviewed`. `uvx copier update` moves `ops/ports.py` and
  `.github/workflows/ci.yml`: nothing is done by hand, but `ci` now also runs when a
  label is put on or taken off a pull request. A contract that says nothing of
  classifications, tags or roles is judged as before.

## [0.2.0]

The table changes are in the plan a pull request reviews, and two products on one laptop
no longer meet. `uvx copier update` from 0.1.0 applies without a conflict, and then
`mise install` brings the tools the product now pins. Two things stay as they are in a
product that exists, because the files are the product's own, and each has its steps by
hand below: the lines under `owned_elsewhere:` and the example pipeline's name. Neither
has to be taken.

- With stevin, with lely and without dbt, the table changes are in the plan a pull
  request reviews. The step `tables` in `lely.yml` is lely's own `stevin` step: the plan
  lists what changes on each table, and the merge applies that plan. `ops/tables.py` is
  gone. `uvx copier update` moves `lely.yml` and `mise.toml` and removes
  `ops/tables.py`: nothing is done by hand.
- A first deploy of such a product needs no deploy by hand. On a target that is new the
  plan shows the tables waiting, because their schema is the bundle's and is not there
  yet. At a terminal `mise run apply` is one command: it deploys the bundle, then plans
  the tables, shows them and asks. Through the workflows it is two pull requests: the
  first `apply` deploys the bundle and ends red at the tables, with exit code 2, which
  is expected that once; the next pull request's plan lists the tables and its merge
  makes them. This has not been seen on a workspace yet.
- `mise.toml` pins lely to 0.4.1 and stevin to 0.4.0a3. lely was `latest`, which does
  not bring a release on its first day. Run `mise install` after the update.
- In a new product, `stevin/stevin.yml` says whose tables are whose with one pattern for
  each schema, named as the bundle names it, so a new dbt model needs no line there. A
  product that exists keeps its own file: `stevin/**` is the product's. To take it by
  hand, replace the lines under `owned_elsewhere:` with

  ```yaml
  owned_elsewhere:
    ${catalog}.${resources.schemas.raw.name}.*: dlt
    ${catalog}.${resources.schemas.silver.name}.*: dbt
  ```

  and leave the dbt line as it was when `stevin/security/` is switched on: its tables
  are stevin's own and stand in `silver`. The lines of 0.1.0 keep working with stevin
  0.4.0a3.
- In a new product the example's dlt pipeline is named `<package>_example`, no longer
  `example`, so two products on one laptop no longer load into each other's file. It
  loads into `<package>_example.duckdb`. A product that exists keeps its name:
  `src/**` and `contracts/**` are the product's, and the update changes neither. To take
  it by hand, give `create_pipeline` the new name in `src/<package>/pipelines/example.py`
  and, with contracts and without dbt and stevin, change the `local` server in
  `contracts/output/numbers/v1.odcs.yaml` to `database: <package>_example.duckdb` and
  `schema: <package>_example_dataset`. A new name is a new pipeline to dlt: on the
  laptop the next `mise run dev` is a first run into the new file, and
  `~/.dlt/pipelines/example/` and `example.duckdb` can be deleted. What the renamed
  pipeline does on its first run in the job has not been tried.

## [0.1.0]

The first release. Until it, copier took whatever `main` was that day.

- A product is a Databricks Asset Bundle: the schemas `raw`, `raw_staging` and `silver`,
  one job, dlt pipelines run by leeghwater, a `ci` workflow, `AGENTS.md`, and every task
  behind `mise run`.
- Each part is a question, and a product may leave it out: dbt, stevin with or without
  the access examples, lely with its `plan` and `apply` workflows, caland, and contracts
  through the Data Contract CLI.
- A part that was not chosen leaves nothing in the product: no file, no task, no line in
  `.gitignore`, and no pointer to a `lely.yml` that is not there.
- `mise run ingest` and `mise run transform` stop with what is missing when the deployed
  names cannot be read. They used to go on without them.
- A product made from `main` before this release takes it with `uvx copier update`.
