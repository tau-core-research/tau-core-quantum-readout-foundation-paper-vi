#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[1]
OUTS = [ROOT / "figures", ROOT / "paperVI_submission_source" / "figures"]
for out in OUTS:
    out.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, w, h, text, color="#e8f0f7"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                           linewidth=1.2, edgecolor="#35556f", facecolor=color)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)


def arrow(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=12,
                                 linewidth=1.2, color="#35556f"))


def save(fig, name):
    for out in OUTS:
        fig.savefig(out / name, bbox_inches="tight")
    plt.close(fig)


fig, ax = plt.subplots(figsize=(10, 2.8))
ax.set_xlim(0, 10); ax.set_ylim(0, 2.8); ax.axis("off")
labels = [
    (0.1, "Atemporal body\nand observer access"),
    (2.15, "Lossy stable\nreadout classes"),
    (4.2, "Metric + phase\ncurvature"),
    (6.25, "Hilbert, effects,\ncoherent composition"),
    (8.3, "Born, unitary,\nno-signalling")]
for x, text in labels:
    box(ax, x, 1.0, 1.55, 0.8, text)
for i in range(4):
    arrow(ax, (labels[i][0] + 1.55, 1.4), (labels[i + 1][0], 1.4))
ax.text(3.0, 0.35, "information loss alone is insufficient", color="#a33b32", fontsize=10)
save(fig, "fig_quantum_descent_spine.pdf")

fig, ax = plt.subplots(figsize=(8.5, 4.2))
ax.set_xlim(0, 8.5); ax.set_ylim(0, 4.2); ax.axis("off")
box(ax, 3.1, 3.0, 2.3, 0.75, "Same ordered\ntwo-class quotient", "#f3f0df")
box(ax, 0.7, 1.0, 2.5, 1.0, "Classical completion\ncommutative algebra\nno interference", "#eaf3e8")
box(ax, 5.3, 1.0, 2.5, 1.0, "Quantum completion\ncomplex rays + effects\ninterference", "#e8eef8")
arrow(ax, (3.7, 3.0), (2.1, 2.0)); arrow(ax, (4.8, 3.0), (6.5, 2.0))
ax.text(4.25, 0.35, "quotient and finite capacity do not select the branch",
        ha="center", color="#a33b32", fontsize=10)
save(fig, "fig_quantum_classical_fork.pdf")

fig, ax = plt.subplots(figsize=(9.2, 4.3))
ax.set_xlim(0, 9.2); ax.set_ylim(0, 4.3); ax.axis("off")
box(ax, 3.45, 3.1, 2.3, 0.7, "Joint state $\\rho_{AB}$", "#f3f0df")
box(ax, 0.6, 1.1, 2.5, 0.9, "Local instrument on A\nselective record", "#e8eef8")
box(ax, 6.1, 1.1, 2.5, 0.9, "Local CPTP map on B\nnonselective", "#eaf3e8")
arrow(ax, (4.0, 3.1), (2.0, 2.0)); arrow(ax, (5.2, 3.1), (7.3, 2.0))
ax.text(4.6, 0.45,
        "remote marginal unchanged by local CPTP operation;\nconditional postselection is a different claim",
        ha="center", fontsize=10, color="#35556f")
save(fig, "fig_no_signalling_instrument.pdf")

print("QUANTUM_FIGURES_BUILT")

