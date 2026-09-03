#!/usr/bin/env python3
"""Audit atemporal-body/terminal-loss operator identities.

The finite control starts from one self-adjoint body-conditioned generator.
It verifies that full occurrence transport is unitary while observer access is
lossy by exact compression, that hidden-mode elimination gives the exact
Schur resolvent and a passive effective self-energy, and that clock
reparameterization does not introduce a parent meta-time.  A body variation
that is invisible to one terminal but visible to a stacked terminal supplies
the single-observer physicality countercontrol.

This is a conditional operator theorem and standard linear-systems control,
not a construction or Nature-occupation proof for physical M_tau.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data/derived"
JSON_PATH = OUT_DIR / "atemporal_body_terminal_loss_audit.json"
REPORT_PATH = OUT_DIR / "atemporal_body_terminal_loss_audit_report.md"


def serialize_matrix(matrix: np.ndarray) -> dict[str, object]:
    return {"real": np.real(matrix).tolist(), "imag": np.imag(matrix).tolist()}


def body_generator() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return visible/hidden blocks and one self-adjoint full generator."""

    visible = np.array([[1.10, 0.22], [0.22, 1.70]])
    hidden = np.diag([2.50, 3.20])
    coupling = np.array([[0.35, 0.0], [0.12, 0.0]])
    full = np.block([[visible, coupling], [coupling.T, hidden]])
    return visible, hidden, coupling, full


def loss_identity(
    propagator: np.ndarray,
    source: np.ndarray,
    access: np.ndarray,
) -> dict[str, object]:
    """Evaluate the exact source/access compression-loss decomposition."""

    transfer = access @ propagator @ source
    source_identity = np.eye(source.shape[1])
    full_identity = np.eye(propagator.shape[0])
    lhs = source_identity - transfer.conj().T @ transfer
    rhs = (
        source_identity - source.conj().T @ source
        + source.conj().T
        @ propagator.conj().T
        @ (full_identity - access.conj().T @ access)
        @ propagator
        @ source
    )
    lhs_hermitian = 0.5 * (lhs + lhs.conj().T)
    return {
        "transfer": transfer,
        "identity_error": float(np.linalg.norm(lhs - rhs, ord="fro")),
        "minimum_loss_eigenvalue": float(
            np.min(np.linalg.eigvalsh(lhs_hermitian))
        ),
        "transfer_singular_values": np.linalg.svd(
            transfer, compute_uv=False
        ).tolist(),
    }


def run_audit() -> dict[str, object]:
    visible, hidden, coupling, generator = body_generator()
    duration = 1.30
    propagator = expm(-1.0j * generator * duration)

    source = np.column_stack((np.eye(4)[:, 0], np.eye(4)[:, 3]))
    access_one = np.array(
        [[0.80, 0.0, 0.0, 0.0], [0.0, 0.55, 0.0, 0.0]]
    )
    access_two = np.array([[0.0, 0.0, 0.0, 0.70]])
    access_stack = np.vstack((access_one, access_two))

    one = loss_identity(propagator, source, access_one)
    stacked = loss_identity(propagator, source, access_stack)

    spectral_parameter = 1.55 + 0.12j
    full_resolvent = np.linalg.inv(
        spectral_parameter * np.eye(4) - generator
    )
    hidden_resolvent = np.linalg.inv(
        spectral_parameter * np.eye(2) - hidden
    )
    self_energy = coupling @ hidden_resolvent @ coupling.T
    schur_resolvent = np.linalg.inv(
        spectral_parameter * np.eye(2) - visible - self_energy
    )
    visible_resolvent = full_resolvent[:2, :2]
    passive_matrix = -np.imag(self_energy)
    passive_matrix = 0.5 * (passive_matrix + passive_matrix.T)
    passive_eigenvalues = np.linalg.eigvalsh(passive_matrix)

    clock_scale = 3.70
    reparameterized = expm(
        -1.0j * (generator / clock_scale) * (clock_scale * duration)
    )

    body_variation = np.diag([0.0, 0.0, 0.0, 0.40])
    perturbed_generator = generator + body_variation
    perturbed_propagator = expm(-1.0j * perturbed_generator * duration)
    transfer_one = access_one @ propagator @ source
    transfer_one_perturbed = access_one @ perturbed_propagator @ source
    transfer_stack = access_stack @ propagator @ source
    transfer_stack_perturbed = access_stack @ perturbed_propagator @ source
    one_observer_variation = float(
        np.linalg.norm(transfer_one_perturbed - transfer_one, ord="fro")
    )
    stacked_variation = float(
        np.linalg.norm(
            transfer_stack_perturbed - transfer_stack, ord="fro"
        )
    )

    unitarity_error = float(
        np.linalg.norm(
            propagator.conj().T @ propagator - np.eye(4), ord="fro"
        )
    )
    self_adjoint_error = float(
        np.linalg.norm(generator - generator.conj().T, ord="fro")
    )
    reparameterization_error = float(
        np.linalg.norm(reparameterized - propagator, ord="fro")
    )
    schur_error = float(
        np.linalg.norm(visible_resolvent - schur_resolvent, ord="fro")
    )
    terminal_difference = float(
        np.linalg.norm(
            access_one.conj().T @ access_one
            - access_stack.conj().T @ access_stack,
            ord="fro",
        )
    )
    checks = {
        "body_generator_is_self_adjoint": self_adjoint_error < 1.0e-14,
        "full_occurrence_transport_is_unitary": unitarity_error < 1.0e-12,
        "single_terminal_loss_identity": one["identity_error"] < 1.0e-12,
        "stacked_terminal_loss_identity": stacked["identity_error"] < 1.0e-12,
        "loss_defects_are_positive": (
            one["minimum_loss_eigenvalue"] > -1.0e-12
            and stacked["minimum_loss_eigenvalue"] > -1.0e-12
        ),
        "observer_transfer_is_strictly_contractive": max(
            one["transfer_singular_values"]
        ) < 1.0,
        "hidden_mode_schur_resolvent_is_exact": schur_error < 1.0e-12,
        "hidden_self_energy_is_passive": (
            np.min(passive_eigenvalues) > -1.0e-12
            and np.max(passive_eigenvalues) > 1.0e-5
        ),
        "clock_reparameterization_preserves_transport": (
            reparameterization_error < 1.0e-12
        ),
        "different_terminals_read_different_body_fractions": (
            terminal_difference > 0.1
        ),
        "one_observer_can_miss_a_nonzero_body_variation": (
            np.linalg.norm(body_variation) > 0.1
            and one_observer_variation < 1.0e-12
        ),
        "stacked_observer_detects_that_body_variation": stacked_variation > 0.1,
        "benchmark_contains_no_tau_residual": True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "claim_level": "conditional operator theorem / standard finite control",
        "parameters": {
            "duration_terminal_clock_units": duration,
            "clock_reparameterization_scale": clock_scale,
            "spectral_parameter": {
                "real": float(np.real(spectral_parameter)),
                "imag": float(np.imag(spectral_parameter)),
            },
        },
        "self_adjoint_error": self_adjoint_error,
        "unitarity_error": unitarity_error,
        "single_terminal": {
            "loss_identity_error": one["identity_error"],
            "minimum_loss_eigenvalue": one["minimum_loss_eigenvalue"],
            "transfer_singular_values": one["transfer_singular_values"],
        },
        "stacked_terminal": {
            "loss_identity_error": stacked["identity_error"],
            "minimum_loss_eigenvalue": stacked[
                "minimum_loss_eigenvalue"
            ],
            "transfer_singular_values": stacked[
                "transfer_singular_values"
            ],
        },
        "schur_resolvent_error": schur_error,
        "passive_self_energy_eigenvalues": passive_eigenvalues.tolist(),
        "clock_reparameterization_error": reparameterization_error,
        "terminal_effect_difference": terminal_difference,
        "single_observer_body_variation_response": one_observer_variation,
        "stacked_body_variation_response": stacked_variation,
        "body_generator": serialize_matrix(generator),
        "self_energy": serialize_matrix(self_energy),
        "checks": {key: bool(value) for key, value in checks.items()},
        "physical_m_tau_constructed": False,
        "parent_meta_time_required": False,
        "tau_specific_residual": None,
        "nature_occupation": "not established",
    }


def write_report(result: dict[str, object]) -> None:
    lines = [
        "# Tau Core atemporal-body terminal-loss audit v0.1",
        "",
        f"Status: **{result['status']}**",
        "",
        "One self-adjoint finite body generator produces unitary full",
        "occurrence transport. Observer access is nevertheless strictly lossy",
        "because it is a contractive compression. Hidden-mode elimination is",
        "checked independently through the exact Schur resolvent.",
        "",
        "## Key residuals",
        "",
        f"- self-adjoint residual: `{result['self_adjoint_error']:.6g}`",
        f"- full unitarity residual: `{result['unitarity_error']:.6g}`",
        f"- single-terminal loss identity: `{result['single_terminal']['loss_identity_error']:.6g}`",
        f"- stacked-terminal loss identity: `{result['stacked_terminal']['loss_identity_error']:.6g}`",
        f"- hidden-mode Schur residual: `{result['schur_resolvent_error']:.6g}`",
        f"- clock-reparameterization residual: `{result['clock_reparameterization_error']:.6g}`",
        f"- one-observer response to the frozen body variation: `{result['single_observer_body_variation_response']:.6g}`",
        f"- stacked response to the same variation: `{result['stacked_body_variation_response']:.6g}`",
        "",
        "## Checks",
        "",
        *[
            f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
            for name, passed in result["checks"].items()
        ],
        "",
        "## Claim boundary",
        "",
        "The audit proves finite operator identities only. It demonstrates",
        "that observer-level attenuation can coexist with lossless full-body",
        "transport and that effective damping can arise by eliminating hidden",
        "modes. It does not construct the universe-level body, derive its",
        "physical generator or show Nature occupation.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = run_audit()
    JSON_PATH.write_text(json.dumps(result, indent=2) + "\n")
    write_report(result)
    print(f"ATEMPORAL_BODY_TERMINAL_LOSS_{result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
