# HBM Wafer Sort vs Final Test & KGD Strategy

*Monday, Jun 15 2026*

*Module 5.3 — ATE & Production*

## Purpose of Separate Wafer‑Sort and Final Test

Wafer‑sort validates raw die functionality and early‑stage parametric limits (e.g., `RDIMM_SBL`, `WR_TRAIN` timing, VDD, VPP). Final test confirms full stack‑level performance after TSV, interposer bonding, and device‑under‑test (DUT) integration, including high‑speed I/O, power‑noise, and thermal‑cycling compliance.
- Wafer‑sort targets high‑yield screening with low‑cost ATE (e.g., Advantest T3 with **2 ns** timing resolution).- Final test uses production‑grade ATE (e.g., Teradyne 4‑EB) with full HBM‑specific vectors (JEDEC <em>JESD235C</em> DDR5/DDR4 over‑clocks, BIST, stress).

## Key Test Differences and Parameter Sets

**Wafer‑sort** focuses on:
- Basic memory array read/write (`tRCD`, `tRP`), `VREF` calibration, and `IDDQ` leakage per die.- Die‑level BIST (JESD235C §5.2) without multi‑die coordination.- Parametric limits defined in KGD <em>Section 4.1</em> (e.g., `VDDQ` 1.2 V ±5 %).**Final test** adds:
- Stack‑level 2‑D/3‑D channel alignment checks (eye‑diagram, jitter < 0.3 UI, JEDEC <em>JESD233</em>).- Thermal‑cycling (0 °C → 85 °C, 100 cycles) and DRAM‑retention after package stress.- Power‑Integrity checks: `IDD5B`, `IDD6`, simultaneous switching noise on all four pseudo‑channels.

## KGD (Key Goal Definition) Alignment

KGD documents (e.g., Samsung KGD‑HBM2E‑2023) dictate that wafer‑sort yield ≥ 95 % for `tRAS` ≤ 38 ns, while final‑test yield must meet system‑level spec (≤ 2 % DPM). The KGD also requires:
- Traceability of wafer‑sort failures to specific `VF` bins for root‑cause analysis.- Cross‑check of wafer‑sort `IDDQ` distributions against final‑test `IDD5B` to detect latent defects.Non‑conformance at wafer‑sort triggers a hold‑and‑re‑test flow before package integration, reducing final‑test re‑work.


## ATE Configuration & Flow Integration

Both flows share a common test library but differ in timing constraints and stimulus depth.
- Wafer‑sort ATE: `CycleTime` 2 µs, `PatternDepth` 512 Mbits, limited to 2‑channel per die.- Final‑test ATE: `CycleTime` 200 ns, full 8‑channel DDR5 cascade, includes `JEDEC_March` BIST with `AK` and `CKE` duty‑cycle variations.Integration points: data‑export in `.vanguard` format for KGD dashboard, automatic binning rules per JEDEC <em>JESD248</em> for defect classification.


## Risk Mitigation & Yield Optimization

Strategic use of wafer‑sort data reduces final‑test failures:
- Statistical process control (SPC) on `tRC` and `IDDQ` trends predicts > 80 % of final‑test out‑of‑spec dies.- Early thermal‑stress on wafer‑sort (short `TempRamp` to 70 °C) catches TSV delamination before expensive 3‑D integration.- KGD mandates a **Yield Review Board** after every 10 k die, using combined wafer‑sort/final‑test histograms to adjust guard‑band spec.

## Key Takeaways

- Wafer‑sort validates die‑level electrical specs; final test validates full stack performance and system‑level reliability.
- KGD defines distinct yield targets and traceability requirements that shape test flow and binning logic.
- Coordinated ATE configuration and early‑stress testing bridge the gap, minimizing costly final‑test re‑work.

## References

1. **[JEDEC]** JEDEC JESD235C – DDR5 RDIMM/BGA Test Specification — Section 5.2 BIST, Section 6.3 Timing Parameter Limits
2. **[JEDEC]** JEDEC JESD233 – DDR5 Eye‑Diagram Test Methodology — Clause 4.4 – Jitter and Eye‑Width Measurements
3. **[Paper]** Samsung KGD for HBM2E 2023 — Internal KGD document, Samsung Foundry, 2023
4. **[Web]** Advantest T3 ATE Architecture for 3‑D Memory — https://www.advantest.com/products/t3-ate
5. **[IEEE]** Thermal‑Cycling Impacts on TSV Reliability — IEEE Trans. Components, Packaging and Manufacturing Technology, vol.12, 2022

## 🔍 Additional Learning: Machine‑Learning Yield Prediction from Wafer‑Sort Data

Recent studies (IEEE TIP 2024) show that neural‑network models trained on wafer‑sort <code>IDDQ</code> and timing variance can predict final‑test DPM with > 85 % confidence, enabling dynamic guard‑band adjustments before package assembly.
