# Terrestrial Helium-3 Exergy & Hybrid Cryogenic Extractor Audit (Paper 9)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--5351--446X-green.svg)](https://orcid.org/0009-0003-5351-446X)
[![Portfolio](https://img.shields.io/badge/Portfolio-The%20Matrioska%20Protocol-blueviolet)](https://bruno-olivaes.github.io)

**First-Principles Exergy, Nuclear, and Techno-Economic Audit of Terrestrial Helium-3 Harvesting**  
**Author:** Bruno Luçardo Olivaes (`brunoolivaes@gmail.com`)

---

## Overview

This repository audits non-lunar Helium-3 ($^3\mathrm{He}$) supply routes against the benchmark market price of **USD 2,500/L STP (~USD 18,579/g)** driven by neutron detectors and quantum-computing dilution refrigerators (linking hardware cryogenics to [Paper 4 / Qiskit ZNE](https://github.com/bruno-olivaes/qiskit-lombscargle-zne)):

1. **Coulomb-Stopping Wall in Cold Accelerators:** Proves that $200\text{ keV}$ $\mathrm{D}\text{--}\mathrm{D}$ on solid targets ($Y \sim 10^{-5}$) consumes **$3.55 \times 10^8\text{ kWh/g}$ (USD 17.77M/g electricity)** and requires **$101.4\text{ A}$ ($20.28\text{ MW}$ beam)** for just $1\text{ g/yr}$.
2. **Nuclear Reactor Tritium Capture ($3\text{ GW}_{\text{th}}$):** Quantifies $0.10\text{ excess n/fission} \to 1{,}480\text{ g/yr}$ tritium ($81.0\text{ g/yr}$ $^3\mathrm{He}$ in year 1; $12.32\text{ yr}$ half-life), limited by non-proliferation regulation rather than physics.
3. **Hybrid Quantum Cryogenic Cascade (`25 K` N-Graphene + `1.8 K` MWCNT Superfluid Filter):**
   - Attaches to an existing **$1{,}000\text{ L/day}$ liquid-helium plant** ($2.765 \times 10^8\text{ L STP/yr}$).
   - Cuts parasitic electrical power by **$18.25\times$** (**$9.92\text{ kW}$** vs. **$181.11\text{ kW}$** for direct full-stream $1.8\text{ K}$ filtration).
   - Yields **$372.05\text{ g/yr}$** at **$233.8\text{ kWh/g}$ (USD 11.69/g electricity)** on mantle-enriched helium ($x_0 = 10^{-5}$) and **$5.58\text{ g/yr}$** at **$15{,}586\text{ kWh/g}$ (USD 779.29/g)** on crustal gas-stream helium ($x_0 = 1.5\times 10^{-7}$)—supporting **$2.07$ to $138.25$ transmon dilution refrigerators/yr** per skid.

---

## Reproducibility

```bash
python src/he3_exergy_engine.py
python -m pytest -v
```

Generated artifacts:
- `results/he3_exergy_summary.json`
- `figures/fig1_he3_terrestrial_exergy_audit.pdf` / `.png`
- `manuscript/Paper9_Terrestrial_He3_Exergy_Audit.pdf`

