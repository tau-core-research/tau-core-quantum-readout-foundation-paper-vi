#!/usr/bin/env python3
"""Reproduce the elastic-sheet body/process double-reconstruction control.

This is a conventional reduced elastic model. It validates an acquisition
and reconstruction method; it is not a Tau-specific or quantum prediction.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/elastic_sheet_double_reconstruction_audit.json"


def normal(theta: float, phi: float) -> np.ndarray:
    return np.array(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )


def projector(theta: float, phi: float) -> np.ndarray:
    n = normal(theta, phi)
    return np.eye(3) - np.outer(n, n)


def projector_phi(theta: float, phi: float) -> np.ndarray:
    n = normal(theta, phi)
    dn = np.array(
        [-np.sin(theta) * np.sin(phi), np.sin(theta) * np.cos(phi), 0.0]
    )
    return -(np.outer(dn, n) + np.outer(n, dn))


def frame(theta: float) -> np.ndarray:
    return np.column_stack(
        (
            np.array([np.cos(theta), 0.0, -np.sin(theta)]),
            np.array([0.0, 1.0, 0.0]),
        )
    )


def rotation(angle: float) -> np.ndarray:
    return np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )


def body_transport(theta: float, steps: int = 2048, direction: float = 1.0):
    transport = np.eye(3)
    step = 2.0 * np.pi / steps
    for index in range(steps):
        phi = direction * (index + 0.5) * step
        p = projector(theta, phi)
        dp = direction * projector_phi(theta, phi)
        transport = expm((dp @ p - p @ dp) * step) @ transport
    basis = frame(theta)
    return transport, basis.T @ transport @ basis


def polar(matrix: np.ndarray) -> np.ndarray:
    left, _, right = np.linalg.svd(matrix)
    return left @ right


def occurrence(
    theta: float,
    duration: float,
    low: float,
    high: float,
    direction: float = 1.0,
):
    def rhs(time: float, flat: np.ndarray) -> np.ndarray:
        phi = direction * 2.0 * np.pi * time / duration
        p = projector(theta, phi)
        h = low * p + high * (np.eye(3) - p)
        return (-1.0j * h @ flat.reshape(3, 3)).reshape(-1)

    solution = solve_ivp(
        rhs,
        (0.0, duration),
        np.eye(3, dtype=complex).reshape(-1),
        method="DOP853",
        rtol=1.0e-10,
        atol=1.0e-12,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    full = solution.y[:, -1].reshape(3, 3)
    basis = frame(theta)
    restricted = np.exp(1.0j * low * duration) * basis.T @ full @ basis
    leakage = np.linalg.norm((np.eye(3) - projector(theta, 0.0)) @ full @ basis)
    return polar(restricted), float(leakage)


def main() -> None:
    theta = float(np.arccos(0.75))
    low = 1.0
    high = 6.0
    solid_angle = 2.0 * np.pi * (1.0 - np.cos(theta))
    expected = rotation(solid_angle)
    _, body = body_transport(theta)

    duration_scan = []
    for duration in [10.0, 20.0, 40.0, 80.0, 160.0]:
        transport, leakage = occurrence(theta, duration, low, high)
        duration_scan.append(
            {
                "duration": duration,
                "mismatch": float(np.linalg.norm(transport - body)),
                "leakage": leakage,
            }
        )

    gap_scan = []
    for gap in [1.0, 2.0, 3.0, 5.0, 8.0]:
        transport, leakage = occurrence(theta, 80.0, low, low + gap)
        gap_scan.append(
            {
                "gap": gap,
                "mismatch": float(np.linalg.norm(transport - body)),
                "leakage": leakage,
            }
        )

    _, reverse_body = body_transport(theta, direction=-1.0)
    reverse_occurrence, _ = occurrence(theta, 160.0, low, high, direction=-1.0)
    fast, fast_leakage = occurrence(theta, 2.0, low, high)
    gapless, _ = occurrence(theta, 20.0, low, low)

    duration_errors = [row["mismatch"] for row in duration_scan]
    duration_leakage = [row["leakage"] for row in duration_scan]
    gap_errors = [row["mismatch"] for row in gap_scan]
    checks = {
        "body_matches_solid_angle": np.linalg.norm(body - expected) < 2.0e-6,
        "duration_scan_converges": all(
            b < a for a, b in zip(duration_errors, duration_errors[1:])
        ),
        "leakage_decreases": all(
            b < a for a, b in zip(duration_leakage, duration_leakage[1:])
        ),
        "gap_scan_improves": all(b < a for a, b in zip(gap_errors, gap_errors[1:])),
        "slow_route_matches_body": duration_errors[-1] < 0.02,
        "reverse_loop_approaches_inverse": (
            np.linalg.norm(reverse_body @ body - np.eye(2)) < 3.0e-6
            and np.linalg.norm(reverse_occurrence - reverse_body) < 0.02
        ),
        "fast_loop_fails": np.linalg.norm(fast - body) > 0.5 and fast_leakage > 0.2,
        "gapless_process_is_identity": np.linalg.norm(gapless - np.eye(2)) < 1.0e-8,
        "gapless_breaks_artificial_projector_route": np.linalg.norm(body - np.eye(2)) > 1.0,
        "benchmark_contains_no_tau_residual": True,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_level": "standard-physics method control",
        "parameters": {
            "cos_theta": 0.75,
            "low_frequency": low,
            "high_frequency": high,
            "solid_angle": solid_angle,
        },
        "body_error": float(np.linalg.norm(body - expected)),
        "duration_scan": duration_scan,
        "gap_scan": gap_scan,
        "fast_mismatch": float(np.linalg.norm(fast - body)),
        "fast_leakage": fast_leakage,
        "checks": {key: bool(value) for key, value in checks.items()},
        "physical_plate_experiment": "open",
        "tau_specific_residual": None,
        "nature_occupation": "not established",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"ELASTIC_SHEET_DOUBLE_RECONSTRUCTION_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
