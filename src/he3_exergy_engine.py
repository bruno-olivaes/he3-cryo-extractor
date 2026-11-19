"""
First-Principles Thermodynamic, Nuclear, and Exergy Audit of Terrestrial Helium-3
Production and Cryogenic Harvesting Routes.

Connects:
  - Geochemical mantle/crustal Helium-3 fluxes (Olson & Sharp, 2022)
  - Stage 1: Cryogenic N-functionalized nanoporous graphene quantum sieving (Hauser & Schwerdtfeger, 2012)
  - Stage 2: Superfluid 4He MWCNT entropy filtration below T_lambda = 2.1768 K (Niechcial et al., 2021)
  - Contrast against beam-target Coulomb-stopping barriers, D-D plasma breeding,
    fission tritium decay, and quantum dilution-refrigerator supply demand (Paper 4).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Fundamental Physical & Market Constants (CODATA / Standard STP)
# ---------------------------------------------------------------------------

AVOGADRO = 6.02214076e23          # mol^-1
M_HE3_G_MOL = 3.0160293           # g/mol
M_HE4_G_MOL = 4.00260325          # g/mol
M_TRITIUM_G_MOL = 3.01604928      # g/mol
R_GAS = 8.314462618               # J/(mol K)
MOLAR_VOL_STP_L = 22.4139695      # L/mol at 273.15 K, 1 atm
EV_TO_J = 1.602176634e-19
J_PER_KWH = 3.6e6
SEC_PER_YEAR = 365.25 * 86400.0
HOURS_PER_YEAR = 365.25 * 24.0

ATOMS_PER_G_HE3 = AVOGADRO / M_HE3_G_MOL                 # 1.99671e23 atoms/g
GRAMS_PER_L_STP_HE3 = M_HE3_G_MOL / MOLAR_VOL_STP_L      # 0.13456 g/L
LITERS_STP_PER_G_HE3 = 1.0 / GRAMS_PER_L_STP_HE3         # 7.4316 L/g

MARKET_PRICE_USD_PER_L_STP = 2500.0
MARKET_PRICE_USD_PER_G = MARKET_PRICE_USD_PER_L_STP / GRAMS_PER_L_STP_HE3  # ~18,579 USD/g
ELEC_PRICE_USD_PER_KWH = 0.05

T_AMBIENT_K = 300.0
T_LAMBDA_HE4_K = 2.1768
L_STP_PER_L_LIQ_HE = 757.0
RHO_LIQ_HE_G_PER_L = 125.0


def audit_accelerator_and_plasma_synthesis() -> dict[str, Any]:
    """
    Quantify the Coulomb-stopping electricity barrier for beam-target D-D synthesis
    vs. recirculating hot-plasma D-D breeding.
    """
    scenarios = [
        {
            "name": "Cold solid-target D-D (200 keV, Y=1e-5)",
            "key": "cold_target_200keV",
            "energy_keV": 200.0,
            "wall_eff": 0.50,
            "yield_he3_per_ion": 1.0e-5,
        },
        {
            "name": "Optimistic beam-target D-D (300 keV, Y=5e-5)",
            "key": "optimistic_target_300keV",
            "energy_keV": 300.0,
            "wall_eff": 0.50,
            "yield_he3_per_ion": 5.0e-5,
        },
        {
            "name": "Recirculating hot-plasma D-D (50 keV, Y_eff=0.05)",
            "key": "recirculating_plasma_dd",
            "energy_keV": 50.0,
            "wall_eff": 0.50,
            "yield_he3_per_ion": 0.05,
        },
    ]

    results: list[dict[str, float | str]] = []
    atoms_per_s_for_1g_yr = ATOMS_PER_G_HE3 / SEC_PER_YEAR

    for sc in scenarios:
        e_elec_per_atom_j = (sc["energy_keV"] * 1.0e3 * EV_TO_J) / (
            sc["wall_eff"] * sc["yield_he3_per_ion"]
        )
        kwh_per_g = (e_elec_per_atom_j * ATOMS_PER_G_HE3) / J_PER_KWH
        elec_usd_per_g = kwh_per_g * ELEC_PRICE_USD_PER_KWH
        ions_per_s = atoms_per_s_for_1g_yr / sc["yield_he3_per_ion"]
        beam_current_a = ions_per_s * EV_TO_J
        beam_power_mw = beam_current_a * sc["energy_keV"] * 1.0e3 / 1.0e6
        results.append({
            "key": sc["key"],
            "name": sc["name"],
            "energy_keV": sc["energy_keV"],
            "yield_he3_per_ion": sc["yield_he3_per_ion"],
            "kwh_per_g": round(kwh_per_g, 1),
            "elec_cost_usd_per_g": round(elec_usd_per_g, 2),
            "beam_current_A_for_1g_yr": round(beam_current_a, 3),
            "beam_power_MW_for_1g_yr": round(beam_power_mw, 3),
            "market_cost_ratio": round(elec_usd_per_g / MARKET_PRICE_USD_PER_G, 2),
        })

    return {
        "atoms_per_g_he3": ATOMS_PER_G_HE3,
        "liters_stp_per_g_he3": round(LITERS_STP_PER_G_HE3, 4),
        "market_price_usd_per_L_stp": MARKET_PRICE_USD_PER_L_STP,
        "market_price_usd_per_g": round(MARKET_PRICE_USD_PER_G, 2),
        "scenarios": results,
    }


def audit_reactor_tritium_decay() -> dict[str, Any]:
    """
    Evaluate 3He yield from parasitic neutron capture (0.10 excess n/fission)
    in a 3.0 GW_th (1.0 GW_e) fission reactor via 6Li(n,alpha)3H / CANDU pathways.
    """
    thermal_power_w = 3.0e9
    energy_per_fission_j = 200.0e6 * EV_TO_J
    excess_n_per_fission = 0.10
    half_life_yr = 12.32

    fissions_per_s = thermal_power_w / energy_per_fission_j
    n_excess_per_s = excess_n_per_fission * fissions_per_s
    tritium_g_per_yr = (n_excess_per_s * SEC_PER_YEAR / AVOGADRO) * M_TRITIUM_G_MOL

    decay_frac_yr1 = 1.0 - math.exp(-math.log(2.0) / half_life_yr)
    he3_g_yr1 = tritium_g_per_yr * decay_frac_yr1 * (M_HE3_G_MOL / M_TRITIUM_G_MOL)
    he3_l_stp_yr1 = he3_g_yr1 * LITERS_STP_PER_G_HE3
    he3_g_steady = tritium_g_per_yr * (M_HE3_G_MOL / M_TRITIUM_G_MOL)

    return {
        "reactor_thermal_gw": 3.0,
        "excess_n_per_fission": excess_n_per_fission,
        "tritium_g_per_yr": round(tritium_g_per_yr, 1),
        "decay_fraction_yr1": round(decay_frac_yr1, 5),
        "he3_yr1_g": round(he3_g_yr1, 1),
        "he3_yr1_L_stp": round(he3_l_stp_yr1, 1),
        "he3_steady_state_g_per_yr": round(he3_g_steady, 1),
    }


def _reversible_mixing_kwh_per_g(x_he3: float) -> float:
    """Ideal isothermal reversible work W_min = R*T0*(1 - ln(x_he3)) per mole at x << 1."""
    w_j_per_mol = R_GAS * T_AMBIENT_K * (1.0 - math.log(x_he3))
    w_j_per_g = w_j_per_mol / M_HE3_G_MOL
    return w_j_per_g / J_PER_KWH


def audit_hybrid_cryo_cascade() -> dict[str, Any]:
    """
    Model a parasitic two-stage quantum separation skid attached to an existing
    1,000 L/day liquid-helium cryo-plant:
      - Direct full-stream 1.8 K MWCNT superfluid filtration (baseline comparison)
      - Hybrid Stage 1 (T1 = 25 K N-graphene sieve, 20x pre-concentration)
        + Stage 2 (T2 = 1.8 K MWCNT superfluid entropy filter on 5% slipstream).
    """
    lhe_liters_per_day = 1000.0
    v_gas_stp_per_yr = lhe_liters_per_day * 365.25 * L_STP_PER_L_LIQ_HE
    m_dot_he_g_s = (lhe_liters_per_day * RHO_LIQ_HE_G_PER_L) / 86400.0  # 1.4468 g/s

    # Cryogenic Carnot + engineering figure of merit (FOM)
    t_sf_k = 1.8
    fom_1_8k = 0.072  # realistic sub-lambda superfluid cryoplant FOM (~7.2% of Carnot)
    w_elec_per_w_1_8k = (T_AMBIENT_K - t_sf_k) / (fom_1_8k * t_sf_k)

    # Cooling 4.2 K -> 1.8 K enthalpy (~11.2 J/g) + fountain heat-flush flux (~28 J/g) + cryostat leak
    enthalpy_and_flush_j_per_g = 11.2 + 28.0
    q_direct_1_8k_w = m_dot_he_g_s * enthalpy_and_flush_j_per_g + 22.0
    p_direct_kw = (q_direct_1_8k_w * w_elec_per_w_1_8k) / 1000.0
    e_direct_kwh_yr = p_direct_kw * HOURS_PER_YEAR

    # Hybrid Stage 1 (T1 = 25 K nanoporous graphene sieve inside cold-box slipstream)
    pre_conc_factor = 20.0
    split_frac = 1.0 / pre_conc_factor
    t_gr_k = 25.0
    fom_25k = 0.15
    w_elec_per_w_25k = (T_AMBIENT_K - t_gr_k) / (fom_25k * t_gr_k)

    # Ambient permeate delta-P recompression + small 25 K cold-box thermal intercept (15 W)
    n_dot_he = m_dot_he_g_s / M_HE4_G_MOL
    p_recomp_ambient_w = (n_dot_he * R_GAS * T_AMBIENT_K * math.log(2.5)) / 0.72
    p_stage1_25k_kw = (p_recomp_ambient_w + 15.0 * w_elec_per_w_25k) / 1000.0

    # Hybrid Stage 2 (1.8 K MWCNT superfluid filter on only 1/20th mass stream + micro-cryostat 1.5 W)
    q_hybrid_1_8k_w = (m_dot_he_g_s * split_frac) * (11.2 + 28.0) + 0.50
    p_stage2_1_8k_kw = (q_hybrid_1_8k_w * w_elec_per_w_1_8k) / 1000.0

    p_hybrid_kw = p_stage1_25k_kw + p_stage2_1_8k_kw
    e_hybrid_kwh_yr = p_hybrid_kw * HOURS_PER_YEAR
    power_reduction_factor = e_direct_kwh_yr / e_hybrid_kwh_yr

    feedstocks = [
        {"key": "crustal", "name": "Crustal natural-gas He (1.5e-7)", "x_he3": 1.5e-7},
        {"key": "atmospheric", "name": "Atmospheric He (1.38e-6)", "x_he3": 1.38e-6},
        {"key": "mantle", "name": "Mantle/geothermal-enriched He (1.0e-5)", "x_he3": 1.0e-5},
    ]

    streams: list[dict[str, Any]] = []
    for fs in feedstocks:
        l_stp_yr = v_gas_stp_per_yr * fs["x_he3"]
        g_yr = l_stp_yr * GRAMS_PER_L_STP_HE3
        rev_usd_yr = l_stp_yr * MARKET_PRICE_USD_PER_L_STP
        w_min_kwh_g = _reversible_mixing_kwh_per_g(fs["x_he3"])
        hybrid_kwh_g = e_hybrid_kwh_yr / g_yr
        hybrid_usd_g = hybrid_kwh_g * ELEC_PRICE_USD_PER_KWH
        direct_kwh_g = e_direct_kwh_yr / g_yr
        direct_usd_g = direct_kwh_g * ELEC_PRICE_USD_PER_KWH
        streams.append({
            "key": fs["key"],
            "name": fs["name"],
            "x_he3": fs["x_he3"],
            "he3_L_stp_per_yr": round(l_stp_yr, 2),
            "he3_g_per_yr": round(g_yr, 2),
            "annual_market_value_usd": round(rev_usd_yr, 2),
            "gibbs_min_exergy_kwh_per_g": round(w_min_kwh_g, 5),
            "direct_1_8K_kwh_per_g": round(direct_kwh_g, 1),
            "direct_1_8K_usd_per_g": round(direct_usd_g, 2),
            "hybrid_kwh_per_g": round(hybrid_kwh_g, 1),
            "hybrid_usd_per_g": round(hybrid_usd_g, 2),
            "margin_over_elec_ratio": round(MARKET_PRICE_USD_PER_G / hybrid_usd_g, 1),
        })

    return {
        "plant_lhe_L_per_day": lhe_liters_per_day,
        "gas_throughput_L_stp_per_yr": round(v_gas_stp_per_yr, 1),
        "mass_flow_g_per_s": round(m_dot_he_g_s, 4),
        "pre_concentration_factor": pre_conc_factor,
        "direct_1_8K_cold_W": round(q_direct_1_8k_w, 2),
        "direct_1_8K_elec_kW": round(p_direct_kw, 2),
        "direct_1_8K_kwh_per_yr": round(e_direct_kwh_yr, 1),
        "hybrid_stage1_25K_elec_kW": round(p_stage1_25k_kw, 2),
        "hybrid_stage2_1_8K_cold_W": round(q_hybrid_1_8k_w, 2),
        "hybrid_stage2_1_8K_elec_kW": round(p_stage2_1_8k_kw, 2),
        "hybrid_total_elec_kW": round(p_hybrid_kw, 2),
        "hybrid_kwh_per_yr": round(e_hybrid_kwh_yr, 1),
        "power_reduction_factor": round(power_reduction_factor, 2),
        "feedstocks": streams,
    }


def audit_quantum_cryo_supply() -> dict[str, Any]:
    """
    Benchmark harvested 3He output against superconducting quantum computer
    dilution-refrigerator inventories (20 L STP = 2.69 g per 10-20 mK cryostat, Paper 4 link).
    """
    dr_inventory_L_stp = 20.0
    dr_inventory_g = dr_inventory_L_stp * GRAMS_PER_L_STP_HE3
    cascade = audit_hybrid_cryo_cascade()

    coverage = {}
    for fs in cascade["feedstocks"]:
        systems_per_yr = fs["he3_L_stp_per_yr"] / dr_inventory_L_stp
        coverage[fs["key"]] = {
            "dilution_fridges_per_yr": round(systems_per_yr, 2),
            "inventory_cost_usd_per_fridge": round(dr_inventory_L_stp * MARKET_PRICE_USD_PER_L_STP, 2),
        }

    return {
        "dilution_fridge_charge_L_stp": dr_inventory_L_stp,
        "dilution_fridge_charge_g": round(dr_inventory_g, 3),
        "skid_coverage_by_feedstock": coverage,
    }


def generate_exergy_figure(out_dir: str | Path) -> list[str]:
    """Generate 4-panel first-principles exergy and supply comparison figure."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    synth = audit_accelerator_and_plasma_synthesis()
    cascade = audit_hybrid_cryo_cascade()
    qsupply = audit_quantum_cryo_supply()

    plt.rcParams.update({
        "font.size": 9.3,
        "axes.titlesize": 10.3,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.3,
        "legend.fontsize": 7.8,
    })

    fig, axes = plt.subplots(2, 2, figsize=(11.8, 8.7), constrained_layout=True)

    # Panel (a): Electricity Cost per Gram across Routes (Log Scale vs Market Value)
    ax = axes[0, 0]
    labels_a = [
        "Cold Target D-D\n(200 keV)",
        "Opt. Target D-D\n(300 keV)",
        "Hot FRC Plasma\n(D-D Q~1)",
        "Hybrid Cryo\n(Crustal He)",
        "Hybrid Cryo\n(Mantle He)",
    ]
    costs_a = [
        synth["scenarios"][0]["elec_cost_usd_per_g"],
        synth["scenarios"][1]["elec_cost_usd_per_g"],
        synth["scenarios"][2]["elec_cost_usd_per_g"],
        cascade["feedstocks"][0]["hybrid_usd_per_g"],
        cascade["feedstocks"][2]["hybrid_usd_per_g"],
    ]
    colors_a = ["#dc2626", "#f97316", "#2563eb", "#0891b2", "#16a34a"]
    bars = ax.bar(np.arange(len(labels_a)), costs_a, color=colors_a, width=0.58)
    ax.axhline(MARKET_PRICE_USD_PER_G, color="#0f172a", linestyle="--", linewidth=1.6,
               label=f"3He Market (USD 2,500/L = USD {MARKET_PRICE_USD_PER_G:,.0f}/g)")
    ax.set_yscale("log")
    ax.set_ylim(3.0, 1.5e8)
    ax.set_xticks(np.arange(len(labels_a)))
    ax.set_xticklabels(labels_a, fontsize=8)
    ax.set_ylabel("Electricity Cost per Gram [USD/g]")
    ax.set_title("(a) Coulomb-Stopping Wall vs. Hybrid Cryo Harvesting")
    for b, val in zip(bars, costs_a):
        txt = f"${val/1e6:.1f}M" if val >= 1e6 else f"${val:,.0f}" if val >= 100 else f"${val:.2f}"
        ax.text(b.get_x() + b.get_width() / 2, val * 1.35, txt, ha="center", va="bottom", fontsize=7.8, fontweight="bold")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(axis="y", alpha=0.25)

    # Panel (b): Stage 1 + Stage 2 Power Breakdown (Direct 1.8K vs Hybrid 25K+1.8K)
    ax = axes[0, 1]
    x_b = np.array([0, 1])
    p_s1 = np.array([0.0, cascade["hybrid_stage1_25K_elec_kW"]])
    p_s2 = np.array([cascade["direct_1_8K_elec_kW"], cascade["hybrid_stage2_1_8K_elec_kW"]])
    ax.bar(x_b, p_s2, width=0.46, color="#2563eb", label="Stage 2: 1.8 K MWCNT Superfluid Filter")
    ax.bar(x_b, p_s1, width=0.46, bottom=p_s2, color="#10b981", label="Stage 1: 25 K N-Graphene Quantum Sieve")
    ax.set_xticks(x_b)
    ax.set_xticklabels(["Direct 1.8 K\nFull 1,000 L/d Stream", "Hybrid 25 K + 1.8 K\n(20x Slipstream)"])
    ax.set_ylabel("Parasitic Electric Power [kW]")
    ax.set_title(f"(b) Cryogenic Power Drop: {cascade['power_reduction_factor']:.2f}x Savings")
    ax.set_ylim(0, cascade["direct_1_8K_elec_kW"] * 1.18)
    ax.text(0, cascade["direct_1_8K_elec_kW"] + 4, f"{cascade['direct_1_8K_elec_kW']:.1f} kW", ha="center", fontweight="bold")
    ax.text(1, cascade["hybrid_total_elec_kW"] + 4, f"{cascade['hybrid_total_elec_kW']:.1f} kW", ha="center", fontweight="bold", color="#065f46")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(axis="y", alpha=0.25)

    # Panel (c): Scaling of Annual 3He Yield & Revenue vs Feedstock Concentration
    ax = axes[1, 0]
    x_grid = np.logspace(-7, -4.7, 200)
    g_yr_curve = cascade["gas_throughput_L_stp_per_yr"] * x_grid * GRAMS_PER_L_STP_HE3
    ax.loglog(x_grid, g_yr_curve, color="#0f172a", linewidth=2.0, label="1,000 L/d LHe Loop Yield [g/yr]")
    fs_cols = ["#0891b2", "#7c3aed", "#16a34a"]
    for fs, col in zip(cascade["feedstocks"], fs_cols):
        ax.scatter([fs["x_he3"]], [fs["he3_g_per_yr"]], color=col, s=60, zorder=5,
                   label=f"{fs['key'].title()}: {fs['he3_g_per_yr']:.1f} g/yr (${fs['annual_market_value_usd']/1e3:,.0f}k/yr)")
    ax.set_xlabel("Feedstock Isotope Fraction $x_0 = {^3\\mathrm{He}}/{^4\\mathrm{He}}$")
    ax.set_ylabel("Annual Harvested $^3\\mathrm{He}$ [g/yr]")
    ax.set_title("(c) Terrestrial Yield vs. Geochemical Concentration")
    ax.legend(loc="upper left", frameon=True)
    ax.grid(True, which="both", alpha=0.22)

    # Panel (d): Superconducting Transmon Dilution Fridges Supplied per Skid (Paper 4 Link)
    ax = axes[1, 1]
    keys_d = ["Crustal He\n(1.5e-7)", "Atmospheric He\n(1.38e-6)", "Mantle He\n(1.0e-5)"]
    fridges_d = [
        qsupply["skid_coverage_by_feedstock"]["crustal"]["dilution_fridges_per_yr"],
        qsupply["skid_coverage_by_feedstock"]["atmospheric"]["dilution_fridges_per_yr"],
        qsupply["skid_coverage_by_feedstock"]["mantle"]["dilution_fridges_per_yr"],
    ]
    bars_d = ax.bar(np.arange(3), fridges_d, color=fs_cols, width=0.52)
    ax.set_yscale("log")
    ax.set_ylim(0.5, 450.0)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(keys_d, fontsize=8.5)
    ax.set_ylabel("Quantum Dilution Fridges / yr (20 L STP each)")
    ax.set_title("(d) Transmon Qubit Cryostat Capacity per Skid (Paper 4 Link)")
    for b, val in zip(bars_d, fridges_d):
        ax.text(b.get_x() + b.get_width() / 2, val * 1.25, f"{val:.1f}/yr", ha="center", fontweight="bold", fontsize=8.5)
    ax.grid(axis="y", alpha=0.25)

    saved: list[str] = []
    for ext in ("pdf", "png"):
        target = out_path / f"fig1_he3_terrestrial_exergy_audit.{ext}"
        fig.savefig(target, dpi=220)
        saved.append(str(target))
    plt.close(fig)
    return saved


def run_full_he3_audit(base_dir: str | Path | None = None) -> dict[str, Any]:
    """Execute full terrestrial Helium-3 audit and optionally write JSON and figures."""
    summary = {
        "accelerator_and_plasma_synthesis": audit_accelerator_and_plasma_synthesis(),
        "reactor_tritium_decay": audit_reactor_tritium_decay(),
        "hybrid_cryo_cascade": audit_hybrid_cryo_cascade(),
        "quantum_cryo_supply": audit_quantum_cryo_supply(),
    }
    if base_dir is not None:
        root = Path(base_dir)
        res_dir = root / "results"
        res_dir.mkdir(parents=True, exist_ok=True)
        with open(res_dir / "he3_exergy_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        summary["figures"] = generate_exergy_figure(root / "figures")
    return summary


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    out = run_full_he3_audit(repo_root)
    print("Direct 1.8K kW:", out["hybrid_cryo_cascade"]["direct_1_8K_elec_kW"])
    print("Hybrid 25K+1.8K kW:", out["hybrid_cryo_cascade"]["hybrid_total_elec_kW"])
    print("Power reduction:", out["hybrid_cryo_cascade"]["power_reduction_factor"], "x")
    for fs in out["hybrid_cryo_cascade"]["feedstocks"]:
        print(fs["key"], fs["he3_g_per_yr"], "g/yr |", fs["hybrid_kwh_per_g"], "kWh/g | $", fs["hybrid_usd_per_g"], "/g")
