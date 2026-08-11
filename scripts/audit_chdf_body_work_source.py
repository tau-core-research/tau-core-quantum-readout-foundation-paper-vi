#!/usr/bin/env python3
"""Verify the exact CHDF quotient body-work form used by Paper VI."""

import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/chdf_body_work_source_audit.json"

y_r, y_t1, y_t2, s = sp.symbols("y_r y_t1 y_t2 s", real=True)
k_r = sp.Rational(59, 64) - sp.sqrt(3) / 12
k_t = 1 + sp.sqrt(3) / 24
coordinates = sp.Matrix([y_r, y_t1, y_t2])
K = sp.diag(k_r, k_t, k_t)
action = sp.expand((coordinates.T * K * coordinates)[0] / 2)
force = sp.Matrix([sp.diff(action, q) for q in coordinates])
hessian = force.jacobian(coordinates)

endpoint = {y_r: sp.Rational(2, 5), y_t1: -sp.Rational(1, 3), y_t2: sp.Rational(1, 4)}
straight = sp.Matrix([s * endpoint[q] for q in coordinates])
straight_integral = sp.integrate(
    (force.subs(dict(zip(coordinates, straight))).T * sp.diff(straight, s))[0], (s, 0, 1)
)
segments = [
    sp.Matrix([s * endpoint[y_r], 0, 0]),
    sp.Matrix([endpoint[y_r], s * endpoint[y_t1], 0]),
    sp.Matrix([endpoint[y_r], endpoint[y_t1], s * endpoint[y_t2]]),
]
piecewise_integral = sum(
    sp.integrate(
        (force.subs(dict(zip(coordinates, segment))).T * sp.diff(segment, s))[0],
        (s, 0, 1),
    )
    for segment in segments
)
endpoint_action = action.subs(endpoint)

result = {
    "schema_version": "1.0",
    "source": "WR-T21 CHDF minimum-action quotient theorem",
    "radial_stiffness_exact": str(k_r),
    "tangent_stiffness_exact": str(k_t),
    "action": str(action),
    "body_work_form_components": [str(value) for value in force],
    "checks": {
        "positive_radial_stiffness": bool(k_r > 0),
        "positive_tangent_stiffness": bool(k_t > 0),
        "hessian_equals_K_leaf": hessian == K,
        "one_form_is_closed": sp.simplify(hessian - hessian.T) == sp.zeros(3),
        "straight_integral_equals_endpoint_action": sp.simplify(straight_integral - endpoint_action) == 0,
        "piecewise_integral_equals_endpoint_action": sp.simplify(piecewise_integral - endpoint_action) == 0,
        "path_integrals_agree": sp.simplify(straight_integral - piecewise_integral) == 0,
    },
    "proof_levels": {
        "body_quotient": "derived from the existing CHDF minimum-action theorem",
        "post_body_availability": "conditional on the adopted PRRC-P1/PJR-P1 constitutive continuation",
        "quantum_connector_and_xA_equals_xQ": "not derived by this audit",
        "parent_law_realization_occupation_and_empirical_measurement": "open",
    },
    "verdict": "CHDF_BODY_WORK_FORM_IS_EXACT_AND_SOURCE_OWNED_ON_THE_BODY_QUOTIENT_BUT_A8B_REMAINS_OPEN",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
