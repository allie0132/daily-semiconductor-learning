# First Silicon HBM Bringup: Oscilloscope Debug & Lab Checklist

*Saturday, Sep 12 2026*

*Module 17.7 — HBM Ecosystem & Cross-Domain Test Engineering*

## Why Lab Bringup Precedes ATE

When first silicon arrives from the foundry, ATE programs are rarely complete, loadboard qualification is in progress, and package-level yield data is nonexistent. The lab bringup phase bridges tape-out delivery and ATE readiness. Its primary goals are: **verify power-on sanity** (clocks active, no catastrophic shorts), characterize worst-case operating corners, and generate failure signatures that seed ATE pattern development.
For HBM stacks specifically, the interposer introduces additional parasitics and the microbump array is not reworkable, making early DC parametric checks critical before any functional test is attempted. A systematic lab flow prevents permanent damage to the expensive package-on-interposer assembly.


## Power Sequencing and DC Validation

The JEDEC JESD235C specification defines HBM3 power domains: `VDDQ` (1.1V ±3%), `VDD` (1.1V ±3%), and `VDDIO` for the host PHY. Sequencing must follow the device datasheet — typically `VDD` before `VDDQ` — because premature `VDDQ` with unbiased core can forward-bias ESD structures across TSVs.
- Use a bench power supply with current limiting set to 10–20% above typical Icc for each domain.- Monitor inrush with a current probe (e.g., Tektronix CT-1) on each rail; first-silicon inrush peaks exceeding 2× expected indicate TSV shorts or microbump bridging.- Confirm `VDDQ` ripple &lt;5mV p-p at idle using a 20MHz BW-limited probe on the device pin itself, not the regulator output.- Log leakage: `VDD` quiescent current &gt;15% above characterization spec is a red flag for TSV leakage.

## Clock and DLL Lock Verification with Oscilloscope

HBM3 operates at data rates up to 9.6 Gb/s per pin. The internal DLL locks the internal WCK (write clock) to the external differential `WCK_t/WCK_c` pair driven at half data rate (4.8 GHz for HBM3 max). Before ATE, use a high-bandwidth oscilloscope (≥20 GHz analog BW, e.g., Tektronix DPO73304 or Keysight MSOS804A) to probe `WCK` at the package ball or via a probing interposer.
- Verify WCK differential swing: JEDEC specifies 200–500mV differential amplitude at the device input.- Measure WCK jitter: JESD235C Section 9 specifies RJ &lt;0.8 ps RMS for WCK; use TIE (Time Interval Error) histogram to separate random from deterministic jitter.- **DLL Lock Indicator:** Most HBM PHY implementations assert a `DLL_LOCK` status register bit (accessible via the Mode Register MR32 or implementation-specific CSR). Toggle CKE and observe recovery time — lock should re-establish within 1024 WCK cycles per JESD235C Section 8.3.- Check reference clock source: a TCXO or VCXO phase noise floor &lt;−140 dBc/Hz at 10 MHz offset is recommended to prevent floor-limited jitter accumulation.

## CATTRIP and Thermal Monitor Checkout

`CATTRIP` (Catastrophic Temperature Trip) is a mandatory HBM feature from HBM2 onwards (JESD235B Section 5.9, carried through JESD235C). It is an open-drain output that asserts low when the die temperature exceeds the catastrophic limit (~95°C on commercial stacks). In lab bringup:
- Confirm `CATTRIP` is pulled up on the board (typically 10kΩ to 1.8V) and monitor with a DMM or logic analyzer input.- Intentionally ramp device temperature with a thermal chuck or heat gun while logging `CATTRIP` state; verify it asserts before thermal runaway.- Read MR temperature readout register (MR4 bits[4:0] in HBM2e/HBM3 — temperature range 0–120°C in 8-step encoding) via JEDEC Training/Mode Register Write sequence to cross-check with an external thermocouple placed on the package lid.- Document the delta between on-die sensor and external measurement — this calibration offset becomes an input to ATE thermal spec limits.

## Basic DRAM Functional Checkout Before ATE

Once power-on and clock checks pass, a minimal functional smoke test can be performed using a pattern generator or FPGA-based host controller (e.g., Xilinx Versal or custom bringup board). The goal is **not** full characterization — it is pass/fail on fundamental row-column access:
- **AWORD loopback:** Drive the address/command bus (CA[9:0], CKE, PAR) at `t_CK` = 200 ps (HBM3 max rate) and capture with a logic analyzer to verify signal integrity and setup/hold margins against JEDEC AC spec Table 21.- **Write-Read-Compare:** Execute a JEDEC ACTIVATE → WRITE → READ → PRECHARGE sequence on a single row in each pseudo-channel. A rotating 0x55/0xAA pattern on 128-bit DQ bus is sufficient to catch catastrophic open/short failures on individual DQ lanes.- **Refresh test:** Leave a written row idle through ≥tRFC (JESD235C Table 15: tRFC1 = 160ns for 2H, 260ns for 4H stack) and verify data retention — early TSV-related leakage shows up as single-bit fail on bit 0 (lowest TSV layer) before propagating up the stack.- Record the scope capture of DQ eye at the stack output ball; an eye opening narrower than 80 mV / 20 ps is a flag for marginal SI on the interposer traces.

## Key Takeaways

- Sequence HBM power rails per datasheet (VDD before VDDQ) and monitor inrush current to detect TSV shorts before functional test.
- Verify WCK differential swing (200–500mV) and RJ (<0.8 ps RMS) with ≥20 GHz oscilloscope before ATE DLL tests.
- Validate CATTRIP assertion and MR4 thermal sensor readout early — these protect the device during characterization sweeps.
- A minimal Write-Read-Compare on all pseudo-channels with rotating 0x55/0xAA patterns catches catastrophic DQ failures in under 30 minutes of lab time.

## References

1. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM3) DRAM Standard — JESD235C Sections 5.9 (CATTRIP), 8.3 (DLL lock recovery), 9 (AC timing), Table 15 (tRFC), Table 21 (CA AC specs)
2. **[JEDEC]** JEDEC JESD235B — High Bandwidth Memory (HBM2e) DRAM Standard — JESD235B Section 5.9, MR4 thermal encoding — legacy reference for HBM2e stacks still in bringup
3. **[Web]** Keysight Application Note: Debugging High-Speed Memory with Oscilloscopes — Keysight App Note 5992-3765EN — covers TIE jitter decomposition and eye diagram methodology for LPDDR/HBM interfaces
4. **[Datasheet]** Tektronix: HBM Signal Integrity Measurement Guide — Tektronix document 48W-60850-0 — DPO/MSO70000 setup for WCK probing and jitter analysis on HBM packages
5. **[Paper]** Advanced Packaging First Silicon Bringup Best Practices — ECTC 2022, Lee et al. — 'Lab-to-ATE Handoff Methodology for 2.5D HBM Packages', pp. 1423–1430
6. **[Datasheet]** Micron HBM3 Product Brief and Datasheet — Micron HMABAGR0CAR4 HBM3 datasheet — power sequencing, Icc tables, and CATTRIP pull-up recommendations

## 🔍 Additional Learning: Using a Probing Interposer for Ball-Level Access on HBM

Accessing HBM microbumps with oscilloscope probes directly is physically impossible once the stack is assembled to the interposer. Test houses (e.g., Xcerra/Cohu, Advantest) and in-house bringup teams solve this by designing a probing interposer — an intermediate substrate that routes critical HBM signals (WCK, CA, DQ[0:3]) to accessible pads or SMA connectors while maintaining matched trace lengths to stay within JEDEC de-embedding specs. The probing interposer must preserve differential impedance (85Ω ±5% for WCK per JESD235C) and add <5 ps excess group delay relative to the production interposer, or measured jitter numbers will not map to ATE test conditions.
