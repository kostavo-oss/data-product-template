# CLAUDE.md

`vierlingh`: a Databricks Asset Bundle template for a data product (dlt, dbt, one job, the
schemas as bundle resources), with the Kostavo tools around it as options. Read
`spec/README.md` first: what a generated product must do, who decided what, and what has
been tried on a workspace.

## Rules

- It is a copier template (`copier.yml`, `template/`, `_templates_suffix: .jinja`). Only
  files ending in `.jinja` are rendered; dbt's models (Jinja of their own), GitHub's
  workflows (`${{ }}`) and mise's files are copied as they are. An optional part is a file
  or folder whose name carries its condition: `{% if include_dbt %}dbt{% endif %}`.
- Every optional part stays optional, and the product must work without it: `databricks
  bundle deploy` without lely, `databricks secrets` without caland.
- `_skip_if_exists` names what a product owns (its pipelines, models, README); everything
  else is the wiring `copier update` may move. Keep that line: a product that cannot be
  updated is a one-time gift.
- What the template writes is tried, not read: `tests/` generates the full and the bare
  answers with copier and runs the generated project's own checks. No workspace, no CLI.
- Nothing in a generated product references a specific team, platform or customer.
- Small PR-sized commits, conventional commit messages. A release is the owner's word.

## Commands

```sh
uv sync
mise run check    # lint, format, the tests; LEEGHWATER_WHEEL=<wheel> until leeghwater is on PyPI
```
