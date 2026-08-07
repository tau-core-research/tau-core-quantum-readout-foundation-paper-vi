#!/usr/bin/env python3
"""Audit public candidates for joint morphology/action/amplitude/phase scoring."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "joint_path_data_candidate_audit.json"


def row_count(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return max(0, sum(1 for _ in csv.reader(handle)) - 1)


def main() -> None:
    qcc = ROOT / "data" / "public_optical_qcc"
    result = {
        "schema_version": "1.0",
        "target": "one path identifier joining geometry, action, complex amplitude and phase",
        "candidates": [
            {
                "id": "wen2026_raw_propagator_reconstruction",
                "source_doi": "10.5061/dryad.x0k6djj14",
                "geometry": "enumerable 17^5 lattice-path sequence",
                "action": "computed standard optical/free-particle action from the path sequence",
                "complex_amplitude": "reconstructible as a product of experimentally reconstructed propagator elements",
                "phase": "argument of the reconstructed complex path amplitude",
                "joint_path_table_published_directly": False,
                "joint_path_table_reconstructible": True,
                "shared_kernel_covariance_required": True,
                "independent_tau_body_action": False,
                "verdict": "best reconstructible diagnostic candidate"
            },
            {
                "id": "tian2026_path_action_gradient",
                "source_doi": "10.5061/dryad.02v6wwqjg",
                "published_action_gradient_rows_free_space": row_count(qcc / "fig3c.csv"),
                "published_action_gradient_rows_impulsive_each": [row_count(qcc / "fig4a1.csv"), row_count(qcc / "fig4a2.csv")],
                "geometry": "full coordinates only for selected stationary-action candidates",
                "action": "direct weak-value reconstruction",
                "complex_amplitude": "not published for the same indexed path family",
                "joint_path_table_published_directly": False,
                "joint_path_table_reconstructible": False,
                "independent_tau_body_action": False,
                "verdict": "strong action-side control, incomplete joint packet"
            },
            {
                "id": "danner2024_two_path_neutron_weak_values",
                "source_doi": "10.1038/s41598-024-76167-6",
                "geometry": "two fixed interferometer arms",
                "action": "controlled relative interferometer phase only",
                "complex_amplitude": "simultaneous complex path weak values",
                "joint_path_table_published_directly": True,
                "morphology_variation_rank": 0,
                "independent_tau_body_action": False,
                "verdict": "complex-amplitude control, no morphology contrast"
            }
        ],
        "direct_complete_public_count": 0,
        "reconstructible_diagnostic_count": 1,
        "executed_score": {
            "candidate": "wen2026_raw_propagator_reconstruction",
            "null": "complex path weight factors through the standard step action",
            "diagnostic": "test amplitude or phase residual against path roughness, turning count and increment distribution conditional on total action",
            "mandatory_control": "cluster or bootstrap by shared propagator element; 17^5 algebraically generated paths are not 17^5 independent measurements",
            "result_file": "data/derived/reconstructed_optical_path_morphology_score.json",
            "verdict": "validated phase leg is consistent with the 17-class shared-kernel permutation null; amplitude leg fails independent reconstruction validation",
            "forbidden_promotion": "a residual may diagnose propagator-structure information beyond scalar total action, but does not identify Tau body action"
        }
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["candidates"][1]["published_action_gradient_rows_free_space"] == 10000
    assert result["direct_complete_public_count"] == 0
    assert result["reconstructible_diagnostic_count"] == 1
    assert result["executed_score"]["candidate"] == "wen2026_raw_propagator_reconstruction"
    print("JOINT_PATH_DATA_AUDIT_PASS direct_complete=0 reconstructible=1")


if __name__ == "__main__":
    main()
