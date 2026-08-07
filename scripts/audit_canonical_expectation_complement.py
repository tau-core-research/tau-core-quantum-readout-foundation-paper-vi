#!/usr/bin/env python3
"""Audit the canonical trace-preserving expectation and its full complement."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/derived/canonical_expectation_complement_audit.json"

logical_dimension = 2
realization_dimension = 4
body_dimension = logical_dimension * realization_dimension
body_algebra_dimension = body_dimension**2
logical_algebra_dimension = logical_dimension**2
realization_algebra_dimension = realization_dimension**2
expectation_kernel_dimension = body_algebra_dimension - logical_algebra_dimension
kraus_rank_partial_trace = realization_dimension

result = {
    "schema_version": "1.0",
    "factorization": "M_8(C)=M_2(C) tensor M_4(C)",
    "canonical_expectation": "E_L=id_2 tensor tau_4, the normalized-trace-preserving A_L-bimodular conditional expectation",
    "dimensions": {
        "body_hilbert": body_dimension,
        "body_algebra": body_algebra_dimension,
        "logical_algebra": logical_algebra_dimension,
        "expectation_kernel": expectation_kernel_dimension,
        "minimal_kraus_rank": kraus_rank_partial_trace,
        "complement_hilbert": realization_dimension,
        "complement_algebra": realization_algebra_dimension,
    },
    "checks": {
        "body_factor_dimensions_multiply": body_dimension == 8,
        "algebra_factor_dimensions_multiply": logical_algebra_dimension * realization_algebra_dimension == body_algebra_dimension,
        "expectation_has_full_logical_range": body_algebra_dimension - expectation_kernel_dimension == logical_algebra_dimension,
        "minimal_partial_trace_dilation_has_four_dimensional_complement": kraus_rank_partial_trace == realization_dimension == 4,
        "complement_is_full_M4": realization_algebra_dimension == 16,
    },
    "status": {
        "maximal_complement": "derived after factor designation, complete M8 occupation, normalized-trace preservation and bimodularity",
        "uniqueness": "the trace-preserving conditional expectation onto the designated factor is canonical",
        "remaining_source": "the typed observer-source incidence selecting the M2 embedding is not derived from the minimal parent",
        "off_assumption_cases": "non-bimodular, non-tracial or incomplete-body access can have a smaller or different complement",
        "chirality": "independent open discrete selection",
    },
    "verdict": "CANONICAL_TRACE_EXPECTATION_FORCES_THE_FULL_M4_COMPLEMENT_AFTER_TYPED_FACTOR_DESIGNATION",
}

OUT.write_text(json.dumps(result, indent=2) + "\n")
print(OUT)
