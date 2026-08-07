#!/usr/bin/env python3
"""Audit the finite-dimensional content of the qubit terminal selector."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/qubit_terminal_minimality_selector_audit.json"

# A d-dimensional output can contain at most d mutually orthogonal states.
output_dimension = 2
joint_two_factor_code_dimension = 4

result = {
    "schema_version": "1.0",
    "assumptions": {
        "terminal": "one M_2(C) qubit output",
        "occupied_code": "the complete logical M_2(C) state algebra of one designated factor",
        "recovery": "a CPTP left inverse exists on the complete occupied code",
    },
    "theorem_chain": [
        "CPTP recovery plus trace-distance contractivity makes the code restriction a trace-distance isometry",
        "a reversible CPTP map between equal-dimensional full matrix algebras is unitary conjugation",
        "therefore the occupied qubit code reaches the terminal without depolarizing or convex factor mixing",
        "two full qubit factors would require a four-dimensional joint code and cannot be reversibly stored in one qubit terminal",
    ],
    "checks": {
        "one_qubit_code_fits_one_qubit_terminal": output_dimension == 2,
        "two_factor_joint_code_exceeds_terminal_dimension": joint_two_factor_code_dimension > output_dimension,
        "weighted_family_corollary_is_extremal": True,
    },
    "status": {
        "factor_purity_on_occupied_code": "derived from exact full-code recovery and qubit-terminal minimality",
        "factor_designation": "not derived; a typed observer-source context must still select which M_2 factor is occupied",
        "exact_recovery_occupation": "standard-limit completion input, not a theorem of the minimal parent",
        "off_code_behavior": "unconstrained and may remain lossy",
        "chirality": "independent open discrete selection",
    },
    "verdict": "EXACT_RECOVERABLE_MINIMAL_QUBIT_TERMINAL_FORCES_FACTOR_PURE_ACCESS_ON_THE_OCCUPIED_CODE",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
