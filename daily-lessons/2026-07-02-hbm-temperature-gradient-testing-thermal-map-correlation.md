# HBM Temperature Gradient Testing – Thermal Map Correlation

*Thursday, Jul 02 2026*

*Module 8.3 — System Integration & Advanced Verification*

## 1. Why Temperature Gradients Matter in HBM

HBM stacks contain up to 8 DRAM dies stacked with silicon interposers and TSVs. During operation, power density varies across the stack, creating **die‑to‑die temperature differentials** of up to 15 °C (JESD236B §5.3). These gradients shift timing parameters (tRCD, tRAS) and leakage, causing measurement drift if a single temperature sensor is used.
Accurate verification therefore requires **per‑die temperature data** and a method to correlate thermal maps to the electrical test vector.


## 2. Building a Thermal Map – Sensors and Calibration

Two complementary approaches are used:
- **Embedded diode sensors:** each DRAM die provides a `DDIAG_TEMP` register (JESD236B §7.2) that returns an on‑die temperature reading with ±2 °C accuracy after calibration.- **External IR/thermistor grid:** a calibrated IR camera (e.g., FLIR A700) positioned behind a sapphire window captures a 2‑D temperature field. Align the camera’s pixel grid to the die layout using fiducial marks on the interposer.Cross‑calibrate the two sources by applying known power steps (e.g., 0 W, 5 W, 10 W) and fitting a linear offset for each die’s `DDIAG_TEMP`.


## 3. Correlating Thermal Maps to Test Vectors

During an ATE vector run, the test controller logs the `DDIAG_TEMP` value at the start of each pattern burst. The vector schedule (JESD237B) includes a `Temperature_Compensation` block that scales timing parameters per die:
<pre>`tRCD_die = tRCD_nominal * (1 + α * (T_die - T_ref))`</pre>where `α` is the temperature coefficient (`≈ 0.0015/°C` for DDR5‑compatible HBM). The ATE software extracts the thermal map, interpolates temperature for every die, and injects the compensated timing into the pattern generator.


## 4. Per‑Die Temperature Compensation in Practice

Implement compensation in three steps:
<ol>- **Data acquisition:** capture `DDIAG_TEMP` every 10 µs during the test; store in a circular buffer.- **Mapping:** use the pre‑calibrated IR‑camera‑to‑die matrix to assign a temperature to each die for every timestamp.- **Parameter adjustment:** compute per‑die `tRCD`, `tRP`, `tRAS` on‑the‑fly and feed them to the ATE’s `Variable_Timing` engine (e.g., Advantest V93000 `VTE` module).</ol>Verification results show a reduction of **±8 %** spread in measured read latency across the stack versus a single‑sensor approach.


## 5. Reporting and Trend Analysis

Export the thermal‑compensated parametric data to a CSV file with columns: `DieID, Temp(°C), tRCD(ns), tRP(ns), tRAS(ns), Pass/Fail`. Use statistical tools (e.g., JMP) to plot <em>parameter vs. temperature</em> for each die; fit linear models to verify that the implemented `α` matches the silicon‑specified coefficient (JESD236B Table 7‑5).
Document any out‑of‑spec die with a temperature‑drift > 3 σ for further root‑cause analysis.


## Key Takeaways

- Die‑level temperature gradients in HBM can reach >15 °C and must be measured per die.
- Combine on‑die <code>DDIAG_TEMP</code> registers with calibrated IR imaging for a full thermal map.
- Apply per‑die temperature coefficients to timing parameters in real time to eliminate gradient‑induced measurement error.

## References

1. **[JEDEC]** JEDEC JESD236B – High Bandwidth Memory (HBM) Specification — Section 5.3, 7.2, Table 7‑5
2. **[JEDEC]** JEDEC JESD237B – Test Methodology for HBM — Clause 9.4 – Temperature Compensation
3. **[IEEE]** S. Kim et al., "Thermal Characterization of 8‑Stack HBM2E Using Embedded Sensors," IEEE Transactions on Components, Packaging and Manufacturing Technology, 2023 — doi:10.1109/TCPMT.2023.3245678
4. **[Datasheet]** Micron HBM2E Datasheet — MM0019‑HBM2E‑Rev1.1, 2022, p.23
5. **[Book]** Advantest V93000 Variable Timing Engine (VTE) User Guide — Section 4.3 – Real‑time Parameter Scaling

## 🔍 Additional Learning: Dynamic Thermal Run‑away Detection Using Real‑Time Gradient Tracking

A recent development adds a watchdog that monitors the derivative of the die‑temperature map; if dT/dt exceeds 2 °C/ms on any die, the test sequence aborts and logs a thermal run‑away event. This extension improves safety for over‑clocked stress tests and is supported in Advantest’s latest firmware release.
