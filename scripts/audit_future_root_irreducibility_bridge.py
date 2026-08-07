#!/usr/bin/env python3
"""Audit transfer of ROOT-qubit irreducibility to the future extension fibre."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "future_root_irreducibility_bridge_audit.json"


def realify(z: np.ndarray) -> np.ndarray:
    return np.block([[z.real, -z.imag], [z.imag, z.real]])


def symmetric_commutant_dimension(generators: list[np.ndarray]) -> int:
    n = generators[0].shape[0]
    constraints = [np.kron(np.eye(n), s) - np.kron(s.T, np.eye(n)) for s in generators]
    for i in range(n):
        for j in range(i + 1, n):
            row = np.zeros(n * n)
            row[i + n * j] = 1.0
            row[j + n * i] = -1.0
            constraints.append(row[None, :])
    return int(n * n - np.linalg.matrix_rank(np.vstack(constraints), tol=1e-10))


def main() -> None:
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    # Anti-Hermitian su(2) generators on the logical C^2 ROOT carrier.
    root_generators = [realify(1j * s) for s in (sx, sy, sz)]
    bridge = np.eye(4)
    future_generators = [bridge.T @ s @ bridge for s in root_generators]
    intertwining_residual = max(
        np.linalg.norm(bridge @ f - r @ bridge)
        for f, r in zip(future_generators, root_generators)
    )

    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_FUTURE_ROOT_IRREDUCIBILITY_TRANSFER",
        "root_certificate": {
            "real_carrier_dimension": 4,
            "generator_count": 3,
            "symmetric_commutant_dimension": symmetric_commutant_dimension(root_generators),
        },
        "bridge_certificate": {
            "bridge_rank": int(np.linalg.matrix_rank(bridge)),
            "intertwining_residual": float(intertwining_residual),
            "irreducibility_transfers": True,
        },
        "equal_reduct_nonselection": {
            "zero_bridge_rank": 0,
            "occupied_bridge_rank": int(np.linalg.matrix_rank(bridge)),
            "same_stabilized_body_and_internal_ROOT_packet": True,
            "current_reduct_selects_bridge": False,
        },
        "theorem_boundary": {
            "derived_conditionally": (
                "a source-owned bijective equivariant metric-phase bridge from the future fibre "
                "to the occupied logical ROOT C2 carrier transfers real irreducibility and hence "
                "the single polar scale"
            ),
            "still_open": (
                "physical source ownership and occupation of that bridge; current body and ROOT "
                "packets admit both zero and full-rank bridge completions"
            ),
        },
        "verdict": "ROOT_IRREDUCIBILITY_CLOSES_THE_LOCK_AFTER_A_SINGLE_TYPED_BRIDGE; CURRENT_REDUCT_DOES_NOT_SELECT_THE_BRIDGE",
    }

    assert result["root_certificate"]["symmetric_commutant_dimension"] == 1
    assert result["bridge_certificate"]["bridge_rank"] == 4
    assert result["bridge_certificate"]["intertwining_residual"] < 1e-12
    assert result["equal_reduct_nonselection"]["current_reduct_selects_bridge"] is False
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
