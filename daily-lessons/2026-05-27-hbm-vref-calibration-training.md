# HBM Vref Calibration & Training

*Wednesday, May 27 2026*

*Module 2.5 — Electrical Testing*

## Why Vref Calibration Matters

HBM’s high‑speed DRAM channels operate with a 1.2 V I/O supply and a narrow differential voltage swing (`VREF`=0.6 V ± 30 mV). Any offset degrades eye margin, increases BER, and may cause link failure during the JEDEC‑defined link training.
Calibration aligns the receiver's sense amplifiers to the transmitted swing, compensating for process variation, temperature, and board‑level mismatches.


## Calibration Register Overview (JEDEC JESD235C)

The memory controller (MC) uses the following JEDEC‑defined registers for Vref handling:
- `VREF_CTRL (0x0A30)` – enables/disables calibration, selects source (DAC or external pin).- `VREF_DAC_VALUE (0x0A34)` – 10‑bit code driving the on‑chip DAC (0‑1023 maps to 0.55‑0.65 V).- `VREF_STATUS (0x0A38)` – reports calibrated value, lock status, and any error flags.All writes must be performed via the MC’s configuration space using a 32‑bit AXI transaction with `APB` timing (t<sub>CL</sub>=1 ns, t<sub>CH</sub>=1 ns).


## Standard Calibration Flow

1. **Pre‑condition**: Power‑up HBM stack, wait for `INIT_DONE` (≤ 10 µs).<br/>2. Set `VREF_CTRL.EN=0` and program `VREF_DAC_VALUE` to midpoint (512).<br/>3. Issue `CAL_START` bit in `VREF_CTRL` – MC begins a 5‑sample sweep across the DAC range (step = 2 LSB).<br/>4. For each step, MC captures the eye‑opening metric from the DFE (Digital Front End) and stores it in a temporary buffer.<br/>5. After the sweep, MC selects the DAC code that yields the maximum eye‑height (> 150 mV) and writes it back to `VREF_DAC_VALUE`.<br/>6. Set `VREF_CTRL.EN=1` to lock the value. Verify `VREF_STATUS.LOCKED=1`.
The entire sequence completes in **≈ 30 µs** (JEDEC spec 4.5.2), well within the boot‑time budget.


## Training Procedure Coupled with Vref

Link training (JEDEC JESD235C §5) consists of two phases: <em>Clock Training</em> and <em>Read‑Write Training</em>. Vref calibration must be finished before Read‑Write Training begins.
- **Clock Training**: MC sends `CLK_TRAIN` pattern; receiver adjusts DLL phase until the measured jitter < 5 ps.- **Read‑Write Training**: MC transmits `TRAINING_PATTERN_A/B` on each lane. The receiver’s DFE and Vref are co‑optimized – the MC iterates over Vref offsets (± 5 LSB) while monitoring `BER` for each pattern.Final link is declared `TRAINED` when BER < 10⁻¹² and Vref offset < 2 LSB for all lanes. Any lane that fails the Vref window triggers a lane‑re‑train without power‑cycle.


## Practical Debug Tips for Senior Engineers

• Use the ATE’s `VREF_MEAS` probe (e.g., Advantest T2000) to capture the actual on‑chip Vref voltage; compare against `VREF_DAC_VALUE` conversion table in the datasheet.
• If lock fails, check for excessive board‑level crosstalk: verify `VDDQ` decoupling and `VREF` routing impedance < 30 Ω.
• Temperature drift: schedule a re‑calibration after every 20 °C change; many MCs support automatic `PERIODIC_CAL_EN` (default period = 100 ms).


## Key Takeaways

- Vref calibration is a deterministic 5‑step sweep defined in JESD235C and must complete before read‑write training.
- Key registers are VREF_CTRL, VREF_DAC_VALUE, and VREF_STATUS; correct sequencing is critical for lock confirmation.
- Training couples Vref with DLL phase; a successful link requires BER < 10⁻¹² and Vref offset ≤ 2 LSB across all lanes.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Specification — Section 4.5.2 Vref Calibration, Section 5 Link Training
2. **[IEEE]** IEEE Std 1855‑2022 – HBM System Architecture — pp. 12‑14, training flow diagram
3. **[Datasheet]** Micron HBM2E Datasheet – MT40A512MHA-062E — Table 8‑2 DAC code to Vref voltage conversion
4. **[Web]** Advantest T2000 Application Note 2023 – Vref Measurement for HBM — https://www.advantest.com/appnotes/t2000/hbm_vref
5. **[Paper]** Huang et al., "Adaptive Vref Calibration for Stacked DRAM", ISSCC 2022 — Proposes a dynamic Vref window algorithm reducing BER by 30 %.

## 🔍 Additional Learning: Dynamic Vref Adjustment During Runtime

Modern MCs can vary Vref in 1 LSB steps while the link is active, using real‑time eye‑monitoring to compensate for temperature or voltage droop, eliminating the need for a full re‑train after a thermal event.
