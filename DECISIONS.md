# Decisions

What a reader cannot get from [RULES.md](RULES.md) or from the template itself: why
something is so, and what was tried or considered and rejected, so that nobody proposes
it again. A decision that says neither has no entry here.

An entry has a number, a date, the decision in a sentence, the reason, and what it
replaced. **An entry is never edited**: a decision that changes gets a new entry at the
end, which names the one it supersedes by its number.

## 1. 2026-10-07 — copier, not `databricks bundle init`

Both were built to compare them. With copier a product takes the template's next change
(`copier update`, with `_skip_if_exists` keeping the product's own files); a bundle
template writes a product once and leaves it on its own. A template whose products
cannot take its next change is a one-time gift, and the wiring will change. Besides:
Go's text/template renders every file and its `{{ }}` clashes with dbt's Jinja, GitHub's
`${{ }}` and mise's own, where copier renders only `.jinja` files; and generating with
`bundle init` needs the Databricks CLI and configured credentials, where copier needs
Python. The cost: a bundle template can be registered in a workspace's UI, and this one
is found by one command in the README.

Replaced: the bundle template of the repository's first commit, and before it
`leeghwater init`, a command that wrote a project. Why that command left is not
recorded.

## 2. 2026-10-07 — No local dbt run, so no local test of a dbt product's contract

From a laptop dbt runs against a workspace. Models written in Databricks SQL would not
all run on DuckDB. It follows (2026-10-10) that the contract of `squares` names the
deployed table only and that `contracts:test` exists only without dbt: a developer's run
writes `numbers` and never `squares`. The default answers are left without a local test
of the contract.

Replaced: a design in which every contract had a `duckdb` server.

## 3. 2026-10-08 — The secret scope is a step of the product's own

A new target then brings its scope with it, and the scope's name is typed once, not in
the job and again by hand on the workspace.

## 4. 2026-10-10 — Renamed data-product-template

The address copier is given then says what it is. The namesake stays in the README.

Replaced: `vierlingh`.

## 5. 2026-10-10 — Contracts without a package of our own

The template writes files, tasks, a CI gate and one script, and runs the Data Contract
CLI as a pinned `uvx` command. The CLI already does what a package would have done:
`lint`, `test` on a DuckDB file, `breaking`, `catalog`, `dbt sync`. What it does not
know is where a product keeps its files and which contract belongs to which port, and
that is the script.

Replaced: a contracts package, which was specified first and dropped.

## 6. 2026-10-10 — A version of a contract is a file, and ids can be read

`contracts/<direction>/<port>/v<N>.odcs.yaml`, not a folder for each version: a port has
one contract for each version and nothing else to keep beside it. The product's id is
its name and a contract's is `<product>.<port>`, not the UUID ODPS suggests: ODPS
requires only a string.

## 7. 2026-10-10 — Names that differ per target are variables with a default

A contract's server says `${CATALOG:-main}` and `${SILVER:-<package>}`. The CLI fills
them from the environment, `mise.local.toml` and `ops/names.py` already give those
names, and the default is the prod target's, so nothing new had to be made up.

## 8. 2026-10-10 — What ODPS leaves open, settled

An input port gives its contract's address under `authoritativeDefinitions`, as
`type: dataContract`: ODPS v1.1.0 has that list and its `type` is free text, so
`customProperties` was not needed. A path is accepted beside a URL, though the schema
marks `url` as `format: uri`: validators do not enforce formats unless asked. A port
without `contractId` or `version` is refused, though ODPS allows both to be left out:
such a port names nothing to fetch and gives its snapshot no name.

## 9. 2026-10-10 — The script fetches, the CLI compares

`pull`, `check` and `breaking` read both sides themselves and hand the CLI two local
files: one way of fetching, and equal bytes need no CLI. The CLI's `breaking` exits 1
for a breaking change and also for a file it cannot read, so the script tells them apart
by the word `Details`, which the CLI prints only when a comparison was made.

## 10. 2026-10-10 — `check` asks about the port's life before it compares

A producer that withdraws a version usually removes its contract file too, and "the
producer no longer lists version 1.0.0" says more than "not found".

Replaced: the design, which compared first.

## 11. 2026-10-10 — `ci.yml` is rendered, and holds no `${{ }}`

The contracts gate is a conditional step, so the file has to be rendered. It reads the
base branch from `GITHUB_BASE_REF`, which keeps GitHub's `${{ }}` out of a rendered
file. The gate looks only at version files that exist: taking a version away is the
producer's last step after deprecating it, and no comparison can say whether it is time.

Replaced: `ci.yml` copied as it is.

## 12. 2026-10-10 — `ops/ports.py` is wiring, not the product's own

`_skip_if_exists` names `dataproduct.yaml` and `contracts/**` and not the script, so
that `copier update` brings a newer pin of the CLI and a fix to a verb. A product that
changed the script settles the difference at the update.

## 13. 2026-10-10 — `.env` is ignored

The Data Contract CLI loads a `.env` file, walking up the directories, and a developer
puts a token there. In the run on GitHub of that day the file showed as untracked, one
careless `git add` from being published.

## 14. 2026-10-10 — A dlt schema from a contract: frozen on each table, written by the script

Three places for the freeze were tried (TRIED.md). dlt does not keep the `settings` of a
schema file it imports. A freeze on the run needs a line on every run. On the table, the
file carries it and a pipeline needs one argument. The script writes the file itself and
does not use `datacontract export custom`: a template cannot refuse, and printed
`data_type: ` with nothing after it for a property without a type.

## 15. 2026-10-10 — What is in the schema file

It is inside the package, because a job runs the wheel and its working directory is not
the product's folder. It is named after the port, because dlt looks for the file by the
schema's name. dlt's own two tables and `previous_hashes` are in it, because dlt refuses
a file without them. A `number` is a double, because ODCS gives it no scale. A name dlt
would change (`paidAt`) is refused, not renamed: the script has no dlt to ask, and a
schema under the wrong name would freeze a column that never arrives.

## 16. 2026-10-11 — Where stevin runs in a deploy

Without dbt, a step of the product's own, `ops/tables.py`, runs `stevin apply --yes`
after the bundle. lely 0.3.1 has a `stevin` step that can plan and cannot apply, and
`lely apply` refuses a project that uses it. The cost is issue #19: the reviewed plan
shows one run, not the table changes. With dbt stevin is no step at all: its one spec
governs a table the job lands, which a new target does not have after the deploy, so a
step would fail every first deploy.

Replaced: the design, lely's own `stevin` step in `lely.yml`, so that one plan shows
both.

## 17. 2026-10-11 — stevin cannot name a schema of the bundle, in two places

`owned_elsewhere` names tables with `*` for the schema (`${catalog}.*.squares: dbt`): a
key is read as three parts between dots, `${resources.schemas.silver.name}` has dots of
its own, and a literal name would be wrong in a target that prefixes it. So a new dbt
model needs a line. And groups per schema are comments in `resources/schemas.yml`, not a
stevin spec: stevin's plan refuses a spec for a schema the bundle declares.

Replaced: the design, one pattern for each schema, and schema grants as a spec.

## 18. 2026-10-11 — Nothing is planned that names a group no account has

A group that is not there fails the apply, and under lely the deploy. So the access
examples are written and not listed in `stevin/stevin.yml`, and the spec for `squares`
has its grant as a comment. The spec for `numbers`, with dbt, does name a placeholder
group, by the owner's choice: it is applied by hand, after a plan was read.

## 19. 2026-10-11 — stevin's pin and its tasks

stevin is pinned to an exact version in `mise.toml`: every release so far is a
pre-release, and mise's `latest` finds none of those. The tasks are `tables:*` because
`plan`, `apply` and `destroy` are lely's. They set `BUNDLE_VAR_warehouse_id`, because
stevin asks the Databricks CLI to resolve the bundle, and a bundle whose warehouse has
no default does not resolve without it.

## 20. 2026-10-11 — No `history_schema`

It would be a schema stevin makes, or a fourth one in the bundle. Without it an apply is
not recorded and takes no lock.

## 21. 2026-10-11 — One place per fact

The repository had a `spec/` folder: one file that held the requirements, the
decisions, the runs, the open questions and the history together. A fact written in two
places went stale in one of them, and the file contradicted itself. Now each kind of
fact has one file (CLAUDE.md), as in `kostavo-oss/tools`.

Replaced: the spec.
