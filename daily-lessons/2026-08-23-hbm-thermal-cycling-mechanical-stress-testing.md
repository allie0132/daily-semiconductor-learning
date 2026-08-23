# HBM Thermal Cycling & Mechanical Stress Testing

*Sunday, Aug 23 2026*

*Module 15.3 — Reliability & Qualification Testing*

## CTE Mismatch in HBM 2.5D/3D Assemblies

Coefficient of Thermal Expansion (CTE) mismatch is the dominant mechanical driver of fatigue failure in HBM assemblies. The HBM stack (Si, CTE ≈ 2.3 ppm/°C) sits on a silicon interposer or organic substrate with CTE ranging from 2.3 ppm/°C (Si interposer) to 17 ppm/°C (FR-4 PCB). Even on a CoWoS silicon interposer, the interposer-to-package substrate interface sees a CTE step of roughly 15 ppm/°C across temperature excursions.
For an HBM2E package with a 55 mm diagonal interposer, a ΔT of 100 °C produces a differential thermal displacement of approximately `Δε = (CTE_substrate − CTE_Si) × ΔT × L/2 ≈ 41 µm` at the corner C4 bumps — well into the plastic regime for 100 µm-pitch micro-bumps. HBM micro-bumps (nominally 25–55 µm diameter, Cu/SnAg) carry this strain on every thermal cycle.
Three material interfaces demand attention: - **HBM die-to-interposer micro-bumps** — smallest pitch, highest strain concentration- **Interposer-to-package substrate C4 bumps** — larger pitch, higher absolute displacement- **Underfill-to-die edge** — stress singularity at die corner drives delamination


## Solder Joint Fatigue Mechanics

Solder joint fatigue in HBM interconnects is governed by the Coffin-Manson low-cycle fatigue relationship, modified by the Engelmaier model for viscoplastic solder creep:
`Nf = ½ (2εf' / Δγ)^(1/c)`
where `Nf` is cycles to failure, `εf'` is the fatigue ductility coefficient (~0.65 for SnAgCu), `Δγ` is the shear strain range, and `c` is the fatigue ductility exponent (−0.442 − 6×10⁻⁴T for SnAgCu at temperature T in °C).
For HBM micro-bumps, the dominant failure mode progression is:
- **Initiation**: crack nucleation at IMC layer (Cu₆Sn₅ / Cu₃Sn) — brittle, accelerated by high current density EM in functional devices- **Propagation**: crack growth through bulk solder along grain boundaries- **Fracture**: open circuit or intermittent contact detected by continuity chain daisy-chain structuresHigh-Pb solder alternatives are no longer viable under RoHS; SAC305 (Sn-3.0Ag-0.5Cu) is standard for C4 bumps, while micro-bumps increasingly use Cu pillar with thin SnAg cap to minimize IMC growth and improve mechanical reliability.


## JEDEC Thermal Cycling Test Conditions

JESD22-A104 defines standardized thermal cycling conditions. For HBM reliability qualification, Condition G (−40 °C to +125 °C) and Condition B (−55 °C to +125 °C) are most commonly applied, with a 10–15 minute dwell at each extreme and ramp rates of 10–20 °C/min. Key parameters:
- **Condition B**: −55/+125 °C, ΔT = 180 °C — most stringent, used for military/automotive qualification- **Condition G**: −40/+125 °C, ΔT = 165 °C — standard HPC/AI accelerator qualification- **Condition H**: −55/+150 °C — emerging for high-junction-temp GPU packagesJESD47 (Stress-Test-Driven Qualification of Integrated Circuits) mandates the acceptance criteria: zero failures in sample sizes defined by the qualification risk assessment. Typical HBM qualification runs 1000 cycles with in-situ or periodic continuity monitoring via daisy-chain test vehicles.
The JEDEC JEP122 failure mechanism reference classifies solder fatigue as a wearout mechanism following a Weibull distribution with β > 1, distinguishing it from random failure modes (β ≈ 1) for FIT rate calculations.


## Test Vehicle Design and Measurement

Daisy-chain test vehicles (TCVs) are the workhorse for mechanical stress monitoring. A well-designed TCV for HBM qualification includes:
- **Corner daisy-chains**: chains through the four highest-strain corner micro-bumps to detect first-crack events; resistance measured in-situ or at intervals- **Center-to-edge gradient chains**: isolate spatial strain distribution vs. Coffin-Manson predictions- **IMC thickness monitors**: cross-section SEM/TEM after 0, 500, and 1000 cycles to track Cu₆Sn₅ growth rateIn-situ resistance monitoring uses a 4-wire Kelvin measurement with `I_force = 10 mA` (low enough to avoid self-heating) and resolution of 1 mΩ — a 10% resistance increase typically signals crack initiation per JEDEC JESD22-B106.
Acoustic microscopy (C-SAM at 15–100 MHz) before and after cycling images underfill delamination without cross-section destruction. For 25 µm micro-bumps, high-frequency CSAM (>200 MHz) or X-ray laminography is needed to resolve bump-level defects.
Finite Element Analysis (FEA) using ANSYS or Abaqus with viscoplastic material models (Anand parameters for SAC305) predicts accumulated plastic strain per cycle and ranks design variants before physical builds.


## Underfill Selection and Its Role in Stress Mitigation

Capillary underfill (CUF) and molded underfill (MUF) are both used in HBM assemblies, with different stress profiles. Underfill mechanically couples the die to the substrate, redistributing CTE-mismatch strain away from solder joints — but introduces its own failure modes:
- **CUF (epoxy, CTE ~25–30 ppm/°C)**: flows under die post-reflow; good gap fill for 20–50 µm standoffs; but CTE mismatch with Si at die edge creates a stress concentration that drives delamination- **MUF**: applied during compression molding; more uniform but harder to achieve void-free fill at sub-50 µm pitches- **No-underfill (NUF)**: used in some reworkable configurations but dramatically reduces thermal cycle reliability — typically acceptable only for ≥250 µm pitch C4 bumpsKey underfill material properties for HBM: glass transition temperature Tg > 125 °C (so cycling stays below Tg for Condition G), CTE₁ (below Tg) matched as close as possible to silicon (~3–8 ppm/°C achievable with SiO₂ filler loading >70 wt%), and Young's modulus E > 8 GPa at room temperature to stiffen the joint against shear.
Filler particle size must be &lt;50% of the minimum gap height — for 30 µm standoff micro-bumps, maximum filler diameter is 15 µm, typically requiring silica particle D90 &lt; 10 µm formulations.


## Key Takeaways

- CTE mismatch between silicon HBM die (~2.3 ppm/°C) and organic substrate (~17 ppm/°C) drives corner micro-bump fatigue; JEDEC Condition G (−40/+125 °C, 1000 cycles) is the standard HBM qualification benchmark.
- Daisy-chain TCVs with 4-wire in-situ resistance monitoring (10 mA force, 1 mΩ resolution) detect solder crack initiation; a >10% resistance rise per JESD22-B106 signals failure.
- Cu pillar + thin SnAg cap micro-bumps outperform Cu/SnAg bumps in thermal cycling by limiting Cu₆Sn₅ IMC growth; underfill with Tg >125 °C and SiO₂ filler CTE ≈ 3–8 ppm/°C is essential to redistribute die-corner stress.

## References

1. **[JEDEC]** JESD22-A104: Temperature Cycling — JEDEC Solid State Technology Association, JESD22-A104F, 2014 — defines thermal cycling conditions A through N
2. **[JEDEC]** JESD47: Stress-Test-Driven Qualification of Integrated Circuits — JEDEC JESD47J, 2017 — qualification flow including sample sizes and failure criteria for reliability stress tests
3. **[JEDEC]** JEP122: Failure Mechanisms and Models for Semiconductor Devices — JEDEC JEP122H, 2016 — Coffin-Manson and Engelmaier solder fatigue models, Weibull wearout classification
4. **[Paper]** Engelmaier Model for Solder Joint Reliability — Engelmaier, W., 'Fatigue Life of Leadless Chip Carrier Solder Joints During Power Cycling', IEEE CHMT, vol. 6, no. 3, 1983
5. **[JEDEC]** HBM2E JESD235C Physical Layer Specification — JEDEC JESD235C, 2021 — HBM2E physical layer including package dimensions, bump pitch, and interposer interface requirements
6. **[Paper]** Advanced Packaging for High Bandwidth Memory — Kim, J. et al., 'Reliability of CoWoS HBM2 Package Under Thermal Cycling and Drop Conditions', IEEE ECTC 2019, pp. 1712-1717

## 🔍 Additional Learning: Anand Viscoplastic Model Parameters for SAC305

FEA thermal cycling simulations for HBM solder joints require accurate viscoplastic constitutive models. The Anand model captures both rate-independent plasticity and creep in a unified formulation — critical for SAC305 at temperatures above 0.5Tm (≈50 °C for SnAg). Published Anand constants for SAC305 (Lau et al., 2012): s₀ = 1.8 MPa, Q/R = 8900 K, A = 277,780 s⁻¹, ξ = 7, m = 0.2, ĥ₀ = 1,500 MPa, ŝ = 39.4 MPa, n = 0.07, a = 1.3. These constants yield predicted Nf within ±15% of experimental daisy-chain data for Condition G cycling at standard HBM bump pitches.
