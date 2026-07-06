# Advanced HBM Failure Analysis: PFA, De-processing & EBIC/OBIRCH

*Monday, Jul 06 2026*

*Module 8.7 — System Integration & Advanced Verification*

## The HBM PFA Challenge

Physical Failure Analysis (PFA) of HBM devices is among the most demanding tasks in advanced packaging FA. A typical HBM2E stack (JESD235C) comprises one base die plus 4 or 8 DRAM dies bonded via **Through-Silicon Vias (TSVs)** of 5–8 µm diameter on a ~55 µm pitch, with die thicknesses thinned to 50–80 µm. The total stack height can exceed 700 µm. Defect localization must survive this vertical complexity while preserving fragile micro-bump interconnects (diameter ~25 µm, pitch ~55 µm) between every die interface.
Unlike monolithic DRAM, a failure in HBM may reside in:
- The base die logic (PHY, command/address decoder, temperature sensor)- A specific DRAM die (die 0–7) at a particular row/column/bank- A micro-bump or redistribution layer (RDL) interconnect between dies- A TSV itself (open, leakage, or stress-induced partial contact)- The interposer bump or Cu pillar connecting HBM to the 2.5D interposerElectrical isolation to a specific die level requires careful test vector sequencing using `MRS` (Mode Register Set) commands and per-die addressability defined in JESD235C Table 28 (Die ID assignment via `CABI` pin).


## PFA Flow for HBM Devices

The HBM PFA flow proceeds in a strict sequence to avoid destroying evidence:
- **Step 1 – Electrical characterization:** Re-verify the failure signature at wafer or package level. Capture IDDQ leakage, parametric margin, and failing address map. Use `PRBS` pattern or worst-case `checkerboard` stress to reproduce. Document the failing pseudo-channel (PC0/PC1) and die ID.- **Step 2 – Non-destructive inspection:** X-ray (2D and CT) to locate delamination, bump void, or gross mechanical damage. Acoustic microscopy (C-SAM at 200 MHz) to detect die-attach voids and delamination at each die interface.- **Step 3 – Emission microscopy (EMMI/OBIRCH/EBIC):** Localize the defect to a region before any destructive step. EMMI is run with the device powered in failure mode; OBIRCH and EBIC are used for leakage or open localization respectively.- **Step 4 – Top-side de-processing:** Remove dies one at a time from the top, stopping to re-verify electrical continuity at each interface.- **Step 5 – Cross-section and SEM/TEM:** FIB (Focused Ion Beam) cross-section at the localized defect site, followed by SEM imaging and TEM/EDX for elemental analysis.The key discipline is **never cross-sectioning blind**. Every destructive step must be preceded by an electrical or optical localization that narrows the defect to within ~5 µm of the FIB site target.


## De-processing Stacked Dies

De-processing HBM stacked dies requires mechanical, chemical, or laser techniques tailored to the epoxy molding compound (EMC) and underfill present between each die.
**Mechanical polishing:** A precision lapping jig removes material from the top surface. The lapping rate must be controlled to ±2 µm to avoid damaging the next die's active surface. Stop layers (e.g., nitride passivation) are identified by endpoint detection using optical reflectance change.
**Chemical/plasma etch de-cap:** Fuming HNO₃ or a dry-etch plasma (O₂ + CF₄) removes EMC without attacking silicon. However, underfill removal between micro-bumps requires a selective underfill etch (hot solvent or UV laser ablation at 355 nm) to expose individual bump rows without shearing them.
**Laser ablation:** UV (355 nm) or IR (1064 nm) pulsed laser ablation with ~5 µm spot size is used for localized die-top removal over a suspect TSV column. This avoids mechanical stress propagation to adjacent micro-bumps.
**Critical checkpoints at each die interface:**
- Inspect micro-bump integrity with 5 kV SEM before proceeding- Re-measure `ZQ` calibration and `DQSP/DQSN` termination resistance to confirm no new opens were introduced by the de-processing step- Photograph the full die surface at 500× before moving to the next level

## EBIC Technique for HBM Open/Short Localization

**Electron Beam Induced Current (EBIC)** is a scanning electron microscope (SEM)-based technique where the primary electron beam generates electron-hole pairs in the semiconductor. At a `p-n junction` or Schottky barrier, the built-in field separates these carriers, producing a measurable current (typically 10 pA – 1 nA) collected via external contacts. This current image reveals junction continuity, open interconnects, and sub-surface delamination.
In HBM analysis, EBIC is applied to:
- **TSV opens:** A TSV with a partial void shows reduced EBIC signal at the void location. The beam is scanned along the TSV axis (cross-sectioned by FIB first) and the current profile identifies the open segment.- **Micro-bump opens:** After de-processing to the bump level, EBIC maps current collection through each bump. A non-contacted bump appears as a dark region in the EBIC image.- **Junction leakage in DRAM cell:** Retention fail cells can be located by EBIC at the cell capacitor junction, where a defect causes anomalous current contrast.Beam energy is typically set to 10–20 keV, with beam current 100 pA. The signal-to-noise ratio is improved by lock-in amplification at a modulation frequency of 100 kHz – 1 MHz. Cooling the sample to −40°C (liquid nitrogen stage) increases minority carrier lifetime and enhances EBIC contrast for weak junctions.


## OBIRCH Technique for Resistance and Leakage Localization

**Optical Beam Induced Resistance Change (OBIRCH)** uses a focused infrared laser (typically 1300 nm) scanned over a powered device. Local heating from the laser changes the resistance of metal conductors (positive TCR) and semiconductors (negative TCR in polysilicon/diffusions), which alters the device current. The change in supply current ΔI is mapped as a function of beam position, producing a localization image.
OBIRCH applications in HBM PFA:
- **Leakage path localization:** A biased leakage path draws current; the laser heats nearby conductors and the ΔI signal pinpoints the resistive leakage. For HBM, this is used to find inter-die shorts through the underfill or EMC.- **Via/contact resistance hotspots:** High-resistance vias in the DRAM back-end-of-line (BEOL) produce a stronger OBIRCH signal due to higher ΔR from self-heating.- **RDL trace opens:** An open RDL trace shows no OBIRCH signal beyond the break point — the current path terminates there.OBIRCH is run from the **backside** for HBM DRAM dies (silicon is transparent at 1300 nm with thinned dies below 80 µm). The die must be thinned to &lt;50 µm for acceptable resolution through the silicon substrate. Backside OBIRCH avoids the need to remove metal layers and allows localization while the device is still assembled in the package.
Typical sensitivity: ΔI/I ≈ 10⁻⁵ at 1 mW laser power. Lock-in detection at 1 kHz modulation frequency is standard to reject DC drift.


## Key Takeaways

- Never cross-section HBM blind — always localize with EMMI, EBIC, or OBIRCH before FIB.
- De-processing must be die-by-die with electrical re-verification at each interface to confirm no new damage.
- EBIC localizes opens and junction defects (10–20 keV beam, lock-in at 100 kHz–1 MHz); works best at cryogenic temperature.
- OBIRCH from the backside (1300 nm IR, die thinned <80 µm) localizes leakage and high-resistance paths without front-side metal removal.
- TSV defects require combined FIB cross-section + EBIC profiling along the TSV axis to pinpoint partial voids.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM2E) Standard — JESD235C, Table 28 (Die ID/CABI), Section 4 (Initialization), JEDEC Solid State Technology Association, 2021
2. **[Book]** Failure Analysis of Microelectronic Packages — Noel Villalobos & Cheryl Tulkoff, ASM International Handbook Vol. 11B, Chapter 14 — 3D IC and TSV FA, 2021
3. **[Paper]** EBIC and OBIRCH Techniques for Advanced Package Failure Analysis — K. Nikawa & S. Inoue, IEEE IPFA Proceedings, pp. 1–8, 2019. DOI: 10.1109/IPFA.2019.8819442
4. **[IEEE]** Physical Failure Analysis of TSV-Based 3D-ICs — A. Mercha et al., IEEE Transactions on Device and Materials Reliability, vol. 17, no. 1, pp. 98–107, March 2017
5. **[Paper]** HBM Reliability and Failure Mechanisms — J. Kim et al., 'Reliability Characterization of HBM2 DRAM for High-Performance Computing', IEEE IEDM 2018, pp. 28.4.1–28.4.4
6. **[Paper]** Backside IR-OBIRCH for 3D IC Debug — C.-T. Tsai et al., Proc. ISTFA 2020, pp. 188–194, ASM International — demonstrates backside localization on thinned stacked dies

## Additional Learning: Correlating EBIC/OBIRCH with In-situ FIB-SEM for TSV Voids

When EBIC localizes an open within a TSV, the standard next step is FIB cross-section — but a single cross-section risks missing a void that is not centered on the cut plane. Modern dual-beam FIB-SEM systems running in serial sectioning mode (automated 10 nm slice-and-image) reconstruct the full 3D void morphology within a 10×10×60 µm volume, enabling precise defect volumetrics (void aspect ratio, position relative to the liner/barrier stack). Correlating this 3D reconstruction with the EBIC current profile confirms whether the void is a complete open or a resistive partial contact — a distinction that determines root cause (Cu fill void from ECD process vs. stress-migration during thermal cycling).
