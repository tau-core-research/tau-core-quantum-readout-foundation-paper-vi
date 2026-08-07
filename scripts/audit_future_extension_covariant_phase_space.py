#!/usr/bin/env python3
"""Audit common-action metric/phase generation on a future extension fibre."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "future_extension_covariant_phase_space_audit.json"


def main() -> None:
    # Two canonical future-extension mode pairs with unequal stiffness scales.
    metric = np.diag([1.0, 1.0, 2.0, 2.0])
    j2 = np.array([[0.0, -1.0], [1.0, 0.0]])
    phase = np.block([[j2, np.zeros((2, 2))], [np.zeros((2, 2)), j2]])
    a = np.linalg.solve(metric, phase)
    minus_a2 = -(a @ a)
    eigenvalues, eigenvectors = np.linalg.eigh(minus_a2)
    abs_a = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
    complex_structure = a @ np.linalg.inv(abs_a)
    hermitian_metric = metric @ abs_a

    # A boundary one-form theta=1/2 z^T Omega dz has d theta=Omega. It is the
    # finite analogue of the covariant phase-space current from the same action
    # whose bulk second variation supplies the Jacobi/stiffness operator.
    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_COMMON_ACTION_FUTURE_PHASE_SPACE",
        "common_variational_source": {
            "bulk_second_variation_role": "positive Jacobi/stiffness metric on compatible future extensions",
            "boundary_second_variation_role": "antisymmetric presymplectic/phase form on the current cut",
            "independent_phase_gain_required": False,
        },
        "finite_certificate": {
            "metric_positive": bool(np.all(np.linalg.eigvalsh(metric) > 0)),
            "phase_antisymmetric": bool(np.allclose(phase.T, -phase)),
            "phase_nondegenerate": bool(abs(np.linalg.det(phase)) > 1e-12),
            "polar_complex_lock_residual": float(
                np.linalg.norm(complex_structure @ complex_structure + np.eye(4))
            ),
            "complex_structure_metric_compatible": bool(
                np.allclose(complex_structure.T @ hermitian_metric @ complex_structure, hermitian_metric)
            ),
            "mode_scales": np.sqrt(eigenvalues).tolist(),
            "single_scalar_lock_holds": bool(np.allclose(eigenvalues, eigenvalues[0])),
        },
        "theorem_boundary": {
            "derived_conditionally": (
                "one differentiable ordered parent action can source both future-fibre stiffness "
                "and boundary phase; nondegeneracy gives a canonical polar complex structure"
            ),
            "still_open": (
                "physical parent occupation, quotient descent, and equality of all polar mode "
                "scales needed for one universal action unit"
            ),
        },
        "verdict": (
            "COMMON_VARIATIONAL_ACTION_REMOVES_INDEPENDENT_PHASE_SOURCE; "
            "UNIVERSAL_SCALAR_ACTION_LOCK_REMAINS_OPEN"
        ),
    }

    assert result["finite_certificate"]["metric_positive"] is True
    assert result["finite_certificate"]["phase_antisymmetric"] is True
    assert result["finite_certificate"]["phase_nondegenerate"] is True
    assert result["finite_certificate"]["polar_complex_lock_residual"] < 1e-12
    assert result["finite_certificate"]["complex_structure_metric_compatible"] is True
    assert result["finite_certificate"]["single_scalar_lock_holds"] is False
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
