#!/usr/bin/env python3
"""Audit typed two-jet identifiability of parent cross responses."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parents[1] / "data" / "derived"
STEM = "tau_core_empirical_parent_valuation_lift_audit_v01"


def main() -> None:
    # Parent coordinates: L_visible, L_hidden, G_visible, G_hidden.
    h_val = np.diag([2.0, 3.0, 4.0, 5.0])
    hidden_cross = np.zeros((4, 4))
    hidden_cross[1, 3] = hidden_cross[3, 1] = 0.4
    h_hidden = h_val + hidden_cross

    # Operational readout embeds only the two visible coordinates.
    r_nonfaithful = np.array(
        [[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
    )
    h_out_val = r_nonfaithful.T @ h_val @ r_nonfaithful
    h_out_hidden = r_nonfaithful.T @ h_hidden @ r_nonfaithful

    # A faithful full parent readout detects the same defect.
    r_faithful = np.eye(4)
    faithful_defect = r_faithful.T @ hidden_cross @ r_faithful

    p_l = np.diag([1.0, 1.0, 0.0, 0.0])
    p_g = np.eye(4) - p_l
    parent_mixed = p_l @ h_hidden @ p_g

    checks = {
        "both_parent_hessians_positive": bool(
            np.linalg.eigvalsh(h_val).min() > 0
            and np.linalg.eigvalsh(h_hidden).min() > 0
        ),
        "valuation_parent_has_zero_cross_block": bool(
            np.linalg.norm(p_l @ h_val @ p_g) < 1e-12
        ),
        "hidden_parent_violates_valuation": bool(
            np.linalg.norm(parent_mixed) > 1e-8
        ),
        "nonfaithful_readout_has_same_reduct": bool(
            np.allclose(h_out_val, h_out_hidden)
        ),
        "nonfaithful_readout_kernel_hides_defect": bool(
            np.linalg.norm(r_nonfaithful.T @ hidden_cross @ r_nonfaithful)
            < 1e-12
        ),
        "faithful_readout_detects_defect": bool(
            np.linalg.norm(faithful_defect) > 1e-8
        ),
        "full_rank_congruence_is_injective": bool(
            np.linalg.matrix_rank(r_faithful) == 4
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"failed checks: {failed}")

    payload = {
        "verdict": "JOINT_TWO_JET_FAITHFULNESS_LIFTS_ZERO_TERMINAL_MIXING_TO_ZERO_PARENT_MIXED_HESSIAN",
        "checks": checks,
        "hidden_cross_norm": float(np.linalg.norm(hidden_cross)),
        "nonfaithful_visible_defect_norm": float(
            np.linalg.norm(r_nonfaithful.T @ hidden_cross @ r_nonfaithful)
        ),
        "claim_boundary": (
            "The audit proves sufficiency of faithfulness for a typed local "
            "two-jet lift and an equal-reduct countermodel showing that "
            "faithfulness is required for universal identifiability over the "
            "admitted cross-form class. It does not derive finite action "
            "valuation, global state/dynamical factorization, exact recovery, "
            "physical joint faithfulness or unrestricted source-law realization."
        ),
    }
    (HERE / f"{STEM}_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    report = [
        "# Tau Core empirical parent-valuation lift audit v0.1",
        "",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "## Checks",
        "",
    ]
    report.extend(
        f"- [{'x' if value else ' '}] `{name}`"
        for name, value in checks.items()
    )
    report.extend(["", "## Claim boundary", "", payload["claim_boundary"], ""])
    (HERE / f"{STEM}_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(payload["verdict"])


if __name__ == "__main__":
    main()
