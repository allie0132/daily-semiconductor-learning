# HBM3 Power‑Down & Retention Mode Verification

*Monday, Apr 27 2026*

## Why Power‑Down/Retention Matters in HBM3

HBM3 introduces a **Deep Power‑Down (DPD)** state and a **Retention (RET)** mode to meet sub‑10 W system budgets. Accurate verification of entry/exit timing, voltage domains, and data‑retention integrity is essential for both silicon yield and system‑level power‑management compliance.


## Entry Sequence and Timing Checks

Follow the JESD235C §5.2 entry sequence:
- Assert `DEEP_PWRDN_N` low while `VDDQ` is >0.7 V.- Wait `tDPD_ENT` = 40 ns (max) before driving `CK` low.- De‑assert all command pins (`CS_N`, `CKE`, `ODT`) and place `DQ` in high‑impedance.Use the ATE’s high‑resolution time‑interval analyzer (TIA) to capture edge‑to‑edge latency and compare against the spec. Record any variation >5 ns as a potential violation.


## Exit (Wake‑Up) Sequence and Data Integrity

Wake‑up requires the `DEEP_PWRDN_N` to transition high, then `CK` must be re‑driven after `tDPD_EX` = 80 ns (typ). Critical checks:
- Verify `VDDQ` ramps to nominal (1.2 V) within `tVDDQ_RISE` = 150 ns.- Issue a `READ` to a known‑pattern address <em>immediately</em> after `tDPD_EX` and compare data to the pre‑sleep value.- Check `RDATA` eye diagram for **eye‑height** ≥ 80 % of V<sub>DDQ</sub> after wake‑up.Automate this loop on the tester to run >10k cycles across temperature corners (‑40 °C to 125 °C) to stress retention circuitry.


## Retention Mode Specifics

Retention mode keeps `VDDQ` powered while all banks are placed in self‑refresh. Key parameters:
- `tRET_ENT` = 30 ns to assert `RET_EN`.- Monitor `VREFDQ` stability; jitter must stay below 2 ps RMS.- Validate that `READ`/`WRITE` commands are ignored until `RET_EN` is de‑asserted.Use the ATE’s built‑in `JESD84B` pattern generator to inject a pseudo‑random bit sequence (PRBS‑31) during retention and verify no spurious activity on the bus analyzer.


## Practical Tips for ATE Implementation

1. **Probe Calibration**: Calibrate interposer probe insertion loss at 1 GHz – 4 GHz before each run; DPD power‑down can shift probe capacitance.
2. **Voltage Sequencing**: Use a programmable power supply with `VPP` slew control to meet the 5 V/µs limit for `VDDQ` ramp.
3. **Failure Isolation**: If a wake‑up data mismatch occurs, capture the `CK` eye at the exact `tDPD_EX` edge to spot timing‑skew or supply‑droop issues.


## Key Takeaways

- HBM3 DPD/RET entry/exit timing must meet JESD235C limits; use TIA for sub‑nanosecond verification.
- Data integrity after wake‑up is the ultimate pass/fail metric; automate high‑cycle stress across temperature.
- Retention mode demands strict VDDQ stability and command gating; monitor jitter and bus activity with PRBS patterns.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) 3 Specification — Section 5.2–5.4, pages 56‑68
2. **[JEDEC]** JEDEC JESD84B – HBM3 PRBS Test Methodology — Section 3.1, Table 3‑2
3. **[Datasheet]** Intel® Xeon® Scalable Processors with HBM3 Design Guide — Intel, 2025, https://www.intel.com/content/www/us/en/architecture-and-technology/hbm3-design-guide.html
4. **[IEEE]** Power‑Down Strategies for 3D‑Stacked Memories — K. Lee et al., IEEE TCAD, vol. 44, no. 3, 2023, DOI:10.1109/TCAD.2023.3267891
5. **[Paper]** Advanced Test‑Equipment for HBM3 Low‑Power Modes — A. Gupta, A. S. Borkar, ISSCC 2024, pp. 587‑590
