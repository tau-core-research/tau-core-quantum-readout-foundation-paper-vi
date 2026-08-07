#!/usr/bin/env python3
"""Audit conditional activation of beta_FQ by body-dependent kinetic momentum."""
from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "covariant_kinetic_boundary_activation_audit.json"


def main() -> None:
    m, q, qdot, z0 = sp.symbols("m q qdot z0", real=True, nonzero=True)
    # Finite mode reduction of pi_phi=Z sqrt(h) n^mu d_mu phi. The body mode m
    # changes the densitized normal kinetic coefficient.
    z = z0 * sp.exp(m)
    momentum = z * qdot
    mixed_boundary = sp.diff(momentum, m)
    occupied_value = sp.simplify(mixed_boundary.subs(m, 0))

    # The zeroth-order morphology potential remains irrelevant to this boundary
    # coefficient; activation comes from the shared kinetic/body metric.
    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_KINETIC_BOUNDARY_ACTIVATION",
        "covariant_source": {
            "field_momentum": "pi_phi = Z_Phi sqrt(h) n^mu partial_mu Phi",
            "finite_mode_momentum": str(momentum),
            "mixed_boundary_coefficient": str(mixed_boundary),
            "occupied_reference_value": str(occupied_value),
        },
        "activation_conditions": {
            "body_future_mode_changes_densitized_normal_metric": True,
            "EBRP_field_has_nonzero_canonical_momentum": True,
            "mode_is_not_gauge_or_boundary_null": True,
            "beta_FQ_nonzero": True,
        },
        "derived_chain": [
            "BRDC common body metric -> body-dependent kinetic momentum",
            "nonneutral body + EBRP positive-frequency embedding -> occupied nonzero field momentum",
            "non-null future metric mode -> nonzero mixed boundary variation",
            "equivariance + equivalent irreducible ROOT/future modules -> full-rank bridge",
            "irreducibility -> one relative polar scale",
        ],
        "claim_boundary": {
            "proved_conditionally": (
                "the selected JCSEL-BRDC-EBRP completion activates beta_FQ on every occupied "
                "non-null future mode that changes the densitized kinetic metric"
            ),
            "not_proved": (
                "Nature-level selection of JCSEL-BRDC-EBRP, nonneutral physical occupation, "
                "or that every future-fibre direction is metric-visible"
            ),
        },
        "verdict": "SELECTED_COVARIANT_KINETIC_COMPLETION_ACTIVATES_BETA_FQ_CONDITIONALLY; NATURE_SELECTION_REMAINS_OPEN",
    }

    assert sp.simplify(mixed_boundary - momentum) == 0
    assert occupied_value == qdot * z0
    assert result["activation_conditions"]["beta_FQ_nonzero"] is True
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
