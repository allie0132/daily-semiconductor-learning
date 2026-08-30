# HBM AWORD/DWORD Training Algorithms: ZQ Calibration & Read/Write Leveling Automation

*Friday, Aug 28 2026*

*Module 16.2 — HBM Test Program Development & Characterization*

## HBM Training Algorithm Overview

HBM (High Bandwidth Memory) uses AWORD (address‑word) and DWORD (data‑word) training sequences defined in JESD235C to synchronize the memory controller with the DRAM die stack. The algorithm consists of three phases: ZQ calibration, read leveling (DQS‑DQ alignment), and write leveling (DQS‑DQ delay). Each phase programs specific MR (mode register) fields – e.g., MR62[ZQCAL] for ZQ, MR64[RDLEVEL] for read, MR66[WRLEVEL] for write – and relies on ATE‑generated pattern loops that measure eye margins.


## ZQ Calibration Automation

ZQ calibration adjusts the internal ODT and driver strength to match the external 240 Ω reference resistor. In HBM2E, the ZQCS command (MR62 write) triggers a calibration that must complete within tZQinit = 1 µs (or tZQoper = 256 ns for periodic). An ATE test program issues a ZQCS, polls the ZQDone flag via MR62[ZQDONE] (bit 0), and repeats until the flag is set or a timeout occurs. The measured ZQcode (MR63) is stored for later ODT/driver re‑calibration across temperature.


## Read Leveling (DQS‑DQ) Automation

Read leveling aligns the incoming DQS strobe with the data window on each DQ pin. The ATE drives a programmable pattern (e.g., 0xAAAA/0x5555) while sweeping the DQS delay line (MR64[RDLEVEL] 0‑63). For each delay setting, the tester captures the DQ samples and computes a pass/fail based on the expected pattern. The algorithm selects the delay that yields the maximum valid eye, typically targeting the center of the eye. JEDEC specifies tDQSCK(min/max) = 300‑600 ps; the sweep step is usually 16 ps (fine) or 64 ps (coarse).


## Write Leveling (DQS‑DQ) Automation

Write leveling ensures the controller’s write DQS leads the DQ data to meet tDSS/tDSH specifications. The ATE programs a write pattern (e.g., 0xFFFF/0x0000) and varies the write DQS delay (MR66[WRLEVEL] 0‑63). After each write, the tester reads back the data through a read‑leveling window to verify correct capture. The optimal write leveling delay is the smallest setting that yields zero bit‑errors across all DQ pins, satisfying tDSS ≥ 150 ps and tDSH ≥ 150 ps (HBM2E).


## Integrated Training Flow & Debug Techniques

A typical HBM ATE test program executes: 1) Reset (MR0), 2) ZQCS + poll ZQDone, 3) Read leveling sweep → store MR64 values, 4) Write leveling sweep → store MR66 values, 5) Optional periodic ZQ re‑calibration (every tZQoper). Debug is aided by reading the training status registers (MR62[ZQDONE], MR64[RDVALID], MR66[WRVALID]) and capturing the DQS/DQ eye diagrams with a real‑time oscilloscope or the ATE’s built‑in eye‑scope. Failed ZQ calibration often points to missing external ZQ resistor or incorrect MR62 write.


## Key Takeaways

- ZQ calibration must be completed within tZQinit/tZQoper and verified via MR62[ZQDONE] before proceeding to leveling.
- Read and write leveling sweeps use MR64[RDLEVEL] and MR66[WRLEVEL] respectively, with step sizes of 16 ps (fine) or 64 ps (coarse) to center the data eye.
- Integrated ATE flow combines reset, ZQCS, read leveling, write leveling, and periodic ZQ refresh, with debug via MR status flags and eye‑diagram capture.

## References

1. **[JEDEC]** JEDEC Standard JESD235C, High Bandwidth Memory (HBM) DRAM — Section 4.2 – Training Procedures (2020)
2. **[JEDEC]** JEDEC Standard JESD235B, High Bandwidth Memory (HBM) DRAM — Section 5.3 – ZQ Calibration (2017)
3. **[Datasheet]** Micron Technology, HBM2E 8Gb x4 Datasheet — Revision 1.0, 2021, pp. 23‑27 (MR definitions)
4. **[Whitepaper]** Samsung Electronics, HBM3 Technical Whitepaper — Section 3.1 – Dynamic ZQ and Leveling (2022)
5. **[Web]** Keysight Technologies, ATE Application Note: HBM Training Automation — AN‑HBM‑001, 2023
6. **[Paper]** S. Lee et al., Automated Read/Write Leveling Algorithms for 3D‑Stacked DRAM — IEEE TCAD, vol. 41, no. 4, April 2022, pp. 845‑858

## 🔍 Additional Learning: Adaptive ZQ Calibration Using On‑Die Temperature Sensors

Recent HBM3 implementations embed a temperature‑sensor‑driven ZQ trigger that automatically re‑issues ZQCS when the die temperature crosses a programmable delta (e.g., ±5 °C), reducing ATE intervention. This dynamic calibration leverages MR62[ZQEN] and MR63[ZQCODE] updates in real time, allowing the ATE to monitor ZQDone status only during initial calibration and rely on the DRAM’s self‑refresh for subsequent temperature compensation.
