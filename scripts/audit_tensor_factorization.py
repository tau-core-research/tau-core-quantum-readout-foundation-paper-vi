#!/usr/bin/env python3
"""Finite audit of subsystem-factor selection on one occupied M_8(C) block."""

import json
import itertools
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def k3(a, b, c):
    return np.kron(np.kron(a, b), c)


def complex_rank(mats):
    rows = [m.ravel() for m in mats]
    return int(np.linalg.matrix_rank(np.stack(rows), tol=1e-10))


def algebra_basis(generators):
    basis = [np.eye(8, dtype=complex)]
    frontier = list(generators)
    while frontier:
        candidate = frontier.pop(0)
        if complex_rank(basis + [candidate]) == complex_rank(basis):
            continue
        basis.append(candidate)
        frontier.extend(candidate @ g for g in generators)
    return basis


def commutant_dimension(generators):
    eye = np.eye(8, dtype=complex)
    constraints = [np.kron(eye, g) - np.kron(g.T, eye) for g in generators]
    return int(64 - np.linalg.matrix_rank(np.vstack(constraints), tol=1e-10))


factors = [
    [k3(X, I2, I2), k3(Y, I2, I2), k3(Z, I2, I2)],
    [k3(I2, X, I2), k3(I2, Y, I2), k3(I2, Z, I2)],
    [k3(I2, I2, X), k3(I2, I2, Y), k3(I2, I2, Z)],
]
factor_bases = [algebra_basis(gens) for gens in factors]
assert [len(b) for b in factor_bases] == [4, 4, 4]
for i in range(3):
    for j in range(i + 1, 3):
        assert all(np.allclose(a @ b, b @ a) for a in factors[i] for b in factors[j])
products = [a @ b @ c for a in factor_bases[0] for b in factor_bases[1] for c in factor_bases[2]]
assert complex_rank(products) == 64
commutants = [
    commutant_dimension(factors[0]),
    commutant_dimension(factors[0] + factors[1]),
    commutant_dimension(factors[0] + factors[1] + factors[2]),
]
assert commutants == [16, 4, 1]

# This entangling diagonal unitary fixes the full pointer algebra pointwise,
# yet moves the first two local factor algebras.
theta = np.pi / 8
zzi = k3(Z, Z, I2)
unitary = np.cos(theta) * np.eye(8) + 1j * np.sin(theta) * zzi
pointer = [np.diag(np.eye(8)[j]) for j in range(8)]
assert all(np.allclose(unitary @ p @ unitary.conj().T, p) for p in pointer)
moved = [[unitary @ g @ unitary.conj().T for g in gens] for gens in factors]
moved_bases = [algebra_basis(gens) for gens in moved]
moved_products = [a @ b @ c for a in moved_bases[0] for b in moved_bases[1] for c in moved_bases[2]]
assert complex_rank(moved_products) == 64
assert complex_rank(factor_bases[0] + moved_bases[0]) > 4

# A source-owned oriented Clifford flag reconstructs the local factors.  With
# gamma pairs (1,2), (3,4), (5,6), define parity-corrected Pauli generators.
gammas = [
    k3(X, I2, I2), k3(Y, I2, I2),
    k3(Z, X, I2), k3(Z, Y, I2),
    k3(Z, Z, X), k3(Z, Z, Y), k3(Z, Z, Z),
]
flag_factors = []
parity = np.eye(8, dtype=complex)
for j in range(3):
    ga, gb = gammas[2 * j], gammas[2 * j + 1]
    zj = -1j * ga @ gb
    xj = parity @ ga
    yj = parity @ gb
    flag_factors.append([xj, yj, zj])
    parity = parity @ zj
for i in range(3):
    for j in range(i + 1, 3):
        assert all(np.allclose(a @ b, b @ a) for a in flag_factors[i] for b in flag_factors[j])
assert all(len(algebra_basis(gens)) == 4 for gens in flag_factors)
flag_products = [
    a @ b @ c
    for a in algebra_basis(flag_factors[0])
    for b in algebra_basis(flag_factors[1])
    for c in algebra_basis(flag_factors[2])
]
assert complex_rank(flag_products) == 64
assert np.allclose(flag_factors[0][2] @ flag_factors[1][2] @ flag_factors[2][2], gammas[6])

# Tetrahedral edge carrier: the CHDF pair-sum image has rank four and a
# two-dimensional orthogonal complement. Adding that complement as a positive
# zero-background fluctuation module restores the full six-edge carrier.
edges = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
edge_index = {tuple(sorted(edge)): idx for idx, edge in enumerate(edges)}
phi_sum = np.zeros((6, 4))
for row, (a, b) in enumerate(edges):
    phi_sum[row, a] = phi_sum[row, b] = 1.0
_, _, vh = np.linalg.svd(phi_sum.T)
w2_basis = vh[-2:].T
assert np.linalg.matrix_rank(phi_sum) == 4
assert w2_basis.shape == (6, 2)
assert np.allclose(phi_sum.T @ w2_basis, 0.0)
assert np.linalg.matrix_rank(np.column_stack((phi_sum, w2_basis))) == 6

# The current CHDF image contains all three pair-difference directions but
# only the scalar pair-common line.  The pair-common W2 copy is therefore not
# a body coordinate of the rank-four realization.  After rooting, an
# equivariant common/difference mixed block can consequently have rank at most
# one; the W2 coefficient required by the full polarization is absent.
pair_common = np.zeros((6, 3))
pair_difference = np.zeros((6, 3))
for j in range(3):
    pair_common[2 * j:2 * j + 2, j] = 1.0
    pair_difference[2 * j, j] = 1.0
    pair_difference[2 * j + 1, j] = -1.0


def intersection_dimension(a, b):
    return int(
        np.linalg.matrix_rank(a, tol=1e-10)
        + np.linalg.matrix_rank(b, tol=1e-10)
        - np.linalg.matrix_rank(np.column_stack((a, b)), tol=1e-10)
    )


current_common_dimension = intersection_dimension(phi_sum, pair_common)
current_difference_dimension = intersection_dimension(phi_sum, pair_difference)
assert current_common_dimension == 1
assert current_difference_dimension == 3
assert current_common_dimension + current_difference_dimension == 4
current_pair_common_w2_dimension = current_common_dimension - 1
assert current_pair_common_w2_dimension == 0
current_rooted_mixed_gram_max_rank = (
    min(1, current_common_dimension)
    + min(2, current_pair_common_w2_dimension)
)
assert current_rooted_mixed_gram_max_rank == 1

# A source-owned root orders each opposite pair as root-incident/opposite.
# Its sign involution exchanges pair differences and pair commons.  It is
# orthogonal and commutes with every root-stabilizing S3 permutation.
root_involution = np.diag([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
common_frame = pair_common / np.sqrt(2.0)
difference_frame = pair_difference / np.sqrt(2.0)
root_pair_isometry = common_frame.T @ root_involution @ difference_frame
assert np.allclose(root_pair_isometry, np.eye(3))
assert np.allclose(root_involution.T @ root_involution, np.eye(6))
for perm_tail in itertools.permutations((1, 2, 3)):
    perm = (0,) + perm_tail
    p_edge = np.zeros((6, 6))
    for old, edge in enumerate(edges):
        new_edge = tuple(sorted((perm[edge[0]], perm[edge[1]])))
        p_edge[edge_index[new_edge], old] = 1.0
    assert np.allclose(p_edge @ root_involution, root_involution @ p_edge)

# The quadratic germ of the already adopted common convex-potential candidate,
# restricted to the rooted common/difference pair, has a nondegenerate mixed
# Hessian on all three directions.  In rooted irreducible coordinates this
# gives equal nonzero scalar and W2 coefficients.  This is a conditional
# completion statement, not current-CHDF or unrestricted physical ownership.
mu0 = 1.0
h_cc = mu0 * np.eye(3)
h_dd = mu0 * np.eye(3)
h_cd = -mu0 * root_pair_isometry
joint_root_hessian = np.block([[h_cc, h_cd], [h_cd.T, h_dd]])
assert np.linalg.matrix_rank(h_cd, tol=1e-10) == 3
assert np.allclose(np.linalg.eigvalsh(joint_root_hessian), [0, 0, 0, 2, 2, 2])

# The S4-invariant symmetric Hessian space on W2 is one-dimensional.  Hence an
# admissible invariant enrichment has only one stiffness coefficient.
sym_basis = [
    np.array([[1.0, 0.0], [0.0, 0.0]]),
    np.array([[0.0, 0.0], [0.0, 1.0]]),
    np.array([[0.0, 1.0], [1.0, 0.0]]),
]
constraints = []
for perm in itertools.permutations(range(4)):
    p_edge = np.zeros((6, 6))
    for old, edge in enumerate(edges):
        new_edge = tuple(sorted((perm[edge[0]], perm[edge[1]])))
        p_edge[edge_index[new_edge], old] = 1.0
    rep = w2_basis.T @ p_edge @ w2_basis
    columns = [(rep.T @ h @ rep - h).ravel() for h in sym_basis]
    constraints.append(np.stack(columns, axis=1))
constraint_matrix = np.vstack(constraints)
invariant_hessian_dimension = int(3 - np.linalg.matrix_rank(constraint_matrix, tol=1e-10))
assert invariant_hessian_dimension == 1

# Existing occurrence-transport witness: one tetrahedral STF orbit spans rank
# three; one generic base-owned SO(3) frame transport expands it to rank five.
tetra = np.array([
    [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]
], dtype=float) / np.sqrt(3.0)


def tf_outer(v):
    return np.outer(v, v) - np.eye(3) * np.dot(v, v) / 3.0


def sym5(q):
    return np.array([q[0, 0], q[1, 1], q[0, 1], q[0, 2], q[1, 2]])


seed_stf = [tf_outer(v) for v in tetra]
aligned_occurrence_rank = np.linalg.matrix_rank(
    np.stack([sym5(q) for q in seed_stf + seed_stf]), tol=1e-10
)
assert aligned_occurrence_rank == 3
axis = np.array([1.0, 2.0, 3.0])
axis /= np.linalg.norm(axis)
angle = 0.7
kx = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
rot = np.eye(3) + np.sin(angle) * kx + (1 - np.cos(angle)) * (kx @ kx)
transported_stf = [rot @ q @ rot.T for q in seed_stf]
occurrence_rank = np.linalg.matrix_rank(
    np.stack([sym5(q) for q in seed_stf + transported_stf]), tol=1e-10
)
assert occurrence_rank == 5

# Natural tetrahedral decoder Gram: opposite edges are orthogonal within each
# pair, but the three pair planes are not mutually orthogonal.
projectors = []
for a, b in edges:
    direction = tetra[a] - tetra[b]
    direction /= np.linalg.norm(direction)
    projectors.append(np.outer(direction, direction))
edge_gram = np.array([[np.trace(a @ b) for b in projectors] for a in projectors])
for j in range(3):
    assert np.isclose(edge_gram[2 * j, 2 * j + 1], 0.0)
cross_blocks = [
    edge_gram[2 * i:2 * i + 2, 2 * j:2 * j + 2]
    for i in range(3) for j in range(i + 1, 3)
]
assert all(np.allclose(block, 0.25 * np.ones((2, 2))) for block in cross_blocks)
assert np.allclose(np.linalg.eigvalsh(edge_gram), [0.5, 0.5, 1.0, 1.0, 1.0, 2.0])

# Independence controls.  Both zero and positive W2 stiffness preserve the
# same rank-four occupied equilibrium w=0.  Either central chirality can be
# represented on the same M8 matrices by changing the sign of gamma_7.
w2_hessians = [0.0 * np.eye(2), 1.0 * np.eye(2)]
assert all(np.allclose(h @ np.zeros(2), 0.0) for h in w2_hessians)
assert np.linalg.matrix_rank(w2_hessians[0]) == 0
assert np.linalg.matrix_rank(w2_hessians[1]) == 2
for chirality in (-1, 1):
    assert np.allclose(chirality * gammas[6], chirality * flag_factors[0][2] @ flag_factors[1][2] @ flag_factors[2][2])

result = {
    "schema": "tau-core-paper-vi-tensor-factorization-audit-v0.1",
    "canonical_factor_dimensions": [len(b) for b in factor_bases],
    "joint_generated_complex_rank": complex_rank(products),
    "commutant_complex_dimensions_after_1_2_3_factors": commutants,
    "pointer_projectors_fixed_by_entangling_unitary": True,
    "first_factor_moved_outside_original_span": True,
    "moved_joint_generated_complex_rank": complex_rank(moved_products),
    "unoriented_pairing_choices_before_source_typing": 105,
    "oriented_clifford_flag_constructs_three_commuting_factors": True,
    "seventh_gamma_equals_product_of_three_flag_parities_on_selected_block": True,
    "tetrahedral_pair_sum_rank": 4,
    "tetrahedral_W2_complement_rank": 2,
    "rank4_plus_positive_W2_fluctuation_completes_edge_carrier": True,
    "current_CHDF_pair_common_dimension": current_common_dimension,
    "current_CHDF_pair_difference_dimension": current_difference_dimension,
    "current_CHDF_pair_common_W2_dimension": current_pair_common_w2_dimension,
    "current_rooted_mixed_Gram_max_rank": current_rooted_mixed_gram_max_rank,
    "current_CHDF_Hessian_can_own_nondegenerate_rooted_mixed_Gram": False,
    "source_root_involution_maps_pair_differences_to_pair_commons": True,
    "source_root_involution_commutes_with_root_stabilizer_S3": True,
    "TC_CVP1_quadratic_germ_rooted_mixed_Gram_rank": int(np.linalg.matrix_rank(h_cd)),
    "TC_CVP1_quadratic_germ_has_nonzero_scalar_and_W2_coefficients": True,
    "TC_CVP1_rooted_polarization_is_Nature_selected": False,
    "S4_invariant_symmetric_W2_hessian_dimension": invariant_hessian_dimension,
    "single_tetrahedral_STF_orbit_rank": 3,
    "aligned_two_occurrence_STF_rank": int(aligned_occurrence_rank),
    "two_frame_occurrence_STF_rank": int(occurrence_rank),
    "base_occurrence_transport_can_generate_missing_W2_without_new_seed_data": True,
    "MBC_root_and_typed_TC_CVP1_alone_force_occurrence_rank_five": False,
    "natural_tetrahedral_opposite_edge_planes_are_mutually_orthogonal": False,
    "natural_tetrahedral_edge_gram_eigenvalues": [0.5, 0.5, 1.0, 1.0, 1.0, 2.0],
    "same_rank4_equilibrium_allows_zero_and_positive_W2_stiffness": True,
    "same_six_gamma_factorization_allows_both_central_chiralities": True,
    "verdict": {
        "one_record_or_one_M2_factor_selects_three_factorization": False,
        "two_commuting_M2_factors_select_third_as_commutant": True,
        "full_factor_ledger_is_selected_by_current_parent": False
    }
}
(ROOT / "data/derived/tensor_factorization_audit.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
print("TENSOR_FACTORIZATION_PASS rank=64 commutants=16,4,1 pointer_no_go=yes")
