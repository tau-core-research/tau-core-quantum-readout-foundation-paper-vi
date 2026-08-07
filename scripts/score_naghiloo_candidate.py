#!/usr/bin/env python3
"""Score the Naghiloo trajectory packet without converting controls into a Tau signal."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "naghiloo2020_reported_controls.json"
OUT = ROOT / "data" / "derived" / "naghiloo2020_candidate_scoring.json"


def main() -> None:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    feedback_contrast = d["feedback_vs_unitary_work_slope"] / d["open_vs_unitary_work_slope"]
    capability = {
        "same_carrier_state_path": 2 if d["same_carrier_state_path"] else 0,
        "trajectory_energy_leg": 1 if d["trajectory_heat_work"] else 0,
        "independent_endpoint_check": 2 if d["terminal_projective_check"] else 0,
        "closed_holonomy": 2 if d["closed_bargmann_or_uhlmann_loop"] else 0,
        "independent_body_action": 3 if d["body_action_map_frozen"] else 0,
        "reusable_raw_data": 1 if d["raw_trajectory_archive_located"] else 0,
        "errors_and_feedback_control": 1 if d["measurement_efficiency"] > 0 else 0,
    }
    result = {
        "schema_version": "1.0",
        "capability_score": sum(capability.values()),
        "capability_maximum": 13,
        "components": capability,
        "reported_control_metrics": {
            "time_resolution_ns": d["time_resolution_ns"],
            "trajectory_count": d["trajectory_count_per_reported_ensemble"],
            "measurement_efficiency": d["measurement_efficiency"],
            "heat_feedback_correlation": d["heat_feedback_correlation"],
            "feedback_to_open_slope_ratio": feedback_contrast,
        },
        "eligible_scores": [
            "first-law closure control",
            "feedback-versus-open-loop control",
            "trajectory-versus-projective endpoint consistency",
        ],
        "forbidden_scores": [
            "x_A equals x_Q",
            "finite A8b Tau residual",
            "closed-holonomy consistency",
            "QOR timing discriminator",
        ],
        "tau_primary_score_eligible": False,
        "reason": (
            "The energetic quantities are reconstructed from rho(t) and H(t), and the packet "
            "contains neither an independent body-action calibration nor a closed holonomy or "
            "reusable raw trajectories."
        ),
        "decision": "Promote as a standard-physics control candidate, not as a Tau-signal endpoint."
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["capability_score"] == 6
    assert abs(feedback_contrast - 72.83333333333333) < 1e-10
    assert result["tau_primary_score_eligible"] is False
    print("NAGHILOO_CANDIDATE_SCORE_PASS score=6/13 feedback_contrast=72.833 tau_primary=no")


if __name__ == "__main__":
    main()
