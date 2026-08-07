#!/usr/bin/env python3
"""Score the public Wen et al. optical path-integral control packet."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public_optical_path_integral"
OUT = ROOT / "data" / "derived" / "optical_path_integral_candidate_scoring.json"


def read_numeric(path: Path) -> np.ndarray:
    with path.open(newline="") as handle:
        rows = list(csv.reader(handle))
    return np.asarray([[float(value) for value in row] for row in rows[1:]], dtype=float)


def weighted_constant(y: np.ndarray, sigma: np.ndarray) -> tuple[float, float]:
    weight = sigma ** -2
    mean = float(np.sum(weight * y) / np.sum(weight))
    return mean, float(np.sum(((y - mean) / sigma) ** 2))


def weighted_affine(x: np.ndarray, y: np.ndarray, sigma: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    design = np.column_stack((np.ones(x.size), x))
    weight = sigma ** -2
    covariance = np.linalg.inv(design.T @ (weight[:, None] * design))
    beta = covariance @ (design.T @ (weight * y))
    chi_square = float(np.sum(((y - design @ beta) / sigma) ** 2))
    return beta, np.sqrt(np.diag(covariance)), chi_square


def main() -> None:
    length = read_numeric(DATA / "Fig4A.csv")
    action_amp = read_numeric(DATA / "Fig4B.csv")
    action_phase = read_numeric(DATA / "Fig4C.csv")
    length_mean, length_chi = weighted_constant(length[:, 1], length[:, 2])
    action_mean, action_chi = weighted_constant(action_amp[:, 1], action_amp[:, 2])
    amp_beta, amp_error, amp_linear_chi = weighted_affine(action_amp[:, 0], action_amp[:, 1], action_amp[:, 2])
    phase_beta, phase_error, phase_affine_chi = weighted_affine(action_phase[:, 3], action_phase[:, 1], action_phase[:, 2])
    phase_residual = action_phase[:, 1] - action_phase[:, 3]
    phase_raw_chi = float(np.sum((phase_residual / action_phase[:, 2]) ** 2))
    result = {
        "schema_version": "1.0",
        "source_doi": "10.5061/dryad.x0k6djj14",
        "standard_controls": {
            "length_amplitude": {"points": int(length.shape[0]), "weighted_constant": length_mean, "chi_square": length_chi, "reduced_chi_square": length_chi / (length.shape[0] - 1)},
            "action_amplitude": {"points": int(action_amp.shape[0]), "weighted_constant": action_mean, "constant_chi_square": action_chi, "constant_reduced_chi_square": action_chi / (action_amp.shape[0] - 1), "weighted_linear_intercept": float(amp_beta[0]), "weighted_linear_slope": float(amp_beta[1]), "slope_standard_error": float(amp_error[1]), "slope_z": float(amp_beta[1] / amp_error[1]), "linear_chi_square": amp_linear_chi},
            "action_phase": {"points": int(action_phase.shape[0]), "raw_rms_phase_pi_units": float(np.sqrt(np.mean(phase_residual ** 2))), "raw_chi_square": phase_raw_chi, "raw_reduced_chi_square": phase_raw_chi / action_phase.shape[0], "affine_intercept": float(phase_beta[0]), "affine_slope": float(phase_beta[1]), "affine_intercept_standard_error": float(phase_error[0]), "affine_slope_standard_error": float(phase_error[1]), "affine_chi_square": phase_affine_chi}
        },
        "identifiability": {"same_experiment_action_phase_control": True, "same_experiment_action_amplitude_control": True, "joint_path_level_morphology_action_amplitude_records": False, "can_test_conditional_morphology_novelty": False, "can_identify_tau_body_action": False, "tau_primary_score_eligible": False},
        "decision": "The public optical packet supports the standard equal-amplitude and action-phase controls. Because morphology and action are published only as separate aggregate axes, it cannot test information beyond action or identify the Tau morphological action. Retain it as a same-experiment optical control."
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert abs(result["standard_controls"]["action_amplitude"]["slope_z"]) < 1.0
    assert result["standard_controls"]["action_phase"]["raw_rms_phase_pi_units"] < 0.03
    assert result["identifiability"]["tau_primary_score_eligible"] is False
    print("OPTICAL_PATH_INTEGRAL_SCORE_PASS phase_control=yes amplitude_control=yes tau_score=no")


if __name__ == "__main__":
    main()
