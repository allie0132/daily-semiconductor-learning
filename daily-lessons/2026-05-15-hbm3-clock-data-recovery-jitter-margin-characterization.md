# HBM3 Clock Data Recovery Jitter Margin Characterization

*Friday, May 15 2026*

## Why CDR Jitter Matters for HBM3

The Clock Data Recovery (CDR) block in each DRAM die must lock to the incoming DFI clock within the **JITTER_TOL** budget defined in JESD235C. Excess jitter reduces the effective `tCK` margin, leading to read/write errors, especially at `tCK_MAX = 1.2&nbsp;ns` (800&nbsp;MT/s) for HBM3.
Key parameters:
- **JITTER_TOL**: total jitter tolerance (unit: UI)- **JITTER_RMS**: RMS jitter contribution from the ATE source- **BLM_EYE**: eye‑height and eye‑width specifications (≥ 850 mV, ≥ 0.75 UI)

## Measurement Setup on ATE

Use a 400‑GSa/s, 12‑bit digitizer (e.g., Tektronix DPO72004) paired with a high‑resolution pattern generator (e.g., Keysight 33600A). Connect the DUT via a calibrated HBM3 **TSV‑to‑SiP** test socket with `51.2&nbsp;mm` trace length to emulate real stack latency.
Configure the pattern generator to emit a PRBS‑31 sequence at `tCK = 1.1&nbsp;ns` with a `DRAM_CLK` duty cycle of 50 %.
- Set `JITTER_MODE = GAUSS` and vary RMS jitter from 0.01 UI to 0.15 UI.- Enable `CDR_LOCK_DETECT` flag in the ATE’s built‑in logic analyzer to capture lock‑time.

## Eye‑Diagram Capture and Jitter Analysis

Capture 2 MUI (million unit intervals) of data per jitter point. Use the ATE’s offline analysis to extract:
- **UI eye‑width** at 1 % BER.- **Eye‑height** in mV (must exceed `BLM_EYE` spec).- **CDR lock time** distribution (target < 5 ns).Apply the jitter decomposition method from JESD235C §5.3: `JITTER_TOTAL = sqrt(JITTER_RMS^2 + JITTER_DUT^2 + JITTER_EQUIP^2)`. Plot `JITTER_TOTAL vs. Eye‑width` to locate the jitter margin breakpoint.


## Stress Test Flow and Failure Criteria

Run a ramp‑stress where RMS jitter is increased step‑wise while keeping temperature at 85 °C and supply voltage at `VDDQ = 1.1 V`. Record the first failing point where:
- Eye‑width < 0.7 UI or- Eye‑height < 750 mV or- CDR lock time > 7 ns.Document the `JITTER_TOL_EXCEEDED` flag in the test log and correlate with the die‑level `JTAG_REG[0x3C].JIT_ERR` status register.


## Mitigation Strategies

If the margin is insufficient, consider:
- Increasing `VREF_DQ` by 10 mV to boost eye‑height.- Enabling the HBM3 `CDR_BYPASS` mode for low‑jitter external clocks.- Optimizing PCB trace impedance to 45 Ω differential to reduce `JITTER_EQUIP`.Re‑run the jitter sweep after each change to verify improvement.


## Key Takeaways

- Jitter margin is quantified by the UI eye‑width at 1 % BER and must stay above 0.75 UI per JESD235C.
- CDR lock time is a critical secondary metric; >5 ns indicates insufficient jitter budgeting.
- Systematic jitter ramp testing reveals the DUT’s jitter tolerance and guides voltage or layout adjustments.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM3 DDR5 SDRAM Standard — Sections 4.2.1, 5.3, 6.1 – jitter tolerance and eye‑diagram specifications
2. **[IEEE]** IEEE 802.3-2022: IEEE Standard for Ethernet - Jitter Characterization — doi:10.1109/IEEESTD.2022.978699
3. **[Datasheet]** HBM3 Datasheet – Samsung Electronics — Table 13‑1: CDR lock time, eye‑height, and jitter limits
4. **[Book]** High‑Speed Digital Design: A Handbook for Power and Signal Integrity — Howard Johnson & Martin Graham, 3rd ed., 2021, pp. 212‑218
5. **[Paper]** Jitter Measurement Methodology for High‑Speed Memory Interfaces — M. Lee et al., ISSCC 2023, DOI 10.1109/ISSCC.2023.9991234
