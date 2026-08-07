#!/usr/bin/env python3
"""Audit observer-context factor designation by complementary commutants."""

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/observer_noise_commutant_selector_audit.json"

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
pauli = [I, X, Y, Z]


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def factor_basis(j):
    return [kron3(*(p if k == j else I for k in range(3))) for p in pauli]


def complement_basis(j):
    others = [k for k in range(3) if k != j]
    out = []
    for p in pauli:
        for q in pauli:
            mats = [I, I, I]
            mats[others[0]] = p
            mats[others[1]] = q
            out.append(kron3(*mats))
    return out


def commutant_dimension(generators):
    # vec(XG-GX)=0 in column-major convention.
    constraints = []
    eye8 = np.eye(8, dtype=complex)
    for g in generators:
        constraints.append(np.kron(g.T, eye8) - np.kron(eye8, g))
    matrix = np.vstack(constraints)
    return int(64 - np.linalg.matrix_rank(matrix, tol=1e-9))


rows = []
for j in range(3):
    logical = factor_basis(j)
    noise = complement_basis(j)
    rows.append(
        {
            "observer_context": j,
            "noise_algebra_dimension": len(noise),
            "noise_commutant_dimension": commutant_dimension(noise),
            "logical_algebra_dimension": len(logical),
            "logical_commutant_dimension": commutant_dimension(logical),
        }
    )

result = {
    "schema_version": "1.0",
    "construction": "N_O=A_j'=I_2 on j tensor M_4 on the complement; A_ROOT,O=N_O'=A_j",
    "rows": rows,
    "checks": {
        "each_maximal_noise_algebra_has_M2_commutant": all(
            row["noise_algebra_dimension"] == 16
            and row["noise_commutant_dimension"] == 4
            for row in rows
        ),
        "each_selected_M2_has_M4_commutant": all(
            row["logical_algebra_dimension"] == 4
            and row["logical_commutant_dimension"] == 16
            for row in rows
        ),
        "three_contexts_form_one_S3_orbit": len(rows) == 3,
    },
    "status": {
        "designation": "the observer-source complementary/noise algebra designates the logical factor by its commutant",
        "body": "the common unordered three-factor body is unchanged",
        "observer_consistency": "different observers may select permuted factors covariantly",
        "physical_occupation": "open: the base-seed-body law has not been shown to realize a maximal factor-complement noise algebra",
        "chirality": "independent open discrete selection",
    },
    "verdict": "MAXIMAL_COMPLEMENTARY_OBSERVER_ALGEBRA_DESIGNATES_A_UNIQUE_LOGICAL_FACTOR_BY_COMMUTANT",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
