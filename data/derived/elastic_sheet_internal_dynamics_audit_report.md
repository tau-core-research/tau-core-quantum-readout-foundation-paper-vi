# Tau Core elastic-sheet internal-dynamics audit v0.1

Status: **PASS**

This conventional finite control compares two frequency-operator
families with exactly the same isolated rank-two projector path but
different in-band spectra. It tests the standard Kato-frame
adiabatic factorization; it is not a Tau-specific prediction.

| duration | factorization error | matrix-corrected geometry error | scalar-only error | leakage |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 0.26559 | 0.249895 | 0.742637 | 0.0907491 |
| 20 | 0.137913 | 0.13576 | 1.63582 | 0.0243781 |
| 40 | 0.0792934 | 0.0757377 | 2.4572 | 0.0234991 |
| 80 | 0.0407616 | 0.0405714 | 2.29303 | 0.00393317 |
| 160 | 0.0220996 | 0.020741 | 2.10187 | 0.00762971 |

## Checks

- `same_projector_path`: **PASS**
- `different_internal_spectra`: **PASS**
- `same_kato_body_geometry`: **PASS**
- `different_complete_occurrence_transport`: **PASS**
- `degenerate_internal_dynamics_is_scalar`: **PASS**
- `split_internal_dynamics_is_not_scalar`: **PASS**
- `factorization_improves_with_duration`: **PASS**
- `matrix_corrected_geometry_improves`: **PASS**
- `slow_factorization_matches`: **PASS**
- `matrix_correction_recovers_body`: **PASS**
- `scalar_only_correction_fails_for_split_band`: **PASS**
- `benchmark_contains_no_tau_residual`: **PASS**

## Claim boundary

The common projector determines the common Kato/body geometry,
but it does not determine the complete occurrence transport.
A scalar phase removal is valid only for the exactly degenerate
band used in the earlier finite control. A general isolated band
requires independent reconstruction of its matrix-valued internal
dynamical propagator. Physical plate occupation and every
Tau-specific inference remain open.
