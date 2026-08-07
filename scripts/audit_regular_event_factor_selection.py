#!/usr/bin/env python3
"""Audit factor selection by a regular observer-event incidence."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/regular_event_factor_selection_audit.json"

incidences = {
    "null_event": [0.0, 0.0, 0.0],
    "mixed_regular_event": [1.0, 2.0, 1.0],
    "axis_event_0": [1.0, 0.0, 0.0],
    "axis_event_1": [0.0, 3.0, 0.0],
    "axis_event_2": [0.0, 0.0, 2.0],
}

rows = []
for name, amplitudes in incidences.items():
    norm2 = sum(x * x for x in amplitudes)
    weights = [x * x / norm2 for x in amplitudes] if norm2 else [0.0, 0.0, 0.0]
    support = [j for j, weight in enumerate(weights) if weight > 0.0]
    rows.append(
        {
            "event": name,
            "regular": norm2 > 0.0,
            "weights": weights,
            "support": support,
            "exact_recovery_eligible": len(support) == 1,
            "selected_factor": support[0] if len(support) == 1 else None,
        }
    )

result = {
    "schema_version": "1.0",
    "weight_law": "w_j=||P_j j_OS_evt||^2 / sum_k ||P_k j_OS_evt||^2",
    "rows": rows,
    "checks": {
        "null_event_selects_no_factor": rows[0]["selected_factor"] is None,
        "mixed_regular_event_fails_exact_recovery": rows[1]["regular"] and not rows[1]["exact_recovery_eligible"],
        "each_axis_event_selects_one_factor": [row["selected_factor"] for row in rows[2:]] == [0, 1, 2],
        "regular_exact_recovery_events_have_vertex_weights": all(
            sorted(row["weights"]) == [0.0, 0.0, 1.0]
            for row in rows if row["regular"] and row["exact_recovery_eligible"]
        ),
    },
    "status": {
        "incidence_source": "SHR-QOBSEVENT1 supplies a nonzero compact incidence for a regular finite event on adopted E1/EREM",
        "factor_selection": "exact recovery restricts the normalized incidence to one factor axis, whose support designates the M2 embedding",
        "mixed_control": "a regular mixed-factor event is allowed as incidence but cannot be promoted to an exact full-qubit A8b terminal",
        "minimal_parent": "does not force E1/EREM occupation or exact recovery",
        "chirality": "independent open discrete selection",
    },
    "verdict": "REGULAR_EVENT_INCIDENCE_PLUS_EXACT_RECOVERY_DESIGNATES_ONE_FACTOR_WITHOUT_A_NEW_LABEL",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
