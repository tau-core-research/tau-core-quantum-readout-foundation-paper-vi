#!/usr/bin/env python3
"""Audit boundedness of the morphology-conditioned future possibility body."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "bounded_future_possibility_body_audit.json"


def unit_ball_volume(n: int) -> float:
    return math.pi ** (n / 2) / math.gamma(n / 2 + 1)


def main() -> None:
    # Restricted body Hessian on a finite future fibre.
    eigenvalues = np.array([1.0, 1.5, 2.0, 3.0])
    cutoff = 2.0
    axes = np.sqrt(cutoff / eigenvalues)
    volume = unit_ball_volume(len(eigenvalues)) * float(np.prod(axes))
    resolution = 0.1
    cell_upper_bound = int(np.prod(np.ceil(2 * axes / resolution) + 1))

    result = {
        "schema_version": "1.0",
        "status": "BOUNDED_MORPHOLOGICAL_FUTURE_BODY",
        "definition": (
            "E_plus(x,Lambda)=F_plus intersect C_plus intersect D_M "
            "intersect {v:<v,g_plus v><=Lambda}"
        ),
        "sufficient_conditions": [
            "finite-dimensional future fibre",
            "positive-definite restricted body Hessian",
            "finite morphology/action cutoff",
            "closed causal and morphology-admissibility constraints",
        ],
        "finite_certificate": {
            "future_fibre_dimension": len(eigenvalues),
            "hessian_eigenvalues": eigenvalues.tolist(),
            "finite_cutoff": cutoff,
            "ellipsoid_axes": axes.tolist(),
            "ellipsoid_volume": volume,
            "observer_resolution": resolution,
            "finite_resolved_cell_upper_bound": cell_upper_bound,
        },
        "claim_boundary": {
            "proved": (
                "under the stated local conditions the future possibility body is compact, "
                "finite-volume and has finitely many observer-resolved cells"
            ),
            "not_proved": (
                "global compactness across singular/topology-changing parent regions, a "
                "universal cutoff, or the numerical capacity of the physical observer"
            ),
        },
        "verdict": "FUTURE_FLUIDITY_IS_RELATIVE_AND_BODY_BOUNDED_NOT_INFINITE",
    }

    assert np.all(eigenvalues > 0)
    assert math.isfinite(volume) and volume > 0
    assert cell_upper_bound > 0
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
