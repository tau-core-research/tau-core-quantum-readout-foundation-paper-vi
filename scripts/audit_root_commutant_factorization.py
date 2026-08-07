#!/usr/bin/env python3
"""Audit ROOT/commutant factorization on the occupied M8 block."""

import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/root_commutant_factorization_audit.json"
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def k3(a, b, c):
    return np.kron(np.kron(a, b), c)


def rank(mats):
    return int(np.linalg.matrix_rank(np.stack([m.ravel() for m in mats]), tol=1e-10))


pauli = [I2, X, Y, Z]
logical = [k3(a, I2, I2) for a in pauli]
gauge = [k3(I2, b, c) for b in pauli for c in pauli]
products = [a @ b for a in logical for b in gauge]
eye8 = np.eye(8, dtype=complex)
constraints = [np.kron(g.T, eye8) - np.kron(eye8, g) for g in logical]
commutant_dim = int(64 - np.linalg.matrix_rank(np.vstack(constraints), tol=1e-10))

result = {
    "schema_version": "1.0",
    "occupied_block": "M8(C)=M2(C) tensor M4(C)",
    "logical_ROOT_algebra_dimension": rank(logical),
    "realization_commutant_dimension": rank(gauge),
    "logical_commutant_dimension_in_M8": commutant_dim,
    "joint_generated_dimension": rank(products),
    "checks": {
        "logical_and_realization_algebras_commute": bool(all(np.allclose(a @ b, b @ a) for a in logical for b in gauge)),
        "realization_algebra_is_full_logical_commutant": bool(rank(gauge) == commutant_dim == 16),
        "logical_and_commutant_generate_full_occupied_block": bool(rank(products) == 64),
        "logical_factor_has_M2_dimension": bool(rank(logical) == 4),
        "realization_factor_has_M4_dimension": bool(rank(gauge) == 16),
    },
    "theorem_status": {
        "factorization": "a selected ROOT M2 factor canonically determines its M4 realization commutant",
        "recovery_split": "tracing the commutant can lose realization data while preserving the ROOT factor",
        "physical_selection": "the current parent still must select and occupy the ROOT M2 factor/Clifford flag",
    },
    "verdict": "SELECTED_ROOT_FACTOR_CANONICALLY_DETERMINES_THE_PROTECTED_LOGICAL_REALIZATION_SPLIT",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
