# HBM Known-Good-Die Qualification – JEDEC, Sort Flow & Reliability Screening

*Tuesday, Aug 18 2026*

*Module 14.5 — Production Test Automation & Cost Optimization*

## JEDEC KGD Definition for HBM

Per JEDEC JESD235C, a Known‑Good‑Die (KGD) is a die that satisfies all parametric, functional, and reliability limits before HBM stacking.
- Parametric: VDDQ tolerance ±5 mV, IDDQ leakage < 10 nA/µm², VREF tolerance ±2 %- Functional: read/write latency ≤ tCK+2 ns, burst length BL8, ECC correctable error rate < 1×10⁻¹²- Reliability: HTOL 125 °C 1000 h, Temperature Cycling –55 °C/+125 °C 1000 cycles, ESD HBM ≥ 2 kV (JESD22A114)

## HBM KGD Sort Flow Overview

The production sort flow consists of wafer‑level probe, die‑level test, optional burn‑in, and final qualification before package stacking.
<ol>- Wafer probe: DC parametric (IDDQ, VDDQ, VREF) and basic AC (tCK, tAA) using a parametric test site.- Die‑level functional test: read/write patterns, latency, ECC validation on a multi‑site tester (e.g., Advantest T2000).- Burn‑in (optional): High‑Temperature Operating Life (HTOL) at 125 °C for 168 h to weed out early‑life failures.- Final KGD screen: repeat parametric + functional + limited reliability (TC 100 cycles) to confirm stability.</ol>

## Die‑Level Reliability Screening Tests

Reliability screening targets the dominant failure mechanisms in HBM dies: electromigration, time‑dependent dielectric breakdown, and package‑induced stress.
- HTOL (JESD22A108): 125 °C, 1.2×Vdd, 1000 h – detects oxide breakdown and metal migration.- Temperature Cycling (JESD22A104): –55 °C/+125 °C, 1000 cycles – evaluates CTE mismatch and solder joint fatigue.- Thermal Shock (JESD22A107): –0 °C/+150 °C, 100 cycles – checks for rapid‑temperature induced cracking.- ESD HBM (JESD22A114): ≥ 2 kV, 3 pulses – ensures input‑stage robustness.- Optional: Accelerated Moisture Sensitivity (JESD22A118) for die‑level MSL assessment.

## Cost‑Optimization Techniques in Production Test

Reducing test cost while maintaining KGD quality relies on test time reduction, parallelism, and smart binning.
- Test time reduction: use voltage‑scaled IDDQ measurement (low‑Vdd IDDQ) to cut settlement time by ~30 %.- Multi‑site testing: 4‑site parallel die test on Advantest V93000 cuts per‑die cost proportionally.- Adaptive binning: machine‑learning model predicts pass/fail from early‑life parametric drift, allowing early‑exit of marginal dies.- Wafer‑level burn‑in (WLBI): performing HTOL at wafer level eliminates separate die‑burn‑in step, saving ~15 % of total test time.- Data consolidation: store test results in a central SQL database with SPC charts to trigger immediate process adjustments.

## ATE Implementation Considerations for HBM KGD

Effective ATE setup requires appropriate instruments, fixture design, and software flow to meet JEDEC timing and voltage specs.
- Instruments: Keithley 2636B SMU for IDDQ, Teradyne FlexTester for AC timing (tCK, tAA, tRCD).- Fixture: low‑inductance probe card with ≤ 10 pH loop inductance, Kelvin‑connected VDDQ/VSS sense lines.- Software: test program uses JEDEC‑defined limits stored in a CSV; limits are loaded via Test Shell (TSL) API at runtime.- Calibration: quarterly SMU offset calibration (< 0.1 µA) and annual timing jitter verification (< 5 ps RMS).- Handler: parallel‑load handler capable of 2 kg die mass with < 0.5 ms pick‑place delay to avoid thermal shock during transfer.

## Key Takeaways

- JEDEC JESD235C defines KGD by parametric, functional, and reliability limits that must be met before HBM stacking.
- A typical KGD sort flow includes wafer probe, die‑level functional test, optional HTOL burn‑in, and final validation.
- Reliability screening focuses on HTOL, temperature cycling, thermal shock, and ESD HBM per JESD22A108/A104/A107/A114.
- Cost savings are achieved via voltage‑scaled IDDQ, multi‑site testing, adaptive ML binning, and wafer‑level burn‑in.
- ATE implementation requires low‑inductance SMUs, precise timing instruments, calibrated fixtures, and handler compatibility for HBM die mass.

## References

1. **[JEDEC]** JESD235C: High Bandwidth Memory (HBM) Specification — Section 4.2 – KGD Definition; Section 5.3 – Parametric Limits
2. **[JEDEC]** JESD22A108: High Temperature Operating Life (HTOL) — Test conditions 125 °C, 1.2×Vdd, 1000 h
3. **[JEDEC]** JESD22A104: Temperature Cycling — –55 °C/+125 °C, 1000 cycles
4. **[JEDEC]** JESD22A114: Electrostatic Discharge (ESD) Sensitivity Testing – Human Body Model (HBM) — ≥ 2 kV, 3 pulses
5. **[Datasheet]** Advantest V93000 Series Datasheet — Multi‑site test capability up to 8 sites, timing resolution 1 ps
6. **[Datasheet]** Keithley 2636B System SourceMeter Specifications — SMU current resolution 10 fA, voltage accuracy 0.015 %
7. **[Paper]** Wafer‑Level Burn‑In for HBM: Reducing Test Flow Complexity — IEEE ITC 2022, pp. 145‑150
8. **[Paper]** Machine Learning‑Based Adaptive Binning for Memory Die Test — DATE 2023, pp. 887‑892

## 🔍 Additional Learning: Wafer‑Level Burn‑In (WLBI) for HBM KGD

Recent industry practice integrates HTOL directly at the wafer stage using a specialized WLBI chuck that maintains uniform 125 °C across the die array while applying bias stress. This eliminates the separate die‑burn‑in step, reduces handling-induced damage, and can cut total test time by up to 20 % while preserving the same defect detection level as traditional die‑level HTOL.
