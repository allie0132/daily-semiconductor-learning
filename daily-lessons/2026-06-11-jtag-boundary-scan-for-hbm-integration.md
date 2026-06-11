# JTAG Boundary Scan for HBM Integration

*Thursday, Jun 11 2026*

*Module 4.9 — DFT & Built-In Test*

## Why Boundary Scan Matters for HBM

HBM (High‑Bandwidth Memory) stacks are assembled using silicon‑on‑silicon interposers or embedded multi‑die interconnect (EMIB). Traditional probe access to each die pin is impossible after bonding; JTAG boundary scan provides a non‑intrusive path to control and observe every pad, including DRAM I/O, power‑good pins, and test‑chip reset lines.
Key benefits:
- Detect opens/shorts on TSVs and interposer traces before package burn‑in.- Program on‑die test registers (e.g., JEDEC `DRAM_TRAINING_CFG`) without external stimulus.- Enable in‑system firmware updates of the HBM controller via `TAP_RESET` and `IR` shifts.

## JTAG TAP Architecture in an HBM‑Enabled SoC

The Test Access Port (TAP) consists of four pins: `TCK`, `TMS`, `TDI`, `TDO`, plus optional `TRST_N`. In HBM‑integrated devices the TAP controller is usually located in the silicon‑interposer and cascades to each DRAM die. The typical instruction register (IR) length is 4‑6 bits; common instructions are:
- **EXTEST** – drive/observe pad pins for board‑level tests.- **SAMPLE** – capture internal logic states.- **IDCODE** – read IEEE 1149.1 device ID (e.g., 0x0F15C0xx for Samsung HBM).- **CFG_SCAN** – vendor‑specific configuration of DRAM training registers.Each DRAM die adds a boundary‑scan cell chain; the total chain length can exceed 10 k bits, so ATE must support high‑speed serial scan (up to 25 MHz TCK) and extended shift registers.


## Timing Requirements and Constraints

IEEE 1149.1 defines `TCK` period, setup, and hold times. For HBM stacks the JEDEC JESD235C adds the following constraints:
- `TCK` ≤ 25 MHz (40 ns period) to accommodate long interposer routing.- Data‑out `TDO` must meet `TDO_SETUP` ≥ 2 ns and `TDO_HOLD` ≥ 1 ns after falling edge of `TCK`.- Maximum scan chain delay `TSC_DELAY` ≤ 200 ns per 1 k bits (includes interposer capacitance).ATE configuration should set `MAX_TAP_DELAY` = 200 ns and verify with a built‑in `STY` (stuck‑at) pattern before production.


## Practical Test Flow for HBM Boundary Scan

Typical flow on a modern ATE (e.g., Advantest T2000):
<ol>- Reset TAP: assert `TRST_N` low for ≥ 5 µs, then release.- Read `IDCODE` to confirm all HBM dies are present.- Execute `EXTEST` with a predefined vector set that drives `DQ` pins high/low to measure leakage and continuity.- Shift in `CFG_SCAN` data to program DRAM training registers (`DRAM_TRAINING_CFG[31:0]`).- Run `SAMPLE` to capture internal state machines (e.g., `INIT_COMPLETE` flag) for functional verification.</ol>Results are logged in a JTAG Test Data Log (JTDL) file and correlated with electrical parametric tests.


## Debugging Common Boundary‑Scan Issues

Symptoms and root causes:
- **Stuck‑at TDO** – likely a broken interposer TSV or missing TAP power; check `VDD_TAP` (1.0 V) and continuity with a low‑frequency `EXTEST` sweep.- **IR shift errors** – mismatched IR length; verify instruction register size in the `JTAG_DESC` file (often 5 bits for HBM).- **Timing violations** – excessive chain delay; insert a `SCAN_CLK_DIV` (e.g., divide TCK by 2) in the ATE script.Use the IEEE 1149.1 `BS_CHAIN` command to isolate a failing segment by inserting `BYPASS` cells.


## Key Takeaways

- Boundary scan provides the only viable access to HBM pad pins after stack assembly.
- HBM TAP chains can exceed 10 k bits; ATE must support extended shift registers and up to 25 MHz TCK.
- JEDEC JESD235C adds specific timing limits (TCK ≤ 25 MHz, TSC_DELAY ≤ 200 ns/1k bits) for HBM interposers.

## References

1. **[IEEE]** IEEE Standard 1149.1-2013 (JTAG) — Standard for test access port and boundary‑scan architecture.
2. **[JEDEC]** JEDEC JESD235C: HBM 3.0 Specification — Section 6.4 – JTAG test requirements, timing constraints.
3. **[Book]** Advantest T2000 JTAG User Manual — Chapter 8 – High‑speed scan chain configuration for 3‑D packages.
4. **[Datasheet]** Samsung HBM3 Datasheet – Device ID and JTAG Instructions — 2023 revision, pages 42‑48.
5. **[Paper]** Miller, R. & Lee, K. (2022) ‘Boundary‑Scan Techniques for 2.5‑D/3‑D Stacked Memory’, IEEE Trans. Adv. Packag. — doi:10.1109/TAP.2022.3156789

## 🔍 Additional Learning: IEEE 1687 (IJTAG) for HBM On‑Die Test

IEEE 1687 extends JTAG with an internal scan network (IJTAG) that can address each DRAM macro individually. Recent silicon releases embed an IJTAG controller in the HBM die, enabling on‑die self‑test and firmware download without external TAP access. Evaluate whether your ATE supports IJTAG to reduce scan‑chain length and improve test time.
