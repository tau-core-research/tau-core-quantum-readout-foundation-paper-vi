#!/usr/bin/env python3
"""Audit the isolated logical non-leakage selector and classical control."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "isolated_logical_nonleakage_selector_audit.json"


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    singular = np.linalg.svd(rho - sigma, compute_uv=False)
    return float(0.5 * np.sum(singular))


def dephase(rho: np.ndarray) -> np.ndarray:
    return np.diag(np.diag(rho))


def main() -> None:
    zero = np.array([1.0, 0.0], dtype=complex)
    one = np.array([0.0, 1.0], dtype=complex)
    plus = (zero + one) / np.sqrt(2.0)
    minus = (zero - one) / np.sqrt(2.0)
    state = lambda vector: np.outer(vector, vector.conj())

    rho_zero, rho_one = state(zero), state(one)
    rho_plus, rho_minus = state(plus), state(minus)

    pointer_in = trace_distance(rho_zero, rho_one)
    pointer_out = trace_distance(dephase(rho_zero), dephase(rho_one))
    phase_in = trace_distance(rho_plus, rho_minus)
    phase_out = trace_distance(dephase(rho_plus), dephase(rho_minus))

    result = {
        "schema_version": "1.0",
        "selector": "isolated logical non-leakage on the complete occupied operator system",
        "finite_control": {
            "pointer_pair_trace_distance_before": pointer_in,
            "pointer_pair_trace_distance_after_dephasing": pointer_out,
            "phase_pair_trace_distance_before": phase_in,
            "phase_pair_trace_distance_after_dephasing": phase_out,
            "classical_repeatability_survives": bool(np.isclose(pointer_out, pointer_in)),
            "full_coherent_distinguishability_survives": bool(np.isclose(phase_out, phase_in)),
        },
        "theorem": {
            "assumptions": [
                "C is CPTP on the complete occupied logical matrix algebra",
                "the complementary output is independent of every logical input",
                "the terminal has the same minimal logical dimension",
            ],
            "conclusion": (
                "C is reversible on the complete logical algebra; at equal minimal dimension "
                "it is unitary conjugation and has a CPTP inverse"
            ),
            "proof_route": (
                "constant complementary output implies correctability by the information-disturbance "
                "theorem; equal-dimensional reversible matrix-algebra channels are unitary"
            ),
        },
        "physical_interpretation": {
            "what_forces_recovery": (
                "an isolated parent relation must not export logical-state information into the "
                "observer-inaccessible realization complement"
            ),
            "what_does_not_force_recovery": (
                "stable observer existence, pointer repeatability, finite capacity or CPTP descent alone"
            ),
            "source_status": (
                "required by the observed isolated-system unitary quantum limit, but not yet derived "
                "from the current base-seed action alone"
            ),
        },
        "verdict": "ISOLATED_FULL_LOGICAL_NONLEAKAGE_SELECTS_EXACT_RECOVERY",
    }

    assert np.isclose(pointer_in, 1.0) and np.isclose(pointer_out, 1.0)
    assert np.isclose(phase_in, 1.0) and np.isclose(phase_out, 0.0)
    assert result["finite_control"]["classical_repeatability_survives"] is True
    assert result["finite_control"]["full_coherent_distinguishability_survives"] is False
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
