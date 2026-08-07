#!/usr/bin/env python3
"""Construct one qubit path supporting work, state, and Uhlmann readouts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "joint_qubit_source_model_audit.json"
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def hermitian_function(a: np.ndarray, fn) -> np.ndarray:
    values, vectors = np.linalg.eigh(a)
    return (vectors * fn(values)) @ vectors.conj().T


def hamiltonian(q: float, delta0: float, modulation: float, theta: float) -> np.ndarray:
    delta = delta0 * (1.0 + modulation * np.cos(q))
    n = np.array([np.sin(theta) * np.cos(q), np.sin(theta) * np.sin(q), np.cos(theta)])
    return 0.5 * delta * (n[0] * SX + n[1] * SY + n[2] * SZ)


def gibbs_state(h: np.ndarray, beta: float) -> np.ndarray:
    raw = hermitian_function(-beta * h, np.exp)
    return raw / np.trace(raw)


def sqrtm_psd(a: np.ndarray) -> np.ndarray:
    return hermitian_function(a, lambda x: np.sqrt(np.clip(x, 0.0, None)))


def logm_psd(a: np.ndarray) -> np.ndarray:
    return hermitian_function(a, lambda x: np.log(np.clip(x, 1e-15, None)))


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    middle = sqrtm_psd(rho) @ sigma @ sqrtm_psd(rho)
    return float(np.real(np.trace(sqrtm_psd(middle))) ** 2)


def unitary_exponential(h: np.ndarray, factor: complex) -> np.ndarray:
    return hermitian_function(h, lambda x: np.exp(factor * x))


def work_characteristic(rho: np.ndarray, h0: np.ndarray, h1: np.ndarray, u: float) -> complex:
    return np.trace(unitary_exponential(h1, 1j * u) @ unitary_exponential(h0, -1j * u) @ rho)


def uhlmann_transport(states: list[np.ndarray]) -> tuple[complex, np.ndarray]:
    roots = [sqrtm_psd(rho) for rho in states]
    unitary = I2.copy()
    w0 = roots[0].copy()
    previous = w0
    for root in roots[1:]:
        current = previous.conj().T @ root
        left, _, right_h = np.linalg.svd(current)
        unitary = right_h.conj().T @ left.conj().T
        previous = root @ unitary
    loop_overlap = np.trace(w0.conj().T @ previous)
    return loop_overlap, unitary


def main() -> None:
    beta = 1.3
    delta0 = 1.0
    modulation = 0.35
    theta = 1.0
    points = 65
    qs = np.linspace(0.0, 2.0 * np.pi, points)
    hs = [hamiltonian(q, delta0, modulation, theta) for q in qs]
    states = [gibbs_state(h, beta) for h in hs]

    endpoint_fidelities = [fidelity(states[i], states[i + 1]) for i in range(points - 1)]
    xq_steps = [2.0 * (1.0 - np.sqrt(f)) for f in endpoint_fidelities]
    relative_entropies = [
        float(np.real(np.trace(states[i] @ (logm_psd(states[i]) - logm_psd(states[i + 1])))))
        for i in range(points - 1)
    ]
    work_to_chord_ratios = [d / x for d, x in zip(relative_entropies, xq_steps) if x > 1e-12]
    u_grid = [0.0, 0.4, 0.8, 1.2]
    work_chars = [work_characteristic(states[0], hs[0], hs[1], u) for u in u_grid]
    mean_quench_work = float(np.real(np.trace(states[0] @ (hs[1] - hs[0]))))
    loop_overlap, loop_unitary = uhlmann_transport(states)
    phase = float(np.angle(loop_overlap))

    result = {
        "schema_version": "1.0",
        "model": {
            "H_q": "Delta0(1+m cos q) n(q).sigma/2",
            "n_q": "(sin(theta) cos q, sin(theta) sin q, cos(theta))",
            "rho_q": "exp(-beta H(q))/Tr exp(-beta H(q))",
            "beta": beta,
            "delta0": delta0,
            "modulation": modulation,
            "theta": theta,
            "path_points": points,
        },
        "same_path_readouts": {
            "work_characteristic_real_imag": [
                [u, float(value.real), float(value.imag)] for u, value in zip(u_grid, work_chars)
            ],
            "first_step_mean_quench_work": mean_quench_work,
            "mean_step_xQ": float(np.mean(xq_steps)),
            "max_step_xQ": float(np.max(xq_steps)),
            "min_relative_entropy_to_xQ_ratio": float(np.min(work_to_chord_ratios)),
            "max_relative_entropy_to_xQ_ratio": float(np.max(work_to_chord_ratios)),
            "relative_entropy_to_xQ_ratio_spread": float(np.ptp(work_to_chord_ratios)),
            "loop_uhlmann_overlap_real_imag": [float(loop_overlap.real), float(loop_overlap.imag)],
            "loop_uhlmann_phase": phase,
            "loop_unitary_defect": float(np.linalg.norm(loop_unitary.conj().T @ loop_unitary - I2)),
        },
        "checks": {
            "closed_state_loop": bool(np.linalg.norm(states[0] - states[-1]) < 1e-12),
            "nontrivial_work_characteristic": bool(any(abs(v - 1.0) > 1e-6 for v in work_chars[1:])),
            "nonzero_state_distance": bool(max(xq_steps) > 1e-8),
            "nonzero_uhlmann_phase": bool(abs(phase) > 1e-5),
            "unitary_transport": bool(np.linalg.norm(loop_unitary.conj().T @ loop_unitary - I2) < 1e-10),
            "work_is_independent_body_action": False,
            "one_constant_converts_dissipated_work_to_xQ": bool(np.ptp(work_to_chord_ratios) < 1e-6),
        },
        "verdict": (
            "One closed qubit Hamiltonian family consistently supports work-characteristic, "
            "endpoint-state and Uhlmann-loop readouts. This proves protocol compatibility, "
            "not x_A=x_Q: the quench work remains a terminal thermodynamic observable until "
            "an independent source/body action map and common unit are derived."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    expected_false = {"work_is_independent_body_action", "one_constant_converts_dissipated_work_to_xQ"}
    assert all(value for key, value in result["checks"].items() if key not in expected_false)
    assert result["checks"]["work_is_independent_body_action"] is False
    assert result["checks"]["one_constant_converts_dissipated_work_to_xQ"] is False
    print(f"JOINT_QUBIT_SOURCE_MODEL_PASS phase={phase:.6f} mean_work={mean_quench_work:.6e}")


if __name__ == "__main__":
    main()
