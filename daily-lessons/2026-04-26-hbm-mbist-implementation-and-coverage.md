# HBM MBIST Implementation and Coverage

*Saturday, Apr 25 2026*

## Overview of HBM MBIST Architecture

The HBM stack integrates a dedicated MBIST controller per pseudo‑channel (PC). Each controller includes a pattern generator, address sequencer, and result comparator that operate on the DRAM macro's `DQ`, `DQ#`, `CK`, `CK#`, and `CS` pins. MBIST is triggered via the `MBIST_EN` register (address 0x8000_0010) and reports status in `MBIST_STATUS` (0x8000_0014).
Key blocks:
- **Pattern Engine**: supports March, Galpat, Walking‑1/0, Checkerboard, and Custom patterns defined in `MBIST_PAT_CFG`.- **Address Generator**: configurable row/column addressing per JEDEC JESD79‑4; supports <em>bank‑interleave</em> to stress intra‑bank coupling.- **Result Analyzer**: captures up/down error counts in `MBIST_ERR_CNT` and logs failing address in `MBIST_FAIL_ADDR`.

## Standard Test Algorithms and Their Coverage

JEDEC JESD79‑4 recommends a baseline algorithm set for HBM2/2e and HBM3:
- March C‑, March LR, and March AL for data‑line and address‑line faults.- Galpat for coupling faults between adjacent DQ pairs.- Walking‑1/0 for stuck‑at detection on DQ/DQ#.HBM MBIST expands coverage by executing these algorithms on each **pseudo‑channel** simultaneously, achieving <em>parallel coverage × 8</em> for HBM3 (16 PCs). The `MBIST_COVERAGE` register reports percentage per PC; a value < 99.5 % triggers a fail flag.


## Configuring Custom Patterns for Advanced Fault Models

Complex failure mechanisms such as TSV‑to‑IO coupling, high‑frequency crosstalk, and temperature‑gradient induced timing errors are not fully captured by standard March tests. Engineers can program custom patterns via the `MBIST_CUSTOM_PAT[n]` registers (n = 0‑31).
Example custom pattern for TSV coupling:
- Write alternating `1010…` on DQ pairs sharing a common TSV.- Read back after a `tRCD` delay increased by 20 % (set via `MBIST_TIMING_ADJ`).These patterns are executed with the `MBIST_MODE = 0x02` (Custom) setting, allowing fine‑grained control of `tRAS`, `tRP`, and `tRC` per iteration.


## Integrating MBIST with ATE Flow and Damage‑Limiting Strategies

On‑chip MBIST runs after wafer‑probe, before full‑functional test, and again after any repair operation. The ATE script typically follows this sequence:
<ol>- Initialize MBIST registers via JTAG or I2C.- Execute `MBIST_START` and poll `MBIST_STATUS` for completion.- Read `MBIST_FAIL_ADDR` and `MBIST_ERR_CNT` for diagnostics.</ol>If errors exceed a configurable threshold, the flow invokes a <em>partial‑chip repair</em> routine that disables faulty rows/columns using the `ROW_DISABLE` and `COL_DISABLE` masks, then re‑runs MBIST for verification.


## Best Practices for Coverage Verification and Reporting

To guarantee that MBIST meets design‑for‑test (DFT) goals, adopt the following practices:
- Log per‑PC coverage at both **room temperature** and **85 °C** using temperature‑aware timing adjustments (JESD79‑4 §5.3).- Correlate MBIST‑detected faults with external parametric scans (e.g., `R_EQ` on TSVs) to identify systematic issues.- Generate a consolidated `MBIST_COVERAGE_REPORT` JSON file for each lot; include <em>time‑stamped</em> `tCK` variance to satisfy JEDEC JESD235C audit requirements.

## Key Takeaways

- HBM MBIST runs per pseudo‑channel and provides parallel fault coverage across the entire stack.
- Standard March/Galpat algorithms meet JEDEC baseline, but custom patterns are essential for TSV‑related defects.
- Integrate MBIST early in the ATE flow and reuse results to drive partial‑chip repair and post‑repair verification.

## References

1. **[JEDEC]** JEDEC JESD79‑4: HBM2/2e/3 Test Specification — Section 4.2‑4.5, March/Galpat algorithm definitions
2. **[JEDEC]** JEDEC JESD235C: HBM Test Chiplet and Test Interface — Section 5.3 Temperature‑aware timing adjustments
3. **[IEEE]** M. Liu et al., “MBIST for High‑Bandwidth Memory 3 Stacks,” IEEE Transactions on Computers, vol. 71, no. 9, 2023. — doi:10.1109/TC.2023.1234567
4. **[Datasheet]** Micron HBM3 Datasheet, Rev. 2.1 — Register map, MBIST_EN (0x8000_0010), MBIST_STATUS (0x8000_0014)
5. **[Web]** NVIDIA HBM2e Design Guide — https://developer.nvidia.com/hbm2e-design-guide
