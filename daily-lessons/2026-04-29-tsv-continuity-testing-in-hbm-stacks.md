# TSV Continuity Testing in HBM Stacks

*Wednesday, Apr 29 2026*

## Why TSV Continuity Matters

Through‑silicon vias (TSVs) carry high‑speed data, power, and ground across the HBM stack. An open TSV leads to loss of a channel, while a short between TSVs can cause crosstalk, timing violations, or latch‑up. JEDEC JESD235‑C specifies **continuity‑test (CT)** as a mandatory parametric for each TSV‑pair before functional qualification.


## Test Methodology Overview

The continuity test is performed on a wafer‑level probed die or on a packaged interposer using a 400 µm pitch micro‑probe card. The flow comprises:
- Apply a DC bias (typically +5 V on the TSV under test and 0 V on the reference ground TSV).- Measure the resulting current through a low‑value sense resistor (10 mΩ–100 mΩ) to derive resistance.- Repeat for each TSV pair using a `pin‑to‑pin sweep` matrix, leveraging the ATE's `DC_TSV_CONT` routine.Typical pass/fail limits: `R<sub>TSV</sub> ≤ 30 mΩ` for power/ground TSVs, `R<sub>TSV` ≤ 50 mΩ` for signal TSVs. Open detection is flagged when measured current < 1 µA (i.e., >5 MΩ).


## Timing and Stress Conditions

Continuity should be verified under both ambient (25 °C) and elevated (125 °C) conditions to capture thermally‑induced opens.
- Temperature ramp: 25 °C → 125 °C at 3 °C/min, hold 10 min, then measure.- Voltage stress: Apply +12 V for 100 ms before measurement to pre‑condition marginal contacts (JEDEC JESD235‑C §5.4).Record resistance versus temperature; a slope >0.2 µΩ/°C may indicate a compromised TSV wall.


## Automated Failure Analysis

If a TSV fails continuity, the ATE logs the failing pin pair and triggers a **focused IR‑thermal scan** on the wafer or an **EBIC** (electron‑beam induced current) map on the diced die. Correlate the resistance value with the physical location to differentiate between:
- Open due to void or delamination.- Short to adjacent TSV (usually `R ≤ 5 mΩ` and accompanied by a parallel‑path signature in the sweep matrix).Use the ATE’s `CONT_FAIL_ANALYSIS()` macro to generate a CSV report for yield tracking.


## Best‑Practice Checklist for Production

Integrate these steps into the production test flow:
- Run a quick `DC_TSV_CONT` at 25 °C before burn‑in.- Perform a full temperature‑stress sweep only on wafers flagged by the quick test.- Document resistance trends per lot to spot systematic process drifts.- Maintain a calibrated sense‑resistor bank (±0.5 % tolerance) and verify with a 4‑wire Kelvin measurement.

## Key Takeaways

- TSV continuity is a parametric requirement (JESD235‑C) and must be measured at both room and high temperature.
- Resistance limits differ for power/ground vs. signal TSVs; open detection relies on sub‑µA current thresholds.
- Automated failure analysis (IR‑thermal, EBIC) accelerates root‑cause identification and improves yield tracking.

## References

1. **[JEDEC]** JEDEC JESD235‑C: HBM Test Specification — Section 5.3–5.5, 2022
2. **[IEEE]** S. Kim et al., “Reliability of TSVs in 2.5‑D HBM Stacks,” IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 11, no. 4, pp. 642‑650, 2021 — doi:10.1109/TCPMT.2021.3059234
3. **[Book]** TSMC 2.5‑D Interposer Design Handbook — TSMC, 2020, Chapter 7 – TSV Test Methods
4. **[Datasheet]** Micron HBM3 Datasheet — Micron Technology, Rev. 3.2, 2023, Table 3‑9 – TSV resistance spec
5. **[Paper]** A. Patel, “Automated IR‑Thermal Imaging for TSV Fault Localization,” Proc. ISSCC, 2022 — ISSCC, 2022, pp. 115‑117
