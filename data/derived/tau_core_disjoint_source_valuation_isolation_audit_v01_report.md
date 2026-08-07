# Tau Core disjoint-source valuation isolation audit v0.1

**Verdict:** `DISJOINT_SOURCE_VALUATION_FORCES_ACTION_ADDITIVITY_AND_ZERO_MIXED_HESSIAN;_RECOVERY_NEEDS_ADDITIONAL_GLOBAL_FACTORIZATION`

## Checks

- [x] `valuation_hessian_positive`
- [x] `countermodel_hessian_positive`
- [x] `valuation_action_adds_on_disjoint_components`
- [x] `valuation_mixed_hessian_zero`
- [x] `countermodel_preserves_internal_component_symmetry`
- [x] `countermodel_violates_disjoint_additivity`
- [x] `countermodel_has_nonzero_mixed_hessian`
- [x] `cross_defect_matches_bilinear_term`

## Claim boundary

Finite representation and non-entailment audit. It proves the action and Hessian consequences of disjoint-source valuation and shows that weaker once-counting, positivity and symmetry assumptions do not select it. A zero mixed Hessian alone does not prove factorization of loads, generators, occupied states or exact quantum recovery. It does not prove that Nature realizes the valuation law.
