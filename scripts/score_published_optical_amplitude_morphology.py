#!/usr/bin/env python3
"""Score Wen's published radial amplitudes against frozen path morphology."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public_optical_path_integral"
OUT = ROOT / "data" / "derived" / "published_optical_amplitude_morphology_score.json"
RNG_SEED = 20260806
UNCERTAINTY_DRAWS = 9999


def load_path_module():
    path = ROOT / "scripts" / "score_reconstructed_optical_path_morphology.py"
    spec = importlib.util.spec_from_file_location("path_score", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def amplitude_packet() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hist = pd.read_excel(DATA / "FigS2C.xlsx")
    summary = pd.read_excel(DATA / "FigS2D.xlsx")
    bins = hist.iloc[:, 0].to_numpy(dtype=float)
    amplitude = summary.iloc[:17, 1].to_numpy(dtype=float)
    counts = np.empty(17, dtype=int)
    standard_error = np.empty(17)
    for radial_class in range(17):
        frequency = hist.iloc[:, radial_class + 1].fillna(0).to_numpy(dtype=float)
        count = int(np.sum(frequency))
        mean = float(np.sum(bins * frequency) / count)
        variance = float(np.sum((bins - mean) ** 2 * frequency) / (count - 1))
        counts[radial_class] = count
        standard_error[radial_class] = np.sqrt(variance / count)
    return amplitude, standard_error, counts


def main() -> None:
    path_score = load_path_module()
    amplitude, standard_error, counts = amplitude_packet()
    positions, increments = path_score.enumerate_paths()
    descriptor_matrix, descriptor_names = path_score.descriptors(positions, increments)
    step_class = np.abs(increments)
    action_design = np.column_stack((np.ones(17), np.arange(17, dtype=float) ** 2))

    log_amplitude = np.log(amplitude)
    action_beta = np.linalg.lstsq(action_design, log_amplitude, rcond=None)[0]
    kernel_residual = log_amplitude - action_design @ action_beta
    target = np.sum(kernel_residual[step_class], axis=1)
    full_score = path_score.score_target(target, descriptor_matrix)
    permutation = path_score.kernel_permutation_null(
        increments, descriptor_matrix, kernel_residual, full_score["delta_r2"]
    )

    # Propagate the published histogram uncertainty under a constant-amplitude
    # null. Sufficient-statistic matrices avoid materializing every path target
    # for each Monte Carlo draw.
    rng = np.random.default_rng(RNG_SEED)
    sample_index = rng.choice(increments.shape[0], size=100_000, replace=False)
    sampled_steps = step_class[sample_index]
    sampled_descriptors = descriptor_matrix[sample_index]
    class_counts = np.stack(
        [np.sum(sampled_steps == radial_class, axis=1) for radial_class in range(17)], axis=1
    ).astype(float)
    baseline = np.column_stack((np.ones(sample_index.size), sampled_descriptors[:, 0]))
    enriched = np.column_stack((baseline, sampled_descriptors[:, 1:]))
    cc = class_counts.T @ class_counts
    baseline_c = baseline.T @ class_counts
    enriched_c = enriched.T @ class_counts
    inv_baseline = np.linalg.inv(baseline.T @ baseline)
    inv_enriched = np.linalg.inv(enriched.T @ enriched)
    centered_c = class_counts - np.mean(class_counts, axis=0)
    centered_cc = centered_c.T @ centered_c
    action_projector = np.eye(17) - action_design @ np.linalg.inv(
        action_design.T @ action_design
    ) @ action_design.T

    def sufficient_delta_r2(candidate: np.ndarray) -> float:
        residual = action_projector @ np.log(candidate)
        total = float(residual @ centered_cc @ residual)
        if total <= 1e-30:
            return 0.0
        sse_baseline = float(
            residual @ cc @ residual
            - residual @ baseline_c.T @ inv_baseline @ baseline_c @ residual
        )
        sse_enriched = float(
            residual @ cc @ residual
            - residual @ enriched_c.T @ inv_enriched @ enriched_c @ residual
        )
        return (sse_baseline - sse_enriched) / total

    weights = standard_error**-2
    constant_amplitude = float(np.sum(weights * amplitude) / np.sum(weights))
    observed_sample_delta_r2 = sufficient_delta_r2(amplitude)
    uncertainty_null = np.empty(UNCERTAINTY_DRAWS)
    for index in range(UNCERTAINTY_DRAWS):
        draw = np.maximum(rng.normal(constant_amplitude, standard_error), 1e-9)
        uncertainty_null[index] = sufficient_delta_r2(draw)
    uncertainty_p = float(
        (1 + np.sum(uncertainty_null >= observed_sample_delta_r2))
        / (UNCERTAINTY_DRAWS + 1)
    )

    jackknife = []
    for radial_class in range(17):
        mask = np.arange(17) != radial_class
        beta = np.linalg.lstsq(action_design[mask], log_amplitude[mask], rcond=None)[0]
        replacement = amplitude.copy()
        replacement[radial_class] = np.exp(action_design[radial_class] @ beta)
        jackknife.append(
            {
                "replaced_radial_class": radial_class,
                "sample_delta_r2": sufficient_delta_r2(replacement),
            }
        )

    result = {
        "schema_version": "1.0",
        "source_doi": "10.5061/dryad.x0k6djj14",
        "status": "STANDARD_OPTICAL_KERNEL_SIGNAL_NOT_TAU_ENDPOINT",
        "published_packet": {
            "radial_classes": 17,
            "histogram_counts": counts.tolist(),
            "normalized_amplitude_means": amplitude.tolist(),
            "standard_errors_of_means": standard_error.tolist(),
            "mean_amplitude": float(np.mean(amplitude)),
            "coefficient_of_variation_across_class_means": float(
                np.std(amplitude) / np.mean(amplitude)
            ),
        },
        "score": {**full_score, "shared_kernel_permutation": permutation},
        "constant_amplitude_uncertainty_null": {
            "weighted_constant": constant_amplitude,
            "draws": UNCERTAINTY_DRAWS,
            "sample_observed_delta_r2": observed_sample_delta_r2,
            "null_mean_delta_r2": float(np.mean(uncertainty_null)),
            "null_95_percentile_delta_r2": float(np.quantile(uncertainty_null, 0.95)),
            "uncertainty_null_p": uncertainty_p,
        },
        "single_class_replacement": {
            "minimum_delta_r2": float(min(row["sample_delta_r2"] for row in jackknife)),
            "rows": jackknife,
        },
        "descriptors": descriptor_names,
        "interpretation": {
            "detected": "published radial-amplitude kernel structure beyond scalar total standard action",
            "not_detected": "independent Tau morphological-body action or Tau-specific quantum deviation",
            "claim_boundary": (
                "The same 17 published kernel classes generate all paths. The result is a "
                "standard optical-kernel diagnostic and may contain ordinary calibration, "
                "finite-sample or propagator structure. It is not an unrestricted physical Tau endpoint."
            ),
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["published_packet"]["radial_classes"] == 17
    assert result["score"]["delta_r2"] > 0.4
    assert result["score"]["shared_kernel_permutation"]["kernel_permutation_p"] < 0.01
    assert result["constant_amplitude_uncertainty_null"]["uncertainty_null_p"] < 0.01
    assert result["single_class_replacement"]["minimum_delta_r2"] > 0.25
    assert result["status"] == "STANDARD_OPTICAL_KERNEL_SIGNAL_NOT_TAU_ENDPOINT"
    print(
        "PUBLISHED_OPTICAL_AMPLITUDE_SCORE_PASS "
        f"delta_r2={full_score['delta_r2']:.6f} "
        f"permutation_p={permutation['kernel_permutation_p']:.4f} "
        f"uncertainty_p={uncertainty_p:.4f}"
    )


if __name__ == "__main__":
    main()
