# Clinical substitution agent: architecture and workflow

The Clinical Substitutions workspace uses an **LLM + tools** agent to simulate a shortage response **without touching production** until a pharmacist approves and applies the plan.

This is decision support. It does not auto-change the live formulary.

## Why this is agentic

A fixed program can only check rules someone coded in advance for every drug pair. The agent:

1. Reads the request and the two drugs’ pharmacologic classes.
2. Chooses **which investigations to run** from what it finds (class switch vs same-class swap).
3. Segments patients into categories that are **not a pre-built template** for every SKU.
4. Corrects dosing and cost **mid-simulation** when indication matters (for example hypertension vs HFrEF).
5. Surfaces **unexpected findings** (P&T flag, pediatric exclusion, titration protocol).

Example: Lisinopril 10 mg → Losartan 50 mg is an **ACE inhibitor → ARB therapeutic interchange**, not a generic substitution. The agent is expected to notice that and expand the workup (angioedema cross-reactivity, eGFR, pediatric label, potassium, indication-based dose).

## Architecture

```
┌─────────────────────────────────────────────────┐
│     Pharmacist / supply chain user              │
│  "Simulate switching Lisinopril to Losartan"    │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│              AGENT (LLM + tools)                 │
│                                                  │
│  Planning loop:                                  │
│  1. Understand the substitution request          │
│  2. Create a Lakebase branch for isolation       │
│  3. Investigate — decide what to check next      │
│  4. Simulate changes on the branch               │
│  5. Synthesize findings + flag surprises         │
│  6. Present recommendation with evidence         │
└──────┬───────────┬──────────┬───────────────────┘
       │           │          │
       ▼           ▼          ▼
   ┌───────┐  ┌────────┐  ┌──────────┐
   │Branch │  │Clinical│  │ External │
   │SQL    │  │rules   │  │ sources  │
   └───────┘  └────────┘  └──────────┘
```

| Tool | Role |
| --- | --- |
| **Branch SQL** | Copy-on-write Lakebase branch (`sim-…`). Census, formulary, and category writes stay off production. |
| **Clinical rules** | Packaged pharmacology (class switch, angioedema cross-reactivity, renal start dose, pediatric label, potassium, HFrEF titration). |
| **External sources** | Foundation Model (`databricks-claude-sonnet-4-6`) plans the investigation set. If the model is unavailable, rule-based planning from drug class is used. |

Production Lakebase is read for landscape and later **apply to live formulary**. All simulated writes go to the `sim-` branch until that apply step.

## Human workflow (UI)

On **Clinical Substitutions**:

1. Ask a clinical question **or** start a simulation (`Simulate switching …` chip / prompt).
2. Agent steps: **Isolate → Connect → Investigate → Simulate → Recommend**.
3. Pharmacist reviews categories, unexpected findings, transcript, and report.
4. **Approve plan** freezes the recommendation; production is still unchanged.
5. **Apply to live formulary** writes the approved change to production and closes the working copy.
6. **Discard** drops the simulation (and branch when live). **Re-simulate selected facilities** reuses the same branch with a facility filter.

Shortage candidate queues (for example Cefazolin / Cefuroxime) are **not** the live formulary. Applying a plan does not by itself remove a pair from the candidate list.

## Runtime loop

```
POST /api/substitutions/simulate
        │
        ├─ resolve SKUs from body or natural-language prompt
        ├─ Isolate: create Lakebase branch sim-{sku}-{id} (2h TTL)
        ├─ Connect: branch host / database
        ├─ Investigate: run_agent()
        │     Understand landscape + drug classes
        │     LLM or rules → investigation IDs
        │     query_patients / clinical_rule per finding
        │     categorize, correct cost, unexpected findings
        ├─ Simulate: compute_plan + write plan onto the branch
        └─ Recommend: status = presented
                │
                ├─ POST …/decide  approved | modified | rejected
                └─ POST …/replay  apply approved plan to production
```

### 1. Understand

- Parse the prompt (`resolve_pair`) or use selected shortage / alternative SKUs.
- `query_patients`: census (Lisinopril demo cohort = **1,847** patients).
- `lookup_drugs`: pharmacologic class. Same class vs **class switch** changes the investigation set.

### 2. Isolate

- Branch id: `sim-{sku}-{hex}` unless the client supplies one.
- Copy-on-write from production. Platform Ops labels these **Agent branches** (`sim-` prefix) vs **Feature branches**.

### 3. Investigate (dynamic)

Investigation IDs the planner may choose:

| ID | Trigger | Typical finding |
| --- | --- | --- |
| `angioedema_cross_reactivity` | ACE-I → ARB | Do not auto-switch; case review |
| `renal_function` | eGFR band / class | Dose-adjust rather than 1:1 mg swap |
| `pediatric_label` | Age band | Losartan labeled ≥ 6 years; younger need another class |
| `potassium_interaction` | Concurrent K+ | Eligible, but monitoring protocol update |
| `indication_dosing` | HTN vs HFrEF / post-MI | 50 mg vs 25 mg start + titration |
| `allergy_to_alternative` | Same-class cephalosporin, etc. | Allergy flags |
| `inventory_cover` | Cover / allocation | Facility days cover and cost |

Planner:

- Live: Foundation Model returns JSON `{ "investigations": [...] }`.
- Mock / model failure: `investigations_for(knowledge)` from class switch.

Each finding is appended to the **transcript** (phase, thought, tool, result).

### 4. Simulate

Patient categories **emerge from findings** (Lisinopril → Losartan):

| Key | Severity | Meaning |
| --- | --- | --- |
| A | ok | Safe to auto-substitute (standard HTN conversion) |
| B | watch | Renal-adjusted start |
| C | stop | Angioedema history — individual review |
| D | stop | Pediatric age exclusion (consider amlodipine) |
| E | info | Potassium monitoring (overlap; still eligible) |
| F | watch | Heart failure / post-MI titration, not a flat 50 mg switch |

On the branch the agent stages formulary / census impact via `compute_plan` and `_write_plan_to_pg`. Cost for Lisinopril uses **indication-based equivalency**, not a naive 1:1 unit-price × all patients (naive ~+$52,000/month vs corrected HTN vs HFrEF trajectory).

### 5. Synthesize and recommend

The payload includes:

- `steps` — Isolate / Connect / Investigate / Simulate / Recommend
- `impact` — facilities, cover, cost, summary
- `impact.agent` — `transcript`, `categories`, `unexpected`, `report_markdown`, `planner`, `investigations`

Unexpected findings typically include: P&T class-switch flag, pediatric patients with no suitable ARB, HFrEF titration, silent angioedema conversion if someone did a 1:1 SKU swap.

## Worked example

**Request:** Simulate switching Lisinopril 10 mg to Losartan 50 mg across all facilities.

| Phase | Agent behavior |
| --- | --- |
| Understand | 1,847 patients; ACE-I vs ARB → class switch |
| Isolate | `sim-ph112-…` from production |
| Investigate | Angioedema, eGFR &lt; 30, age &lt; 6, potassium, HTN vs HFrEF counts |
| Simulate | Categories A–F; write branch; recalc cost after indication split |
| Recommend | Auto-sub vs hold vs alternative consult; corrected monthly cost; Approve / Modify / Discard |

## APIs

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/substitutions/simulate` | Start agent run. Body: SKUs and/or `prompt`. |
| `POST` | `/api/substitutions/simulate/{id}/decide` | `approved` (freeze), `modified` (re-run facilities on same branch), `rejected` (discard). |
| `POST` | `/api/substitutions/simulate/{id}/replay` | Apply **approved** plan to live formulary; close branch. |
| `POST` | `/api/substitutions/agent-query` | Clinical Q&A only (not a branch simulation). |

## Code map

| File | Responsibility |
| --- | --- |
| `backend/sim_agent.py` | Drug knowledge, aliases, cohorts, tools, planner, `run_agent` |
| `backend/substitution_sim.py` | Facility census plan, cover, naive unit-cost model |
| `backend/main.py` | Branch lifecycle, simulate / decide / replay HTTP API |
| `backend/models.py` | `SubstitutionSimulateRequest` (`prompt` optional) |
| `migrations/006_substitution_sim.sql` | Simulation tables |
| `migrations/007_agentic_sim.sql` | `drug_knowledge`, `substitution_patient_cohorts`, categories |
| `frontend/src/App.tsx` | Clinical Substitutions UI: chips, transcript, categories, approve / apply |

## Terminology

| Term | Use in this product |
| --- | --- |
| **Clinical substitution** | Page-level name for shortage alternatives and simulations |
| **Therapeutic interchange** | Different molecule / class under protocol (ACE-I → ARB) |
| **Generic substitution** | Same active ingredient, strength, form, route |
| **Equivalent / similar / partial** | Clinical comparability rating on a candidate, not the workflow name |

## Guardrails

- Simulation is isolated on a `sim-` branch until apply.
- The substitution agent’s Lakebase role is created only on that `sim-` branch. Production keeps the Databricks App identity for the dashboard; the simulation path never grants the agent role there.
- Approve ≠ apply. Production changes only on **Apply to live formulary**.
- Stop-severity cohorts (angioedema, age exclusion) must not be treated as auto-swap.
- Foundation Model output is constrained to known investigation IDs; unknown IDs are dropped.
- Pharmacist review is required before any live formulary change.
