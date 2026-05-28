# HBM Signal Integrity: Eye, ISI & Crosstalk

*Thursday, May 28 2026*

*Module 2.7 — Electrical Testing*

## Eye Diagram Fundamentals for HBM

HBM uses a 2 ns (500 MHz) base clock with 8‑bit (or 16‑bit) parallel lanes per stack. The eye is measured on the `DQ`/`DM` pins after the equalizer and before the PHY retimer. JEDEC JESD235C defines the eye‑height (≥ 0.6 UI) and eye‑width (≥ 1.2 UI) limits for the **RDBI** (Read‑Data‑Bus‑Inversion) mode. Use a high‑bandwidth sampling oscilloscope (≥ 20 GHz) or a BERT with eye‑capture (e.g., Keysight 86400B) to collect a statistically valid eye (minimum 1 MUI).
- Mount the probe on the `STP` (staggered pin) test point to avoid loading the stack.- Apply the JEDEC‑defined `VREF` (0.5 VDDQ) to center the eye.- Record both `DQ0` and `DQ7` to capture worst‑case skew across the lane.

## Intersymbol Interference (ISI) Characterization

ISI in HBM is dominated by the micro‑bump parasitics and the TSV stack impedance. The spec in JESD236A requires an eye‑closure due to ISI of ≤ 0.2 UI at 100 °C. Perform a jitter‑decomposition using a BERT‑based jitter analyzer: separate deterministic jitter (DJ) from random jitter (RJ). The DJ component is further split into **ISI‑induced** (`DJ_ISI`) and **cable‑delay** (`DJ_CDL`).
- Set the BERT to a PRBS‑7 pattern; the high transition density stresses the channel.- Measure the eye opening at 0 % and 100 % BER to extract `DJ_ISI` using the bathtub curve.- Compare the measured `DJ_ISI` with the simulated eye using the HBM stack S‑parameter model (e.g., ANSYS SIwave).

## Crosstalk Sources and Measurement

HBM’s dense TSV array creates both near‑end crosstalk (NEXT) and far‑end crosstalk (FEXT). JEDEC JESD229B specifies a max NEXT of –30 dB for any `DQ` pair within the same stack, and –45 dB for adjacent stacks. Use a multi‑channel BIST that toggles a single aggressor lane while monitoring the victim lane’s eye. Record the induced eye‑closure and compute the crosstalk‑induced jitter (`CTJ`).
- Apply the worst‑case pattern: aggressor = PRBS‑31, victim = static 0.- Use a 4‑port VNA up to 30 GHz to extract S‑parameters `S21` for adjacent lanes; verify against the –30 dB spec.- Compensate with on‑die pre‑emphasis (PE) settings; typical PE = +2 dB for lane 0, –1 dB for lane 7 reduces `CTJ` by ~15 ps.

## Practical Test Flow for Production

1. **Setup**: Warm‑up DUT to 85 °C, apply VDDQ = 1.2 V, VREF = 0.6 V. 2. **Baseline Eye**: Capture 10 k UI eye on a reference lane (e.g., DQ0). 3. **ISI Sweep**: Vary PE/De‑emphasis (PE+, DE–) in 0.5 dB steps; log `DJ_ISI`. 4. **Crosstalk Test**: Enable aggressor lane, record victim eye, compute `CTJ`. 5. **Decision**: Pass if eye‑height ≥ 0.6 UI, `DJ_ISI` ≤ 0.15 UI, and `CTJ` ≤ 0.1 UI.

All data are stored in the test database with JEDEC test‑ID (e.g., 23‑03‑00) for traceability.


## Troubleshooting Common Failures

**Symmetric eye closure** often indicates a power‑rail droop; verify VDDQ decoupling and IR‑drop using on‑chip voltage monitors. **Asymmetric eye** (more closure on falling edge) points to excessive ISI from high‑frequency loss; increase PE or add a passive equalizer. **Random jitter spikes** at high temperature suggest TSV stress‑induced resistance change; schedule a thermal‑cycling test per JESD236B.


## Key Takeaways

- Eye‑diagram limits for HBM are defined in JESD235C; use ≥0.6 UI height and ≥1.2 UI width as pass criteria.
- Separate ISI from total jitter using PRBS patterns and jitter decomposition; target ≤0.2 UI ISI‑induced closure.
- Crosstalk must stay below –30 dB (NEXT) and –45 dB (FEXT); measure with aggressor/victim tests and S‑parameter checks.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM Electrical Test Methods — Section 4.2 Eye‑Diagram Limits
2. **[JEDEC]** JEDEC JESD236A – Signal Integrity for Stacked DRAM — Clause 5.3 ISI limits
3. **[IEEE]** IEEE 802.3bz-2021 – 2.5GBASE‑T1 and 5GBASE‑T1 PHY Specs — Relevant for high‑speed lane equalization
4. **[Datasheet]** HBM3 Datasheet – Samsung 8Gb — Table 13‑1 VREF and timing tables
5. **[Book]** High‑Speed Digital Design: A Handbook — Howard Johnson & Martin Graham, 2015, ch.7

## 🔍 Additional Learning: Machine‑Learning‑Based Eye Prediction for HBM

Recent work (IEEE Access 2024) uses convolutional neural nets trained on S‑parameter–derived eye data to predict worst‑case eye closure under process variation, reducing test time by up to 40 % while staying within JESD235C limits.
