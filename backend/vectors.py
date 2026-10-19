from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from backend.database import json_safe, store

VECTOR_DIM = 1536


def hashed_embedding(text: str, dim: int = VECTOR_DIM) -> list[float]:
    vec = [0.0] * dim
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    if not tokens:
        tokens = ["empty"]
    for i, tok in enumerate(tokens):
        digest = hashlib.sha256(f"{tok}:{i}".encode()).digest()
        for j in range(0, 32, 4):
            idx = int.from_bytes(digest[j : j + 2], "big") % dim
            sign = 1.0 if digest[j + 2] % 2 == 0 else -1.0
            vec[idx] += sign / (1.0 + i)
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    dot = sum(a[i] * b[i] for i in range(n))
    na = math.sqrt(sum(a[i] * a[i] for i in range(n))) or 1.0
    nb = math.sqrt(sum(b[i] * b[i] for i in range(n))) or 1.0
    return max(0.0, min(1.0, dot / (na * nb)))


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


async def embeddings_mode() -> str:
    if store.mock:
        return "memory"
    cols = await store.fetch(
        """
        SELECT column_name, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'supply_intel' AND table_name = 'item_embeddings'
        """
    )
    names = {row["column_name"]: row["udt_name"] for row in cols}
    if names.get("embedding") == "vector":
        return "pgvector"
    if "embedding_json" in names:
        return "json"
    return "missing"


async def catalog_rows() -> list[dict[str, Any]]:
    if store.mock:
        return [
            {
                "item_id": item["item_id"],
                "item_description": item["item_description"],
                "item_category": item["item_category"],
            }
            for item in store.data["risk_items"]
        ]
    return await store.fetch(
        "SELECT item_id, item_description, item_category FROM supply_intel.risk_scores ORDER BY item_id"
    )


async def ensure_item_embeddings() -> str:
    mode = await embeddings_mode()
    if mode in {"memory", "missing"}:
        return mode
    existing = await store.fetch("SELECT item_id FROM supply_intel.item_embeddings")
    have = {row["item_id"] for row in existing}
    items = await catalog_rows()
    for item in items:
        if item["item_id"] in have:
            continue
        text = f"{item['item_id']} {item['item_description']} {item['item_category']}"
        vec = hashed_embedding(text)
        if mode == "pgvector":
            await store.execute(
                """
                INSERT INTO supply_intel.item_embeddings (item_id, item_description, category, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (item_id) DO UPDATE
                  SET item_description = EXCLUDED.item_description,
                      category = EXCLUDED.category,
                      embedding = EXCLUDED.embedding
                """,
                (item["item_id"], item["item_description"], item["item_category"], vector_literal(vec)),
            )
        else:
            await store.execute(
                """
                INSERT INTO supply_intel.item_embeddings (item_id, item_description, category, embedding_json)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (item_id) DO UPDATE
                  SET item_description = EXCLUDED.item_description,
                      category = EXCLUDED.category,
                      embedding_json = EXCLUDED.embedding_json
                """,
                (item["item_id"], item["item_description"], item["item_category"], vector_literal(vec)),
            )
    return mode


async def similar_items(query: str, item_id: str | None = None, limit: int = 5) -> dict[str, Any]:
    mode = await ensure_item_embeddings()
    items = await catalog_rows()
    if item_id:
        seed = next((item for item in items if item["item_id"] == item_id), None)
        text = f"{seed['item_id']} {seed['item_description']} {seed['item_category']}" if seed else query
    else:
        text = query
    probe = hashed_embedding(text)

    if mode == "pgvector":
        try:
            literal = vector_literal(probe)
            if item_id:
                rows = await store.fetch(
                    """
                    SELECT item_id, item_description, category,
                           (1 - (embedding <=> %s::vector))::float AS similarity
                    FROM supply_intel.item_embeddings
                    WHERE item_id <> %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (literal, item_id, literal, limit),
                )
            else:
                rows = await store.fetch(
                    """
                    SELECT item_id, item_description, category,
                           (1 - (embedding <=> %s::vector))::float AS similarity
                    FROM supply_intel.item_embeddings
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (literal, literal, limit),
                )
            return {"mode": "pgvector", "query": text, "matches": json_safe(rows)}
        except Exception as exc:
            print(f"pgvector similarity fallback: {exc}")
            mode = "memory"

    scored: list[dict[str, Any]] = []
    if mode == "json":
        stored = await store.fetch(
            "SELECT item_id, item_description, category, embedding_json FROM supply_intel.item_embeddings"
        )
        for row in stored:
            if item_id and row["item_id"] == item_id:
                continue
            raw = row.get("embedding_json") or []
            if isinstance(raw, str):
                raw = [float(x) for x in raw.strip("[]").split(",") if x.strip()]
            scored.append(
                {
                    "item_id": row["item_id"],
                    "item_description": row["item_description"],
                    "category": row["category"],
                    "similarity": round(cosine(probe, [float(x) for x in raw]), 4),
                }
            )
    else:
        for item in items:
            if item_id and item["item_id"] == item_id:
                continue
            other = hashed_embedding(f"{item['item_id']} {item['item_description']} {item['item_category']}")
            scored.append(
                {
                    "item_id": item["item_id"],
                    "item_description": item["item_description"],
                    "category": item["item_category"],
                    "similarity": round(cosine(probe, other), 4),
                }
            )
    scored.sort(key=lambda row: row["similarity"], reverse=True)
    return {"mode": mode, "query": text, "matches": scored[:limit]}
