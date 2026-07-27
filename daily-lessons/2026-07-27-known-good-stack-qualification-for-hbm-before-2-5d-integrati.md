# Known-Good-Stack Qualification for HBM Before 2.5D Integration

*Monday, Jul 27 2026*

*Module 12.5 — Heterogeneous Integration & Advanced Packaging Test*

## Overview of KGS Qualification Flow

Known‑Good‑Stack (KGS) qualification begins after wafer‑level burn‑in and continues through final test before die‑to‑die stacking. The flow consists of: (1) baseline electrical verification, (2) register‑mode checks, (3) AC‑timing margin testing, (4) thermal‑mechanical stress screening, and (5) signal‑integrity/eye‑margin validation. Each step generates a pass/fail flag that feeds into a yield‑management database.


## Electrical Test Sequence and Register Checks

Using an ATE site (e.g., Advantest V93000 HBM test site), the following sequence is executed:
- Power‑up and `MRR` of Mode Register 0 to confirm device ID and revision.- Write/read of MR2, MR4, MR6 to set operating parameters (e.g., CAS latency, write recovery).- March C‑ and walking‑ones patterns across all banks to detect stuck‑at and coupling faults.- Measurement of **tCK** (min 0.5 ns), **tRCD** (13.75 ns), **tCL** (13.5 ns), **tRP** (13.75 ns), **tRAS** (32 ns), and **tRC** (45.75 ns) per JEDEC JESD235C Table 5‑3.All register values must match the expected values within ±1 LSB before proceeding.


## Thermal‑Mechanical Stress and Reliability Screening

After electrical baseline, the stack undergoes:
- High‑temperature operating life (HTOL) at 125 °C for 168 hrs to accelerate latent defects.- Temperature cycling (‑55 °C → 125 °C, 1000 cycles) to expose package‑level CTE mismatches.- During each thermal step, a quick `MRR` of MR0 is performed to verify that no register corruption occurred due to thermomechanical stress.Failure thresholds: **IDDQ** increase > 10 % or any MR bit‑flip results in stack rejection.


## Signal‑Integrity Validation and Eye‑Margin Analysis

Using a high‑speed BERT (e.g., Keysight N4903A) attached to the HBM I/O lanes via a calibrated interposer, the following measurements are taken:
- Eye height and width at the nominal data rate (e.g., 4.6 Gb/s for HBM2E, 6.4 Gb/s for HBM3).- Jitter tolerance: total jitter (TJ) must be < 0.2 UI; deterministic jitter (DJ) < 0.07 UI.- BER target: < 1e‑12 after 10^12 bits transmitted.If any lane fails the eye‑margin criteria, the stack is flagged for rework or scrap.


## Failure Analysis, Yield Tracking and Data Management

All test results are logged into a centralized MES with traceability to wafer lot, die coordinates, and stack ID. Failures trigger:
- Automated fault‑isolations (e.g., defective TSV detection via laser‑scanning microscopy).- Root‑cause classification (electrical vs. thermal‑mechanical vs. signal‑integrity).- Yield impact calculation and feedback to upstream wafer‑sort and die‑stack processes.This closed‑loop data flow enables continuous improvement of the KGS qualification methodology.


## Key Takeaways

- KGS qualification combines electrical register verification, AC‑timing margin, thermal‑mechanical stress, and high‑speed signal‑integrity checks.
- Strict MRR checks after each thermal step prevent silent register corruption that could escape detection.
- Eye‑margin analysis using BERT ensures each HBM lane meets the required BER before 2.5D integration.
- Traceable failure analysis and yield tracking feed back to improve stack assembly and wafer‑sort processes.

## References

1. **[JEDEC]** JEDEC Standard JESD235C, High Bandwidth Memory (HBM) DRAM — Sections 4.2 (Mode Registers) and 5.3 (AC Timing) – defines MR map and timing parameters such as tCK, tRCD, tCL, tRP, tRAS, tRC.
2. **[JEDEC]** JEDEC Standard JESD210B, Wide I/O 2 Interface — Annex B – Electrical signaling specifications relevant to HBM I/O lanes and eye‑margin requirements.
3. **[Datasheet]** Micron Technology, HBM2E Product Technical Note, TN‑40‑001 — Register map, recommended test patterns (March C‑, walking‑ones), and typical timing values for HBM2E.
4. **[Web]** Advantest, V93000 HBM Test Site Application Note, AN‑V93000‑HBM‑01 — Site‑specific timing budgets, MRR procedures, and example test program flow for HBM KGS qualification.
5. **[Paper]** IEEE Transactions on Component Packaging and Manufacturing, "Test Strategies for 3D‑Stacked DRAM in Heterogeneous Integration" — Vol. 28, No. 4, pp. 1023‑1035, 2023 – discusses KGS methodology, thermal‑cycling correlation, and yield‑impact analysis.

## 🔍 Additional Learning: In‑situ MBIST for HBM KGS Validation

Modern HBM die embed a Memory Built‑In Self‑Test (MBIST) controller that can execute March‑type patterns at-speed without ATE stimulation. By triggering MBIST via a dedicated test mode register (MR7[3:0]) and capturing the pass/fail flag in MR8, test time can be reduced by up to 40 % while still detecting stuck‑at and coupling faults. This approach is especially useful for early‑stage wafer‑sort screening before full stack assembly.
