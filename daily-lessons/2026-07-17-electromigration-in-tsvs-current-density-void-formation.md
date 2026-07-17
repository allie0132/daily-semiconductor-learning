# Electromigration in TSVs: Current Density & Void Formation

*Friday, Jul 17 2026*

*Module 10.7 — Yield Optimization & Failure Analysis*

## Electromigration Fundamentals in TSV Interconnects

Electromigration (EM) in Through-Silicon Vias (TSVs) is driven by momentum transfer from conducting electrons to metal atoms, causing net atomic flux in the direction of electron flow. For copper-filled TSVs — the dominant fill material in HBM stacks — this manifests as mass transport along grain boundaries, the Cu/barrier interface, and the Cu/dielectric liner interface.
The atomic flux **J<sub>atom</sub>** is governed by: `J = (C·D·Z*·e·ρ·j) / (k·T)`, where Z* is the effective charge number (≈ −4 for Cu), ρ is resistivity, j is current density, and D is the diffusivity. At TSV aspect ratios of 5:1 to 10:1 with via diameters of 5–10 µm, the confined geometry dramatically concentrates flux divergence at via ends — the primary failure initiation sites.
Unlike planar M1–M8 interconnects where EM is a second-order concern at modern linewidths, TSV current densities during HBM power delivery can approach 0.5–2.0 MA/cm², making EM a primary reliability limiter. JEDEC JEP154 provides the reliability qualification framework specifically addressing 3D-IC and TSV structures.


## Black's Equation and Current Density Limits

TSV electromigration lifetime is modeled by Black's equation: `MTF = A · j<sup>−n</sup> · exp(E<sub>a</sub> / k·T)`, where MTF is median time to failure, j is current density (A/cm²), n is the current exponent (typically 1–2 for Cu TSVs), and E<sub>a</sub> is the activation energy (0.7–0.9 eV for Cu grain boundary diffusion).
Practical current density limits for TSV qualification depend on the failure mechanism:
- **Conservative limit (void-free): ** j &lt; 0.5 MA/cm² for 10-year lifetime at 85°C junction temperature- **Typical TSV spec:** j &lt; 1 MA/cm² with &lt;10% resistance increase as failure criterion per JEDEC JESD22-A105- **Accelerated test conditions:** 2–5 MA/cm² at 250–300°C to generate failures within 200–500 hoursHBM3E power delivery TSVs handling 1A+ per signal group at 5 µm diameter (area ≈ 19.6 µm²) must be carefully analyzed — peak transient current during refresh operations can transiently exceed DC limits, requiring AC EM models that account for pulse frequency and duty cycle.


## Void Formation Mechanisms and Failure Modes

Void nucleation in TSVs follows a distinct sequence driven by flux divergence at structural discontinuities:
- **Via-bottom void:** Most common failure; cathode end depletion where electrons enter the TSV from the landing pad. Atoms migrate upward (in electron direction), depleting the bottom. Resistance increases gradually then spikes at void pinch-off.- **Via-top hillock:** Companion failure at the anode — atoms accumulate, forming a Cu extrusion that can bridge to adjacent vias or delaminate the passivation. This is the dominant short-failure mode.- **Mid-via grain boundary void:** Occurs at bamboo-to-polycrystalline grain structure transitions. Cu TSVs annealed at &lt;400°C often show mixed grain morphology with bamboo structures near center and polycrystalline near the liner, creating flux divergence points.In HBM stacks, void formation at the bottom TSV interface (Cu pillar landing on the interposer redistribution layer) is particularly critical because it is electrically in series with the DQ path. A 10% resistance increase in a single TSV can cause read eye closure at HBM3E 6.4 Gbps data rates where timing margins are already &lt;50 ps.


## Stress-Induced Voiding in TSVs

Stress-induced voiding (SIV) is a thermomechanical failure distinct from current-driven EM. It occurs without any applied current, driven purely by hydrostatic stress gradients created by the CTE mismatch between Cu (17 ppm/°C), Si (2.6 ppm/°C), and the SiO₂ liner (0.5 ppm/°C).
During thermal cycling (e.g., −40°C to +125°C per JEDEC JESD22-A104), the Cu fill expands far more than the surrounding Si. The liner and barrier (TaN/Ta, typically 50–100 nm total) must accommodate this strain. At low temperatures, the Cu contracts and develops tensile hydrostatic stress, driving vacancy migration toward regions of maximum tension — typically the via bottom and any Cu grain triple junctions.
Key parameters governing SIV susceptibility:
- **Via aspect ratio:** Higher AR increases stress gradient; 10:1 vias are significantly more SIV-prone than 5:1- **Anneal temperature:** 400°C post-fill anneal is the critical threshold — below this, residual tensile stress from electroplated Cu accelerates SIV- **Liner quality:** Continuous, pinhole-free TaN barrier prevents Cu diffusion that would relax stress beneficially at grain boundaries- **Keep-out zone (KOZ):** TSMC and SK Hynix specify a 2–5 µm KOZ around TSVs for active circuit placement to avoid stress-induced transistor threshold shiftsSIV failures typically exhibit a characteristic bathtub curve: high early-life rate (driven by anneal-induced stress), low steady-state, then rising late-life (cumulative thermal cycle fatigue).


## Test Engineering Implications: Detection and Qualification

From a test engineering perspective, both EM voids and SIV failures present as gradual resistance increases before catastrophic opens. Detection strategies in production and qualification testing include:
- **Four-wire Kelvin resistance:** Baseline TSV chain resistance measurement at wafer sort; Δ &gt;5% flags marginal vias. ATE instruments (Advantest T2000, Teradyne UltraFlex) can resolve &lt;0.1 Ω changes on 10–50 Ω TSV chains.- **Temperature coefficient of resistance (TCR) measurement:** Healthy Cu TSV shows TCR ≈ 3800 ppm/°C; void-containing vias show reduced TCR due to increased grain boundary scattering — measurable with forced temperature cycling during test.- **High-current stress test:** Per JEDEC JESD22-A105, stress at 2× nominal current density at 125°C for 1000 hours; measure intermediate resistance at 168h, 500h, 1000h.- **Thermal cycling with in-situ monitoring:** JEDEC JESD22-A104 Class H (−55°C to +125°C, 1000 cycles); resistance monitored in-situ with continuous logging to capture transient opens that self-heal at temperature.For HBM qualification, JEDEC JESD79-4B (HBM4) and the HBM manufacturer's IQ/OQ/PQ test plan require TSV chain resistance characterization across temperature, combined EM/SIV stress, and post-stress functional verification of all DQ, address, and power delivery paths through the TSV array.


## Key Takeaways

- TSV EM lifetime follows Black's equation with E_a ≈ 0.7–0.9 eV for Cu; current density must stay below ~1 MA/cm² for 10-year HBM reliability targets
- Void formation initiates at via cathode ends (opens) and anode ends form hillocks (shorts); mid-via grain boundary voids occur at bamboo-to-polycrystalline transitions
- Stress-induced voiding is thermomechanically driven by CTE mismatch (Cu 17 vs Si 2.6 ppm/°C) and occurs without current; 400°C post-fill anneal and a 2–5 µm keep-out zone are key mitigation measures
- ATE detection uses four-wire Kelvin resistance (&lt;0.1 Ω resolution on 10–50 Ω chains) and TCR measurement; JEDEC JESD22-A105 governs accelerated EM stress testing

## References

1. **[JEDEC]** JEDEC JEP154: Guideline for Characterization of TSV Reliability — Electromigration and Stress-Induced Voiding — JEP154, Rev. A, 2013 — primary TSV EM/SIV characterization framework
2. **[JEDEC]** JEDEC JESD22-A105: Power and Temperature Cycling — JESD22-A105D — accelerated EM stress test conditions, resistance increase criterion
3. **[JEDEC]** JEDEC JESD22-A104: Temperature Cycling — JESD22-A104E, Class H (−55°C/+125°C) — thermal cycle test for SIV qualification
4. **[IEEE]** Black, J.R.: Electromigration — A Brief Survey and Some Recent Results — IEEE Transactions on Electron Devices, vol. 16, no. 4, pp. 338–347, 1969 — foundational MTF equation derivation
5. **[Paper]** Lu, K.H. et al.: Thermomechanical Reliability of 3-D ICs Containing Through Silicon Vias — IEEE ECTC 2009 — CTE mismatch stress modeling and keep-out zone determination for TSVs
6. **[Paper]** Sukharev, V. et al.: Electromigration in TSV-Based 3-D IC Interconnect Structures — IEEE Transactions on Device and Materials Reliability, vol. 12, no. 2, 2012 — flux divergence modeling at TSV ends

## Additional Learning: AC Electromigration in TSVs: Pulse Frequency Effects on Lifetime

Under AC or pulsed current conditions — common in HBM DQ and power delivery TSVs during burst read/write operations — electromigration lifetime can be significantly longer than DC Black's equation predicts, due to partial atomic back-flow during current reversal. The Shatzkes-Lloyd model and later work by Tan et al. (IEEE T-EDL, 2007) quantify this: for bidirectional pulse currents with duty cycle r and frequency f, the effective stress is j_eff = j_peak × √(r), and for f > 1 MHz the Blech short-length immunity effect further suppresses void nucleation. This is critical for HBM3E interface TSVs operating at 6.4 Gbps — the high toggle rate and low average current means DC-qualified current density limits are overly conservative, allowing thinner or higher-resistivity TSVs than DC analysis would permit.
