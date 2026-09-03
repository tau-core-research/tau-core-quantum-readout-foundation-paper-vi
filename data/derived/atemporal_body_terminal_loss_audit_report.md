# Tau Core atemporal-body terminal-loss audit v0.1

Status: **PASS**

One self-adjoint finite body generator produces unitary full
occurrence transport. Observer access is nevertheless strictly lossy
because it is a contractive compression. Hidden-mode elimination is
checked independently through the exact Schur resolvent.

## Key residuals

- self-adjoint residual: `0`
- full unitarity residual: `5.10387e-16`
- single-terminal loss identity: `3.73049e-16`
- stacked-terminal loss identity: `3.72829e-16`
- hidden-mode Schur residual: `1.03107e-15`
- clock-reparameterization residual: `9.6782e-16`
- one-observer response to the frozen body variation: `3.15548e-16`
- stacked response to the same variation: `0.359913`

## Checks

- `body_generator_is_self_adjoint`: **PASS**
- `full_occurrence_transport_is_unitary`: **PASS**
- `single_terminal_loss_identity`: **PASS**
- `stacked_terminal_loss_identity`: **PASS**
- `loss_defects_are_positive`: **PASS**
- `observer_transfer_is_strictly_contractive`: **PASS**
- `hidden_mode_schur_resolvent_is_exact`: **PASS**
- `hidden_self_energy_is_passive`: **PASS**
- `clock_reparameterization_preserves_transport`: **PASS**
- `different_terminals_read_different_body_fractions`: **PASS**
- `one_observer_can_miss_a_nonzero_body_variation`: **PASS**
- `stacked_observer_detects_that_body_variation`: **PASS**
- `benchmark_contains_no_tau_residual`: **PASS**

## Claim boundary

The audit proves finite operator identities only. It demonstrates
that observer-level attenuation can coexist with lossless full-body
transport and that effective damping can arise by eliminating hidden
modes. It does not construct the universe-level body, derive its
physical generator or show Nature occupation.
