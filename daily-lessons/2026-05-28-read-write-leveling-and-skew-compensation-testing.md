# Read/Write Leveling and Skew Compensation Testing

*Thursday, May 28 2026*

*Module 2.6 — Electrical Testing*

## Why Leveling Is Critical in HBM

HBM connects the GPU/CPU die to stacked DRAM through thousands of microbumps on a 2.5D silicon interposer. Each of the 8 independent pseudo-channels carries 128-bit data bursts at up to 6.4 GT/s (HBM3E). Unlike DDR5, there is no on-die termination negotiation — the controller must compensate for all skew sources in the bump/RDL/TSV path.
Skew sources include: **microbump-to-microbump pitch variation** (~±5 ps per 40 µm pitch change), **RDL trace length mismatch** on the interposer, **TSV delay spread** inside the HBM stack (&lt;5 µm diameter vias at 55 µm pitch), and **on-die clock distribution jitter** within each DRAM die. JESD235C Table 10 specifies a maximum AC input setup/hold window (tDQSS) of ±0.27 UI at the HBM3 data rate, leaving very little margin for uncorrected skew.


## Write Leveling: DQS-to-CK Alignment

Write leveling adjusts the phase of each pseudo-channel's DQS strobe relative to the CK clock received at the DRAM. The controller sweeps the DQS launch edge in fine-grained steps (typically 1/64 or 1/128 UI resolution in the PHY) and observes the DRAM's write leveling feedback register (Mode Register MR4[2:0] in JESD235C).
- **Procedure:** Enter write leveling mode via MPC command; drive DQS pulses while CK runs; read back the DRAM's edge-detect output; binary-search for the 0→1 transition; set PHY DQS delay to center of passing window.- **ATE implementation:** On a Teradyne UltraFLEX or Advantest T2000, the per-pin timing hardware steps DQS in &lt;1 ps increments. The training loop runs in-system via the controller's firmware or via tester pattern injection using the MBIST engine.- **Pass criterion:** All pseudo-channels must converge to DQS centering within ±0.15 UI of nominal (JESD235C §6.4). Channels that do not converge flag a marginal bump or TSV open.

## Read Leveling: DQ-to-DQS Capture Window

Read leveling centers the DQ bits within the DQS preamble window as seen at the controller PHY input. Because each DQ bit traverses a slightly different path length through the interposer RDL, per-bit deskew is required in addition to per-channel DQS phase adjustment.
The standard two-step sequence is:
- **Step 1 — Gate training:** Find the DQS preamble rising edge by issuing back-to-back READ commands and sweeping the DQS gate enable delay until the first valid edge is captured. The PHY measures the gate-open window (tDQSCK from JESD235C Table 7) which must span ≥0.5 UI.- **Step 2 — Per-bit deskew:** Write a fixed PRBS7 or checkerboard pattern, then sweep each DQ lane's delay independently; identify center of the bit's eye using a bit-error-rate scan or single-edge comparison. On HBM3E at 6.4 GT/s the UI is 156 ps, so per-bit delays must be resolved to &lt;5 ps (≈1/32 UI).ATE testers using an on-chip BIST engine can run per-bit deskew in parallel across all 8 pseudo-channels simultaneously, reducing test time by 8× vs. sequential scanning.


## Skew Compensation Testing on ATE

After leveling, a residual skew characterization sweep verifies that the trained delays hold across the full operating envelope:
- **PVT corners:** Repeat leveling at (fast-fast, 0.95V, 0°C) and (slow-slow, 1.05V, 85°C) to confirm the PHY delay range covers all corners without saturating the delay line.- **Shmoo plots:** 2D frequency vs. voltage shmoos at the leveled state reveal the yield cliff; a cliff slope steeper than 50 mV/100 MHz typically indicates residual skew rather than a bulk timing margin problem.- **Eye-diagram correlation:** For engineering characterization, a high-bandwidth oscilloscope (≥25 GHz) probed on interposer test pads confirms that the trained eye center matches the PHY's calculated optimum. Discrepancies &gt;0.05 UI indicate a model error in the skew budget.- **Stressed retrain:** After 1000 thermal cycles (−40°C to +125°C per JEDEC JESD22-A104), rerun leveling and measure the delta in trained delay values. Delta &gt;0.05 UI signals bump fatigue or TSV void growth.

## Common Failure Signatures and Debug

Leveling failures fall into three diagnostic categories:
- **No convergence (all DQS delay steps fail):** Indicates an open microbump, a shorted TSV pair, or a dead PHY lane. Isolate with a continuity test (DCR &lt;2 Ω expected) followed by a TSV chain resistance measurement from the BIST diagnostic register.- **Narrow passing window (&lt;0.2 UI):** Excessive crosstalk from adjacent power/ground bump inductance, or a marginal via stack with higher-than-spec resistance. Check PDN impedance at 1–3 GHz range; resonances above 100 mΩ correlate with narrow leveling windows.- **Channel-to-channel skew mismatch (&gt;0.1 UI spread across 8 channels):** RDL routing asymmetry on the interposer. Cross-reference the interposer layout GDS to measure trace length delta; each 1 mm of RDL at εr = 3.7 adds ~5.5 ps of delay.Systematic logging of trained delay values across a production lot in SPC charts allows early detection of process drift in interposer RDL patterning before yield falls.


## Key Takeaways

- Write leveling aligns DQS phase to DRAM CK using MR4 feedback; pass criterion is centering within ±0.15 UI per JESD235C §6.4.
- Read leveling requires two steps — DQS gate training followed by per-bit DQ deskew — to achieve <5 ps resolution at HBM3E rates.
- Production ATE skew testing must cover PVT corners and include shmoo plots; a cliff steeper than 50 mV/100 MHz suggests residual uncorrected skew.
- Convergence failures diagnose as open bumps or dead PHY lanes; narrow windows (<0.2 UI) point to PDN resonance or marginal TSV resistance.
- SPC tracking of trained delay values across lots detects interposer RDL process drift before it impacts yield.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, Tables 7 and 10, §6.4 — DQS timing specs, write leveling procedure, tDQSS and tDQSCK definitions
2. **[JEDEC]** HBM3E DRAM Standard — JESD235D (2024) — 6.4 GT/s timing budgets, per-bit deskew register map, MPC command encoding
3. **[IEEE]** 2.5D/3D IC Interconnect Test Challenges — Marinissen et al., 'Testing TSV-Based Three-Dimensional Stacked ICs,' IEEE Design & Test, Vol. 29, No. 1, 2012
4. **[Paper]** Silicon Interposer Signal Integrity for HBM — Kim et al., 'Analysis of High-Bandwidth Memory Interface on Silicon Interposer,' IEEE ECTC 2018 — RDL trace delay modeling, crosstalk characterization
5. **[Datasheet]** UltraFLEX HBM Test Solution Application Note — Teradyne AN-2019-HBM — per-pin timing hardware specs, MBIST integration for leveling training, <1 ps delay step resolution
6. **[Book]** Memory Systems: Cache, DRAM, Disk — Jacob, Ng & Wang, Morgan Kaufmann 2008 — Chapter 8: DDR/LPDDR training algorithms, foundational reference for leveling concepts

## Additional Learning: Per-Pin Adaptive Equalization Beyond Basic Leveling

HBM3E at 6.4 GT/s introduces optional continuous time linear equalizer (CTLE) settings in the PHY to compensate for frequency-dependent insertion loss in the interposer RDL. Unlike static leveling, CTLE coefficients must be re-optimized whenever the trained DQ delay changes by more than ~0.05 UI, creating a coupled adaptation loop. ATE characterization of CTLE vs. leveling interaction — sweeping both the DQ delay register and the CTLE boost setting in a 2D grid — is necessary to find the global optimum; single-parameter optimization finds only a local maximum and can underestimate true timing margin by 10–15%.
