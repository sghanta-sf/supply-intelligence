# Apex Healthcare Supply Intelligence Platform
### Lakehouse Intelligence + Lakebase Operational Serving + Platform Admin UI

![Platform Architecture](https://img.shields.io/badge/Lakebase-PostgreSQL%2017-087c91?style=for-the-badge&logo=postgresql)
![Databricks Apps](https://img.shields.io/badge/Databricks-Apps%20Deployable-FF3621?style=for-the-badge&logo=databricks)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20uv-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react)

---

## Overview

This repository is a **reference implementation and synthetic demo**, not a production healthcare system. **Apex Healthcare Systems** and all facilities, patients, inventory, orders, and clinical scenarios in the project are fictitious.

The implemented application combines:

1. **Lakebase operational storage**: PostgreSQL migrations, seeded synthetic data, audited writebacks, and an in-memory fallback for local development.
2. **Materials and pharmacist workspace**: A React 18 application for reviewing risk records, purchase recommendations, clinical substitutions, recalls, and transfers.
3. **Clinical substitution agent**: A Databricks Foundation Model endpoint can select investigation steps; deterministic rules are used when model serving is unavailable.
4. **Platform administration demo**: Databricks Postgres SDK calls for branch lifecycle and short-lived database credentials, plus migration tracking.

### Implementation boundary

The broader LTAP diagram is a **target architecture**. This repository does **not** provision ERP/EHR/pharmacy ingestion, ML training pipelines, continuous Lakehouse-to-Lakebase Synced Tables, or a production SLA.

What the code does provide:

- `migrations/` creates the Lakebase schema and loads synthetic demo records.
- `scripts/bootstrap_lakehouse.py` performs an explicit, one-time export from Lakebase into Unity Catalog Delta tables. It is not continuous replication.
- The backend can inspect Lakebase CDF / `wal2delta` and Unity Catalog targets **when they have already been configured in the workspace**. It does not create that reverse-ETL configuration.
- Latency shown by health endpoints is runtime telemetry or mock/demo data, not a benchmark or guaranteed response time.

---

## Business Application Capabilities

### Supply Operations (Materials Manager & Pharmacist)
- **Shortage Risk Command**: Interactive views over 30 seeded risk records with days-of-supply, synthetic risk factors, and 30d/90d demand forecasts.
- **Recommended Purchase Orders**: 100 seeded purchase recommendations. Materials managers can **Approve**, **Modify** (quantities/suppliers), or **Reject** with audit logging directly to Lakebase.
- **Clinical Substitutions & AI Pharmacist**: Pharmacists view clinical alternatives with bioequivalence ratings (`equivalent`, `similar`, `partial`) and formulary availability. An interactive **Databricks Foundation Model (Claude Sonnet 4.6)** agent evaluates dosing conversion, renal adjustment, and pediatric considerations.
- **FDA Recall Response**: Multi-facility exposure tracking for Class I, II, and III recalls, with lot mapping, patient exposure counts, and immediate **Quarantine** and **Patient Tracing** actions.
- **Inter-Facility Transfers**: 20 automated inventory rebalancing recommendations transferring excess stock from the Central Distribution Hub to acute care facilities.

### Optional LTAP integrations

These capabilities require workspace resources configured outside this repository:

- **Lakehouse tables**: The bootstrap script can create snapshot Delta tables from the current Lakebase data.
- **Lakebase CDF**: The UI reports status for configured CDF / `wal2delta` targets; it does not create them.
- **Autoscaling and scale-to-zero**: The UI reads endpoint settings from the Databricks API. Actual behavior depends on the deployed Lakebase endpoint configuration.

### Platform Admin & Branch Lifecycle
- **Database Branching**: Dev and ops teams can request Lakebase branches using the Databricks Postgres SDK. Creation time depends on the workspace and service.
- **Connection Details & Credential Minting**: Generates copyable PostgreSQL connection strings and short-lived (1-hour) OAuth tokens for direct `psql` or local application testing.
- **Role Management**: Grants branch-level permissions to Service Principals and developer identities using native SQL roles.
- **SHA-256 Migration Tracking**: Audits applied migrations from `supply_intel.schema_migrations` with drift detection.
- **GitHub Actions CI/CD**: Demonstrates branch-per-PR automated validation.

---

## Repository Structure

```
supply-intelligence/
├── app.yaml                    # Databricks App runtime specification
├── databricks.yml              # Databricks Asset Bundle (DAB) declaration
├── pyproject.toml              # Python dependencies managed via uv
├── requirements.txt            # Production Python requirements
├── backend/
│   ├── __init__.py
│   ├── database.py             # Dual-mode Lakebase pool + mock fallback
│   ├── main.py                 # FastAPI operational & admin endpoints
│   └── models.py               # Pydantic request & response schemas
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── App.tsx             # Complete React 18 multi-track application
│       ├── main.tsx            # React DOM mounting
│       ├── styles.css          # Design system & responsive layout
│       └── vite-env.d.ts
├── migrations/
│   ├── 001_initial_schema.sql  # Core DDL: risk_scores, orders, recalls, etc.
│   ├── 002_seed_data.sql       # 30 items, 100 POs, 15 alternatives, 3 recalls
│   ├── 003_pgvector_search.sql # Vector catalog embedding table
│   └── 004_expiration_alerts.sql # Demo migration showing branch schema evolution
├── scripts/
│   ├── lakebase_ci.py          # Branch-per-PR validation runner
│   └── migrations_runner.py    # SHA-256 migration runner with drift detection
├── docs/
│   ├── README.md               # Docs index
│   └── agent-architecture.md   # Substitution agent architecture and workflow
├── tests/
│   └── test_api.py             # Automated pytest suite
└── .github/
    └── workflows/              # GitHub Actions CI/CD pipelines
```

---

## Getting started

Prerequisites: Python 3.11+, Node.js 20+, [`uv`](https://docs.astral.sh/uv/), and the [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) authenticated to a workspace that supports Lakebase Autoscaling Postgres.

### 1. Create the Lakebase project

This creates project `supply-intelligence` with a `production` branch and a `databricks_postgres` database. Wait until the command finishes.

```bash
databricks auth login -p <profile>
databricks postgres create-project supply-intelligence -p <profile>
databricks postgres list-branches projects/supply-intelligence -p <profile>
```

Confirm a READY `production` branch before continuing. The app expects endpoint `projects/supply-intelligence/branches/production/endpoints/primary`.

### 2. Configure credentials and apply migrations

```bash
cp .env.example .env
# Set DATABRICKS_HOST and either a CLI profile (DATABRICKS_PROFILE)
# or M2M credentials (DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET).
# Keep LAKEBASE_PROJECT=supply-intelligence and LAKEBASE_BRANCH=production.

uv sync
uv run pytest

# Apply SQL in migrations/ to the production branch
LAKEBASE_PROJECT=projects/supply-intelligence \
LAKEBASE_SOURCE_BRANCH=projects/supply-intelligence/branches/production \
LAKEBASE_DATABASE=databricks_postgres \
uv run python scripts/lakebase_ci.py deploy
```

`lakebase_ci.py` uses the full resource name (`projects/supply-intelligence`). The app `.env` uses the short project id (`supply-intelligence`); both are required as shown.

Starting the backend also runs any unapplied files in `migrations/` on connect. Use the CLI step above if you want the schema seeded before the first app start.

### 3. Run the app

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

Without Lakebase, set `USE_MOCK_BACKEND=true` for an in-memory preview (no Postgres, no branching).

```bash
cd frontend
npm ci
npm run build
```

For local UI against the API, `npm run dev` in `frontend/` proxies `/api` to port 8000.

---

## Databricks Deployment

Deploy via Databricks Asset Bundles. Use your workspace CLI profile (`-p`) and pass the SQL warehouse ID:

```bash
# Validate bundle configuration
databricks bundle validate -p <profile> --var="warehouse_id=<sql-warehouse-id>"

# Deploy bundle (creates app and attaches Lakebase & Model Serving resources)
databricks bundle deploy -p <profile> --var="warehouse_id=<sql-warehouse-id>"

# Run app
databricks bundle run supply_intelligence -p <profile> --var="warehouse_id=<sql-warehouse-id>"
```
