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
