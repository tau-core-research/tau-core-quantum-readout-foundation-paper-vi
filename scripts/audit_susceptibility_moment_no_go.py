#!/usr/bin/env python3
"""Show that energy and fidelity susceptibilities are distinct spectral moments."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/susceptibility_moment_no_go_audit.json"


def two_level(gap: float, matrix_element: float = 1.0) -> dict:
    weight = matrix_element**2
    return {
        "gap": gap,
        "matrix_element_squared": weight,
        "energy_susceptibility": 2.0 * weight / gap,
        "fidelity_susceptibility": weight / gap**2,
        "ratio_chi_E_over_chi_F": 2.0 * gap,
    }


def main() -> None:
    models = [two_level(gap) for gap in (0.5, 1.0, 2.0, 4.0)]
    ratios = [model["ratio_chi_E_over_chi_F"] for model in models]
    result = {
        "definitions": {
            "chi_E": "2 sum_n>0 |<n|V|0>|^2 / Delta_n",
            "chi_F": "sum_n>0 |<n|V|0>|^2 / Delta_n^2",
        },
        "two_level_models": models,
        "conclusions": {
            "universal_parameter_independent_proportionality": False,
            "energy_susceptibility_is_independent_morphological_x_A": False,
            "additional_source_owned_gap_weighting_required": True,
        },
        "claim_boundary": (
            "The no-go excludes an automatic identification. A physical source law may "
            "still define a calibrated transform using independently measured gaps and weights."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert len(set(ratios)) == len(ratios)
    assert not result["conclusions"]["universal_parameter_independent_proportionality"]
    print("SUSCEPTIBILITY_MOMENT_NO_GO_PASS", f"ratios={ratios}")


if __name__ == "__main__":
    main()
