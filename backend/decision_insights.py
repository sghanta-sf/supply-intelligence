from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from backend.database import json_safe, store


def _day_key(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    text = str(value)
    return text[:10]


def _count_bars(rows: list[dict[str, Any]], key: str, limit: int = 8) -> list[dict[str, Any]]:
    counts = Counter(str(row.get(key) or "unknown") for row in rows)
    total = max(sum(counts.values()), 1)
    return [
        {"label": label, "count": count, "share": round(count / total, 3)}
        for label, count in counts.most_common(limit)
    ]


def build_insights(
    *,
    orders: list[dict[str, Any]],
    substitutions: list[dict[str, Any]],
    recalls: list[dict[str, Any]],
    source: str,
    source_tables: dict[str, str],
    labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    labels = labels or {}
    timeline: dict[str, dict[str, int]] = defaultdict(lambda: {"orders": 0, "substitutions": 0, "recalls": 0})
    for row in orders:
        day = _day_key(row.get("decided_at"))
        if day:
            timeline[day]["orders"] += 1
    for row in substitutions:
        day = _day_key(row.get("selected_at"))
        if day:
            timeline[day]["substitutions"] += 1
    for row in recalls:
        day = _day_key(row.get("performed_at"))
        if day:
            timeline[day]["recalls"] += 1

    recent: list[dict[str, Any]] = []
    for row in orders:
        recent.append(
            {
                "family": "Purchase order",
                "action": row.get("decision") or "decision",
                "actor": row.get("decided_by") or "unknown",
                "occurred_at": row.get("decided_at"),
                "detail": row.get("decision_reason") or f"Recommendation {row.get('recommendation_id')}",
            }
        )
    for row in substitutions:
        shortage = str(row.get("shortage_item_id") or "")
        alt = str(row.get("selected_alternative_id") or "")
        recent.append(
            {
                "family": "Substitution",
                "action": "selected",
                "actor": row.get("selected_by") or "unknown",
                "occurred_at": row.get("selected_at"),
                "detail": f"{labels.get(shortage, shortage)} → {labels.get(alt, alt)}",
            }
        )
    for row in recalls:
        recent.append(
            {
                "family": "Recall response",
                "action": row.get("action_type") or "action",
                "actor": row.get("performed_by") or "unknown",
                "occurred_at": row.get("performed_at"),
                "detail": row.get("notes") or f"Recall {row.get('recall_id')}",
            }
        )
    recent.sort(key=lambda item: str(item.get("occurred_at") or ""), reverse=True)

    sub_pairs = Counter(
        (
            str(row.get("shortage_item_id") or "unknown"),
            str(row.get("selected_alternative_id") or "unknown"),
        )
        for row in substitutions
    )
    substitution_pairs = [
        {
            "shortage_item_id": shortage,
            "shortage_item": labels.get(shortage, shortage),
            "selected_alternative_id": alt,
            "selected_alternative": labels.get(alt, alt),
            "count": count,
        }
        for (shortage, alt), count in sub_pairs.most_common(8)
    ]

    actors = Counter()
    for row in orders:
        actors[str(row.get("decided_by") or "unknown")] += 1
    for row in substitutions:
        actors[str(row.get("selected_by") or "unknown")] += 1
    for row in recalls:
        actors[str(row.get("performed_by") or "unknown")] += 1

    total = len(orders) + len(substitutions) + len(recalls)
    latest = max(
        [str(row.get("decided_at") or "") for row in orders]
        + [str(row.get("selected_at") or "") for row in substitutions]
        + [str(row.get("performed_at") or "") for row in recalls],
        default="",
    )
    source_label = {
        "cdf": "Lakehouse CDF · decision-history",
        "lakebase": "Lakebase operational events",
        "mock": "Local preview data",
    }.get(source, source)

    return json_safe(
        {
            "source": source,
            "source_label": source_label,
            "source_tables": source_tables,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "kpis": [
                {
                    "label": "Operational decisions",
                    "value": total,
                    "subtext": source_label,
                    "trend": f"Latest {latest[:16].replace('T', ' ') or '—'}",
                    "status": "medium",
                },
                {
                    "label": "Order decisions",
                    "value": len(orders),
                    "subtext": "Approve / modify / reject",
                    "trend": f"{_count_bars(orders, 'decision')[0]['label'] if orders else 'none'} most common",
                    "status": "high" if orders else "medium",
                },
                {
                    "label": "Substitution selections",
                    "value": len(substitutions),
                    "subtext": "Shortage alternatives authorized",
                    "trend": f"{len(sub_pairs)} unique pairs",
                    "status": "medium",
                },
                {
                    "label": "Recall actions",
                    "value": len(recalls),
                    "subtext": "Quarantine, trace, close-out",
                    "trend": f"{_count_bars(recalls, 'action_type')[0]['label'] if recalls else 'none'} most common",
                    "status": "critical" if recalls else "medium",
                },
            ],
            "by_family": [
                {"label": "Purchase orders", "count": len(orders)},
                {"label": "Substitutions", "count": len(substitutions)},
                {"label": "Recall responses", "count": len(recalls)},
            ],
            "order_outcomes": _count_bars(orders, "decision"),
            "recall_actions": _count_bars(recalls, "action_type"),
            "substitution_pairs": substitution_pairs,
            "by_actor": [{"label": actor, "count": count} for actor, count in actors.most_common(8)],
            "timeline": [
                {"day": day, **counts}
                for day, counts in sorted(timeline.items())
            ],
            "recent": recent[:25],
        }
    )


def mock_insights() -> dict[str, Any]:
    orders = list(store.data.get("order_decisions") or [])
    substitutions = list(store.data.get("substitution_selections") or [])
    recalls = list(store.data.get("recall_actions") or [])
    if not orders and not substitutions and not recalls:
        orders = [
            {"decision": "approved", "decided_by": "materials.mgr@apexhealth.org", "decided_at": "2026-09-27T01:35:51Z", "recommendation_id": 12, "decision_reason": "Emergency OR restock"},
            {"decision": "approved", "decided_by": "materials.mgr@apexhealth.org", "decided_at": "2026-09-27T01:36:10Z", "recommendation_id": 18, "decision_reason": "GPO contract price"},
            {"decision": "modified", "decided_by": "pharmacy.dir@apexhealth.org", "decided_at": "2026-09-27T12:10:00Z", "recommendation_id": 4, "decision_reason": "Reduced qty for weekend census"},
        ]
        substitutions = [
            {"shortage_item_id": "SKU-PH-101", "selected_alternative_id": "SKU-PH-ALT-02", "selected_by": "pharmacist@apexhealth.org", "selected_at": "2026-09-28T00:15:46Z", "clinical_notes": "Cefuroxime equivalent for prophylaxis"},
            {"shortage_item_id": "SKU-SR-201", "selected_alternative_id": "SKU-SR-ALT-10", "selected_by": "pharmacist@apexhealth.org", "selected_at": "2026-09-27T18:02:00Z"},
        ]
        recalls = [
            {"action_type": "quarantined", "performed_by": "materials.mgr@apexhealth.org", "performed_at": "2026-09-27T01:40:00Z", "recall_id": 1, "notes": "Lot isolated"},
            {"action_type": "traced_patients", "performed_by": "quality.rn@apexhealth.org", "performed_at": "2026-09-27T01:45:22Z", "recall_id": 1, "notes": "Exposure roster generated"},
        ]
    labels = {
        "SKU-PH-101": "Cefazolin 1g IV Vial",
        "SKU-PH-ALT-02": "Cefuroxime 1.5g IV Vial",
        "SKU-SR-201": "14 Fr Hydrophilic Foley Tray",
        "SKU-SR-ALT-10": "16 Fr Silicone Foley Tray",
    }
    return build_insights(
        orders=orders,
        substitutions=substitutions,
        recalls=recalls,
        source="mock",
        source_tables={},
        labels=labels,
    )
