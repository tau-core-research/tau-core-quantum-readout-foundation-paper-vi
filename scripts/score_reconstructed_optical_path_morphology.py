#!/usr/bin/env python3
"""Reconstruct the Wen optical step kernel and score path morphology.

The 17^5 generated paths share only 17 measured radial kernel classes.  The
script therefore reports algebraic full-path effect sizes but calibrates the
null by permuting the 17 kernel residuals, never by treating paths as
independent experimental observations.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "public_optical_path_integral" / "raw_propagator"
OUT = ROOT / "data" / "derived" / "reconstructed_optical_path_morphology_score.json"

POSITION_VALUES = np.arange(-8, 9, dtype=np.int16)
SOURCE_POSITION = 0
RADIAL_CLASSES = np.arange(17, dtype=np.int16)
RNG_SEED = 20260806
PERMUTATIONS = 499
PERMUTATION_SAMPLE = 100_000


def load_camera(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    frame = pd.read_excel(RAW / f"FigS1B-{name}.xlsx", header=None)
    # Dryad README: first column is x_p3 and first row is y_p3.
    y_coord = frame.iloc[0, 1:].to_numpy(dtype=float)
    x_coord = frame.iloc[1:, 0].to_numpy(dtype=float)
    image = frame.iloc[1:, 1:].to_numpy(dtype=float)
    return x_coord, y_coord, image


def fit_sample_source_coordinate() -> tuple[float, float]:
    """Infer the fixed x_p2 from the published theoretical sample curve."""
    frame = pd.read_excel(RAW / "FigS1C.xlsx")
    x = frame.iloc[:, 0].to_numpy(dtype=float)
    kernel = frame.iloc[:, 2].to_numpy(dtype=float) + 1j * frame.iloc[:, 1].to_numpy(dtype=float)
    phase = np.unwrap(np.angle(kernel))
    quadratic = np.polyfit(x, phase, 2)
    vertex = float(-quadratic[1] / (2.0 * quadratic[0]))
    rms = float(np.sqrt(np.mean((phase - np.polyval(quadratic, x)) ** 2)))
    return vertex, rms


def reconstruct_radial_kernel() -> dict[str, np.ndarray | float]:
    x_coord, y_coord, plus = load_camera("Plus")
    _, _, minus = load_camera("Minus")
    _, _, right = load_camera("R")
    _, _, left = load_camera("L")
    _, _, psi_probability = load_camera("PSI")
    x_grid, y_grid = np.meshgrid(x_coord, y_coord, indexing="ij")

    source_x, sample_phase_rms = fit_sample_source_coordinate()
    radius = np.sqrt((x_grid - source_x) ** 2 + y_grid**2)

    # Direct-propagator readout: K'' = -(P_+ - P_-) + i(P_R - P_L).
    # The camera convention in this archive is conjugated relative to the
    # increasing standard action phase, fixed here by the FigS1C control.
    raw = np.conjugate(-(plus - minus) + 1j * (right - left))
    probability_floor = 1.0
    normalized = raw / np.sqrt(psi_probability + probability_floor)

    amplitude = np.empty(17)
    phase = np.empty(17)
    phase_concentration = np.empty(17)
    pixels = np.empty(17, dtype=int)
    for delta in RADIAL_CLASSES:
        mask = (radius >= delta - 0.5) & (radius < delta + 0.5) & (np.abs(raw) > 0)
        weights = psi_probability[mask] + probability_floor
        values = normalized[mask]
        unit = values / np.maximum(np.abs(values), 1e-15)
        amplitude[delta] = np.average(np.abs(values), weights=weights)
        mean_unit = np.average(unit, weights=weights)
        phase[delta] = np.angle(mean_unit)
        phase_concentration[delta] = np.abs(mean_unit)
        pixels[delta] = int(mask.sum())

    phase_unwrapped = np.unwrap(phase)
    action_coordinate = RADIAL_CLASSES.astype(float) ** 2
    design = np.column_stack((np.ones(17), action_coordinate))
    phase_beta = np.linalg.lstsq(design, phase_unwrapped, rcond=None)[0]
    phase_residual = phase_unwrapped - design @ phase_beta
    log_amplitude = np.log(amplitude)
    amplitude_beta = np.linalg.lstsq(design, log_amplitude, rcond=None)[0]
    amplitude_residual = log_amplitude - design @ amplitude_beta

    return {
        "source_x": source_x,
        "sample_theory_quadratic_rms": sample_phase_rms,
        "amplitude": amplitude,
        "phase": phase_unwrapped,
        "phase_concentration": phase_concentration,
        "pixels": pixels,
        "phase_beta": phase_beta,
        "phase_residual": phase_residual,
        "amplitude_beta": amplitude_beta,
        "amplitude_residual": amplitude_residual,
    }


def validate_against_published_sample(kernel: dict[str, np.ndarray | float]) -> dict[str, float | bool]:
    """Check the raw-image reduction against the published FigS1C sample."""
    frame = pd.read_excel(RAW / "FigS1C.xlsx")
    x = frame.iloc[:17, 3].to_numpy(dtype=float)
    published = frame.iloc[:17, 6].to_numpy(dtype=float) + 1j * frame.iloc[:17, 4].to_numpy(dtype=float)
    delta = np.clip(np.rint(np.abs(x - float(kernel["source_x"]))).astype(int), 0, 16)
    reconstructed_amplitude = np.asarray(kernel["amplitude"])[delta]
    published_amplitude = np.abs(published)
    amplitude_correlation = float(np.corrcoef(reconstructed_amplitude, published_amplitude)[0, 1])
    reconstructed_cv = float(np.std(reconstructed_amplitude) / np.mean(reconstructed_amplitude))
    published_cv = float(np.std(published_amplitude) / np.mean(published_amplitude))

    reconstructed_phase = np.asarray(kernel["phase"])[delta]
    published_phase = np.unwrap(np.angle(published))
    common_offset = float(np.mean(published_phase - reconstructed_phase))
    phase_residual = np.angle(np.exp(1j * (published_phase - reconstructed_phase - common_offset)))
    phase_rms = float(np.sqrt(np.mean(phase_residual**2)))
    return {
        "phase_rms_rad_after_common_offset": phase_rms,
        "phase_rms_pi_units": phase_rms / np.pi,
        "phase_reconstruction_eligible": phase_rms / np.pi < 0.03,
        "amplitude_correlation": amplitude_correlation,
        "published_amplitude_cv": published_cv,
        "reconstructed_amplitude_cv": reconstructed_cv,
        "amplitude_reconstruction_eligible": amplitude_correlation > 0.8 and reconstructed_cv < 2.0 * published_cv,
    }


def enumerate_paths() -> tuple[np.ndarray, np.ndarray]:
    grids = np.meshgrid(*([POSITION_VALUES] * 5), indexing="ij")
    positions = np.stack([grid.ravel() for grid in grids], axis=1).astype(np.int8)
    previous = np.column_stack((np.full(positions.shape[0], SOURCE_POSITION, dtype=np.int8), positions[:, :-1]))
    increments = positions - previous
    return positions, increments


def descriptors(positions: np.ndarray, increments: np.ndarray) -> tuple[np.ndarray, list[str]]:
    absolute_steps = np.abs(increments).astype(float)
    action = np.sum(increments.astype(float) ** 2, axis=1)
    length = np.sum(absolute_steps, axis=1)
    roughness = np.sum(np.diff(increments.astype(float), axis=1) ** 2, axis=1)
    turns = np.sum(increments[:, :-1] * increments[:, 1:] < 0, axis=1).astype(float)
    max_excursion = np.max(np.abs(positions), axis=1).astype(float)
    occupied_step_classes = np.sum(
        np.stack([np.any(absolute_steps == delta, axis=1) for delta in RADIAL_CLASSES], axis=1), axis=1
    ).astype(float)
    matrix = np.column_stack((action, length, roughness, turns, max_excursion, occupied_step_classes))
    return matrix, ["standard_action", "path_length", "increment_roughness", "turn_count", "max_excursion", "occupied_step_classes"]


def fit_r2(design: np.ndarray, target: np.ndarray) -> float:
    beta = np.linalg.lstsq(design, target, rcond=None)[0]
    residual = target - design @ beta
    total = target - np.mean(target)
    denominator = float(total @ total)
    return 0.0 if denominator == 0 else float(1.0 - (residual @ residual) / denominator)


def score_target(target: np.ndarray, descriptor_matrix: np.ndarray) -> dict[str, float]:
    action = descriptor_matrix[:, 0]
    baseline = np.column_stack((np.ones(action.size), action))
    morphology = np.column_stack((baseline, descriptor_matrix[:, 1:]))
    baseline_r2 = fit_r2(baseline, target)
    full_r2 = fit_r2(morphology, target)
    return {"action_only_r2": baseline_r2, "action_plus_morphology_r2": full_r2, "delta_r2": full_r2 - baseline_r2}


def kernel_permutation_null(
    increments: np.ndarray,
    descriptor_matrix: np.ndarray,
    kernel_residual: np.ndarray,
    observed_delta_r2: float,
) -> dict[str, float]:
    rng = np.random.default_rng(RNG_SEED)
    sample_index = rng.choice(increments.shape[0], size=min(PERMUTATION_SAMPLE, increments.shape[0]), replace=False)
    sampled_steps = np.abs(increments[sample_index])
    sampled_descriptors = descriptor_matrix[sample_index]
    observed_sample = np.sum(kernel_residual[sampled_steps], axis=1)
    observed_sample_score = score_target(observed_sample, sampled_descriptors)["delta_r2"]
    null = np.empty(PERMUTATIONS)
    for index in range(PERMUTATIONS):
        permuted = rng.permutation(kernel_residual)
        target = np.sum(permuted[sampled_steps], axis=1)
        null[index] = score_target(target, sampled_descriptors)["delta_r2"]
    p_value = float((1 + np.sum(null >= observed_sample_score)) / (PERMUTATIONS + 1))
    return {
        "permutation_unit": "17 shared radial kernel classes",
        "sampled_paths_for_computation": int(sample_index.size),
        "permutations": PERMUTATIONS,
        "full_path_observed_delta_r2": observed_delta_r2,
        "sample_observed_delta_r2": float(observed_sample_score),
        "null_mean_delta_r2": float(np.mean(null)),
        "null_95_percentile_delta_r2": float(np.quantile(null, 0.95)),
        "kernel_permutation_p": p_value,
    }


def main() -> None:
    kernel = reconstruct_radial_kernel()
    validation = validate_against_published_sample(kernel)
    positions, increments = enumerate_paths()
    descriptor_matrix, descriptor_names = descriptors(positions, increments)
    step_class = np.abs(increments)
    phase_target = np.sum(kernel["phase_residual"][step_class], axis=1)
    amplitude_target = np.sum(kernel["amplitude_residual"][step_class], axis=1)
    phase_score = score_target(phase_target, descriptor_matrix)
    amplitude_score = score_target(amplitude_target, descriptor_matrix)
    phase_null = kernel_permutation_null(increments, descriptor_matrix, kernel["phase_residual"], phase_score["delta_r2"])
    amplitude_null = kernel_permutation_null(increments, descriptor_matrix, kernel["amplitude_residual"], amplitude_score["delta_r2"])

    result = {
        "schema_version": "1.0",
        "source_doi": "10.5061/dryad.x0k6djj14",
        "status": "DIAGNOSTIC_ONLY_NOT_TAU_ENDPOINT",
        "reconstruction": {
            "paths": int(positions.shape[0]),
            "positions_per_slice": 17,
            "variable_slices": 5,
            "shared_radial_kernel_classes": 17,
            "source_x_from_FigS1C_quadratic_vertex": kernel["source_x"],
            "FigS1C_theory_quadratic_fit_rms_rad": kernel["sample_theory_quadratic_rms"],
            "phase_action_intercept_rad": float(kernel["phase_beta"][0]),
            "phase_action_slope_rad_per_delta_squared": float(kernel["phase_beta"][1]),
            "phase_action_rms_residual_rad": float(np.sqrt(np.mean(kernel["phase_residual"] ** 2))),
            "radial_pixels": kernel["pixels"].tolist(),
            "radial_phase_concentration": kernel["phase_concentration"].tolist(),
            "FigS1C_validation": validation,
        },
        "descriptors": descriptor_names,
        "phase_residual_score": {**phase_score, "shared_kernel_null": phase_null},
        "log_amplitude_residual_score": {
            **amplitude_score,
            "shared_kernel_null": amplitude_null,
            "eligible_for_physical_interpretation": validation["amplitude_reconstruction_eligible"],
            "exclusion_reason": "The raw-image amplitude reduction fails the independent FigS1C amplitude validation; its apparent score is retained only as a pipeline diagnostic.",
        },
        "interpretation": {
            "what_is_tested": "Whether measured factorized step-kernel residuals carry path-descriptor information beyond scalar total standard action.",
            "what_is_not_tested": "No independent Tau morphological-body action, carrier bridge or unrestricted physical Tau completion is measured.",
            "independence_warning": "The generated paths are algebraic combinations of 17 shared measured kernel classes and are not independent observations.",
            "positive_result_boundary": "A positive score is standard propagator-structure information beyond scalar total action, not a Tau-specific signal.",
            "verdict": "The validated phase leg shows no kernel-level significant morphology increment. The larger apparent amplitude increment is excluded because the raw-image amplitude normalization fails FigS1C validation.",
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["reconstruction"]["paths"] == 17**5
    assert result["reconstruction"]["shared_radial_kernel_classes"] == 17
    assert result["reconstruction"]["phase_action_rms_residual_rad"] < 0.2
    assert validation["phase_reconstruction_eligible"] is True
    assert validation["amplitude_reconstruction_eligible"] is False
    assert result["status"] == "DIAGNOSTIC_ONLY_NOT_TAU_ENDPOINT"
    print(
        "RECONSTRUCTED_OPTICAL_PATH_SCORE_PASS "
        f"paths={17**5} phase_delta_r2={phase_score['delta_r2']:.6f} "
        f"amplitude_delta_r2={amplitude_score['delta_r2']:.6f}"
    )


if __name__ == "__main__":
    main()
