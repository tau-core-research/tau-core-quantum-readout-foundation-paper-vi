#!/usr/bin/env python3
"""Show that pairwise fidelities do not fix loop/Bargmann holonomy."""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/endpoint_holonomy_no_go.json"


def inner(left: tuple[complex, complex], right: tuple[complex, complex]) -> complex:
    return left[0].conjugate() * right[0] + left[1].conjugate() * right[1]


def packet(theta: float, phi: float) -> dict:
    states = (
        (1.0 + 0j, 0j),
        (math.cos(theta) + 0j, math.sin(theta) + 0j),
        (math.cos(theta) + 0j, cmath.exp(1j * phi) * math.sin(theta)),
    )
    overlaps = (
        inner(states[0], states[1]),
        inner(states[1], states[2]),
        inner(states[2], states[0]),
    )
    fidelities = [abs(value) ** 2 for value in overlaps]
    bargmann = overlaps[0] * overlaps[1] * overlaps[2]
    return {
        "phi": phi,
        "pairwise_fidelities": fidelities,
        "bargmann_phase": cmath.phase(bargmann),
        "bargmann_magnitude": abs(bargmann),
    }


def main() -> None:
    positive = packet(0.8, 0.9)
    negative = packet(0.8, -0.9)
    max_fidelity_difference = max(
        abs(a - b)
        for a, b in zip(positive["pairwise_fidelities"], negative["pairwise_fidelities"])
    )
    result = {
        "family": "psi0=(1,0), psi1=(cos theta,sin theta), psi2=(cos theta,e^{i phi}sin theta)",
        "positive_phase_packet": positive,
        "negative_phase_packet": negative,
        "max_pairwise_fidelity_difference": max_fidelity_difference,
        "conclusions": {
            "pairwise_endpoint_distances_fix_loop_holonomy": False,
            "closed_loop_phase_witness_required": True,
            "complex_conjugate_packets_are_distance_indistinguishable": True,
        },
        "claim_boundary": (
            "The example proves endpoint-distance incompleteness; it does not identify "
            "which holonomy Nature selects."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert max_fidelity_difference < 1e-12
    assert abs(positive["bargmann_phase"] + negative["bargmann_phase"]) < 1e-12
    assert abs(positive["bargmann_phase"]) > 1e-6
    print(
        "ENDPOINT_HOLONOMY_NO_GO_PASS",
        f"phase_plus={positive['bargmann_phase']:.6f}",
        f"phase_minus={negative['bargmann_phase']:.6f}",
    )


if __name__ == "__main__":
    main()
