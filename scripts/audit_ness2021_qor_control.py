#!/usr/bin/env python3
"""Audit the public Ness et al. Figure 2 data against standard QSL curves."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/public_qgt/ness2021_figure2"
OUT = ROOT / "data/derived/ness2021_qor_control_audit.json"
SERIES = ("a_0_04", "b_0_08", "c_0_16")


def read_table(path: Path) -> np.ndarray:
    return np.genfromtxt(path, names=True, delimiter="\t", dtype=float)


def interpolate(table: np.ndarray, name: str, time: np.ndarray) -> np.ndarray:
    return np.interp(time, table["time"], table[name])


def audit_series(name: str) -> dict:
    measured = read_table(DATA / f"{name}_measuredData.dat")
    fitted = read_table(DATA / f"{name}_fittedCurves.dat")
    time = measured["time"]

    mt = interpolate(fitted, "MTlimit", time)
    ml = interpolate(fitted, "MLlimit", time)
    mt_high = interpolate(fitted, "MTlimitHigh", time)
    ml_high = interpolate(fitted, "MLlimitHigh", time)
    use_mt = mt >= ml
    lower_bound = np.where(use_mt, mt, ml)
    lower_bound_high = np.where(use_mt, mt_high, ml_high)

    overlap = measured["overlap"]
    overlap_low = measured["overlapLow"]
    sigma_measured_low = np.maximum(overlap - overlap_low, 0.0)
    sigma_bound_high = np.maximum(lower_bound_high - lower_bound, 0.0)
    sigma_combined = np.hypot(sigma_measured_low, sigma_bound_high)
    z_violation = np.divide(
        lower_bound - overlap,
        sigma_combined,
        out=np.zeros_like(overlap),
        where=sigma_combined > 0,
    )

    return {
        "points": int(len(time)),
        "central_below_bound": int(np.sum(overlap < lower_bound)),
        "max_one_sided_violation_z": float(np.max(z_violation)),
        "violations_above_1_96_sigma": int(np.sum(z_violation > 1.96)),
        "violations_above_3_sigma": int(np.sum(z_violation > 3.0)),
        "minimum_central_margin": float(np.min(overlap - lower_bound)),
        "bound_selection": {
            "MT_points": int(np.sum(use_mt)),
            "ML_points": int(np.sum(~use_mt)),
        },
    }


def main() -> None:
    series = {name: audit_series(name) for name in SERIES}
    result = {
        "source": "Ness et al. 2021, Science Advances 7, eabj9119, Figure 2 Data S1",
        "test": "measured overlap is not significantly below max(MT, ML) lower bound",
        "uncertainty_rule": (
            "one-sided quadrature of measured lower interval and selected-bound upper interval"
        ),
        "series": series,
        "total_points": sum(item["points"] for item in series.values()),
        "max_one_sided_violation_z": max(
            item["max_one_sided_violation_z"] for item in series.values()
        ),
        "standard_QSL_consistent_at_1_96_sigma": all(
            item["violations_above_1_96_sigma"] == 0 for item in series.values()
        ),
        "tau_identifiability": {
            "independent_x_Q_available": True,
            "independent_x_A_available": False,
            "tests_x_A_equals_x_Q": False,
        },
        "claim_boundary": (
            "Standard QSL control only; consistency cannot validate the Tau connector."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["total_points"] == 53
    assert result["standard_QSL_consistent_at_1_96_sigma"]
    assert not result["tau_identifiability"]["tests_x_A_equals_x_Q"]
    print(
        "NESS2021_QOR_CONTROL_PASS",
        f"points={result['total_points']}",
        f"max_z={result['max_one_sided_violation_z']:.6f}",
    )


if __name__ == "__main__":
    main()

