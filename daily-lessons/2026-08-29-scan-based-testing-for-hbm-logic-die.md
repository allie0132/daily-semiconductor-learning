# Scan-Based Testing for HBM Logic Die

*Saturday, Aug 29 2026*

*Module 16.3 — HBM Test Program Development & Characterization*

## Why Scan Testing Is Critical for HBM Logic Die

The HBM logic die — also called the base die — contains the I/O PHY, command/address decoders, temperature sensors, training logic, and DFT infrastructure for the entire stack. Unlike conventional DDR packages where ATE probes reach every pin directly, the HBM logic die is buried beneath DRAM dies and accessed only through micro-bumps or TSVs, making direct probe contact physically impossible after assembly.
Scan-based testing addresses this access problem in two complementary ways: **boundary-scan (IEEE 1149.1)** verifies interconnect continuity at package boundaries and inter-die connections, while **internal scan chains** (LSSD, muxed-D, or clocked-scan) exercise combinational logic within the die itself. Both mechanisms share the same four-wire Test Access Port (TAP): `TDI`, `TDO`, `TCK`, and `TMS`, plus the optional `TRST#` reset.
HBM JESD235C mandates that all compliant die include DFT provisions sufficient for post-stack diagnostic access, though it does not prescribe a specific scan topology — that is left to the die vendor's implementation.


## TAP Routing Through the 2.5D/3D Stack

In a 2.5D configuration (HBM stack on silicon interposer beside host GPU/CPU), the TAP signals are typically routed: **host controller → interposer wiring → HBM logic die bump → TAP controller on logic die**. The TAP runs at lower frequency than operational clocks — typically 10–50 MHz — and is kept on a dedicated power domain so the TAP controller remains accessible even when HBM power-saving modes have gated operational clocks.
In 3D configurations where the logic die is the bottom tier and DRAM core dies are stacked above, TSVs carry TAP signals vertically. JEDEC defines HBM TSV assignments in JESD235C Table 4; `TDI`, `TDO`, `TCK`, and `TMS` each have reserved TSV positions in the bump array. The TAP state machine on the logic die is the only TAP that appears external to the package — individual DRAM dies within the stack may have their own internal scan infrastructure accessed via IEEE 1500 wrapper cells rather than a separate external TAP.
HBM2E and HBM3 stacks expose a single external JTAG TAP on the logic die. The logic die TAP controller then acts as a **Test Data Register (TDR) multiplexer**, routing scan data to: (1) the logic die's own boundary-scan register, (2) the logic die internal scan chains, or (3) through a hierarchical path that reaches individual DRAM die via IEEE 1500 `SI/SO` ports over TSVs.


## Boundary-Scan Register Structure and BSDL

The Boundary-Scan Description Language (BSDL) file for the HBM logic die describes every I/O cell that participates in the boundary-scan chain. For HBM, the boundary cells cover: DQ/DQS/DM pads, CA/CK/CS pads, power and ground sense cells, and temperature alert outputs. Each cell is one of three types defined in IEEE 1149.1-2013:
- **BC_1** — bidirectional cell with output enable: used for DQ and DQS pads- **BC_2** — output-only with three-state control: used for CS, CK, CA outputs driven by the logic die toward DRAM- **BC_7** — input-only: used for voltage-sense and thermal alert inputsThe full boundary-scan chain length for a single HBM3 stack is typically 800–1200 bits depending on the I/O count (128-bit channels × 8 channels = 1024 data bits, plus command/address). The BSDL's `INSTRUCTION_LENGTH` is commonly 8 bits, supporting instructions: `EXTEST` (FF hex), `BYPASS` (FF hex), `SAMPLE/PRELOAD` (02 hex), `IDCODE` (01 hex), and vendor-specific instructions for temperature readout and training status capture.
During wafer probe of the logic die KGD, the full boundary-scan chain is exercised with alternating 0/1 patterns to verify cell capture and update paths. At final ATE after assembly, `EXTEST` mode drives the micro-bump connections from the logic die boundary cells toward DRAM and checks DRAM boundary cell responses — verifying TSV continuity without needing direct probe access.


## Internal Scan Chain Architecture and Test Coverage

The HBM logic die internal scan chains are partitioned into **clock domains**, with each partition using its own scan clock (`SE` shift-enable plus one or two scan clocks). Typical partitions in an HBM3 logic die include:
- **PHY partition**: DFI-to-pad serializers/deserializers, read/write leveling logic, DQS gating — clocked at a divided version of CK- **Command decode partition**: CA bus receivers, row/column address decoders, refresh counter logic- **Power management partition**: VDD island sequencers, ZQ calibration control, temperature sensor ADC- **Training and MRS partition**: mode register shadow copies, ODT control, RCD equivalent logic (in pseudo-channel mode)Each partition connects to the TAP via a dedicated Scan Data Register (SDR) or via an IEEE 1500 wrapper. The ATE typically runs scan at **at-speed** for launch-capture tests (LBIST-style) to catch path-delay faults that shift-speed tests miss. HBM ATE patterns use `STIL` (IEEE 1450.0) format, with scan pattern annotations specifying which partition each scan segment targets.
Fault coverage targets for logic die internal scan are typically &gt;95% stuck-at coverage and &gt;85% transition fault coverage for a KGD pass. These metrics are reported in the die sort data attached to the KGD lot traveler used by the packaging house during stack assembly.


## ATE Setup and Practical JTAG Access on HBM ATE

Modern HBM ATE platforms (Advantest T2000/V93000, Teradyne Magnum/UltraFLEX) provide dedicated JTAG resource cards with TCK rates programmable from 1 kHz to 100 MHz. For HBM post-stack test, the JTAG channel is typically assigned to a single instrument in the ATE, while the main high-speed channels handle DDR5/HBM functional tests.
A typical JTAG test flow for a packaged HBM module on ATE proceeds as:
- Power on at nominal VDD/VDDQ with TAP held at TMS=1 for 5+ TCK cycles to guarantee TAP reset- Read `IDCODE` — verify against expected vendor JEDEC manufacturer ID (bits [11:1]) and part version; mismatch indicates wrong device or power failure- Execute `SAMPLE/PRELOAD` to capture operational I/O state without disturbing functional operation — useful for capturing power-on training state- Execute `EXTEST` with interposer-side DQ driven to logic '1' and '0' patterns — verify DRAM sees expected CA/DQ values by reading DRAM boundary-scan TDO chain- Run internal scan: load scan vectors via TDI, capture response via TDO, compare against ATPG-generated expected responsesKey timing constraint: `TCK` setup to `TMS`/`TDI` is typically 2 ns minimum; `TDO` hold from `TCK` falling edge is 0–15 ns for most logic die implementations. These parameters appear in the HBM JEDEC BSDL file's `AC_CONDITIONS` section and must be met by the ATE JTAG resource card's drive/sense timing.


## Key Takeaways

- HBM JESD235C mandates DFT access on the logic die; a single external JTAG TAP on the logic die hierarchically reaches internal scan chains and DRAM die via TSV-routed IEEE 1500 paths
- Boundary-scan EXTEST through micro-bumps/TSVs is the primary method for post-assembly interconnect verification without direct probe access to buried logic die pads
- ATE JTAG test flows must respect strict TAP timing parameters (TCK setup ≥2 ns, TDO hold 0–15 ns) and use STIL-format scan patterns specifying per-partition clock domain assignments
- KGD qualification requires >95% stuck-at and >85% transition fault coverage from internal scan; this data travels with the lot traveler through the packaging supply chain

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, 2021 — Section 7 (DFT requirements), Table 4 (TSV signal assignments including TAP pins)
2. **[IEEE]** IEEE Standard for Test Access Port and Boundary-Scan Architecture — IEEE 1149.1-2013 — Clause 4 (TAP controller), Clause 8 (BSDL), BC_1/BC_2/BC_7 cell definitions
3. **[IEEE]** IEEE Standard Embedded Core Test (SECT) — IEEE P1500 / IEEE 1500-2005 — Wrapper cell architecture used for per-DRAM-die scan access within HBM stack
4. **[Paper]** HBM Test Methodology for 2.5D Packages — Kang et al., 'Known-Good-Die Testing of HBM2 in 2.5D Packages,' IEEE ITC 2018, DOI:10.1109/TEST.2018.8624710
5. **[Book]** Boundary-Scan Testing: A Practical Introduction — K. Parker, 'The Boundary-Scan Handbook,' 4th ed., Springer, 2022 — Chapter 9 covers stacked-die and 3D-IC JTAG topologies
6. **[Datasheet]** Advantest T2000 HBM DFT Application Note — Advantest, 'HBM3 KGD and Stack Test Using T2000 JTAG Resource,' App Note AN-T2000-HBM-DFT-001, 2022

## Additional Learning: Hierarchical TAP via IEEE 1149.7 (cJTAG) in HBM

Some next-generation HBM implementations are adopting IEEE 1149.7 (compact JTAG, cJTAG) to reduce the TAP pin count from 4+optional to 2 pins (TCKC and TMSC) — important in advanced packaging where every bump is precious. cJTAG uses a star-2 topology where a single 2-wire cJTAG host on the interposer can address multiple HBM stacks sequentially without requiring separate TAP signals for each stack. The cJTAG controller on each logic die implements the OAW (One-to-All Write) and one-to-one addressing specified in IEEE 1149.7-2009, and is backward-compatible with IEEE 1149.1 four-wire mode via the Scan Path Linker (SPL) state machine.
