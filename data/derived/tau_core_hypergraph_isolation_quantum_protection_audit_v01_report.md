# Tau Core hypergraph-isolation quantum-protection audit v0.1

**Verdict:** `FULL_SOURCE_HYPERGRAPH_FACTORIZATION_IMPLIES_QUANTUM_PROTECTION;_ACTION_VALUATION_ALONE_IMPLIES_ONLY_ZERO_MIXED_HESSIAN`

## Checks

- [x] `disconnected_local_action_is_block_diagonal`
- [x] `isolated_hessian_is_positive`
- [x] `crossing_hyperedge_creates_mixed_hessian`
- [x] `isolated_descent_recovers_every_test_state`
- [x] `isolated_complement_is_state_independent`
- [x] `crossing_interaction_exports_information`
- [x] `crossing_interaction_dephases_coherence`
- [x] `interaction_control_preserves_total_trace`
- [x] `interaction_control_preserves_global_purity`

## Theorem

Disjoint action valuation forces action additivity and a zero mixed Hessian. If the source load, global generator and occupied state also factor across the same components, the inaccessible complement is logical-state independent and observer descent has an exact CPTP left inverse. The latter factors are additional global premises, not consequences of the Hessian calculation alone.

## Interaction boundary

A source-owned hyperedge crossing the partition creates the mixed Hessian and permits logical information to enter the complement. Local decoherence is then allowed while the complete joint state remains normalized and pure/unitary.

## Claim boundary

This verifies the full-factorization-to-recovery implication and the weaker valuation-to-Hessian implication separately. It does not derive global factorization from a local Hessian, prove exact isolation for every real apparatus, rule out weak residual couplings, derive a decoherence rate, measurement outcome or absolute hbar.
