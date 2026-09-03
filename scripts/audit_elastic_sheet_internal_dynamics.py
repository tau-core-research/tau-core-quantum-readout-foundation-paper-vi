#!/usr/bin/env python3
"""Audit Kato/internal-dynamics factorization for one elastic spectral band.

Two conventional finite Hamiltonian families have exactly the same isolated
rank-two projector path but different spectra inside that band.  The audit
checks that the Kato/body transport is common, while the complete occurrence
transport is not.  It then reconstructs the in-band dynamical propagator in
the Kato frame and verifies the standard adiabatic factorization.

This is a standard-physics method and no-go control.  It is not evidence for
the Tau parent, a physical universe-level M_tau, or Nature occupation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/derived"
JSON_PATH = OUT_DIR / "elastic_sheet_internal_dynamics_audit.json"
REPORT_PATH = OUT_DIR / "elastic_sheet_internal_dynamics_audit_report.md"


def unit_normal(theta: float, phi: float) -> np.ndarray:
    return np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )


def normal_phi_derivative(theta: float, phi: float) -> np.ndarray:
    return np.array(
        [-np.sin(theta) * np.sin(phi), np.sin(theta) * np.cos(phi), 0.0]
    )


def modal_frame(theta: float, phi: float) -> np.ndarray:
    """Return the source-fixed oriented tangent frame [e_theta,e_phi]."""

    return np.column_stack(
        (
            np.array(
                [
                    np.cos(theta) * np.cos(phi),
                    np.cos(theta) * np.sin(phi),
                    -np.sin(theta),
                ]
            ),
            np.array([-np.sin(phi), np.cos(phi), 0.0]),
        )
    )


def modal_projector(theta: float, phi: float) -> np.ndarray:
    normal = unit_normal(theta, phi)
    return np.eye(3) - np.outer(normal, normal)


def projector_phi_derivative(theta: float, phi: float) -> np.ndarray:
    normal = unit_normal(theta, phi)
    derivative = normal_phi_derivative(theta, phi)
    return -(np.outer(derivative, normal) + np.outer(normal, derivative))


def frequency_operator(
    theta: float,
    phi: float,
    low_frequency: float,
    high_frequency: float,
    internal_split: float,
) -> np.ndarray:
    """Return a positive frequency operator with one isolated rank-two band."""

    frame = modal_frame(theta, phi)
    normal = unit_normal(theta, phi)
    band = np.diag(
        [low_frequency + internal_split, low_frequency - internal_split]
    )
    return frame @ band @ frame.T + high_frequency * np.outer(normal, normal)


def unitary_polar(matrix: np.ndarray) -> np.ndarray:
    left, _, right = np.linalg.svd(matrix)
    return left @ right


def distance_from_scalar_unitary(matrix: np.ndarray) -> float:
    """Return distance from the nearest scalar phase times the identity."""

    phase = np.angle(np.trace(matrix)) if abs(np.trace(matrix)) > 1.0e-14 else 0.0
    return float(np.linalg.norm(matrix - np.exp(1.0j * phase) * np.eye(2)))


def integrate_factorization(
    theta: float,
    duration: float,
    low_frequency: float,
    high_frequency: float,
    internal_split: float,
    relative_tolerance: float = 1.0e-10,
    absolute_tolerance: float = 1.0e-12,
) -> dict[str, object]:
    """Integrate exact occurrence, Kato transport and Kato-frame dynamics."""

    basis0 = modal_frame(theta, 0.0)
    initial = np.concatenate(
        (
            np.eye(3, dtype=complex).reshape(-1),
            np.eye(3, dtype=complex).reshape(-1),
            np.eye(2, dtype=complex).reshape(-1),
        )
    )

    def right_hand_side(time: float, state: np.ndarray) -> np.ndarray:
        occurrence = state[:9].reshape(3, 3)
        kato = state[9:18].reshape(3, 3)
        internal = state[18:].reshape(2, 2)
        phi = 2.0 * np.pi * time / duration
        projector = modal_projector(theta, phi)
        projector_dot = (
            2.0 * np.pi / duration * projector_phi_derivative(theta, phi)
        )
        kato_generator = projector_dot @ projector - projector @ projector_dot
        operator = frequency_operator(
            theta,
            phi,
            low_frequency,
            high_frequency,
            internal_split,
        )
        effective_band_operator = (
            basis0.T.conj() @ kato.T.conj() @ operator @ kato @ basis0
        )
        return np.concatenate(
            (
                (-1.0j * operator @ occurrence).reshape(-1),
                (kato_generator @ kato).reshape(-1),
                (-1.0j * effective_band_operator @ internal).reshape(-1),
            )
        )

    solution = solve_ivp(
        right_hand_side,
        (0.0, duration),
        initial,
        method="DOP853",
        rtol=relative_tolerance,
        atol=absolute_tolerance,
    )
    if not solution.success:
        raise RuntimeError(solution.message)

    occurrence = solution.y[:9, -1].reshape(3, 3)
    kato = solution.y[9:18, -1].reshape(3, 3)
    internal = solution.y[18:, -1].reshape(2, 2)
    exact_band_map = occurrence @ basis0
    adiabatic_band_map = kato @ basis0 @ internal
    restricted_occurrence = basis0.T.conj() @ occurrence @ basis0
    body_holonomy = basis0.T.conj() @ kato @ basis0
    recovered_geometry = unitary_polar(
        restricted_occurrence @ internal.T.conj()
    )
    scalar_removed_geometry = unitary_polar(
        np.exp(1.0j * low_frequency * duration) * restricted_occurrence
    )
    initial_projector = modal_projector(theta, 0.0)
    leakage = np.linalg.norm(
        (np.eye(3) - initial_projector) @ exact_band_map,
        ord="fro",
    )
    return {
        "occurrence": occurrence,
        "kato": kato,
        "internal": internal,
        "body_holonomy": body_holonomy,
        "restricted_occurrence": restricted_occurrence,
        "factorization_error": float(
            np.linalg.norm(exact_band_map - adiabatic_band_map, ord="fro")
        ),
        "geometric_recovery_error": float(
            np.linalg.norm(recovered_geometry - body_holonomy, ord="fro")
        ),
        "scalar_only_error": float(
            np.linalg.norm(scalar_removed_geometry - body_holonomy, ord="fro")
        ),
        "leakage": float(leakage),
        "internal_non_scalarity": distance_from_scalar_unitary(internal),
        "function_evaluations": int(solution.nfev),
    }


def serialize_matrix(matrix: np.ndarray) -> dict[str, object]:
    return {"real": np.real(matrix).tolist(), "imag": np.imag(matrix).tolist()}


def run_audit() -> dict[str, object]:
    theta = float(np.arccos(0.75))
    low_frequency = 1.0
    high_frequency = 6.0
    internal_split = 0.17
    durations = [10.0, 20.0, 40.0, 80.0, 160.0]

    projector_errors = []
    internal_spectrum_differences = []
    for phi in np.linspace(0.0, 2.0 * np.pi, 13):
        analytic = modal_projector(theta, float(phi))
        for split in (0.0, internal_split):
            operator = frequency_operator(
                theta,
                float(phi),
                low_frequency,
                high_frequency,
                split,
            )
            _, eigenvectors = np.linalg.eigh(operator)
            spectral = eigenvectors[:, :2] @ eigenvectors[:, :2].T
            projector_errors.append(np.linalg.norm(spectral - analytic))
        degenerate_spectrum = np.linalg.eigvalsh(
            frequency_operator(
                theta, float(phi), low_frequency, high_frequency, 0.0
            )
        )[:2]
        split_spectrum = np.linalg.eigvalsh(
            frequency_operator(
                theta,
                float(phi),
                low_frequency,
                high_frequency,
                internal_split,
            )
        )[:2]
        internal_spectrum_differences.append(
            np.linalg.norm(split_spectrum - degenerate_spectrum)
        )

    split_scan = []
    for duration in durations:
        row = integrate_factorization(
            theta,
            duration,
            low_frequency,
            high_frequency,
            internal_split,
        )
        split_scan.append(
            {
                "duration": duration,
                "factorization_error": row["factorization_error"],
                "geometric_recovery_error": row["geometric_recovery_error"],
                "scalar_only_error": row["scalar_only_error"],
                "leakage": row["leakage"],
                "internal_non_scalarity": row["internal_non_scalarity"],
            }
        )

    degenerate = integrate_factorization(
        theta,
        durations[-1],
        low_frequency,
        high_frequency,
        0.0,
    )
    split = integrate_factorization(
        theta,
        durations[-1],
        low_frequency,
        high_frequency,
        internal_split,
    )
    scalar_internal = np.exp(-1.0j * low_frequency * durations[-1]) * np.eye(2)
    occurrence_difference = float(
        np.linalg.norm(
            (degenerate["occurrence"] - split["occurrence"])
            @ modal_frame(theta, 0.0),
            ord="fro",
        )
    )
    factor_errors = [row["factorization_error"] for row in split_scan]
    recovery_errors = [row["geometric_recovery_error"] for row in split_scan]

    checks = {
        "same_projector_path": max(projector_errors) < 1.0e-10,
        "different_internal_spectra": min(internal_spectrum_differences) > 0.2,
        "same_kato_body_geometry": np.linalg.norm(
            degenerate["body_holonomy"] - split["body_holonomy"]
        ) < 1.0e-10,
        "different_complete_occurrence_transport": occurrence_difference > 0.2,
        "degenerate_internal_dynamics_is_scalar": np.linalg.norm(
            degenerate["internal"] - scalar_internal
        ) < 2.0e-7,
        "split_internal_dynamics_is_not_scalar": split["internal_non_scalarity"] > 0.2,
        "factorization_improves_with_duration": factor_errors[-1] < factor_errors[0],
        "matrix_corrected_geometry_improves": recovery_errors[-1] < recovery_errors[0],
        "slow_factorization_matches": factor_errors[-1] < 0.03,
        "matrix_correction_recovers_body": recovery_errors[-1] < 0.03,
        "scalar_only_correction_fails_for_split_band": split["scalar_only_error"] > 0.2,
        "benchmark_contains_no_tau_residual": True,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_level": "standard-physics adiabatic method/no-go control",
        "parameters": {
            "cos_theta": 0.75,
            "low_frequency_s^-1": low_frequency,
            "high_frequency_s^-1": high_frequency,
            "internal_split_s^-1": internal_split,
            "external_gap_s^-1": high_frequency
            - (low_frequency + internal_split),
        },
        "maximum_projector_error": float(max(projector_errors)),
        "minimum_internal_spectrum_difference": float(
            min(internal_spectrum_differences)
        ),
        "same_projector_occurrence_difference": occurrence_difference,
        "split_duration_scan": split_scan,
        "degenerate_scalar_internal_error": float(
            np.linalg.norm(degenerate["internal"] - scalar_internal)
        ),
        "final_body_holonomy": serialize_matrix(split["body_holonomy"]),
        "final_split_internal_propagator": serialize_matrix(split["internal"]),
        "checks": {key: bool(value) for key, value in checks.items()},
        "physical_plate_experiment": "open",
        "tau_specific_residual": None,
        "nature_occupation": "not established",
    }
    return result


def write_report(result: dict[str, object]) -> None:
    scan = result["split_duration_scan"]
    lines = [
        "# Tau Core elastic-sheet internal-dynamics audit v0.1",
        "",
        f"Status: **{result['status']}**",
        "",
        "This conventional finite control compares two frequency-operator",
        "families with exactly the same isolated rank-two projector path but",
        "different in-band spectra. It tests the standard Kato-frame",
        "adiabatic factorization; it is not a Tau-specific prediction.",
        "",
        "| duration | factorization error | matrix-corrected geometry error | scalar-only error | leakage |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in scan:
        lines.append(
            f"| {row['duration']:.0f} | {row['factorization_error']:.6g} | "
            f"{row['geometric_recovery_error']:.6g} | "
            f"{row['scalar_only_error']:.6g} | {row['leakage']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            *[
                f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
                for name, passed in result["checks"].items()
            ],
            "",
            "## Claim boundary",
            "",
            "The common projector determines the common Kato/body geometry,",
            "but it does not determine the complete occurrence transport.",
            "A scalar phase removal is valid only for the exactly degenerate",
            "band used in the earlier finite control. A general isolated band",
            "requires independent reconstruction of its matrix-valued internal",
            "dynamical propagator. Physical plate occupation and every",
            "Tau-specific inference remain open.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = run_audit()
    JSON_PATH.write_text(json.dumps(result, indent=2) + "\n")
    write_report(result)
    print(f"ELASTIC_SHEET_INTERNAL_DYNAMICS_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
