# ATE Platform Setup for HBM Production Test

*Saturday, Jun 13 2026*

*Module 5.1 — ATE & Production*

## ATE Platform Landscape for HBM

HBM test cells are built on high-pin-count SoC platforms rather than legacy standalone memory testers, because the DUT is almost always a host ASIC/interposer assembly with HBM stacks attached, not a bare HBM die. The two dominant platforms are the **Advantest V93000 EXA Scale** (the modern successor in the "93K" family) and the **Teradyne UltraFLEX / UltraFLEX Plus** (with J750Ex cells still common for mixed-signal pre-screen of the host die before HBM-attach test).
On the V93000, HBM channels are driven by `HSD` (High Speed Digital) cards paired with `DPS` (Device Power Supply) modules for the multiple HBM voltage rails. On UltraFLEX, the equivalent is the `HSDIO` digital card family combined with `Matrix` DC instruments. Both platforms support per-pin programmable timing sets, which is mandatory for HBM3's sub-nanosecond data-valid windows.


## Pin Count and Channel Resource Planning

An HBM3 stack exposes a 1024-bit data interface across 16 pseudo-channels (64 bits each), plus per-channel command/address (CA), clock, and DERR/DBI pins. Including redundant TSV rows, a single stack can require well over 1,100 signal connections at the interposer. Per JESD235D, each channel also carries dedicated RDQS/WDQS strobes that must be routed to a strobe-capable HSD channel.
Resource planning starts with the per-card channel density (e.g., 32 or 64 channels per HSD/HSDIO card) and works backward to the number of test-head slots needed per site. Multi-site parallelism is usually capped not by digital channel count but by `DPS` current capacity — HBM3 VDD/VDDQ rails can draw several amps per stack during burst IDD tests, and DPS modules are shared across sites in many configurations.


## DUT Interface Board and Socket Design

The micro-bump pitch on an HBM interposer (typically 35-55 µm) is far too fine for direct ATE probing, so production test is always routed through the host ASIC's PHY pins at the package ball grid, using the DUT board (load board) as the translation layer. Sockets are high-density elastomer or pogo-pin designs (e.g., from Johnstech, Multitest, or R&D Circuits) qualified for the BGA pitch and the current density of the power rails.
Trace routing on the load board must preserve controlled impedance (typically 40-50Ω differential for HBM3 DQ/strobe pairs) and minimize skew between bit lanes, since JESD235D's AC timing budget at 6.4 Gb/s/pin leaves only tens of picoseconds of margin before `tDQSCK` and `tDQSQ` specs are violated by board-induced skew alone.


## Calibration and Power Sequencing

Before any functional or AC test runs, the cell must execute per-pin deskew calibration against a golden device or calibration standard, plus DC level calibration (VIH/VIL, VOH/VOL) using Kelvin sense lines to remove load-board IR drop from the measurement. Timing sets are generated from the JESD235D AC table and then trimmed per-site using the calibration results.
Power sequencing is handled by the DPS/Matrix instruments under program control: VDD (1.1V core), VDDQ (0.4V I/O for HBM3), and VPP (wordline boost, ~1.8-2.5V depending on generation) must ramp in a JEDEC-specified order with defined slew rates, and the ATE must monitor IDD during ramp to catch latch-up or short conditions before proceeding to functional test.


## Test Program Flow and Multi-Site Strategy

A typical production flow orders tests from cheapest/most-likely-to-catch-gross-defects to most expensive: continuity and leakage (IDDQ), then mode-register init and training, then MBIST/repair verification, then AC parametric (eye-diagram, timing margin) sweeps, and finally full functional pattern sets. Failing early stages skips the expensive AC and functional stages, which dominate test time.
Multi-site test programs share a common pin map but must independently sequence DPS rails per site to avoid simultaneous-switching power transients that could trip protection circuits across the test head. Thermal control (hot/cold chuck temperature) is applied per the test plan's corner matrix, since HBM AC margins are tightest at temperature extremes due to TSV thermal resistance variation.


## Key Takeaways

- HBM production test runs on SoC-class platforms (Advantest V93000 EXA Scale, Teradyne UltraFLEX/UltraFLEX Plus) using HSD/HSDIO digital cards and DPS/Matrix power instruments, not standalone memory testers.
- A single HBM3 stack needs 1,100+ signal pins and multiple high-current voltage rails, so resource planning for multi-site parallelism is usually limited by DPS current capacity, not digital channel count.
- Per-pin deskew calibration, Kelvin-sensed DC level calibration, and JEDEC-sequenced power-rail ramping must all complete successfully before AC/functional HBM test can produce valid results.

## References

1. **[JEDEC]** HBM3 Standard — AC/DC Timing and Power Sequencing Tables — JESD235D, sections covering tDQSCK/tDQSQ AC timing and VDD/VDDQ/VPP power-up sequencing
2. **[Datasheet]** V93000 EXA Scale Test System — HSD and DPS Module Specifications — Advantest V93000 EXA Scale platform datasheet, High Speed Digital (HSD) and Device Power Supply (DPS) card specs
3. **[Datasheet]** UltraFLEX Plus Test System — HSDIO and Matrix Instrument Specifications — Teradyne UltraFLEX Plus platform datasheet, HSDIO digital card and Matrix DC instrument specs
4. **[Paper]** Scalable ATE Architectures for High-Bandwidth Memory Production Test — IEEE International Test Conference (ITC), session on memory/HBM test cell architecture and multi-site DPS resource sharing
5. **[Book]** Mixed-Signal and Digital ATE Calibration Fundamentals — Burns & Roberts, An Introduction to Mixed-Signal IC Test and Measurement, chapters on per-pin timing and DC level calibration

## 🔍 Additional Learning: BIST Offload Is Shrinking the ATE Pin Budget

As HBM4 pushes toward a 2048-bit interface, driving every data pin from the tester becomes impractical even with the densest HSD/HSDIO cards. The industry trend is to offload array testing to on-die MBIST/Logic BIST controlled via a slim JTAG/serial interface, so the ATE only needs to handle power sequencing, BIST kickoff, and a reduced set of 'golden' AC pins for SI verification — turning future HBM test cells into lighter-weight, JTAG-centric setups.
