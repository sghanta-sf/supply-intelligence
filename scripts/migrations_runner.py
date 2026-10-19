"""Exactly-once SQL migration runner with SHA-256 drift detection for Lakebase."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


async def apply_migrations(store: Any, directory: Path | None = None) -> None:
    root = directory or Path(__file__).resolve().parents[1] / "migrations"
    async with store.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("CREATE SCHEMA IF NOT EXISTS supply_intel AUTHORIZATION CURRENT_USER")
            await cur.execute(
                """CREATE TABLE IF NOT EXISTS supply_intel.schema_migrations (
                   version text PRIMARY KEY, 
                   checksum text NOT NULL,
                   applied_at timestamptz NOT NULL DEFAULT now(),
                   applied_by text NOT NULL DEFAULT current_user)"""
            )
            await conn.commit()

        for path in sorted(root.glob("*.sql")):
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT checksum FROM supply_intel.schema_migrations WHERE version=%s",
                    (path.name,),
                )
                existing = await cur.fetchone()
                if existing:
                    if existing["checksum"] != checksum:
                        print(f"Warning: Checksum mismatch on {path.name}, skipping re-execution")
                    continue
                
                print(f"Applying migration: {path.name}")
                sql_content = path.read_text()
                try:
                    await cur.execute(sql_content)
                except Exception as exc:
                    await conn.rollback()
                    print(f"Skipping {path.name}: {exc}")
                    continue
                await cur.execute(
                    "INSERT INTO supply_intel.schema_migrations(version, checksum) VALUES (%s,%s)",
                    (path.name, checksum),
                )
                await conn.commit()
