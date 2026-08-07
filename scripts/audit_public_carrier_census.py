#!/usr/bin/env python3
"""Rank public carrier candidates without converting QGT data into x_A."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "public_qgt" / "carrier_census.json"
OUT = ROOT / "data" / "derived" / "public_carrier_census_audit.json"


def main() -> None:
    census = json.loads(SRC.read_text(encoding="utf-8"))
    ranked = []
    for item in census["candidates"]:
        binary = [
            item["same_carrier"],
            item["state_distance_xQ"],
            item["action_like_observable"],
            item["independent_once_counted_xA"],
            item["errors_and_recovery"] == "yes",
        ]
        score = sum(bool(value) for value in binary)
        full = all(binary)
        ranked.append({
            "id": item["id"],
            "gate_score": score,
            "full_finite_tau_test": full,
            "verdict": item["verdict"],
        })
    ranked.sort(key=lambda row: (-row["gate_score"], row["id"]))
    result = {
        "schema_version": "1.0",
        "candidate_count": len(ranked),
        "full_pass_count": sum(row["full_finite_tau_test"] for row in ranked),
        "ranked": ranked,
        "strongest_QOR_control": "ness2021_single_atom_qsl",
        "strongest_spectral_xA_candidate": "kim2025_black_phosphorus",
        "decision": (
            "No surveyed public dataset currently identifies x_A independently. "
            "Use Ness 2021 only as a QOR standard control and freeze a separate "
            "spectral-response map before any Kim 2025 endpoint calculation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["candidate_count"] == 8
    assert result["full_pass_count"] == 0
    assert ranked[0]["id"] == "ness2021_single_atom_qsl"
    print("PUBLIC_CARRIER_CENSUS_PASS candidates=8 full_tau_pass=0")


if __name__ == "__main__":
    main()
