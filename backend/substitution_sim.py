from __future__ import annotations

from typing import Any

THERAPEUTIC_CLASS = {
    "SKU-PH-101": "surgical_prophylaxis_cephalosporin",
    "SKU-PH-102": "vte_anticoagulation",
    "SKU-PH-103": "icu_sedation",
    "SKU-SR-201": "indwelling_urinary_catheter",
    "SKU-CC-301": "adult_airway_ett",
    "SKU-PH-106": "vasodilator_infusion",
    "SKU-PH-112": "hypertension_ace_inhibitor",
}

ALT_UNIT_COST = {
    "SKU-PH-ALT-01": 18.40,
    "SKU-PH-ALT-02": 16.90,
    "SKU-PH-ALT-03": 9.75,
    "SKU-PH-ALT-04": 28.50,
    "SKU-PH-ALT-05": 41.00,
    "SKU-PH-ALT-06": 186.00,
    "SKU-PH-ALT-07": 14.20,
    "SKU-PH-ALT-08": 62.00,
    "SKU-PH-ALT-09": 4.80,
    "SKU-SR-ALT-10": 46.50,
    "SKU-SR-ALT-11": 22.00,
    "SKU-CC-ALT-12": 15.40,
    "SKU-CC-ALT-13": 24.80,
    "SKU-PH-ALT-14": 19.10,
    "SKU-PH-ALT-15": 47.25,
    "SKU-PH-ALT-20": 1.15,
    "SKU-PH-ALT-21": 0.62,
}

LEAD_TIME_DELTA = {
    "FAC-01": 0,
    "FAC-02": 2,
    "FAC-03": 2,
    "FAC-04": 0,
    "FAC-05": 1,
    "FAC-06": 0,
    "FAC-07": 2,
    "FAC-08": 0,
}

MOCK_CENSUS: list[dict[str, Any]] = [
    {"item_id": "SKU-PH-101", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "active_order_count": 200, "allergy_flag_count": 6, "contraindication_count": 2, "avg_daily_doses": 48.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "active_order_count": 50, "allergy_flag_count": 3, "contraindication_count": 1, "avg_daily_doses": 12.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "active_order_count": 72, "allergy_flag_count": 2, "contraindication_count": 0, "avg_daily_doses": 18.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "active_order_count": 38, "allergy_flag_count": 1, "contraindication_count": 0, "avg_daily_doses": 14.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "active_order_count": 16, "allergy_flag_count": 0, "contraindication_count": 0, "avg_daily_doses": 4.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-06", "facility_name": "Apex Central Distribution Hub", "active_order_count": 0, "allergy_flag_count": 0, "contraindication_count": 0, "avg_daily_doses": 0.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "active_order_count": 28, "allergy_flag_count": 1, "contraindication_count": 0, "avg_daily_doses": 6.0},
    {"item_id": "SKU-PH-101", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "active_order_count": 22, "allergy_flag_count": 1, "contraindication_count": 1, "avg_daily_doses": 5.0},
    {"item_id": "SKU-PH-102", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "active_order_count": 120, "allergy_flag_count": 4, "contraindication_count": 8, "avg_daily_doses": 36.0},
    {"item_id": "SKU-PH-102", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "active_order_count": 44, "allergy_flag_count": 2, "contraindication_count": 3, "avg_daily_doses": 10.0},
    {"item_id": "SKU-PH-102", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "active_order_count": 51, "allergy_flag_count": 1, "contraindication_count": 2, "avg_daily_doses": 12.0},
    {"item_id": "SKU-PH-102", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "active_order_count": 19, "allergy_flag_count": 0, "contraindication_count": 1, "avg_daily_doses": 6.0},
    {"item_id": "SKU-PH-103", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "active_order_count": 86, "allergy_flag_count": 0, "contraindication_count": 5, "avg_daily_doses": 22.0},
    {"item_id": "SKU-PH-103", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "active_order_count": 41, "allergy_flag_count": 0, "contraindication_count": 2, "avg_daily_doses": 11.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "active_order_count": 520, "allergy_flag_count": 12, "contraindication_count": 18, "avg_daily_doses": 520.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "active_order_count": 187, "allergy_flag_count": 3, "contraindication_count": 4, "avg_daily_doses": 90.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "active_order_count": 310, "allergy_flag_count": 4, "contraindication_count": 8, "avg_daily_doses": 310.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "active_order_count": 165, "allergy_flag_count": 1, "contraindication_count": 3, "avg_daily_doses": 140.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "active_order_count": 98, "allergy_flag_count": 1, "contraindication_count": 2, "avg_daily_doses": 98.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "active_order_count": 240, "allergy_flag_count": 1, "contraindication_count": 4, "avg_daily_doses": 240.0},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "active_order_count": 327, "allergy_flag_count": 1, "contraindication_count": 2, "avg_daily_doses": 327.0},
]

FORMULARY_SEED = [
    {"therapeutic_class": "surgical_prophylaxis_cephalosporin", "active_item_id": "SKU-PH-101", "active_item_description": "Cefazolin 1g IV Vial"},
    {"therapeutic_class": "vte_anticoagulation", "active_item_id": "SKU-PH-102", "active_item_description": "Heparin Sodium 5,000 USP Units/mL 10mL"},
    {"therapeutic_class": "icu_sedation", "active_item_id": "SKU-PH-103", "active_item_description": "Propofol 10mg/mL 20mL Diprivan Emulsion"},
    {"therapeutic_class": "indwelling_urinary_catheter", "active_item_id": "SKU-SR-201", "active_item_description": "14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor"},
    {"therapeutic_class": "adult_airway_ett", "active_item_id": "SKU-CC-301", "active_item_description": "Endotracheal Tube 7.5mm Cuffed Murphy Eye"},
    {"therapeutic_class": "vasodilator_infusion", "active_item_id": "SKU-PH-106", "active_item_description": "Nitroglycerin 50mg/250mL in D5W Premix"},
    {"therapeutic_class": "hypertension_ace_inhibitor", "active_item_id": "SKU-PH-112", "active_item_description": "Lisinopril 10mg Tablet"},
]

sessions: dict[str, dict[str, Any]] = {}


def _fallback_census(item_id: str) -> list[dict[str, Any]]:
    rows = [row for row in MOCK_CENSUS if row["item_id"] == item_id]
    if rows:
        return rows
    return [
        {
            "item_id": item_id,
            "facility_id": f"FAC-0{i}",
            "facility_name": name,
            "active_order_count": count,
            "allergy_flag_count": 1 if i in {1, 2} else 0,
            "contraindication_count": 1 if i == 1 else 0,
            "avg_daily_doses": max(2.0, count / 4),
        }
        for i, (name, count) in enumerate(
            [
                ("Apex Memorial Hospital", 64),
                ("Apex Children's Medical Center", 22),
                ("Apex Valley Health", 31),
                ("Apex Ambulatory Surgical", 18),
                ("Apex Northgate Clinic", 9),
                ("Apex Central Distribution Hub", 0),
                ("Apex Westside Specialty", 14),
                ("Apex Crestview Rehab", 11),
            ],
            start=1,
        )
    ]


def compute_plan(
    *,
    shortage_item_id: str,
    shortage_desc: str,
    alternative_item_id: str,
    alternative_desc: str,
    census: list[dict[str, Any]],
    current_unit_cost: float,
    alt_on_hand: int,
    forecast_90d: int,
    facility_ids: list[str] | None,
) -> dict[str, Any]:
    included = set(facility_ids) if facility_ids else None
    alt_cost = ALT_UNIT_COST.get(alternative_item_id, current_unit_cost * 1.12)
    facilities: list[dict[str, Any]] = []
    patients = 0
    allergies = 0
    contraindications = 0
    daily_doses = 0.0
    monthly_cost = 0.0
    delayed = []

    for row in census:
        if row.get("item_id") and row["item_id"] != shortage_item_id:
            continue
        fid = row["facility_id"]
        if included is not None and fid not in included:
            continue
        count = int(row.get("active_order_count") or 0)
        doses = float(row.get("avg_daily_doses") or 0)
        lead = LEAD_TIME_DELTA.get(fid, 0)
        month_units = doses * 30
        delta = round((alt_cost - current_unit_cost) * month_units, 2)
        patients += count
        allergies += int(row.get("allergy_flag_count") or 0)
        contraindications += int(row.get("contraindication_count") or 0)
        daily_doses += doses
        monthly_cost += delta
        if lead > 0 and count > 0:
            delayed.append(row["facility_name"])
        share = (count / patients) if patients else 0
        facilities.append(
            {
                "facility_id": fid,
                "facility_name": row["facility_name"],
                "patients": count,
                "allergy_flags": int(row.get("allergy_flag_count") or 0),
                "contraindications": int(row.get("contraindication_count") or 0),
                "avg_daily_doses": doses,
                "units_allocated": int(round(month_units)),
                "monthly_cost_delta": delta,
                "lead_time_delta_days": lead,
                "included": True,
                "share": share,
            }
        )

    # Reallocate alt stock proportional to patient need (step 3 depends on step 2).
    total_patients = max(patients, 1)
    remaining = alt_on_hand
    for idx, fac in enumerate(facilities):
        if idx == len(facilities) - 1:
            allocated = remaining
        else:
            allocated = int(round(alt_on_hand * (fac["patients"] / total_patients)))
            remaining -= allocated
        fac["units_allocated"] = allocated
        cover = round(allocated / fac["avg_daily_doses"], 1) if fac["avg_daily_doses"] else 999
        fac["days_cover"] = cover
        fac["share"] = round(fac["patients"] / total_patients, 3)

    demand_90 = forecast_90d or int(daily_doses * 90)
    covers_90 = alt_on_hand >= demand_90 if demand_90 else True
    monthly_cost = round(monthly_cost, 2)
    verb = "saves" if monthly_cost < 0 else "adds"
    delay_clause = (
        f" Lead time increases by {max((f['lead_time_delta_days'] for f in facilities), default=0)} day(s) at {len(delayed)} facilities ({', '.join(delayed)})."
        if delayed
        else " Lead times are unchanged at included facilities."
    )
    coverage_clause = (
        f" {alternative_desc} on-hand ({alt_on_hand:,} units) covers 90-day projected demand ({demand_90:,})."
        if covers_90
        else f" {alternative_desc} on-hand ({alt_on_hand:,} units) is short of 90-day demand ({demand_90:,}); expedite restock before shipping."
    )
    summary = (
        f"Switching {shortage_desc} → {alternative_desc} {verb} ${abs(monthly_cost):,.0f}/month "
        f"across {len(facilities)} facilities and {patients:,} active orders."
        f"{delay_clause}{coverage_clause}"
    )
    return {
        "therapeutic_class": THERAPEUTIC_CLASS.get(shortage_item_id, "unclassified"),
        "shortage_item_id": shortage_item_id,
        "shortage_item_description": shortage_desc,
        "alternative_item_id": alternative_item_id,
        "alternative_item_description": alternative_desc,
        "patients_affected": patients,
        "allergy_flags": allergies,
        "contraindications": contraindications,
        "monthly_cost_delta": monthly_cost,
        "alt_on_hand": alt_on_hand,
        "forecast_demand_90d": demand_90,
        "covers_90d": covers_90,
        "delayed_facilities": delayed,
        "facilities": facilities,
        "summary": summary,
    }
