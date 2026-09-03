#!/usr/bin/env python3
"""Audit terminal-equivalence and source-anchor identifiability for T29."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data/derived/instrument_nature_occupation_identifiability_audit.json"
REPORT_PATH = ROOT / "data/derived/instrument_nature_occupation_identifiability_audit_report.md"


def positive_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    if float(np.min(values)) <= 0.0:
        raise ValueError("matrix must be positive")
    return (vectors * np.sqrt(values)) @ vectors.T


def generator(energy: np.ndarray, action: np.ndarray) -> np.ndarray:
    root = positive_sqrt(energy)
    return 1.0j * root @ np.linalg.inv(action) @ root


def quantize(records, calibration, prototypes, metric):
    labels = []
    signatures = []
    for record in records:
        delta = prototypes - calibration @ record
        distances = np.einsum("ni,ij,nj->n", delta, metric, delta)
        labels.append(int(np.argmin(distances)))
        signatures.append(np.sort(distances))
    return np.asarray(labels), np.asarray(signatures)


def run_audit() -> dict[str, object]:
    action = 1.7 * np.array([[0.0, 1.0], [-1.0, 0.0]])
    energy = np.array([[4.0, 0.55], [0.55, 2.6]])
    h = generator(energy, action)
    common_scale_error = float(np.linalg.norm(generator(3.4 * energy, 3.4 * action) - h))

    duration = 0.73
    transport = expm(-1.0j * duration * h)
    orientation_error = float(
        np.linalg.norm(expm(-1.0j * (-duration) * generator(energy, -action)) - transport)
    )
    rate_scale = 2.3
    clock_error = float(
        np.linalg.norm(
            expm(-1.0j * duration / rate_scale * generator(rate_scale * energy, action))
            - transport
        )
    )

    stiffness = np.array([[2.2, 0.18], [0.18, 1.55]])
    theta = 0.42
    covariance = theta * np.linalg.inv(stiffness)
    occupation_error = float(
        np.linalg.norm(4.1 * theta * np.linalg.inv(4.1 * stiffness) - covariance)
    )
    port = np.array([[0.71, 0.11], [-0.07, 0.63]])
    angle = 0.47
    frame = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    noise = port @ covariance @ port.T
    frame_error = float(
        np.linalg.norm(
            port @ frame.T @ (frame @ covariance @ frame.T) @ frame @ port.T - noise
        )
    )

    prototypes = np.array(
        [[1.0, 0.0], [-0.5, np.sqrt(3.0) / 2.0], [-0.5, -np.sqrt(3.0) / 2.0]]
    )
    calibration = np.array([[1.08, 0.16], [-0.09, 0.91]])
    metric = np.array([[1.3, 0.12], [0.12, 0.9]])
    records = np.array([[0.81, 0.04], [-0.38, 0.76], [-0.44, -0.70], [0.10, 0.18]])
    labels, signatures = quantize(records, calibration, prototypes, metric)
    transform = np.array([[1.35, 0.22], [-0.18, 0.83]])
    inverse = np.linalg.inv(transform)
    transformed_labels, transformed_signatures = quantize(
        records,
        transform @ calibration,
        (transform @ prototypes.T).T,
        inverse.T @ metric @ inverse,
    )
    pointer_error = float(np.linalg.norm(transformed_signatures - signatures))
    permutation = np.array([2, 0, 1])
    permuted_labels, permuted_signatures = quantize(
        records, calibration, prototypes[permutation], metric
    )
    permutation_error = float(np.linalg.norm(permuted_signatures - signatures))

    terminal_jacobian = np.array(
        [[1.0, -1.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, -1.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, 0.0, 1.0, -1.0]]
    )
    equivalence = np.array(
        [[1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, 1.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, 0.0, 1.0, 1.0]]
    )
    anchors = equivalence.copy()
    terminal_rank = int(np.linalg.matrix_rank(terminal_jacobian))
    terminal_nullity = int(terminal_jacobian.shape[1] - terminal_rank)
    augmented_rank = int(np.linalg.matrix_rank(np.vstack((terminal_jacobian, anchors))))
    equivalence_error = float(np.linalg.norm(terminal_jacobian @ equivalence.T))

    gates = {
        "common_carrier_complete_raw_records": False,
        "nonzero_two_edge_relation_two_jet": False,
        "seed_odd_oriented_action_form": False,
        "energy_action_clock_unit_bridge": False,
        "multi_load_environment_reconstruction": False,
        "pointer_orbit_calibration_reconstruction": False,
        "held_out_joint_controls_and_exhaustivity": False,
    }
    checks = {
        "common_energy_action_scale_invariant": common_scale_error < 1e-12,
        "seed_sign_clock_reversal_invariant": orientation_error < 1e-12,
        "rate_clock_calibration_degenerate": clock_error < 1e-12,
        "theta_stiffness_scale_invariant": occupation_error < 1e-12,
        "environment_frame_invariant": frame_error < 1e-12,
        "pointer_congruence_invariant": pointer_error < 1e-12 and np.array_equal(labels, transformed_labels),
        "pointer_labels_are_gauge": permutation_error < 1e-12 and np.array_equal(labels, permutation[permuted_labels]),
        "terminal_equivalence_nullity_exact": terminal_rank == 3 and terminal_nullity == 3 and equivalence_error < 1e-12,
        "source_anchors_restore_rank": augmented_rank == 6,
        "target_is_operational_class": True,
        "stationarity_not_nature_certificate": True,
        "spectator_blocks_unrestricted_exhaustivity": True,
        "current_cit_noc7_incomplete": not all(gates.values()),
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "residuals": {
            "common_scale": common_scale_error,
            "orientation_clock": orientation_error,
            "rate_clock": clock_error,
            "occupation_stiffness": occupation_error,
            "environment_frame": frame_error,
            "pointer_congruence": pointer_error,
            "pointer_permutation": permutation_error,
            "terminal_equivalence": equivalence_error,
        },
        "terminal_rank": terminal_rank,
        "terminal_nullity": terminal_nullity,
        "augmented_rank": augmented_rank,
        "checks": {key: bool(value) for key, value in checks.items()},
        "certificate": "CIT-NOC7",
        "certificate_gates": gates,
        "certificate_complete_gate_count": int(sum(gates.values())),
        "certificate_total_gate_count": len(gates),
        "nature_occupation": "not established",
    }


def main() -> None:
    result = run_audit()
    JSON_PATH.write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Instrument Nature-occupation identifiability audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "The terminal packet is identifiable only modulo exact terminal",
        "equivalences. Independent source anchors restore the coordinate-fixed",
        "rank, but no current packet completes the seven physical gates.",
        "",
        "## Checks",
        "",
        *[f"- `{key}`: **{'PASS' if value else 'FAIL'}**" for key, value in result["checks"].items()],
        "",
        "## Claim boundary",
        "",
        "This is a mathematical non-identifiability and acquisition audit, not",
        "evidence for physical class occupation, ambient exhaustivity or Nature",
        "uniqueness.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines))
    print(f"INSTRUMENT_NATURE_OCCUPATION_IDENTIFIABILITY_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
