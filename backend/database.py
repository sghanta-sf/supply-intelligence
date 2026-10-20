from __future__ import annotations

import asyncio
import os
import random
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from scripts.migrations_runner import apply_migrations
from backend.settings import (
    DATABASE,
    DEFAULT_IDENTITY_EMAIL,
    DEFAULT_IDENTITY_NAME,
    ENDPOINT,
    mock_connection,
    uses_m2m,
    workspace_client,
)
from backend.substitution_sim import FORMULARY_SEED, MOCK_CENSUS

SCHEMA = "supply_intel"


def _seed_data() -> dict[str, Any]:
    # 30 items with realistic healthcare shortage telemetry
    risk_items = [
        {
            "item_id": "SKU-PH-101",
            "item_description": "Cefazolin 1g IV Vial (Surgical Prophylaxis)",
            "item_category": "Pharmacy",
            "current_on_hand": 42,
            "avg_daily_usage": 28.5,
            "days_of_supply": 1.5,
            "risk_score": 96.4,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.28, "lead_time_variance_days": 18, "port_congestion_index": 0.88, "formulary_spike": "OR scheduling +24%"},
            "forecast_demand_30d": 855,
            "forecast_demand_90d": 2600,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-102",
            "item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "item_category": "Pharmacy",
            "current_on_hand": 65,
            "avg_daily_usage": 34.0,
            "days_of_supply": 1.9,
            "risk_score": 94.8,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.35, "lead_time_variance_days": 21, "port_congestion_index": 0.76, "formulary_spike": "Cardio +18%"},
            "forecast_demand_30d": 1020,
            "forecast_demand_90d": 3100,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-201",
            "item_description": "14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor",
            "item_category": "Surgical",
            "current_on_hand": 18,
            "avg_daily_usage": 12.0,
            "days_of_supply": 1.5,
            "risk_score": 93.2,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.40, "lead_time_variance_days": 14, "port_congestion_index": 0.92, "formulary_spike": "ICU census high"},
            "forecast_demand_30d": 360,
            "forecast_demand_90d": 1100,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-103",
            "item_description": "Propofol 10mg/mL 20mL Diprivan Emulsion",
            "item_category": "Pharmacy",
            "current_on_hand": 55,
            "avg_daily_usage": 30.0,
            "days_of_supply": 1.8,
            "risk_score": 91.5,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.32, "lead_time_variance_days": 16, "port_congestion_index": 0.81, "formulary_spike": "Surgical volume peak"},
            "forecast_demand_30d": 900,
            "forecast_demand_90d": 2750,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-CC-301",
            "item_description": "Endotracheal Tube 7.5mm Cuffed Murphy Eye",
            "item_category": "Critical Care",
            "current_on_hand": 22,
            "avg_daily_usage": 10.5,
            "days_of_supply": 2.1,
            "risk_score": 89.7,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.45, "lead_time_variance_days": 12, "port_congestion_index": 0.74, "formulary_spike": "Respiratory surge"},
            "forecast_demand_30d": 315,
            "forecast_demand_90d": 950,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-104",
            "item_description": "Epinephrine 1mg/mL (1:1000) 1mL Ampul",
            "item_category": "Pharmacy",
            "current_on_hand": 38,
            "avg_daily_usage": 14.0,
            "days_of_supply": 2.7,
            "risk_score": 88.0,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.41, "lead_time_variance_days": 15, "port_congestion_index": 0.65, "formulary_spike": "Crash cart restock cycle"},
            "forecast_demand_30d": 420,
            "forecast_demand_90d": 1260,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-202",
            "item_description": "Surgical Stapler Endopath 45mm Articulating",
            "item_category": "Surgical",
            "current_on_hand": 14,
            "avg_daily_usage": 4.5,
            "days_of_supply": 3.1,
            "risk_score": 86.4,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.50, "lead_time_variance_days": 10, "port_congestion_index": 0.83, "formulary_spike": "Colorectal cases +30%"},
            "forecast_demand_30d": 135,
            "forecast_demand_90d": 410,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-105",
            "item_description": "Sodium Chloride 0.9% IV Infusion 1000mL Bag",
            "item_category": "Pharmacy",
            "current_on_hand": 210,
            "avg_daily_usage": 65.0,
            "days_of_supply": 3.2,
            "risk_score": 85.1,
            "risk_tier": "critical",
            "risk_factors": {"supplier_reliability": 0.48, "lead_time_variance_days": 11, "port_congestion_index": 0.79, "formulary_spike": "System-wide baseline high"},
            "forecast_demand_30d": 1950,
            "forecast_demand_90d": 5900,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-LB-401",
            "item_description": "High-Sensitivity Troponin I Reagent Kit (100 tests)",
            "item_category": "Laboratory",
            "current_on_hand": 8,
            "avg_daily_usage": 2.2,
            "days_of_supply": 3.6,
            "risk_score": 82.3,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.58, "lead_time_variance_days": 9, "port_congestion_index": 0.60, "formulary_spike": "ED chest pain protocol"},
            "forecast_demand_30d": 66,
            "forecast_demand_90d": 200,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-106",
            "item_description": "Nitroglycerin 50mg/250mL in D5W Premix",
            "item_category": "Pharmacy",
            "current_on_hand": 15,
            "avg_daily_usage": 3.8,
            "days_of_supply": 3.9,
            "risk_score": 81.0,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.52, "lead_time_variance_days": 8, "port_congestion_index": 0.62, "formulary_spike": "Cath lab demand"},
            "forecast_demand_30d": 114,
            "forecast_demand_90d": 350,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-203",
            "item_description": "Titanium Hemostatic Clips Small 6-clip Cartridge",
            "item_category": "Surgical",
            "current_on_hand": 45,
            "avg_daily_usage": 11.0,
            "days_of_supply": 4.1,
            "risk_score": 79.5,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.61, "lead_time_variance_days": 7, "port_congestion_index": 0.58, "formulary_spike": "Vascular cases stable"},
            "forecast_demand_30d": 330,
            "forecast_demand_90d": 1000,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-CC-302",
            "item_description": "Central Venous Catheter Triple Lumen 7 Fr 20cm",
            "item_category": "Critical Care",
            "current_on_hand": 28,
            "avg_daily_usage": 6.0,
            "days_of_supply": 4.6,
            "risk_score": 78.2,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.55, "lead_time_variance_days": 8, "port_congestion_index": 0.69, "formulary_spike": "ICU line placement trend"},
            "forecast_demand_30d": 180,
            "forecast_demand_90d": 550,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-107",
            "item_description": "Albuterol Sulfate Inhalation Solution 2.5mg/3mL",
            "item_category": "Pharmacy",
            "current_on_hand": 140,
            "avg_daily_usage": 28.0,
            "days_of_supply": 5.0,
            "risk_score": 76.8,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.63, "lead_time_variance_days": 6, "port_congestion_index": 0.51, "formulary_spike": "Seasonal pediatric asthma"},
            "forecast_demand_30d": 840,
            "forecast_demand_90d": 2550,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-GM-501",
            "item_description": "Nitrile Exam Gloves Powder-Free Medium (Box 200)",
            "item_category": "General Medical",
            "current_on_hand": 320,
            "avg_daily_usage": 60.0,
            "days_of_supply": 5.3,
            "risk_score": 75.4,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.65, "lead_time_variance_days": 7, "port_congestion_index": 0.68, "formulary_spike": "Inpatient baseline"},
            "forecast_demand_30d": 1800,
            "forecast_demand_90d": 5400,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-204",
            "item_description": "Monocryl 3-0 Suture PS-1 Needle 27 inch Undyed",
            "item_category": "Surgical",
            "current_on_hand": 50,
            "avg_daily_usage": 9.0,
            "days_of_supply": 5.5,
            "risk_score": 74.0,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.68, "lead_time_variance_days": 6, "port_congestion_index": 0.54, "formulary_spike": "Plastics and ortho cases"},
            "forecast_demand_30d": 270,
            "forecast_demand_90d": 820,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-108",
            "item_description": "Dextrose 50% Injection 25g/50mL Bristoject Syringe",
            "item_category": "Pharmacy",
            "current_on_hand": 30,
            "avg_daily_usage": 5.2,
            "days_of_supply": 5.7,
            "risk_score": 72.5,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.60, "lead_time_variance_days": 7, "port_congestion_index": 0.49, "formulary_spike": "Hypoglycemia protocol"},
            "forecast_demand_30d": 156,
            "forecast_demand_90d": 480,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-LB-402",
            "item_description": "Blood Gas Capillary Tubes Heparinized (Pack 250)",
            "item_category": "Laboratory",
            "current_on_hand": 12,
            "avg_daily_usage": 2.0,
            "days_of_supply": 6.0,
            "risk_score": 71.0,
            "risk_tier": "high",
            "risk_factors": {"supplier_reliability": 0.64, "lead_time_variance_days": 5, "port_congestion_index": 0.52, "formulary_spike": "NICU usage steady"},
            "forecast_demand_30d": 60,
            "forecast_demand_90d": 185,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-CC-303",
            "item_description": "Arterial Line Insertion Kit 20G 12cm Radial",
            "item_category": "Critical Care",
            "current_on_hand": 42,
            "avg_daily_usage": 6.5,
            "days_of_supply": 6.4,
            "risk_score": 66.8,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.70, "lead_time_variance_days": 5, "port_congestion_index": 0.44, "formulary_spike": "Cardiac surgical schedule"},
            "forecast_demand_30d": 195,
            "forecast_demand_90d": 600,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-205",
            "item_description": "Electrosurgical Pencil Rocker Switch w/ Holster",
            "item_category": "Surgical",
            "current_on_hand": 85,
            "avg_daily_usage": 12.0,
            "days_of_supply": 7.0,
            "risk_score": 64.2,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.72, "lead_time_variance_days": 4, "port_congestion_index": 0.41, "formulary_spike": "Main OR rotation"},
            "forecast_demand_30d": 360,
            "forecast_demand_90d": 1100,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-109",
            "item_description": "Vancomycin HCl 1.25g Pharmacy Bulk Package",
            "item_category": "Pharmacy",
            "current_on_hand": 70,
            "avg_daily_usage": 9.5,
            "days_of_supply": 7.3,
            "risk_score": 62.5,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.75, "lead_time_variance_days": 4, "port_congestion_index": 0.38, "formulary_spike": "Antimicrobial stewardship"},
            "forecast_demand_30d": 285,
            "forecast_demand_90d": 870,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-GM-502",
            "item_description": "ChloraPrep One-Step 26mL Applicator Hi-Lite Orange",
            "item_category": "General Medical",
            "current_on_hand": 110,
            "avg_daily_usage": 14.5,
            "days_of_supply": 7.5,
            "risk_score": 60.1,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.77, "lead_time_variance_days": 4, "port_congestion_index": 0.35, "formulary_spike": "Pre-op skin prep standard"},
            "forecast_demand_30d": 435,
            "forecast_demand_90d": 1320,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-LB-403",
            "item_description": "Vacutainer SST Plus Blood Collection Tubes Gold",
            "item_category": "Laboratory",
            "current_on_hand": 450,
            "avg_daily_usage": 58.0,
            "days_of_supply": 7.7,
            "risk_score": 58.4,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.79, "lead_time_variance_days": 3, "port_congestion_index": 0.32, "formulary_spike": "Outpatient draw volume"},
            "forecast_demand_30d": 1740,
            "forecast_demand_90d": 5300,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-110",
            "item_description": "Ondansetron 4mg/2mL Multi-Dose Vial",
            "item_category": "Pharmacy",
            "current_on_hand": 130,
            "avg_daily_usage": 16.0,
            "days_of_supply": 8.1,
            "risk_score": 55.7,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.81, "lead_time_variance_days": 3, "port_congestion_index": 0.30, "formulary_spike": "Post-op PACU standard"},
            "forecast_demand_30d": 480,
            "forecast_demand_90d": 1450,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-CC-304",
            "item_description": "Closed Suction Catheter 14 Fr T-Piece Ventilator",
            "item_category": "Critical Care",
            "current_on_hand": 54,
            "avg_daily_usage": 6.2,
            "days_of_supply": 8.7,
            "risk_score": 53.0,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.82, "lead_time_variance_days": 3, "port_congestion_index": 0.28, "formulary_spike": "VAP prevention bundle"},
            "forecast_demand_30d": 186,
            "forecast_demand_90d": 570,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-206",
            "item_description": "Surgical Skin Stapler 35 Wide Staples",
            "item_category": "Surgical",
            "current_on_hand": 90,
            "avg_daily_usage": 10.0,
            "days_of_supply": 9.0,
            "risk_score": 51.2,
            "risk_tier": "medium",
            "risk_factors": {"supplier_reliability": 0.84, "lead_time_variance_days": 3, "port_congestion_index": 0.26, "formulary_spike": "Wound closure standard"},
            "forecast_demand_30d": 300,
            "forecast_demand_90d": 910,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-GM-503",
            "item_description": "Sterile Gauze Sponges 4x4 12-Ply (Pack 100)",
            "item_category": "General Medical",
            "current_on_hand": 420,
            "avg_daily_usage": 35.0,
            "days_of_supply": 12.0,
            "risk_score": 34.5,
            "risk_tier": "low",
            "risk_factors": {"supplier_reliability": 0.92, "lead_time_variance_days": 2, "port_congestion_index": 0.15, "formulary_spike": "Normal variance"},
            "forecast_demand_30d": 1050,
            "forecast_demand_90d": 3200,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-PH-111",
            "item_description": "Acetaminophen 325mg Oral Tablets (Bottle 1000)",
            "item_category": "Pharmacy",
            "current_on_hand": 85,
            "avg_daily_usage": 4.0,
            "days_of_supply": 21.2,
            "risk_score": 22.0,
            "risk_tier": "low",
            "risk_factors": {"supplier_reliability": 0.95, "lead_time_variance_days": 1, "port_congestion_index": 0.10, "formulary_spike": "Stable floor stock"},
            "forecast_demand_30d": 120,
            "forecast_demand_90d": 365,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-LB-404",
            "item_description": "Urine Specimen Cups Sterile 4oz with Temp Strip",
            "item_category": "Laboratory",
            "current_on_hand": 600,
            "avg_daily_usage": 40.0,
            "days_of_supply": 15.0,
            "risk_score": 28.5,
            "risk_tier": "low",
            "risk_factors": {"supplier_reliability": 0.91, "lead_time_variance_days": 2, "port_congestion_index": 0.12, "formulary_spike": "Standard outpatient usage"},
            "forecast_demand_30d": 1200,
            "forecast_demand_90d": 3600,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-SR-207",
            "item_description": "Suction Tubing Non-Conductive 1/4 inch x 10ft",
            "item_category": "Surgical",
            "current_on_hand": 240,
            "avg_daily_usage": 18.0,
            "days_of_supply": 13.3,
            "risk_score": 31.0,
            "risk_tier": "low",
            "risk_factors": {"supplier_reliability": 0.89, "lead_time_variance_days": 2, "port_congestion_index": 0.18, "formulary_spike": "Standard OR turnover"},
            "forecast_demand_30d": 540,
            "forecast_demand_90d": 1650,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "item_id": "SKU-GM-504",
            "item_description": "Alcohol Prep Pads Sterile Medium (Box 200)",
            "item_category": "General Medical",
            "current_on_hand": 800,
            "avg_daily_usage": 50.0,
            "days_of_supply": 16.0,
            "risk_score": 18.4,
            "risk_tier": "low",
            "risk_factors": {"supplier_reliability": 0.98, "lead_time_variance_days": 1, "port_congestion_index": 0.08, "formulary_spike": "System wide routine"},
            "forecast_demand_30d": 1500,
            "forecast_demand_90d": 4500,
            "last_scored_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    facilities = [
        ("FAC-01", "Apex Memorial Hospital"),
        ("FAC-02", "Apex Children's Medical Center"),
        ("FAC-03", "Apex Valley Health"),
        ("FAC-04", "Apex Ambulatory Surgical"),
        ("FAC-05", "Apex Northgate Clinic"),
        ("FAC-06", "Apex Central Distribution Hub"),
        ("FAC-07", "Apex Westside Specialty"),
        ("FAC-08", "Apex Crestview Rehab")
    ]

    suppliers = [
        ("SUP-001", "McKesson Medical-Surgical Inc."),
        ("SUP-002", "Cardinal Health Distribution"),
        ("SUP-003", "Medline Industries LP"),
        ("SUP-004", "AmerisourceBergen Healthcare"),
        ("SUP-005", "Baxter Healthcare Supply"),
        ("SUP-006", "B. Braun Medical Inc."),
        ("SUP-007", "Owens & Minor Distribution")
    ]

    # 100 recommended orders
    recommended_orders = []
    for i in range(1, 101):
        item = risk_items[i % len(risk_items)]
        fac = facilities[i % len(facilities)]
        sup = suppliers[i % len(suppliers)]
        qty = ((i * 13) % 40 + 10) * 10
        unit_cost = round(((i * 19) % 80 + 15) * 1.0, 2)
        total_cost = round(qty * unit_cost, 2)
        reason = ["shortage_prevention", "restock", "safety_stock", "recall_replacement"][i % 4]
        urgency = ["emergency", "expedite", "routine"][i % 3]
        conf = round(82.0 + (i % 17) * 1.0, 1)

        recommended_orders.append({
            "recommendation_id": i,
            "item_id": item["item_id"],
            "item_description": item["item_description"],
            "supplier_id": sup[0],
            "supplier_name": sup[1],
            "recommended_qty": qty,
            "unit_cost": unit_cost,
            "total_cost": total_cost,
            "order_reason": reason,
            "urgency": urgency,
            "confidence_score": conf,
            "model_reasoning": f"Lakehouse Demand Model v4.2 detected days of supply ({round(float(item['days_of_supply']))}d) falling below safety threshold for {fac[1]}.",
            "comments": None,
            "facility_id": fac[0],
            "facility_name": fac[1],
            "decision_status": "pending",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=i * 2)).isoformat()
        })

    # 15 substitution candidates
    substitutions = [
        {
            "substitution_id": 1,
            "shortage_item_id": "SKU-PH-101",
            "shortage_item_description": "Cefazolin 1g IV Vial",
            "alternative_item_id": "SKU-PH-ALT-01",
            "alternative_item_description": "Ampicillin-Sulbactam 1.5g IV Vial",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Broad-spectrum beta-lactam coverage suitable for surgical prophylaxis in GI/GYN procedures. Review renal dosing before ordering.",
            "confidence_score": 92.5
        },
        {
            "substitution_id": 2,
            "shortage_item_id": "SKU-PH-101",
            "shortage_item_description": "Cefazolin 1g IV Vial",
            "alternative_item_id": "SKU-PH-ALT-02",
            "alternative_item_description": "Cefuroxime 1.5g IV Vial (Zinacef)",
            "clinical_equivalence": "equivalent",
            "formulary_status": "on_formulary",
            "availability": "available_to_order",
            "agent_reasoning": "Direct 2nd gen cephalosporin alternative with identical coverage for cardiothoracic and orthopedic pre-incisional dosing.",
            "confidence_score": 96.0
        },
        {
            "substitution_id": 3,
            "shortage_item_id": "SKU-PH-101",
            "shortage_item_description": "Cefazolin 1g IV Vial",
            "alternative_item_id": "SKU-PH-ALT-03",
            "alternative_item_description": "Clindamycin 600mg in 50mL D5W IVPB",
            "clinical_equivalence": "partial",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Indicated for severe penicillin/cephalosporin allergic patients. Lacks gram-negative coverage; co-administration with gentamicin recommended.",
            "confidence_score": 87.0
        },
        {
            "substitution_id": 4,
            "shortage_item_id": "SKU-PH-102",
            "shortage_item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "alternative_item_id": "SKU-PH-ALT-04",
            "alternative_item_description": "Enoxaparin Sodium 40mg/0.4mL Prefilled Syringe",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "LMWH alternative for VTE prophylaxis. Long half-life, requires dose adjustment for CrCl < 30 mL/min.",
            "confidence_score": 94.0
        },
        {
            "substitution_id": 5,
            "shortage_item_id": "SKU-PH-102",
            "shortage_item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "alternative_item_id": "SKU-PH-ALT-05",
            "alternative_item_description": "Fondaparinux 2.5mg/0.5mL Prefilled Syringe",
            "clinical_equivalence": "similar",
            "formulary_status": "restricted",
            "availability": "in_stock",
            "agent_reasoning": "Synthetic Factor Xa inhibitor for surgical thromboprophylaxis and suspected HIT patients. Restricted pharmacy approval required.",
            "confidence_score": 89.5
        },
        {
            "substitution_id": 6,
            "shortage_item_id": "SKU-PH-102",
            "shortage_item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "alternative_item_id": "SKU-PH-ALT-06",
            "alternative_item_description": "Bivalirudin 250mg IV Vial",
            "clinical_equivalence": "partial",
            "formulary_status": "on_formulary",
            "availability": "available_to_order",
            "agent_reasoning": "Direct thrombin inhibitor for procedural anticoagulation in cath lab/PCI when heparin-induced thrombocytopenia is suspected.",
            "confidence_score": 85.0
        },
        {
            "substitution_id": 7,
            "shortage_item_id": "SKU-PH-103",
            "shortage_item_description": "Propofol 10mg/mL 20mL Diprivan Emulsion",
            "alternative_item_id": "SKU-PH-ALT-07",
            "alternative_item_description": "Etomidate 2mg/mL 10mL Syringe",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Hemodynamically stable induction agent suitable for rapid sequence intubation. Not indicated for prolonged ICU sedation due to adrenal suppression.",
            "confidence_score": 91.0
        },
        {
            "substitution_id": 8,
            "shortage_item_id": "SKU-PH-103",
            "shortage_item_description": "Propofol 10mg/mL 20mL Diprivan Emulsion",
            "alternative_item_id": "SKU-PH-ALT-08",
            "alternative_item_description": "Dexmedetomidine (Precedex) 200mcg/2mL Vial",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Selective alpha-2 agonist for light-to-moderate ICU sedation without respiratory depression. May cause bradycardia and hypotension.",
            "confidence_score": 88.5
        },
        {
            "substitution_id": 9,
            "shortage_item_id": "SKU-SR-201",
            "shortage_item_description": "14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor",
            "alternative_item_id": "SKU-SR-ALT-10",
            "alternative_item_description": "16 Fr Silicone Elastomer Foley Tray w/ Temp Sensor",
            "clinical_equivalence": "equivalent",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Direct size-adjacent equivalent catheter. Suitable for adult ICU patients without urethral strictures.",
            "confidence_score": 95.0
        },
        {
            "substitution_id": 10,
            "shortage_item_id": "SKU-SR-201",
            "shortage_item_description": "14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor",
            "alternative_item_id": "SKU-SR-ALT-11",
            "alternative_item_description": "14 Fr Standard 2-Way Foley Tray (Non-Sensor)",
            "clinical_equivalence": "partial",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Identical lumen caliber and comfort; requires secondary axillary or core esophageal temperature probe for hypothermia protocols.",
            "confidence_score": 89.0
        },
        {
            "substitution_id": 11,
            "shortage_item_id": "SKU-CC-301",
            "shortage_item_description": "Endotracheal Tube 7.5mm Cuffed Murphy Eye",
            "alternative_item_id": "SKU-CC-ALT-12",
            "alternative_item_description": "Endotracheal Tube 7.0mm Cuffed Murphy Eye",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Slightly smaller diameter acceptable for adult female patients or emergency airways where 7.5mm is depleted.",
            "confidence_score": 90.0
        },
        {
            "substitution_id": 12,
            "shortage_item_id": "SKU-CC-301",
            "shortage_item_description": "Endotracheal Tube 7.5mm Cuffed Murphy Eye",
            "alternative_item_id": "SKU-CC-ALT-13",
            "alternative_item_description": "Endotracheal Tube 8.0mm Cuffed Subglottic Suction",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Premium tube with integrated subglottic drainage lumen, superior for preventing VAP during ventilator stays > 48h.",
            "confidence_score": 93.0
        },
        {
            "substitution_id": 13,
            "shortage_item_id": "SKU-PH-106",
            "shortage_item_description": "Nitroglycerin 50mg/250mL in D5W Premix",
            "alternative_item_id": "SKU-PH-ALT-14",
            "alternative_item_description": "Nitroprusside 50mg/2mL IV Solution (Requires Dilution)",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Potent arterial and venous vasodilator for acute hypertensive crisis. Requires continuous intra-arterial blood pressure monitoring.",
            "confidence_score": 87.5
        },
        {
            "substitution_id": 16,
            "shortage_item_id": "SKU-PH-112",
            "shortage_item_description": "Lisinopril 10mg Tablet",
            "alternative_item_id": "SKU-PH-ALT-20",
            "alternative_item_description": "Losartan 50mg Tablet",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "ACE-I to ARB class switch. Screen angioedema, renal function, pediatric label, and indication-based dose equivalency before any system-wide swap.",
            "confidence_score": 88.0
        },
        {
            "substitution_id": 14,
            "shortage_item_id": "SKU-PH-106",
            "shortage_item_description": "Nitroglycerin 50mg/250mL in D5W Premix",
            "alternative_item_id": "SKU-PH-ALT-15",
            "alternative_item_description": "Nicardipine 25mg/10mL Ampul IV Infusion",
            "clinical_equivalence": "similar",
            "formulary_status": "on_formulary",
            "availability": "available_to_order",
            "agent_reasoning": "Dihydropyridine calcium channel blocker for blood pressure control without the tachyphylaxis seen with nitroglycerin infusions.",
            "confidence_score": 92.0
        },
        {
            "substitution_id": 15,
            "shortage_item_id": "SKU-PH-103",
            "shortage_item_description": "Propofol 10mg/mL 20mL Diprivan Emulsion",
            "alternative_item_id": "SKU-PH-ALT-09",
            "alternative_item_description": "Midazolam 5mg/mL 2mL Vial",
            "clinical_equivalence": "partial",
            "formulary_status": "on_formulary",
            "availability": "in_stock",
            "agent_reasoning": "Benzodiazepine sedative. Higher risk of delirium in elderly ICU patients compared to propofol; requires flumazenil on hand.",
            "confidence_score": 83.0
        }
    ]

    # 3 FDA recalls across facilities
    recalls = [
        {
            "recall_id": 1,
            "fda_recall_number": "FDA-2026-REC-0842",
            "recall_class": "I",
            "item_id": "SKU-EQ-901",
            "item_description": "Alaris Infusion Pump Model 8015 PCU Door Latch",
            "affected_lot": "LOT-AL-2025-9921",
            "facility_id": "FAC-01",
            "facility_name": "Apex Memorial Hospital",
            "location_in_facility": "Central Biomedical Storage - Bay 4",
            "qty_on_hand": 24,
            "patient_exposure_count": 18,
            "recall_date": "2026-09-12",
            "status": "open"
        },
        {
            "recall_id": 2,
            "fda_recall_number": "FDA-2026-REC-0842",
            "recall_class": "I",
            "item_id": "SKU-EQ-901",
            "item_description": "Alaris Infusion Pump Model 8015 PCU Door Latch",
            "affected_lot": "LOT-AL-2025-9921",
            "facility_id": "FAC-02",
            "facility_name": "Apex Children's Medical Center",
            "location_in_facility": "PICU Clean Utility Rm 3B",
            "qty_on_hand": 12,
            "patient_exposure_count": 14,
            "recall_date": "2026-09-12",
            "status": "open"
        },
        {
            "recall_id": 3,
            "fda_recall_number": "FDA-2026-REC-0842",
            "recall_class": "I",
            "item_id": "SKU-EQ-901",
            "item_description": "Alaris Infusion Pump Model 8015 PCU Door Latch",
            "affected_lot": "LOT-AL-2025-9921",
            "facility_id": "FAC-03",
            "facility_name": "Apex Valley Health",
            "location_in_facility": "Surgical Step-Down Unit",
            "qty_on_hand": 16,
            "patient_exposure_count": 9,
            "recall_date": "2026-09-12",
            "status": "open"
        },
        {
            "recall_id": 4,
            "fda_recall_number": "FDA-2026-REC-0719",
            "recall_class": "II",
            "item_id": "SKU-PH-102",
            "item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "affected_lot": "LOT-HP-88301-B",
            "facility_id": "FAC-01",
            "facility_name": "Apex Memorial Hospital",
            "location_in_facility": "Main Pharmacy Vault - Pyxis Carousel 2",
            "qty_on_hand": 40,
            "patient_exposure_count": 31,
            "recall_date": "2026-09-18",
            "status": "open"
        },
        {
            "recall_id": 5,
            "fda_recall_number": "FDA-2026-REC-0719",
            "recall_class": "II",
            "item_id": "SKU-PH-102",
            "item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "affected_lot": "LOT-HP-88301-B",
            "facility_id": "FAC-04",
            "facility_name": "Apex Ambulatory Surgical",
            "location_in_facility": "Pre-Op Medication Refrigerator A",
            "qty_on_hand": 15,
            "patient_exposure_count": 6,
            "recall_date": "2026-09-18",
            "status": "open"
        },
        {
            "recall_id": 6,
            "fda_recall_number": "FDA-2026-REC-0719",
            "recall_class": "II",
            "item_id": "SKU-PH-102",
            "item_description": "Heparin Sodium 5,000 USP Units/mL 10mL",
            "affected_lot": "LOT-HP-88301-B",
            "facility_id": "FAC-06",
            "facility_name": "Apex Central Distribution Hub",
            "location_in_facility": "Cold Chain Zone 1 - Rack C",
            "qty_on_hand": 110,
            "patient_exposure_count": 0,
            "recall_date": "2026-09-18",
            "status": "open"
        },
        {
            "recall_id": 7,
            "fda_recall_number": "FDA-2026-REC-0655",
            "recall_class": "III",
            "item_id": "SKU-SR-208",
            "item_description": "Silk Suture 2-0 Braided Black 30 inch (Box 36)",
            "affected_lot": "LOT-SK-2026-004A",
            "facility_id": "FAC-01",
            "facility_name": "Apex Memorial Hospital",
            "location_in_facility": "OR Sterile Core - Cabinet 7",
            "qty_on_hand": 28,
            "patient_exposure_count": 4,
            "recall_date": "2026-09-21",
            "status": "open"
        },
        {
            "recall_id": 8,
            "fda_recall_number": "FDA-2026-REC-0655",
            "recall_class": "III",
            "item_id": "SKU-SR-208",
            "item_description": "Silk Suture 2-0 Braided Black 30 inch (Box 36)",
            "affected_lot": "LOT-SK-2026-004A",
            "facility_id": "FAC-05",
            "facility_name": "Apex Northgate Clinic",
            "location_in_facility": "Minor Procedure Supply Closet",
            "qty_on_hand": 8,
            "patient_exposure_count": 2,
            "recall_date": "2026-09-21",
            "status": "open"
        }
    ]

    # 20 transfers
    transfers = [
        {
            "transfer_id": 1,
            "item_id": "SKU-PH-101",
            "item_description": "Cefazolin 1g IV Vial",
            "from_facility_id": "FAC-06",
            "from_facility_name": "Apex Central Distribution Hub",
            "to_facility_id": "FAC-01",
            "to_facility_name": "Apex Memorial Hospital",
            "recommended_qty": 150,
            "reason": "shortage_relief",
            "from_days_of_supply": 24.5,
            "to_days_of_supply": 1.5,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "transfer_id": 2,
            "item_id": "SKU-PH-102",
            "item_description": "Heparin Sodium 5,000 USP Units/mL",
            "from_facility_id": "FAC-06",
            "from_facility_name": "Apex Central Distribution Hub",
            "to_facility_id": "FAC-02",
            "to_facility_name": "Apex Children's Medical Center",
            "recommended_qty": 80,
            "reason": "shortage_relief",
            "from_days_of_supply": 19.0,
            "to_days_of_supply": 1.9,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "transfer_id": 3,
            "item_id": "SKU-SR-201",
            "item_description": "14 Fr Hydrophilic Foley Catheter Tray",
            "from_facility_id": "FAC-03",
            "from_facility_name": "Apex Valley Health",
            "to_facility_id": "FAC-01",
            "to_facility_name": "Apex Memorial Hospital",
            "recommended_qty": 30,
            "reason": "rebalance",
            "from_days_of_supply": 16.2,
            "to_days_of_supply": 1.5,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "transfer_id": 4,
            "item_id": "SKU-PH-103",
            "item_description": "Propofol 10mg/mL 20mL Diprivan",
            "from_facility_id": "FAC-06",
            "from_facility_name": "Apex Central Distribution Hub",
            "to_facility_id": "FAC-03",
            "to_facility_name": "Apex Valley Health",
            "recommended_qty": 90,
            "reason": "shortage_relief",
            "from_days_of_supply": 22.0,
            "to_days_of_supply": 1.8,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "transfer_id": 5,
            "item_id": "SKU-CC-301",
            "item_description": "Endotracheal Tube 7.5mm Cuffed",
            "from_facility_id": "FAC-04",
            "from_facility_name": "Apex Ambulatory Surgical",
            "to_facility_id": "FAC-01",
            "to_facility_name": "Apex Memorial Hospital",
            "recommended_qty": 25,
            "reason": "rebalance",
            "from_days_of_supply": 28.0,
            "to_days_of_supply": 2.1,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]

    return {
        "risk_items": risk_items,
        "recommended_orders": recommended_orders,
        "substitutions": substitutions,
        "recalls": recalls,
        "transfers": transfers,
        "order_decisions": [],
        "substitution_selections": [],
        "recall_actions": [],
        "transfer_confirmations": [],
        "audit": [],
        "formulary": [dict(row) for row in FORMULARY_SEED],
        "patient_census": [dict(row) for row in MOCK_CENSUS],
        "substitution_simulations": [],
        "branches": [
            {
                "id": "production",
                "state": "READY",
                "default": True,
                "parent": None,
                "logical_size_bytes": 1048576,
                "created_at": "2026-09-25T20:59:05Z",
                "connection": mock_connection(),
                "roles": [],
            }
        ],
        "migrations": [
            {"version": "001_initial_schema.sql", "checksum": "a1b2c3d4e5f6...", "applied_at": "2026-09-25T20:59:15Z", "applied_by": "admin@apexhealth.org"},
            {"version": "002_seed_data.sql", "checksum": "f6e5d4c3b2a1...", "applied_at": "2026-09-25T20:59:20Z", "applied_by": "admin@apexhealth.org"}
        ]
    }


class Store:
    def __init__(self) -> None:
        self.mock = os.getenv("USE_MOCK_BACKEND", "").lower() == "true"
        self.data = _seed_data()
        self.pool: AsyncConnectionPool | None = None
        
        self._sdk = None
        if self.mock or "pytest" in sys.modules:
            return
        try:
            self._sdk = workspace_client()
        except Exception as e:
            print(f"Databricks SDK init warning: {e}")
            self._sdk = None

    async def start(self) -> None:
        if self.mock:
            print("Store running in mock data mode (offline or local preview)")
            return
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                await self._connect()
                self.mock = False
                try:
                    await self.run_migrations()
                except Exception as exc:
                    print(f"Migration warning (keeping live Lakebase connection): {exc}")
                print("Lakebase Postgres connected successfully!")
                return
            except Exception as exc:
                last_error = exc
                print(f"Lakebase connection attempt {attempt} failed: {exc}")
                await self.close()
                await asyncio.sleep(min(2**attempt, 10))
        
        print("Falling back to local in-memory store mode due to connection error:", last_error)
        self.mock = True

    async def _connect(self) -> None:
        if self._sdk is None:
            raise RuntimeError("Databricks SDK is unavailable")
        
        endpoint = await asyncio.to_thread(self._sdk.postgres.get_endpoint, name=ENDPOINT)
        host = endpoint.status.hosts.host
        username = os.environ.get("DATABRICKS_CLIENT_ID") or self._sdk.current_user.me().user_name

        credential = await asyncio.to_thread(self._sdk.postgres.generate_database_credential, endpoint=ENDPOINT)
        conninfo = (
            f"host={host} dbname={DATABASE} user={username} password={credential.token} "
            "sslmode=require connect_timeout=15"
        )
        self.pool = AsyncConnectionPool(
            conninfo,
            min_size=1,
            max_size=10,
            max_lifetime=2700,
            timeout=20,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        await self.pool.open(wait=True)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[Any]:
        if not self.pool:
            raise RuntimeError("Database pool is unavailable")
        try:
            async with self.pool.connection() as conn:
                yield conn
        except Exception as exc:
            if "password authentication failed" in str(exc).lower():
                await self.close()
                await self._connect()
            raise

    async def fetch(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if self.mock:
            return []
        async with self.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return list(await cur.fetchall())

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
        if self.mock:
            return {}
        async with self.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                row = await cur.fetchone() if cur.description else None
                await conn.commit()
                return dict(row) if row else {}

    async def run_migrations(self) -> None:
        if self.mock:
            return
        await apply_migrations(self)


store = Store()


def current_identity(headers: Any) -> dict[str, str]:
    return {
        "email": headers.get("x-forwarded-email")
        or headers.get("x-forwarded-user")
        or DEFAULT_IDENTITY_EMAIL,
        "name": headers.get("x-forwarded-preferred-username") or DEFAULT_IDENTITY_NAME,
        "role": "Materials Manager / Platform Admin"
    }


def json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    return value
