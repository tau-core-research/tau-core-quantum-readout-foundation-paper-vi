#!/usr/bin/env python3
"""Audit exact logical recovery together with lossy realization descent."""

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/protected_logical_recovery_split_audit.json"

rho0 = np.array([[1.0, 0.0], [0.0, 0.0]])
rho1 = np.array([[0.0, 0.0], [0.0, 1.0]])
rho_plus = 0.5 * np.array([[1.0, 1.0], [1.0, 1.0]])
g0 = rho0.copy()
g1 = rho1.copy()
tau_g = 0.5 * np.eye(2)


def partial_trace_g(rho_lg: np.ndarray) -> np.ndarray:
    return np.trace(rho_lg.reshape(2, 2, 2, 2), axis1=1, axis2=3)


def embed(rho_l: np.ndarray) -> np.ndarray:
    return np.kron(rho_l, tau_g)


logical_states = [rho0, rho1, rho_plus]
logical_recovery_errors = [
    float(np.max(np.abs(embed(partial_trace_g(embed(rho))) - embed(rho))))
    for rho in logical_states
]

body_a = np.kron(rho_plus, g0)
body_b = np.kron(rho_plus, g1)
readout_a = partial_trace_g(body_a)
readout_b = partial_trace_g(body_b)

result = {
    "schema_version": "1.0",
    "construction": "body H_L tensor H_G; observer descent Tr_G; protected embedding rho_L -> rho_L tensor I_G/2",
    "checks": {
        "logical_code_recovers_exactly": bool(max(logical_recovery_errors) < 1e-12),
        "distinct_realizations_collapse_to_same_readout": bool(np.max(np.abs(readout_a - readout_b)) < 1e-12),
        "body_realizations_are_distinct": bool(np.linalg.norm(body_a - body_b) > 1e-12),
        "descent_is_globally_noninjective": bool(np.max(np.abs(readout_a - readout_b)) < 1e-12),
        "logical_coherence_is_retained": bool(abs(readout_a[0, 1] - 0.5) < 1e-12),
    },
    "theorem_status": {
        "compatibility": "lossy body descent and exact recovery of a protected logical algebra are compatible",
        "A8b_selector_scope": "full occupied logical ROOT operator system, not the complete body realization space",
        "general_condition": "the complementary/environment output must be independent of the protected logical state",
        "physical_selection": "requires the base-seed law to place ROOT information wholly in the protected logical factor",
    },
    "verdict": "EXACT_LOGICAL_RECOVERY_IS_COMPATIBLE_WITH_GLOBAL_OBSERVER_INFORMATION_LOSS",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
