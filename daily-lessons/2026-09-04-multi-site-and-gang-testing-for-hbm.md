# Multi-Site and Gang Testing for HBM

*Friday, Sep 04 2026*

*Module 16.8 — HBM Test Program Development & Characterization*

## Multi-Site vs. Gang Test Fundamentals

Multi-site testing runs **N independent DUTs** concurrently on separate tester sites — each site has its own instrument resources (VFs, timing generators, DPS). Gang testing applies a **single set of stimulus/capture resources** shared across all DUTs simultaneously, trading true independence for raw throughput.
For HBM, gang configurations typically share `DRAM clock`, command/address buses, and power supply rails while monitoring each stack's DQ response independently. The parallelism limit is set by the ATE's channel count per site card and the number of DQ lanes per HBM stack (128-bit per pseudo-channel × number of pseudo-channels).


## Resource Sharing and Parallelism Limits

HBM2E and HBM3 stacks expose **64 DQ per pseudo-channel (PC)** with two PCs per die and up to 12 Hi dies per stack (JESD235C). Sharing ATE timing resources between stacks means a single `STROBE` edge must be valid for all DUTs simultaneously — any per-DUT skew in driver loading becomes an irreducible test-floor constraint.
- **Channel count limit:** A 512-DQ HBM3 stack × 4 gang DUTs = 2048 ATE DQ pins minimum. Only ATE systems with ≥2K DQ channels per test head can sustain 4× gang.- **DPS sharing:** Shared `VDDQ` rails prohibit per-DUT supply forcing when characterising VDDQ margins — gang DUTs must target nominal; margin splits require switching to single-DUT mode.- **Timing resolution:** Shared fine-delay must satisfy worst-case DUT loading; budgeting ≥50 ps guard-band on `tDQS2DQ` skew (JESD235C Table 39) per site is common practice.

## Yield Impact and Fail Binning

Gang testing introduces **site-interaction failure modes** absent in true multi-site. A single failing DUT that pulls a shared bus low (e.g., open-drain `ALERT_n`) can mask or corrupt responses from adjacent passing DUTs — a systematic nuisance yield loss unrelated to intrinsic defect density.
Key accounting practices:
- Log **fail-by-site-context** separately: a DUT that fails only during gang operation but passes single-site is a test-floor artefact, not a product defect.- Calibrate **residual crosstalk** at qualification — inject a known aggressor pattern on one stack and measure noise coupling on idle stacks. If `VIL` is violated on any DQ, gang configuration is invalid for that pattern.- Track **site correlation** across the production run; correlation below 98% between sites for the same pattern indicates a shared-resource drift (DPS output impedance, temperature gradient on handler).

## ATE Architecture Considerations for HBM Gang Test

Modern ATE platforms supporting HBM gang test (e.g., Advantest T2000, Teradyne UltraFLEX) use **shared clock domains** with per-site programmable delays. The tester's `HFDI` (High-Frequency Driver/Input) cards drive CK_t/CK_c differentially from a single PLL source — any skew between stacks accumulates as a `tCK` window error at the DRAM input.
- Compensate socket-to-DUT delay mismatches with per-site **static delay calibration** before production: measure round-trip delay using loopback mode (JESD235C MRS field `OP[2]` for read DQ calibration) and program offset registers accordingly.- Enable **per-lane fail capture** (PPMU or logic capture) even in gang mode — this is critical for distinguishing single-DUT hard fails from bus contention events that flag all sites simultaneously.

## Cost-of-Test Optimisation and Trade-offs

Gang factor selection is a cost-of-test (CoT) optimisation: doubling the gang factor halves test time but raises **instrument capital cost** non-linearly and increases yield-loss risk from bus interactions. The sweet spot depends on defect density, stack pin count, and handler throughput.
Rule of thumb for HBM3 production: gang ×2 is almost always justified; gang ×4 requires rigorous crosstalk qualification and is viable only if raw device yield exceeds ~95%. Beyond ×4, instrument sharing risk typically erodes the CoT benefit.
- **Requalify gang configuration** on each new die revision — BEOL changes can alter driver strengths and shift the aggressor/victim coupling matrix.- Reserve **single-site mode** for characterisation, margining, and first-silicon debug regardless of production gang factor.

## Key Takeaways

- Gang testing HBM stacks shares ATE stimulus resources to multiply throughput, but parallelism is fundamentally bounded by the tester's channel count and DPS rail count per head.
- Shared bus topologies introduce site-interaction failures (bus contention, crosstalk-induced noise) that must be distinguished from intrinsic DUT defects via per-site fail logging and correlation tracking.
- The economic optimum for HBM3 gang factor is typically ×2–×4; beyond ×4, instrument cost and yield-loss risk exceed the throughput benefit in most production scenarios.

## References

1. **[JEDEC]** JEDEC Standard JESD235C — High Bandwidth Memory (HBM) DRAM — JESD235C, November 2021 — Table 39 (tDQS2DQ skew budget), MRS OP[2] loopback calibration mode
2. **[Datasheet]** Advantest T2000 HBM Test Solution Application Note — Advantest Corp., 2022 — Multi-site HBM2E/HBM3 configuration, shared PLL architecture, per-site delay calibration registers
3. **[Datasheet]** Teradyne UltraFLEX HBM Test Module AN-2021-HBM3 — Teradyne Inc., 2021 — HFDI card specification, gang test resource sharing limits, per-lane PPMU capture in gang mode
4. **[Paper]** Cost-of-Test Optimization for Advanced Memory Devices — Kim, J. et al., IEEE International Test Conference (ITC) 2020, Paper 3.1 — Gang factor selection model, yield-loss risk vs. throughput trade-off analysis
5. **[JEDEC]** JEDEC Standard JESD79-5B — DDR5 SDRAM (for shared-bus methodology reference) — JESD79-5B, September 2022 — Appendix A, bus topology crosstalk characterisation methodology applicable to HBM gang configurations

## Additional Learning: Per-Site Temperature Gradient in Gang HBM Test

In gang configurations, DUTs share a common handler plate or thermal chuck, so a temperature gradient across the handler surface imposes an uncontrolled per-DUT junction temperature spread of typically 3–8 °C. Because HBM refresh timing (tREFI) and retention margin are temperature-sensitive, a uniform tREFI pass/fail threshold applied gang-wide can under-stress the hottest DUT or over-stress the coolest. Best practice is to instrument the handler with per-socket thermal sensors, compensate handler set-point per lot, and maintain a ±2 °C Tj budget across all gang DUTs before declaring test results valid.
