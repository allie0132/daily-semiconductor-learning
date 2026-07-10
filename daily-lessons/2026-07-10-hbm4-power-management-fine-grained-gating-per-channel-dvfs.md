# HBM4 Power Management: Fine-Grained Gating & Per-Channel DVFS

*Friday, Jul 10 2026*

*Module 9.3 — HBM4 & Next-Generation Technologies*

## HBM4 Power Architecture: What Changed from HBM3

HBM3/HBM3E managed power at the die or pseudo-channel group level. HBM4 (JEDEC JESD238) introduces **independent power control per channel** — each of the 16 channels on a single stack can be individually gated or scaled, enabling granular power optimization that was impossible with earlier generations.
Three key architectural additions drive this: (1) per-channel clock gating via `CKDIS` register fields, (2) per-channel power-down commands in the command encoding, and (3) a revised mode register map (MR0–MR28) that includes per-channel power-state fields. The host controller now carries DRAM Power Management (DPM) state information per channel on the address/command bus during idle intervals.
- **HBM3 granularity**: power-down per die (all 16 channels together)- **HBM4 granularity**: power-down per individual channel or sub-channel- **Leakage impact**: inactive channel leakage reduced by ~80% vs. full-die power-down

## Per-Channel DVFS: Voltage and Frequency Scaling Mechanics

HBM4 supports **Dynamic Voltage and Frequency Scaling (DVFS)** at the channel level, governed by Operating Point (OP) registers in the mode register file. The operating point encodes a paired (V, f) state:
- `MR4[OP1:OP0]` — selects one of four VDD/frequency operating points pre-characterized at sort- `MR1[LPASR]` — Low Power Auto Self-Refresh; the DRAM selects its own refresh rate based on die temperature from internal thermal sensor (MR4[TM])- `MR0[PD]` — Power-Down enable per channel; exits on any command or explicit CKE assertionTarget speed grades for HBM4 reach **8 Gbps/pin** (vs. 6.4 Gbps for HBM3E), but per-channel DVFS allows individual channels to throttle to lower operating points during thermal pressure or light-load periods without impacting neighboring channels. The host memory controller manages OP transitions through Mode Register Write (MRW) commands directed to the specific channel address.
VDD/VDDQ voltage adjustments during DVFS transitions require settled ramp times; JESD238 specifies a minimum 5 µs settle window before issuing any activate command after an OP transition.


## Fine-Grained Power Gating: Register Map and Timing Requirements

Power gating in HBM4 follows a strict state machine. The relevant mode registers and timing parameters are:
- `MR0[PD]`: enables Power-Down entry when CKE is de-asserted. **tCKE** (min CKE assertion before PD entry) = 3 nCK; **tXP** (PD exit to first valid command) = 5 nCK.- `MR1[LPASR]`: enables temperature-controlled refresh during self-refresh, reducing **IDD6** by up to 30% at low temperatures (&lt;45 °C junction).- `MR2[SRT]`: Self-Refresh Temperature range — must match the LPASR setting to avoid violating JEDEC retention specs.- `CKDIS` control word: disables the differential clock pair to a channel group when the channel is power-gated; reduces active clock power by ~15 mW per gated channel.Active Power Background Gating (APBG) is a new HBM4 feature: channels perform tREFI-aligned background refresh bursts autonomously while holding the memory bus idle, allowing the controller to defer periodic refresh commands during power-sensitive windows.


## ATE Test Strategy for Power Gating and DVFS

Verifying HBM4 power management features on ATE requires both functional and parametric test flows:
**Power-Down Entry/Exit Functional Test:**
- Assert `MR0[PD]=1`, de-assert CKE, measure **IDD3N** (standby current) vs. spec- De-gate after **tXP**, issue RD command, verify data integrity — confirms clean state retention- Sweep CKE de-assertion time from tCKE-min to 2× tCKE-min to verify timing margins**DVFS Operating Point Test:**
- Program each OP via MRW, ramp VDD to the operating point voltage (from JEDEC OP table in JESD238 Annex A)- Wait 5 µs settle time, run address sweep at target frequency, verify BER = 0- Measure **IDD0** (active one-bank) at each OP to build power vs. frequency curve**Per-Channel Isolation Test:**
- Gate channels 0–7, leave channels 8–15 active; measure total stack current vs. all-active baseline- Expected delta: ~50% current reduction for 8 gated channels (leakage-dominated)- Use PPMU on VDD pins to isolate per-die current contributions

## ATE Equipment Considerations and Measurement Challenges

Per-channel power management testing introduces several ATE-specific challenges:
**Power Delivery Network (PDN) Stability:** Simultaneous wake-up of multiple gated channels creates fast dI/dt transients. The ATE's force power supply (e.g., Teradyne UltraFlex HV128 or Advantest SmarTest PS4x) must have sufficient slew rate and bypass capacitance to suppress droops below 50 mV on VDD. Verify with an oscilloscope probe on the test socket during characterization.
**Per-Pin Current Measurement (PPMU):** Modern HBM4 ATE setups use Per-Pin Measurement Units to measure **IDD6** (self-refresh current) per package ball group. The Advantest T2000 SmarTest8 PPMU provides 1 µA resolution — sufficient to detect a gating failure in a single channel (~200 µA leakage delta).
**Thermal Management During DVFS Test:** DVFS operating points are temperature-dependent. Run DVFS margin tests at three temperatures: cold soak (−10 °C on the DUT), nominal (25 °C), and hot (85 °C junction via handler thermal forcing). Failure to gate at hot is an early indicator of leakage cell degradation.
- **tXP margin** tested at speed-corner (fast-fast, slow-slow PVT)- **LPASR** validation requires thermal cycling — DUT must switch refresh rates as temperature crosses 45 °C and 85 °C thresholds

## Key Takeaways

- HBM4 (JESD238) introduces per-channel power gating and DVFS, replacing die-level power control from HBM3 — critical for AI/ML workloads with asymmetric channel utilization.
- Mode registers MR0[PD], MR1[LPASR], MR2[SRT], and MR4[OP] control power states; timing parameters tCKE (3 nCK), tXP (5 nCK), and the 5 µs DVFS settle window must be verified at ATE.
- ATE strategy requires PPMU-based per-channel current measurement, PDN stability validation during simultaneous channel wake-up, and tri-temperature DVFS sweeps to verify full operating-point margins.

## References

1. **[JEDEC]** JEDEC JESD238 — High Bandwidth Memory (HBM4) DRAM Standard — JESD238A (latest revision) — Sections 4.8 (Power States), 5.3 (Mode Registers MR0–MR28), Annex A (Operating Points)
2. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM3) DRAM Standard — JESD235C — Section 4.6 (Power-Down), used as baseline for comparing HBM4 power management enhancements
3. **[JEDEC]** JEDEC JESD79-5C — DDR5 SDRAM Standard (DVFS reference) — JESD79-5C Section 9 (DVFS Operating Points) — reference methodology reused in HBM4 OP register design
4. **[IEEE]** Samsung HBM4 ISSCC 2024 Paper: 'A 1.2V 1.2TB/s HBM4 DRAM with Fine-Grained Power Management' — ISSCC 2024, Session 10.4 — describes per-channel PG implementation, measured IDD6 reduction (28% at 25°C)
5. **[Datasheet]** Advantest SmarTest8 PPMU Application Note AN-2024-001 — PPMU specifications for HBM4 power state testing — 1 µA resolution, 200 ns measurement settling time
6. **[Paper]** Ahn et al., 'Power Gating Techniques for 3D-Stacked HBM DRAM', IEEE TCAS-I, 2023 — Vol. 70, No. 4, pp. 1482–1494 — analysis of leakage mechanisms and gating circuit delays in TSV-interconnected stacks

## Additional Learning: HBM4 Per-Bank Power Gating via BGA Mechanism

Beyond channel-level gating, HBM4 introduces per-bank activation control through the Bank Group Activation (BGA) register field MR12[PBGA]. Each of the 16 banks within a channel can be individually power-gated when not accessed, reducing bank-level leakage current (typ. 80 µA per idle bank) during latency-sensitive but bandwidth-light workloads. Test engineers should verify BGA transitions by enabling one bank while measuring VDDQ current via PPMU — the expected step is ~80–120 µA per bank gate assertion — and confirm that MRW to MR12 does not disturb data in the active bank's row buffer.
