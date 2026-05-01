# Eye‑Pattern & Jitter Analysis for HBM3 IO

*Friday, May 01 2026*

## Why Eye‑Pattern Matters in HBM3

HBM3 operates up to 3.2 Gb/s per lane with tight UI (Unit Interval) budgets. Eye‑pattern measurement provides a direct view of timing margin, voltage swing, and jitter sources that affect BER targets (<10⁻¹²). The JEDEC JESD235‑C spec defines the `IEE` (Input Eye) and `EIE` (Output Eye) parameters that must be met for each DBI (Data Bus Inversion) pattern.


## Test Setup and Instrumentation

Use a high‑bandwidth (<12 GHz) oscilloscopic BERT (e.g., Keysight M9709A) with a programmable DDR5/HBM3 pattern generator. Connect to the HBM3 stack via a custom probe card with `50 Ω` controlled‑impedance micro‑bumps. Ensure the ATE’s `IOVDD` and `VREF` are calibrated per JEDEC JESD236‑A.
- Configure the BERT for NRZ, 8‑bit data‑bus‑inversion (DBI) patterns.- Set the clock source to the HBM3 reference clock (2.4 GHz) with phase‑aligned jitter cleaning.- Enable on‑chip eye‑monitor registers: `HBM3_EYE_CTRL`, `HBM3_EYE_STATUS`.

## Key Eye‑Diagram Metrics

The following parameters are extracted per JEDEC JESD235‑C Table 5.3 and must meet the limits for each pin:
- **UI Margin**: Minimum 0.65 UI opening at 80 % eye height.- **Voltage Swing**: 0.6–1.2 V differential (typical 0.9 V) at the sampling point.- **Total Jitter (TJ)**: `TJ` ≤ 0.2 UI (RMS) over 10⁶ UI.- **Random Jitter (RJ)** and **Deterministic Jitter (DJ)**: RJ ≤ 0.12 UI, DJ ≤ 0.08 UI.- **Eye Width** at 50 % amplitude must exceed 1.2 UI.

## Analyzing Jitter Sources

Separate jitter contributions using the BERT’s jitter decomposition function:
- **Clock phase noise** – measured by disconnecting the DUT and sampling the reference clock; compare against the spec in JESD236‑A clause 7.2.- **Power‑supply noise** – inject controlled PDN ripple (0.5 % of VDD) and observe TJ increase; correlate with on‑die `VDDIO_MON` registers.- **Crosstalk** – enable adjacent lane activity; monitor eye degradation using the `HBM3_CROSSTALK_EN` register.Mitigation approaches include adjusting termination resistance, re‑balancing DBI patterns, and tightening the PDN decoupling on the interposer.


## Reporting and Pass/Fail Criteria

Document eye‑diagram screenshots with UI grid overlay. Compile a CSV of measured metrics per lane and compare against the limits in JESD235‑C. Use the ATE’s `HBM3_EYE_RESULT` register to auto‑flag failures. For any lane exceeding TJ limits, trigger a retest with increased eye‑margin (‑10 mV VREF) before marking the stack as non‑conforming.


## Key Takeaways

- Eye‑pattern compliance is a direct indicator of HBM3 signal integrity and must meet JESD235‑C UI margins.
- Accurate jitter decomposition identifies whether clock, PDN, or crosstalk dominates the eye degradation.
- Automated registers (HBM3_EYE_CTRL/STATUS) enable inline pass/fail decisions within ATE flow.

## References

1. **[JEDEC]** JEDEC JESD235‑C: High Bandwidth Memory (HBM) Electrical Test Methodology — Section 5.3 Eye‑Pattern Measurements, 2022
2. **[JEDEC]** JEDEC JESD236‑A: HBM Power Delivery and PDN Guidelines — Clause 7.2 Clock Jitter, 2021
3. **[IEEE]** IEEE 802.3: 25‑Gb/s and 40‑Gb/s Ethernet PHY Design — IEEE Std 802.3-2020, relevant jitter analysis techniques
4. **[Datasheet]** Keysight M9709A BERT User Manual — Keysight Technologies, Rev B, 2023
5. **[Book]** HBM3 Stack Design Handbook — M. K. Hsu, "HBM3 Stack Design and Test," Springer, 2024
