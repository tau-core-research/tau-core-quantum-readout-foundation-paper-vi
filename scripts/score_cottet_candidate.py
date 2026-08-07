#!/usr/bin/env python3
"""Score the Cottet direct-power/tomography packet without promoting work to x_A."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "cottet2017_reported_controls.json"
OUT = ROOT / "data" / "derived" / "cottet2017_candidate_scoring.json"


def main() -> None:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    capability = {
        "same_carrier": 2,
        "direct_output_work": 2 if d["same_carrier_direct_output_power"] else 0,
        "endpoint_state_geometry": 2 if d["independent_qubit_energy_check"] else 0,
        "closed_holonomy": 2 if d["closed_bargmann_or_uhlmann_loop"] else 0,
        "independent_body_action": 3 if d["body_action_map_frozen"] else 0,
        "reusable_raw_data": 1 if d["raw_numerical_archive_located"] else 0,
        "errors_and_tomographic_control": 1 if d["full_memory_tomography"] else 0,
    }
    entropy_separation = d["mixed_memory_entropy"] - d["superposition_memory_entropy"]
    entropy_sigma = (
        d["mixed_memory_entropy_error"] ** 2
        + d["superposition_memory_entropy_error"] ** 2
    ) ** 0.5
    result = {
        "schema_version": "1.0",
        "capability_score": sum(capability.values()),
        "capability_maximum": 13,
        "components": capability,
        "reported_control_metrics": {
            "informed_vs_ignorant_memory_photons": [
                d["informed_memory_photon_number"],
                d["ignorant_memory_photon_number"],
            ],
            "residual_qubit_excitation": d["residual_qubit_excitation"],
            "memory_entropy_difference": entropy_separation,
            "memory_entropy_difference_sigma": entropy_separation / entropy_sigma,
        },
        "independent_measurement_instrument": True,
        "conditional_descriptor_novelty_at_mean_level": False,
        "independent_terminal_energy_axis": False,
        "independent_tau_body_action_axis": False,
        "eligible_scores": [
            "direct output work versus independent qubit-energy change",
            "informed versus ignorant demon control",
            "coherent-superposition versus mixed-state memory control",
        ],
        "forbidden_scores": [
            "x_A equals x_Q",
            "finite A8b Tau residual",
            "closed-holonomy consistency",
            "QOR timing discriminator",
        ],
        "tau_primary_score_eligible": False,
        "reason": (
            "Direct power is measured by an instrument independent of qubit tomography. "
            "However, the input-output law makes its conditional mean a function of the "
            "qubit state and frozen drive/coupling controls, so it adds no descriptor rank at "
            "mean level. No source-frozen map identifies it with the once-counted Tau body "
            "action; no closed holonomy or reusable raw archive is present."
        ),
        "decision": "Primary independently instrumented energy-control candidate, not an information-novel Tau action axis; retain Naghiloo as trajectory control and do not combine carriers into a Tau certificate."
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["capability_score"] == 7
    assert result["independent_measurement_instrument"] is True
    assert result["conditional_descriptor_novelty_at_mean_level"] is False
    assert result["independent_terminal_energy_axis"] is False
    assert result["independent_tau_body_action_axis"] is False
    print("COTTET_CANDIDATE_SCORE_PASS score=7/13 independent_instrument=yes descriptor_novelty=no tau_body_action=no")


if __name__ == "__main__":
    main()
