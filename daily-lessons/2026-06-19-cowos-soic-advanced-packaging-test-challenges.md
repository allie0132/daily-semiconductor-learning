# CoWoS & SoIC Advanced Packaging Test Challenges

*Friday, Jun 19 2026*

*Module 6.2 — Advanced Topics*

## CoWoS Architecture and Testability Overview

TSMC's Chip-on-Wafer-on-Substrate (CoWoS) family integrates multiple dies on a passive silicon interposer (CoWoS-S), RDL interposer (CoWoS-R), or local-silicon-plus-RDL bridge (CoWoS-L) before mounting on an organic substrate. The interposer carries dense micro-bump arrays—typically 40 µm pitch for CoWoS-S—and through-silicon vias (TSVs) with a 10–40 µm diameter forming the vertical signal path from die to substrate.
From a test perspective, CoWoS creates a **three-stage inspection problem**: (1) wafer-level die sort before dicing, (2) interposer continuity and leakage after TSV reveal, and (3) assembled module functional test. Each stage uses different equipment—standard probe cards, specialized TSV kelvin probes, and socket-based or direct-dock ATE contactors—and must detect different fault modes including open TSVs, micro-bump bridging, and die-to-interposer alignment voids.


## Known Good Die (KGD) Requirements and Wafer-Level Strategy

The cost driver in CoWoS assembly is the **Known Good Die** requirement. A single defective die in a multi-chiplet stack condemns the entire assembled package, which may carry $1,000–$10,000+ in upstream value. JEDEC JEP160 defines KGD as a die proven to be electrically equivalent to a packaged part with a defect level below 100 DPPM.
Achieving KGD-grade confidence at wafer level demands:
- **Full-speed functional test** at the target operating frequency—often 3.2–6.4 GT/s for HBM I/O interfaces—using resonant fixture probe cards that suppress stub resonance below −20 dB across the band of interest.- **Burn-in at wafer level (WLBI)** using forced-air or liquid-cooled chuck systems capable of holding junction temperature within ±2 °C of target across a 300 mm wafer during 48–168 h stress.- **Stress-test pattern sequencing**: static IDDQ → March-C DRAM array scan → pseudo-random PRBS stress → functional corner sweep (−40 to 125 °C, 0.72–1.1 V VDD).Probe card challenges include maintaining &lt;50 mΩ contact resistance on micro-bumps as small as 25 µm, requiring tungsten carbide MEMS tips or advanced spring pin designs with CMP-polished tips.


## Signal Integrity Challenges at the Interposer Interface

The silicon interposer's dielectric constant (~11.7 for silicon vs. ~3.5 for low-k organic) creates transmission-line impedances that differ from conventional PCB environments. A 10 µm-wide, 200 µm-long interposer trace has a characteristic impedance of approximately 25–35 Ω, requiring careful impedance matching at die micro-bumps and substrate BGA balls to prevent reflections that corrupt high-speed signals.
ATE vector delivery must account for **stub resonance** in TSV arrays: a 100 µm-deep TSV forms a λ/4 resonant stub at roughly 375 GHz, but parasitic coupling between adjacent TSVs in a dense array (5 µm pitch) can induce resonances in the 10–60 GHz range detectable as periodic BER floors during PRBS-31 tests.
Practical SI verification steps:
- Measure insertion loss S21 and return loss S11 on representative daisy-chain coupons using a 67 GHz VNA prior to lot qualification.- Apply **de-embedding** to strip probe and fixture effects—use a 2×Thru SOLT calibration with substrate-based ISS standards.- Validate eye diagrams on all lane pairs at 1.25× production data rate; reject lanes with eye height &lt;30% of UI or jitter Tj &gt;0.3 UI at 10⁻¹² BER.

## SoIC Hybrid Bonding and 3D Test Constraints

TSMC's System on Integrated Chips (SoIC) uses **direct Cu-to-Cu hybrid bonding** (also called bumpless bonding) with pitches as fine as 0.5–9 µm, eliminating solder micro-bumps entirely. This achieves 10–100× higher interconnect density than flip-chip, enabling memory-on-logic or logic-on-logic stacks with sub-1 fJ/bit I/O energy, but it fundamentally eliminates any possibility of separating the stacked dies after bonding—making pre-bond test completeness non-negotiable.
Key DFT constraints imposed by SoIC:
- **No post-bond physical access** to die-to-die interfaces; boundary scan (IEEE 1149.1) chains must be designed to route through the bonded interface or bypass it entirely with dedicated test modes.- **Thermal gradients** from stacked power dissipation (up to 100 W/cm² in logic layers) cause timing shifts of 5–15% in memory arrays—test must apply worst-case thermal vectors, not isothermal conditions.- **Interconnect stress testing**: the Cu-Cu bond reliability is characterized by electromigration (EM) at current densities &gt;10⁶ A/cm² and by Cu diffusion at temperatures &gt;200 °C. HTOL and EM tests must stress the die-to-die links with repetitive toggle patterns achieving average IDac matching peak device specs.The IEEE P1838 standard (Die-to-Die Test) defines a scalable test access mechanism (TAM) and wrapper cell architecture specifically for 3D-IC stacks, allowing ATE access to individual die cores without requiring separate I/O pads on the bonded die.


## Thermal Management and ATE Integration for Advanced Packages

CoWoS packages for AI accelerators (e.g., NVIDIA H100, AMD MI300X) dissipate 300–700 W in a 75 mm × 75 mm footprint, creating extreme thermal gradients that ATE handlers and thermal force units (TFUs) must manage during test. Inadequate thermal control leads to **thermally-induced test escapes**: a device that passes at 25 °C die temperature but fails at 85 °C Tj may ship defective if the test socket's thermal resistance (θ_jc + θ_contact) is undercharacterized.
Best practices for thermal-aware ATE integration:
- Characterize socket θ_jc using a calibrated thermal test die (TTD) per JEDEC JESD51-14 to within ±2 °C before production ramp.- Use closed-loop TFU with die-surface thermocouple feedback; set dwell time ≥30 s after temperature setpoint change to allow thermal equilibrium across the interposer mass.- Apply **power sequencing guards**: do not apply full VDD until Tj is within ±5 °C of target; sudden power-on of a cold 700 W package into a warm socket causes thermal shock that can crack BGA joints.- Validate thermal derating curves: measure IDDQ, leakage, and timing at 5 °C intervals from 0 to 125 °C junction temperature to populate the production guard-band table.

## Key Takeaways

- KGD at ≤100 DPPM is mandatory before CoWoS assembly; full-speed wafer-level functional test and WLBI are the primary gates, not just DC parametric screening.
- SoIC hybrid bonding eliminates post-bond die separation, making IEEE P1838 TAM wrappers and pre-bond thermal stress patterns the only path to adequate die-to-die interface coverage.
- ATE thermal management for 300–700 W CoWoS packages requires JESD51-14-characterized socket θ_jc, closed-loop TFU control, and power-sequencing guards to prevent test escapes and thermally-induced package damage.

## References

1. **[JEDEC]** JEDEC JEP160: Known Good Die (KGD) Requirements — JEP160.01 — defines KGD electrical equivalency and DPPM targets for 2.5D/3D assembly
2. **[IEEE]** IEEE Std 1149.1-2013: Boundary-Scan Architecture — IEEE 1149.1-2013, clause 4 — JTAG test access port and boundary scan register definitions
3. **[IEEE]** IEEE P1838: Die-to-Die Test for 3D-IC — IEEE P1838 D3.0 — scalable TAM and wrapper cell standard for stacked-die test access
4. **[JEDEC]** JEDEC JESD51-14: Transient Dual Interface Measurement of Thermal Resistance — JESD51-14 — socket and package thermal resistance characterization methodology
5. **[Web]** TSMC CoWoS Technology Overview — TSMC 2023 Technology Symposium, CoWoS Platform Update — CoWoS-S/-R/-L architecture and interconnect pitch specs
6. **[Paper]** Chen et al., Hybrid Bonding Technology for 3D IC Integration, IEEE TED 2022 — IEEE Trans. Electron Devices, vol. 69, no. 8, Aug. 2022 — Cu-Cu bond reliability, EM, and diffusion characterization

## Additional Learning: Redundancy Mapping in CoWoS HBM Channel Allocation

CoWoS packages integrating HBM stacks rely on post-assembly redundancy mapping to retire defective DRAM columns and rows discovered during module-level test, a step that must be completed before the package is soldered onto a PCB. The ATE writes a redundancy map into one-time-programmable (OTP) e-fuses or SRAM-backed registers on the logic die via the JTAG/1149.1 interface; the HBM PHY then masks defective lanes during normal operation. Critically, test must verify the complete redundancy allocation path—from ATE pattern injection to e-fuse programming to PHY lane masking—because a failed OTP write creates a device that passes lane-level tests but exhibits intermittent errors in the field when the masked lane is occasionally accessed.
