#!/usr/bin/env python3
"""Audit alternative public sources for the finite Paper-VI discriminator."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "alternative_source_census.json"
OUT = ROOT / "data" / "derived" / "alternative_source_census_audit.json"


def strict_yes(value: object) -> bool:
    return value is True


def main() -> None:
    packet = json.loads(SRC.read_text(encoding="utf-8"))
    gates = packet["required_gates"]
    rows = []
    for candidate in packet["candidates"]:
        passed = {gate: strict_yes(candidate[gate]) for gate in gates}
        rows.append(
            {
                "id": candidate["id"],
                "strict_gate_score": sum(passed.values()),
                "full_same_carrier_pass": all(passed.values()),
                "missing_gates": [gate for gate, ok in passed.items() if not ok],
                "verdict": candidate["verdict"],
            }
        )
    rows.sort(key=lambda row: (-row["strict_gate_score"], row["id"]))
    result = {
        "schema_version": "1.0",
        "candidate_count": len(rows),
        "full_pass_count": sum(row["full_same_carrier_pass"] for row in rows),
        "ranked": rows,
        "strongest_work_tomography_leg": "cottet2017_maxwell_demon",
        "strongest_holonomy_leg": "viyuela2018_superconducting_uhlmann",
        "strongest_integrated_architecture": "zhao2020_xmon_geometric_gate",
        "strongest_trajectory_resolved_candidate": "naghiloo2020_quantum_trajectories",
        "decision": (
            "Alternative experimental source legs exist, but no located public experiment "
            "provides the complete source-frozen same-carrier action/state/holonomy packet. "
            "The finite reopening architecture is work interferometry plus endpoint tomography "
            "plus a closed Bargmann/Uhlmann loop on one carrier; thermodynamic work or imposed "
            "control-pulse area must not be renamed morphological action without an independent bridge."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["candidate_count"] == 6
    assert result["full_pass_count"] == 0
    assert rows[0]["strict_gate_score"] >= 3
    print("ALTERNATIVE_SOURCE_CENSUS_PASS candidates=6 full_pass=0")


if __name__ == "__main__":
    main()
