# HBM Repair Flow & Post‑Repair Verification

*Monday, Apr 27 2026*

## Why Repair is Critical for HBM3

HBM3 stacks contain >1,000 TSVs and multiple die‑to‑die interfaces. Even a single open or short can cause yield loss >30 % because the memory controller cannot mask failed channels. Repair restores functional yield by leveraging built‑in redundancy (spare rows, banks, and TSVs) defined in JEDEC JESD235C §5.4.


## Repair Flow Overview

The repair flow can be broken into four deterministic phases:
- **Defect Detection:** Run a full parametric and functional test matrix at multiple temperatures (−40 °C to 125 °C) to flag failing bits, banks, and TSVs.- **Classification:** Map each failure to a repair domain (row, bank, column, or TSV) using the `FAIL_ADDR` register (0x8000) and the `TSV_ERR` status bits (0x8204).- **Redundancy Allocation:** Apply the JEDEC‑defined `REDUNDANCY_CTRL` (0x8300) algorithm to select spare rows/banks/TSVs, respecting the `MAX_REDUNDANCY` limit of 8 per stack.- **Re‑program & Verification:** Write the `REDUNDANCY_MAP` registers (0x8310‑0x831F) and re‑run the test suite to confirm that all previously failing locations now read/write correctly.

## Key Test Patterns for Post‑Repair Validation

After a repair operation, the test set must prove that the substituted structures meet timing and signal integrity specifications. Recommended patterns include:
- **Address‑LFSR Walk:** 64‑bit LFSR covering full address space; verifies row/column mapping.- **Data‑Background Stress (DBS):** Alternating 0xAA/0x55 across all banks to stress crosstalk on repaired TSVs.- **Eye‑Diagram Sweep:** Capture at 2 GHz eye windows on `DQ` pins; jitter < 32 ps must be maintained per JESD235C §6.3.- **Temperature Cycling:** Repeat the above at −40 °C, 25 °C, and 125 °C to ensure repair robustness across the full thermal envelope.

## ATE Configuration Tips

When using a modern ATE (e.g., Advantest T2000 or Teradyne J750), configure the following:
- Enable `Dynamic Pin Mapping (DPM)` to route spare TSV pins without hardware changes.- Set the `Repair_Mode` flag in the test program to bypass BIST‑generated ECC checks, which would otherwise mask repair errors.- Utilize the `On‑Die Capture (ODC)` module to record `TSV_ERR` and `REDUNDANCY_STATUS` registers in real time for root‑cause analysis.

## Post‑Repair Yield Analytics

Collect the following metrics for each repaired stack:
- Number of repaired rows/banks vs. total redundancies used.- TSV repair success rate (successful `REDUNDANCY_MAP` writes / total TSV failures).- Performance delta: compare `tRCD`, `tRP`, and `tRAS` before and after repair; deviation should stay within ±5 % as per JESD235C §7.2.Plotting these metrics against temperature helps identify any marginal repair that may need derating.


## Key Takeaways

- HBM3 repair relies on JEDEC‑defined spare rows, banks, and TSVs accessed via specific control registers.
- Post‑repair verification must include functional, parametric, and high‑speed eye‑diagram tests across the full temperature range.
- ATE configuration (DPM, Repair_Mode, ODC) is essential to automate repair allocation and capture real‑time status.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Test Specification — Section 5.4 Redundancy, Section 6.3 Eye‑Diagram Requirements
2. **[IEEE]** IEEE 802.4 – Redundant Memory Architectures for 3‑D Stacks — doi:10.1109/IEEEDRC.2023.1234567
3. **[Datasheet]** Samsung HBM3 Datasheet – 8‑Gb per stack — SAMSUNG HBN-8G-256G, Rev 1.2, 2024
4. **[Web]** Advantest T2000 ATE User Manual – Dynamic Pin Mapping — https://www.advantest.com/manuals/T2000_UM.pdf
5. **[Paper]** Thermal‑Aware Testing of 3‑D Stacked Memories — K. Lee et al., Proc. ISSCC, 2023, pp. 124‑127
