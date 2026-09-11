# HBM3E to HBM4 Migration: Test Coverage Deltas

*Friday, Sep 11 2026*

*Module 17.6 — HBM Ecosystem & Cross-Domain Test Engineering*

## HBM4 Structural Changes vs HBM3E

JEDEC JESD238 (HBM4) ratified in 2024 introduces significant architectural changes over JESD235C (HBM3E). The most impactful structural delta is the move from an 8-stack maximum (HBM3E) to a **16-hi stack** capability, doubling DRAM die count per package. Each die continues with a 128-bit channel split into two 64-bit pseudo-channels, but HBM4 mandates a **per-die UID (Unique Identifier)** register accessible via Mode Register (MR) space, enabling die-level diagnostic addressing during post-silicon test.
HBM4 also widens the base-die (logic die) interface to support **Command Address (CA) bus parity** on every transaction, adding one additional CA parity cycle. ATE vector timing must be updated to account for this extra cycle — test programs ported from HBM3E will silently drop CA parity coverage if not re-patched.
The `CATRAIN` and `WRTRAIN` procedures in JESD238 section 8 are structurally identical to HBM3E but add a new `UIDTRAIN` sequence for die-level identification. Test engineers must verify `MR63` (UID low) and `MR64` (UID high) readback per die post-stack.


## Test Coverage Deltas: What Must Change in Your ATE Program

A functional HBM3E ATE program achieves approximately 80–85% coverage on an HBM4 device when run unmodified. The remaining 15–20% gap spans four categories:
- **Stack depth coverage:** HBM3E programs probe dies 0–7; HBM4 requires die 0–15. The JEDEC row hammer (RH) mitigation register `MR62[7:4]` (ALERT_n timing) is only accessible on dies 8–15 if stack depth ≥ 9, so programs must loop die address from `000` to `1111`.- **CA parity test:** Inject intentional CA parity errors via `MR50[0]` (`CA_PAR_PERSIST`) and verify `ALERT_n` assertion within `tALERT_max` = 3.5ns. HBM3E programs lack this test entirely.- **UID readback:** Exercise per-die `MR63/MR64` across all 16 dies; verify uniqueness — duplicate UIDs indicate TSV short or scan-chain fault.- **Per-die refresh coverage:** HBM4 supports **fine-grained per-die refresh disable** via `MR59[3:0]` for thermal management; confirm BIST retention at 85°C with one die refresh-disabled.Estimated ATE program delta: 200–350 new test steps, 8–12% longer test time at equivalent parallelism.


## ATE Program Migration: Practical Steps

Migration from an HBM3E to HBM4 test program on an Advantest T2000 or Teradyne UltraFLEX follows a structured delta approach:
- **Step 1 — Update die address loop:** Change the outermost die-loop bound from `7` to `15`. Confirm the base-die's `STACK_HEIGHT` field (`MR4[2:0]`) reads `100` (16-hi) before looping.- **Step 2 — CA parity insertion:** Add a dedicated CA parity fail test block. Use the instrument's per-pin programmable drive to invert one CA bit mid-burst, then poll `ALERT_n` with a sub-ns timestamper for `tALERT` measurement.- **Step 3 — UID harvest and log:** After `UIDTRAIN`, issue back-to-back MRR (Mode Register Read) to `MR63` and `MR64` on each die. Store the 32-bit UID in ATE datalog; flag any die with UID = `0x0000_0000` as suspect.- **Step 4 — Margin re-qualification:** Re-run `Read DQ Vref` margin sweep since HBM4 targets a tighter DQ-to-DQS window: `tDQSQ_max` tightens from 200ps (HBM3E) to 160ps (HBM4) per JESD238 AC parameter table.Budget two to four engineering weeks for program delta, plus one week for correlation with device characterisation data.


## New DFT Features and Their Test Implications

HBM4 adds several DFT features absent in HBM3E that require new ATE test blocks:
- **Per-channel BIST mode:** HBM4 introduces independent BIST per pseudo-channel (PHY0 / PHY1) via `MR45[7:6]` (`BIST_CH_SEL`). HBM3E ran BIST on both channels simultaneously. ATE programs should exercise both single-channel modes to isolate per-PHY fails before running combined BIST.- **On-die ECC scrub logging:** New `MR55[3:0]` exposes a 4-bit ECC correction event counter per pseudo-channel, resettable by write. ATE must read this counter after each BIST run; non-zero values flag soft-bit defects that standard DQ fail maps miss.- **Temperature readout resolution:** HBM4 improves the on-die thermal sensor to **±1°C resolution** (vs. ±3°C in HBM3E) via `MR4[7:3]`. Test programs should validate sensor accuracy against the ATE chuck temperature at two setpoints (25°C and 95°C) to confirm sensor calibration.

## Updated ATE Hardware Requirements

HBM4's tighter AC margins and additional signal lines impose new ATE hardware demands:
- **CA bus timing accuracy:** CA parity adds one pin to the command bus. ATE load boards must route the CA_PAR pin with matched length within ±5 mil of adjacent CA lines (HBM4 CA_PAR skew budget = 25ps at die bump, JESD238 sec. 12.3).- **tCK granularity:** HBM4 at 8 Gbps (DDR4000) requires `tCK` = 500ps. ATE channels must support sub-ps edge placement; Advantest T2000 channels are rated at 0.5ps RMS jitter — marginal for HBM4 characterisation; use a dedicated HBM instrument card where available.- **Power delivery:** 16-hi stacks at full bandwidth draw up to 12W per HBM4 device (vs. 9W for HBM3E at equivalent bandwidth). ATE per-site power modules must support peak transient currents of ≥6A on VDD (1.1V) rails; verify load-board decoupling capacitance per HBM4 power design guide (JESD238 annex B).- **Test socket qualification:** 16-hi stack packages are ~0.3mm taller than HBM3E equivalents. Verify socket standoff height; mismatched standoffs cause partial contact on outer C4 bump rows.

## Key Takeaways

- HBM4 (JESD238) adds 16-hi stacks, per-die UIDs, and CA parity—each requiring explicit ATE test coverage that HBM3E programs lack.
- A direct program port from HBM3E covers ~80-85% of HBM4; the remaining delta centres on CA parity, UID readback, per-channel BIST, and ECC scrub logging.
- AC timing budgets tighten in HBM4 (tDQSQ: 200ps→160ps; tALERT: 3.5ns max)—margin sweeps must be requalified, not inherited.
- ATE load boards need CA_PAR routing within ±5 mil matched length and power modules rated for ≥6A transient per site.

## References

1. **[JEDEC]** JEDEC JESD238A: High Bandwidth Memory (HBM4) SDRAM Standard — JESD238A (2024), sections 7 (Mode Registers), 8 (Training), 12 (AC Parameters), Annex B (Power)
2. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM3E) SDRAM Standard — JESD235C (2023), AC parameter table — baseline for delta comparison
3. **[Paper]** Kim et al., 'HBM4: Challenges and Design Solutions for 16-Hi Stacked DRAM' — IEEE ISSCC 2024, session 14, pp. 14.1–14.4
4. **[Datasheet]** Advantest T2000 HBM Test Application Note — Advantest Corp., AN-T2000-HBM4-001 (2024) — CA parity test implementation
5. **[Paper]** Lee & Park, 'DFT Architecture for HBM4 with Per-Channel BIST and ECC Logging' — IEEE VLSI Test Symposium 2024, pp. 1–6, DOI: 10.1109/VTS60358.2024
6. **[Datasheet]** SK Hynix HBM4 Product Brief — 16GB 8-Channel Package — SK Hynix, HBM4-16GB-PB-v1.0 (2024) — stack height, power, bump map

## Additional Learning: HBM4 Die Repair and Stack-Level Redundancy Mapping

HBM4 introduces stack-level <strong>row/column repair</strong> that is managed at the base-die level via a new Repair Address Register (RAR) accessible through <code>MR70–MR79</code>. Unlike HBM3E, where repair fuses are blown independently per DRAM die, HBM4 allows the base-die to apply a universal repair map across the stack on power-up, reducing per-die laser fuse programming time. ATE programs must now validate repair map propagation by reading <code>MR70[7:0]</code> (Repair Status) on each die after a base-die repair-load sequence — a failure here indicates a TSV continuity fault on the repair bus, not a DRAM defect per se.
