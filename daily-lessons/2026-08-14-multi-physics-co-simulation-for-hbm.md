# Multi-Physics Co-Simulation for HBM

*Friday, Aug 14 2026*

*Module 13.8 — Emerging Technologies & Future Directions*

## EM-Thermal-Mechanical Coupling in HBM

HBM stacks concentrate enormous current densities through microbumps (diameter ~25 µm, pitch 55 µm for HBM2E) and TSVs (diameter ~10 µm, aspect ratio ~8:1), creating a tightly coupled multi-physics environment. Electromigration (EM) in Cu TSVs is governed by Black's equation — `MTTF = A · J<sup>-n</sup> · exp(Ea/kT)` — where current density J and temperature T are inseparable. Joule heating from I²R losses in TSVs (resistivity ~2.1 µΩ·cm for Cu) raises local temperature by 5–15 °C under full HBM3 bandwidth (>819 GB/s), which in turn relaxes yield strength and accelerates EM voiding.
Thermal gradients across the HBM stack drive differential expansion between Si (CTE ~3 ppm/°C), Cu (CTE ~17 ppm/°C), and the oxide liner (CTE ~0.5 ppm/°C). The resulting biaxial stress tensor at TSV sidewalls can exceed 200 MPa during burn-in at 125 °C, approaching the yield limit of electroplated Cu. Accurate co-simulation requires solving Maxwell's equations (for current distribution), the heat equation (for temperature field), and the Navier-Stokes stress equations simultaneously — not sequentially.


## Stress-Induced TSV Failure Mechanisms

Three dominant TSV failure modes emerge from multi-physics loading: **Cu pumping**, **liner delamination**, and **keep-out zone (KOZ) mobility degradation**.
- **Cu pumping**: Repeated thermal cycling (−55 °C to 125 °C) causes Cu to plastically extrude above the TSV due to its higher CTE. Extrusion heights of 100–300 nm have been measured by AFM after 1000 cycles, risking microbump joint failure above the stack.- **Liner delamination**: The SiO₂ or SiN liner between Cu TSV and Si substrate experiences Mode-I fracture when interfacial tensile stress exceeds ~1 J/m² adhesion energy. JEDEC JEP122H classifies this as a stress-corrosion mechanism exacerbated by moisture ingress.- **KOZ mobility degradation**: Compressive stress from TSV CTE mismatch extends 5–8 µm radially into the Si substrate, shifting threshold voltage (ΔVt ~10–30 mV) and degrading carrier mobility by 5–15% in pMOS devices within the KOZ. JEDEC JESD235C recommends a minimum KOZ radius of 8 µm for HBM3 TSV arrays.Stress-induced leakage currents through the TSV liner (SILC) manifest as increased IDD standby current — a measurable parametric signature detectable with `IACC` current monitoring during ATE test at elevated temperature.


## TCAD and FEM Simulation Tools

Technology Computer-Aided Design (TCAD) tools model device physics from first principles. For HBM multi-physics work, the primary platforms are:
- **Synopsys Sentaurus TCAD**: Solves drift-diffusion and hydrodynamic transport equations. The `Sdevice` tool incorporates piezoresistivity models (Kanda's coefficients for Si) to quantify mobility change under TSV-induced stress tensor components σ_xx, σ_yy, σ_xy.- **Silvaco ATLAS + VICTORY Stress**: Coupled electro-mechanical solver that maps FEM stress fields into ATLAS device simulations; useful for modeling SILC in thermally stressed TSV oxide liners.- **ANSYS Mechanical + HFSS**: Industry-standard FEM for thermal-mechanical analysis. HFSS extracts S-parameters of TSV arrays at HBM signal frequencies (up to 8 Gbps per pin for HBM3); Mechanical imports Joule heating maps as thermal loads for creep and fatigue analysis.- **Cadence Sigrity PowerSI**: Power integrity co-simulation that couples PDN impedance with thermal resistance networks, generating frequency-dependent TSV impedance matrices (Z-parameters) under thermal loading.TCAD calibration requires TEM cross-sections, XRD residual stress measurements, and SIMS dopant profiles. Uncalibrated models carry ±30% error on EM lifetime predictions.


## Multi-Physics Co-Simulation Workflow

A production-quality multi-physics flow for HBM TSV reliability follows a tightly coupled loop rather than a linear chain:
- **Step 1 — EM extraction**: Extract TSV and microbump current density maps from HFSS or StarRC under worst-case I/O switching (all 128 data pins switching simultaneously, worst-case SSO pattern). Peak J in TSV Cu typically reaches 5×10⁵ A/cm² at HBM3 data rates.- **Step 2 — Thermal solution**: Import Joule heating (W/µm³) into ANSYS Fluent or PrimeThermal. Boundary conditions: 85 °C junction via JEDEC JESD51-1 still-air or 25 °C liquid-cooled for HPC. Solve for 3D T(x,y,z) field across 12-die HBM3E stack.- **Step 3 — Mechanical stress**: Apply ΔT as thermal load in ANSYS Mechanical. Material properties: Cu (E=120 GPa, ν=0.34, CTE=17 ppm/°C), Si (E=130 GPa anisotropic, CTE=2.6 ppm/°C), SiO₂ liner (E=70 GPa, CTE=0.5 ppm/°C). Extract σ_von_Mises at TSV sidewalls and liner interface.- **Step 4 — TCAD feedback**: Map stress tensor back into Sentaurus Sdevice to compute piezoresistivity-corrected TSV resistance (ΔR/R ≈ 0.5–2% under full thermal load), then re-run EM extraction. Iterate until convergence (typically 2–3 cycles).- **Step 5 — Reliability projection**: Feed converged J and T distributions into EM lifetime model, Coffin-Manson fatigue model for Cu pumping (N_f = C · ΔεP^-β, β≈0.6 for electroplated Cu), and fracture mechanics model for liner delamination.

## Test Engineering Implications

Multi-physics simulation results directly inform ATE test strategy for HBM screening and qualification:
- **Stress screening**: Burn-in at 125 °C with full I/O activity targets Cu pumping and liner delamination within the first 100–500 hours (infant mortality regime per JEDEC JEP122H Weibull analysis). HTOL (High-Temperature Operating Life) at 125 °C for 1000 h per JEDEC JESD47 screens for EM-induced opens.- **TSV resistance monitoring**: 4-wire (Kelvin) TSV resistance measurement at ATE resolves ΔR as small as 0.1 mΩ, enabling detection of stress-induced resistance shift before catastrophic open. Teradyne UltraFlex and Advantest T2000 support Kelvin-connect modes for this measurement.- **Temperature-dependent parametric test**: IDD current measured at −10 °C, 25 °C, and 85 °C reveals TSV liner leakage (SILC) by its superlinear temperature dependence — unlike bulk leakage which follows Arrhenius cleanly. A ΔI > 50 µA across this range flags potential SILC.- **Pattern sensitivity**: Worst-case SSO (Simultaneous Switching Output) patterns that maximize di/dt in the PDN should be used during burn-in; simulation identifies the highest-J patterns. JEDEC JESD235C Appendix A provides recommended HBM3 test patterns that correlate with peak TSV stress.- **Post-stress parametric shift**: Compare AC timing margins (tRCD, tCL, tRP) before and after HTOL. A multi-physics model predicts which timing paths are most affected by KOZ Vt shift — paths through memory array periphery close to TSV columns.

## Key Takeaways

- EM-thermal-mechanical coupling in HBM TSVs requires fully coupled (not sequential) multi-physics simulation to accurately predict reliability under >819 GB/s bandwidth loading
- Cu pumping, liner delamination, and KOZ carrier mobility degradation are the three primary stress-induced TSV failure mechanisms, each with distinct ATE-detectable signatures
- TCAD calibration to TEM/XRD/SIMS data is mandatory — uncalibrated models carry ±30% EM lifetime prediction error; converged multi-physics loops require 2–3 EM-thermal-mechanical-TCAD iterations

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) Standard — JESD235C, 2022 — Section 4.5 TSV Requirements, Annex A Test Patterns
2. **[JEDEC]** Failure Mechanisms and Models for Semiconductor Devices — JEP122H, 2016 — Section 3.1 Electromigration, Section 4.4 Stress-Corrosion Cracking
3. **[IEEE]** Electromigration Reliability of Cu TSVs for 3D IC Integration — Lau, J.H. et al., IEEE Trans. Components Packag. Manuf. Technol., vol. 5, no. 8, 2015
4. **[Paper]** Piezoresistivity Effects in Silicon near TSVs: TCAD Modeling — Selvanayagam, C.S. et al., IEEE Trans. Electron Devices, vol. 56, no. 8, pp. 1527–1535, 2009
5. **[Datasheet]** Sentaurus Device User Guide — Synopsys, Version T-2022.03 — Chapter 14: Stress and Piezoresistivity Models
6. **[JEDEC]** JEDEC Standard: Reliability Test Method for Semiconductor Devices — JESD47K, 2020 — HTOL Test Conditions for Advanced Packaging

## Additional Learning: Compact Thermal Resistance Networks for Real-Time TSV Monitoring

Advanced HBM3E controllers are beginning to incorporate on-die thermal sensors within 20 µm of TSV arrays, feeding compact RC thermal network models (CTMs) that estimate real-time TSV temperatures without full FEM re-simulation. These CTMs, calibrated against multi-physics simulation, enable dynamic power throttling when predicted TSV junction temperature exceeds a programmable threshold — extending field reliability without conservative static derating. The JEDEC HBM3E addendum (2023 draft) includes a ThermalSensor register interface that exposes these per-DRAM-die temperature readings to the host via the PHY management bus.
