# JEDEC JESD235 Compliance Testing Details

*Sunday, May 31 2026*

*Module 3.1 — Protocol & Compliance*

## JESD235 Standard Revisions and Scope

JEDEC JESD235 is the device-level standard governing HBM DRAM electrical and functional requirements. It has progressed through three major revisions: JESD235 (HBM1, 2013), JESD235A (HBM2, 2016), and JESD235C (HBM2E/HBM3 precursor, 2021). Each revision expanded data rates, stacking options, and compliance test categories.
The standard defines two compliance domains: **device compliance** (the HBM die itself) and **package/interposer compliance** (signal integrity within the 2.5D/3D stack). Test engineers must distinguish which domain applies to each test category — silicon characterization labs focus on device compliance while system validation teams address package compliance.
- JESD235: 1 Gbps/pin, up to 4-Hi stack, 128-bit channel × 2- JESD235A: 2 Gbps/pin, 8-Hi stack, HBM2 extended addressing- JESD235C: 3.2 Gbps/pin, adds pseudo-channel mode, DBI-AC, on-die ECC

## DC Electrical Compliance Tests

DC tests validate the HBM I/O cell behavior under steady-state conditions. Key parameters from JESD235C Table 4 include: `VDD = 1.2 V ± 5%`, `VDDQ = 1.2 V ± 5%`, and `VDDIO = 1.0 V ± 5%`. Each supply rail is characterized for leakage, quiescent current (IDD0 through IDD8 test modes), and supply rejection ratio.
Output driver compliance tests measure **VOH** and **VOL** at the specified load current against VDDQ/2 ± swing specifications. The HBM DQ driver uses a <em>pseudo-open-drain</em> topology with calibrated Ron via ZQ calibration (ZQCAL command, target 240 Ω external reference).
- `IOL` (output low current): ≥ 8 mA at VOL = 0.2 × VDDQ- `IOH` (output high current): ≥ 8 mA at VOH = 0.8 × VDDQ- ZQ calibration tolerance: ±10% of target Ron across PVT- Input leakage (II): ≤ ±10 µA per pin over voltage range

## AC Timing Compliance Tests

AC timing compliance covers the full set of DRAM timing parameters that govern memory controller scheduling. JESD235C Table 9 lists over 40 AC parameters; the most critical for test engineering are those which are both easily measured on ATE and architecturally significant for controller interoperability.
The key timing parameters tested at production include: `tCK` (clock cycle time, minimum per speed bin), `tRCDRD/tRCDWR` (RAS-to-CAS delay, separate for read/write paths in HBM2E), `tRC` (row cycle time), `tRFC1/tRFC2` (refresh cycle times for single/double rate refresh), and `tWL/tRL` (write/read latency measured from CK edge to first DQ valid).
- Speed bin compliance: tested at nominal VDD and TJ = 85°C- `tRFC1` (8-Gi device): 350 ns; `tRFC2`: 160 ns (JESD235C §4.12)- AC parametric tests use ATE pattern-based timing margin sweep (left/right eye closure)- Clock jitter (tJIT,cc): ≤ 50 ps peak-to-peak at rated speed grade

## Protocol and Command Compliance

Protocol compliance verifies that the HBM device correctly decodes and responds to the command/address (CA) bus. The CA bus in HBM2E is a 10-bit unidirectional bus clocked by the differential CK/CK_t pair at half the data rate. JESD235C §3.3 defines the command truth table; ACTIVATE, READ, WRITE, PRECHARGE, REFRESH, and MODE REGISTER READ/WRITE (MRR/MRW) must all be validated.
Mode register compliance is a critical test category — all 24 mode registers (MR0–MR23 in HBM2E) must be verified for read-back integrity after write. MR4[3:0] controls **read preamble length**, MR2[2:0] encodes **read CAS latency**, and MR1[5:3] sets **drive strength** (6 levels, 17–55 Ω). ATE patterns must exercise illegal command combinations to confirm PHY error response.
- CA loopback mode (MR6[7]=1): echoes CA bus through DQ for CA timing margin testing- JTAG boundary scan (IEEE 1500/1149.1): mandatory for package-level connectivity testing- BIST (Built-In Self Test): MR32–MR39 configure LFSR seed, pattern type, and column/row range- Illegal command detection: ATE must verify SERR# assertion on CKE violation or undefined opcode

## PVT Corner Coverage and ATE Considerations

Full compliance sign-off requires testing across Process, Voltage, and Temperature (PVT) corners. JEDEC compliance defines three mandatory electrical corners: **Nominal** (1.2 V, 25°C), **Fast** (1.26 V, 0°C), and **Slow** (1.14 V, 85°C). Package-level thermal resistance (θJA) affects junction temperature estimation during ATE — HBM2E stacks can reach 95°C TJ under full-array BIST patterns.
On ATE, the compressed test time challenge is significant: a full 4-Hi HBM2E stack has 8 Gbit of DRAM requiring ~15 seconds of BIST at 2 Gbps single-pin rate without compression. Production tests use **concurrent channel testing** (both 64-bit pseudo-channels simultaneously) and **algorithmic patterns** (MATS+, Galloping 1, March C−) with an on-die ECC engine to reduce raw bit failures from affecting yield.
- ATE per-pin timing accuracy requirement: ≤ 10 ps RMS edge placement for 2 Gbps compliance test- Temperature forcing: ATE thermal chuck or DUT soak oven at 85°C ±2°C- ZQ recalibration after temperature change: mandatory per JESD235C §4.5 before AC tests- Concurrent pseudo-channel BIST reduces test time by ~45% vs. serial channel testing

## Key Takeaways

- JESD235 compliance spans four domains: DC electrical, AC timing, protocol/command, and package/interposer — each requiring distinct ATE test content.
- ZQ calibration must be re-run after every voltage or temperature change to maintain DC electrical compliance accuracy.
- CA loopback mode (MR6[7]=1) is the primary on-chip mechanism for verifying command/address timing margins without requiring a logic analyzer.

## References

1. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM Standard — JESD235C, February 2021. §4 Electrical Characteristics, §3.3 Command Truth Table, §4.12 Refresh Timing
2. **[JEDEC]** JEDEC JESD235A — High Bandwidth Memory (HBM2) DRAM Standard — JESD235A, November 2016. Baseline for HBM2 mode register definitions MR0–MR23
3. **[IEEE]** IEEE Std 1500-2005 — Embedded Core Test — IEEE 1500 Wrapper cell standard referenced by JESD235C for HBM JTAG/boundary scan compliance
4. **[Paper]** Van Santen et al., 'Reliability and Test Aspects of 2.5D/3D Integration with HBM' — IEEE Electronic Components and Technology Conference (ECTC) 2019, pp. 914–921
5. **[Datasheet]** Micron HBM2E Component Data Sheet — MT53E2G80D8HQ — Micron Technology, Rev B, 2021. Electrical specifications correlated to JESD235C compliance tables
6. **[JEDEC]** JEDEC JEP106 and JESD79-5B (DDR5) — Background reference for DRAM timing test methodology — JESD79-5B §4.24 ZQ Calibration — methodology parallels HBM ZQ implementation in JESD235C §4.5

## Additional Learning: HBM BIST Modes: LFSR vs. March Pattern Selection

JESD235C §4.18 specifies two BIST pattern families selectable via MR32[1:0]: LFSR (pseudorandom, maximum length sequence for noise stress) and March patterns (deterministic address-sensitive fault coverage). For production compliance, March C− is preferred over LFSR because it provides guaranteed detection of stuck-at, transition, and coupling faults with only 10N memory operations — critical for minimizing ATE test time while meeting full-array fault coverage requirements set by JEDEC. LFSR patterns are reserved for characterization and burn-in, where stress amplitude matters more than diagnostic resolution.
