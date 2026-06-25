# SPC & FMEA for HBM Yield Improvement

*Thursday, Jun 25 2026*

*Module 7.4 — Advanced Test Methodologies*

## Why SPC Matters in HBM Production

High‑Bandwidth Memory (HBM) stacks involve wafer‑level test (WLT), die‑attach, TSV formation, and final module test. Each step contributes variance to key parameters such as `DIE_TRAINING_TIME`, `VREF` window, and `JTAG_PULSE_WIDTH`. SPC detects shifts before they cause bin‑rejects, reducing scrap from >10% to <3% in mature lines.


## Control Charts for Critical HBM Metrics

Use separate **X‑bar** and **R** charts for each metric:
- **DIE_TRAINING_TIME** (ns): target 10 ns, USL 12 ns, LSL 8 ns.- **VREF_WINDOW** (mV): target 200 mV, USL 250 mV, LSL 150 mV.- **IO_TDR** (ps): target 3 ps, USL 4 ps, LSL 2 ps.Data are collected per lot (~1 k dies) from ATE (e.g., Teradyne _TSM‑HBM_). Plotting `X‑bar` (mean) and `R` (range) with 3σ control limits reveals:
- Trend drifts indicating equipment wear (e.g., probe needle force). - assignable causes such as flux bump height variance.

## Integrating SPC with Process Capability (Cpk)

Calculate `Cpk = min[(USL-μ)/(3σ), (μ-LSL)/(3σ)]` for each metric. Aim for Cpk ≥ 1.33 per <a href="https://doi.org/10.1109/Proc.2019.00021">IEEE 2020 HBM Yield Symposium</a>. When Cpk falls below 1.33, trigger a corrective action request (CAR) and update the SPC database.


## FMEA Workflow Aligned to SPC Findings

1. **Identify Failure Modes** – e.g., TSV open, Bump delamination, RDC skew.
2. **Assign Severity (S), Occurrence (O), Detection (D)** – use the SPC risk priority number (RPN = S×O×D). SPC trends feed O scores: a rising `R` chart adds +2 to O.
3. **Prioritize Actions** – focus on modes with RPN > 100. Example: TSV open has S=9, O from SPC = 8, D=4 → RPN=288 → immediate process audit.
4. **Implement Controls** – add a secondary `p‑chart` for TSV resistance, tighten probe overtravel, and update test program (JESD235‑C `HMEM_TEST_CFG`).


## Real‑Time SPC Dashboard in ATE

Modern ATE (e.g., Advantest `V93000‑HBM`) streams metric samples to a historian (OSIsoft PI). The dashboard plots live `X‑bar`, `R`, and `p‑chart` with automated alerts when a point exceeds ±2σ. Integration with MES triggers a hold on the lot if `Cpk` drops below 1.2 for any metric.


## Key Takeaways

- Control charts (X‑bar/R and p‑charts) provide early warning of drift in HBM test metrics.
- Process capability (Cpk ≥ 1.33) should be continuously monitored; low Cpk triggers CARs.
- FMEA uses SPC‑derived occurrence data to focus corrective actions on the highest‑risk failure modes.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM Test Specification — Section 4.3 Test Parameter Definitions, 2022
2. **[IEEE]** Statistical Process Control in Semiconductor Test — IEEE Trans. Test 2020, vol. 68, pp. 101‑112
3. **[Paper]** Failure Modes and Effects Analysis for Advanced Packages — J. Chen et al., "FMEA for 2.5D/3D Stacks," IEDM 2021
4. **[Datasheet]** Advantest V93000 HBM Test System User Manual — Rev. B, 2023, pp. 12‑18
5. **[Book]** Statistical Methods for Yield Improvement — S. Hamacher, "Yield Analysis in Electronics," 2nd ed., 2019

## 🔍 Additional Learning: Multivariate SPC for Correlated HBM Parameters

Recent work (IEEE 2023) shows that applying Hotelling's T² control charts to jointly monitor <code>DIE_TRAINING_TIME</code>, <code>VREF_WINDOW</code>, and <code>IO_TDR</code> captures cross‑parameter shifts that univariate charts miss, enabling earlier corrective actions.
