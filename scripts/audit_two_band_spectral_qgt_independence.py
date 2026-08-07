#!/usr/bin/env python3
"""Construct two-band countermodels separating spectrum and state geometry."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/two_band_spectral_qgt_independence_audit.json"


def model(angular_rate: float, radial_quadratic: float) -> dict:
    # H(q)=r(q)n(q).sigma, r(q)=1+b q^2 and
    # n(q)=(sin(aq),0,cos(aq)), evaluated at q=0.
    return {
        "angular_rate_a": angular_rate,
        "radial_quadratic_b": radial_quadratic,
        "ground_state_quantum_metric_g_qq": angular_rate**2 / 4.0,
        "positive_energy_second_derivative": 2.0 * radial_quadratic,
        "gap_at_q0": 2.0,
    }


def main() -> None:
    same_geometry_1 = model(1.0, 1.0)
    same_geometry_2 = model(1.0, 3.0)
    same_spectrum_1 = model(1.0, 1.0)
    same_spectrum_2 = model(2.0, 1.0)

    result = {
        "family": "H(q)=r(q)n(q).sigma with r=1+bq^2 and n=(sin(aq),0,cos(aq))",
        "identity": "g_qq(0)=a^2/4 while E_+''(0)=2b",
        "same_QGT_different_spectral_curvature": [same_geometry_1, same_geometry_2],
        "same_spectral_curvature_different_QGT": [same_spectrum_1, same_spectrum_2],
        "conclusions": {
            "spectrum_determines_QGT_in_generic_two_band_family": False,
            "QGT_determines_spectral_curvature_in_generic_two_band_family": False,
            "spectral_curvature_can_be_relabelled_as_independent_x_A_without_extra_source_law": False,
        },
        "claim_boundary": (
            "A source-owned relation tying radial and angular Bloch data could evade this "
            "countermodel, but that relation must be derived independently."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert same_geometry_1["ground_state_quantum_metric_g_qq"] == same_geometry_2[
        "ground_state_quantum_metric_g_qq"
    ]
    assert same_geometry_1["positive_energy_second_derivative"] != same_geometry_2[
        "positive_energy_second_derivative"
    ]
    assert same_spectrum_1["positive_energy_second_derivative"] == same_spectrum_2[
        "positive_energy_second_derivative"
    ]
    assert same_spectrum_1["ground_state_quantum_metric_g_qq"] != same_spectrum_2[
        "ground_state_quantum_metric_g_qq"
    ]
    print("TWO_BAND_SPECTRAL_QGT_INDEPENDENCE_PASS")


if __name__ == "__main__":
    main()
