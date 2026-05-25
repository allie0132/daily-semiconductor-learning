# HBM PHY Interface Testing Strategies

*Monday, May 25 2026*

*Module 2.1 — Electrical Testing*

## 1. Overview of the HBM PHY Layer

The HBM PHY implements a DDR4‑like high‑speed serial link over **128‑bit per stack** channels, using `DQ`, `DQ#`, `CK`, `CK#`, `CS`, `CS#`, `CB` (calibration bus) and optional `ONFI` sideband signals. JEDEC JESD235C defines the electrical parameters (impedance, eye‑height, jitter) and the <em>training algorithm</em> (WR, RD, and DDR4‑like DFE). Understanding the PHY is prerequisite for building test vectors that drive and sample these signals correctly.


## 2. Primary Test Domains


  - **Static DC Tests**: Verify `VDDQ` levels, `OO` (output‑enable) bias, and termination resistance per JESD235C §4.2.
  - **Eye‑Diagram & Jitter**: Use high‑speed sampling (e.g., Keysight 86108D) to capture 20‑UI eye at 2‑3× data rate; assess `UI` jitter <5 % and eye‑height > 40 % of VREF.
  - **Training Loop Validation**: Execute the JEDEC‑defined BIST training sequence, monitor `TRAIN_EN` and `TRAIN_DONE` flags, and compare measured DFE tap values to spec.
  - **Clock‑Data Recovery (CDR) Checks**: Measure phase error between `CK`/`CK#` and recovered data using a dual‑channel oscilloscope; ensure `ΔΦ` < 0.3 UI across temperature.
  - **Latency & Throughput**: Run a pseudo‑random bit sequence (PRBS‑31) write‑read loop and verify that the round‑trip latency matches `tRL` + `tWL` per the PHY spec.


## 3. ATE Test Flow Architecture

Typical ATE (e.g., Advantest T2000) flow:

<ol>
  - Pre‑bias: Apply `VDDQ` and `VDD`, perform `ON` power‑up sequencing per JESD235C §5.1.
  - IO‑Calibrate: Run `CK` edge‑align calibration using the `CAL_EN` pin; store `CAL_TAP` values.
  - Training Execution: Load the JEDEC training pattern (WR‑training, RD‑training) via the ATE’s vector memory; capture `TRAIN_STATUS` registers.
  - Eye & Jitter Capture: Switch the pin‑group to high‑speed mode, acquire 10‑k UI eye per channel, compute RMS jitter.
  
  - Functional BIST: Issue `WRITE` and `READ` commands through the HBM controller, verify data integrity with CRC.
</ol>
All steps must be repeated at \( -40\,°C, 25\,°C, 125\,°C \) and at the full data‑rate ramp (2.4‑3.2 Gb/s per lane). 


## 4. Key Timing Parameters & Measurement Tips

Critical timing registers (JEDEC JESD235C §6.3):


  - `tCK` – clock period, nominal 312.5 ps @ 3.2 Gb/s.
  - `tDQSQ` – DQS‑to‑DQ skew < 20 ps.
  - `tRCD` – command‑to‑data latency; validate with read‑latency eye.
  - `tVREF` – VREF calibration offset; measure with the ATE’s built‑in VREF monitor.

Tips:


  - Use a **low‑skew fixture** (≤5 ps) and calibrate the probe launch using built‑in TDR.
  - When measuring jitter, separate deterministic jitter (DJ) from random jitter (RJ) using a dual‑axis histogram.
  - Record the DFE tap coefficients after each training iteration; out‑of‑range taps (>±31) indicate routing impedance issues.


## 5. Failure Diagnosis & Debug

Common PHY failures and ATE‑based diagnostics:


  - **Training Timeout** – Check `TRAIN_ERR` bits; often caused by excessive ODT mismatch or insufficient VREF.
  - **Eye Closure** – Use S-parameter de‑embedding to locate bump‑to‑pad return‑loss >‑15 dB.
  - **CDR Phase Walk** – Plot phase vs. temperature; a slope >0.2 UI/°C suggests PLL gain errors.
  - **Data‑Integrity Errors** – Compare CRC failures against PRBS error mask; isolate to specific lanes for pinpointing via‑die metal discontinuities.

All debug data should be logged in the ATE’s `.csv` report and correlated with the stack’s temperature‑profile CSV for root‑cause analysis.


## Key Takeaways

- HBM PHY testing must cover static, dynamic, and training domains per JESD235C.
- Accurate timing measurement of tCK, tDQSQ, and DFE taps is essential for high‑speed compliance.
- A repeatable ATE flow with temperature‑cornering and voltage‑margining reveals most PHY defects.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2/2E Electrical Specification — Section 4‑6, 6‑3, 7‑2
2. **[IEEE]** IEEE 802.3cd‑2020 – High‑Speed Ethernet PHY Design — Relevant for CDR and jitter analysis, pp. 34‑42
3. **[Book]** Advantest T2000 User Manual – High‑Speed I/O Module — Chapter 12, pp. 285‑312
4. **[Datasheet]** Micron HBM2E Datasheet – Electrical Characteristics — Table 3‑15, Timing Summary
5. **[Paper]** J. Lee et al., “Training Algorithms for Stacked DRAM PHYs,” IEEE TCAD 2022 — DOI:10.1109/TCAD.2022.3156741

## 🔍 Additional Learning: Eye‑Mask Testing with Adaptive BIST

Recent HBM2E releases support an Adaptive BIST that dynamically generates an eye‑mask based on real‑time jitter measurements, allowing on‑chip pass/fail decisions without external ATE eye capture. Integrating this feature reduces test time by up to 30 % while still meeting JESD235C mask specifications.
