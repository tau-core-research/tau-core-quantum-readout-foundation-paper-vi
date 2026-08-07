#!/usr/bin/env python3
"""Apply the frozen public-process scoring gate to located data candidates."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/public_qgt/public_single_shot_candidate_audit.json"
OUT = ROOT / "data/derived/public_single_shot_candidate_scoring.json"
FIELDS = ["public_direct_download", "single_shot_records", "time_resolved_records", "independent_endpoint_labels", "frozen_process_model", "second_nonfactorizing_readout"]

def main() -> None:
    data = json.loads(SRC.read_text())
    rows = []
    for item in data["candidates"]:
        rows.append({"id": item["id"], "score": sum(bool(item[k]) for k in FIELDS), "maximum": 6, "process_residual_eligible": all(bool(item[k]) for k in FIELDS)})
    wang = next(x for x in data["candidates"] if x["id"] == "wang2025_longitudinal_readout")
    result = {"schema_version": "1.0", "rows": rows, "eligible_count": sum(r["process_residual_eligible"] for r in rows), "wang_readout_control": {"minimum_midpoint_accuracy": min(wang["midpoint_accuracy"]), "maximum_midpoint_accuracy": max(wang["midpoint_accuracy"]), "minimum_d_prime": min(wang["d_prime"])}, "tau_score_eligible": False, "decision": "Zero directly public packets pass the process-residual gate. Wang is a strong single-shot readout control; Ficheux is the strongest architecture but lacks directly public raw records."}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["eligible_count"] == 0
    assert next(r for r in rows if r["id"] == "wang2025_longitudinal_readout")["score"] == 3
    assert result["wang_readout_control"]["minimum_midpoint_accuracy"] > 0.995
    print("PUBLIC_SINGLE_SHOT_CANDIDATE_AUDIT_PASS candidates=3 eligible=0 wang_control=yes tau_score=no")

if __name__ == "__main__":
    main()
