#!/usr/bin/env python3
"""Separate BRAC bulk mixing from the required mixed boundary phase incidence."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "brac_vs_boundary_bridge_activation_audit.json"


def main() -> None:
    m, x, y, p, q = sp.symbols("m x y p q", real=True)
    i_k = 1 + m
    brac = sp.Rational(1, 2) * i_k * (x**2 + y**2)
    bulk_mixed = [sp.diff(brac, m, field) for field in (x, y)]

    # A zeroth-order potential contains no derivative variation and therefore
    # contributes no covariant symplectic boundary potential of its own.
    brac_boundary_potential = sp.Integer(0)
    brac_boundary_mixed = sp.diff(brac_boundary_potential, m)

    # Minimal typed positive candidate: a body-dependent kinetic/boundary
    # coefficient. theta=z(m) p dq gives d theta a mixed dm wedge dq term when
    # z'(m) p is nonzero. This is a construction target, not current ownership.
    z = sp.exp(m)
    candidate_mixed_coefficient = sp.diff(z * p, m)

    result = {
        "schema_version": "1.0",
        "status": "TYPE_SEPARATION_BRAC_DOES_NOT_ACTIVATE_BOUNDARY_BRIDGE",
        "brac_bulk": {
            "action": str(brac),
            "mixed_body_field_derivative": [str(v) for v in bulk_mixed],
            "nonzero_on_occupied_nonzero_field": True,
            "supports_existing_morphology_driven_quantum_mixing": True,
        },
        "brac_boundary": {
            "zeroth_order_potential_boundary_theta": str(brac_boundary_potential),
            "mixed_presymplectic_coefficient": str(brac_boundary_mixed),
            "activates_beta_FQ": False,
        },
        "minimal_positive_target": {
            "boundary_one_form": "theta_candidate = z(m) p dq",
            "mixed_coefficient": str(candidate_mixed_coefficient),
            "nonzero_condition": "z'(m) p != 0 on the occupied source",
            "current_parent_ownership": False,
        },
        "claim_boundary": {
            "proved": (
                "the existing BRAC potential gives a nonzero bulk morphology-field Hessian "
                "but cannot by itself generate the mixed boundary phase block beta_FQ"
            ),
            "still_open": (
                "a source-owned body-dependent kinetic/boundary term, or an equivalent "
                "constraint-reduced symplectic incidence, in the actual parent action"
            ),
        },
        "verdict": "EXISTING_BRAC_COUPLING_IS_PHYSICAL_BUT_WRONG_TYPE_FOR_BETA_FQ; KINETIC_BOUNDARY_SOURCE_REMAINS_OPEN",
    }

    assert bulk_mixed == [x, y]
    assert brac_boundary_mixed == 0
    assert candidate_mixed_coefficient == sp.exp(m) * p
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
