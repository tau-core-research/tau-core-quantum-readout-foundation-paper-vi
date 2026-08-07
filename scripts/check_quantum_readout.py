#!/usr/bin/env python3
import json
from itertools import combinations
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ledger = json.loads((ROOT / "data/derived/quantum_readout_ledger.json").read_text())

# Metric-symplectic lock on R^4: A=g^{-1}omega and A^2=-I.
J2 = np.array([[0.0, -1.0], [1.0, 0.0]])
J = np.block([[J2, np.zeros((2, 2))], [np.zeros((2, 2)), J2]])
g = np.eye(4)
omega = g @ J
assert np.allclose(J @ J, -np.eye(4))
assert np.allclose(J.T @ g @ J, g)
assert np.allclose(omega.T, -omega)

# A commuting symmetric generator produces an orthogonal/unitary flow.
K = np.diag([1.0, 1.0, 2.0, 2.0])
X = J @ K
assert np.allclose(X.T, -X)
assert np.allclose(X @ J, J @ X)

# Born normalization and coherent interference.
psi = np.array([1.0, 1.0j]) / np.sqrt(2.0)
effects = [np.diag([1.0, 0.0]), np.diag([0.0, 1.0])]
probs = [np.real(np.vdot(psi, e @ psi)) for e in effects]
assert np.allclose(probs, [0.5, 0.5])
assert np.isclose(sum(probs), 1.0)
a, b, phi = 0.6, 0.8, 0.37
p_coh = abs(a + b * np.exp(1j * phi)) ** 2
p_expanded = a * a + b * b + 2 * a * b * np.cos(phi)
assert np.isclose(p_coh, p_expanded)

# Bell state: every local unitary on B leaves rho_A invariant.
bell = np.zeros(4, dtype=complex)
bell[0] = bell[3] = 1 / np.sqrt(2.0)
rho = np.outer(bell, bell.conj())
U = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
UB = np.kron(np.eye(2), U)
rho_out = UB @ rho @ UB.conj().T

def partial_trace_b(mat):
    return np.trace(mat.reshape(2, 2, 2, 2), axis1=1, axis2=3)

assert np.allclose(partial_trace_b(rho), partial_trace_b(rho_out))

# Dephasing keeps populations but removes the phase witness.
rho_plus = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
rho_dephased = np.diag(np.diag(rho_plus))
assert np.allclose(np.diag(rho_plus), np.diag(rho_dephased))
assert not np.allclose(rho_plus, rho_dephased)

# P3 record-rank ladder on one irreducible Cl_7(C) block.
I2 = np.eye(2, dtype=complex)
PX = np.array([[0, 1], [1, 0]], dtype=complex)
PY = np.array([[0, -1j], [1j, 0]], dtype=complex)
PZ = np.array([[1, 0], [0, -1]], dtype=complex)


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


gammas = [
    kron3(PX, I2, I2),
    kron3(PY, I2, I2),
    kron3(PZ, PX, I2),
    kron3(PZ, PY, I2),
    kron3(PZ, PZ, PX),
    kron3(PZ, PZ, PY),
    kron3(PZ, PZ, PZ),
]


def clifford_word(indices):
    out = np.eye(8, dtype=complex)
    for idx in indices:
        out = np.einsum("ij,jk->ik", out, gammas[idx])
    k = len(indices)
    return (1j ** (k * (k - 1) // 2)) * out


def cumulative_rank(max_grade):
    words = [
        clifford_word(indices)
        for grade in range(max_grade + 1)
        for indices in combinations(range(7), grade)
    ]
    rows = [
        np.concatenate((word.real.ravel(), word.imag.ravel())) for word in words
    ]
    return int(np.linalg.matrix_rank(np.stack(rows), tol=1e-10))


assert [cumulative_rank(k) for k in range(4)] == [1, 8, 29, 64]

# Canonical binary spectral effects span the full operator space, whereas one
# Frobenius-copyable pointer basis spans only the diagonal algebra.
all_words = [
    clifford_word(indices)
    for grade in range(4)
    for indices in combinations(range(7), grade)
]
spectral_effects = [
    (np.eye(8) + sign * word) / 2
    for word in all_words[1:]
    for sign in (1, -1)
]
effect_rows = [
    np.concatenate((effect.real.ravel(), effect.imag.ravel()))
    for effect in spectral_effects
]
pointer_rows = [
    np.concatenate((effect.real.ravel(), effect.imag.ravel()))
    for effect in [np.diag(np.eye(8)[k]) for k in range(8)]
]
assert len(spectral_effects) == 126
assert np.linalg.matrix_rank(np.stack(effect_rows), tol=1e-10) == 64
assert np.linalg.matrix_rank(np.stack(pointer_rows), tol=1e-10) == 8

assert ledger["proved"]["lossy_quotient_alone_implies_quantum_mechanics"] is False
assert ledger["proved"]["enriched_MVP_P3_handoff_constructs_single_system_packet"] is True
assert ledger["proved"]["separating_record_scalar_action_selects_Clifford_handoff"] is True
assert ledger["proved"]["normalized_trace_alone_selects_Clifford_handoff"] is False
assert ledger["proved"]["primitive_P3_records_are_separating"] is False
assert ledger["proved"]["binary_P3_word_records_are_separating"] is False
assert ledger["proved"]["ternary_P3_word_closure_is_separating"] is True
assert ledger["proved"]["ternary_P3_spectral_effect_atlas_is_separating"] is True
assert ledger["proved"]["frobenius_pointer_copying_alone_is_separating"] is False
assert ledger["proved"]["full_S4_effect_interval_plus_S5_terminal_implies_spectral_closure"] is True
assert ledger["proved"]["post_handoff_spectral_closure_selects_P3_handoff_noncircularly"] is False
assert ledger["proved"]["single_M2_or_pointer_record_selects_three_factor_tensor_structure"] is False
assert ledger["proved"]["two_commuting_M2_factors_select_the_third_as_commutant"] is True
assert ledger["proved"]["current_CHDF_Hessian_selects_nondegenerate_rooted_mixed_Gram"] is False
assert ledger["proved"]["occurrence_rank_completion_alone_selects_rooted_mixed_Gram"] is False
assert ledger["proved"]["source_root_involution_selects_pair_common_difference_isometry"] is True
assert ledger["proved"]["TC_CVP1_rooted_restriction_conditionally_selects_nondegenerate_mixed_Gram"] is True
assert ledger["proved"]["physical_parent_selects_TC_CVP1_rooted_restriction"] is False
assert ledger["proved"]["MBC_ACT_and_typed_TC_CVP1_reduce_continuous_tensor_blocker_to_occurrence_rank_five"] is True
assert ledger["proved"]["MBC_root_and_typed_TC_CVP1_alone_force_occurrence_rank_five"] is False
assert ledger["proved"]["OHC_P1_irreducible_occurrence_holonomy_forces_rank_five"] is True
assert ledger["proved"]["physical_MVP_adopts_OHC_P1_as_4D_constrained_completion"] is True
assert ledger["proved"]["nature_empirically_selects_OHC_P1"] is False
assert ledger["proved"]["physical_MVP_recovers_singlet_Tsirelson_correlations"] is True
assert ledger["proved"]["physical_MVP_conditionally_recovers_perturbative_causal_QFT"] is True
assert ledger["proved"]["physical_MVP_derives_nonperturbative_QFT"] is False
assert ledger["proved"]["common_Gram_completion_predicts_x_A_equals_x_Q"] is True
assert ledger["proved"]["current_reduct_entails_complete_joint_quantum_packet"] is False
assert ledger["proved"]["source_faithful_protected_representation_suffices_for_joint_packet"] is True
assert ledger["proved"]["standard_QM_alone_predicts_x_A_equals_x_Q"] is False
assert ledger["proved"]["QOR_speed_limit_is_itself_Tau_specific"] is False
assert ledger["proved"]["local_cptp_operations_preserve_remote_marginal"] is True
assert ledger["proved"]["observer_loss_entropy_is_von_neumann_entropy"] is False

print(
    "QUANTUM_READOUT_PASS "
    "classical_no_go=yes complex_lock=yes existing_source=yes "
    "p3_rank=1,8,29,64 spectral_atlas=64 pointer_rank=8 "
    "born=yes no_signalling=yes decoherence=yes"
)
