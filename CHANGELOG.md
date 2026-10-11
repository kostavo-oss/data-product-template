# Changelog

What changes for a product, release by release. A release is a tag on `main`,
`v<version>`, and its date is the tag's. `uvx copier update` in a product moves it from
the release it was made from to the newest one.

## [Unreleased]

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
