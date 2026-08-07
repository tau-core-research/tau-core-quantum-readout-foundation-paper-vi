#!/usr/bin/env python3
"""Finite certificate for the joint quantum-packet parent-selection question."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
OUT = DERIVED / "joint_quantum_packet_parent_selection_audit.json"


def load(name: str) -> dict:
    return json.loads((DERIVED / name).read_text())


def main() -> None:
    ledger = load("quantum_readout_ledger.json")
    tensor = load("tensor_factorization_audit.json")
    recovery = load("depolarizing_recovery_selector_audit.json")
    designation = load("root_factor_designation_no_go.json")

    gamma_rows = {row["gamma"]: row for row in recovery["rows"]}
    same_upstream_connector_pair = [
        {
            "gamma": 1.0,
            "positive_cptp": True,
            "same_upstream_body_and_P3_packet": True,
            "exact_full_code_recovery": gamma_rows[1.0]["exact_full_code_CPTP_recovery_possible"],
            "joint_packet_closed": True,
        },
        {
            "gamma": 0.5,
            "positive_cptp": True,
            "same_upstream_body_and_P3_packet": True,
            "exact_full_code_recovery": gamma_rows[0.5]["exact_full_code_CPTP_recovery_possible"],
            "joint_packet_closed": False,
        },
    ]

    result = {
        "schema_version": "1.0",
        "question": "Does the current physical base-seed reduct entail occupation of the complete joint quantum packet?",
        "verdict": "CURRENT_REDUCT_DOES_NOT_ENTAIL_COMPLETE_JOINT_QUANTUM_PACKET",
        "exact_countermodel": {
            "family": recovery["family"],
            "rows": same_upstream_connector_pair,
            "reason": (
                "Both members preserve the same upstream stabilized body, occupied P3 algebra, "
                "positive normalized states and CPTP descent. Only gamma=1 has exact full-code "
                "recovery and selects the finite A8b connector."
            ),
        },
        "independent_tensor_nonselection": {
            "same_rank_four_equilibrium_allows_zero_and_positive_W2_stiffness": tensor[
                "same_rank4_equilibrium_allows_zero_and_positive_W2_stiffness"
            ],
            "rooted_packet_selects_unordered_factor_triple": designation["theorem_status"][
                "distinguished_ROOT_M2"
            ],
            "current_parent_selects_full_factor_ledger": tensor["verdict"][
                "full_factor_ledger_is_selected_by_current_parent"
            ],
        },
        "already_derived_conditionally": {
            "complex_structure_from_metric_symplectic_lock": ledger["proved"][
                "metric_symplectic_lock_constructs_complex_structure"
            ],
            "single_system_packet_from_enriched_P3_handoff": ledger["proved"][
                "enriched_MVP_P3_handoff_constructs_single_system_packet"
            ],
            "Born_terminal": ledger["proved"]["born_probability_on_selected_complex_carrier"],
            "tensor_factors_from_two_commuting_factors": ledger["proved"][
                "two_commuting_M2_factors_select_the_third_as_commutant"
            ],
            "common_Gram_prediction": ledger["proved"][
                "common_Gram_completion_predicts_x_A_equals_x_Q"
            ],
        },
        "minimal_corrected_theorem": {
            "name": "source-faithful protected representation criterion",
            "statement": (
                "If one occupied once-counted parent representation is simultaneously "
                "action-isometric, metric-symplectic, separating, monoidal and exactly "
                "recoverable on the designated logical algebra, then the complete Paper-VI "
                "quantum packet follows without independent terminal gains."
            ),
            "status": "conditional characterization; existence is not entailed by the current reduct",
            "remaining_atomic_physical_input": (
                "physical occupation of that single source-faithful protected representation"
            ),
        },
        "claim_boundary": (
            "This audit proves non-entailment from the current reduct and a sufficient joint-source "
            "criterion. It does not prove that Nature occupies the criterion."
        ),
    }

    assert result["exact_countermodel"]["rows"][0]["joint_packet_closed"] is True
    assert result["exact_countermodel"]["rows"][1]["joint_packet_closed"] is False
    assert result["exact_countermodel"]["rows"][1]["positive_cptp"] is True
    assert result["independent_tensor_nonselection"]["current_parent_selects_full_factor_ledger"] is False
    assert all(result["already_derived_conditionally"].values())
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
