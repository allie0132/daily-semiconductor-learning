# KGD Screening for HBM: Burn‑in Wafer Probing and Sort Flows

*Tuesday, Jul 14 2026*

*Module 10.2 — Yield Optimization & Failure Analysis*

## KGD Fundamentals and Impact on HBM Yield

Known‑good‑die (KGD) screening is performed after wafer sort to remove die with parametric or functional defects before they are stacked, directly boosting HBM stack yield and reducing costly re‑work cycles.
JEDEC JESD235C defines KGD criteria: functional pass at nominal VDD, IDDQ < 5 µA, and no hard fails across all banks.


## Burn‑in Wafer Probing: Principles and Equipment Settings

Wafer‑level burn‑in applies elevated temperature (typically 125 °C–150 °C) and voltage stress (VDD = 1.35 V–1.5 V, VDDQ = 1.2 V) for a defined time (e.g., 2 h) to accelerate latent defects such as electromigration and TDDB.
Modern probe stations (e.g., FormFactor® Genesis®) use programmable thermal chucks and precision current sources to maintain `±0.5 °C` temperature uniformity and `±1 mV` voltage accuracy across the wafer.


## Test Patterns, Stress Conditions, and Failure Mechanisms

Typical burn‑in patterns include marching‑ones/zeros, checkerboard, and pseudo‑random sequences that exercise all I/O banks and internal arrays, maximizing switching activity.
Failure mechanisms monitored: **IDDQ increases** (gate‑oxide leakage), **delay faults** (RTN, NBTI), and **soft errors** (single‑event upsets) captured via built‑in self‑test (BIST) signatures.


## Sort Flow, Binning Logic, and Post‑Probe Repair

After burn‑in, dies are sorted into bins: <em>Pass</em> (meets all KGD limits), <em>Retest</em> (marginal IDDQ or speed), and <em>Fail</em> (hard fail).
Retest dies may undergo a second, lower‑temperature burn‑in or repair via laser‑fuse redundancy if supported by the HBM architecture.


## Yield Data Collection, Feedback to Fab, and Continuous Improvement

Wafer‑level test data (IDDQ, timing margins, fail codes) are logged in a manufacturing execution system (MES) and fed back to the front‑end for process adjustment (e.g., gate‑oxide thickness, metal line width).
Trend analysis using control charts helps detect drift in burn‑in escape rates, enabling proactive yield improvement loops.


## Key Takeaways

- KGD screening removes defective die before stacking, directly increasing HBM stack yield.
- Wafer‑level burn‑in uses elevated temperature and voltage to accelerate latent defects, guided by JEDEC JESD216A stress profiles.
- Post‑burn‑in sort data provide critical feedback to the fab for process control and yield enhancement.

## References

1. **[JEDEC]** JESD235C: High Bandwidth Memory (HBM) DRAM — Section 4.2 – Known‑Good‑Die requirements and burn‑in wafer probing
2. **[JEDEC]** JESD216A: Burn‑in and Stress Test Procedures for Memory Devices — Defines temperature, voltage, and time profiles for wafer‑level burn‑in
3. **[Datasheet]** Micron HBM2E 8‑GB datasheet — Specifies KGD test limits: Iddq < 5 µA, functional margin @ 1.35 V, 2 GHz
4. **[Datasheet]** Samsung HBM3 16‑GB product brief — Describes sort flow: wafer probe → burn‑in → final test → stack
5. **[Paper]** Y. Zhang et al., “Adaptive Burn‑in for HBM Using On‑Die Sensors,” IEEE TCAD, vol. 42, no. 3, pp. 567‑580, Mar. 2023 — Shows real‑time temperature compensation and defect escape reduction
6. **[Book]** S. M. Sze, “Physics of Semiconductor Devices,” 3rd ed., Wiley, 2006 — Chapter 9 – Failure mechanisms relevant to burn‑in (electromigration, TDDB)

## 🔍 Additional Learning: Machine‑Learning Defect Classification from Burn‑in Wafer Probe Data

Recent fabs deploy supervised ML models that ingest time‑resolved IDDQ and delay‑margin measurements from burn‑in wafer probes to predict latent failure modes. By labeling historical escape data, these models improve binning accuracy and reduce over‑test of good die, tightening yield ramps for next‑gen HBM stacks.
