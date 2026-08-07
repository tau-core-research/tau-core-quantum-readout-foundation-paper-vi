#!/usr/bin/env python3
"""Audit future-extension flexibility and the extra phase requirement."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "future_extension_quantum_carrier_audit.json"


def nullity(matrix: np.ndarray) -> int:
    return int(matrix.shape[1] - np.linalg.matrix_rank(matrix, tol=1e-12))


def main() -> None:
    # Positive body stiffness. Orientation alone does not change this quadratic
    # form, so future and reversed tangent balls have equal volume.
    stiffness = np.diag([1.0, 2.0, 3.0, 4.0])
    determinant = float(np.linalg.det(stiffness))
    forward_volume_factor = determinant ** -0.5
    backward_volume_factor = determinant ** -0.5

    # The occupied seed/current boundary fixes all backward degrees, whereas
    # only two independent restrictions constrain compatible forward extensions.
    backward_restriction = np.eye(4)
    forward_restriction = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])
    future_basis = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    future_metric = future_basis.T @ stiffness @ future_basis

    # A Hessian supplies only a symmetric metric. A separately source-owned
    # phase form is needed. Construct the canonical compatible form explicitly.
    sqrt_g = np.diag(np.sqrt(np.diag(future_metric)))
    inv_sqrt_g = np.linalg.inv(sqrt_g)
    j0 = np.array([[0.0, -1.0], [1.0, 0.0]])
    complex_structure = inv_sqrt_g @ j0 @ sqrt_g
    phase_form = future_metric @ complex_structure
    induced = np.linalg.inv(future_metric) @ phase_form

    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_FUTURE_EXTENSION_QUANTUM_CARRIER",
        "orientation_only_control": {
            "body_stiffness_eigenvalues": np.linalg.eigvalsh(stiffness).tolist(),
            "forward_volume_factor": forward_volume_factor,
            "backward_volume_factor": backward_volume_factor,
            "future_is_larger_from_orientation_and_stiffness_alone": False,
        },
        "boundary_conditioned_extension_fibers": {
            "backward_restriction_rank": int(np.linalg.matrix_rank(backward_restriction)),
            "backward_fiber_dimension": nullity(backward_restriction),
            "forward_restriction_rank": int(np.linalg.matrix_rank(forward_restriction)),
            "forward_fiber_dimension": nullity(forward_restriction),
            "future_fiber_is_strictly_larger": nullity(forward_restriction) > nullity(backward_restriction),
        },
        "future_carrier": {
            "metric": future_metric.tolist(),
            "metric_positive": bool(np.all(np.linalg.eigvalsh(future_metric) > 0)),
            "hessian_alone_supplies_phase_form": False,
            "source_owned_phase_form": phase_form.tolist(),
            "phase_form_antisymmetric": bool(np.allclose(phase_form.T, -phase_form)),
            "complex_lock_residual": float(np.linalg.norm(induced @ induced + np.eye(2))),
        },
        "theorem_boundary": {
            "proved": (
                "seed/current boundary asymmetry can make the compatible future-extension fiber "
                "strictly larger, and the restricted Hessian supplies its positive metric"
            ),
            "not_proved": (
                "the actual physical base-seed body has this rank asymmetry or sources the required "
                "phase curvature and coherent terminal composition"
            ),
        },
        "verdict": (
            "FUTURE_FLEXIBILITY_REQUIRES_ORIENTED_BOUNDARY_FIBER; "
            "QUANTUM_STRUCTURE_ALSO_REQUIRES_SOURCE_OWNED_PHASE_LOCK"
        ),
    }

    assert np.isclose(forward_volume_factor, backward_volume_factor)
    assert result["boundary_conditioned_extension_fibers"]["backward_fiber_dimension"] == 0
    assert result["boundary_conditioned_extension_fibers"]["forward_fiber_dimension"] == 2
    assert result["future_carrier"]["metric_positive"] is True
    assert result["future_carrier"]["phase_form_antisymmetric"] is True
    assert result["future_carrier"]["complex_lock_residual"] < 1e-12
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
