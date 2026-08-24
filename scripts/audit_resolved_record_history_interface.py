#!/usr/bin/env python3
"""Finite checks for the Paper-VI resolution, Choi and no-retro interface."""

import numpy as np


# Stable-cell exit bounds.
a_norm = 2.0
curvature = 0.5
r_inner = 0.10
r_outer = 0.20
disc = a_norm**2 - 2.0 * curvature * r_outer
assert disc > 0.0
delta_exit = (a_norm - np.sqrt(disc)) / curvature
delta_small = 0.02
delta_resolved = 1.05 * delta_exit
assert delta_small * a_norm + 0.5 * curvature * delta_small**2 < r_inner
assert delta_resolved * a_norm - 0.5 * curvature * delta_resolved**2 > r_outer

# One outward rank-one Kato jet on a rank-two accessible support.
e1, e2, e3 = np.eye(3)
P = np.diag([1.0, 1.0, 0.0])
X = np.outer(e3, e1)
assert np.allclose((np.eye(3) - P) @ X @ P, X)
G = X - X.T
roots = [np.outer(e1, e1), np.outer(e2, e2)]
assert np.allclose(sum((s @ s for s in roots), start=np.zeros((3, 3))), P)

choi_derivatives = []
effect_derivatives = []
for root in roots:
    kdot = G @ root
    ket = root.reshape(-1)
    dotket = kdot.reshape(-1)
    choi_derivatives.append(np.outer(dotket, ket) + np.outer(ket, dotket))
    effect_derivatives.append(kdot.T @ root + root @ kdot)

assert any(np.linalg.norm(dot_j) > 1e-12 for dot_j in choi_derivatives)
assert np.linalg.norm(choi_derivatives[1]) < 1e-12  # incomplete blind subset
assert all(np.linalg.norm(dot_f) < 1e-12 for dot_f in effect_derivatives)

# Common preparation plus normalized later kernels preserves the early marginal.
weights = np.array([0.1, 0.2, 0.3, 0.4])
early = np.array([0, 0, 1, 1])
kernels = {
    0: np.array([[0.8, 0.2], [0.4, 0.6], [0.3, 0.7], [0.9, 0.1]]),
    1: np.array([[0.1, 0.9], [0.7, 0.3], [0.6, 0.4], [0.2, 0.8]]),
}
expected_early = np.array([weights[early == x].sum() for x in (0, 1)])
for kernel in kernels.values():
    assert np.allclose(kernel.sum(axis=1), 1.0)
    joint = np.zeros((2, 2))
    for p, weight in enumerate(weights):
        joint[early[p]] += weight * kernel[p]
    assert np.allclose(joint.sum(axis=1), expected_early)

# Record invariance alone is insufficient if the preparation changes with setting.
weights_changed = np.array([0.4, 0.3, 0.2, 0.1])
changed_early = np.array([weights_changed[early == x].sum() for x in (0, 1)])
assert not np.allclose(changed_early, expected_early)

# Complementary conditioned fringes cancel in the unconditioned marginal.
phase = np.linspace(0.0, 2.0 * np.pi, 17, endpoint=False)
visibility = 0.73
plus = (1.0 + visibility * np.cos(phase)) / (2.0 * len(phase))
minus = (1.0 - visibility * np.cos(phase)) / (2.0 * len(phase))
assert np.allclose(plus + minus, np.full(len(phase), 1.0 / len(phase)))

print(
    "RESOLVED_RECORD_HISTORY_INTERFACE_PASS "
    "cell_window=yes exhaustive_choi=yes probability_blind=yes "
    "no_retro_marginal=yes record_invariance_alone=no"
)
