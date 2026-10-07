"""An example pipeline. It makes its own rows, so the first run needs no source and no secret."""

import dlt
import leeghwater
from leeghwater import pipeline


@dlt.resource(write_disposition="merge", primary_key="id")
def numbers(count: int):
    yield from ({"id": n, "square": n * n} for n in range(1, count + 1))


@pipeline
def example(count: int = 10):
    """Load a few numbers and their squares."""
    # Not dlt.pipeline() and not pipeline.run(): where a run loads is the run's to say.
    # On your laptop that is a local DuckDB file, in the job the schema the bundle deployed.
    p = leeghwater.create_pipeline("example")
    return leeghwater.run(p, numbers(count))


# The same, with a secret. dlt asks for `sources.example.api_key`, and finds it in the
# environment, in .dlt/secrets.toml, or in a secret scope as `sources-example-api_key`:
#
#   databricks secrets put-secret <scope> sources-example-api_key
#
# @dlt.source
# def from_an_api(api_key: str = dlt.secrets.value):
#     ...
