# HBM3 Write‑Boost Voltage Swing Stress Test

*Wednesday, May 13 2026*

## Purpose and Scope

The write‑boost operation in HBM3 uses a higher DRAM VDDQ voltage (typically 1.2 V ± 10 %) during a write burst to improve timing margins. This lesson covers how to program stress patterns, capture VDDQ waveforms, and assess compliance with JESD235C §5.3.2.


## Register Configuration

Configure the DRAM mode registers on each stack using the `MRW` command:
- **MR0[WRBOOST_EN]** = 1 to enable write‑boost.- **MR2[WRBOOST_TMR]** = 0x3C (30 ns) to set the boost duration.- **MR3[WRBOOST_V]** = 0x5 (select 1.2 V boost level per JESD235C Table 14).For ATE, use the `SET_MR` primitive with the address and data fields as defined in the <em>HBM3 Test Flow Specification</em> (see reference 2).


## Stimulus Generation on ATE

Program the pattern generator to issue a sequence of `WRITE` bursts followed by `PRECHARGE` commands, repeating the cycle 10 000 times. Typical timing:
- tRCD = 12 ns- tWRBOOST = 30 ns (set via MR2)- tRP = 12 nsUse the `BURST_WRITE` macro with `BL=16` and `CMD_RATE=2T`. Ensure the ATE’s `VDDQ` driver can swing to 1.3 V peak‑to‑peak; calibrate with a `VPP` measurement on a dummy load before the DUT.


## Measurement and Analysis

Capture VDDQ on‑die using a high‑bandwidth (≥2 GHz) differential probe connected to a sampling oscilloscope. Measure:
- Peak voltage during boost (**VBOOST**) – must be ≤ 1.35 V (JESD235C §5.3.2).- Rise/Fall time – ≤ 1 ns to meet **tVDDQ_RISE** spec.- Boost window jitter – ≤ 200 ps rms.Export the waveform data to the ATE's analysis software and compute `ΔV = VBOOST – VDDQ_NOM`. Plot a histogram of ΔV across all stacks; outliers beyond 3σ indicate possible power‑grid issues.


## Failure Modes and Mitigation

Typical non‑compliant observations:
- **Overshoot > 1.35 V**: caused by insufficient decoupling on the stack‑through (ST) via; add 0.1 µF BGA‑type caps per 4 mm².- **Slow rise > 1 ns**: driver impedance too high; adjust ATE `VDDQ_DRIVER_IMP` to 30 Ω.- **Jitter > 200 ps**: clock feed‑through coupling; reduce `CLK_DRIVE_STRENGTH` or insert a series termination on the clock path.Re‑run the stress test after each hardware change to confirm compliance.


## Key Takeaways

- Enable write‑boost via MR0, MR2, MR3 and verify timing with JESD235C §5.3.2.
- Use high‑bandwidth VDDQ probing to capture boost voltage, rise time, and jitter.
- Identify overshoot, slow rise, and jitter root causes and mitigate with on‑die decoupling, driver impedance tuning, and clock termination.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) Specification — Section 5.3.2 Write‑Boost Voltage, Table 14, 2022
2. **[Datasheet]** HBM3 Test Flow Specification – Micron — Micron Technologies, Rev B, 2023, http://www.micron.com/hbm3-test-flow
3. **[IEEE]** IEEE 802.3bt Power Over Ethernet – Voltage Swing Considerations — IEEE Std 802.3bt-2021, §7.4, 2021
4. **[Book]** Advanced Signal Integrity for 3D‑Stacked Memories — M. Patel, "Signal Integrity in 3D Packages," Springer, 2021
5. **[Paper]** Characterization of Write‑Boost in HBM3 Using TSMC 3D-IC Test Chips — S. Lee et al., ISSCC 2023, pp. 124‑125
