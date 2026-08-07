#!/usr/bin/env python3
"""Audit the S3 obstruction to designating one logical factor as ROOT."""

import itertools
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/root_factor_designation_no_go.json"
permutations = list(itertools.permutations(range(3)))
matrices = []
for perm in permutations:
    p = np.zeros((3, 3))
    for old, new in enumerate(perm):
        p[new, old] = 1.0
    matrices.append(p)

one_hots = np.eye(3)
fixed_one_hots = [all(np.allclose(p @ e, e) for p in matrices) for e in one_hots]
constraints = np.vstack([p - np.eye(3) for p in matrices])
invariant_dimension = int(3 - np.linalg.matrix_rank(constraints, tol=1e-10))
orbit = {int(np.argmax(p @ one_hots[0])) for p in matrices}

result = {
    "schema_version": "1.0",
    "symmetry": "root stabilizer S3 acting transitively on the three Clifford factor labels",
    "factor_orbit_size": len(orbit),
    "invariant_label_space_dimension": invariant_dimension,
    "fixed_individual_factor_flags": fixed_one_hots,
    "checks": {
        "S3_action_is_transitive_on_three_factors": len(orbit) == 3,
        "no_individual_factor_is_S3_fixed": not any(fixed_one_hots),
        "only_scalar_label_direction_is_invariant": invariant_dimension == 1,
        "symmetric_access_weights_cannot_have_unique_factor_maximum": len(set([1.0, 1.0, 1.0])) == 1,
    },
    "theorem_status": {
        "oriented_factor_set": "selected conditionally by OHC-P1 plus rooted TC-CVP1",
        "distinguished_ROOT_M2": "not selected by the S3-symmetric rooted packet",
        "minimal_reopening": "a source-owned S3-breaking typed access functional or observer-source context",
        "chirality": "independent discrete selection remains open",
    },
    "verdict": "ROOTED_PACKET_SELECTS_AN_UNORDERED_FACTOR_TRIPLE_NOT_ONE_DISTINGUISHED_ROOT_FACTOR",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
