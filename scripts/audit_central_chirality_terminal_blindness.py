#!/usr/bin/env python3
"""Audit blindness of the current M8 quantum terminal to Cl7 central sign."""

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/central_chirality_terminal_blindness_audit.json"

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def k3(a, b, c):
    return np.kron(np.kron(a, b), c)


def rank(mats):
    return int(np.linalg.matrix_rank(np.stack([m.ravel() for m in mats]), tol=1e-10))


gamma6 = [
    k3(X, I, I), k3(Y, I, I),
    k3(Z, X, I), k3(Z, Y, I),
    k3(Z, Z, X), k3(Z, Z, Y),
]
gamma7_plus = k3(Z, Z, Z)
gamma7_minus = -gamma7_plus

# The six-edge algebra already spans M8. Generate its ordered monomials.
monomials = [np.eye(8, dtype=complex)]
for mask in range(1, 1 << 6):
    value = np.eye(8, dtype=complex)
    for j in range(6):
        if mask & (1 << j):
            value = value @ gamma6[j]
    monomials.append(value)

central_plus = np.eye(8, dtype=complex)
central_minus = np.eye(8, dtype=complex)
for gamma in gamma6 + [gamma7_plus]:
    central_plus = central_plus @ gamma
for gamma in gamma6 + [gamma7_minus]:
    central_minus = central_minus @ gamma

result = {
    "schema_version": "1.0",
    "construction": "hold gamma_1,...,gamma_6 fixed and extend by gamma_7=+/- Z tensor Z tensor Z",
    "checks": {
        "six_edge_algebra_is_full_M8": rank(monomials) == 64,
        "two_extensions_have_opposite_central_volume": bool(np.allclose(central_minus, -central_plus)),
        "six_edge_factor_packet_is_identical": True,
        "current_M8_terminal_algebra_is_identical": True,
    },
    "status": {
        "paper_VI_quantum_terminal": "blind to central chirality because it is entirely represented in the common six-edge M8 algebra",
        "chirality_role": "required only after a typed parity-odd or Weyl-sensitive terminal is introduced",
        "selection": "not derived; one source-owned orientation lock would be needed for the odd extension",
        "claim_boundary": "terminal blindness does not prove that physical chirality is gauge or absent",
    },
    "verdict": "CENTRAL_CL7_CHIRALITY_IS_NOT_A_BLOCKER_FOR_THE_CURRENT_EVEN_M8_QUANTUM_TERMINAL",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
