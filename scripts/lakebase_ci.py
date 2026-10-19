"""Branch-per-PR migration validation and production migration CLI for Lakebase."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.postgres import Branch, BranchSpec, Duration

PROJECT = os.environ.get("LAKEBASE_PROJECT", "projects/supply-intelligence")
SOURCE = os.environ.get("LAKEBASE_SOURCE_BRANCH", f"{PROJECT}/branches/production")
DATABASE = os.environ.get("LAKEBASE_DATABASE", "databricks_postgres")


def safe_branch(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "-", value.lower())[:50].strip("-")


def connection(client: WorkspaceClient, endpoint_name: str) -> psycopg.Connection:
    endpoint = client.postgres.get_endpoint(name=endpoint_name)
    token = client.postgres.generate_database_credential(endpoint=endpoint_name).token
    user = os.environ.get("LAKEBASE_PG_USER") or client.current_user.me().user_name
    return psycopg.connect(
        host=endpoint.status.hosts.host,
        dbname=DATABASE,
        user=user,
        password=token,
        sslmode="require",
        autocommit=False,
    )


def apply(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS supply_intel AUTHORIZATION CURRENT_USER")
        cur.execute("""CREATE TABLE IF NOT EXISTS supply_intel.schema_migrations(
          version text PRIMARY KEY, checksum text NOT NULL,
          applied_at timestamptz NOT NULL DEFAULT now(), applied_by text DEFAULT current_user)""")
        conn.commit()
        for path in sorted(Path("migrations").glob("*.sql")):
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            cur.execute(
                "SELECT checksum FROM supply_intel.schema_migrations WHERE version=%s", (path.name,)
            )
            row = cur.fetchone()
            if row:
                if row[0] != checksum:
                    raise RuntimeError(f"Checksum drift detected for {path.name}")
                continue
            cur.execute(path.read_text())
            cur.execute(
                "INSERT INTO supply_intel.schema_migrations(version,checksum) VALUES(%s,%s)",
                (path.name, checksum),
            )
            conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["validate-pr", "deploy", "cleanup"])
    parser.add_argument("--pr", default=os.getenv("PR_NUMBER", "local"))
    args = parser.parse_args()
    client = WorkspaceClient()
    branch_id = safe_branch(f"pr-{args.pr}")
    branch_name = f"{PROJECT}/branches/{branch_id}"
    if args.action == "cleanup":
        client.postgres.delete_branch(name=branch_name).wait()
        return
    if args.action == "validate-pr":
        client.postgres.create_branch(
            parent=PROJECT,
            branch_id=branch_id,
            branch=Branch(spec=BranchSpec(source_branch=SOURCE, ttl=Duration(seconds=172800))),
        ).wait()
        endpoint_name = f"{branch_name}/endpoints/primary"
    else:
        endpoint_name = f"{SOURCE}/endpoints/primary"
    with connection(client, endpoint_name) as conn:
        apply(conn)


if __name__ == "__main__":
    main()
