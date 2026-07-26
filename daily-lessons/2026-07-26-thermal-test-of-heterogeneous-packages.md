# Thermal Test of Heterogeneous Packages

*Sunday, Jul 26 2026*

*Module 12.3 — Heterogeneous Integration & Advanced Packaging Test*

## Thermal Resistance in Multi-Die Heterogeneous Packages

In a heterogeneous package—such as an HBM2e/HBM3 stack bonded to a logic die via micro-bumps on an interposer (e.g., CoWoS, InFO-AiP, or EMIB)—there is no single θJC. Each die has its own junction-to-case thermal resistance path that interacts with neighboring dice through shared heat spreaders, TIM layers, and the substrate.
The composite thermal resistance network is modeled as a Cauer or Foster RC ladder per die. For an HBM3 12-Hi stack bonded to a GPU die on a CoWoS interposer, the dominant thermal paths are: HBM DRAM stack → TIM1 → lid → TIM2 → heatsink; and GPU die → TIM1 → lid → TIM2 → heatsink. The HBM stack and the logic die share the same TIM1 and lid, creating **thermal crosstalk**: power dissipated in the GPU heats the HBM stack, raising its junction temperature and degrading refresh margins.
JEDEC JESD235C (HBM3 standard) specifies a maximum junction temperature T<sub>J,max</sub> of 95°C for the DRAM array. At elevated T<sub>J</sub>, the HBM temperature sensor (on-die thermal diode or ring oscillator calibrated to temperature) reports an alarm via the CATTRIP pin, triggering a system-level throttle.


## θJC Measurement: JEDEC JESD51 Methods for Multi-Die Packages

JEDEC JESD51-14 defines the standard methodology for measuring thermal resistance of stacked packages. For a heterogeneous multi-chip module, the approach involves **electrical test vehicle (ETV) structures** that allow one die to be powered while others remain unpowered, isolating each die's contribution to the overall θJC.
The key technique is the **K-factor calibration** (also called sensitivity coefficient S<sub>VT</sub>): a temperature-sensitive parameter (TSP) on each die—typically a forward-biased diode junction, where V<sub>F</sub> changes linearly with temperature at ~−2 mV/°C—is calibrated in a temperature-controlled oven at two or more temperatures (e.g., 25°C and 125°C). The resulting S<sub>VT</sub> [mV/°C] allows in-situ junction temperature measurement during power application.
For HBM specifically, the DRAM die temperature is read via the on-die temperature sensor registers accessible through the APB (auxiliary power bus) or through JEDEC Mode Register MR4 (thermal sensor readout). Test procedure per JESD51-14:
- Apply calibration current I<sub>M</sub> = 1 mA through the TSP diode; record V<sub>F,cold</sub> at T<sub>amb</sub>- Apply heating power P<sub>H</sub> to the target die; allow thermal steady state (~5× thermal time constant)- Switch back to I<sub>M</sub>; record V<sub>F,hot</sub> within &lt;1 ms (before thermal transient decays)- Compute: θ<sub>JC</sub> = (T<sub>J</sub> − T<sub>case</sub>) / P<sub>H</sub> = [(V<sub>F,cold</sub> − V<sub>F,hot</sub>) / S<sub>VT</sub>] / P<sub>H</sub>The case temperature T<sub>case</sub> is measured with a calibrated thermocouple or RTD bonded to the package lid at the die footprint centroid, per JESD51-2A fixturing requirements.


## Structural Function Analysis and Thermal Transient Methods

Thermal transient analysis (TTA) using tools such as the Mentor (Siemens) T3Ster or Micred instrument captures the **cumulative structure function** Z<sub>th</sub>(t) of the package. When heating power is applied and then removed, the junction temperature transient is recorded and transformed via Fourier deconvolution into a Cauer RC ladder—each RC stage representing a physical thermal layer.
In a heterogeneous package, the structure function reveals distinct plateaus corresponding to: (1) the die itself (small C, small R—silicon thermal capacitance), (2) the micro-bump and interposer layer, (3) the TIM1 layer, (4) the heat spreader/lid, and (5) the TIM2/heatsink interface. Deviations from the reference (golden sample) structure function pinpoint voiding in TIM layers or delamination at bump interfaces—a critical yield and reliability indicator.
For HBM stacks, each DRAM die layer adds a discrete RC stage. A 12-Hi HBM3 stack shows 12 identifiable thermal layers in the structure function, allowing per-layer θ quantification. This is used in production to detect stack bonding failures without destructive cross-section: a collapsed RC stage indicates a voided TSV or hybrid bond interface.


## Infrared Thermography and Junction Temperature Mapping

Lock-in infrared thermography (LIT) is the gold-standard spatial technique for junction temperature mapping in heterogeneous packages. An IR camera (e.g., InfraTec VarioCAM HD or FLIR X6900sc with InSb detector, 3–5 µm wavelength) images the package surface while power is modulated at a reference frequency f<sub>lock-in</sub> (typically 0.1–10 Hz). Phase-sensitive detection suppresses background noise by √(N<sub>frames</sub>), achieving spatial resolution to ~20 µm on a bare die and temperature sensitivity to &lt;0.1 mK.
For packaged heterogeneous devices, the lid must be removed (decap) or a high-emissivity coating applied to the bare die surface (ε ≈ 0.9 with carbon spray). Critical considerations:
- **Emissivity calibration**: Silicon ε varies with doping and surface finish; use a calibrated reference die or integrate a platinum RTD on the DUT surface for spot-check correlation.- **HBM TSV stack opacity**: The stacked DRAM dies are optically opaque to IR; only the top die surface is directly measurable. Internal die temperatures must be inferred from model correlation or TSP electrical methods.- **Spatial resolution vs. depth**: IR thermography is a surface technique. For sub-surface hotspots (e.g., a buried DRAM die in a 12-Hi stack), thermal spreading blurs the signal; numerical deconvolution with thermal model is required.Photon emission microscopy (PEM) and laser voltage probing (LVP) complement IR thermography by detecting anomalous junction activity co-located with thermal hotspots, helping distinguish resistive heating from switching-related dissipation.


## HBM-Specific Thermal Test Considerations on ATE

On automated test equipment (ATE) such as the Advantest T2000 or Teradyne UltraFLEX with HBM load board, thermal testing of HBM packages requires specific instrumentation:
- **Thermal control unit (TCU)**: Forced-air or liquid-cooled temperature-forcing head (e.g., inTEST Thermal, Thermonics T-2500RE) maintains T<sub>case</sub> at ±0.1°C. For HBM junction temperature validation, the TCU is set to T<sub>J,max</sub> − (θ<sub>JC</sub> × P<sub>max</sub>) to ensure T<sub>J</sub> = 95°C at maximum HBM power.- **On-die temperature sensor readout**: HBM3 Mode Register MR4[7:0] (per JESD235C Table 22) encodes the on-die temperature in 1°C steps from 0°C to 127°C, with an accuracy of ±3°C (typical) to ±5°C (maximum). Test firmware reads MR4 via the APB interface after each pattern burst to verify T<sub>J</sub> compliance.- **CATTRIP threshold validation**: The CATTRIP pin asserts when T<sub>J</sub> > T<sub>CATTRIP</sub> (typically 85°C–95°C, set by vendor fuse or mode register). ATE test item verifies CATTRIP asserts at the correct threshold: ramp T<sub>case</sub> in 1°C steps, poll CATTRIP, record T<sub>J,assert</sub> from MR4.- **Power-temperature co-stress**: JEDEC HTOL (JESD22-A108) and HBM-specific qualification require 1000h burn-in at T<sub>J</sub> = 95°C with maximum toggle pattern (PRBS15 data, all banks active). ATE must sustain full-bandwidth HBM3 traffic (up to 819 GB/s per device) while maintaining thermal setpoint.

## Key Takeaways

- Heterogeneous packages have multiple θJC paths that interact; measure each die independently using K-factor TSP calibration per JESD51-14.
- Structural function analysis from thermal transient data resolves individual layers (TIM, interposer, TSV stack) and detects voiding without destructive analysis.
- HBM3 MR4 provides on-die temperature with ±3°C accuracy; CATTRIP assertion threshold must be validated on ATE by ramping T_case and polling both MR4 and the CATTRIP pin.
- Lock-in IR thermography provides sub-100 µm spatial temperature mapping but requires decap and emissivity calibration; internal stack temperatures need model-based deconvolution.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM Standard — JESD235C, Sections 4.3 (Thermal), 8.3 (Mode Register MR4), Annex A (Electrical Characteristics) — JEDEC Solid State Technology Association, 2022
2. **[JEDEC]** Thermal Measurement Methodology of Electronic Packages — JESD51-14: Transient Dual Interface Test Method for the Measurement of the Thermal Resistance Junction-to-Board and Junction-to-Case of Semiconductor Packages with Two Thermal Resistance Paths — JEDEC, 2010
3. **[JEDEC]** Thermal Test Vehicle Standards for Semiconductor Packages — JESD51-2A: Integrated Circuit Thermal Test Method Environmental Conditions — Natural Convection (Still Air) — JEDEC, 2008
4. **[Book]** Lock-in Thermography: Basics and Use for Evaluating Electronic Devices and Materials — O. Breitenstein, W. Warta, M. Langenkamp — Springer Series in Advanced Microelectronics, 3rd Ed., 2018, ISBN 978-3-319-99644-0
5. **[Paper]** Thermal Characterization of 2.5D IC Packages with HBM Using Structural Function Analysis — Lee, J. et al. — IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 11, No. 8, pp. 1287–1296, 2021, DOI: 10.1109/TCPMT.2021.3088542
6. **[Paper]** CoWoS-S Process and Thermal Performance of 2.5D AI Accelerator Package — TSMC Technology Symposium 2023; Chen, Y.-S. et al. — IEEE ECTC 2023, pp. 312–318, DOI: 10.1109/ECTC51909.2023.00056

## Additional Learning: Transient Dual Interface Method for θJC Accuracy

JESD51-14 specifies the Transient Dual Interface Method (TDIM) as the most accurate technique for θJC measurement, eliminating the TIM2 uncertainty that plagued older steady-state methods. Two transient measurements are taken with different TIM2 compounds (high-conductivity vs. low-conductivity) between the package lid and a cold plate; the structural function difference between the two curves converges at the same RC stage—precisely at the θJC split point—giving θJC without needing to know T_case directly. For HBM packages, TDIM is particularly important because the HBM die footprint is recessed within the overmold or interposer, making accurate T_case thermocouple placement difficult. TDIM avoids this problem entirely and is now the required method for all JEDEC-compliant θJC datasheet values.
