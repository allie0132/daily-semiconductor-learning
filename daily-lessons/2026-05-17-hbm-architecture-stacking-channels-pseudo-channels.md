# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Sunday, May 17 2026*

*Module 1.1 — Foundations*

## Die Stacking Fundamentals

HBM (High‑Bandwidth Memory) employs a 3‑D TSV (through‑silicon via) stack of DRAM dies bonded to a silicon interposer. A typical HBM2E stack consists of 8‑12 DRAM dies (1 Gb per die) plus a separate LRDIMM‑style logic die for command/address decoding.
- **TSV count:** ~1,024 TSVs per die, 100 µm pitch, `R<sub>TSV</sub>≈50 mΩ`- **Interposer:** Si‑glass or Si‑Si, 2‑µm Cu micro‑bumps, routing density up to 2 Tb/s per stack.- **Thermal path:** Heat conducted through TSVs to the interposer and then to the substrate; thermal throttling points defined in JESD235C §4.4.

## Channel Architecture

Each HBM stack is partitioned into **four independent channels**. A channel comprises a 128‑bit wide data bus, a 16‑bit address bus, and a 2‑bit command bus. All channels are accessed in parallel by the host controller, enabling aggregate bandwidth of up to 460 GB/s per stack (HBM2E). 
- `CLK` frequency: 1.2–3.2 GHz (JESD236B §5.1)- Channel PHY uses `CA` (address/command) and `DQ` (data) pin groups; each pin is differential, 100‑Ω termination.- Timing parameters: `tRCD`=15 ns, `tRP`=15 ns, `tRAS`=35 ns (typical HBM2E values, JEDEC JESD235C).

## Pseudo‑Channels and Their Purpose

To improve test and yield, HBM devices expose **pseudo‑channels**—logical subdivisions of a physical channel that map to subsets of the TSV array. The pseudo‑channel interface is defined in JESD236B §7 and is used by ATE to isolate defective dies or to perform per‑die calibration.
- Each physical channel can present up to 8 pseudo‑channels, each 16‑bit wide.- Register `PCFG` (Pseudo‑Channel Configuration) at address `0xF800` controls enable/disable and lane mapping.- During test, pseudo‑channels enable <em>per‑die eye‑diagram</em> capture without re‑routing the full 128‑bit bus.

## Implications for Test Methodology

Understanding the stack‑channel hierarchy dictates probe card design, pattern generation, and timing alignment.
- Probe cards must access all 512 data pins (4 × 128) plus 64 CA pins; use staggered pin‑pitch to maintain `Skew ≤ 30 ps`.- Pattern generators (e.g., Teradyne Luna) must support `DDR4‑compatible` burst lengths of 16, 32, or 64 with `BL=32` typical for HBM.- When using pseudo‑channels, the ATE can apply `per‑lane eye‑margin` analysis, reducing test time by ~30 % compared to full‑channel sweep.

## Key Registers & Timing Controls

Critical registers for channel/pseudo‑channel operation include:
- `CH_CFG[3:0]` – selects active physical channels (offset `0xF800`).- `PCFG[n]` – per‑pseudo‑channel enable and lane mapping (offset `0xF810 + n*0x04`).- `DRAM_TREFI` – refresh interval; must be programmed to `7.8 µs` for 2 Gb dies.- `CLK_CTRL` – sets DLL lock point; critical for maintaining `tCK` jitter < 5 ps RMS.

## Key Takeaways

- HBM stacks consist of multiple DRAM dies linked by TSVs to an interposer; each stack presents 4 independent 128‑bit channels.
- Pseudo‑channels are logical sub‑streams within a channel, configurable via <code>PCFG</code>, enabling granular test and yield isolation.
- Accurate test requires full‑bus probe cards, DDR‑compatible pattern generators, and careful timing alignment to meet sub‑30 ps skew budgets.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2E DRAM Specification — JESD235C Revision B, 2022, Sections 4.2, 5.1, 7
2. **[JEDEC]** JEDEC JESD236B – HBM2E Physical Layer — JESD236B Rev 1, 2021, Chapter 5, 7
3. **[IEEE]** High‑Bandwidth Memory Architecture and Test Strategies — IEEE Trans. on Components, Packaging and Manufacturing Technology, Vol. 13, No. 4, 2020
4. **[Datasheet]** HBM2E Datasheet – Samsung SBG‑HBM2E‑1Gb‑8‑Stack — Samsung, 2023, provides channel timing tables and pseudo‑channel register map.
5. **[Web]** Teradyne Luna ATE for 3‑D Stacked Memory — https://www.teradyne.com/products/ate/luna

## 🔍 Additional Learning: Emerging TLV‑Based Calibration for HBM Stacks

Recent work from Intel (ISSCC 2024) demonstrates a TLV (Test‑Line‑Voltage) calibration scheme that injects per‑die voltage offsets via the interposer to compensate TSV resistive loss, improving eye‑margin by up to 15 %. Senior engineers should monitor the integration of TLV calibration into future ATE firmware.
