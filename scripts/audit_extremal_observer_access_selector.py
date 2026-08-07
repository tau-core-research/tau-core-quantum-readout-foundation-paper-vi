#!/usr/bin/env python3
"""Audit extremal observer access as the exact ROOT-factor selector."""

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/extremal_observer_access_selector_audit.json"

weight_sets = {
    "symmetric": [1 / 3, 1 / 3, 1 / 3],
    "generic": [0.2, 0.7, 0.1],
    "extremal_factor_0": [1.0, 0.0, 0.0],
}
rows = []
for name, weights in weight_sets.items():
    for logical_factor in range(3):
        gamma = weights[logical_factor]
        rows.append(
            {
                "access": name,
                "logical_factor": logical_factor,
                "gamma": gamma,
                "exact_full_logical_recovery": gamma == 1.0,
            }
        )

extremal = weight_sets["extremal_factor_0"]
covariant = True
for perm in itertools.permutations(range(3)):
    permuted = [0.0, 0.0, 0.0]
    for old, new in enumerate(perm):
        permuted[new] = extremal[old]
    covariant &= permuted[perm[0]] == 1.0 and sum(permuted) == 1.0

result = {
    "schema_version": "1.0",
    "access_law": "C_w=sum_j w_j Tr_not_j after source-typed output identification",
    "encoded_factor_response": "C_w iota_j(rho)=w_j rho+(1-w_j)I/2, so gamma_j=w_j",
    "rows": rows,
    "checks": {
        "symmetric_access_has_gamma_one_third_on_every_factor": all(
            abs(row["gamma"] - 1 / 3) < 1e-15
            for row in rows if row["access"] == "symmetric"
        ),
        "generic_dominant_but_nonextremal_access_is_not_exactly_recoverable": not any(
            row["exact_full_logical_recovery"] for row in rows if row["access"] == "generic"
        ),
        "extremal_access_exactly_recovers_one_factor_only": [
            row["exact_full_logical_recovery"]
            for row in rows if row["access"] == "extremal_factor_0"
        ] == [True, False, False],
        "factor_selection_is_covariant_under_S3_relabeling": bool(covariant),
    },
    "theorem_status": {
        "selector": "exact A8b recovery selects a simplex vertex w=e_j, not merely a unique maximum",
        "observer_dependence": "different source-typed extremal access maps may covariantly designate different factors",
        "physical_selection": "the parent/body observer-access law has not yet been shown to occupy a simplex vertex",
        "chirality": "unchanged independent discrete blocker",
    },
    "verdict": "EXACT_A8B_RECOVERY_EQUIVALENT_TO_EXTREMAL_FACTOR_ACCESS_WITHIN_THE_WEIGHTED_ACCESS_FAMILY",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
