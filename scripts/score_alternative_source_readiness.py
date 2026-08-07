#!/usr/bin/env python3
"""Predeclared readiness score for alternative Paper-VI source packets."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "alternative_source_census.json"
OUT = ROOT / "data" / "derived" / "alternative_source_readiness_scoring.json"


def graded(value: object, full: int, partial: int = 1) -> int:
    if value is True or value == "yes":
        return full
    if isinstance(value, str) and value not in {"no", "figure-level"}:
        return partial
    return 0


def main() -> None:
    census = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for item in census["candidates"]:
        components = {
            "same_carrier": graded(item["physical_same_carrier"], 2),
            "direct_work": graded(item["direct_action_or_work_record"], 2),
            "endpoint_geometry": graded(item["endpoint_state_geometry"], 2),
            "loop_holonomy": graded(item["closed_loop_phase_or_holonomy"], 2),
            "independent_body_action_bridge": graded(item["independent_action_to_body_mapping"], 3),
            "public_reusable_data": 1 if item["public_numerical_data"] is True else 0,
            "errors_and_recovery": graded(item["errors_and_recovery"], 1),
        }
        score = sum(components.values())
        hard_pass = (
            components["same_carrier"] == 2
            and components["independent_body_action_bridge"] == 3
            and components["endpoint_geometry"] == 2
            and components["loop_holonomy"] == 2
        )
        rows.append(
            {
                "id": item["id"],
                "score": score,
                "maximum": 13,
                "components": components,
                "hard_tau_ready": hard_pass,
                "interpretation": "capability readiness only" if not hard_pass else "eligible for blind Tau scoring",
            }
        )
    rows.sort(key=lambda row: (-row["score"], row["id"]))
    result = {
        "schema_version": "1.0",
        "rubric_frozen_before_scoring": True,
        "score_is_tau_signal": False,
        "hard_gate_overrides_total": True,
        "ranking": rows,
        "tau_ready_count": sum(row["hard_tau_ready"] for row in rows),
        "decision": (
            "Zhao 2020 is the strongest integrated protocol architecture; Cottet 2017 and "
            "Viyuela 2018 are complementary work/tomography and holonomy legs. No candidate "
            "is eligible for Tau residual scoring because all lack the independent CHDF "
            "body-action bridge, and none supplies a complete reusable public packet."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert rows[0]["id"] == "zhao2020_xmon_geometric_gate"
    assert rows[0]["score"] == 8
    assert result["tau_ready_count"] == 0
    print("ALTERNATIVE_SOURCE_READINESS_SCORE_PASS top=zhao2020 score=8/13 tau_ready=0")


if __name__ == "__main__":
    main()
