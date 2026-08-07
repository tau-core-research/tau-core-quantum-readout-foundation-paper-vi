#!/usr/bin/env python3
"""Audit a mixed parent-boundary incidence as the future-to-ROOT bridge source."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "mixed_boundary_future_root_source_audit.json"


def joint_phase(lam: float) -> np.ndarray:
    j2 = np.array([[0.0, -1.0], [1.0, 0.0]])
    j4 = np.block([[j2, np.zeros((2, 2))], [np.zeros((2, 2)), j2]])
    cross = lam * np.eye(4)
    return np.block([[j4, cross], [-cross.T, j4]])


def main() -> None:
    lam = 0.5
    omega_zero = joint_phase(0.0)
    omega_mixed = joint_phase(lam)
    bridge = omega_mixed[:4, 4:]

    # The diagonal restrictions are identical: the current separate future and
    # ROOT packets cannot distinguish the zero and occupied mixed incidences.
    same_diagonal_reduct = bool(
        np.allclose(omega_zero[:4, :4], omega_mixed[:4, :4])
        and np.allclose(omega_zero[4:, 4:], omega_mixed[4:, 4:])
    )

    result = {
        "schema_version": "1.0",
        "status": "CONDITIONAL_MIXED_BOUNDARY_BRIDGE_SOURCE",
        "source_construction": {
            "parent_boundary_role": (
                "the mixed future-fibre/ROOT block of the antisymmetrized boundary "
                "second variation"
            ),
            "mixed_incidence_lambda": lam,
            "joint_phase_antisymmetric": bool(np.allclose(omega_mixed.T, -omega_mixed)),
            "joint_phase_nondegenerate": bool(abs(np.linalg.det(omega_mixed)) > 1e-12),
            "bridge_rank": int(np.linalg.matrix_rank(bridge)),
        },
        "schur_transfer": {
            "premise": (
                "future and ROOT carriers are equivalent irreducible parent modules and the "
                "mixed boundary block is a nonzero equivariant intertwiner"
            ),
            "kernel_and_image_are_invariant": True,
            "nonzero_intertwiner_is_isomorphism": True,
            "separate_bijectivity_assumption_needed": False,
        },
        "equal_reduct_counterpair": {
            "same_diagonal_future_and_ROOT_phase_packets": same_diagonal_reduct,
            "zero_member_bridge_rank": int(np.linalg.matrix_rank(omega_zero[:4, 4:])),
            "occupied_member_bridge_rank": int(np.linalg.matrix_rank(bridge)),
            "common_parent_action_alone_selects_nonzero_mixed_block": False,
        },
        "claim_boundary": {
            "proved_conditionally": (
                "one nonzero equivariant mixed boundary incidence generates the full-rank "
                "future-to-ROOT bridge"
            ),
            "not_proved": (
                "the physical base-seed boundary action has a nonzero mixed incidence; "
                "the diagonal common-action packet permits lambda=0"
            ),
        },
        "verdict": "BRIDGE_REDUCED_TO_ONE_NONZERO_MIXED_BOUNDARY_INCIDENCE; CURRENT_DIAGONAL_PACKET_DOES_NOT_ACTIVATE_IT",
    }

    src = result["source_construction"]
    assert src["joint_phase_antisymmetric"] is True
    assert src["joint_phase_nondegenerate"] is True
    assert src["bridge_rank"] == 4
    assert result["equal_reduct_counterpair"]["same_diagonal_future_and_ROOT_phase_packets"] is True
    assert result["equal_reduct_counterpair"]["zero_member_bridge_rank"] == 0
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
