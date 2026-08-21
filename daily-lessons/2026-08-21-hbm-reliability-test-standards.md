# HBM Reliability Test Standards

*Friday, Aug 21 2026*

*Module 15.1 — Reliability & Qualification Testing*

## Overview of JEDEC Reliability Standards for HBM

**JEDEC JEP122H** (*Failure Mechanisms and Models for Silicon Semiconductor Devices*) catalogues the physical failure modes that govern HBM qualification: electromigration (EM) in TSV landing pads and microbumps, time-dependent dielectric breakdown (TDDB) in inter-layer dielectrics, hot-carrier injection (HCI) in the logic base die, and stress-migration in Cu TSV fill. Every reliability screen for HBM must trace its test conditions to a JEP122 mechanism and an acceleration model.
**JEDEC JEP148B** (*Reliability Qualification Standards for Packaged Multichip Modules*) provides the overarching qualification framework for multi-die packages including 2.5D and 3D stacks. It mandates a Bill of Reliability (BoR) — a table mapping each identified failure mechanism to a test vehicle, test condition, sample size, and acceptance criterion. For HBM on interposer (CoWoS, EMIB), the BoR typically includes ≥3 separate test vehicles: the HBM stack alone, the host SoC alone, and the assembled 2.5D package.
Together, JEP122 and JEP148 form the contractual foundation between HBM suppliers (SK Hynix, Samsung, Micron) and system integrators: the supplier qualifies the HBM stack to JEP148 BoR; the integrator qualifies the assembled package with additional package-level stresses per JESD47.


## High-Temperature Operating Life (HTOL) for HBM

**HTOL** (JESD22-A108F) is the workhorse reliability screen. Devices are biased at rated VDD with functional patterns toggling at reduced frequency while held at **Tj = 125 °C** (or 150 °C for extended grade) for a minimum of **1000 hours**. The Arrhenius model with *Ea = 0.7 eV* (for EM/TDDB mechanisms) is used to translate accelerated failures at 125 °C to field lifetime at 85 °C junction.
For HBM specifically, HTOL test challenges include:- **Power delivery**: All 8 channels must be active simultaneously to stress PDN and on-die termination (ODT). Peak IDD at 125 °C is 15–25% higher than room-temperature spec due to leakage.- **Pattern selection**: Row hammer and checkerboard patterns are used in rotation to stress DRAM cell retention and array EM simultaneously.- **TSV thermal gradient**: The base die runs hotter than the top DRAM die because heat must conduct down through TSVs. Temperature sensors embedded in the base die (`TEMP_OUT` register in the HBM Mode Register set) should be read at HTOL entry and exit.
Typical HTOL sample sizes per JEP148 for a new process node: **3 lots × 77 units = 231 units**, targeting a C=0 accept plan with 90% confidence at 1000 FIT reliability goal.


## Highly Accelerated Stress Test (HAST) and Moisture Reliability

**HAST** (JESD22-A110E) is the primary moisture-corrosion screen. Unbiased HAST runs at **130 °C / 85% RH** for 96 hours; biased HAST at **110 °C / 85% RH** for 264 hours. Both are equivalent to 1000 hours of standard 85°C/85%RH (THB) testing by the Peck model with *n = 2.66*.
HBM stacks present a unique HAST challenge: the die-to-die interfaces sealed by underfill have very low moisture diffusivity, but any microbump voids or delamination at the Cu/SiO₂ interface can act as moisture ingress paths directly to active circuitry. Test acceptance criteria per JEP148 require:
- Zero opens or shorts on any of the 1024 data I/Os per channel post-HAST- No IDDQ increase >20% versus pre-stress baseline- Full functional test pass using the same ATE pattern set as productionNote that for fully assembled 2.5D packages (HBM + SoC on interposer), HAST is typically applied only at the *component* level before assembly, since the organic substrate cannot survive 130 °C / 85% RH without delamination. Post-assembly moisture screening uses JESD22-A101 (standard THB at 85°C/85%RH).


## Thermal Cycling, TMCL, and Mechanical Stress Qualification

**Temperature Cycling (TMCL)** per JESD22-A104E exposes HBM to repeated thermal excursions from −40 °C to +125 °C (Condition J, 500–1000 cycles) to drive CTE mismatch fatigue at solder joints, TSV Cu/SiO₂ interfaces, and NCP underfill boundaries. The dominant HBM-specific failure mode is **TSV Cu pumping** — repeated thermal expansion causes Cu to extrude from the via, eventually cracking the overlying ILD.
Acceptance criterion for TMCL: daisy-chain resistance shift ≤10% from baseline, measured after 500 and 1000 cycles with in-situ monitoring where possible. Failed units must be cross-sectioned (FIB-SEM) and failure mode verified as TMCL-induced before being counted against the qualification lot.
**Mechanical shock and vibration** (JESD22-B110B, -B103B) are included in the BoR for HBM modules destined for automotive and high-performance computing applications. These are typically run on singulated packages with in-circuit monitoring for resistance shifts exceeding 50 Ω transient spikes.


## Sample Sizes, Accept Plans, and Qualification Lot Requirements

JEP148 specifies qualification lot requirements by process maturity. For a **new HBM process node** (e.g., HBM3e at 1 Gamma node):
- Minimum 3 production-representative wafer lots, each from a separate manufacturing cycle- HTOL: 231 units (C=0, 90% confidence, Ea=0.7 eV, 1000 FIT target)- HAST: 77 units minimum (C=0)- TMCL: 77 units (C=0, 1000 cycles)- ESD: per JESD22-A114F (HBM ESD model) and JESD22-C101F (CDM), 3 units minimum per pinFor a **process change qualification** (PCQ) or **design change qualification** (DCQ), JEP148 allows reduced sample sizes and shorter stress durations, with a delta-qualification approach targeting only the affected mechanisms. This is commonly used when HBM memory density increases (e.g., 24 Gb to 36 Gb per die) without changes to the TSV or interconnect process.
All qualification data must be archived in a **Qualification Summary Report (QSR)** traceable to the device production spec and submitted to customers upon request. JEDEC JEP001 defines the minimum QSR content.


## Key Takeaways

- JEP122 maps failure mechanisms to physics models; JEP148 translates those into the Bill of Reliability qualification plan that HBM suppliers must execute.
- HTOL at 125 °C / 1000 h screens EM, TDDB, and HCI in the HBM stack; TSV temperature gradients and simultaneous channel activation are critical for stress realism.
- HAST at 130 °C / 85% RH / 96 h accelerates moisture-driven corrosion; assembled 2.5D packages switch to lower-temperature THB post-bonding to avoid substrate damage.
- TSV Cu pumping under TMCL is the primary mechanical failure mode unique to HBM; cross-section FIB-SEM verification of failures is mandatory before counting against qualification lots.
- C=0 accept plans with 3-lot, 77+ unit samples are the standard for new process node qualifications; PCQ/DCQ allows delta-qualification with reduced scope.

## References

1. **[JEDEC]** JEDEC JEP122H — Failure Mechanisms and Models for Silicon Semiconductor Devices — JEP122H, 2023 — sections 3.5 (EM), 4.2 (TDDB), 6.1 (HCI)
2. **[JEDEC]** JEDEC JEP148B — Reliability Qualification Standards for Packaged MCMs — JEP148B, 2022 — section 4 (Bill of Reliability), section 5 (sample size)
3. **[JEDEC]** JESD22-A108F — Temperature, Bias, and Operating Life — JESD22-A108F, 2021 — HTOL conditions and acceptance criteria
4. **[JEDEC]** JESD22-A110E — Highly Accelerated Temperature and Humidity Stress Test — JESD22-A110E, 2020 — biased and unbiased HAST conditions
5. **[JEDEC]** JESD22-A104E — Temperature Cycling — JESD22-A104E, 2014 — condition J (-40 to 125 °C) for 3D-IC packaging
6. **[Paper]** An et al. — TSV Copper Pumping and Reliability in 3D IC Integration — IEEE Trans. Device Mater. Rel., vol. 19, no. 1, 2019, pp. 23–31

## Additional Learning: Activation Energy Choices for HBM HTOL Extrapolation

The standard E_a = 0.7 eV used for EM and TDDB in bulk CMOS is often too conservative for TSV-dominated failure paths, where measured activation energies range from 0.5–0.9 eV depending on via aspect ratio and barrier metal (TiN vs. Ta/TaN). SK Hynix's HBM2e reliability white paper (2021) reported E_a = 0.82 eV for TSV EM in their 20nm-class process, yielding significantly more optimistic field-life projections than the JEDEC default. Teams running HTOL-to-field lifetime extrapolations should request supplier-specific E_a data from the qualification QSR rather than relying on the JEP122 default.
