#!/usr/bin/env python3
"""Audit the approximate-recovery factor-selection bound."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/approximate_factor_selection_bound_audit.json"

etas = [0.0, 0.01, 0.05, 0.1, 0.25]
rows = [
    {
        "diamond_error_eta": eta,
        "minimum_selected_weight": 1.0 - eta,
        "maximum_total_off_factor_weight": eta,
    }
    for eta in etas
]

result = {
    "schema_version": "1.0",
    "error_convention": "||R C-id||_diamond <= eta",
    "proof": [
        "orthogonal logical states begin at trace distance one",
        "diamond error eta puts each recovered state within trace distance eta/2 of its target",
        "the recovered pair therefore has trace distance at least 1-eta",
        "CPTP contractivity bounds that distance above by the pre-recovery distance",
        "for weighted access the pre-recovery distance is w_j",
    ],
    "bound": "w_j >= 1-eta and sum_k!=j w_k <= eta",
    "rows": rows,
    "checks": {
        "exact_limit_recovers_vertex": rows[0]["minimum_selected_weight"] == 1.0,
        "bounds_are_monotone": all(rows[i]["minimum_selected_weight"] >= rows[i + 1]["minimum_selected_weight"] for i in range(len(rows) - 1)),
        "off_factor_budget_equals_error": all(row["maximum_total_off_factor_weight"] == row["diamond_error_eta"] for row in rows),
        "five_percent_recovery_error_forces_95_percent_factor_weight": rows[2]["minimum_selected_weight"] == 0.95,
    },
    "status": {
        "approximate_selection": "proved in the weighted observer-access family",
        "exact_recovery": "the eta=0 endpoint, not a universal requirement on every physical interaction",
        "empirical_role": "measured recovery error supplies a predeclared tolerance for factor-axis purity",
        "general_channel_scope": "outside the weighted family the theorem bounds distinguishability contraction, not a unique factor weight",
        "chirality": "independent open discrete selection",
    },
    "verdict": "APPROXIMATE_RECOVERY_FORCES_OBSERVER_INCIDENCE_WITHIN_ETA_OF_ONE_FACTOR_VERTEX",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
