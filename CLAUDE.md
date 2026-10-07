# CLAUDE.md

`vierlingh`: a Databricks Asset Bundle template for a data product (dlt, dbt, one job, the
schemas as bundle resources), with the Kostavo tools around it as options. Read
`spec/README.md` first: what a generated product must do, who decided what, and what has
been tried on a workspace.

## Rules

- Files under `template/` ending in `.tmpl` are Go templates (`missingkey=error`): every
  `.input` must exist in `databricks_template_schema.json`. Files with dbt's Jinja, GitHub's
  `${{ }}` or mise's templates are **not** `.tmpl`: the two syntaxes clash.
- Every optional part is skipped from `databricks.yml.tmpl` with `{{ skip }}`, and the
  product must work without it: `databricks bundle deploy` without lely, `databricks
  secrets` without caland.
- What the template writes is tried, not read: `tests/` generates every prompt combination
  with the Databricks CLI and runs the generated project's own `check`.
- Nothing in a generated product references a specific team, platform or customer.
- Small PR-sized commits, conventional commit messages. A release is the owner's word.

## Commands

```sh
uv sync
mise run test     # needs the Databricks CLI (mise installs it)
mise run check
```
