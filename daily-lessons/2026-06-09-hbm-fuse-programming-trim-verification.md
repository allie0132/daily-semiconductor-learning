# HBM Fuse Programming & Trim Verification

*Tuesday, Jun 09 2026*

*Module 4.6 — DFT & Built-In Test*

## Purpose of Fuse & Trim in HBM

Fuses and trim bits configure device‑specific parameters, enable/disable built‑in self‑test (BIST) blocks, and set timing margins for high‑speed DRAM stacks. In HBM, they are programmed during wafer sort or final test and must be verified before shipment to guarantee compliance with JEDEC JESD235C and JESD235D specifications.


## Programming Sequence and Timing

The programming flow follows the **JESD235C** "HBM Fuse Programming" procedure:
- Enter `PROGRAM_MODE` via `REGISTER_FUSE_CTRL[0]` (set to 1b).- Load fuse data into `REGISTER_FUSE_DATA` (64‑bit payload per fuse row).- Issue `PROGRAM_PULSE` on `REGISTER_FUSE_CTRL[1]` with a minimum width of 200 ns (max 2 µs) to toggle the high‑voltage fuse driver.- Verify completion by polling `REGISTER_FUSE_STATUS[0]` (ready=1b) within 10 µs.Trim bits are written through `REGISTER_TRIM_CTRL` using the same pulse width but with a 10‑bit resolution (0‑1023) for voltage reference offsets.


## Verification Methodology

Verification consists of two complementary checks:
- **Read‑back integrity**: After programming, read `REGISTER_FUSE_DATA` back and compare bit‑wise to the target pattern. Any mismatch > 1 bit triggers a `FUSE_ERR` flag.- **Functional trim validation**: Execute built‑in test vectors that read analog trim‑adjusted registers (e.g., `VREF_DQ`, `VREF_CA`) and confirm that the measured voltage lies within ±5 mV of the programmed offset, as mandated by JESD235D clause 7.4.Automated ATE scripts should capture both the digital read‑back and the analog measurement via the on‑board precision ADC (≤0.2 % FSR error).


## Common Failure Modes & Debugging

Typical issues arise from insufficient `PROGRAM_PULSE` width, voltage droop on the high‑voltage fuse driver, or latch‑up during trim calibration. Use the following diagnostic steps:
- Measure the actual pulse width on the `FUSE_PROG` pin with a high‑bandwidth oscilloscope (≥1 GHz). Ensure >200 ns.- Check V<sub>DDH</sub> (programmable fuse supply) stability; it must stay within 3.3 V ± 5 % during the entire sequence.- If read‑back fails, issue a `RESET_FUSE` command (JESD235C §5.3) and re‑program.

## Integration with Built‑In Test (BIST)

After successful programming, enable the HBM BIST blocks by setting `REGISTER_BIST_EN[2:0]` according to the selected test mode (e.g., address‐walk, data‑eye). The BIST will automatically verify that programmed trims are active by sampling the calibrated VREF and checking for eye‑height ≥ 700 mV at 2 Gb/s per JEDEC JESD236.


## Key Takeaways

- Fuse programming requires a 200 ns–2 µs high‑voltage pulse and immediate status polling.
- Trim verification must combine digital read‑back with analog BIST checks of VREF offsets.
- Voltage stability of the high‑voltage fuse domain is the most common root cause of programming failures.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM Fuse Programming — Section 4.2, 2022
2. **[JEDEC]** JEDEC JESD235D: HBM Trim and Calibration — Clause 7.4, 2023
3. **[IEEE]** IEEE Transactions on Components, Packaging and Manufacturing Technology, 2023 — “Reliability of High‑Voltage Fuse Programming in 3D‑Stacked DRAM”
4. **[Datasheet]** Micron HBM2E Datasheet — Rev. 1.3, 2022, pp. 48‑52
5. **[Book]** Advanced Test Systems for 2.5D/3D Packages — J. Liu, 2021, Chapter 9

## 🔍 Additional Learning: In‑Field Fuse Re‑Programming via Firmware

Newer HBM generations support limited in‑field re‑programming of non‑volatile trim bits through a secure firmware API, allowing post‑silicon margin tuning without returning the device to the wafer‑sort line.
