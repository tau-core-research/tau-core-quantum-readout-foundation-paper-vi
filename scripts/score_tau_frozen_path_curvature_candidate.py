#!/usr/bin/env python3
"""Score one frozen, conditional Tau path-curvature candidate.

The candidate is the Dirichlet energy of the path-increment field,
sum_k (Delta x_{k+1} - Delta x_k)^2.  Existing Tau body theory selects a
primitive Dirichlet form, but its application to the increment carrier still
requires a typed body-derived edge carrier.  The result is therefore a
conditional descriptor diagnostic, not a Tau endpoint.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "tau_frozen_path_curvature_candidate_score.json"
RNG_SEED = 20260806
PERMUTATIONS = 999
PERMUTATION_SAMPLE = 100_000


def load_module(name: str, filename: str):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fit(target: np.ndarray, action: np.ndarray, candidate: np.ndarray | None = None) -> dict[str, float]:
    columns = [np.ones(target.size), action]
    if candidate is not None:
        columns.append(candidate)
    design = np.column_stack(columns)
    beta = np.linalg.lstsq(design, target, rcond=None)[0]
    residual = target - design @ beta
    centered = target - np.mean(target)
    total = float(centered @ centered)
    r2 = 0.0 if total <= 1e-30 else float(1.0 - (residual @ residual) / total)
    result = {"r2": r2}
    if candidate is not None:
        result["candidate_coefficient"] = float(beta[-1])
        candidate_sd = float(np.std(candidate))
        target_sd = float(np.std(target))
        result["standardized_candidate_coefficient"] = (
            0.0 if target_sd <= 1e-30 else float(beta[-1] * candidate_sd / target_sd)
        )
    return result


def delta_r2(target: np.ndarray, descriptors: np.ndarray, column: int) -> dict[str, float]:
    baseline = fit(target, descriptors[:, 0])
    enriched = fit(target, descriptors[:, 0], descriptors[:, column])
    return {
        "action_only_r2": baseline["r2"],
        "action_plus_candidate_r2": enriched["r2"],
        "delta_r2": enriched["r2"] - baseline["r2"],
        "candidate_coefficient": enriched["candidate_coefficient"],
        "standardized_candidate_coefficient": enriched["standardized_candidate_coefficient"],
    }


def main() -> None:
    path = load_module("path_score", "score_reconstructed_optical_path_morphology.py")
    published = load_module("published_score", "score_published_optical_amplitude_morphology.py")
    amplitude, _, _ = published.amplitude_packet()
    positions, increments = path.enumerate_paths()
    descriptors, names = path.descriptors(positions, increments)
    step_class = np.abs(increments)

    action_design = np.column_stack((np.ones(17), np.arange(17, dtype=float) ** 2))
    log_amplitude = np.log(amplitude)
    action_beta = np.linalg.lstsq(action_design, log_amplitude, rcond=None)[0]
    kernel_residual = log_amplitude - action_design @ action_beta
    target = np.sum(kernel_residual[step_class], axis=1)

    scores = {names[column]: delta_r2(target, descriptors, column) for column in range(1, len(names))}
    ranked = sorted(scores, key=lambda name: scores[name]["delta_r2"], reverse=True)
    observed = scores["increment_roughness"]["delta_r2"]

    rng = np.random.default_rng(RNG_SEED)
    sample_index = rng.choice(increments.shape[0], size=PERMUTATION_SAMPLE, replace=False)
    sampled_steps = step_class[sample_index]
    sampled_descriptors = descriptors[sample_index]
    observed_sample_target = np.sum(kernel_residual[sampled_steps], axis=1)
    observed_sample = delta_r2(observed_sample_target, sampled_descriptors, 2)["delta_r2"]
    null = np.empty(PERMUTATIONS)
    for index in range(PERMUTATIONS):
        permuted = rng.permutation(kernel_residual)
        permuted_target = np.sum(permuted[sampled_steps], axis=1)
        null[index] = delta_r2(permuted_target, sampled_descriptors, 2)["delta_r2"]
    p_value = float((1 + np.sum(null >= observed_sample)) / (PERMUTATIONS + 1))

    result = {
        "schema_version": "1.0",
        "source_doi": "10.5061/dryad.x0k6djj14",
        "status": "TAU_CONDITIONAL_DESCRIPTOR_DIAGNOSTIC_NOT_ENDPOINT",
        "frozen_candidate": {
            "name": "increment_roughness",
            "formula": "sum_k (Delta x[k+1] - Delta x[k])^2",
            "theory_status": (
                "Dirichlet energy of the increment field; Tau body theory selects a primitive "
                "Dirichlet form, but a body-derived typed increment carrier is not yet proved."
            ),
            "sign_prediction": "not fixed without a proved body-to-amplitude connector",
        },
        "paths": int(positions.shape[0]),
        "shared_kernel_classes": 17,
        "single_descriptor_scores": scores,
        "wrong_family_ranking": ranked,
        "candidate_rank_of_five": ranked.index("increment_roughness") + 1,
        "shared_kernel_permutation": {
            "permutation_unit": "17 shared radial kernel classes",
            "sampled_paths": PERMUTATION_SAMPLE,
            "permutations": PERMUTATIONS,
            "full_path_observed_delta_r2": observed,
            "sample_observed_delta_r2": observed_sample,
            "null_mean_delta_r2": float(np.mean(null)),
            "null_95_percentile_delta_r2": float(np.quantile(null, 0.95)),
            "p_value": p_value,
        },
        "verdict": (
            "A significant partial score would establish only that the conditional curvature "
            "descriptor tracks published optical-kernel structure beyond total action. Tau-specific "
            "interpretation additionally requires a sourced edge carrier and connector."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["paths"] == 17**5
    assert result["status"] == "TAU_CONDITIONAL_DESCRIPTOR_DIAGNOSTIC_NOT_ENDPOINT"
    print(
        "TAU_FROZEN_PATH_CURVATURE_SCORE_PASS "
        f"delta_r2={observed:.6f} p={p_value:.4f} rank={result['candidate_rank_of_five']}/5"
    )


if __name__ == "__main__":
    main()
