"""Create Unity Catalog gold/analytics tables from live Lakebase data."""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from typing import Any

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import VolumeType
from databricks.sdk.service.sql import StatementState
from psycopg.rows import dict_row

PROFILE = os.getenv("DATABRICKS_PROFILE") or os.getenv("DATABRICKS_CONFIG_PROFILE") or ""
CATALOG = os.getenv("LAKEHOUSE_CATALOG", "")
GOLD_SCHEMA = "gold"
ANALYTICS_SCHEMA = "analytics"
VOLUME = "landing"
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
ENDPOINT = os.getenv(
    "LAKEBASE_ENDPOINT",
    "projects/supply-intelligence/branches/production/endpoints/primary",
)
DATABASE = os.getenv("PGDATABASE", os.getenv("LAKEBASE_DATABASE", "databricks_postgres"))

GOLD_TABLES = {
    "supply_risk_scores": "SELECT * FROM supply_intel.risk_scores",
    "recommended_orders": "SELECT * FROM supply_intel.recommended_orders",
    "substitution_candidates": "SELECT * FROM supply_intel.substitution_candidates",
    "recall_exposure": "SELECT * FROM supply_intel.recall_items",
    "transfer_recommendations": "SELECT * FROM supply_intel.transfer_recommendations",
}

ANALYTICS_TABLES = {
    "order_decision_history": "SELECT * FROM supply_intel.order_decisions",
    "substitution_history": "SELECT * FROM supply_intel.substitution_selections",
    "recall_response_history": "SELECT * FROM supply_intel.recall_actions",
}


def json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    raise TypeError(f"Unsupported type: {type(value)}")


def wait_sql(w: WorkspaceClient, statement: str) -> None:
    result = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=statement,
        wait_timeout="50s",
    )
    state = result.status.state if result.status else None
    if state != StatementState.SUCCEEDED:
        error = result.status.error if result.status else None
        raise RuntimeError(f"SQL failed ({state}): {error}\n{statement}")


def ensure_namespace(w: WorkspaceClient) -> str:
    for schema in (GOLD_SCHEMA, ANALYTICS_SCHEMA):
        try:
            w.schemas.get(full_name=f"{CATALOG}.{schema}")
        except Exception:
            w.schemas.create(
                name=schema,
                catalog_name=CATALOG,
                comment="Apex Healthcare Supply Intelligence lakehouse layer",
            )
    volume_name = f"{CATALOG}.{GOLD_SCHEMA}.{VOLUME}"
    try:
        w.volumes.read(name=volume_name)
    except Exception:
        w.volumes.create(
            catalog_name=CATALOG,
            schema_name=GOLD_SCHEMA,
            name=VOLUME,
            volume_type=VolumeType.MANAGED,
            comment="Landing files for gold table bootstrap",
        )
    return f"/Volumes/{CATALOG}/{GOLD_SCHEMA}/{VOLUME}"


def connect_postgres(w: WorkspaceClient) -> psycopg.Connection:
    endpoint = w.postgres.get_endpoint(name=ENDPOINT)
    host = endpoint.status.hosts.host
    token = w.postgres.generate_database_credential(endpoint=ENDPOINT).token
    user = w.current_user.me().user_name
    return psycopg.connect(
        host=host,
        dbname=DATABASE,
        user=user,
        password=token,
        sslmode="require",
        connect_timeout=15,
        row_factory=dict_row,
    )


def serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, dict):
            out[key] = json.dumps(value)
        else:
            out[key] = value
    return out


def write_ndjson(w: WorkspaceClient, volume_root: str, table: str, rows: list[dict[str, Any]]) -> str:
    payload = "\n".join(json.dumps(serialize_row(row), default=json_default) for row in rows)
    if not payload:
        payload = ""
    path = f"{volume_root}/{table}.json"
    w.files.upload(path, BytesIO(payload.encode("utf-8")), overwrite=True)
    return path


EMPTY_SCHEMAS = {
    "order_decision_history": """
        decision_id BIGINT,
        recommendation_id BIGINT,
        decision STRING,
        modified_qty INT,
        modified_supplier_id STRING,
        decision_reason STRING,
        decided_by STRING,
        decided_at TIMESTAMP
    """,
    "substitution_history": """
        selection_id BIGINT,
        substitution_id BIGINT,
        shortage_item_id STRING,
        selected_alternative_id STRING,
        clinical_notes STRING,
        selected_by STRING,
        selected_at TIMESTAMP
    """,
    "recall_response_history": """
        action_id BIGINT,
        recall_id BIGINT,
        action_type STRING,
        notes STRING,
        performed_by STRING,
        performed_at TIMESTAMP
    """,
}


def create_delta_table(
    w: WorkspaceClient, full_name: str, volume_path: str, rows: list[dict[str, Any]], table: str
) -> None:
    if rows:
        wait_sql(
            w,
            f"""
            CREATE OR REPLACE TABLE {full_name}
            USING DELTA
            TBLPROPERTIES (delta.enableChangeDataFeed = true)
            AS SELECT * FROM json.`{volume_path}`
            """,
        )
        return

    schema = EMPTY_SCHEMAS[table]
    wait_sql(
        w,
        f"""
        CREATE OR REPLACE TABLE {full_name} (
            {schema}
        )
        USING DELTA
        TBLPROPERTIES (delta.enableChangeDataFeed = true)
        """,
    )


def main() -> None:
    if not CATALOG or not WAREHOUSE_ID:
        raise SystemExit("Set LAKEHOUSE_CATALOG and DATABRICKS_WAREHOUSE_ID before running bootstrap.")
    w = WorkspaceClient(profile=PROFILE) if PROFILE else WorkspaceClient()
    volume_root = ensure_namespace(w)
    with connect_postgres(w) as conn:
        with conn.cursor() as cur:
            for table, query in GOLD_TABLES.items():
                cur.execute(query)
                rows = list(cur.fetchall())
                path = write_ndjson(w, volume_root, table, rows)
                full_name = f"{CATALOG}.{GOLD_SCHEMA}.{table}"
                create_delta_table(w, full_name, path, rows, table)
                print(f"{full_name}: {len(rows)} rows")

            for table, query in ANALYTICS_TABLES.items():
                cur.execute(query)
                rows = list(cur.fetchall())
                path = write_ndjson(w, volume_root, table, rows)
                full_name = f"{CATALOG}.{ANALYTICS_SCHEMA}.{table}"
                create_delta_table(w, full_name, path, rows, table)
                print(f"{full_name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
