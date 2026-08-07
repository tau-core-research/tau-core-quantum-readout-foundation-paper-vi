import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

def test_required_files_exist():
    for rel in [
        "paperVI_submission_source/main.tex",
        "paperVI_submission_source/main.pdf",
        "paperVI_submission_source/refs.bib",
        "figures/fig_quantum_descent_spine.pdf",
        "figures/fig_quantum_classical_fork.pdf",
        "figures/fig_no_signalling_instrument.pdf",
        "data/derived/quantum_readout_ledger.json",
        "data/derived/tensor_factorization_audit.json",
        "data/derived/standard_recovery_discriminator_audit.json",
        "data/derived/public_qgt_evidence_audit.json",
        "data/derived/public_carrier_census_audit.json",
        "data/derived/ness2021_qor_control_audit.json",
        "data/derived/two_band_spectral_qgt_independence_audit.json",
        "data/derived/susceptibility_moment_no_go_audit.json",
        "data/derived/local_stiffness_finite_distance_no_go.json",
        "data/derived/endpoint_holonomy_no_go.json",
        "data/derived/alternative_source_census_audit.json",
        "data/derived/joint_qubit_source_model_audit.json",
        "data/derived/alternative_source_readiness_scoring.json",
        "data/derived/resonator_axis_audit.json",
        "data/derived/generalized_force_independence_audit.json",
        "data/derived/public_source_port_candidate_audit.json",
        "data/derived/chdf_body_work_source_audit.json",
        "data/derived/chdf_uhlmann_range_and_selection_audit.json",
        "data/derived/depolarizing_recovery_selector_audit.json",
        "data/derived/protected_logical_recovery_split_audit.json",
        "data/derived/root_commutant_factorization_audit.json",
        "data/derived/root_factor_designation_no_go.json",
        "data/derived/extremal_observer_access_selector_audit.json",
        "data/derived/qubit_terminal_minimality_selector_audit.json",
        "data/derived/observer_noise_commutant_selector_audit.json",
        "data/derived/canonical_expectation_complement_audit.json",
        "data/derived/regular_event_factor_selection_audit.json",
        "data/derived/approximate_factor_selection_bound_audit.json",
        "data/derived/central_chirality_terminal_blindness_audit.json",
        "data/derived/joint_quantum_packet_parent_selection_audit.json",
        "data/derived/isolated_logical_nonleakage_selector_audit.json",
        "data/derived/tau_core_hypergraph_isolation_quantum_protection_audit_v01_summary.json",
        "data/derived/tau_core_disjoint_source_valuation_isolation_audit_v01_summary.json",
        "data/derived/tau_core_empirical_parent_valuation_lift_audit_v01_summary.json",
        "data/derived/future_extension_quantum_carrier_audit.json",
        "data/derived/future_extension_covariant_phase_space_audit.json",
        "data/derived/irreducible_future_mode_scale_lock_audit.json",
        "data/derived/future_root_irreducibility_bridge_audit.json",
        "data/derived/mixed_boundary_future_root_source_audit.json",
        "data/derived/brac_vs_boundary_bridge_activation_audit.json",
        "data/derived/covariant_kinetic_boundary_activation_audit.json",
        "data/derived/record_conditioned_future_fluidity_audit.json",
        "data/derived/bounded_future_possibility_body_audit.json",
        "data/derived/concrete_body_root_rank_eligibility_audit.json",
        "data/derived/naghiloo2020_candidate_scoring.json",
        "data/derived/cottet2017_candidate_scoring.json",
        "data/derived/optical_path_integral_candidate_scoring.json",
        "data/derived/joint_path_data_candidate_audit.json",
        "data/derived/reconstructed_optical_path_morphology_score.json",
        "data/derived/wen_figs2b_phase_control_audit.json",
        "data/derived/published_optical_amplitude_morphology_score.json",
        "data/derived/tau_frozen_path_curvature_candidate_score.json",
        "arxiv_submission_source.zip",
    ]:
        assert (ROOT / rel).exists(), rel

def test_claim_markers():
    tex = (ROOT / "paperVI_submission_source/main.tex").read_text()
    for marker in [
        "Quantum Readout from Observer-Relative Lossy Descent",
        "Inherited proof hierarchy",
        "Loss-only no-go",
        "Metric--symplectic quantum completion",
        "Existing Tau source realization",
        "Separating-record selector",
        "P3 separating-record rank",
        "Ternary spectral-record occupation",
        "Born and interference terminal",
        "Tensor composition and no-signalling",
        "Subsystem-factorization boundary",
        "Measurement, decoherence and the classical limit",
        "Planck action scale",
        "Standard quantum recovery and Tau-specific discriminator",
        "Public-data audit",
        "What is proved and what remains open",
        "Disjoint-source valuation and the isolation theorem",
        "Operational-to-parent two-jet lifting theorem and no-go",
    ]:
        assert marker in tex
    assert "observed Tau quantum anomaly" not in tex

def test_ledger():
    data = json.loads((ROOT / "data/derived/quantum_readout_ledger.json").read_text())
    assert data["proved"]["lossy_quotient_alone_implies_quantum_mechanics"] is False
    assert data["proved"]["metric_symplectic_lock_constructs_complex_structure"] is True
    assert data["proved"]["enriched_MVP_P3_handoff_constructs_single_system_packet"] is True
    assert data["proved"]["separating_record_scalar_action_selects_Clifford_handoff"] is True
    assert data["proved"]["primitive_P3_records_are_separating"] is False
    assert data["proved"]["binary_P3_word_records_are_separating"] is False
    assert data["proved"]["ternary_P3_word_closure_is_separating"] is True
    assert data["proved"]["ternary_P3_spectral_effect_atlas_is_separating"] is True
    assert data["proved"]["frobenius_pointer_copying_alone_is_separating"] is False
    assert data["proved"]["full_S4_effect_interval_plus_S5_terminal_implies_spectral_closure"] is True
    assert data["proved"]["post_handoff_spectral_closure_selects_P3_handoff_noncircularly"] is False
    assert data["proved"]["single_M2_or_pointer_record_selects_three_factor_tensor_structure"] is False
    assert data["proved"]["two_commuting_M2_factors_select_the_third_as_commutant"] is True
    audit = json.loads((ROOT / "data/derived/tensor_factorization_audit.json").read_text())
    assert audit["joint_generated_complex_rank"] == 64
    assert audit["commutant_complex_dimensions_after_1_2_3_factors"] == [16, 4, 1]
    discriminator = json.loads(
        (ROOT / "data/derived/standard_recovery_discriminator_audit.json").read_text()
    )
    assert discriminator["standard_recovery"]["normalized_Born_probabilities"] is True
    assert discriminator["tau_discriminator"]["common_Gram_identity_holds"] is True
    assert discriminator["tau_discriminator"]["standard_QM_alone_entails_x_A_equals_x_Q"] is False
    public = json.loads(
        (ROOT / "data/derived/public_qgt_evidence_audit.json").read_text()
    )
    assert public["identifiability"]["same_carrier_local_quantum_geometry_replicated"] is True
    assert public["identifiability"]["public_data_can_test_x_A_equals_x_Q"] is False
    census = json.loads(
        (ROOT / "data/derived/public_carrier_census_audit.json").read_text()
    )
    assert census["candidate_count"] == 8
    assert census["full_pass_count"] == 0
    assert census["strongest_QOR_control"] == "ness2021_single_atom_qsl"
    ness = json.loads(
        (ROOT / "data/derived/ness2021_qor_control_audit.json").read_text()
    )
    assert ness["total_points"] == 53
    assert ness["standard_QSL_consistent_at_1_96_sigma"] is True
    assert ness["tau_identifiability"]["tests_x_A_equals_x_Q"] is False
    two_band = json.loads(
        (ROOT / "data/derived/two_band_spectral_qgt_independence_audit.json").read_text()
    )
    assert two_band["conclusions"]["spectrum_determines_QGT_in_generic_two_band_family"] is False
    assert two_band["conclusions"]["QGT_determines_spectral_curvature_in_generic_two_band_family"] is False
    moments = json.loads(
        (ROOT / "data/derived/susceptibility_moment_no_go_audit.json").read_text()
    )
    assert moments["conclusions"]["universal_parameter_independent_proportionality"] is False
    assert moments["conclusions"]["additional_source_owned_gap_weighting_required"] is True
    stiffness = json.loads(
        (ROOT / "data/derived/local_stiffness_finite_distance_no_go.json").read_text()
    )
    assert stiffness["conclusions"]["local_stiffness_alone_fixes_finite_chord"] is False
    assert stiffness["conclusions"]["connector_or_extrinsic_transport_required"] is True
    holonomy = json.loads(
        (ROOT / "data/derived/endpoint_holonomy_no_go.json").read_text()
    )
    assert holonomy["max_pairwise_fidelity_difference"] < 1e-12
    assert holonomy["conclusions"]["pairwise_endpoint_distances_fix_loop_holonomy"] is False
    alternatives = json.loads(
        (ROOT / "data/derived/alternative_source_census_audit.json").read_text()
    )
    assert alternatives["candidate_count"] == 6
    assert alternatives["full_pass_count"] == 0
    assert alternatives["strongest_work_tomography_leg"] == "cottet2017_maxwell_demon"
    assert alternatives["strongest_trajectory_resolved_candidate"] == "naghiloo2020_quantum_trajectories"
    joint = json.loads(
        (ROOT / "data/derived/joint_qubit_source_model_audit.json").read_text()
    )
    assert joint["checks"]["closed_state_loop"] is True
    assert joint["checks"]["nontrivial_work_characteristic"] is True
    assert joint["checks"]["nonzero_state_distance"] is True
    assert joint["checks"]["nonzero_uhlmann_phase"] is True
    assert joint["checks"]["unitary_transport"] is True
    assert joint["checks"]["work_is_independent_body_action"] is False
    assert joint["checks"]["one_constant_converts_dissipated_work_to_xQ"] is False
    readiness = json.loads(
        (ROOT / "data/derived/alternative_source_readiness_scoring.json").read_text()
    )
    assert readiness["ranking"][0]["id"] == "zhao2020_xmon_geometric_gate"
    assert readiness["ranking"][0]["score"] == 8
    assert readiness["tau_ready_count"] == 0
    assert readiness["score_is_tau_signal"] is False
    resonator = json.loads(
        (ROOT / "data/derived/resonator_axis_audit.json").read_text()
    )
    assert resonator["candidate_count"] == 7
    assert resonator["independent_measurement_axis_count"] == 1
    assert resonator["independent_xA_axis_count"] == 0
    generalized_force = json.loads(
        (ROOT / "data/derived/generalized_force_independence_audit.json").read_text()
    )
    assert generalized_force["factorization"]["stacked_jacobian_rank_increase_beyond_rho_and_controls"] == 0
    assert generalized_force["adiabatic_response"]["qgt_reconstruction_is_independent_tau_action_axis"] is False
    assert generalized_force["status"] == "STANDARD_GENERALIZED_FORCE_SHORTCUT_CLOSED"
    source_ports = json.loads(
        (ROOT / "data/derived/public_source_port_candidate_audit.json").read_text()
    )
    assert source_ports["candidate_count"] == 3
    assert source_ports["public_raw_packet_count"] == 1
    assert source_ports["independent_source_port_axis_count"] == 0
    assert source_ports["tau_endpoint_eligible_count"] == 0
    body_work = json.loads(
        (ROOT / "data/derived/chdf_body_work_source_audit.json").read_text()
    )
    assert all(body_work["checks"].values())
    assert body_work["proof_levels"]["quantum_connector_and_xA_equals_xQ"] == "not derived by this audit"
    connector = json.loads(
        (ROOT / "data/derived/chdf_uhlmann_range_and_selection_audit.json").read_text()
    )
    assert all(connector["checks"].values())
    assert connector["theorem_status"]["existence"] == "proved for the occupied sector 0 <= x_A <= 2"
    assert connector["theorem_status"]["physical_selection"] == "not implied by positivity, normalization, or CPTP descent"
    recovery_selector = json.loads(
        (ROOT / "data/derived/depolarizing_recovery_selector_audit.json").read_text()
    )
    assert all(recovery_selector["checks"].values())
    assert recovery_selector["theorem_status"]["within_depolarizing_family"] == "exact full-code CPTP recoverability iff gamma=1"
    protected = json.loads(
        (ROOT / "data/derived/protected_logical_recovery_split_audit.json").read_text()
    )
    assert all(protected["checks"].values())
    assert protected["theorem_status"]["A8b_selector_scope"] == "full occupied logical ROOT operator system, not the complete body realization space"
    hypergraph_isolation = json.loads(
        (ROOT / "data/derived/tau_core_hypergraph_isolation_quantum_protection_audit_v01_summary.json").read_text()
    )
    assert all(hypergraph_isolation["checks"].values())
    assert hypergraph_isolation["verdict"].startswith(
        "FULL_SOURCE_HYPERGRAPH_FACTORIZATION_IMPLIES_QUANTUM_PROTECTION"
    )
    source_valuation = json.loads(
        (ROOT / "data/derived/tau_core_disjoint_source_valuation_isolation_audit_v01_summary.json").read_text()
    )
    assert all(source_valuation["checks"].values())
    assert source_valuation["verdict"].startswith(
        "DISJOINT_SOURCE_VALUATION_FORCES_ACTION_ADDITIVITY_AND_ZERO_MIXED_HESSIAN"
    )
    valuation_lift = json.loads(
        (ROOT / "data/derived/tau_core_empirical_parent_valuation_lift_audit_v01_summary.json").read_text()
    )
    assert all(valuation_lift["checks"].values())
    assert valuation_lift["verdict"].startswith(
        "JOINT_TWO_JET_FAITHFULNESS_LIFTS_ZERO_TERMINAL_MIXING"
    )
    root_factor = json.loads(
        (ROOT / "data/derived/root_commutant_factorization_audit.json").read_text()
    )
    assert all(root_factor["checks"].values())
    assert root_factor["joint_generated_dimension"] == 64
    assert root_factor["realization_commutant_dimension"] == 16
    designation = json.loads(
        (ROOT / "data/derived/root_factor_designation_no_go.json").read_text()
    )
    assert all(designation["checks"].values())
    assert designation["factor_orbit_size"] == 3
    assert designation["theorem_status"]["distinguished_ROOT_M2"] == "not selected by the S3-symmetric rooted packet"
    access_selector = json.loads(
        (ROOT / "data/derived/extremal_observer_access_selector_audit.json").read_text()
    )
    assert all(access_selector["checks"].values())
    assert access_selector["theorem_status"]["selector"] == "exact A8b recovery selects a simplex vertex w=e_j, not merely a unique maximum"
    terminal_selector = json.loads(
        (ROOT / "data/derived/qubit_terminal_minimality_selector_audit.json").read_text()
    )
    assert all(terminal_selector["checks"].values())
    assert terminal_selector["status"]["factor_purity_on_occupied_code"] == "derived from exact full-code recovery and qubit-terminal minimality"
    noise_selector = json.loads(
        (ROOT / "data/derived/observer_noise_commutant_selector_audit.json").read_text()
    )
    assert all(noise_selector["checks"].values())
    assert noise_selector["rows"][0]["noise_commutant_dimension"] == 4
    assert noise_selector["rows"][0]["logical_commutant_dimension"] == 16
    expectation = json.loads(
        (ROOT / "data/derived/canonical_expectation_complement_audit.json").read_text()
    )
    assert all(expectation["checks"].values())
    assert expectation["dimensions"]["expectation_kernel"] == 60
    assert expectation["dimensions"]["complement_algebra"] == 16
    event_selector = json.loads(
        (ROOT / "data/derived/regular_event_factor_selection_audit.json").read_text()
    )
    assert all(event_selector["checks"].values())
    assert [row["selected_factor"] for row in event_selector["rows"][2:]] == [0, 1, 2]
    approximate = json.loads(
        (ROOT / "data/derived/approximate_factor_selection_bound_audit.json").read_text()
    )
    assert all(approximate["checks"].values())
    assert approximate["rows"][2]["minimum_selected_weight"] == 0.95
    chirality = json.loads(
        (ROOT / "data/derived/central_chirality_terminal_blindness_audit.json").read_text()
    )
    assert all(chirality["checks"].values())
    assert chirality["status"]["paper_VI_quantum_terminal"] == "blind to central chirality because it is entirely represented in the common six-edge M8 algebra"
    nagh = json.loads(
        (ROOT / "data/derived/naghiloo2020_candidate_scoring.json").read_text()
    )
    assert nagh["capability_score"] == 6
    assert nagh["tau_primary_score_eligible"] is False
    cottet = json.loads(
        (ROOT / "data/derived/cottet2017_candidate_scoring.json").read_text()
    )
    assert cottet["capability_score"] == 7
    assert cottet["independent_measurement_instrument"] is True
    assert cottet["conditional_descriptor_novelty_at_mean_level"] is False
    assert cottet["independent_terminal_energy_axis"] is False
    assert cottet["independent_tau_body_action_axis"] is False
    cottet_fluct = json.loads(
        (ROOT / "data/derived/cottet_fluctuation_novelty_audit.json").read_text()
    )
    assert [row["novelty"] for row in cottet_fluct["rows"][:3]] == [False, True, False]
    assert cottet_fluct["cottet_publication_supports_fluctuation_score"] is False
    public_shot = json.loads(
        (ROOT / "data/derived/public_single_shot_candidate_scoring.json").read_text()
    )
    assert public_shot["eligible_count"] == 0
    assert public_shot["wang_readout_control"]["minimum_midpoint_accuracy"] > 0.995
    assert public_shot["tau_score_eligible"] is False
    optical = json.loads(
        (ROOT / "data/derived/optical_path_integral_candidate_scoring.json").read_text()
    )
    assert abs(optical["standard_controls"]["action_amplitude"]["slope_z"]) < 1.0
    assert optical["standard_controls"]["action_phase"]["raw_rms_phase_pi_units"] < 0.03
    assert optical["identifiability"]["can_test_conditional_morphology_novelty"] is False
    assert optical["identifiability"]["tau_primary_score_eligible"] is False
    joint_paths = json.loads(
        (ROOT / "data/derived/joint_path_data_candidate_audit.json").read_text()
    )
    assert joint_paths["direct_complete_public_count"] == 0
    assert joint_paths["reconstructible_diagnostic_count"] == 1
    assert joint_paths["executed_score"]["candidate"] == "wen2026_raw_propagator_reconstruction"
    reconstructed_paths = json.loads(
        (ROOT / "data/derived/reconstructed_optical_path_morphology_score.json").read_text()
    )
    assert reconstructed_paths["reconstruction"]["paths"] == 17**5
    assert reconstructed_paths["reconstruction"]["shared_radial_kernel_classes"] == 17
    validation = reconstructed_paths["reconstruction"]["FigS1C_validation"]
    assert validation["phase_reconstruction_eligible"] is True
    assert validation["amplitude_reconstruction_eligible"] is False
    assert reconstructed_paths["phase_residual_score"]["shared_kernel_null"]["kernel_permutation_p"] > 0.05
    assert reconstructed_paths["log_amplitude_residual_score"]["eligible_for_physical_interpretation"] is False
    assert reconstructed_paths["status"] == "DIAGNOSTIC_ONLY_NOT_TAU_ENDPOINT"
    figs2b = json.loads(
        (ROOT / "data/derived/wen_figs2b_phase_control_audit.json").read_text()
    )
    assert figs2b["experimental_points"] == 17
    assert figs2b["theory_points"] == 200
    assert figs2b["comparison"]["all_points_within_one_sigma"] is True
    assert figs2b["eligibility"]["tau_primary_score_eligible"] is False
    published_amplitude = json.loads(
        (ROOT / "data/derived/published_optical_amplitude_morphology_score.json").read_text()
    )
    assert published_amplitude["published_packet"]["radial_classes"] == 17
    assert published_amplitude["score"]["delta_r2"] > 0.4
    assert published_amplitude["score"]["shared_kernel_permutation"]["kernel_permutation_p"] < 0.01
    assert published_amplitude["constant_amplitude_uncertainty_null"]["uncertainty_null_p"] < 0.01
    assert published_amplitude["single_class_replacement"]["minimum_delta_r2"] > 0.25
    assert published_amplitude["status"] == "STANDARD_OPTICAL_KERNEL_SIGNAL_NOT_TAU_ENDPOINT"
    frozen_curvature = json.loads(
        (ROOT / "data/derived/tau_frozen_path_curvature_candidate_score.json").read_text()
    )
    assert frozen_curvature["paths"] == 17**5
    assert frozen_curvature["candidate_rank_of_five"] == 4
    assert frozen_curvature["single_descriptor_scores"]["increment_roughness"]["delta_r2"] < 0.001
    assert frozen_curvature["single_descriptor_scores"]["path_length"]["delta_r2"] > 0.45
    assert frozen_curvature["shared_kernel_permutation"]["p_value"] > 0.05
    assert frozen_curvature["status"] == "TAU_CONDITIONAL_DESCRIPTOR_DIAGNOSTIC_NOT_ENDPOINT"
    assert data["proved"]["local_cptp_operations_preserve_remote_marginal"] is True
    selection = json.loads(
        (ROOT / "data/derived/joint_quantum_packet_parent_selection_audit.json").read_text()
    )
    assert selection["verdict"] == "CURRENT_REDUCT_DOES_NOT_ENTAIL_COMPLETE_JOINT_QUANTUM_PACKET"
    assert selection["exact_countermodel"]["rows"][0]["joint_packet_closed"] is True
    assert selection["exact_countermodel"]["rows"][1]["joint_packet_closed"] is False
    assert selection["independent_tensor_nonselection"]["current_parent_selects_full_factor_ledger"] is False
    nonleakage = json.loads(
        (ROOT / "data/derived/isolated_logical_nonleakage_selector_audit.json").read_text()
    )
    assert nonleakage["finite_control"]["classical_repeatability_survives"] is True
    assert nonleakage["finite_control"]["full_coherent_distinguishability_survives"] is False
    assert nonleakage["verdict"] == "ISOLATED_FULL_LOGICAL_NONLEAKAGE_SELECTS_EXACT_RECOVERY"
    future = json.loads(
        (ROOT / "data/derived/future_extension_quantum_carrier_audit.json").read_text()
    )
    assert future["orientation_only_control"]["future_is_larger_from_orientation_and_stiffness_alone"] is False
    assert future["boundary_conditioned_extension_fibers"]["future_fiber_is_strictly_larger"] is True
    assert future["future_carrier"]["metric_positive"] is True
    assert future["future_carrier"]["hessian_alone_supplies_phase_form"] is False
    assert future["future_carrier"]["complex_lock_residual"] < 1e-12
    phase_space = json.loads(
        (ROOT / "data/derived/future_extension_covariant_phase_space_audit.json").read_text()
    )
    assert phase_space["common_variational_source"]["independent_phase_gain_required"] is False
    assert phase_space["finite_certificate"]["polar_complex_lock_residual"] < 1e-12
    assert phase_space["finite_certificate"]["single_scalar_lock_holds"] is False
    assert phase_space["verdict"] == (
        "COMMON_VARIATIONAL_ACTION_REMOVES_INDEPENDENT_PHASE_SOURCE; "
        "UNIVERSAL_SCALAR_ACTION_LOCK_REMAINS_OPEN"
    )
    scale_lock = json.loads(
        (ROOT / "data/derived/irreducible_future_mode_scale_lock_audit.json").read_text()
    )
    assert scale_lock["irreducible_certificate"]["symmetric_commutant_dimension"] == 1
    assert scale_lock["irreducible_certificate"]["scalar_lock_residual"] < 1e-12
    assert scale_lock["reducible_control"]["single_scale"] is False
    root_bridge = json.loads(
        (ROOT / "data/derived/future_root_irreducibility_bridge_audit.json").read_text()
    )
    assert root_bridge["root_certificate"]["symmetric_commutant_dimension"] == 1
    assert root_bridge["bridge_certificate"]["bridge_rank"] == 4
    assert root_bridge["bridge_certificate"]["intertwining_residual"] < 1e-12
    assert root_bridge["equal_reduct_nonselection"]["current_reduct_selects_bridge"] is False
    mixed_source = json.loads(
        (ROOT / "data/derived/mixed_boundary_future_root_source_audit.json").read_text()
    )
    assert mixed_source["source_construction"]["joint_phase_antisymmetric"] is True
    assert mixed_source["source_construction"]["bridge_rank"] == 4
    assert mixed_source["schur_transfer"]["separate_bijectivity_assumption_needed"] is False
    assert mixed_source["equal_reduct_counterpair"]["zero_member_bridge_rank"] == 0
    brac_type = json.loads(
        (ROOT / "data/derived/brac_vs_boundary_bridge_activation_audit.json").read_text()
    )
    assert brac_type["brac_bulk"]["nonzero_on_occupied_nonzero_field"] is True
    assert brac_type["brac_boundary"]["activates_beta_FQ"] is False
    kinetic = json.loads(
        (ROOT / "data/derived/covariant_kinetic_boundary_activation_audit.json").read_text()
    )
    assert kinetic["activation_conditions"]["beta_FQ_nonzero"] is True
    assert kinetic["status"] == "CONDITIONAL_KINETIC_BOUNDARY_ACTIVATION"
    fluidity = json.loads(
        (ROOT / "data/derived/record_conditioned_future_fluidity_audit.json").read_text()
    )
    assert fluidity["formal_packet"]["past_kernel_embeds_in_future_kernel"] is True
    assert fluidity["finite_certificate"]["dimension_gap"] == 7
    assert fluidity["finite_certificate"]["record_rank_on_future_fibre"] == 7
    assert fluidity["controls"]["parent_memory_or_stored_history_used"] is False
    bounded = json.loads(
        (ROOT / "data/derived/bounded_future_possibility_body_audit.json").read_text()
    )
    assert bounded["status"] == "BOUNDED_MORPHOLOGICAL_FUTURE_BODY"
    assert bounded["finite_certificate"]["ellipsoid_volume"] > 0
    assert bounded["finite_certificate"]["finite_resolved_cell_upper_bound"] > 0
    rank_eligibility = json.loads(
        (ROOT / "data/derived/concrete_body_root_rank_eligibility_audit.json").read_text()
    )
    assert rank_eligibility["candidate_audit"]["CHDF_leaf"]["max_algebraic_bridge_rank_if_identified_with_F_plus"] == 3
    assert rank_eligibility["candidate_audit"]["CHDF_leaf"]["max_even_phase_rank"] == 2
    assert rank_eligibility["candidate_audit"]["CHDF_leaf"]["can_support_full_real_rank_four_ROOT_bridge"] is False
    assert rank_eligibility["candidate_audit"]["JCSEL_BRDC_EBRP"]["numerical_beta_rank_currently_evaluable"] is False
    assert "interaction_content_nonperturbative_QFT_and_renormalization_conditions" in data["open"]

def test_arxiv_source_is_source_only():
    with zipfile.ZipFile(ROOT / "arxiv_submission_source.zip") as zf:
        names = zf.namelist()
    assert "main.tex" in names
    assert "refs.bib" in names
    assert "figures/fig_quantum_descent_spine.pdf" in names
    assert "main.pdf" not in names
