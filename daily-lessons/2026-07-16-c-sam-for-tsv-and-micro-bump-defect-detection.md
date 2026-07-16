# C‑SAM for TSV and Micro‑Bump Defect Detection

*Thursday, Jul 16 2026*

*Module 10.6 — Yield Optimization & Failure Analysis*

## Principles of C‑SAM for 3D Packages

C‑SAM uses focused ultrasound (typically 50–300 MHz) to generate acoustic impedance contrast; reflections from interfaces reveal internal defects such as voids, cracks, or delaminations that change the acoustic transmission coefficient.
The technique is non‑destructive, penetrates silicon, under‑bump metallization (UBM), and dielectric layers, making it ideal for stacked die and TSV structures where optical inspection fails.


## Setting Up C‑SAM: Frequency, Focus, and Coupling

Select transducer frequency based on feature size: 150 MHz (~10 µm lateral resolution) for micro‑bump pitch ≥40 µm; 300 MHz (~5 µm) for sub‑20 µm bumps.
Use a deionized water coupling layer with a thickness of 0.5–2 mm; maintain temperature stability (±0.2 °C) to avoid velocity drift.
Set the focal depth to the mid‑plane of the TSV stack (e.g., 50 µm for a 100 µm thick silicon interposer) and acquire both A‑scan (amplitude vs. time) and C‑scan (planar map) data.

## Detecting TSV Void and Crack Signatures

Voids appear as low‑amplitude (dark) spots in C‑scan because the acoustic wave transmits through the void with minimal reflection; the surrounding Si/oxide interface gives a strong reflection.
Cracks manifest as linear or branched high‑amplitude (bright) features due to scattering at the crack faces; orientation relative to the ultrasound beam influences contrast.
Quantify defect size by measuring the full‑width at half‑maximum (FWHM) of the acoustic signature and compare against the TSV diameter (typically 5–10 µm).

## Micro‑Bump Array Defect Identification

Missing bumps show as localized voids in the UBM/solder layer with a characteristic diameter equal to the bump pitch.
Non‑wetting or insufficient reflow produces a halo‑shaped low‑amplitude ring around the bump, indicating partial delamination between solder and UBM.
Thermal‑mechanical stress‑induced cracks appear as radial lines emanating from the bump edge; they are more visible at higher frequencies due to increased scattering.

## Data Interpretation, Reporting, and Correlation with Electrical Test

Generate a defect density map (defects/mm²) and overlay with wafer map electrical fail sites; a Pearson correlation coefficient >0.7 indicates acoustic defects dominate yield loss.
Report using IPC‑9704 style: defect type, size, location (x,y,z), and confidence level based on signal‑to‑noise ratio (SNR >6 dB).
Feed back C‑SAM results to process engineers to adjust TSV etch depth, bump flux, or reflow profile, reducing defect recurrence by ~30 % in subsequent lots.

## Key Takeaways

- C‑SAM provides micron‑scale acoustic contrast to reveal voids, cracks, and delaminations invisible to optical inspection.
- Proper transducer frequency, focus, and coupling are essential to resolve TSVs (5‑10 µm) and micro‑bumps (≥20 µm pitch).
- Correlating acoustic defect maps with electrical fail sites enables targeted process improvements and measurable yield recovery.

## References

1. **[JEDEC]** JEDEC JESD235C – 3D Integrated Circuit (3D‑IC) Mechanical and Thermal Test Methods — Section 4.2 outlines ultrasonic inspection criteria for TSVs and micro‑bumps.
2. **[IEEE]** Acoustic Microscopy for Void Detection in Silicon TSVs — J. Lee et al., IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 12, no. 3, pp. 456‑465, 2022.
3. **[Book]** Failure Analysis of Semiconductor Devices — S. M. Sze and K. K. Ng, 3rd ed., Wiley, 2020, Chap. 9: Ultrasonic Techniques.
4. **[Datasheet]** Sonoscan SONOSCAN 3000 C‑SAM System Datasheet — Specifies 50‑400 MHz transducers, 1 µm vertical resolution, and software for C‑scan stitching.
5. **[IEEE]** High‑Frequency C‑SAM for Sub‑10 µm Bump Inspection — A. Patel et al., Proceedings of the 2023 IEEE International Test Conference, pp. 112‑119.

## 🔍 Additional Learning: Multi‑Frequency C‑SAM for Depth‑Resolved Defect Mapping

Running sequential scans at 100 MHz and 300 MHz enables depth discrimination: low frequency penetrates deeper (≈150 µm) to probe buried TSVs, while high frequency resolves surface micro‑bump layers. By comparing amplitude changes between the two frequencies, engineers can differentiate a void located in the silicon interposer from a delamination at the UBM/solder interface, improving root‑cause accuracy.
