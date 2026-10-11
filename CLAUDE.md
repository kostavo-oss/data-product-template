# CLAUDE.md

`data-product-template`: a copier template for a data product on Databricks. A product
is a Databricks Asset Bundle: dlt lands the data, dbt or a SQL task shapes it, one job
runs both, and the schemas are the bundle's. The Kostavo tools around it are options.

## Where a fact lives

One place per fact. Write a fact where it lives, and link to it from anywhere else.

| The fact | Its one place |
|---|---|
| What the template is for, what a product gets, how to choose | `README.md` |
| How to use a product | `template/README.md.jinja`: the product's own README |
| What must be true of a product | `RULES.md`: numbered rules, each with the tests that hold it |
| Why it is so, and what was tried and rejected | `DECISIONS.md`: a log, appended to and never edited |
| What ran for real, and what did not | `TRIED.md` |
| What a tool or Databricks does that the template leans on | a comment in the template file or the test that leans on it |
| An idea that is wanted and not built | a GitHub issue |
| What a release changes for a product | `CHANGELOG.md` |
| How it came to be | git |

There is no `spec/` folder, and none comes back.

## Rules of working

- **A change to what the template writes changes its rule, in the same pull request.**
  Find the rule in `RULES.md`, change it or add one with the next number of its area,
  and name the tests that hold it under `Held by:`. Each of those tests cites the
  identifier in a comment or its docstring. A number is never reused.
  `tests/test_rules.py` fails when a citation, a rule and a test disagree.
- **A rule is checked against a generated product before it is written, and states the
  whole promise.** What the template does not keep yet gets an issue, and the rule says
  `Not kept yet:` with its number. A rule is not worded down to what happens to hold.
- **A decision gets an entry in `DECISIONS.md` only when it says why, or what was tried
  and rejected.** What a rule or the template already says is not repeated there. An
  entry is appended with its date, and none is edited: a new one names the one it
  supersedes.
- **What the template writes is tried, not read.** The tests generate products with
  copier from the working tree and run their own checks. No workspace, no Databricks
  CLI. What could not be run is not in the template: it is under "Not yet" in
  `TRIED.md`, with an issue.
- **Nothing under "Not yet" in `TRIED.md` is written about as if it had run.** A run on
  a workspace or on GitHub is recorded there, with its date, and nowhere else.
- **Only files ending in `.jinja` are rendered** (GEN-4). A file with Jinja or `${{ }}`
  of its own, such as a dbt model or a workflow, is copied as it is. An optional part is
  a file or folder whose name carries its condition:
  `{% if include_dbt %}dbt{% endif %}`.
- **Every optional part stays optional** (GEN-5): every combination of the answers is
  generated and searched for the names of what it left out. A new part gets its names
  in `tests/test_parts.py`. `include_dbt` and `include_stevin` are apart (STV-1).
- **`_skip_if_exists` in `copier.yml` names what a product owns** (GEN-6). Everything
  else is the wiring `copier update` may move. A new kind of file is one or the other:
  say which, and keep `tests/test_update.py` in step.
- **Nothing under `template/` cites a rule or names a team, a platform or a customer**
  (GEN-7). A product has no copy of `RULES.md`.
- **A pull request that changes what a product gets adds a line under `[Unreleased]` in
  `CHANGELOG.md`**, saying what changes for a product.
- Small pull-request-sized commits, conventional commit messages.

## A release

A release is a tag on `main`, which copier takes (REL-1). It is the owner's word, each
time. Nothing but the tag and the changelog carries the version: `pyproject.toml` is the
tests' own and stays `0.0.0`.

1. A pull request moves the lines under `[Unreleased]` in `CHANGELOG.md` to a new
   section, `## [X.Y.Z]`, and names that version in the README's `--vcs-ref` example
   (REL-2). `mise run check` passes.
2. On the owner's word, after that pull request is merged:

   ```sh
   git fetch origin
   git tag -a vX.Y.Z -m "vX.Y.Z" origin/main
   git push origin vX.Y.Z
   ```

3. The tag is recorded in `TRIED.md`, with its date, in the next pull request.

A tag is never moved or deleted: a product records the tag it was made from. A
pre-release is a tag such as `vX.Y.Za1`; copier does not take it unless asked.

## Layout

```
copier.yml                       the questions, and what a product owns
template/                        everything a product gets
template/README.md.jinja         the product's README: its how-to
template/AGENTS.md.jinja         the product's rules for a coding agent (DOC-1)
template/ops/                    the product's scripts: names, dbt sign-in, ports, scope, tables
tests/conftest.py                the full and the bare answers, and how a product is generated
tests/test_template.py           what is written: the bundle, the job, the tasks (GEN, BND, TSK, SEC)
tests/test_generated_project.py  a generated product, run: its checks and its example (DLT, DBT)
tests/test_contracts.py          the contracts and ops/ports.py, run (CON)
tests/test_stevin.py             stevin and the access examples (STV, ACC)
tests/test_parts.py              every combination of the parts: what was left out leaves nothing (GEN-5)
tests/test_update.py             copier update on a product (GEN-6)
tests/test_release.py            what a tag promises, and the changelog (REL)
tests/test_rules.py              RULES.md against the tests and the documents
```

The tests generate eight products as fixtures: the full and the bare answers
(`conftest.py`), contracts without dbt and dbt without contracts (`test_contracts.py`),
and stevin with and without dbt, each with everything else and with nothing else
(`test_stevin.py`). `test_parts.py` generates all 96 combinations of the answers. Some
tests generate one more of their own.

## Commands

uv and ruff. Never pip, black or mypy.

```sh
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest         # generates the products; they sync leeghwater, lely and stevin from PyPI
mise run check        # the three above: the gate before a commit, and what CI runs
```

`LEEGHWATER_WHEEL=<path>` makes the generated product use a local wheel of leeghwater,
to try a change before it is released.
