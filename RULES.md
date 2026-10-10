# Rules

What must be true of a product this template writes. Each rule is one or two sentences in
the present tense, and names the tests that hold it. Why a rule is so is in
[DECISIONS.md](DECISIONS.md); what ran for real, on a workspace, on GitHub or on a
laptop, is in [TRIED.md](TRIED.md).

## How this file is kept

- A rule has an identifier: an area and a number, such as `BND-3`. Tests and documents
  cite a rule by that identifier and by nothing else. Nothing under `template/` cites
  one: a product has no copy of this file.
- A new rule takes the next number in its area. A number is never reused: a rule that is
  dropped leaves a gap, and a rule that changes its meaning gets a new number.
- Under each rule stands `Held by:` with the tests that hold it, each as
  `tests/<file>.py::<test>`. Each of those tests cites the identifier, and no other test
  does.
- A rule no test can hold says `Not tested:` and why, in place of `Held by:`.
- A rule states the whole promise, also when the template does not keep all of it yet.
  Such a rule is open: it says `Not kept yet:`, the number of the issue that tracks it,
  and what the template does instead, as `Not kept yet: #12 — what happens instead`. Its
  `Held by:` names the tests of the part that holds, if there are any. When the template
  keeps the rule the line is taken out, and the rule gets the test it lacked.
- A rule is checked against a generated product before it is written. A change to what
  the template writes changes its rule and its test in the same pull request.
  `tests/test_rules.py` checks all of the above.

The areas: `GEN` generating and updating a product, `BND` the bundle, `DLT` the
pipelines, `DBT` the dbt project, `TSK` the mise tasks, `DEP` the deploy with lely, `SEC`
secrets, `CON` contracts, `STV` stevin, `ACC` the access examples, `DOC` the pages a
product gets.

## GEN — generating and updating a product

- **GEN-1** — A product is written by `copier copy` from this repository, with or
  without a terminal: every question has a default, and `--data` or a data file answers
  the rest.
  Held by: `tests/test_template.py::test_the_full_answers_write_everything`,
  `tests/test_template.py::test_the_default_answers_write_a_product`.
- **GEN-2** — The questions are a project name, a package name, a catalog, a warehouse
  id, a secret scope, and a yes or no for dbt, stevin, lely, caland and contracts. dbt,
  lely, caland and contracts are on by default and stevin is off. The access examples
  are asked only with stevin. `.copier-answers.yml` in the product records every answer
  that was asked.
  Held by: `tests/test_template.py::test_the_default_answers_write_a_product`,
  `tests/test_template.py::test_the_package_name_is_derived_from_the_project_name`,
  `tests/test_stevin.py::test_without_stevin_nothing_mentions_it`,
  `tests/test_stevin.py::test_the_access_examples_are_asked_only_with_stevin`.
- **GEN-3** — A project name starts with a letter and has only letters, digits, `-` and
  `_`; any other is refused. The package name is derived from it, in small letters with
  `_` for `-`, and names the folder under `src/`, the job's key in the bundle and the
  dbt project.
  Held by: `tests/test_template.py::test_a_name_that_cannot_be_a_project_is_refused`,
  `tests/test_template.py::test_the_package_name_is_derived_from_the_project_name`.
- **GEN-4** — Only a file whose name ends in `.jinja` is rendered. Every other file is
  copied as it is: dbt's models, whose Jinja is dbt's, and the `plan` and `apply`
  workflows, whose `${{ }}` is GitHub's. No template syntax is left in a product but
  theirs.
  Held by: `tests/test_template.py::test_no_template_syntax_survives`,
  `tests/test_stevin.py::test_no_template_syntax_survives_and_every_yaml_file_parses`,
  `tests/test_contracts.py::test_ci_compares_the_contracts_with_the_base_branch`.
- **GEN-5** — A part that was not chosen is not in the product: none of its files, none
  of its tasks, and no mention of it outside `.copier-answers.yml`, which records every
  answer.
  Held by: `tests/test_template.py::test_the_bare_answers_skip_what_was_not_wanted`,
  `tests/test_template.py::test_the_readme_explains_each_part_that_was_included`,
  `tests/test_contracts.py::test_nothing_of_contracts_is_written_when_not_wanted`,
  `tests/test_stevin.py::test_without_stevin_nothing_mentions_it`.
  Not kept yet: #18 — it holds for stevin, lely and caland. Every product's `.gitignore`
  names the Data Contract CLI and `contracts:catalog`. A product without dbt gets
  `ops/dbt_env.py`, dbt's folders in `.gitignore` and in the `clean` task, and a comment
  about dbt in `pyproject.toml`. A product with a secret scope and without lely is
  pointed at a `lely.yml` it does not have, in its `README.md` and its `AGENTS.md`.
- **GEN-6** — `copier update` in a product brings the template's next change to the
  wiring: the bundle, the job, the tasks, the workflows, the scripts in `ops/` and
  `AGENTS.md`. It never touches what the product owns: `README.md`, `.dlt/config.toml`,
  and everything under `src/`, `dbt/models/`, `contracts/`, `stevin/` and `sql/`, and
  `dataproduct.yaml`.
  Held by: `tests/test_update.py::test_an_update_moves_the_wiring_and_keeps_what_the_product_owns`.
- **GEN-7** — Nothing in a product names a team, a platform or a customer.
  Not tested: it is an absence, and no test has the list of names to look for.
- **GEN-8** — The Python a product gets passes `ruff check` and `ruff format --check`,
  and every YAML file it gets parses.
  Held by: `tests/test_template.py::test_every_yaml_file_parses`,
  `tests/test_template.py::test_the_python_passes_the_linter`,
  `tests/test_stevin.py::test_no_template_syntax_survives_and_every_yaml_file_parses`,
  `tests/test_stevin.py::test_the_python_passes_the_linter`.

## BND — the bundle

- **BND-1** — The schemas are resources of the bundle: `raw` and `raw_staging` always,
  and `silver` with dbt or with stevin.
  Held by: `tests/test_template.py::test_the_schemas_are_bundle_resources`,
  `tests/test_stevin.py::test_the_silver_schema_is_the_bundles_with_dbt_or_stevin`.
- **BND-2** — The job is told the schemas by reference, as
  `${resources.schemas.<key>.name}`, and the catalog and the warehouse as variables of
  the bundle. A target may prefix a schema's name and nothing else has to know.
  Held by: `tests/test_template.py::test_the_job_is_told_the_bundles_schema_names_by_reference`.
- **BND-3** — A product has one job. Its first task is `ingest`, a wheel task that runs
  the product's own `ingest` command with the words `run example` and where to load. The
  task turns off the retry serverless compute does by itself.
  Held by: `tests/test_template.py::test_the_job_is_told_the_bundles_schema_names_by_reference`.
- **BND-4** — With dbt the job has a second task, `transform`, a dbt task after `ingest`.
  It names a warehouse, a catalog and a schema and no profiles directory: Databricks
  makes the profile. It runs `dbt build` with `raw_schema` as a variable, and each
  command is one quoted string. With stevin and without dbt `transform` is a SQL task
  (STV-4). With neither the job has the one task.
  Held by: `tests/test_template.py::test_the_job_is_told_the_bundles_schema_names_by_reference`,
  `tests/test_template.py::test_the_job_has_one_task_without_dbt_and_stevin`,
  `tests/test_stevin.py::test_with_dbt_the_job_has_no_sql_task`.
- **BND-5** — The bundle has two targets: `dev`, in development mode and the default,
  and `prod`, in production mode. The catalog has the default that was answered, and the
  warehouse has a default only when one was answered.
  Held by: `tests/test_template.py::test_the_warehouse_has_a_default_only_when_one_was_given`,
  `tests/test_template.py::test_the_targets_are_dev_and_prod`.
- **BND-6** — The wheel carries `.dlt/config.toml`, because a job's working directory is
  not the product's folder, and never `.dlt/secrets.toml`.
  Held by: `tests/test_template.py::test_the_wheel_carries_dlts_config_and_no_secrets`.

## DLT — the pipelines

- **DLT-1** — The product's console script is `ingest`: one command on a laptop and as
  the job's entry point. `ingest list` names the pipelines.
  Held by: `tests/test_generated_project.py::test_the_pipelines_import_and_are_listed`,
  `tests/test_template.py::test_the_package_name_is_derived_from_the_project_name`.
- **DLT-2** — The example pipeline makes its own rows and needs no source, no secret and
  no workspace: the command behind `mise run dev` loads it into a local DuckDB file.
  Held by: `tests/test_generated_project.py::test_the_example_runs_here_into_duckdb`.

## DBT — the dbt project

- **DBT-1** — A model reads raw through `source('raw', ...)`, and the source's schema is
  the variable `raw_schema`. No model names a schema.
  Held by: `tests/test_generated_project.py::test_dbt_parses_the_models`.
- **DBT-2** — `dbt parse` runs with no workspace, against the target `parse` of the
  product's `dbt/profiles.yml`.
  Held by: `tests/test_generated_project.py::test_dbt_parses_the_models`,
  `tests/test_generated_project.py::test_dbt_resolves_the_example_model_as_a_table`.
- **DBT-3** — The example model is a table, by `dbt_project.yml`. No SQL comment in a
  model holds Jinja: dbt reads Jinja in comments too.
  Held by: `tests/test_generated_project.py::test_dbt_resolves_the_example_model_as_a_table`,
  `tests/test_template.py::test_the_jinja_in_the_models_is_only_what_dbt_should_see`.
- **DBT-4** — From a laptop dbt runs against a workspace: `mise run transform` builds
  the models in the dev target's deployed schemas, signed in through the Databricks SDK
  with the profile everything else uses, and no token is pasted anywhere. There is no
  local dbt run.
  Not tested: it needs a workspace. It ran on one on 2026-10-07 (TRIED.md).

## TSK — the mise tasks

- **TSK-1** — `mise.toml` brings the tools: python, uv and the Databricks CLI, and lely,
  stevin and caland when they were chosen.
  Held by: `tests/test_template.py::test_mise_brings_the_tools_and_the_tasks_of_what_was_chosen`,
  `tests/test_template.py::test_the_bare_answers_skip_what_was_not_wanted`.
- **TSK-2** — Every product has the tasks `dev`, `check`, `fix`, `clean`, `deploy`,
  `job`, `doctor` and `ingest`. `transform` comes with dbt, `scope` with a secret scope,
  `plan`, `apply` and `destroy` with lely, `secrets` with caland, the `contracts:*` tasks
  with contracts (CON-4) and the `tables:*` tasks with stevin (STV-7).
  Held by: `tests/test_template.py::test_mise_brings_the_tools_and_the_tasks_of_what_was_chosen`,
  `tests/test_template.py::test_the_bare_answers_skip_what_was_not_wanted`.
- **TSK-3** — `mise run check` is the gate before a commit: ruff's check and format
  check and `ingest list`, then `dbt parse` with dbt, the contracts lint with contracts
  and `stevin validate` with stevin. The product's `ci` workflow runs it, and then the
  example pipeline.
  Held by: `tests/test_template.py::test_mise_brings_the_tools_and_the_tasks_of_what_was_chosen`,
  `tests/test_contracts.py::test_the_tasks_are_there_for_what_was_included`,
  `tests/test_stevin.py::test_ci_checks_the_specs_through_the_check_task`.
- **TSK-4** — `mise run ingest -- <pipeline>` loads from a laptop into the schemas the
  dev target deployed. `ops/names.py` reads their names back from
  `databricks bundle summary`, and says what is missing when there is no CLI or no
  deploy.
  Held by: `tests/test_generated_project.py::test_the_names_script_says_what_is_missing`.
- **TSK-5** — A developer's own profile, warehouse and catalog are in `mise.local.toml`,
  which git ignores. `mise.local.toml.example` is committed.
  Held by: `tests/test_template.py::test_git_ignores_a_file_of_credentials`.

## DEP — the deploy with lely

- **DEP-1** — With lely the product has a `lely.yml` whose steps are, in order: `scope`
  when a secret scope was named, `bundle`, and `tables` with stevin and without dbt.
  Held by: `tests/test_template.py::test_the_scope_is_a_step_before_the_bundle`,
  `tests/test_stevin.py::test_without_dbt_the_tables_are_a_step_after_the_bundle`,
  `tests/test_stevin.py::test_with_dbt_stevin_is_no_step_of_the_deploy`.
- **DEP-2** — With lely the product has two workflows. `plan` plans the dev target on
  every pull request, posts the plan as a comment and keeps it. `apply`, on a push to
  `main`, applies the plan that was made for the last commit of the merged pull request,
  and never a new one. A commit that came from no pull request is refused, so the first
  push to `main` shows a failed `apply`.
  Not tested: a workflow runs on GitHub only. Both held once, on one repository, on
  2026-10-10 (TRIED.md).

## SEC — secrets

- **SEC-1** — When a secret scope is named, `ops/scope.py` makes it. It is a lely step
  and a command of its own, with `plan`, `apply`, `destroy`, `status` and `check`, and
  needs no lely config. `mise run scope` applies it.
  Held by: `tests/test_generated_project.py::test_the_scope_step_runs_on_its_own`,
  `tests/test_template.py::test_the_scope_is_a_step_before_the_bundle`.
- **SEC-2** — Under lely the scope is the first step and gives the bundle its name as
  `${steps.scope.name}`. The job passes `${var.secret_scope}` to `ingest`, and the app
  names the scope.
  Held by: `tests/test_template.py::test_the_scope_is_a_step_before_the_bundle`,
  `tests/test_template.py::test_the_job_is_told_the_bundles_schema_names_by_reference`.
- **SEC-3** — Without a secret scope the bundle has no such variable, the job passes
  none, the app names none, and the README says where to give one.
  Held by: `tests/test_template.py::test_the_bare_answers_skip_what_was_not_wanted`,
  `tests/test_template.py::test_the_readme_explains_each_part_that_was_included`,
  `tests/test_template.py::test_the_scope_is_a_step_before_the_bundle`.
- **SEC-4** — With caland the task `secrets` opens caland on the bundle's workspace, and
  the README names it beside the CLI's own commands.
  Held by: `tests/test_template.py::test_mise_brings_the_tools_and_the_tasks_of_what_was_chosen`,
  `tests/test_template.py::test_the_readme_explains_each_part_that_was_included`.
- **SEC-5** — git ignores `.env`, `.env.*` and `.dlt/secrets.toml`: a token a tool reads
  from a file is not one `git add` from being published.
  Held by: `tests/test_template.py::test_git_ignores_a_file_of_credentials`.

## CON — contracts

- **CON-1** — With contracts, `dataproduct.yaml` lists the product's ports in ODPS
  v1.1.0, and every output port names a contract in ODCS v3.2.0 beside it:
  `contracts/output/<port>/v<N>.odcs.yaml`, where `N` is the major number of the port's
  version. The product's id is its name and a contract's id is `<product>.<port>`.
  Held by: `tests/test_contracts.py::test_contracts_are_written_with_and_without_dbt`,
  `tests/test_contracts.py::test_each_output_port_names_the_contract_beside_it`.
- **CON-2** — The contract a product starts with describes the table its example really
  makes: `squares` with dbt or with stevin, and `numbers`, the table the pipeline loads,
  with neither.
  Held by: `tests/test_contracts.py::test_the_contract_describes_what_the_example_makes`,
  `tests/test_stevin.py::test_the_contract_of_squares_is_there_with_stevin_and_no_dbt`.
- **CON-3** — The contract of `numbers` names two servers: the local DuckDB file and the
  deployed table. The contract of `squares` names the deployed table only, because that
  table is made on the workspace only. A name that differs per target is a variable
  whose default is the prod target's name.
  Held by: `tests/test_contracts.py::test_the_servers_are_the_local_file_and_the_deployed_table`,
  `tests/test_stevin.py::test_the_contract_of_squares_is_there_with_stevin_and_no_dbt`.
- **CON-4** — The tasks `contracts:lint`, `pull`, `check`, `dlt`, `catalog` and `edit`
  come with contracts, each running the same verb of `ops/ports.py`. `contracts:test`
  comes only without dbt and without stevin, and `contracts:dbt` only with dbt. The lint
  is part of `mise run check`.
  Held by: `tests/test_contracts.py::test_the_tasks_are_there_for_what_was_included`,
  `tests/test_stevin.py::test_the_contract_of_squares_is_there_with_stevin_and_no_dbt`.
- **CON-5** — On a pull request the product's `ci` compares every output contract that
  exists with the base branch. A breaking edit is refused with exit code 2 and the name
  of the next version file. A compatible edit and a new version file pass. A base git
  does not know is exit code 1, not a pass. A version file that was removed is not
  judged.
  Held by: `tests/test_contracts.py::test_ci_compares_the_contracts_with_the_base_branch`,
  `tests/test_contracts.py::test_a_compatible_edit_passes_the_gate`,
  `tests/test_contracts.py::test_a_breaking_edit_to_v1_is_refused`,
  `tests/test_contracts.py::test_a_new_version_passes_the_gate`,
  `tests/test_contracts.py::test_a_base_git_does_not_know_is_not_a_pass`.
- **CON-6** — `lint` checks every contract, and refuses with exit code 2 an output port
  that has no contract of its own.
  Held by: `tests/test_contracts.py::test_lint_passes_on_what_was_written`,
  `tests/test_contracts.py::test_lint_refuses_an_output_port_whose_contract_is_missing`.
- **CON-7** — `test` tests every output contract against the data on a server of the
  contract, the local file unless another is named.
  Held by: `tests/test_contracts.py::test_the_loaded_table_keeps_its_contract`.
- **CON-8** — `edit` opens an output contract of this product in the Data Contract
  Editor, and refuses a name that is not one of its output ports.
  Held by: `tests/test_contracts.py::test_edit_opens_a_promise_of_this_product_and_nothing_else`.
- **CON-9** — `dbt` writes columns and tests from the output contracts into the dbt
  models, and with `--dry-run` says what it would write and writes nothing.
  Held by: `tests/test_contracts.py::test_dbt_gets_its_columns_from_the_contract`.
- **CON-10** — `pull` fetches the contract of every input port, from a URL without
  credentials or from a path, and keeps it byte for byte as
  `contracts/input/<port>/v<N>.odcs.yaml`. A file that is another contract is refused.
  Held by: `tests/test_contracts.py::test_pull_keeps_the_producers_contract_as_a_snapshot`,
  `tests/test_contracts.py::test_pull_refuses_a_file_that_is_another_contract`.
- **CON-11** — `check` says whether what an input port reads is still what was pulled,
  and exits with 0 when fine, 1 when it could not run and 2 when it refuses. It asks
  first whether the producer still lists the version, and then compares the contract. It
  refuses when the version is gone or the contract was broken, warns when the version is
  marked deprecated or the contract changed compatibly, and says to pull when there is
  no snapshot.
  Held by: `tests/test_contracts.py::test_check_before_a_pull_says_to_pull`,
  `tests/test_contracts.py::test_check_is_fine_while_the_producer_keeps_its_promise`,
  `tests/test_contracts.py::test_check_warns_when_the_version_is_deprecated`,
  `tests/test_contracts.py::test_check_refuses_when_the_version_is_gone`,
  `tests/test_contracts.py::test_check_refuses_when_the_producer_broke_the_contract`,
  `tests/test_contracts.py::test_check_warns_when_the_producer_changed_the_contract_compatibly`.
- **CON-12** — An input port without a `contractId` or without a `version` is refused,
  with the reason.
  Held by: `tests/test_contracts.py::test_a_port_without_a_contract_is_refused_with_the_reason`,
  `tests/test_contracts.py::test_a_port_without_a_version_is_refused_with_the_reason`.
- **CON-13** — `dlt` writes a dlt schema from every input snapshot, as
  `src/<package>/schemas/<port>.schema.yaml`, and fetches nothing: `pull` does not write
  it. The schema is named after the port. Every schema object of the contract is a
  table, frozen, and every property a column: `string` is `text`, `integer` `bigint`,
  `number` `double`, `boolean` `bool`, `date`, `timestamp` and `time` the same, `object`
  and `array` `json`. A column is not nullable when the property is `required` or a
  `primaryKey`. dlt's own two tables are in the file. Without a snapshot it says to pull.
  Held by: `tests/test_contracts.py::test_dlt_writes_a_schema_from_the_snapshot`,
  `tests/test_contracts.py::test_dlt_before_a_pull_says_to_pull`.
- **CON-14** — `dlt` refuses, by name and with exit code 2, a property whose
  `logicalType` it has no type for or that has none, and a name dlt would load as
  another. It then writes no file.
  Held by: `tests/test_contracts.py::test_dlt_refuses_what_it_cannot_say_in_a_schema`.
- **CON-15** — A pipeline that is named after the port and names the schemas folder
  fails on a row with a column the contract does not have, on a value of another type
  and on an empty key, and loads none of that row.
  Held by: `tests/test_contracts.py::test_a_pipeline_refuses_what_the_contract_does_not_have`.

## STV — stevin

- **STV-1** — stevin is a question of its own, apart from dbt. Each of the four
  combinations is a product: dbt only, stevin only, both, neither.
  Held by: `tests/test_stevin.py::test_the_four_combinations_write_what_each_needs`.
- **STV-2** — stevin takes its targets and variables from the product's bundle:
  `stevin/stevin.yml` names `databricks.yml` and no target of its own. The schemas stay
  the bundle's: no spec declares one, and a spec names one by reference.
  Held by: `tests/test_stevin.py::test_stevin_takes_its_targets_from_the_bundle`,
  `tests/test_stevin.py::test_the_silver_schema_is_the_bundles_with_dbt_or_stevin`.
- **STV-3** — Without dbt the table `squares` is a spec. With contracts the spec takes
  the table's shape from the contract and says none of it itself. Without contracts it
  declares the same columns, types, key and comments. Either way it adds the clustering
  and a tag, and no grant. A spec whose contract is gone is refused.
  Held by: `tests/test_stevin.py::test_without_dbt_the_table_is_declared_and_its_shape_is_said_once`,
  `tests/test_stevin.py::test_a_spec_whose_contract_is_gone_is_refused`.
- **STV-4** — Without dbt the job's `transform` is a SQL task after `ingest`, run from
  `sql/squares.sql`. The file names no catalog and no schema: it takes them as
  parameters, which the job passes by reference. It writes the table's rows and never
  makes the table.
  Held by: `tests/test_stevin.py::test_without_dbt_the_job_fills_the_table_with_a_sql_task_after_ingest`,
  `tests/test_stevin.py::test_the_sql_names_no_schema_and_takes_every_name_as_a_parameter`.
- **STV-5** — With dbt, dbt builds `squares` as before. One spec, without column types,
  puts a tag and a grant on the landed table `numbers`. `stevin/stevin.yml` says that
  `numbers` is dlt's and `squares` is dbt's, so stevin refuses a spec for `squares`, and
  warns when nothing names the owner of `numbers`.
  Held by: `tests/test_stevin.py::test_with_dbt_stevin_governs_the_landed_table_and_leaves_dbts_alone`,
  `tests/test_stevin.py::test_the_governing_spec_warns_when_nothing_names_the_owner`.
- **STV-6** — The specs a product gets pass `stevin validate` with no workspace, for the
  dev and the prod target, without a warning.
  Held by: `tests/test_stevin.py::test_the_specs_validate_for_both_targets`.
- **STV-7** — The tasks are `tables:validate`, `tables:plan`, `tables:apply` and
  `tables:drift`. `validate` is part of `mise run check`. The three that reach a
  workspace give the bundle its warehouse, and `tables:apply` asks before it runs.
  stevin's version is pinned in `mise.toml` and nowhere else.
  Held by: `tests/test_stevin.py::test_the_tasks_are_there_and_stevin_is_pinned_in_one_place`.
- **STV-8** — stevin runs at a deploy and never in the job. Under lely and without dbt
  the tables are a step of the deploy, after the bundle, and the plan a pull request
  reviews shows what that step would change.
  Held by: `tests/test_stevin.py::test_without_dbt_the_tables_are_a_step_after_the_bundle`,
  `tests/test_stevin.py::test_lely_takes_the_config_with_the_tables_step`,
  `tests/test_stevin.py::test_the_tables_step_runs_stevin_apply_for_the_target`.
  Not kept yet: #19 — the step is the product's own `ops/tables.py`, which runs
  `stevin apply --yes` for the target. lely's plan shows it as one run and not what it
  would change; `mise run tables:plan` shows that.
- **STV-9** — With dbt stevin is no step of the deploy. Its spec governs a table the job
  lands, so it is applied from the task, after the job has run once, and the README says
  so.
  Held by: `tests/test_stevin.py::test_with_dbt_stevin_is_no_step_of_the_deploy`.

## ACC — the access examples

- **ACC-1** — With the access examples a product gets `stevin/security/`: three specs
  and a page. Without them it gets none of it.
  Held by: `tests/test_stevin.py::test_the_access_examples_are_asked_only_with_stevin`,
  `tests/test_stevin.py::test_the_access_examples_are_written_only_when_wanted`.
- **ACC-2** — The examples are checked by `mise run check` and are not planned until
  `stevin/stevin.yml` lists their folder. They pass `stevin validate` named on their
  own, and switched on.
  Held by: `tests/test_stevin.py::test_the_access_examples_are_checked_and_not_planned_until_switched_on`,
  `tests/test_stevin.py::test_the_access_examples_validate_on_their_own_and_switched_on`.
- **ACC-3** — Rows by region are a mapping table with its rows, a row-filter function
  that reads it, and an example table that names the function and has a column tagged
  `pii`. The function spec is valid only because the table names it.
  Held by: `tests/test_stevin.py::test_the_row_filter_is_a_function_the_example_table_names`,
  `tests/test_stevin.py::test_a_function_no_filter_names_is_refused`.
- **ACC-4** — Groups per schema are not a stevin spec. The grants stand in
  `resources/schemas.yml`, on `silver`, as comments, spelled as a bundle spells them.
  Held by: `tests/test_stevin.py::test_the_schema_grants_stand_in_the_bundle_as_comments`.
- **ACC-5** — The page of the examples names every placeholder and what stays hard
  before anything else. It shows the policy that masks by tag in Terraform and in SQL,
  and the template writes neither.
  Held by: `tests/test_stevin.py::test_the_readme_of_the_examples_names_every_placeholder_first`.

## DOC — the pages a product gets

- **DOC-1** — A product has an `AGENTS.md`: rules for a coding agent, each with its
  reason, and only the rules of the parts that were chosen.
  Held by: `tests/test_stevin.py::test_the_rules_for_agents_come_with_stevin`,
  `tests/test_contracts.py::test_nothing_of_contracts_is_written_when_not_wanted`.
- **DOC-2** — A product's `README.md` is its how-to. It has the tasks of each part that
  was chosen and, with stevin, the order of a first run: deploy, apply the tables, run
  the job without dbt; deploy, run the job, apply the tables with dbt.
  Held by: `tests/test_template.py::test_the_readme_explains_each_part_that_was_included`,
  `tests/test_stevin.py::test_the_readme_has_the_tasks_and_the_order_of_a_first_run`.
