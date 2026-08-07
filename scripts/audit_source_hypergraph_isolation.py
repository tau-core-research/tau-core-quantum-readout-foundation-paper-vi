#!/usr/bin/env python3
"""Audit hypergraph isolation as a source law for quantum information protection."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parents[1] / "data" / "derived"
STEM = "tau_core_hypergraph_isolation_quantum_protection_audit_v01"
TOL = 1.0e-10


def partial_trace_system(rho: np.ndarray) -> np.ndarray:
    return np.trace(rho.reshape(2, 2, 2, 2), axis1=1, axis2=3)


def partial_trace_environment(rho: np.ndarray) -> np.ndarray:
    return np.trace(rho.reshape(2, 2, 2, 2), axis1=0, axis2=2)


def main() -> None:
    # A local additive parent action on disconnected logical/complement
    # hypergraph components has no mixed second variation.
    h_l = np.asarray(((3.0, 0.4), (0.4, 2.0)))
    h_g = np.asarray(((1.5, -0.2), (-0.2, 1.2)))
    h_iso = np.block([[h_l, np.zeros((2, 2))], [np.zeros((2, 2)), h_g]])
    mixed_iso = h_iso[:2, 2:]

    epsilon = 0.3
    cross = epsilon * np.asarray(((1.0, 0.0), (0.0, -1.0)))
    h_int = np.block([[h_l, cross], [cross.T, h_g]])

    # Isolated occupied realization V|psi>=|psi>|0> has exact observer
    # recovery and a state-independent inaccessible complement.
    zero = np.asarray((1.0, 0.0), dtype=complex)
    plus = np.asarray((1.0, 1.0), dtype=complex) / np.sqrt(2.0)
    one = np.asarray((0.0, 1.0), dtype=complex)
    states = (zero, one, plus)
    recovered = []
    complements = []
    for psi in states:
        joint = np.kron(psi, zero)
        rho_joint = np.outer(joint, joint.conj())
        recovered.append(partial_trace_system(rho_joint))
        complements.append(partial_trace_environment(rho_joint))

    # A crossing interaction (CNOT to the complement) exports logical
    # information and dephases the system for a coherent input.
    cnot = np.asarray(
        ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0)),
        dtype=complex,
    )
    joint_plus = np.kron(plus, zero)
    rho_after = cnot @ np.outer(joint_plus, joint_plus.conj()) @ cnot.conj().T
    system_after = partial_trace_system(rho_after)
    env_after = partial_trace_environment(rho_after)
    rho_plus = np.outer(plus, plus.conj())

    checks = {
        "disconnected_local_action_is_block_diagonal": np.linalg.norm(mixed_iso) < TOL,
        "isolated_hessian_is_positive": np.min(np.linalg.eigvalsh(h_iso)) > TOL,
        "crossing_hyperedge_creates_mixed_hessian": np.linalg.norm(h_int[:2, 2:]) > TOL,
        "isolated_descent_recovers_every_test_state": all(
            np.allclose(out, np.outer(psi, psi.conj()), atol=TOL)
            for out, psi in zip(recovered, states)
        ),
        "isolated_complement_is_state_independent": all(
            np.allclose(out, complements[0], atol=TOL) for out in complements[1:]
        ),
        "crossing_interaction_exports_information": not np.allclose(env_after, complements[0], atol=TOL),
        "crossing_interaction_dephases_coherence": not np.allclose(system_after, rho_plus, atol=TOL),
        "interaction_control_preserves_total_trace": abs(np.trace(rho_after) - 1.0) < TOL,
        "interaction_control_preserves_global_purity": abs(np.trace(rho_after @ rho_after) - 1.0) < TOL,
    }
    checks = {k: bool(v) for k, v in checks.items()}
    result = {
        "schema": STEM,
        "checks": checks,
        "metrics": {
            "isolated_mixed_hessian_norm": float(np.linalg.norm(mixed_iso)),
            "interacting_mixed_hessian_norm": float(np.linalg.norm(h_int[:2, 2:])),
            "isolated_recovery_error": float(max(np.linalg.norm(out - np.outer(psi, psi.conj())) for out, psi in zip(recovered, states))),
            "interaction_coherence_loss": float(np.linalg.norm(system_after - rho_plus)),
        },
        "theorem": (
            "Disjoint action valuation forces action additivity and a zero mixed "
            "Hessian. If the source load, global generator and occupied state also "
            "factor across the same components, the inaccessible complement is "
            "logical-state independent and observer descent has an exact CPTP "
            "left inverse. The latter factors are additional global premises, not "
            "consequences of the Hessian calculation alone."
        ),
        "interaction_law": (
            "A source-owned hyperedge crossing the partition creates the mixed "
            "Hessian and permits logical information to enter the complement. Local "
            "decoherence is then allowed while the complete joint state remains "
            "normalized and pure/unitary."
        ),
        "verdict": "FULL_SOURCE_HYPERGRAPH_FACTORIZATION_IMPLIES_QUANTUM_PROTECTION;_ACTION_VALUATION_ALONE_IMPLIES_ONLY_ZERO_MIXED_HESSIAN",
        "claim_boundary": (
            "This verifies the full-factorization-to-recovery implication and the "
            "weaker valuation-to-Hessian implication separately. It does not derive "
            "global factorization from a local Hessian, prove exact isolation for "
            "every real apparatus, rule out weak residual couplings, derive a "
            "decoherence rate, measurement outcome or absolute hbar."
        ),
    }
    if not all(checks.values()):
        raise AssertionError([k for k, v in checks.items() if not v])
    (HERE / f"{STEM}_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    report = ["# Tau Core hypergraph-isolation quantum-protection audit v0.1", "", f"**Verdict:** `{result['verdict']}`", "", "## Checks", "", *[f"- [x] `{k}`" for k in checks], "", "## Theorem", "", result["theorem"], "", "## Interaction boundary", "", result["interaction_law"], "", "## Claim boundary", "", result["claim_boundary"], ""]
    (HERE / f"{STEM}_report.md").write_text("\n".join(report))
    print(result["verdict"])


if __name__ == "__main__":
    main()
