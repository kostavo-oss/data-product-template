"""What dbt's laptop profile reads, from the same sign-in everything else uses.

The Databricks SDK finds the profile the way the CLI and leeghwater do, and gives a token
for it — a personal access token as it is, an OAuth token freshly made. It goes to the one
dbt command the task runs, and nowhere else.
"""

import os
import shlex

from databricks.sdk import WorkspaceClient

client = WorkspaceClient(profile=os.environ.get("DATABRICKS_CONFIG_PROFILE") or None)
token = client.config.authenticate()["Authorization"].removeprefix("Bearer ")
# dbt wants the host without its scheme.
host = client.config.host.removeprefix("https://").removeprefix("http://")
print(f"export DBT_HOST={shlex.quote(host)}")
print(f"export DBT_TOKEN={shlex.quote(token)}")
