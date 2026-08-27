# Field Failure Analysis of HBM: FIB, EBSD, and Lock‑In Thermography

*Thursday, Aug 27 2026*

*Module 15.8 — Reliability & Qualification Testing*

## Introduction to HBM Failure Modes

HBM stacks exhibit failure mechanisms such as thermal‑induced delamination, micro‑cracks in TSVs, interfacial voids, and redistribution‑layer (R/L) stress‑migration. Recognizing the symptom (e.g., intermittent I/O errors, increased leakage, or thermal runaway) guides the selection of the appropriate FA technique.


## FIB Cross‑Section Technique for HBM

Use a dual‑beam FIB‑SEM (e.g., `FEI Helios NanoLab G4 UC`) to mill a site‑specific cross‑section through the suspected defect region. Typical parameters: 30 kV Ga⁺ ion beam for bulk removal at 1–2 nA, followed by 5 kV low‑current polishing (`50 pA`) to minimize amorphous layer (`≈5 nm`). Acquire high‑resolution SE/BSE images to reveal TSV sidewall cracks, Cu‑Sn intermetallic growth, or delamination at the die‑to‑die interface.
- Protective Pt or W deposition (`≈100 nm`) before milling to reduce redeposition.- Monitor milling progress with low‑kV SEM (`2 kV`) to avoid over‑etch.

## Electron Backscatter Diffraction (EBSD) for Stress/Phase Analysis

After FIB exposure, transfer the lamella to an EBSD‑enabled SEM (e.g., `Bruker AXS D8 Discover` with EBSD camera). Collect orientation maps at `70 °` tilt, step size `50 nm`, and evaluate **kernel average misorientation (KAM)** to quantify lattice strain in Si die and TSV liners. Phase identification distinguishes Cu₆Sn₅ intermetallics from pure Cu, indicating reaction‑induced void formation.
- Indexing tolerance: `0.5°` for Si, `1.0°` for Cu‑based phases.- Apply pattern‑quality filter (>0.1) to suppress noise from amorphous FIB‑damaged layers.

## Lock‑In Thermography for Localized Hot‑Spot Detection

Operate a lock‑in IR camera (e.g., `FLIR A6750sc`) with sinusoidal power modulation at `10 Hz–1 kHz` on the HBM under test. The lock‑in amplifier extracts the in‑phase and quadrature components, revealing temperature oscillations as small as `≈10 mK`. Hot spots appear as localized amplitude peaks, correlating with resistive TSV shorts or delamination‑induced thermal resistance.
- Use emissivity correction (`ε≈0.92` for Si) and spatial calibration (`≈15 µm/pixel` at 1 m working distance).- Synchronize modulation with the ATE’s `VCC` toggling to isolate dynamic power dissipation.

## Integrated FA Workflow and Reporting

Combine the three techniques: (1) locate defect via lock‑in thermography, (2) prepare FIB cross‑section at the hotspot, (3) perform EBSD to assess strain and phase, and (4) correlate with electrical test data (e.g., increased `IDDQ` or timing margins). Document findings in a FA report that includes annotated SE/BSE images, EBSD IPF maps, lock‑in phase images, and a root‑cause conclusion (e.g., “TSV‑Cu‑Sn intermetallic growth causing increased resistivity and localized heating”).
Follow JEDEC JESD235C §8.4 for reliability test classification and IEEE Std 1413‑2021 guidelines for failure analysis documentation.


## Key Takeaways

- FIB cross‑sectioning provides site‑specific structural insight with sub‑10 nm resolution when proper low‑kV polishing is applied.
- EBSD quantifies lattice strain and identifies reaction phases (e.g., Cu₆Sn₅) that are precursors to mechanical failure in HBM stacks.
- Lock‑in thermography detects mK‑scale temperature variations, enabling non‑destructive pinpointing of resistive defects before destructive sectioning.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Device Specification — Section 8.4 – Reliability Test Methods
2. **[Paper]** Failure Analysis of 3D‑Stacked HBM Using FIB‑SEM and EBSD — IEEE Transactions on Device and Materials Reliability, Vol. 21, No. 3, pp. 456‑465, 2022. Authors: S. Lee et al.
3. **[Datasheet]** FEI Helios NanoLab G4 UC FIB‑SEM Datasheet — Thermo Fisher Scientific, 2023 – specifications for 30 kV Ga⁺, 5 kV polishing, Pt deposition.
4. **[Manual]** Bruker AXS D8 Discover EBSD System Manual — Bruker Corporation, 2021 – EBSD acquisition parameters, KAM calculation.
5. **[Datasheet]** FLIR A6750sc Lock‑In Thermography Camera Datasheet — FLIR Systems, 2022 – sensitivity 10 mK, modulation range 10 Hz–1 kHz.
6. **[IEEE]** IEEE Std 1413‑2021 – Standard for Failure Analysis of Electronic Devices — Guidelines for documentation and reporting of FA results.

## 🔍 Additional Learning: In‑Situ FIB‑EBSD Correlative Microscopy with AI‑Assisted Defect Classification

Recent dual‑beam systems integrate an EBSD detector directly into the FIB chamber, allowing site‑specific orientation mapping without breaking vacuum. Combined with machine‑learning‑based pattern indexing, phase fractions and strain gradients can be extracted in <2 min per site, accelerating root‑cause analysis for intermittent HBM defects. This approach reduces sample handling artifacts and enables feedback‑locked milling for targeted defect isolation.
