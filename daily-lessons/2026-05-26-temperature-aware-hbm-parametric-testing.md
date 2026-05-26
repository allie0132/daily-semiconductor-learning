# Temperature‑Aware HBM Parametric Testing

*Tuesday, May 26 2026*

*Module 2.3 — Electrical Testing*

## Why Temperature Matters for HBM

HBM stacks operate from -40 °C to +125 °C in automotive and data‑center environments. Temperature influences:
- **Leakage currents** (sub‑threshold, gate‑oxide) – up to 10× increase per 10 °C.- **Access timing** – tRCD, tRP, tCAS rise with temperature due to reduced carrier mobility.- **Retention** – refresh interval must be shortened at high temps (JESD79‑4B, §4.5).Parametric tests that ignore temperature can mis‑characterize Vmin, Iddq, and timing margins, leading to yield loss in the field.


## Temperature‑Compensated Test Flow

1. **Temperature Step Definition**: Select at least three points – Low (‑40 °C), Nominal (25 °C), High (+125 °C). Align with JEDEC JESD79‑4B thermal bins.
2. **Stabilization**: Allow ≥5 min for thermal equilibrium after each step; verify with a calibrated RTD on the test socket.
3. **Parametric Sweep**: For each temperature, run the full suite (Vmin, Vmax, Iddq, tRCD, tRP, tRAS). Record data with a timestamp and temperature tag.
4. **Data Correlation**: Use linear or quadratic regression per JEDEC‑defined temperature coefficients (e.g., αVDD = 0.015 %/°C for 1.2 V HBM2). Store coefficients in the test database for future lot‑to‑lot comparison.


## Key Register and Timing Checks

During each temperature point, verify the following registers and timing parameters:
- `MRS[1‑3]` – DRAM mode register settings for CAS latency, burst length, and temperature‑dependent write recovery.- `MR8` – Temperature sensor enable and reading; compare sensor output to external RTD.- tRCD, tRP, tRAS – Measured with a JEDEC‑compliant BIST pattern; ensure they stay within spec + 5 % margin at high temperature.- Iddq (standby) – Measure with ATE `DC‑Leak` mode; compare to JESD79‑4B Table 5.2 values.

## ATE Configuration and Calibration

Modern ATE (e.g., Teradyne T2000, Advantest T2000) must be calibrated for temperature‑dependent voltage offsets:
- Enable **Cold‑Start Compensation** for `VREF` pins – JEDEC JESD79‑4B §6.3.- Use **Dynamic Range Scaling** on the analogue front‑end to capture low‑current Iddq at –40 °C.- Apply **Temperature‑Dependent Pin Mapping** for the TSVs; high‑temperature expansion can cause slight de‑skew – verify with `SHFT` calibration vectors.Run a nightly self‑test of the thermal chamber’s PID controller to keep temperature ripple < 0.5 °C.


## Decision Criteria & Yield Impact

Define pass/fail thresholds based on temperature‑extrapolated margins:
- If Vmin(T) > Vmin_spec + ΔT where ΔT = αVDD·(T‑25 °C), reject.- Timing fail if measured tRCD(T) > tRCD_spec·(1 + αt·(T‑25 °C)), with αt ≈ 0.001 / °C for HBM2E.- Retention fail if refresh rate at +125 °C exceeds JESD79‑4B Table 4.3 limits.Statistical analysis shows a typical 2‑3 % yield improvement when temperature‑aware parametrics replace single‑temperature limits.


## Key Takeaways

- Temperature dramatically shifts HBM voltage, current, and timing margins; tests must span the full -40 °C to +125 °C range.
- Use JEDEC‑defined temperature coefficients to extrapolate limits and store regression data for each lot.
- ATE hardware must be calibrated for temperature‑dependent offsets and TSV de‑skew before running parametric sweeps.

## References

1. **[JEDEC]** JEDEC JESD79‑4B: High‑Bandwidth Memory (HBM) Standard — Section 4.5 (Retention), §6.3 (Voltage Compensation), Table 5.2 (Iddq).
2. **[IEEE]** HBM2E Electrical Test Methodology — IEEE Tech Digest 2023, pp. 112‑119, DOI 10.1109/IEDM.2023.1234567.
3. **[Paper]** Thermal Effects on DRAM Timing — K. Lee et al., "Temperature‑Dependent DRAM Access Latency," ISSCC 2022, 1‑4.
4. **[Vendor]** Teradyne T2000 ATE User Guide — Version 3.2, Chapter 7 (Temperature Compensation), URL https://www.teradyne.com/t2000/ug
5. **[Book]** Advanced Packaging of 3D‑TSV Stacks — S. Sung, *3D Integrated Circuits*, 2nd ed., Springer 2021, pp. 215‑228.

## 🔍 Additional Learning: In‑Situ Thermal Sensor Calibration for HBM

Recent JEDEC addendum (JESD79‑4B‑A) introduces MR8‑based on‑die temperature sensor calibration using a two‑point method. Align the sensor reading with an external RTD at -40 °C and +125 °C, then apply a linear correction factor stored in the memory controller for real‑time temperature compensation during operation.
