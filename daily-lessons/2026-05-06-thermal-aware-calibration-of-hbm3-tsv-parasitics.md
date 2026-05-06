# Thermal‑Aware Calibration of HBM3 TSV Parasitics

*Wednesday, May 06 2026*

## Why TSV Parasitics Matter

Through‑silicon vias (TSVs) dominate the high‑frequency interconnect of HBM3 stacks. Their series resistance (R<sub>TSV</sub>) and shunt capacitance (C<sub>TSV</sub>) directly affect signal integrity, eye opening, and power delivery. Both parameters increase with temperature due to silicon resistivity rise (~0.7%/°C) and dielectric constant drift, potentially violating the <a href="https://www.jedec.org/standards-documents/docs/jesd235c">JEDEC JESD235C</a> eye‑margin limits.


## Modeling Temperature Dependence

Use a temperature‑dependent RC model per JEDEC JESD235C Table 5‑2:
- `R_TSV(T) = R_TSV(25°C) × [1 + α_R × (T-25)]`, where `α_R ≈ 0.007/°C`- `C_TSV(T) = C_TSV(25°C) × [1 + α_C × (T-25)]`, where `α_C ≈ -0.001/°C`Implement the model in your ATE’s waveform generator (e.g., Keysight 89600 VSA) as a temperature‑scaled S-parameter block.


## Measurement Procedure

1. Program the HBM3 controller (e.g., Micron's `HBM3_CTRL_REG[0x34]`) to enable a dedicated TSV‑test mode that routes a high‑speed PRBS (2^15‑1) onto each IO pair.
- Set `TSV_CAL_EN = 1'b1` and select the target lane via `TSV_CAL_LANE[4:0]`.2. Use the thermal chuck to stabilize the device at a set point (e.g., 20 °C, 70 °C, 100 °C). Allow 5 min for thermal soak.
3. Capture eye diagrams with the VSA and extract `t<sub>rise</sub>` and `t<sub>fall</sub>`. The change in transition time Δt correlates to ΔR+ΔC via the first‑order RC equation: `Δt ≈ 0.69·(R_TSV·C_TSV)`.
4. Repeat for three temperatures; fit a linear trend to obtain `α_R` and `α_C` for your specific stack.


## Compensation Techniques

Once α values are known, embed a runtime compensation table in the HBM3 PHY firmware:
- During **temperature‑exit** events (e.g., after a thermal‑throttle), read the on‑die temperature sensor (`HBM3_TMON_REG[0x18]`).- Lookup ΔR and ΔC from the table and adjust the ODT drive strength and DFE tap weights accordingly.Alternatively, use an adaptive equalizer that updates its coefficients every 10 µs based on the measured eye‑margin degradation.


## Validation and Sign‑off

Perform a full‑burst read/write regression at the hottest point (typically 105 °C) with the compensation active. Verify that:
- Eye‑height > 70 % of UI (JEDEC JESD235C 4.3.1).- BER ≤ 10<sup>−12</sup> over 10<sup>12</sup> bits.- Power‑up latency remains within 320 ns as specified.Document the temperature‑compensation table and the regression results in the test lot‑release report.


## Key Takeaways

- TSV resistance and capacitance drift predictably with temperature; model them using JEDEC α coefficients.
- A three‑point temperature sweep with PRBS eye capture yields accurate α_R and α_C values for each stack.
- Embedding temperature‑aware compensation in PHY firmware preserves eye margin and BER across the full HBM3 operating range.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM3 Electrical Test Methodology — Section 4.2–4.4, Table 5‑2, 2022
2. **[IEEE]** Thermal Effects on TSV Parasitics in 3D‑ICs — IEEE Trans. on Components, Packaging and Manufacturing Technology, vol. 13, no. 3, 2023
3. **[Datasheet]** Micron HBM3 Datasheet – Register Map — Micron Technology, HBM3 8‑Gb/s, Rev B, 2024
4. **[Book]** High‑Speed PCB Design for 3D‑Stacked Memory — R. Murata, *3D Integrated Circuit Design*, 2nd ed., Springer, 2021
5. **[Web]** Keysight 89600 VSA Application Note 035 — https://www.keysight.com/au/en/assets/7018-03712/application-notes/89600-AN035.pdf
