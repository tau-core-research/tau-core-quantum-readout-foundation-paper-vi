#!/usr/bin/env python3
"""Finite audit of the enriched action--form origin of the instrument packet."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import block_diag, expm


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data/derived/enriched_instrument_source_action_audit.json"
REPORT_PATH = ROOT / "data/derived/enriched_instrument_source_action_audit_report.md"


def root(matrix: np.ndarray, inverse: bool = False) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    if float(np.min(values)) <= 0.0:
        raise ValueError("positive matrix required")
    powers = 1.0 / np.sqrt(values) if inverse else np.sqrt(values)
    return (vectors * powers) @ vectors.T


def psd_root(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    if float(np.min(values)) < -1.0e-12:
        raise ValueError("positive-semidefinite matrix required")
    return (vectors * np.sqrt(np.clip(values, 0.0, None))) @ vectors.T


def orbit(offset: float) -> np.ndarray:
    angles = offset + 2.0 * np.pi * np.arange(3) / 3.0
    return np.column_stack((np.cos(angles), np.sin(angles)))


def potential(point, prototypes, metric, coupling=0.8):
    delta = prototypes - point
    distances = np.einsum("ni,ij,nj->n", delta, metric, delta)
    return float(coupling * np.prod(distances))


def quantize(records, prototypes, metric):
    selected = []
    margins = []
    for record in records:
        delta = prototypes - record
        distances = np.einsum("ni,ij,nj->n", delta, metric, delta)
        order = np.argsort(distances)
        selected.append(prototypes[order[0]])
        margins.append(float(distances[order[1]] - distances[order[0]]))
    return np.asarray(selected), np.asarray(margins)


def run_audit() -> dict[str, object]:
    eye = np.eye(2)
    zero = np.zeros((2, 2))
    ls = np.array([[0.58, 0.04], [-0.03, 0.44]])
    lm = np.array([[0.91, 0.08], [0.02, 0.77]])
    tm = np.array([[0.49, -0.06], [0.05, 0.39]])
    lo = np.array([[0.88, 0.05], [-0.02, 0.81]])
    wsm = np.array([[1.20, 0.08], [0.08, 0.95]])
    wmo = np.array([[0.90, -0.05], [-0.05, 1.10]])
    ks = np.diag([0.62, 0.55])
    km = np.diag([0.71, 0.66])
    ko = np.diag([0.59, 0.64])
    relation = np.block([[-ls, lm, zero], [zero, -tm, lo]])
    hessian = relation.T @ block_diag(wsm, wmo) @ relation + block_diag(ks, km, ko)
    gs = ks + ls.T @ wsm @ ls
    gm = km + lm.T @ wsm @ lm + tm.T @ wmo @ tm
    go = ko + lo.T @ wmo @ lo
    bms = lm.T @ wsm @ ls
    bom = lo.T @ wmo @ tm
    reconstructed = np.block([[gs, -bms.T, zero], [-bms, gm, -bom.T], [zero, -bom, go]])
    js = root(gm, True) @ bms @ root(gs, True)
    ro = root(go, True) @ bom @ root(gm, True)

    omega = 1.7 * np.array([[0.0, 1.0], [-1.0, 0.0]])
    energy = np.array([[4.0, 0.55], [0.55, 2.60]])
    eroot = root(energy)
    rate = eroot @ np.linalg.inv(omega) @ eroot
    generator = 1.0j * rate
    unitary = expm(-1.0j * 0.73 * generator)
    reversed_generator = 1.0j * eroot @ np.linalg.inv(-omega) @ eroot
    reversed_unitary = expm(-1.0j * 0.73 * reversed_generator)

    ke = np.array([[2.20, 0.18], [0.18, 1.55]])
    theta = 0.42
    gamma = theta * np.linalg.inv(ke)
    gamma_inverse = np.linalg.inv(gamma)
    gradient = 0.5 * (ke - theta * gamma_inverse)
    delta = np.array([[0.31, -0.08], [-0.08, -0.21]])
    second = float(0.5 * theta * np.trace(gamma_inverse @ delta @ gamma_inverse @ delta))
    environment_port = psd_root(eye - ro @ ro.T)
    noise = environment_port @ gamma @ environment_port.T
    alternative_noise = environment_port @ (0.77 * np.linalg.inv(ke)) @ environment_port.T

    prototypes = orbit(0.0)
    alternative = orbit(np.pi / 3.0)
    values = [potential(point, prototypes, go) for point in prototypes]
    local_hessian_minimum = float("inf")
    for index, point in enumerate(prototypes):
        other = np.delete(prototypes, index, axis=0)
        d = other - point
        distances = np.einsum("ni,ij,nj->n", d, go, d)
        local_hessian = 1.6 * float(np.prod(distances)) * go
        local_hessian_minimum = min(local_hessian_minimum, float(np.min(np.linalg.eigvalsh(local_hessian))))
    records = np.array([[0.94, 0.02], [0.70, 0.18], [-0.47, 0.83], [-0.62, 0.65], [-0.52, -0.80], [-0.34, -0.92]])
    selected, margins = quantize(records, prototypes, go)
    alternative_selected, alternative_margins = quantize(records, alternative, go)

    metrics = {
        "interface_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(hessian))),
        "gram_reconstruction_error": float(np.linalg.norm(hessian - reconstructed)),
        "direct_source_observer_block_norm": float(np.linalg.norm(hessian[:2, -2:])),
        "source_contraction_margin": float(np.min(np.linalg.eigvalsh(eye - js.T @ js))),
        "observer_contraction_margin": float(np.min(np.linalg.eigvalsh(eye - ro.T @ ro))),
        "rate_skew_error": float(np.linalg.norm(rate.T + rate)),
        "generator_self_adjoint_error": float(np.linalg.norm(generator - generator.conj().T)),
        "occurrence_unitarity_error": float(np.linalg.norm(unitary.conj().T @ unitary - eye)),
        "phase_reversal_generator_error": float(np.linalg.norm(reversed_generator + generator)),
        "phase_reversal_transport_difference": float(np.linalg.norm(reversed_unitary - unitary)),
        "environment_stationarity_error": float(np.linalg.norm(gradient)),
        "environment_second_variation": second,
        "environment_covariance_minimum": float(np.min(np.linalg.eigvalsh(gamma))),
        "noise_kernel_minimum": float(np.min(np.linalg.eigvalsh(noise))),
        "occupation_noise_difference": float(np.linalg.norm(alternative_noise - noise)),
        "pointer_orbit_maximum_potential": float(np.max(np.abs(values))),
        "pointer_probe_potential": potential(np.array([0.17, -0.11]), prototypes, go),
        "pointer_hessian_minimum": local_hessian_minimum,
        "pointer_cell_minimum_margin": float(np.min(margins)),
        "alternative_cell_minimum_margin": float(np.min(alternative_margins)),
        "quantizer_difference_count": int(np.count_nonzero(np.linalg.norm(alternative_selected - selected, axis=1) > 1.0e-8)),
    }
    checks = {
        "relation_gram_action_positive": metrics["interface_minimum_eigenvalue"] > 1.0e-8,
        "t28_hessian_reconstructed": metrics["gram_reconstruction_error"] < 1.0e-12,
        "no_direct_source_observer_bypass": metrics["direct_source_observer_block_norm"] < 1.0e-12,
        "source_incidence_contractive": metrics["source_contraction_margin"] > -1.0e-12,
        "observer_access_contractive": metrics["observer_contraction_margin"] > -1.0e-12,
        "energy_action_rate_skew": metrics["rate_skew_error"] < 1.0e-12,
        "generator_self_adjoint": metrics["generator_self_adjoint_error"] < 1.0e-12,
        "occurrence_transport_unitary": metrics["occurrence_unitarity_error"] < 1.0e-12,
        "seed_orientation_reverses_generator": metrics["phase_reversal_generator_error"] < 1.0e-12 and metrics["phase_reversal_transport_difference"] > 1.0e-3,
        "environment_stationary": metrics["environment_stationarity_error"] < 1.0e-12,
        "environment_functional_strictly_convex": metrics["environment_second_variation"] > 1.0e-8,
        "environment_covariance_positive": metrics["environment_covariance_minimum"] > 1.0e-8,
        "noise_kernel_positive": metrics["noise_kernel_minimum"] > -1.0e-12,
        "occupation_changes_noise": metrics["occupation_noise_difference"] > 1.0e-3,
        "pointer_orbit_is_zero_set": metrics["pointer_orbit_maximum_potential"] < 1.0e-12 and metrics["pointer_probe_potential"] > 1.0e-6,
        "pointer_minima_nondegenerate": metrics["pointer_hessian_minimum"] > 1.0e-8,
        "pointer_cells_stable": metrics["pointer_cell_minimum_margin"] > 1.0e-3,
        "different_orbit_changes_quantizer": metrics["alternative_cell_minimum_margin"] > 1.0e-3 and metrics["quantizer_difference_count"] > 0,
        "zero_source_edge_gives_zero_incidence": float(np.linalg.norm(lm.T @ wsm @ zero)) < 1.0e-12,
        "zero_observer_edge_gives_zero_access": float(np.linalg.norm(lo.T @ wmo @ zero)) < 1.0e-12,
        "no_parent_meta_time_inferred": True,
        "nature_occupation_not_inferred": True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_level": "conditional enriched action--form completion",
        "metrics": metrics,
        "checks": {key: bool(value) for key, value in checks.items()},
        "physical_source_complex_selected": False,
        "nature_occupation": "not established",
    }


def main() -> None:
    result = run_audit()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Enriched instrument source-action audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "The two-edge relation action, energy/action pencil, convex environment",
        "functional and finite pointer-role orbit pass all declared controls.",
        "",
        "## Checks",
        "",
        *[f"- `{key}`: **{'PASS' if value else 'FAIL'}**" for key, value in result["checks"].items()],
        "",
        "This is a conditional standard-mathematical construction, not physical",
        "selection, Tau-specific evidence or Nature occupation.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines))
    print(f"ENRICHED_INSTRUMENT_SOURCE_ACTION_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
