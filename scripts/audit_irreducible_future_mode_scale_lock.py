#!/usr/bin/env python3
"""Audit irreducible-symmetry selection of one future-fibre polar scale."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "irreducible_future_mode_scale_lock_audit.json"


def left_quaternion_generators() -> tuple[np.ndarray, np.ndarray]:
    # Left multiplication by i and j on H ~= R^4. Their real representation is
    # irreducible; right multiplication supplies a commuting complex structure.
    li = np.array(
        [[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]],
        dtype=float,
    )
    lj = np.array(
        [[0, 0, -1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, -1, 0, 0]],
        dtype=float,
    )
    return li, lj


def symmetric_commutant_dimension(generators: tuple[np.ndarray, ...]) -> int:
    # Solve SX=XS together with X=X^T by SVD on the 16 matrix coordinates.
    constraints = []
    eye = np.eye(4)
    for s in generators:
        constraints.append(np.kron(eye, s) - np.kron(s.T, eye))
    for i in range(4):
        for j in range(i + 1, 4):
            row = np.zeros(16)
            row[i + 4 * j] = 1.0
            row[j + 4 * i] = -1.0
            constraints.append(row[None, :])
    matrix = np.vstack(constraints)
    return int(16 - np.linalg.matrix_rank(matrix, tol=1e-10))


def main() -> None:
    li, lj = left_quaternion_generators()
    # Right multiplication by i commutes with the left quaternion action.
    jr = np.array(
        [[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]],
        dtype=float,
    )
    metric = np.eye(4)
    kappa = 3.0
    phase = kappa * metric @ jr
    a = np.linalg.solve(metric, phase)
    polar_square = -(a @ a)

    # Reducible two-plane control: both planes preserve metric and phase but
    # may carry different scales.
    j2 = np.array([[0.0, -1.0], [1.0, 0.0]])
    reducible_a = np.block(
        [[j2, np.zeros((2, 2))], [np.zeros((2, 2)), 0.5 * j2]]
    )
    reducible_scales = np.sqrt(np.linalg.eigvalsh(-(reducible_a @ reducible_a)))

    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_IRREDUCIBLE_MODE_SCALE_LOCK",
        "theorem": {
            "assumptions": [
                "positive future-fibre metric g_plus",
                "nondegenerate phase form omega_plus",
                "one parent symmetry preserves both forms",
                "the occupied real future-fibre representation is irreducible",
            ],
            "conclusion": (
                "the positive polar operator |g_plus^-1 omega_plus| is scalar, "
                "so (g_plus^-1 omega_plus)^2=-kappa^2 I"
            ),
        },
        "irreducible_certificate": {
            "symmetric_commutant_dimension": symmetric_commutant_dimension((li, lj)),
            "phase_invariant_under_generators": bool(
                all(np.allclose(s.T @ phase @ s, phase) for s in (li, lj))
            ),
            "metric_invariant_under_generators": bool(
                all(np.allclose(s.T @ metric @ s, metric) for s in (li, lj))
            ),
            "scalar_lock_residual": float(
                np.linalg.norm(polar_square - kappa**2 * np.eye(4))
            ),
            "selected_kappa": kappa,
        },
        "reducible_control": {
            "mode_scales": reducible_scales.tolist(),
            "single_scale": bool(np.allclose(reducible_scales, reducible_scales[0])),
        },
        "claim_boundary": {
            "proved": "irreducibility plus common metric-phase symmetry forces one polar scale",
            "not_proved": (
                "the physical base-seed parent occupies an irreducible future-fibre orbit, "
                "or the absolute numerical value/SI calibration of kappa"
            ),
        },
        "verdict": "IRREDUCIBILITY_CLOSES_RELATIVE_MODE_SCALE_LOCK; PHYSICAL_OCCUPATION_AND_ABSOLUTE_UNIT_REMAIN_OPEN",
    }

    cert = result["irreducible_certificate"]
    assert cert["symmetric_commutant_dimension"] == 1
    assert cert["phase_invariant_under_generators"] is True
    assert cert["metric_invariant_under_generators"] is True
    assert cert["scalar_lock_residual"] < 1e-12
    assert result["reducible_control"]["single_scale"] is False
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
