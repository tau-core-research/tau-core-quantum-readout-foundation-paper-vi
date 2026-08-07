#!/usr/bin/env python3
"""Finite audit of public calorimetric and mechanical source-port candidates."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/public_source_port_candidate_audit.json"


rows = [
    {
        "id": "gunyho2024_thermal_qubit_readout",
        "same_carrier": True,
        "public_raw_packet": True,
        "source_port_record": "bolometer voltage from absorbed resonator readout power",
        "independent_after_state_and_controls": False,
        "endpoint_quantum_geometry": False,
        "body_action_map": False,
        "verdict": "thermal state-readout terminal, not independent body action",
    },
    {
        "id": "vanner2013_pulsed_optomechanical_tomography",
        "same_carrier": True,
        "public_raw_packet": False,
        "source_port_record": "calibrated pulsed position and radiation-pressure preparation",
        "independent_after_state_and_controls": False,
        "endpoint_quantum_geometry": False,
        "body_action_map": False,
        "verdict": "mechanical phase-space reconstruction without joint body-action/Uhlmann endpoint",
    },
    {
        "id": "ockeloen_korppi2016_collective_mechanical_bae",
        "same_carrier": True,
        "public_raw_packet": False,
        "source_port_record": "collective quadrature tomography and force-sensing capability",
        "independent_after_state_and_controls": False,
        "endpoint_quantum_geometry": False,
        "body_action_map": False,
        "verdict": "capability demonstration, not a joint applied-force/body-action record",
    },
]

result = {
    "schema_version": "1.0",
    "audit_is_finite": True,
    "candidate_count": len(rows),
    "rows": rows,
    "public_raw_packet_count": sum(row["public_raw_packet"] for row in rows),
    "independent_source_port_axis_count": sum(
        row["independent_after_state_and_controls"] for row in rows
    ),
    "tau_endpoint_eligible_count": sum(
        row["independent_after_state_and_controls"]
        and row["endpoint_quantum_geometry"]
        and row["body_action_map"]
        for row in rows
    ),
    "decision": (
        "No located public packet combines a conditionally independent calorimetric or mechanical "
        "source-port axis, same-carrier endpoint quantum geometry, and a frozen map to the once-counted "
        "body action. Public-data-only Tau scoring is therefore closed for the present candidate class."
    ),
    "next_action": (
        "Do not broaden the candidate census. Retain QVI-BWORKT1 as a future experimental protocol, "
        "or derive the body-action bridge internally from the common source law."
    ),
    "status": "PUBLIC_SOURCE_PORT_CLASS_CLOSED_NO_ELIGIBLE_PACKET",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)

