"""Unit tests for the Terrestrial Helium-3 Exergy and Techno-Economic Audit."""

import math
from pathlib import Path

from src.he3_exergy_engine import (
    audit_accelerator_and_plasma_synthesis,
    audit_hybrid_cryo_cascade,
    audit_quantum_cryo_supply,
    audit_reactor_tritium_decay,
    run_full_he3_audit,
)


def test_coulomb_stopping_wall_for_cold_targets() -> None:
    """Verify beam-target Coulomb-stopping energy exceeds market value by >250x."""
    synth = audit_accelerator_and_plasma_synthesis()
    assert math.isclose(synth["liters_stp_per_g_he3"], 7.4316, abs_tol=1e-2)
    cold = synth["scenarios"][0]
    opt = synth["scenarios"][1]
    frc = synth["scenarios"][2]

    assert cold["kwh_per_g"] > 3.5e8
    assert cold["elec_cost_usd_per_g"] > 1.7e7
    assert cold["beam_current_A_for_1g_yr"] > 100.0
    assert opt["market_cost_ratio"] > 250.0
    assert frc["elec_cost_usd_per_g"] < 1000.0


def test_reactor_tritium_decay_budget() -> None:
    """Verify excess-neutron tritium production and Year-1 3He accumulation."""
    rx = audit_reactor_tritium_decay()
    assert 1400.0 < rx["tritium_g_per_yr"] < 1550.0
    assert math.isclose(rx["decay_fraction_yr1"], 0.05471, abs_tol=1e-4)
    assert 78.0 < rx["he3_yr1_g"] < 85.0


def test_hybrid_cryo_cascade_reduction_and_yield() -> None:
    """Verify >18x cryogenic power savings and sub-$15/g electricity on mantle He."""
    cas = audit_hybrid_cryo_cascade()
    assert cas["power_reduction_factor"] > 18.0
    assert cas["hybrid_total_elec_kW"] < 12.0

    crustal, _, mantle = cas["feedstocks"]
    assert math.isclose(crustal["he3_g_per_yr"], 5.58, abs_tol=0.05)
    assert crustal["hybrid_usd_per_g"] < 900.0
    assert math.isclose(mantle["he3_g_per_yr"], 372.05, abs_tol=0.1)
    assert mantle["hybrid_kwh_per_g"] < 250.0
    assert mantle["hybrid_usd_per_g"] < 15.0


def test_quantum_dilution_fridge_coverage() -> None:
    """Verify annual dilution-refrigerator capacity matches Paper 4 linkage."""
    qs = audit_quantum_cryo_supply()
    cov = qs["skid_coverage_by_feedstock"]
    assert math.isclose(cov["crustal"]["dilution_fridges_per_yr"], 2.07, abs_tol=0.05)
    assert cov["mantle"]["dilution_fridges_per_yr"] > 135.0


def test_end_to_end_artifact_generation(tmp_path: Path) -> None:
    """Verify JSON summary and figures render cleanly."""
    out = run_full_he3_audit(tmp_path)
    assert (tmp_path / "results" / "he3_exergy_summary.json").exists()
    assert (tmp_path / "figures" / "fig1_he3_terrestrial_exergy_audit.pdf").exists()
    assert (tmp_path / "figures" / "fig1_he3_terrestrial_exergy_audit.png").exists()
    assert len(out["figures"]) == 2

