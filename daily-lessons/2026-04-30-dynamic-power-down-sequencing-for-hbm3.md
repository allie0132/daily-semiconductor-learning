# Dynamic Power‑Down Sequencing for HBM3

*Thursday, Apr 30 2026*

## Why Power‑Down Sequencing Matters

HBM3 devices support multiple low‑power states (Idle, Power‑Down, Self‑Refresh) to meet datacenter power budgets. Incorrect sequencing can cause latch‑up, data loss, or premature wear of the TSVs. JEDEC JESD235B defines the timing windows (tXP, tCKE, tXPD) that must be met under worst‑case temperature and voltage conditions.


## Key Registers and Commands

The following DRAM registers are used to control power states:
- `MR8[7:0]` – Power‑Down Mode Select (PD, PD‑Auto, PD‑Exit)- `MR5[2:0]` – Self‑Refresh Type (SR, SR‑Auto)- `MR1[5]` – CKE Disable (forces CKE low for power‑down)Power‑down entry is typically triggered by de‑asserting `CKE` while `MR8` is programmed for PD mode. Exit is performed by re‑asserting `CKE` and issuing a NOP or Refresh command within `tXP`.


## Timing Verification on ATE

Program the ATE to sweep the following critical intervals:
- **tCKE** – Minimum low time of CKE before entering PD (JEDEC min 0 ns, max 20 ns).- **tXP** – Minimum time after CKE rise before the first valid command (max 80 ns at 85 °C).- **tXPD** – Maximum low‑power exit latency after CKE rise (≤ 260 ns per JESD235B). Use per‑pin timing edge control on the ATE (e.g., Keysight 33600A) to create sub‑nanosecond jitter and voltage‑bias variations, then monitor the DQ response for correct NOP/Refresh execution.


## Temperature and Supply‑Noise Stress

Run the sequence at three temperature points (−40 °C, 25 °C, 85 °C) while varying VDDQ and VPP by ±5 % to emulate on‑board IR‑drop. Record failure rates and correlate with `tXP` degradation. JEDEC requires that `tXP` increase by ≤ 30 % across the temperature range; any larger shift indicates a need for redesign of the power‑delivery network.


## Reporting and Pass/Fail Criteria

Generate a parametric matrix that lists:
- Measured `tXP` vs. JEDEC max for each temperature.- Observed data‑integrity errors (BER) during exit.- Power‑up/down waveform compliance (edge‑rate, overshoot < 300 mV).A test set passes if all measured values stay within the JEDEC limits and no BER > 10⁻⁹ is detected during 10⁶ exit cycles.


## Key Takeaways

- HBM3 power‑down requires precise CKE timing; tXP is the most failure‑prone window.
- Temperature and supply voltage variations significantly affect tXP; test across the full spec range.
- Automated ATE edge‑control and BER monitoring provide a definitive pass/fail for low‑power state transitions.

## References

1. **[JEDEC]** JEDEC JESD235B – HBM3 Specification — Section 5.4 Power‑Down/Idle Timing, 2022
2. **[IEEE]** IEEE 2021 – Low‑Power State Characterization of 3D‑Stacked DRAM — doi:10.1109/IEDM.2021.964523
3. **[Datasheet]** Samsung HBM3 Datasheet — Samsung Electronics, PN: HBM3‑8Gb‑1, Rev A, 2023
4. **[Web]** Keysight 33600A High‑Speed ATE Manual — https://www.keysight.com/en/pd-1000004676%3Aepsg%3Apga/33600A-Advanced-Testing-Equipment
5. **[Book]** Advanced Packaging of High‑Bandwidth Memory — M. Lee, "Advanced 3D Packaging", Springer, 2020, Chap. 7
