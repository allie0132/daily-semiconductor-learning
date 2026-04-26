# TSV Continuity Testing in HBM Stacks

*Saturday, Apr 25 2026*

## Why TSV Continuity Matters

Through‑silicon vias (TSVs) are the backbone of HBM stacking, providing the high‑bandwidth electrical links between dies. Any open or short in a TSV can cause fatal data‑rate failures, latency spikes, or catastrophic thermal runaway. Continuity testing ensures that each `VDDQ_TSV` and `VSS_TSV` path meets the JEDEC <em>JESD235B</em> resistance and inductance limits (<10 mΩ, <5 nH max).


## Test Structures and Probe Options

Use dedicated **TSV continuity test pads** (often called `TSV_TST`) placed on the interposer per JEDEC <em>JESD236B</em>. Two primary probing schemes:
- **Micromanipulator needle probing:** 12‑µm tungsten tips, `R<sub>probe</sub>≈0.2 Ω`, suitable for 4‑point Kelvin measurements.- **Micro‑bump probe cards:** 30‑µm pitch cards with built‑in Kelvin fixtures, enabling simultaneous test of 8‑12 TSVs.Choose based on die count and ATE pin budget.


## Measurement Methodology

Implement a 4‑wire Kelvin measurement to isolate probe resistance:
<ol>- Apply a constant current source (e.g., 5 mA) from `I+` to `I‑` across the TSV under test.- Measure the voltage drop between `V+` and `V‑` using a high‑resolution DMM (≤1 µV). - Calculate resistance: `R_TSV = V_drop / I_source`.</ol>For short detection, use a **time‑domain reflectometer (TDR)** sweep (0.5–10 GHz) and compare the reflected amplitude to the reference model; a >2 dB deviation flags a discontinuity.


## Automated Test Flow on ATE

Integrate the continuity check into the ATE script (e.g., Advantest V93000):
`test "TSV_Continuity" {
  parametric {
    mode = "4W"
    current = 5mA
    voltage_limit = 0.05V  // 10 mΩ max
  }
  tdr {
    start_freq = 0.5GHz
    stop_freq = 10GHz
    delta = 0.1GHz
    deviation_limit = 2dB
  }
}
`Log results per TSV ID, flag fails, and invoke the repair flow if `R_TSV` > 12 mΩ or TDR deviation exceeds limit.


## Post‑Repair Verification

After laser or focused ion beam (FIB) repair, repeat the 4‑wire measurement and TDR sweep. Verify that the repaired TSV meets both resistance (<10 mΩ) and inductance (<5 nH) specs. Document the before/after values in the test database for statistical process control (SPC).


## Key Takeaways

- 4‑wire Kelvin measurement isolates probe resistance and yields sub‑10 mΩ TSV resistance.
- TDR is essential for detecting open/short defects not visible in DC resistance.
- Automate continuity checks in ATE scripts to integrate with the overall HBM test flow.

## References

1. **[JEDEC]** JEDEC JESD235B: HBM Electrical Test Specification — Section 4.3 – TSV Resistance and Inductance Limits
2. **[JEDEC]** JEDEC JESD236B: Test Structures for HBM Stacking — Section 5.2 – TSV_TST Pad Layout
3. **[IEEE]** A. Gupta et al., “TSV Characterization Using Time‑Domain Reflectometry,” IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 9, no. 4, 2021. — doi:10.1109/TCPMT.2020.3024678
4. **[Web]** Advantest V93000 Application Note 245: 4‑Wire Kelvin Measurements for High‑Speed Devices — https://www.advantest.com/appnotes/AN245_Kelvin.pdf
5. **[Datasheet]** Micron HBM3 Datasheet – Electrical Parameters — Table 6‑2 – TSV Resistance and Inductance
