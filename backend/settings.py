from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

DEFAULT_PROJECT = "supply-intelligence"
DEFAULT_BRANCH = "production"


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def apply_local_env() -> None:
    """Load repo-root .env for local runs. Skip under pytest. Do not override existing env."""
    if "pytest" in sys.modules:
        return
    for key, value in _parse_env_file(ENV_PATH).items():
        os.environ.setdefault(key, value)
    file_secret = os.getenv("LAKEBASE_DATABASE_CLIENT_SECRET")
    if file_secret and not os.getenv("DATABRICKS_CLIENT_SECRET"):
        os.environ["DATABRICKS_CLIENT_SECRET"] = file_secret
    sdk_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
    if sdk_secret and not os.getenv("LAKEBASE_DATABASE_CLIENT_SECRET"):
        os.environ["LAKEBASE_DATABASE_CLIENT_SECRET"] = sdk_secret


apply_local_env()

PROJECT = os.getenv("LAKEBASE_PROJECT", DEFAULT_PROJECT)
BRANCH = os.getenv("LAKEBASE_BRANCH", DEFAULT_BRANCH)
DATABASE = os.getenv("PGDATABASE", os.getenv("LAKEBASE_DATABASE", "databricks_postgres"))
ENDPOINT = os.getenv("LAKEBASE_ENDPOINT") or (
    f"projects/{PROJECT}/branches/{BRANCH}/endpoints/primary"
)
CDF_CONFIG = os.getenv("LAKEBASE_CDF_CONFIG") or (
    f"projects/{PROJECT}/branches/{BRANCH}/databases/databricks-postgres/cdf-configs/supply_intel"
)
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
LAKEHOUSE_CATALOG = os.getenv("LAKEHOUSE_CATALOG", "")
LAKEHOUSE_CDF_SCHEMA = os.getenv("LAKEHOUSE_CDF_SCHEMA", "decision-history")
DATABRICKS_PROFILE = os.getenv("DATABRICKS_PROFILE") or os.getenv("DATABRICKS_CONFIG_PROFILE") or ""
MOCK_LAKEBASE_HOST = os.getenv(
    "LAKEBASE_MOCK_HOST", "ep-mock.database.cloud.databricks.com"
)
DEFAULT_IDENTITY_EMAIL = os.getenv("DEFAULT_IDENTITY_EMAIL", "admin@apexhealth.org")
DEFAULT_IDENTITY_NAME = os.getenv("DEFAULT_IDENTITY_NAME", "Materials Director")
DEMO_ADMIN_EMAILS = "admin@apexhealth.org,materials.mgr@apexhealth.org"


def uses_m2m() -> bool:
    return bool(os.getenv("DATABRICKS_CLIENT_ID") and os.getenv("DATABRICKS_CLIENT_SECRET"))


def agent_client_id() -> str:
    return (os.getenv("LAKEBASE_AGENT_CLIENT_ID") or os.getenv("DATABRICKS_AGENT_CLIENT_ID") or "").strip()


def agent_client_secret() -> str:
    return (os.getenv("LAKEBASE_AGENT_CLIENT_SECRET") or os.getenv("DATABRICKS_AGENT_CLIENT_SECRET") or "").strip()


def uses_agent_m2m() -> bool:
    return bool(agent_client_id() and agent_client_secret())


def platform_admin_emails() -> set[str]:
    raw = os.getenv("PLATFORM_ADMIN_EMAILS", DEMO_ADMIN_EMAILS)
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def mock_postgres_host(branch_id: str | None = None) -> str:
    if branch_id:
        return f"ep-{branch_id[:12]}.{MOCK_LAKEBASE_HOST.split('.', 1)[-1]}"
    return MOCK_LAKEBASE_HOST


def mock_connection(host: str | None = None) -> dict[str, str | int]:
    resolved = host or MOCK_LAKEBASE_HOST
    return {
        "host": resolved,
        "port": 5432,
        "database": DATABASE,
        "schema": "supply_intel",
        "connection_string": (
            f"postgresql://<user>:<token>@{resolved}:5432/{DATABASE}?sslmode=require"
        ),
    }


def workspace_client():
    from databricks.sdk import WorkspaceClient

    if DATABRICKS_PROFILE:
        return WorkspaceClient(profile=DATABRICKS_PROFILE)
    return WorkspaceClient()


def agent_workspace_client():
    """Workspace client for the dedicated agent SP. Never falls back to the app identity."""
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.core import Config

    client_id = agent_client_id()
    client_secret = agent_client_secret()
    if not (client_id and client_secret):
        return None
    host = os.getenv("DATABRICKS_HOST") or ""
    return WorkspaceClient(
        config=Config(
            host=host or None,
            client_id=client_id,
            client_secret=client_secret,
            auth_type="oauth-m2m",
        )
    )
