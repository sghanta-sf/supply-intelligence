# Apex Healthcare Supply Intelligence Platform
### Lakehouse Intelligence + Lakebase Operational Serving + Platform Admin UI

![Platform Architecture](https://img.shields.io/badge/Lakebase-PostgreSQL%2017-087c91?style=for-the-badge&logo=postgresql)
![Databricks Apps](https://img.shields.io/badge/Databricks-Apps%20Deployable-FF3621?style=for-the-badge&logo=databricks)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20uv-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react)

---

## Executive Summary

**Apex Healthcare Systems** operates an 8-facility regional health network (including Apex Memorial Hospital, Apex Children's Medical Center, Apex Valley Health, and the Apex Central Distribution Hub). 

Hospital supply chains face catastrophic risk when critical drugs, surgical devices, and consumables experience unpredicted stockouts or sudden FDA recalls. Traditional ERPs report inventory backwards; batch data warehouses refresh too slowly for real-time operating room scheduling.

The **Apex Supply Intelligence Platform** solves this by unifying:
1. **Lakehouse Intelligence (Layer 1)**: Ingests ERP + EHR + Pharmacy feeds into Delta Lake Gold tables, runs ML models to score stockout risk and optimize reorders.
2. **Lakebase Operational Serving (Layer 2)**: Pushes actionable recommendations into Lakebase Autoscaling (PostgreSQL 17) via continuous Synced Tables with &lt; 5ms query response.
3. **Materials & Pharmacist Workspace**: A React 18 application enabling materials managers and pharmacists to approve orders, evaluate clinical substitutions via Databricks Foundation Model AI, and quarantine recalled lots.
4. **Platform Admin UI (Layer 3)**: A dedicated devops console within the app allowing developers to create zero-copy database feature branches in &lt; 1 second, mint ephemeral OAuth credentials, and track migration checksums.

---

## Business Application Capabilities

### Supply Operations (Materials Manager & Pharmacist)
- **Shortage Risk Command**: Real-time visibility into 30 ML-scored shortage items with days-of-supply burn rates, predictive risk factor breakdowns (supplier reliability, lead time variance, port congestion), and 30d/90d demand forecasts.
- **Recommended Purchase Orders**: 100 AI-optimized proposed purchase orders. Materials managers can **Approve**, **Modify** (quantities/suppliers), or **Reject** with audit logging directly to Lakebase.
- **Clinical Substitutions & AI Pharmacist**: Pharmacists view clinical alternatives with bioequivalence ratings (`equivalent`, `similar`, `partial`) and formulary availability. An interactive **Databricks Foundation Model (Claude Sonnet 4.6)** agent evaluates dosing conversion, renal adjustment, and pediatric considerations.
- **FDA Recall Response**: Multi-facility exposure tracking for Class I, II, and III recalls, with lot mapping, patient exposure counts, and immediate **Quarantine** and **Patient Tracing** actions.
- **Inter-Facility Transfers**: 20 automated inventory rebalancing recommendations transferring excess stock from the Central Distribution Hub to acute care facilities.

### LTAP Architecture & Telemetry
- **Synced Tables**: Lakehouse Gold tables continuously replicate to Lakebase operational tables (`supply_intel.risk_scores`, `supply_intel.recommended_orders`, etc.).
- **Change Data Feed (CDF)**: Operational decisions (approvals, substitution notes, quarantine timestamps) written to Lakebase immediately stream back to Delta Lake for BI executive reporting.
- **Autoscaling & Scale-to-Zero**: Managed compute automatically scales from 1.0 CU down to zero during inactive periods to eliminate idle infrastructure cost.

### Platform Admin & Branch Lifecycle
- **Zero-Copy Database Branching**: Dev and ops teams can branch production Lakebase in &lt; 1 second using the Databricks Postgres SDK.
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

## Local Development Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- `uv` (Fast Python package installer)

### 2. Setup & Test Backend
```bash
# Navigate to project
cd git_projects/supply-intelligence

# Install Python dependencies and run tests
uv sync
uv run pytest

# Local Lakebase: copy .env.example to .env (gitignored), then set credentials and LAKEBASE_BRANCH
cp .env.example .env
# Start FastAPI backend (port 8000) — reads .env for SP + branch
uv run uvicorn backend.main:app --reload --port 8000
```

### 3. Setup & Build Frontend
```bash
cd frontend
npm ci
npm run build
```

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
