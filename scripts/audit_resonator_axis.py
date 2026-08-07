#!/usr/bin/env python3
"""Finite audit of resonator/generalized-force candidates for the missing x_A axis."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "resonator_axis_census.json"
OUT = ROOT / "data" / "derived" / "resonator_axis_audit.json"


def main() -> None:
    packet = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for item in packet["candidates"]:
        independent = (
            item["independent_source_port_calibration"] is True
            and item["factors_through_quantum_state"] is False
        )
        tau_axis = independent and item["body_action_map_frozen"] is True
        rows.append(
            {
                "id": item["id"],
                "independent_measurement_axis": independent,
                "independent_xA_axis": tau_axis,
            }
        )

    result = {
        "schema_version": "1.0",
        "candidate_count": len(rows),
        "independent_measurement_axis_count": sum(
            row["independent_measurement_axis"] for row in rows
        ),
        "independent_xA_axis_count": sum(row["independent_xA_axis"] for row in rows),
        "rows": rows,
        "factorization_no_go": (
            "If R_res=F(rho,c) for frozen controls c, then R_res adds no conditional "
            "information or stacked-Jacobian rank beyond rho and cannot independently "
            "identify x_A."
        ),
        "positive_reopening_condition": (
            "Measure a separately calibrated source-port force, admittance, impedance, "
            "or calorimetric backaction whose conditional response does not factor through "
            "rho/QGT, then freeze its map to the once-counted body action before tomography."
        ),
        "decision": "No audited resonator/generalized-force candidate supplies the missing independent body-action axis."
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["candidate_count"] == 7
    assert result["independent_measurement_axis_count"] == 1
    assert result["independent_xA_axis_count"] == 0
    print("RESONATOR_AXIS_AUDIT_PASS candidates=7 independent_measurement=1 independent_xA=0")


if __name__ == "__main__":
    main()
