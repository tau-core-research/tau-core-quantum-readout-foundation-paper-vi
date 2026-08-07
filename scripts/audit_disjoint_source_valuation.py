#!/usr/bin/env python3
"""Finite audit of the disjoint-source valuation selector."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parents[1] / "data" / "derived"
STEM = "tau_core_disjoint_source_valuation_isolation_audit_v01"


def quadratic_action(z: np.ndarray, h: np.ndarray) -> float:
    return float(0.5 * z @ h @ z)


def main() -> None:
    h_l = np.array([[2.0, -0.5], [-0.5, 2.0]])
    h_g = np.array([[3.0, -0.25], [-0.25, 3.0]])
    zero = np.zeros((2, 2))
    h_val = np.block([[h_l, zero], [zero, h_g]])

    # Positive and internally symmetric, but not component-additive.
    epsilon = 0.2
    cross = epsilon * np.ones((2, 2))
    h_counter = np.block([[h_l, cross], [cross.T, h_g]])

    z_l = np.array([0.4, -0.1])
    z_g = np.array([0.2, 0.3])
    z = np.concatenate((z_l, z_g))
    z_l_full = np.concatenate((z_l, np.zeros(2)))
    z_g_full = np.concatenate((np.zeros(2), z_g))

    val_defect = quadratic_action(z, h_val) - (
        quadratic_action(z_l_full, h_val)
        + quadratic_action(z_g_full, h_val)
    )
    counter_defect = quadratic_action(z, h_counter) - (
        quadratic_action(z_l_full, h_counter)
        + quadratic_action(z_g_full, h_counter)
    )

    p_l = np.diag([1.0, 1.0, 0.0, 0.0])
    p_g = np.eye(4) - p_l
    mixed_val = p_l @ h_val @ p_g
    mixed_counter = p_l @ h_counter @ p_g

    checks = {
        "valuation_hessian_positive": bool(np.linalg.eigvalsh(h_val).min() > 0),
        "countermodel_hessian_positive": bool(
            np.linalg.eigvalsh(h_counter).min() > 0
        ),
        "valuation_action_adds_on_disjoint_components": bool(
            abs(val_defect) < 1e-12
        ),
        "valuation_mixed_hessian_zero": bool(
            np.linalg.norm(mixed_val) < 1e-12
        ),
        "countermodel_preserves_internal_component_symmetry": bool(
            np.allclose(cross, cross[::-1, :])
            and np.allclose(cross, cross[:, ::-1])
        ),
        "countermodel_violates_disjoint_additivity": bool(
            abs(counter_defect) > 1e-8
        ),
        "countermodel_has_nonzero_mixed_hessian": bool(
            np.linalg.norm(mixed_counter) > 1e-8
        ),
        "cross_defect_matches_bilinear_term": bool(
            abs(counter_defect - z_l @ cross @ z_g) < 1e-12
        ),
    }
    if not all(checks.values()):
        failed = [name for name, value in checks.items() if not value]
        raise AssertionError(f"failed checks: {failed}")

    payload = {
        "verdict": "DISJOINT_SOURCE_VALUATION_FORCES_ACTION_ADDITIVITY_AND_ZERO_MIXED_HESSIAN;_RECOVERY_NEEDS_ADDITIONAL_GLOBAL_FACTORIZATION",
        "checks": checks,
        "valuation_defect": val_defect,
        "countermodel_defect": counter_defect,
        "minimum_eigenvalue_valuation": float(np.linalg.eigvalsh(h_val).min()),
        "minimum_eigenvalue_countermodel": float(
            np.linalg.eigvalsh(h_counter).min()
        ),
        "claim_boundary": (
            "Finite representation and non-entailment audit. It proves the "
            "action and Hessian consequences of disjoint-source valuation and "
            "shows that weaker once-counting, positivity and symmetry "
            "assumptions do not select it. A zero mixed Hessian alone does not "
            "prove factorization of loads, generators, occupied states or "
            "exact quantum recovery. It does not prove that Nature realizes "
            "the valuation law."
        ),
    }
    (HERE / f"{STEM}_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    report = [
        "# Tau Core disjoint-source valuation isolation audit v0.1",
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
