# RMA Failure Isolation in 2.5D Packages

*Wednesday, Jul 29 2026*

*Module 12.8 — Heterogeneous Integration & Advanced Packaging Test*

## Field Return Data Collection & Triage

Begin with detailed failure symptom capture: functional test logs, voltage/current margins, temperature cycles, and any observed error codes (e.g., `MCU_ERR_CODE`). Use a triage matrix to separate gross assembly issues (open/interconnect) from subtle timing or signal‑integrity problems.
- Record die‑stack orientation, bump pitch, and TSV count per JEDEC JESD235C Annex B.- Flag units with repeated failures across multiple test sites for focused analysis.

## Non‑Destructive X‑ray CT Inspection

Deploy a high‑resolution micro‑CT system (e.g., Zeiss Xradia Versa) with voxel size ≤1 µm to visualize the interposer, TSVs, micro‑bumps, and die‑attach layers without sectioning.
Key inspection steps:
- Apply a low‑kV beam (80 kV) to reduce sample charging on organic substrates.- Generate orthogonal slices to measure TSV wall thickness variation (>5 % deviation indicates possible void or crack).- Use software defect‑detection thresholds to flag delaminations at the die‑to‑interposer interface (`interface_gap` >2 µm).

## Layer‑Selective FIB Sample Preparation

When CT indicates a suspect region, perform lift‑out using a dual‑beam FIB‑SEM (e.g., Thermo Fisher Helios G4 CX) with gallium ions at 30 kV, 0.5 nA for coarse milling, then reduce to 5 kV, 50 pA for final polishing to minimize amorphous damage.
Layer‑selective strategy:
- Mill a protective Pt/C deposit (`Pt_deposit`) over the area of interest.- Sequentially remove layers: first the upper die‑attach, then the micro‑bump layer, finally exposing the TSV sidewall for cross‑section.- Monitor milling progress with in‑beam secondary electron imaging to avoid over‑etch into adjacent TSVs.

## Correlating Electrical Signatures with Physical Defects

After FIB expose, conduct SEM‑based EBIC or conductive AFM to map leakage paths. Typical failure mechanisms observed in 2.5D returns:
- TSV sidewall leakage (`I_leak` >10 nA at 1 V) indicating process‑induced damage.- Micro‑bump non‑wetting causing open interconnect (`R_contact` >10 kΩ).- Delamination leading to mechanical stress‑induced cracks visible in CT as low‑density voids.Log defect coordinates (X,Y,Z) from CT and match to failing net names from test patterns for root‑cause closure.


## Documentation, Reporting & Preventive Actions

Compile a failure analysis report that includes: CT volume renderings (ISO surface), FIB cross‑section images with annotated layers, EBIC maps, and statistical process control (SPC) charts of key parameters (bump height, TSV diameter).
Recommend corrective actions per JEDEC JESD22‑A108 (ESD) and IPC‑J‑STD‑001 (solder joint reliability) when systematic voids or mis‑alignments are detected.


## Key Takeaways

- Start with systematic field data capture to prioritize units for advanced imaging.
- Micro‑CT provides µm‑scale 3D defect mapping without destroying the package.
- Layer‑selective FIB enables targeted cross‑section of specific interconnect levels while preserving adjacent structures.
- Correlate electrical fault signatures (leakage, resistance) with physical observations for definitive root cause.
- Document findings with standardized images and SPC data to drive corrective actions and prevent recurrence.

## References

1. **[JEDEC]** JEDEC JESD235C: Test Methods for 2.5D/3D IC Packages — Section 4.2 – Interposer and TSV inspection guidelines
2. **[JEDEC]** JEDEC JESD22‑A108: Electrostatic Discharge Sensitivity Testing — Procedure for EOS verification on returned units
3. **[Paper]** Micro‑CT for Defect Detection in 2.5D Interposers — IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 45, No. 3, 2022, pp. 560‑572
4. **[Datasheet]** Thermo Fisher Scientific Helios G4 CX FIB‑SEM Datasheet — Beam energies 0.5‑30 kV, current range 1 pA‑100 nA, Pt/Gas‑EBID capability
5. **[Book]** Advanced Packaging Failure Analysis — Chapter 7: Layer‑Selective FIB and EBIC, S. M. Sze et al., 2021
6. **[Web]** IPC‑J‑STD‑001H: Requirements for Soldered Electrical and Electronic Assemblies — Section 3.5.2 – Void acceptance criteria for micro‑bumps

## 🔍 Additional Learning: In‑Situ Biasing During FIB Milling for Defect Activation

Applying a low‑voltage bias (≤1 V) to the specimen while milling can activate latent leakage paths, making them visible in EBIC or conductive AFM before final polishing. This technique has been shown to increase detection sensitivity for sub‑10 nm TSV sidewall defects by up to 40 % in recent studies (IEEE CPMT 2023).
