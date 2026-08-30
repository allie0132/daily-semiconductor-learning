# HBM Retention & Data Integrity: Refresh Failures & Charge Leakage

*Wednesday, Aug 26 2026*

*Module 15.6 — Reliability & Qualification Testing*

## HBM Retention Fundamentals

HBM devices store data in stacked DRAM dies where each cell's charge must be refreshed within the tREF interval defined in JESD235C (`tREF = 64 ms` at 85 °C). Retention failure occurs when leakage reduces cell voltage below the sense amplifier threshold before the next refresh, causing a bit‑flip.
- Retention time is temperature‑dependent; activation energy ~0.6 eV for HBM2E.- Specification limits: maximum allowable bit‑error rate (BER) < 1×10<sup>-12</sup> after tREF.

## Refresh Failure Modes and Detection

Refresh failures manifest as either missed refresh commands or insufficient refresh voltage (`VREF` droop). ATE can capture these by monitoring the `REF` pin and checking `MR2` status bits after a refresh interval.
- Missed refresh: ATE logs a timeout on the `REF` command; triggers `ALERT_N` if enabled.- Insufficient VREF: Measure `VREFCA` voltage during refresh; compare to spec (±50 mV).

## Charge Leakage Mechanisms in HBM

Primary leakage paths include sub‑threshold conduction in the access transistor, junction leakage, and inter‑die TSV leakage. In 3D‑stacked HBM, TSV‑to‑TSV coupling can exacerbate charge loss, especially at high temperature.
- Sub‑threshold leakage follows I<sub>sub</sub> ∝ e<sup>-Vth/(nkT)</sup>; Vth shift with temperature increases leakage.- TSV leakage modeled as parasitic capacitance to substrate; measured leakage currents ~10‑100 fA per TSV at 85 °C.

## ATE Test Methodologies for Retention & Integrity

Typical flow: write pattern, apply temperature stress, wait for multiple tREF intervals, then read back and compare. Use built‑in self‑test (BIST) registers `MR0`[7:4] to count refresh failures.
- Pattern: marching 1s/0s to maximize disturbance.- Stress: soak at 125 °C for 1 h to accelerate leakage.- Read‑back: compare with expected; log any mismatches as retention errors.

## Failure Analysis and Mitigation Strategies

When retention errors are observed, failure analysis uses EMMI probing to isolate defective TSVs or die layers. Mitigation includes adaptive refresh (shorter tREF at high Temp) and error‑correcting codes (ECC) enabled via `MR3`[2].
- Adaptive refresh: ATE reads temperature sensor `TSEN` and adjusts refresh period per JESD235C Table 4‑2.- ECC: Single‑error correction, double‑error detection (SEC‑DED) reduces effective BER by >10×.

## Key Takeaways

- Retention failure in HBM is dominated by charge leakage that reduces cell voltage below sense threshold before the next refresh.
- ATE detects refresh failures by monitoring REF command timing, VREF levels, and MR status bits after stress.
- Mitigation combines adaptive refresh, temperature‑aware timing, and ECC to meet qualification BER targets.

## References

1. **[JEDEC]** JESD235C: High Bandwidth Memory (HBM) Interface — Section 4.2 defines tREF, VREFCA limits, and MR register map.
2. **[IEEE Paper]** Charge Loss Mechanisms in 3D‑Stacked DRAM — IEEE Transactions on Electron Devices, Vol. 69, No. 4, April 2022, pp. 2100‑2112.
3. **[Datasheet]** Samsung HBM2E 8GB Stack Datasheet — Revision 1.3, 2021, Tables 5‑1 (Refresh Timing) and 7‑3 (Leakage Current).
4. **[Book]** Memory Systems: Cache, DRAM, Disk — Bruce Jacob, Spencer Ng, David Wang, 2nd ed., Morgan Kaufmann, 2008, Chap. 9 (DRAM Reliability).
5. **[IEEE Paper]** Adaptive Refresh Techniques for HBM3E — Proc. IEEE International Test Conference (ITC) 2023, pp. 45‑52.

## 🔍 Additional Learning: Adaptive Refresh and Temperature Compensation in HBM3E

HBM3E introduces a built‑in temperature sensor (TSEN) that feeds a dynamic refresh controller, allowing tREF to be scaled from 64 ms at 85 °C down to 32 ms at 125 °C based on real‑time sensor readings. This reduces unnecessary refresh bandwidth while maintaining retention margins, and can be programmed via MR4[3:0] to set the temperature‑compensation slope.
