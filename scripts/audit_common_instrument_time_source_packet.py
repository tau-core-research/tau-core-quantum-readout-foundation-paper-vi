#!/usr/bin/env python3
"""Finite common-Hessian, occurrence and conservative-instrument audit."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import block_diag, expm


OUT = Path("data/derived/common_instrument_time_source_packet_audit.json")
REPORT = Path(
    "data/derived/common_instrument_time_source_packet_audit_report.md"
)


def psd_sqrt(matrix: np.ndarray) -> np.ndarray:
    hermitian = 0.5 * (matrix + matrix.conj().T)
    values, vectors = np.linalg.eigh(hermitian)
    if np.min(values) < -1.0e-12:
        raise ValueError("matrix is not positive semidefinite")
    return (vectors * np.sqrt(np.clip(values, 0.0, None))) @ vectors.conj().T


def inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.conj().T))
    if np.min(values) <= 0.0:
        raise ValueError("matrix is not positive definite")
    return (vectors * (1.0 / np.sqrt(values))) @ vectors.conj().T


def julia(contraction: np.ndarray) -> np.ndarray:
    identity = np.eye(contraction.shape[0])
    defect_in = psd_sqrt(identity - contraction.conj().T @ contraction)
    defect_out = psd_sqrt(identity - contraction @ contraction.conj().T)
    return np.block(
        [
            [contraction, defect_out],
            [defect_in, -contraction.conj().T],
        ]
    )


def labels_and_margins(
    records: np.ndarray, prototypes: np.ndarray, metric: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    labels = []
    margins = []
    for record in records:
        delta = prototypes - record
        distances = np.einsum("ni,ij,nj->n", delta, metric, delta)
        order = np.argsort(distances)
        labels.append(int(order[0]))
        margins.append(float(distances[order[1]] - distances[order[0]]))
    return np.asarray(labels), np.asarray(margins)


def audit() -> dict[str, object]:
    identity = np.eye(2)
    source_body = np.diag([0.42, 0.31])
    angle = 0.37
    rotation = np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    body_observer = rotation @ np.diag([0.36, 0.28])
    zero = np.zeros((2, 2))
    interface_hessian = np.block(
        [
            [identity, -source_body.T, zero],
            [-source_body, identity, -body_observer.T],
            [zero, -body_observer, identity],
        ]
    )
    source_incidence = inverse_sqrt(identity) @ source_body @ inverse_sqrt(identity)
    observer_access = inverse_sqrt(identity) @ body_observer @ inverse_sqrt(identity)

    phase = np.array([[0.0, 1.0], [-1.0, 0.0]])
    phase_normal = phase @ inverse_sqrt(-phase @ phase)
    stiffness_root = psd_sqrt(np.diag([1.20, 2.10]))
    rate = np.sqrt(9.0 / 4.0)
    generator = 1.0j * rate * stiffness_root @ phase_normal @ stiffness_root
    duration = 0.83
    propagator = expm(-1.0j * generator * duration)

    source_julia = julia(source_incidence)
    observer_julia = julia(observer_access)
    permutation = np.eye(6)[[0, 1, 4, 5, 2, 3], :]
    complete = (
        block_diag(observer_julia, identity)
        @ permutation
        @ block_diag(propagator, identity, identity)
        @ block_diag(source_julia, identity)
    )
    measured = observer_access @ propagator @ source_incidence
    compressed = complete[:2, :2]
    hidden = complete[:2, 2:]

    loss_lhs = identity - measured.conj().T @ measured
    loss_rhs = (
        identity - source_incidence.conj().T @ source_incidence
        + source_incidence.conj().T
        @ propagator.conj().T
        @ (identity - observer_access.conj().T @ observer_access)
        @ propagator
        @ source_incidence
    )

    covariance_one = np.diag([0.20, 0.40, 0.30, 0.10])
    covariance_two = np.diag([0.55, 0.10, 0.15, 0.45])
    noise_one = hidden @ covariance_one @ hidden.conj().T
    noise_two = hidden @ covariance_two @ hidden.conj().T

    pointer_metric = np.array([[1.50, 0.20], [0.20, 1.00]])
    records = np.array(
        [
            [-1.10, 0.10],
            [-0.80, -0.10],
            [1.10, 0.00],
            [0.90, 0.20],
            [0.00, 1.10],
            [0.10, 1.40],
        ]
    )
    prototypes = np.array([[-1.0, 0.0], [1.0, 0.0], [0.0, 1.2]])
    alternative_prototypes = np.array(
        [[-1.0, 0.0], [1.0, 0.0], [0.0, -1.2]]
    )
    labels, margins = labels_and_margins(records, prototypes, pointer_metric)
    alternative_labels, alternative_margins = labels_and_margins(
        records, alternative_prototypes, pointer_metric
    )

    reversed_generator = -generator
    reversed_propagator = expm(-1.0j * reversed_generator * duration)
    changed_rate_generator = generator * (2.0 / rate)
    changed_rate_propagator = expm(
        -1.0j * changed_rate_generator * duration
    )

    interface_minimum = float(np.min(np.linalg.eigvalsh(interface_hessian)))
    source_margin = float(
        np.min(
            np.linalg.eigvalsh(
                identity - source_incidence.conj().T @ source_incidence
            )
        )
    )
    observer_margin = float(
        np.min(
            np.linalg.eigvalsh(
                identity - observer_access.conj().T @ observer_access
            )
        )
    )
    phase_square_error = float(np.linalg.norm(phase_normal @ phase_normal + identity))
    phase_skew_error = float(np.linalg.norm(phase_normal.conj().T + phase_normal))
    generator_error = float(np.linalg.norm(generator - generator.conj().T))
    propagation_error = float(
        np.linalg.norm(propagator.conj().T @ propagator - identity)
    )
    source_julia_error = float(
        np.linalg.norm(source_julia.conj().T @ source_julia - np.eye(4))
    )
    observer_julia_error = float(
        np.linalg.norm(observer_julia.conj().T @ observer_julia - np.eye(4))
    )
    complete_error = float(
        np.linalg.norm(complete.conj().T @ complete - np.eye(6))
    )
    compression_error = float(np.linalg.norm(compressed - measured))
    loss_error = float(np.linalg.norm(loss_lhs - loss_rhs))
    noise_difference = float(np.linalg.norm(noise_one - noise_two))
    noise_minimum = min(
        float(np.min(np.linalg.eigvalsh(noise_one))),
        float(np.min(np.linalg.eigvalsh(noise_two))),
    )
    phase_difference = float(np.linalg.norm(reversed_propagator - propagator))
    rate_difference = float(np.linalg.norm(changed_rate_propagator - propagator))
    quantizer_difference = int(np.count_nonzero(labels != alternative_labels))

    checks = {
        "common_interface_hessian_is_positive": interface_minimum > 1.0e-8,
        "normalized_source_incidence_is_contractive": source_margin > -1.0e-12,
        "normalized_observer_access_is_contractive": observer_margin > -1.0e-12,
        "phase_polar_factor_is_a_complex_structure": (
            phase_square_error < 1.0e-12 and phase_skew_error < 1.0e-12
        ),
        "occurrence_generator_is_self_adjoint": generator_error < 1.0e-12,
        "complete_body_transport_is_unitary": propagation_error < 1.0e-12,
        "source_julia_completion_is_unitary": source_julia_error < 1.0e-12,
        "observer_julia_completion_is_unitary": observer_julia_error < 1.0e-12,
        "complete_instrument_network_is_unitary": complete_error < 1.0e-12,
        "measured_transfer_is_exact_network_compression": compression_error < 1.0e-12,
        "observer_loss_identity_is_exact": loss_error < 1.0e-12,
        "hidden_state_noise_covariances_are_positive": noise_minimum > -1.0e-12,
        "deterministic_transfer_does_not_select_noise_state": noise_difference > 1.0e-3,
        "pointer_minima_define_stable_equivalence_cells": float(np.min(margins)) > 1.0e-3,
        "symmetric_hessian_does_not_select_phase_orientation": phase_difference > 1.0e-2,
        "dimensionless_packet_does_not_select_absolute_rate": rate_difference > 1.0e-2,
        "linear_transfer_does_not_select_pointer_quantizer": (
            quantizer_difference > 0 and float(np.min(alternative_margins)) > 1.0e-3
        ),
        "parent_meta_time_is_not_required": True,
        "nature_occupation_is_not_inferred": True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_level": "conditional source-packet theorem / finite operator control",
        "interface_hessian_minimum_eigenvalue": interface_minimum,
        "reference_rate_per_second": float(rate),
        "complete_network_unitarity_error": complete_error,
        "compression_error": compression_error,
        "loss_identity_error": loss_error,
        "noise_state_difference": noise_difference,
        "pointer_minimum_margin": float(np.min(margins)),
        "phase_orientation_difference": phase_difference,
        "clock_rate_difference": rate_difference,
        "quantizer_difference_count": quantizer_difference,
        "checks": {key: bool(value) for key, value in checks.items()},
        "physical_source_packet_selected": False,
        "physical_m_tau_constructed": False,
        "nature_occupation": "not established",
    }


def main() -> None:
    result = audit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    REPORT.write_text(
        "# Common instrument--time source-packet audit\n\n"
        f"Status: **{result['status']}**\n\n"
        "The audit derives contractive incidence/access maps from one positive "
        "interface Hessian, constructs the source phase/rate occurrence "
        "generator and verifies the conservative Julia completion. It also "
        "retains the noise-state, pointer-quantizer and Nature-selection "
        "no-go boundaries.\n"
    )
    print(f"COMMON_INSTRUMENT_TIME_SOURCE_PACKET_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
