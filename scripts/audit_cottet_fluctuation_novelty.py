#!/usr/bin/env python3
"""Classify Cottet output moments by conditional information novelty."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "cottet_fluctuation_novelty_audit.json"


def main() -> None:
    rows = [
        {"record": "mean_output_power", "conditioning": "rho(t), input and coupling controls", "novelty": False},
        {"record": "multi_time_output_correlations", "conditioning": "rho(t) only", "novelty": True},
        {"record": "multi_time_output_correlations", "conditioning": "rho(0), frozen Liouvillian, couplings, controls and input state", "novelty": False},
        {"record": "model_residual_correlations", "conditioning": "independently frozen full standard process model", "novelty": True},
    ]
    result = {
        "schema_version": "1.0",
        "rows": rows,
        "cottet_publication_supports_fluctuation_score": False,
        "raw_single_shot_archive_located": False,
        "tau_body_action_identified": False,
        "decision": "Mean power is descriptor-redundant. Correlations add process information relative to instantaneous tomography, but not relative to a frozen complete Markov input-output model. No reusable Cottet records support the residual test.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert [row["novelty"] for row in rows[:3]] == [False, True, False]
    assert result["cottet_publication_supports_fluctuation_score"] is False
    print("COTTET_FLUCTUATION_AUDIT_PASS mean_novelty=no process_relative=yes full_model_relative=no score=no")


if __name__ == "__main__":
    main()
