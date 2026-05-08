# Eye‑Diagram Margin Analysis for HBM3 Channels

*Friday, May 08 2026*

## Why Eye‑Diagram Analysis Matters for HBM3

HBM3 operates at up to 3.6 Gb/s per pin with 2.5 V DDR interfaces. The signal integrity (SI) budget is tight because of dense TSV routing, on‑die termination, and the requirement to meet **JESD235‑C** eye‑margin specifications (`Eye‑Opening ≥ 75 % UI` at 2 × speed bin). An accurate eye‑diagram gives a direct view of timing jitter, noise, and attenuation that cannot be captured by simple BER runs.


## Measurement Setup and ATE Configuration

Use a high‑bandwidth (**≥ 20 GHz**) sampling oscilloscope or an ATE channel with built‑in eye‑monitor (e.g., `Teradyne J750/ T650 with 16‑GSa/s ports`). Key configuration steps:
- Enable `PRBS31` pattern at the target data rate (3.6 Gb/s) and capture 10 µs of continuous data.- Set the oscilloscope's `Acquisition Mode = Eye‑Diagram` with `UI = 1/3.6 ns ≈ 278 ps`.- Apply on‑die ODT settings per JEDEC <em>JESD235‑C Table 5‑3</em> (e.g., 80 Ω write, 40 Ω read) to replicate nominal board operation.- Calibrate the probe attenuation and de‑embedding of fixture parasitics using a calibration board (e.g., <em>Keysight 85033E</em>).

## Extracting Eye‑Margin Parameters

After capture, compute the following metrics directly from the eye diagram:
- **Horizontal eye‑opening (t<sub>j</sub>)**: measure the usable UI at the 10 % BER crossing points.- **Vertical eye‑opening (V<sub>eye</sub>)**: difference between the eye’s top and bottom at the sampling point, expressed in mV.- **Jitter components**: separate deterministic jitter (DJ) and random jitter (RJ) using a dual‑ellipse fit per **IEEE 802.3‑28**.Compare results against the spec limits in `JESD235‑C 5.5.2` (e.g., RJ ≤ 3 % UI, DJ ≤ 10 % UI). Document any margin loss versus temperature and voltage corners.


## Worst‑Case Corner Stress and Margin De‑rating

Run the eye‑diagram capture at the four JEDEC corners:
- **TT (typical‑typical)**: 85 °C, 1.10 V VDD, nominal ODT.- **FF (fast‑fast)**: –40 °C, 1.20 V, minimum ODT.- **SS (slow‑slow)**: 125 °C, 0.95 V, maximum ODT.- **SF (slow‑fast)**: 85 °C, 1.20 V, mixed ODT.Apply the <em>Margin De‑rating (MDR)</em> formula defined in `JESD235‑C §6.3` to compute a single figure of merit. If MDR exceeds 20 % the design is non‑compliant and requires SI tuning (e.g., adjusting C<sub>term</sub> on the PCB, re‑biasing ODT, or modifying TSV stub lengths).


## Automating Eye‑Analysis in Production

Integrate the eye‑monitor flow into the ATE test program using `Teradyne TS0/TS1 scripts` or `Advantest V93000` `EyeTest` module. Key automation steps:
- Parameterize the pattern length, voltage, and temperature via test matrix CSV.- Capture eye data and export `.csv` of `t_j, V_eye, RJ, DJ` for each DUT.- Implement a `Python` post‑processor that flags any bin that violates `JESD235‑C` limits and logs the failure mode.This approach reduces test time from 30 s per DUT (BER) to ~8 s per eye‑capture while providing richer diagnostic data.


## Key Takeaways

- Eye‑diagram measurement captures real‑time SI issues that BER tests may miss.
- Use JEDEC JESD235‑C corner definitions and MDR calculation to quantify compliance.
- Automate eye‑monitoring in ATE to achieve fast, repeatable margin analysis for production.

## References

1. **[JEDEC]** JESD235‑C: High Bandwidth Memory (HBM) Specification — Section 5.5.2, 6.3 – Eye‑margin definitions and MDR formula
2. **[IEEE]** IEEE 802.3‑28 Clause 91: Channel Modeling and Eye‑Diagram Analysis — 2022, dual‑ellipse jitter decomposition
3. **[Datasheet]** HBM3 Datasheet – Samsung Electronics — Table 12‑1: ODT settings, timing parameters, voltage corners
4. **[Book]** Signal Integrity for High‑Speed Digital Design — Howard Johnson & Martin Graham, 3rd ed., 2020, Chapter 7
5. **[Web]** High‑Speed Test Solutions – Teradyne J750 — https://www.teradyne.com/products/j750
