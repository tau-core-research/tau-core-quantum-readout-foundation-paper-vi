#!/usr/bin/env python3
"""Show that equal local stiffness does not fix finite endpoint chords."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/local_stiffness_finite_distance_no_go.json"


def straight_chord(delta_q: float) -> float:
    return abs(delta_q)


def circular_chord(delta_q: float, curvature: float) -> float:
    return 2.0 * abs(math.sin(curvature * delta_q / 2.0)) / abs(curvature)


def main() -> None:
    delta_q = 1.0
    curvatures = (0.5, 1.0, 1.5)
    straight = straight_chord(delta_q)
    curved = [circular_chord(delta_q, value) for value in curvatures]
    result = {
        "embeddings": {
            "straight": "W_0(q)=(q,0)",
            "curved": "W_k(q)=(sin(kq)/k,(1-cos(kq))/k)",
        },
        "shared_local_metric": "|dW/dq|^2=1 for every k",
        "delta_q": delta_q,
        "straight_chord": straight,
        "curved_chords": [
            {"curvature": kappa, "chord": chord}
            for kappa, chord in zip(curvatures, curved)
        ],
        "conclusions": {
            "local_stiffness_alone_fixes_finite_chord": False,
            "connector_or_extrinsic_transport_required": True,
            "blind_endpoint_prediction_requires_global_rigidity_audit": True,
        },
        "claim_boundary": (
            "The countermodel does not reject a connector-based certificate; it proves "
            "that intrinsic local stiffness alone is insufficient."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert all(abs(chord - straight) > 1e-6 for chord in curved)
    assert not result["conclusions"]["local_stiffness_alone_fixes_finite_chord"]
    print("LOCAL_STIFFNESS_FINITE_DISTANCE_NO_GO_PASS")


if __name__ == "__main__":
    main()
