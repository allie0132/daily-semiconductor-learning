# Electromigration in HBM TSVs: Mechanisms, Models, Test Design

*Friday, Aug 21 2026*

*Module 15.2 — Reliability & Qualification Testing*

## HBM TSV Structure and EM Fundamentals

HBM stacks use high‑aspect‑ratio TSVs (typically 5‑10 µm diameter, 50‑100 µm depth) filled with Cu and lined with barrier/metal stacks such as TiN/TaN or emerging Ru liners. Electromigration drives Cu atom flux from the cathode toward the anode under high current density, leading to void formation at the cathode and hillock growth at the anode. The driving force is the product of current density (J) and effective charge number (Z*), moderated by temperature‑dependent diffusivity.
- Cu diffusivity D = D0·exp(−Ea/kT)- Flux J_Cu = (D·Z*·e·ρ·J)/kT- Critical parameters: J (A/cm²), T (°C), barrier integrity, liner material.

## Failure Mechanisms Specific to TSVs

Unlike planar interconnects, TSVs experience unique stress fields due to thermal mismatch between Si and Cu, and confinement effects that accelerate void nucleation at the bottom electrode. Key mechanisms include:
- Void nucleation at the Cu/Si interface (cathode side) where tensile stress peaks.- Hillock formation at the anode (top Cu surface) driven by compressive stress.- Stress‑induced void migration along the TSV sidewall, especially when barrier layers are thin or discontinuous.- Accelerated failure when current crowding occurs at via edges due to imperfect lithography.

## Acceleration Models for TSV EM

The classic Black’s equation is adapted for TSV geometry: MTTF = (A·J^−n)·exp(Ea/kT), where n≈2 for Cu‑in‑TSV systems but can vary with barrier effectiveness. Recent JEDEC/IEEE work shows a temperature exponent Ea ranging from 0.6–0.9 eV depending on liner material (TiN ~0.7 eV, Ru ~0.85 eV). Current density exponent n can increase to 2.5–3 when sidewall scattering dominates. Acceleration factors are computed as:
AF = (J_use/J_test)^n · exp[(Ea/k)(1/T_use−1/T_test)]
Use of in‑situ resistance monitoring allows extraction of n and Ea from stepwise stress tests.


## ATE Test Design and Stress Methodology

Effective EM qualification requires constant‑current DC stress at elevated temperature (typically 125‑150 °C) while measuring TSV resistance via four‑point Kelvin probes or on‑die monitor structures. Key ATE considerations:
- Current density selection: 1–5 MA/cm² to induce measurable drift within 100‑1000 h.- Temperature control: ±1 °C uniformity across the probe card; use thermal chuck with PID.- Monitoring strategy: periodic resistance read‑outs (every 30 min) to detect >0.5 % shift indicating void growth.- Failure definition: resistance increase >10 % or open‑circuit detection.- Post‑stress analysis: SEM/FIB cross‑section to validate void location.Typical equipment: Keithley 2400 SourceMeter for current biasing, NI PXIe‑4082 for resistance, and a Thermotron thermal chamber.


## Qualification Criteria and Acceptance Limits

JEDEC JESD235C defines HBM reliability targets, including EM‑related TSV lifetime. Acceptance is based on Weibull analysis of time‑to‑failure (TTF) data extracted from accelerated tests, projected to use conditions (e.g., 0.5 MA/cm², 85 °C) using the acceleration model. Required confidence: 90 % lower‑bound TTF > 10 years at use conditions. Additional checks include:
- No hillocks causing shorts to adjacent TSVs (checked by leakage monitoring).- Barrier integrity verified by post‑stress TEM showing no Cu diffusion beyond liner.- Uniformity: σ/μ of extracted TTF < 20 % across wafer.

## Key Takeaways

- EM in HBM TSVs is governed by Cu flux driven by current density and temperature, with void formation at the cathode and hillocks at the anode being dominant failure modes.
- Black’s equation adapts to TSVs with current exponent n≈2–3 and activation energy Ea≈0.6–0.9 eV, highly dependent on barrier/liner materials (TiN, TaN, Ru).
- Qualification relies on constant‑current DC stress at elevated T, resistance monitoring via four‑point probes, and Weibull projection to use‑condition lifetimes using JEDEC‑based acceleration models.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) Device Specification — Section 4.2.3 covers electromigration limits for TSVs and required test methods.
2. **[JEDEC]** JEDEC JESD22‑B101: Electromigration Test Method for Interconnects — Defines constant‑current stress procedures and resistance monitoring applicable to TSV structures.
3. **[IEEE]** S. H. Han et al., "Electromigration in Through‑Silicon Vias for 3D ICs," IEEE Transactions on Device and Materials Reliability, vol. 20, no. 3, pp. 456‑465, Sep. 2020. — Experimental extraction of n=2.3 and Ea=0.72 eV for Cu/TiN TSVs; discusses sidewall scattering effects.
4. **[Book]** E. Peck, Reliability of Microelectronics, 2nd ed., McGraw‑Hill, 2006. — Chapter 7 provides detailed derivation of Black’s equation and its extensions to confined geometries.
5. **[Datasheet]** Samsung Electronics, HBM2E Product Brief, Rev. 1.3, 2022. — Lists typical operating current densities (<1 MA/cm²) and references EM reliability targets per JESD235C.
6. **[IEEE]** A. Raja et al., "Revisiting Black’s Equation for Cu TSVs with Ru Liners," IEEE International Reliability Physics Symposium (IRPS) Proceedings, pp. 1‑6, 2021. — Shows Ru liner raises Ea to 0.85 eV and reduces n to 1.8, improving EM lifetime by >5×.

## 🔍 Additional Learning: Impact of Ru Liners on TSV EM Resistance

Recent studies demonstrate that replacing conventional TiN/TaN barrier stacks with a thin Ru liner (≈5 nm) significantly reduces Cu diffusivity along the sidewall, increasing the activation energy for EM to ~0.85 eV and lowering the current exponent. This modification can extend projected TSV lifetime at use conditions by an order of magnitude, making Ru an attractive candidate for next‑generation HBM3E stacks.
