#!/usr/bin/env python3
"""Audit the independent Wen Fig. S2B radial phase control."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "public_optical_path_integral" / "FigS2B.xlsx"
OUT = ROOT / "data" / "derived" / "wen_figs2b_phase_control_audit.json"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def numeric_columns(path: Path) -> dict[str, list[float]]:
    columns = {name: [] for name in "ABCDE"}
    with zipfile.ZipFile(path) as archive:
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    for row in sheet.findall(f".//{NS}row")[1:]:
        for cell in row.findall(f"{NS}c"):
            value = cell.find(f"{NS}v")
            if value is not None:
                columns[cell.attrib["r"][0]].append(float(value.text))
    return columns


def main() -> None:
    columns = numeric_columns(SOURCE)
    delta_exp = np.asarray(columns["A"])
    phase_exp = np.asarray(columns["B"])
    phase_sd = np.asarray(columns["C"])
    delta_theory = np.asarray(columns["D"])
    phase_theory = np.asarray(columns["E"])
    predicted = np.interp(delta_exp, delta_theory, phase_theory)
    residual = phase_exp - predicted
    z_score = residual / phase_sd

    result = {
        "schema_version": "1.0",
        "source_doi": "10.5061/dryad.x0k6djj14",
        "source_file": "data/public_optical_path_integral/FigS2B.xlsx",
        "measurement": "aggregate radial phase control in units of pi",
        "experimental_points": int(delta_exp.size),
        "theory_points": int(delta_theory.size),
        "comparison": {
            "interpolation": "linear theory interpolation onto the experimental delta grid",
            "phase_rmse_pi_units": float(np.sqrt(np.mean(residual**2))),
            "reduced_chi_squared": float(np.sum(z_score**2) / (delta_exp.size - 1)),
            "mean_absolute_z": float(np.mean(np.abs(z_score))),
            "maximum_absolute_z": float(np.max(np.abs(z_score))),
            "all_points_within_one_sigma": bool(np.all(np.abs(z_score) < 1.0)),
        },
        "eligibility": {
            "independent_standard_phase_control": True,
            "same_index_complex_amplitude": False,
            "recovery_process_or_error": False,
            "independent_tau_body_action": False,
            "tau_primary_score_eligible": False,
        },
        "verdict": (
            "Fig. S2B independently supports the published radial phase law, "
            "but its aggregate phase-only structure does not supply the missing "
            "same-carrier action, amplitude and recovery legs required for a Tau score."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    assert result["experimental_points"] == 17
    assert result["theory_points"] == 200
    assert result["comparison"]["all_points_within_one_sigma"] is True
    assert result["eligibility"]["tau_primary_score_eligible"] is False
    print(
        "WEN_FIGS2B_PHASE_CONTROL_PASS "
        f"rmse={result['comparison']['phase_rmse_pi_units']:.6f}pi "
        f"max_abs_z={result['comparison']['maximum_absolute_z']:.4f}"
    )


if __name__ == "__main__":
    main()
