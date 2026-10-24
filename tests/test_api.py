import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import store


@pytest.fixture(autouse=True)
def setup_mock_store():
    store.mock = True
    yield


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["schema"] == "supply_intel"


def test_whoami_endpoint():
    client = TestClient(app)
    response = client.get("/api/whoami")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "role" in data


def test_dashboard_endpoint():
    client = TestClient(app)
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert len(data["kpis"]) == 4
    assert "ltap_telemetry" in data


def test_risk_scores_endpoint():
    client = TestClient(app)
    response = client.get("/api/risk-scores")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 30
    assert items[0]["risk_tier"] == "critical"

    # Filter by category
    resp_ph = client.get("/api/risk-scores?category=Pharmacy")
    assert resp_ph.status_code == 200
    for item in resp_ph.json():
        assert item["item_category"] == "Pharmacy"


def test_recommended_orders_and_decision():
    client = TestClient(app)
    response = client.get("/api/recommended-orders")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) > 0
    keys = {(o["item_id"], o["facility_id"]) for o in orders}
    assert len(keys) == len(orders)

    # Record decision
    order_id = orders[0]["recommendation_id"]
    dec_resp = client.post(
        f"/api/recommended-orders/{order_id}/decision",
        json={
            "recommendation_id": order_id,
            "decision": "approved",
            "decision_reason": "Approved for emergency OR restock",
        },
    )
    assert dec_resp.status_code == 200
    assert dec_resp.json()["status"] == "success"

    comment_resp = client.patch(
        f"/api/recommended-orders/{order_id}/comments",
        json={"comments": "Hold for weekend OR volume"},
    )
    assert comment_resp.status_code == 200
    assert comment_resp.json()["comments"] == "Hold for weekend OR volume"
    saved = client.get("/api/recommended-orders").json()
    stored = next(o for o in saved if o["recommendation_id"] == order_id)
    assert stored["comments"] == "Hold for weekend OR volume"


def test_substitutions_and_selection():
    client = TestClient(app)
    response = client.get("/api/substitutions")
    assert response.status_code == 200
    subs = response.json()
    assert len(subs) > 0

    sub_id = subs[0]["substitution_id"]
    sel_resp = client.post(
        "/api/substitutions/select",
        json={
            "substitution_id": sub_id,
            "shortage_item_id": subs[0]["shortage_item_id"],
            "selected_alternative_id": subs[0]["alternative_item_id"],
            "clinical_notes": "Pharmacist reviewed creatinine clearance. Approved.",
        },
    )
    assert sel_resp.status_code == 200
    assert sel_resp.json()["status"] == "success"


def test_recalls_and_action():
    client = TestClient(app)
    response = client.get("/api/recalls")
    assert response.status_code == 200
    recalls = response.json()
    assert len(recalls) > 0

    recall_id = recalls[0]["recall_id"]
    act_resp = client.post(
        f"/api/recalls/{recall_id}/action",
        json={
            "recall_id": recall_id,
            "action_type": "quarantined",
            "notes": "Lot isolated in Central Biomedical quarantine room.",
        },
    )
    assert act_resp.status_code == 200
    assert act_resp.json()["status"] == "success"


def test_transfers_and_confirm():
    client = TestClient(app)
    response = client.get("/api/transfers")
    assert response.status_code == 200
    transfers = response.json()
    assert len(transfers) > 0

    transfer_id = transfers[0]["transfer_id"]
    conf_resp = client.post(
        f"/api/transfers/{transfer_id}/confirm",
        json={
            "transfer_id": transfer_id,
            "decision": "approved",
            "actual_qty": 150,
            "notes": "Dispatched via medical courier van #4",
        },
    )
    assert conf_resp.status_code == 200
    assert conf_resp.json()["status"] == "success"


def test_platform_compute_snapshot():
    client = TestClient(app)
    response = client.get("/api/platform/compute")
    assert response.status_code == 200
    data = response.json()
    assert data["current_cu"] >= 1
    assert data["state"] == "ACTIVE"
    assert "active_queries" in data
    assert "transactions_committed" in data
    assert "transactions_per_second" in data
    assert "connection_utilization_pct" in data
    assert data["observed_at"]


def test_ltap_status_uses_live_counts():
    client = TestClient(app)
    response = client.get("/api/ltap-status")
    assert response.status_code == 200
    data = response.json()
    assert data["synced_tables"]
    assert data["stages"]["planning"]["records"] >= 1
    assert "observed_at" in data
    assert any(row["lakebase_target"] == "supply_intel.risk_scores" for row in data["synced_tables"])
    assert any(row["lakebase_target"] == "supply_intel.inventory_snapshot" for row in data["synced_tables"])
    assert data["edges"][0]["label"]
    assert any(row["lakebase_table"] == "supply_intel.recall_actions" for row in data["lakebase_to_delta_cdf"])
    assert data["edges"][1]["healthy"] is False
    assert "CDC not configured" in data["stages"]["feedback"]["detail"]


def test_ltap_payload_turns_decision_events_green_when_cdf_streams():
    from backend.main import _ltap_payload

    metrics = {
        "risk_count": 1,
        "order_count": 1,
        "sub_count": 1,
        "recall_count": 1,
        "transfer_count": 1,
        "inventory_count": 1,
        "decision_count": 2,
        "sub_hist_count": 1,
        "recall_hist_count": 4,
    }
    payload = _ltap_payload(
        metrics,
        None,
        {"state": "ACTIVE", "connections": 3, "current_cu": 1},
        live=True,
        cdf_status={
            "order_decisions": {"status": "STREAMING", "uc_table": "cat.s.lb_order_decisions_history"},
            "substitution_selections": {"status": "CDF_STATE_STREAMING"},
            "recall_actions": {"status": "STREAMING"},
        },
    )
    assert payload["edges"][1]["healthy"] is True
    assert payload["stages"]["feedback"]["status"] == "healthy"
    assert "CDC not configured" not in payload["stages"]["feedback"]["detail"]
    assert payload["architecture"]["reverse_sync"] == "Lakebase CDF (wal2delta)"


def test_relative_age_handles_plain_dates():
    from datetime import date
    from backend.main import relative_age

    label = relative_age(date(2020, 1, 15))
    assert "ago" in label


def test_catalog_similar_search():
    client = TestClient(app)
    response = client.get("/api/catalog/similar", params={"q": "cefazolin surgical prophylaxis"})
    assert response.status_code == 200
    data = response.json()
    assert data["matches"]
    assert "similarity" in data["matches"][0]

    by_item = client.get("/api/catalog/similar", params={"item_id": "SKU-PH-101"})
    assert by_item.status_code == 200
    assert by_item.json()["matches"]


def test_simulate_inventory():
    client = TestClient(app)
    before = store.data["risk_items"][0]["current_on_hand"]
    response = client.post("/api/simulate/inventory")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert store.data["risk_items"][0]["current_on_hand"] <= before


def test_platform_admin_overview_and_branches():
    client = TestClient(app)
    response = client.get("/api/platform/overview")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "branches" in data
    assert "features" in data

    # Create feature branch
    branch_resp = client.post(
        "/api/platform/branches",
        json={
            "branch_id": "test-feature-branch",
            "parent": "production",
            "ttl_seconds": 86400,
        },
    )
    assert branch_resp.status_code == 201
    assert branch_resp.json()["id"] == "test-feature-branch"

    # Delete feature branch
    del_resp = client.delete("/api/platform/branches/test-feature-branch")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"


def test_substitution_branch_simulation_workflow():
    client = TestClient(app)
    subs = client.get("/api/substitutions").json()
    target = next(s for s in subs if s["shortage_item_id"] == "SKU-PH-101" and s["alternative_item_id"] == "SKU-PH-ALT-02")

    sim = client.post(
        "/api/substitutions/simulate",
        json={
            "substitution_id": target["substitution_id"],
            "shortage_item_id": target["shortage_item_id"],
            "alternative_item_id": target["alternative_item_id"],
            "shortage_item_description": target["shortage_item_description"],
            "alternative_item_description": target["alternative_item_description"],
        },
    )
    assert sim.status_code == 200
    payload = sim.json()
    assert payload["status"] == "presented"
    assert payload["branch_id"].startswith("sim-")
    assert payload["impact"]["patients_affected"] >= 200
    assert len(payload["steps"]) == 5
    assert payload["steps"][0]["id"] == "branch"
    assert payload["steps"][2]["id"] == "investigate"

    delayed = [f["facility_id"] for f in payload["impact"]["facilities"] if f["lead_time_delta_days"] == 0]
    modified = client.post(
        f"/api/substitutions/simulate/{payload['simulation_id']}/decide",
        json={"decision": "modified", "facility_ids": delayed},
    )
    assert modified.status_code == 200
    replay = modified.json()
    assert replay["branch_id"] == payload["branch_id"]
    assert all(f["lead_time_delta_days"] == 0 for f in replay["impact"]["facilities"])

    approved = client.post(
        f"/api/substitutions/simulate/{replay['simulation_id']}/decide",
        json={"decision": "approved"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    shipped = client.post(
        f"/api/substitutions/simulate/{replay['simulation_id']}/replay"
    )
    assert shipped.status_code == 200
    assert shipped.json()["status"] == "shipped"

    again = client.post(
        "/api/substitutions/simulate",
        json={
            "substitution_id": target["substitution_id"],
            "shortage_item_id": target["shortage_item_id"],
            "alternative_item_id": target["alternative_item_id"],
        },
    )
    discarded = client.post(
        f"/api/substitutions/simulate/{again.json()['simulation_id']}/decide",
        json={"decision": "rejected"},
    )
    assert discarded.status_code == 200
    assert discarded.json()["status"] == "discarded"


def test_substitution_agent_role_is_only_on_sim_branch(monkeypatch):
    monkeypatch.setenv("LAKEBASE_AGENT_CLIENT_ID", "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "11111111-2222-3333-4444-555555555555")
    client = TestClient(app)
    before = {row["id"]: list(row.get("roles") or []) for row in client.get("/api/platform/branches").json()}
    sim = client.post(
        "/api/substitutions/simulate",
        json={"prompt": "Simulate switching Lisinopril 10mg to Losartan 50mg across all facilities"},
    )
    assert sim.status_code == 200
    payload = sim.json()
    branch_id = payload["branch_id"]
    assert branch_id.startswith("sim-")
    assert payload["steps"][1]["id"] == "connect"
    assert "granted on" in payload["steps"][1]["detail"]
    assert "production" not in payload["steps"][1]["detail"].split("granted on", 1)[1].split("only")[0]
    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" in payload["steps"][1]["detail"]
    assert "11111111-2222-3333-4444-555555555555" not in payload["steps"][1]["detail"]

    branches = {row["id"]: row for row in client.get("/api/platform/branches").json()}
    production_roles = branches["production"].get("roles") or []
    sim_roles = branches[branch_id].get("roles") or []
    assert production_roles == before.get("production", [])
    assert not any(role.get("purpose") == "agent" for role in production_roles)
    assert any(
        role.get("purpose") == "agent"
        and role.get("branch_id") == branch_id
        and role.get("identity") == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        for role in sim_roles
    )
    assert client.get(f"/api/platform/branches/{branch_id}/roles").json() == sim_roles
    assert client.get("/api/platform/branches/production/roles").json() == production_roles


def test_agentic_lisinopril_simulation_from_prompt():
    client = TestClient(app)
    sim = client.post(
        "/api/substitutions/simulate",
        json={"prompt": "Simulate switching Lisinopril 10mg to Losartan 50mg across all facilities"},
    )
    assert sim.status_code == 200
    payload = sim.json()
    impact = payload["impact"]
    agent = impact["agent"]
    assert impact["shortage_item_id"] == "SKU-PH-112"
    assert impact["alternative_item_id"] == "SKU-PH-ALT-20"
    assert impact["patients_affected"] == 1847
    assert agent["knowledge"]["class_switch"] is True
    keys = {cat["key"] for cat in agent["categories"]}
    assert keys >= {"A", "B", "C", "D", "E", "F"}
    assert any("P&T" in note or "class switch" in note.lower() for note in agent["unexpected"])
    assert impact["monthly_cost_delta"] < impact["naive_monthly_cost_delta"]
    assert impact["naive_monthly_cost_delta"] == 52000
    assert any(turn["phase"] == "Investigate" for turn in agent["transcript"])
    assert "angioedema" in agent["report_markdown"].lower()
    assert "inventory_cover" in agent["investigations"]
    assert any("formulary" in (turn.get("tool") or "") or "inventory" in (turn.get("tool") or "") or "cohort" in (turn.get("tool") or "") for turn in agent["transcript"])
    assert len(agent["transcript"]) >= 8
    tools = [turn.get("tool") or "" for turn in agent["transcript"]]
    assert any(tool == "branch_sql:formulary_update" for tool in tools)
    assert any(tool == "branch_sql:formulary_readback" for tool in tools)
    assert any(tool == "branch_sql:census_update_readback" for tool in tools)
    assert any(tool == "branch_sql:allocations_write_read_correct" for tool in tools)
    assert impact.get("sandbox", {}).get("passes")


def test_decision_insights_endpoint():
    client = TestClient(app)
    response = client.get("/api/decision-insights")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] in {"mock", "lakebase", "cdf"}
    assert len(data["kpis"]) == 4
    assert "by_family" in data
    assert "recent" in data
