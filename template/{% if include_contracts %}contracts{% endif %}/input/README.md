# Input ports

An input port is a table this product reads from another product. Add it to
`dataproduct.yaml` under `inputPorts`, with its `name`, the `version` and `contractId` the
producer gives it, and under `authoritativeDefinitions` an entry of type `dataContract`
whose `url` is where the producer keeps the contract: a URL, or a path from this folder to
a checkout beside it. A second entry, of type `dataProduct`, may name the producer's
`dataproduct.yaml`.

`mise run contracts:pull` fetches the contract and writes it here, as
`<port>/v<major version>.odcs.yaml`. That file is a snapshot of the producer's promise on
the day it was pulled. Commit it, and never edit it by hand: a pull request then shows
what this product depends on, and a later pull shows what the producer changed.

`mise run contracts:check` compares the snapshot with what the producer has now. It
refuses when the producer broke the contract or no longer lists the version, and warns
when the version is marked deprecated. With a server,
`uv run ops/ports.py check --server <name>`, it also tests the producer's data against the
snapshot.

## A pipeline that keeps the contract

`mise run contracts:dlt` writes a dlt schema from every snapshot, as
`src/<package>/schemas/<port>.schema.yaml`. Every schema object of the contract is a
table, every property is a column with its type, and every table is frozen. Run it after
every pull and commit the file. It is never edited by hand: the next run writes it again.

A pipeline that loads the port names the folder:

```python
SCHEMAS = Path(__file__).parent.parent / "schemas"

p = leeghwater.create_pipeline("<port>", import_schema_path=SCHEMAS)
```

dlt looks there for `<schema name>.schema.yaml`. The schema's name is the pipeline's name,
or the name of the `@dlt.source` the pipeline runs: one of the two has to be the port's
name. The resource has the name of the contract's schema object. The run then fails on a
row with a column the contract does not have, on a value of another type, and on an empty
value where the contract says `required` or `primaryKey`.

When the names differ, dlt finds no schema, loads every row, and writes a file of its own
into the folder. To make that a failure too, freeze the run as well. It then also refuses
a table the contract does not have:

```python
leeghwater.run(p, data, schema_contract="freeze")
```

| In the contract (`logicalType`) | In the schema (`data_type`) |
|---|---|
| `string` | `text` |
| `integer` | `bigint` |
| `number` | `double` |
| `boolean` | `bool` |
| `date`, `timestamp`, `time` | the same |
| `object`, `array` | `json` |

A property with no `logicalType`, or with another one, is refused by name, and so is a
name dlt would change (`paidAt` becomes `paid_at`). dlt keeps the rows of a failed run and
tries them again on the next run from the same machine; its message names the command that
drops them.
