#!/usr/bin/env python3
"""Record the conditional-rank audit for standard generalized-force probes."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/generalized_force_independence_audit.json"


result = {
    "schema_version": "1.0",
    "standard_force_law": "M_mu=-Tr[rho d_mu H]",
    "frozen_inputs": ["rho", "H", "d_mu_H", "control_protocol"],
    "factorization": {
        "map": "M=F(rho,H,dH)",
        "conditional_information_I_M_xA_given_rho_controls": 0,
        "stacked_jacobian_rank_increase_beyond_rho_and_controls": 0,
    },
    "adiabatic_response": {
        "schematic_law": "M_mu=M_mu^(0)+F_munu dot(lambda)^nu+O(dot(lambda)^2)",
        "berry_curvature_is_quantum_geometric_response": True,
        "qgt_reconstruction_is_independent_instrumental_control": True,
        "qgt_reconstruction_is_independent_tau_action_axis": False,
    },
    "no_go": (
        "A standard generalized-force/QGT experiment can independently measure quantum geometry, "
        "but after conditioning on the reconstructed state and frozen Hamiltonian family its force "
        "record supplies no new coordinate capable of testing x_A=x_Q."
    ),
    "reopening_condition": (
        "A separately calibrated source-port residual xi_mu=M_mu+Tr[rho d_mu H] must be nonzero, "
        "replicate under blind controls, survive conditioning on rho,H and instrument calibration, "
        "and integrate with a frozen common unit to the once-counted body action before tomography."
    ),
    "remaining_public_route": (
        "Calorimetric or mechanical source-port records may provide conditional measurement novelty, "
        "but no audited public same-carrier packet yet supplies the required body-action map, endpoint "
        "geometry and holonomy."
    ),
    "status": "STANDARD_GENERALIZED_FORCE_SHORTCUT_CLOSED",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)

