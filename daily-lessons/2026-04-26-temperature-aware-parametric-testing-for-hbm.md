# Temperature‑Aware Parametric Testing for HBM

*Sunday, Apr 26 2026*

## Why Temperature Matters in HBM Parametrics

HBM operates from -40 °C to 125 °C, and its key analog parameters (V\_DDQ, V\_DD, V\_REF, pull‑up/down resistances, and on‑die termination) drift with temperature. JEDEC JESD235C defines temperature corners for DC and AC tests because small changes in **R\_PU** or **C\_term** can cause eye‑closure at high data rates.
Temperature‑induced variations affect:
- IO voltage window (V\_DDQ ± 10 % typical)- Impedance of the PHY (Z\_0 30 Ω ± 10 % at 500 °C) - Leakage currents (I\_leak up to 2 µA per pin at 125 °C)

## Test Flow Overview

The flow consists of three loops:
<ol>- **Cold‑Start Sweep**: -40 °C → 0 °C, step 10 °C. Measure V\_DD, V\_DDQ, and on‑die termination (ODT) resistance.- **Hot‑Ramp Sweep**: 25 °C → 125 °C, step 15 °C while exercising MBIST to capture dynamic power.- **Thermal‑Stability Hold**: Hold at each corner for 30 s to let thermal gradients settle before sampling.</ol>At each corner record:
- Static I‑V curves for V\_REF pins (JEDEC JESD235 4.5)- AC S‑parameter of the PHY (S11, S21) up to 8 GHz- Eye diagram at 3 Gb/s and 6 Gb/s per pseudo‑channel

## Key Measurement Techniques

**On‑Die Termination (ODT) Extraction**: Use a vector network analyzer (VNA) with a `TRM‑2000` probe‑card; calibrate to the probe tip (TRL). Measure S11 at 0 dBm, convert to resistance via `R = Z0 * (1‑|S11|)/(1+|S11|)`. Repeat at each temperature corner.
**Leakage Current Mapping**: Employ a low‑noise pico‑ammeter (`Keysight B2985A`) on each V\_DDQ pin while biasing at nominal voltage. Capture trend vs. °C, compare to the JEDEC limit of 2 µA/°C per pin.
**Eye‑Diagram Stress**: Generate PRBS‑31 traffic on all pseudo‑channels simultaneously. Use a high‑bandwidth oscilloscope (`Tektronix DPO72004`, 20 GHz) with a differential probe (`PDH‑250`) positioned on the interposer V\_DDQ lines. Record eye‑height and eye‑width at each temperature.


## Data Analysis and Pass/Fail Criteria

Plot each parameter versus temperature and apply linear regression to extract slope (Δparameter/°C). Compare to JEDEC‑defined limits:
- V\_DDQ window drift ≤ ± 8 % over –40 °C to 125 °C (JESD235 5.2.1)- ODT resistance variation ≤ 15 % (JESD235 5.3.4)- Leakage increase ≤ 1 µA/°C per pin (JESD235 5.4.2)If any slope exceeds the spec, flag the device for re‑binning or schedule a repair flow (e.g., via spare TSV redundancy).


## Practical Tips for ATE Implementation

When programming the ATE (e.g., `Advantest T2000`), use `SMU` blocks with temperature‑compensated calibration tables. Insert a `WAIT(30s)` after each temperature transition to avoid thermal lag. Leverage parallel channel groups to run MBIST while the parametric sweep is idle, maximizing throughput.
For interposer probing, ensure probe‑card thermal expansion matches the silicon‑on‑glass coefficient (<0.5 ppm/°C) to prevent mechanical drift that would corrupt high‑frequency S‑parameter measurements.


## Key Takeaways

- Temperature corners dramatically affect HBM voltage windows, ODT resistance, and leakage currents.
- Use calibrated VNA S‑parameter measurements and pico‑ammeter leakage scans at each corner to meet JESD235 limits.
- Integrate thermal holds and MBIST activity into the ATE flow to capture both static and dynamic temperature effects.

## References

1. **[JEDEC]** JEDEC Standard JESD235C: High Bandwidth Memory (HBM) Test Specification — Sections 4.5, 5.2‑5.4, 7.1
2. **[IEEE]** Temperature‑Dependent Electrical Characterization of 3D‑Stacked DRAM — IEEE Trans. Device Mol. Syst., vol. 14, no. 3, 2022, pp. 456‑466
3. **[Book]** HBM2E and HBM3 Signal Integrity Guidelines — M. Kim, "3D IC and Advanced Packaging", Springer, 2023, Chap. 6
4. **[Web]** Advantest T2000 ATE User Manual – Temperature Sweep Functions — https://www.advantest.com/manuals/t2000
5. **[Datasheet]** Keysight B2985A Low‑Noise Picoammeter Datasheet — Keysight Technologies, Rev B, 2021
