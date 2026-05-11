# HBM3 Clock Data Recovery (CDR) Characterization

*Monday, May 11 2026*

## Why CDR Characterization Matters

HBM3 uses a 2.4 Gbps (per lane) DDR4‑compatible data rate with an embedded Clock Data Recovery (CDR) block in the PHY. Variations in TSV inductance, on‑die termination, and supply noise impact the CDR lock time, jitter tolerance, and eye opening. Accurate CDR characterization ensures compliance with JESD79‑4B <em>HBM3 Spec</em> timing margins and reduces yield loss.


## Measurement Setup and Instrumentation

Use a high‑performance ATE (e.g., Advantest T2000) with:
- Built‑in BIST pattern generator for PRBS‑31 at 2.4 Gbps per lane.- External clock source with `CLK_REF` jitter < 5 ps RMS.- On‑board `CDR_LOCK` probe (pin‑named `CDR_LOCK_N`) for lock detection.- Eye‑diagram analyzer configured for `JITTER_EYE` measurement (JESD22‑A113). 

## Key Test Patterns and Parameters

Run the following patterns per JEDEC JESD79‑4B §5.5:
- **Pattern 1:** PRBS‑31, 2.4 Gbps, capture 10 k UI, measure `CDR_LOCK_TIME`.- **Pattern 2:** Fixed‑pattern “0101…”, 2.4 Gbps, introduce `VREF` offset ±10 mV to evaluate CDR tracking.- **Pattern 3:** Eye‑margin sweep – vary `VDDQ` by ±5 % and record eye height/width.

## Data Analysis and Acceptance Criteria

Extract these metrics:
- `CDR_LOCK_TIME` ≤ 4 ns (JESD79‑4B 4.2.3).- Jitter tolerance: total jitter ≤ 0.12 UI @ 95 % confidence (IEEE 802.3 Clause 74). - Eye height ≥ 150 mV and eye width ≥ 0.8 UI after worst‑case VDDQ/temperature.Plot lock time vs. temperature (–40 °C to 125 °C) to verify linearity; non‑linear drift > 0.2 ns/°C indicates TSV‑induced phase noise.


## Debugging Common CDR Issues

When lock time exceeds limits:
- Check `VREF_DQ` calibration registers (`REG_VREF_DQ0..3`); adjust with `WR_VREF` command.- Inspect supply noise on `VDDQ` with a high‑resolution oscilloscope; add on‑die decoupling if RMS > 30 mV.- Verify TSV resistance using JEDEC 5.2.3 TSV‑DC‑R test; high resistance (> 10 mΩ) can degrade phase detector.

## Key Takeaways

- CDR lock time and jitter directly reflect TSV and supply integrity.
- Use JEDEC‑defined PRBS‑31 patterns and lock‑detect pins for repeatable measurements.
- Correlation of lock time drift with temperature uncovers phase‑noise sources.

## References

1. **[JEDEC]** JEDEC JESD79‑4B: HBM3 Standard — Section 4.2.3, 5.5, and Table 5‑1, 2022
2. **[IEEE]** IEEE 802.3-2022 Clause 74: PHY CDR Requirements — IEEE Std 802.3-2022, Clause 74, 2022
3. **[Book]** Advantest T2000 ATE User Manual — Advantest Corp., 2023, pp. 78‑85
4. **[JEDEC]** JESD22‑A113: Electrical Test Methods for High‑Speed Serial Interfaces — Revision 2, 2021
5. **[Datasheet]** HBM3 PHY Design Guide – Samsung — Samsung Electronics, HBM3‑PHY‑01, Rev C, 2023
