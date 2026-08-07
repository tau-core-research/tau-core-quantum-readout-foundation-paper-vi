#!/usr/bin/env python3
"""Audit the finite range and non-selection of the CHDF--Uhlmann connector."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/chdf_uhlmann_range_and_selection_audit.json"


def radius(x: float) -> float:
    return math.sqrt(x - x * x / 4.0)


def chord(r: float) -> float:
    return 2.0 * (1.0 - math.sqrt(max(0.0, 1.0 - r * r)))


grid = [0.0, 0.25, 0.5, 1.0, 1.5, 1.75, 2.0]
rows = []
for x in grid:
    r = radius(x)
    rows.append({"x_A": x, "bloch_radius": r, "x_Q": chord(r), "error": abs(chord(r) - x)})

x_control = 1.0
r_control = radius(x_control)
counterfamily = [
    {"gamma": gamma, "x_Q": chord(gamma * r_control)}
    for gamma in [0.0, 0.25, 0.5, 0.75, 1.0]
]
x_out = 2.25
r_out = radius(x_out)
out_chord = chord(r_out)

result = {
    "schema_version": "1.0",
    "source": "CHDF body-work theorem plus normalized symmetric-qubit Uhlmann carrier",
    "convention": "x_Q=2(1-root_fidelity), so 0<=x_Q<=2",
    "realization_law": "r(x)^2=x-x^2/4",
    "realization_grid": rows,
    "depolarizing_counterfamily_at_x_A_1": counterfamily,
    "out_of_range_control": {"x_A": x_out, "formal_radius": r_out, "actual_x_Q": out_chord},
    "checks": {
        "exact_realization_on_closed_range": all(row["error"] < 1e-12 for row in rows),
        "normalized_uhlmann_chord_is_bounded_by_two": all(row["x_Q"] <= 2.0 for row in rows),
        "formal_continuation_above_two_uses_wrong_branch": abs(out_chord - x_out) > 1e-6,
        "cptp_depolarization_does_not_select_unique_chord": len({round(row["x_Q"], 12) for row in counterfamily}) > 1,
        "identity_endpoint_recovers_A8b_at_control": abs(counterfamily[-1]["x_Q"] - x_control) < 1e-12,
    },
    "theorem_status": {
        "existence": "proved for the occupied sector 0 <= x_A <= 2",
        "global_identity": "impossible for an unbounded CHDF action and normalized Uhlmann chord",
        "physical_selection": "not implied by positivity, normalization, or CPTP descent",
        "remaining_source_law": "select V_phys=V_r(x), or derive a bounded replacement for x_A",
    },
    "verdict": "BOUNDED_A8B_REALIZATION_EXISTS_BUT_PHYSICAL_CONNECTOR_SELECTION_REMAINS_OPEN",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
