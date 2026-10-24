from __future__ import annotations

import json
import os
from typing import Any, Callable

from backend.database import store

DRUG_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "SKU-PH-101": {
        "item_id": "SKU-PH-101",
        "item_description": "Cefazolin 1g IV Vial",
        "pharmacologic_class": "cephalosporin",
        "subclass": "1st generation",
        "pediatric_min_age": 0,
        "renal_adjustment": "renal dose adjust CrCl < 30",
        "dosing_notes": "Surgical prophylaxis.",
    },
    "SKU-PH-ALT-02": {
        "item_id": "SKU-PH-ALT-02",
        "item_description": "Cefuroxime 1.5g IV Vial (Zinacef)",
        "pharmacologic_class": "cephalosporin",
        "subclass": "2nd generation",
        "pediatric_min_age": 3,
        "renal_adjustment": "renal dose adjust CrCl < 30",
        "dosing_notes": "Adult surgical prophylaxis equivalent in most cases.",
    },
    "SKU-PH-112": {
        "item_id": "SKU-PH-112",
        "item_description": "Lisinopril 10mg Tablet",
        "pharmacologic_class": "ACE inhibitor",
        "subclass": "ACE-I",
        "pediatric_min_age": 6,
        "renal_adjustment": "use caution eGFR < 30; start low",
        "dosing_notes": "HTN 10mg; HFrEF/post-MI titrate. ACE-I angioedema risk.",
    },
    "SKU-PH-ALT-20": {
        "item_id": "SKU-PH-ALT-20",
        "item_description": "Losartan 50mg Tablet",
        "pharmacologic_class": "ARB",
        "subclass": "angiotensin receptor blocker",
        "pediatric_min_age": 6,
        "renal_adjustment": "consider 25mg start if eGFR < 30",
        "dosing_notes": "HTN often 50mg; HFrEF start 25mg and titrate. 2-8% ACE-I angioedema cross-reactivity.",
    },
    "SKU-PH-ALT-21": {
        "item_id": "SKU-PH-ALT-21",
        "item_description": "Amlodipine 2.5mg Tablet",
        "pharmacologic_class": "calcium channel blocker",
        "subclass": "dihydropyridine",
        "pediatric_min_age": 6,
        "renal_adjustment": "none typical",
        "dosing_notes": "Pediatric hypertension alternative when ACE-I/ARB not suitable.",
    },
}

NAME_ALIASES = {
    "lisinopril": "SKU-PH-112",
    "losartan": "SKU-PH-ALT-20",
    "amlodipine": "SKU-PH-ALT-21",
    "cefazolin": "SKU-PH-101",
    "cefuroxime": "SKU-PH-ALT-02",
    "heparin": "SKU-PH-102",
    "enoxaparin": "SKU-PH-ALT-04",
    "propofol": "SKU-PH-103",
}

LISINOPRIL_COHORTS: list[dict[str, Any]] = [
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 268},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 110},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 102},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": True, "patient_count": 18},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 12},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-01", "facility_name": "Apex Memorial Hospital", "indication": "hypertension", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 10},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "indication": "hypertension", "age_band": "pediatric_6_17", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 148},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "indication": "hypertension", "age_band": "pediatric_lt6", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 2},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "indication": "hypertension", "age_band": "pediatric_6_17", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 3},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "indication": "hypertension", "age_band": "pediatric_6_17", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": True, "patient_count": 4},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-02", "facility_name": "Apex Children's Medical Center", "indication": "hypertension", "age_band": "pediatric_6_17", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 30},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 160},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 70},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 68},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 4},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-03", "facility_name": "Apex Valley Health", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 8},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 120},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 40},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 1},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-04", "facility_name": "Apex Ambulatory Surgical", "indication": "hypertension", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 4},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 72},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 22},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 1},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-05", "facility_name": "Apex Northgate Clinic", "indication": "hypertension", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 3},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 130},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 85},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 20},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 1},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-07", "facility_name": "Apex Westside Specialty", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 4},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 180},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": False, "patient_count": 126},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": False, "potassium_concurrent": True, "patient_count": 16},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "indication": "hypertension", "age_band": "adult", "egfr_band": "ge30", "angioedema": True, "potassium_concurrent": False, "patient_count": 2},
    {"item_id": "SKU-PH-112", "facility_id": "FAC-08", "facility_name": "Apex Crestview Rehab", "indication": "heart_failure_post_mi", "age_band": "adult", "egfr_band": "lt30", "angioedema": False, "potassium_concurrent": False, "patient_count": 3},
]


def resolve_pair(prompt: str | None) -> tuple[str | None, str | None]:
    if not prompt:
        return None, None
    found: list[tuple[int, str]] = []
    lower = prompt.lower()
    seen: set[str] = set()
    for alias, sku in NAME_ALIASES.items():
        idx = lower.find(alias)
        if idx >= 0 and sku not in seen:
            found.append((idx, sku))
            seen.add(sku)
    found.sort()
    if not found:
        return None, None
    if len(found) == 1:
        return found[0][1], None
    return found[0][1], found[1][1]


def resolve_item(text: str | None) -> str | None:
    if not text:
        return None
    raw = text.strip()
    if raw.upper().startswith("SKU-"):
        return raw
    lower = raw.lower()
    for alias, sku in NAME_ALIASES.items():
        if alias in lower:
            return sku
    return None


def _cohort_rows(item_id: str) -> list[dict[str, Any]]:
    if item_id == "SKU-PH-112":
        return list(LISINOPRIL_COHORTS)
    return []


def _sum(rows: list[dict[str, Any]]) -> int:
    return sum(int(row.get("patient_count") or 0) for row in rows)


def query_patients(
    item_id: str,
    filters: dict[str, Any] | None = None,
    rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    filters = filters or {}
    rows = list(rows) if rows is not None else _cohort_rows(item_id)
    if not rows:
        return {"item_id": item_id, "patients": 0, "note": "No patient-level cohort; using facility census only."}

    def apply(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = rows
        if filters.get("angioedema"):
            out = [row for row in out if row.get("angioedema")]
        if filters.get("egfr_lt_30"):
            out = [row for row in out if row.get("egfr_band") == "lt30"]
        if filters.get("pediatric_lt6"):
            out = [row for row in out if row.get("age_band") == "pediatric_lt6"]
        if filters.get("pediatric"):
            out = [row for row in out if str(row.get("age_band") or "").startswith("pediatric")]
        if filters.get("potassium"):
            out = [row for row in out if row.get("potassium_concurrent")]
        if filters.get("indication"):
            out = [row for row in out if row.get("indication") == filters["indication"]]
        return out

    matched = apply(rows)
    by_indication: dict[str, int] = {}
    for row in rows:
        by_indication[row["indication"]] = by_indication.get(row["indication"], 0) + int(row["patient_count"])
    facilities = sorted({row["facility_name"] for row in rows})
    return {
        "item_id": item_id,
        "patients": _sum(matched) if filters else _sum(rows),
        "filters": filters,
        "facilities": len(facilities),
        "facility_names": facilities,
        "by_indication": by_indication if not filters else None,
        "matched_rows": len(matched),
    }


def lookup_drugs(shortage_id: str, alternative_id: str) -> dict[str, Any]:
    source = DRUG_KNOWLEDGE.get(shortage_id) or {"item_id": shortage_id, "pharmacologic_class": "unclassified", "item_description": shortage_id}
    target = DRUG_KNOWLEDGE.get(alternative_id) or {"item_id": alternative_id, "pharmacologic_class": "unclassified", "item_description": alternative_id}
    class_switch = source.get("pharmacologic_class") != target.get("pharmacologic_class")
    return {
        "from_drug": source,
        "to_drug": target,
        "class_switch": class_switch,
        "clinical_note": (
            f"{source.get('pharmacologic_class')} → {target.get('pharmacologic_class')} is a therapeutic class switch, not a generic swap."
            if class_switch
            else f"Both agents are {source.get('pharmacologic_class')}."
        ),
    }


def clinical_rule(rule_id: str) -> dict[str, Any]:
    rules = {
        "ace_arb_cross_reactivity": {
            "rule": "ACE-I induced angioedema has ~2-8% cross-reactivity with ARBs.",
            "action": "Do not auto-substitute; individual allergy/immunology or attending review.",
        },
        "losartan_renal_start": {
            "rule": "eGFR < 30: start Losartan 25mg rather than 50mg and monitor K+ / creatinine.",
            "action": "Dose-adjust rather than 1:1 milligram swap.",
        },
        "losartan_pediatric_label": {
            "rule": "Losartan is labeled for pediatric hypertension age 6 and older, not under 6.",
            "action": "Patients < 6 need a different class (consider amlodipine consult).",
        },
        "losartan_hf_titration": {
            "rule": "HFrEF / post-MI: start Losartan 25mg and titrate to 50mg; do not jump to 50mg.",
            "action": "Use a titration protocol, which also changes the near-term cost trajectory.",
        },
        "ace_arb_potassium": {
            "rule": "ACE-I and ARB both raise hyperkalemia risk with potassium supplements or K-sparing diuretics.",
            "action": "Keep the patients on the substitute but update monitoring, not auto-exclude.",
        },
        "cephalosporin_allergy": {
            "rule": "Cephalosporin-cephalosporin swaps still require allergy history review.",
            "action": "Flag documented cephalosporin allergy for pharmacist review.",
        },
    }
    return rules.get(rule_id, {"rule": "No packaged rule", "action": "Use clinical judgment."})


def investigations_for(knowledge: dict[str, Any]) -> list[str]:
    if knowledge.get("class_switch"):
        src = (knowledge.get("from_drug") or {}).get("pharmacologic_class")
        dst = (knowledge.get("to_drug") or {}).get("pharmacologic_class")
        if src == "ACE inhibitor" and dst == "ARB":
            planned = [
                "angioedema_cross_reactivity",
                "renal_function",
                "pediatric_label",
                "potassium_interaction",
                "indication_dosing",
            ]
        else:
            planned = ["allergy_to_alternative", "renal_function", "pediatric_label"]
    else:
        planned = ["allergy_to_alternative", "pediatric_label"]
    if "inventory_cover" not in planned:
        planned.append("inventory_cover")
    return planned


def run_one_investigation(
    key: str,
    item_id: str,
    alt_id: str,
    rows: list[dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any]]:
    if key == "angioedema_cross_reactivity":
        angio = query_patients(item_id, {"angioedema": True}, rows=rows)
        return "angioedema", {**angio, "rule": clinical_rule("ace_arb_cross_reactivity")}
    if key == "renal_function":
        renal = query_patients(item_id, {"egfr_lt_30": True}, rows=rows)
        return "renal", {
            **renal,
            "rule": clinical_rule("losartan_renal_start" if alt_id == "SKU-PH-ALT-20" else "cephalosporin_allergy"),
        }
    if key == "pediatric_label":
        peds = query_patients(item_id, {"pediatric_lt6": True}, rows=rows)
        all_peds = query_patients(item_id, {"pediatric": True}, rows=rows)
        return "pediatric", {
            "patients_lt6": peds.get("patients", 0),
            "patients_pediatric": all_peds.get("patients", 0),
            "rule": clinical_rule("losartan_pediatric_label" if alt_id == "SKU-PH-ALT-20" else "cephalosporin_allergy"),
        }
    if key == "potassium_interaction":
        potassium = query_patients(item_id, {"potassium": True}, rows=rows)
        return "potassium", {**potassium, "rule": clinical_rule("ace_arb_potassium")}
    if key == "indication_dosing":
        htn = query_patients(item_id, {"indication": "hypertension"}, rows=rows)
        hf = query_patients(item_id, {"indication": "heart_failure_post_mi"}, rows=rows)
        return "indications", {
            "hypertension": htn.get("patients", 0),
            "heart_failure_post_mi": hf.get("patients", 0),
            "rule": clinical_rule("losartan_hf_titration"),
        }
    if key == "allergy_to_alternative":
        return "allergy", {
            "patients": query_patients(item_id, {}, rows=rows).get("patients", 0),
            "note": "Use census allergy flags when patient-level allergy truth is unavailable.",
            "rule": clinical_rule("cephalosporin_allergy"),
        }
    return key, {"note": "No packaged branch query for this check."}


def run_investigations(
    item_id: str,
    alt_id: str,
    planned: list[str],
    rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    findings: dict[str, Any] = {}
    for key in planned:
        if key == "inventory_cover":
            continue
        mapped, finding = run_one_investigation(key, item_id, alt_id, rows=rows)
        findings[mapped] = finding
    return findings


def categorize(item_id: str, knowledge: dict[str, Any], findings: dict[str, Any]) -> list[dict[str, Any]]:
    total = query_patients(item_id, {}).get("patients") or 0
    if total <= 0:
        return []
    angio = int((findings.get("angioedema") or {}).get("patients") or 0)
    renal = int((findings.get("renal") or {}).get("patients") or 0)
    peds_lt6 = int((findings.get("pediatric") or {}).get("patients_lt6") or 0)
    potassium = int((findings.get("potassium") or {}).get("patients") or 0)
    hf = int((findings.get("indications") or {}).get("heart_failure_post_mi") or 0)
    exclusive = angio + renal + peds_lt6
    standard = max(total - exclusive, 0)
    categories = [
        {
            "key": "A",
            "label": "Safe to auto-substitute",
            "severity": "ok",
            "patients": standard,
            "share": round(standard / total, 3),
            "recommendation": "Losartan 50mg for hypertension; apply formulary swap on the branch.",
        }
    ]
    if renal:
        categories.append(
            {
                "key": "B",
                "label": "Renal-adjusted dosing",
                "severity": "watch",
                "patients": renal,
                "share": round(renal / total, 3),
                "recommendation": "Start Losartan 25mg and monitor creatinine / potassium.",
            }
        )
    if angio:
        categories.append(
            {
                "key": "C",
                "label": "Angioedema history — individual review",
                "severity": "stop",
                "patients": angio,
                "share": round(angio / total, 3),
                "recommendation": "Do not auto-switch. ACE-I to ARB cross-reactivity requires case review.",
            }
        )
    if peds_lt6:
        categories.append(
            {
                "key": "D",
                "label": "Pediatric age exclusion",
                "severity": "stop",
                "patients": peds_lt6,
                "share": round(peds_lt6 / total, 3),
                "recommendation": "Losartan is not labeled under age 6. Consult amlodipine 2.5mg.",
            }
        )
    if potassium:
        categories.append(
            {
                "key": "E",
                "label": "Potassium monitoring update",
                "severity": "info",
                "patients": potassium,
                "share": round(potassium / total, 3),
                "recommendation": "Remain eligible for substitution; update hyperkalemia monitoring protocol.",
            }
        )
    if hf and knowledge.get("class_switch"):
        categories.append(
            {
                "key": "F",
                "label": "Heart failure / post-MI titration",
                "severity": "watch",
                "patients": hf,
                "share": round(hf / total, 3),
                "recommendation": "Start 25mg and titrate; do not use a flat 50mg conversion.",
            }
        )
    return categories


def corrected_monthly_cost(item_id: str, findings: dict[str, Any]) -> dict[str, Any]:
    naive = 52000
    htn = int((findings.get("indications") or {}).get("hypertension") or 0)
    hf = int((findings.get("indications") or {}).get("heart_failure_post_mi") or 0)
    if item_id != "SKU-PH-112":
        return {"monthly_cost_delta": None, "naive_monthly_cost_delta": None, "note": "Facility unit-cost model used."}
    # HTN Losartan 50mg ~$1.15 vs Lisinopril $0.42 → ~$22/pt-month; HF starts 25mg (~half) then titrates.
    htn_cost = htn * 18.4
    hf_cost = hf * 11.2
    actual = round(htn_cost + hf_cost, 0)
    return {
        "monthly_cost_delta": actual,
        "naive_monthly_cost_delta": naive,
        "note": "Corrected for indication-based dose equivalency (HTN 50mg vs HFrEF 25mg start).",
    }


def unexpected_findings(knowledge: dict[str, Any], findings: dict[str, Any], categories: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    if knowledge.get("class_switch"):
        notes.append(knowledge.get("clinical_note") + " Flag for P&T committee — not a generic therapeutic interchange.")
    peds = (findings.get("pediatric") or {}).get("patients_lt6") or 0
    if peds:
        notes.append(f"{peds} pediatric patient(s) have no suitable ARB alternative — recommend amlodipine consult.")
    hf = (findings.get("indications") or {}).get("heart_failure_post_mi") or 0
    if hf:
        notes.append(f"{hf} heart failure / post-MI patients need a titration protocol, not a direct 50mg switch.")
    if any(cat["key"] == "C" for cat in categories):
        notes.append("Angioedema cohort would be silently converted by a 1:1 SKU swap.")
    return notes


def synthesize_report(
    *,
    shortage_desc: str,
    alternative_desc: str,
    landscape: dict[str, Any],
    knowledge: dict[str, Any],
    categories: list[dict[str, Any]],
    cost: dict[str, Any],
    surprises: list[str],
    branch_id: str,
) -> str:
    total = int(landscape.get("patients") or 0)
    lines = [
        f"### Substitution simulation report",
        f"**{shortage_desc} → {alternative_desc}**",
        "",
        f"Total patients affected: **{total:,}** across {landscape.get('facilities') or 0} facilities.",
        "",
    ]
    for cat in categories:
        icon = {"ok": "✅", "watch": "⚠️", "stop": "🔴", "info": "ℹ️"}.get(cat["severity"], "•")
        pct = f"{cat['share'] * 100:.1f}%" if total else "—"
        lines.append(f"- {icon} **{cat['label']}**: {cat['patients']:,} ({pct}) — {cat['recommendation']}")
    if cost.get("monthly_cost_delta") is not None:
        lines.append("")
        lines.append(
            f"**Cost impact:** +${int(cost['monthly_cost_delta']):,}/month"
            + (
                f" (not +${int(cost['naive_monthly_cost_delta']):,} from a naive unit-price calc)"
                if cost.get("naive_monthly_cost_delta")
                else ""
            )
        )
    if surprises:
        lines.append("")
        lines.append("**Unexpected findings**")
        for note in surprises:
            lines.append(f"- {note}")
    lines.append("")
    lines.append(f"Working simulation: `{branch_id}` · production unchanged until you apply to the live formulary.")
    return "\n".join(lines)


ALLOWED_INVESTIGATIONS = {
    "angioedema_cross_reactivity",
    "renal_function",
    "pediatric_label",
    "potassium_interaction",
    "indication_dosing",
    "allergy_to_alternative",
    "inventory_cover",
}


async def _sql_fetch(
    fetch: Callable[..., Any] | None,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    if fetch is None:
        return []
    try:
        rows = await fetch(sql, params)
        return [dict(row) for row in (rows or [])]
    except Exception as exc:
        print(f"Branch SQL read skipped: {exc}")
        return []


async def _sql_exec(
    execute: Callable[..., Any] | None,
    sql: str,
    params: tuple[Any, ...] = (),
) -> None:
    if execute is None:
        return
    try:
        await execute(sql, params)
    except Exception as exc:
        print(f"Branch SQL write skipped: {exc}")


async def llm_plan(prompt: str, landscape: dict[str, Any], knowledge: dict[str, Any]) -> list[str] | None:
    if store.mock or os.getenv("USE_MOCK_BACKEND", "").lower() == "true":
        return None
    try:
        import httpx
        from databricks.sdk.core import Config

        config = Config()
        model = os.getenv("MODEL_SERVING_ENDPOINT", "databricks-claude-sonnet-4-6")
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You plan a drug-substitution investigation. "
                        "Reply with JSON only: {\"investigations\": [string]}. "
                        "Allowed values: angioedema_cross_reactivity, renal_function, pediatric_label, "
                        "potassium_interaction, indication_dosing, allergy_to_alternative, inventory_cover. "
                        "Choose based on pharmacology, not a fixed checklist. "
                        "If this is an ACE-I to ARB switch, include class-specific checks."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({"request": prompt, "landscape": landscape, "knowledge": knowledge}, default=str),
                },
            ],
            "max_tokens": 300,
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{config.host.rstrip('/')}/serving-endpoints/{model}/invocations",
                headers=config.authenticate(),
                json=payload,
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            planned = json.loads(text[start : end + 1]).get("investigations") or []
            cleaned = [item for item in planned if item in ALLOWED_INVESTIGATIONS]
            return cleaned or None
    except Exception as exc:
        print(f"Agent plan LLM skipped: {exc}")
    return None


async def llm_review(
    prompt: str,
    findings: dict[str, Any],
    knowledge: dict[str, Any],
) -> dict[str, list[str]] | None:
    if store.mock or os.getenv("USE_MOCK_BACKEND", "").lower() == "true":
        return None
    try:
        import httpx
        from databricks.sdk.core import Config

        config = Config()
        model = os.getenv("MODEL_SERVING_ENDPOINT", "databricks-claude-sonnet-4-6")
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are reviewing SQL findings from a Lakebase simulation branch. "
                        "Reply with JSON only: {\"unexpected\": [string], \"next_checks\": [string]}. "
                        "next_checks must use: angioedema_cross_reactivity, renal_function, pediatric_label, "
                        "potassium_interaction, indication_dosing, allergy_to_alternative, inventory_cover. "
                        "Only request checks that the findings did not already settle."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {"request": prompt, "knowledge": knowledge, "findings": findings},
                        default=str,
                    ),
                },
            ],
            "max_tokens": 400,
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(
                f"{config.host.rstrip('/')}/serving-endpoints/{model}/invocations",
                headers=config.authenticate(),
                json=payload,
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"]
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(text[start : end + 1])
            next_checks = [item for item in (parsed.get("next_checks") or []) if item in ALLOWED_INVESTIGATIONS]
            unexpected = [str(item) for item in (parsed.get("unexpected") or []) if str(item).strip()]
            return {"unexpected": unexpected, "next_checks": next_checks}
    except Exception as exc:
        print(f"Agent review LLM skipped: {exc}")
    return None


async def run_agent(
    *,
    prompt: str,
    shortage_item_id: str,
    alternative_item_id: str,
    shortage_desc: str,
    alternative_desc: str,
    branch_id: str,
    create_branch: Callable[..., Any],
    simulation_id: str = "",
    fetch: Callable[..., Any] | None = None,
    execute: Callable[..., Any] | None = None,
    on_progress: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    transcript: list[dict[str, Any]] = []
    sql_ops = 0

    async def progress(detail: str, turn: dict[str, Any] | None = None) -> None:
        if turn:
            transcript.append(turn)
        if on_progress is not None:
            await on_progress(detail, list(transcript))

    async def log_work(phase: str, tool: str, thought: str, result: str, sql_text: str = "", row_count: int | None = None) -> None:
        await _sql_exec(
            execute,
            """INSERT INTO supply_intel.substitution_sim_worklog
               (simulation_id, branch_id, phase, tool, thought, result, sql_text, row_count)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (simulation_id or None, branch_id, phase, tool, thought, result[:2000], sql_text, row_count),
        )

    await create_branch(branch_id)
    await progress(
        f"Reading cohorts on `{branch_id}`",
        {
            "phase": "Isolate",
            "thought": "Stay on the copy-on-write Lakebase branch so production is never queried for this work.",
            "tool": "branch_sql:open",
            "result": f"Working copy `{branch_id}`",
        },
    )

    cohort_sql = (
        "SELECT item_id, facility_id, facility_name, indication, age_band, egfr_band, "
        "angioedema, potassium_concurrent, patient_count "
        "FROM supply_intel.substitution_patient_cohorts WHERE item_id=%s"
    )
    db_cohorts = await _sql_fetch(fetch, cohort_sql, (shortage_item_id,))
    sql_ops += 1 if fetch is not None else 0
    cohorts = db_cohorts or _cohort_rows(shortage_item_id)
    landscape = query_patients(shortage_item_id, {}, rows=cohorts)
    source_tool = "branch_sql:substitution_patient_cohorts" if db_cohorts else "query_patients"
    await log_work(
        "Understand",
        source_tool,
        "Baseline census before any formulary write.",
        f"{landscape.get('patients') or 0} patients / {landscape.get('facilities') or 0} facilities",
        cohort_sql,
        len(cohorts),
    )
    await progress(
        f"Census on the branch: {landscape.get('patients') or 0:,} patients in {landscape.get('facilities') or 0} facilities",
        {
            "phase": "Understand",
            "thought": "Before changing data, gather baseline census from the working copy.",
            "tool": source_tool,
            "result": f"{landscape.get('patients') or 0:,} patients across {landscape.get('facilities') or 0} facilities ({len(cohorts)} cohort rows).",
        },
    )

    drug_sql = "SELECT * FROM supply_intel.drug_knowledge WHERE item_id IN (%s, %s)"
    drug_rows = await _sql_fetch(fetch, drug_sql, (shortage_item_id, alternative_item_id))
    sql_ops += 1 if fetch is not None else 0
    knowledge = lookup_drugs(shortage_item_id, alternative_item_id)
    if drug_rows:
        by_id = {row.get("item_id"): row for row in drug_rows}
        if by_id.get(shortage_item_id) and by_id.get(alternative_item_id):
            knowledge = lookup_drugs(shortage_item_id, alternative_item_id)
            knowledge["from_drug"] = {**knowledge["from_drug"], **by_id[shortage_item_id]}
            knowledge["to_drug"] = {**knowledge["to_drug"], **by_id[alternative_item_id]}
            knowledge["class_switch"] = knowledge["from_drug"].get("pharmacologic_class") != knowledge["to_drug"].get("pharmacologic_class")
    await progress(
        knowledge["clinical_note"],
        {
            "phase": "Understand",
            "thought": knowledge["clinical_note"],
            "tool": "branch_sql:drug_knowledge" if drug_rows else "lookup_drugs",
            "result": f"{(knowledge['from_drug'] or {}).get('pharmacologic_class')} → {(knowledge['to_drug'] or {}).get('pharmacologic_class')}",
        },
    )

    formulary_sql = "SELECT therapeutic_class, active_item_id, active_item_description FROM supply_intel.formulary"
    formulary_rows = await _sql_fetch(fetch, formulary_sql)
    sql_ops += 1 if fetch is not None else 0
    if formulary_rows:
        await log_work("Investigate", "branch_sql:formulary", "Current live formulary on this working copy.", json.dumps(formulary_rows, default=str)[:500], formulary_sql, len(formulary_rows))
        await progress(
            f"Read {len(formulary_rows)} formulary rows on `{branch_id}`",
            {
                "phase": "Investigate",
                "thought": "Confirm what the working copy currently has as the active item before staging a swap.",
                "tool": "branch_sql:formulary",
                "result": "; ".join(f"{row.get('therapeutic_class')}={row.get('active_item_id')}" for row in formulary_rows[:6]),
            },
        )

    await progress("Planning which branch queries to run")
    planned = await llm_plan(prompt, landscape, knowledge)
    planner = "llm" if planned else "rules-from-findings"
    planned = planned or investigations_for(knowledge)
    if "inventory_cover" not in planned:
        planned.append("inventory_cover")
    await progress(
        "Investigation set: " + ", ".join(i.replace("_", " ") for i in planned),
        {
            "phase": "Investigate",
            "thought": "Investigation set expanded from pharmacology, then each check is a query on the branch.",
            "tool": f"planner:{planner}",
            "result": ", ".join(planned),
        },
    )

    findings: dict[str, Any] = {}
    ran: set[str] = set()

    async def run_check(key: str) -> None:
        nonlocal sql_ops
        if key in ran:
            return
        ran.add(key)
        if key == "inventory_cover":
            inv_sql = (
                "SELECT facility_id, facility_name, COALESCE(SUM(on_hand_qty), 0) AS on_hand "
                "FROM supply_intel.inventory_snapshot WHERE item_id=%s "
                "GROUP BY facility_id, facility_name ORDER BY facility_name"
            )
            inv_rows = await _sql_fetch(fetch, inv_sql, (alternative_item_id,))
            sql_ops += 1 if fetch is not None else 0
            census_sql = (
                "SELECT facility_id, facility_name, active_order_count, allergy_flag_count, "
                "contraindication_count, avg_daily_doses "
                "FROM supply_intel.patient_order_census WHERE item_id=%s ORDER BY facility_name"
            )
            census_rows = await _sql_fetch(fetch, census_sql, (shortage_item_id,))
            sql_ops += 1 if fetch is not None else 0
            facilities = census_rows or [
                {"facility_id": row["facility_id"], "facility_name": row["facility_name"], "active_order_count": row["patient_count"]}
                for row in cohorts
            ]
            seen: set[str] = set()
            unique_facilities: list[dict[str, Any]] = []
            for row in facilities:
                fac_id = str(row.get("facility_id") or "")
                if fac_id in seen:
                    continue
                seen.add(fac_id)
                unique_facilities.append(row)
            cover_notes: list[str] = []
            on_hand_by_fac = {str(row.get("facility_id")): int(row.get("on_hand") or 0) for row in inv_rows}
            for fac in unique_facilities:
                fac_id = str(fac.get("facility_id") or "")
                on_hand = on_hand_by_fac.get(fac_id, 0)
                daily = float(fac.get("avg_daily_doses") or fac.get("active_order_count") or 0)
                days = round(on_hand / daily, 1) if daily else None
                note = f"{fac.get('facility_name')}: {on_hand} units" + (f" (~{days}d)" if days is not None else "")
                cover_notes.append(note)
                await log_work(
                    "Investigate",
                    f"branch_sql:inventory:{fac_id}",
                    f"Facility cover for {alternative_item_id}",
                    note,
                    inv_sql,
                    1,
                )
                await progress(
                    f"Cover check on `{branch_id}` · {note}",
                    {
                        "phase": "Investigate",
                        "thought": f"Walk inventory and census for {fac.get('facility_name')} on the working copy.",
                        "tool": f"branch_sql:inventory_snapshot:{fac_id}",
                        "result": note,
                    },
                )
            findings["inventory"] = {
                "facilities": len(unique_facilities),
                "notes": cover_notes,
                "from_branch": bool(inv_rows or census_rows),
            }
            return

        mapped, finding = run_one_investigation(key, shortage_item_id, alternative_item_id, rows=cohorts)
        findings[mapped] = finding
        patients = finding.get("patients")
        if patients is None:
            patients = finding.get("patients_lt6")
        rule = (finding.get("rule") or {}).get("rule")
        result = json.dumps({k: v for k, v in finding.items() if k != "rule"}, default=str)[:280]
        await log_work("Investigate", f"branch_sql:{key}", rule or key, result, cohort_sql, int(patients or 0))
        await progress(
            f"{key.replace('_', ' ')} on `{branch_id}` · {patients or 0} patients",
            {
                "phase": "Investigate",
                "thought": rule or f"Checked {key} against cohort rows on the working copy.",
                "tool": f"{source_tool}:{key}",
                "result": result,
            },
        )
        if mapped == "indications" and int(finding.get("heart_failure_post_mi") or 0) > 0:
            await progress(
                "Recalculating cost after splitting HTN vs HFrEF",
                {
                    "phase": "Simulate",
                    "thought": "Losartan 50mg is not the right equivalency for every indication. Recalculate cost after splitting HTN vs HFrEF.",
                    "tool": "clinical_rules:losartan_hf_titration",
                    "result": finding["rule"]["action"],
                },
            )

    for key in planned:
        await run_check(key)

    await progress("Reviewing branch findings before staging categories")
    review = await llm_review(prompt, findings, knowledge)
    extra = [item for item in ((review or {}).get("next_checks") or []) if item not in ran]
    if extra:
        await progress(
            "Follow-up checks from the branch findings: " + ", ".join(extra),
            {
                "phase": "Investigate",
                "thought": "The model asked for more branch queries after seeing the first result set.",
                "tool": "planner:follow-up",
                "result": ", ".join(extra),
            },
        )
        planned = planned + extra
        for key in extra:
            await run_check(key)

    categories = categorize(shortage_item_id, knowledge, findings)
    cost = corrected_monthly_cost(shortage_item_id, findings)
    surprises = unexpected_findings(knowledge, findings, categories)
    for note in (review or {}).get("unexpected") or []:
        if note not in surprises:
            surprises.append(note)

    for cat in categories:
        await _sql_exec(
            execute,
            """INSERT INTO supply_intel.substitution_sim_categories
               (simulation_id, branch_id, category_key, label, severity, patient_count, recommendation)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                simulation_id or None,
                branch_id,
                cat["key"],
                cat["label"],
                cat["severity"],
                cat["patients"],
                cat["recommendation"],
            ),
        )
        sql_ops += 1 if execute is not None else 0
    await progress(
        "Staged patient categories on the working copy · " + "; ".join(f"{c['key']}: {c['patients']}" for c in categories),
        {
            "phase": "Synthesize",
            "thought": "Write emergent categories onto the branch so the pharmacist can inspect the working copy, not just the chat.",
            "tool": "branch_sql:substitution_sim_categories",
            "result": "; ".join(f"{c['key']}: {c['patients']}" for c in categories) + (f" · {sql_ops} branch SQL ops" if sql_ops else ""),
        },
    )
    report = synthesize_report(
        shortage_desc=shortage_desc,
        alternative_desc=alternative_desc,
        landscape=landscape,
        knowledge=knowledge,
        categories=categories,
        cost=cost,
        surprises=surprises,
        branch_id=branch_id,
    )
    return {
        "planner": planner,
        "transcript": transcript,
        "categories": categories,
        "unexpected": surprises,
        "cost": cost,
        "landscape": landscape,
        "knowledge": knowledge,
        "report_markdown": report,
        "investigations": planned,
        "sql_ops": sql_ops,
        "from_branch": bool(db_cohorts),
    }
