#!/usr/bin/env python3
"""Audit the public same-carrier QGT evidence used by Paper VI."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "public_qgt"
OUT = ROOT / "data" / "derived" / "public_qgt_evidence_audit.json"


def read_csv(name: str) -> list[dict[str, float | str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({
                key: value if key == "component" else float(value)
                for key, value in row.items()
            })
        return rows


def moments(xs: list[float], ys: list[float]) -> dict[str, float]:
    residuals = [y - x for x, y in zip(xs, ys)]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    corr = cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else math.nan
    return {
        "n": len(xs),
        "mae": sum(abs(r) for r in residuals) / len(residuals),
        "rmse": math.sqrt(sum(r * r for r in residuals) / len(residuals)),
        "bias_second_minus_first": sum(residuals) / len(residuals),
        "pearson_r": corr,
    }


def main() -> None:
    tan = read_csv("tan2019_qgt_points.csv")
    phi = [row for row in tan if row["component"] == "phi"]
    theta = [row for row in tan if row["component"] == "theta"]
    yu = read_csv("yu2018_nv_qgt_points.csv")
    yu_interior = [row for row in yu if float(row["q_theta_over_pi"]) > 0]

    result = {
        "schema_version": "1.0",
        "public_sources": {
            "tan2019_superconducting_qubit": moments(
                [float(row["quench_metric"]) for row in phi],
                [float(row["drive_metric"]) for row in phi],
            ),
            "tan2019_theta_normalization": moments(
                [float(row["quench_metric"]) for row in theta],
                [float(row["drive_metric"]) for row in theta],
            ),
            "yu2018_nv_center_qgt_identity": moments(
                [float(row["metric_prediction"]) for row in yu_interior],
                [float(row["berry"]) for row in yu_interior],
            ),
        },
        "identifiability": {
            "same_carrier_local_quantum_geometry_replicated": True,
            "finite_Uhlmann_endpoint_distance_available": False,
            "independent_morphological_action_x_A_available": False,
            "public_data_can_test_x_A_equals_x_Q": False,
            "reason": (
                "All reconstructed axes are standard quantum-geometric terminals; "
                "none is an independently measured once-counted morphological action."
            ),
        },
        "verdict": (
            "Public data support the standard local quantum-geometry recovery and "
            "a same-carrier connector proxy, but do not identify or test the "
            "Tau-specific finite x_A=x_Q relation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["public_sources"]["tan2019_superconducting_qubit"]["pearson_r"] > 0.98
    assert result["public_sources"]["yu2018_nv_center_qgt_identity"]["pearson_r"] > 0.99
    assert not result["identifiability"]["public_data_can_test_x_A_equals_x_Q"]
    print("PUBLIC_QGT_EVIDENCE_PASS local_geometry=yes finite_tau_test=no")


if __name__ == "__main__":
    main()
