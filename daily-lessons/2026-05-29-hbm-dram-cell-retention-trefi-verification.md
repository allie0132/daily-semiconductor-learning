# HBM DRAM Cell Retention & tREFI Verification

*Friday, May 29 2026*

*Module 2.9 — Electrical Testing*

## Why Cell Retention Matters

HBM stacks use deep sub‑micron DRAM cells whose charge leaks over time. The refresh interval `tREFI` (normally 7.8 µs for JEDEC JEDEC 4‑low‑power, 15.6 µs for standard) must be met to avoid data loss. In high‑bandwidth environments, any deviation can cause silent errors at the system level.


## Key Timing Parameters

- **tREFI** – Refresh interval, defined by JEDEC JESD235C 4.3.1.- **tRFC** – Refresh command duration; the longest of `tRFCab` (all‑banks) and `tRFCpb` (per‑bank).- **tREFab** – Minimum time between successive `REFAB` commands; must be ≤ tREFI‑tRFCab.- **tREFpb** – Minimum time between per‑bank refreshes; ≤ tREFI‑tRFCpb.

## Test Flow on ATE

1. **Configure pattern generator**: issue a continuous `REFAB` sequence with a programmable delay.<br/>2. **Set delay sweep**: start at 90% of nominal tREFI and increment in 0.5 µs steps up to 110%.<br/>3. **Write‑verify‑read window**: after each refresh cycle, write a known data pattern to a subset of rows, wait the programmed delay, then read back. Use `RDC` and `WRC` commands per JESD235C.
4. **Capture failure point**: the first delay where ≥1 bit error occurs defines the effective retention limit.


## Analysis & Margin Extraction

Plot error rate vs. delay. Fit a Weibull distribution to estimate <em>tREFI_target</em> (the 99.9% confidence point). Compare against spec: `tREFI_measured ≥ tREFI_nominal × (1‑margin)`. Typical design margin is 10‑15% for temperature extremes (‑40 °C to 125 °C).


## Temperature & Voltage Corners

Cell leakage doubles roughly every 10 °C. Run the same sweep at ‑40 °C, 25 °C, 125 °C, and at ±5 % VDD. Record the worst‑case tREFI. Document the `tREFI(T,V)` lookup table for reliability sign‑off.


## Key Takeaways

- tREFI is the governing interval for DRAM cell retention; failure to meet it causes data loss.
- ATE verification uses a delay sweep on <code>REFAB</code>/<code>REFPB</code> commands combined with write‑read checks to locate the retention limit.
- Temperature and supply voltage corners must be included; the worst‑case margin is usually 10‑15% over the nominal tREFI.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2 Specification — Section 4.3.1, 4.4.2
2. **[JEDEC]** JEDEC JESD79‑4 – DDR SDRAM Refresh Timing — Annex A, defines tREFI and related parameters
3. **[IEEE]** IEEE 2022 – “Refresh‑aware Test Methodology for 3D‑Stacked DRAM” — doi:10.1109/TCAD.2022.3156789
4. **[Datasheet]** Micron HBM2E Datasheet — Table 6‑1: Timing, tREFI = 7.8 µs
5. **[Book]** Advantest T2000 ATE User Manual — Ch. 12: DRAM Refresh Test Sequences

## 🔍 Additional Learning: Dynamic Refresh Rate Scaling (DRRS) in HBM

Modern HBM controllers can lower tREFI during low‑activity periods to save power (DRRS). Verify DRRS by programming the controller’s <code>REFI_CTRL</code> register, then repeating the retention sweep to ensure the reduced interval still meets error‑free operation.
