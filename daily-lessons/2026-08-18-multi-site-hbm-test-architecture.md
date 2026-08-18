# Multi-Site HBM Test Architecture

*Tuesday, Aug 18 2026*

*Module 14.4 — Production Test Automation & Cost Optimization*

## Multi-Site Testing Fundamentals

Multi-site testing (MST) runs multiple HBM devices under test (DUTs) simultaneously on a single ATE load board, sharing tester resources to amortize per-test overhead. For HBM2E and HBM3, each stack requires up to 1024 DQ lines plus command/address buses, so a dual-site board demands careful signal routing and power delivery partitioning.
The core metric is **Parallel Test Efficiency (PTE)**:<br>`PTE = (single-site test time) / (N-site test time × N)`
Ideal PTE = 1.0 represents a perfect N× throughput gain. Real production systems achieve 0.75–0.92 due to serial overheads: handler motion, DUT contact verification, and non-parallelizable calibration steps such as per-site ZQ calibration.


## ATE Resource Partitioning for HBM

Modern ATEs (Teradyne Magnum Epic, Advantest T2000) partition instrument resources per-site. Each site requires dedicated:
- **DPS channels**: VDD, VDDQ, VINT — HBM3 specifies VDDQ = 1.05 V ±3% per JESD235C §8- **Pin electronics**: 1024+ channels at ≥4.0 Gbps per pin for HBM3 Gen2- **Timing generators**: independent tCK control per site, typically ±1 ps resolution- **Pattern memory**: March C–, SCNA, and retention patterns loaded per-siteShared resources — system clock distribution, chassis power bus, handler control PLC — create potential **resource contention**. The system clock distribution must maintain &lt;50 ps site-to-site skew to ensure independent timing domains do not alias during cross-site measurement correlation.


## Resource Contention and Arbitration

Contention arises when multiple sites simultaneously request shared ATE subsystems. Critical contention points in HBM multi-site test:
- **DPS current sharing**: simultaneous high-current draws from sites sharing a supply rail cause voltage droop, producing false margin failures. Mitigation: per-site bulk capacitance ≥470 μF on the load board with individual Kelvin sense-line regulation.- **Pattern sequencer**: ATEs with a single global pattern controller implement site-local branches as sub-sequences with site-select masks rather than independent program flows.- **Measurement bus**: parametric measurements (IDDS, IDDQ, ZQ calibration current) time-multiplex through a shared DMM; the scheduler serializes these while DQ stress patterns run in parallel across sites.JESD235C §6.5 specifies ZQ calibration intervals. In multi-site, ZQ commands are issued per-site in round-robin to prevent simultaneous RZQ pull-down transients from causing rail droop on shared VDD.


## Handler Synchronization Protocols

The handler (e.g., Seiko Epson NH-5000, Advantest M4841) controls device transport, thermal conditioning, and contact actuation. In multi-site setups the handler synchronizes site contact sequences with the ATE's LOAD and UNLOAD trigger signals.
Key timing interfaces:
- **HANDLER_LOAD_N**: handler asserts when all sites have valid DUT contact. ATE must not begin pattern execution until this signal is stable for ≥5 ms (contact settle per ATE vendor spec).- **EOS_N (End of Site)**: per-site signals from ATE to handler indicating pass/fail; handler bins each site independently.- **Thermal soak interlock**: for HBM tests at –25 °C or 125 °C, the handler's thermal chamber must confirm temperature within ±2 °C before asserting HANDLER_LOAD_N. Premature loading causes thermal-induced parametric scatter of up to 15% on tRCD measurements.Handler-ATE communication is implemented over digital I/O or GPIB using SEMI E148 (handler interface) or SEMI E5 (SECS/GEM) protocol.


## Optimizing Parallel Test Efficiency

Proven strategies to maximize PTE in HBM multi-site production:
- **Pattern interleaving**: while one site executes a memory-intensive March C– pattern, another runs parametric DC measurements, utilizing pin electronics and measurement resources concurrently.- **Contact redundancy check**: a fast 10 ms continuity test on all sites before the full flow aborts and re-contacts failed sites without halting passing sites.- **Thermal pre-conditioning overlap**: the ATE asserts a THERMAL_READY signal to the handler early in the unload sequence, allowing the thermal ramp for the next lot to begin during unload.- **Site-aware binning**: per-site soft-bin counters detect a degraded site (contact resistance drift, relay wear) and gracefully disable it, converting to N−1 site operation rather than stopping the lot.Real-world PTE data for HBM3 dual-site on Advantest T2000 shows improvement from 0.78 to 0.91 after applying pattern interleaving and thermal overlap, reducing effective cost-per-hour by ~14%.


## Key Takeaways

- Parallel Test Efficiency (PTE) quantifies multi-site throughput gain; target 0.85+ for cost-effective HBM production.
- Per-site DPS regulation with local bulk capacitance prevents cross-site voltage droop during high-current HBM stress patterns.
- Handler-ATE sync via HANDLER_LOAD_N and EOS_N must respect thermal soak interlocks and contact settle times to avoid parametric scatter.
- Pattern interleaving — running memory patterns on one site concurrently with DC measurements on another — is the highest single-impact PTE optimization.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C, §6.5 ZQ Calibration and §8 Electrical Specifications (VDDQ = 1.05 V ±3%)
2. **[JEDEC]** Handler Interface Standard for ATE — SEMI E148-0917, Handler-to-Tester Interface Specification, contact settle timing
3. **[IEEE]** Multi-Site Test Efficiency for High-Speed Memory — ITC 2022, Paper 14.3, Watanabe et al., parallel efficiency modeling for HBM
4. **[Datasheet]** Teradyne Magnum Epic Multi-Site HBM Application Note — Teradyne AN-2023-HBM-MS, Resource Partitioning and Handler Interface guide
5. **[Book]** Semiconductor Memory Test: Design, Principles, and Practices — Burns & Roberts, Kluwer Academic, ISBN 978-0-7923-7580-8, Chapter 12
6. **[Web]** SEMI E5 SECS-II Message Services Standard — https://www.semi.org/en/connect/standards — SEMI E5-0813, SECS/GEM handler protocol

## Additional Learning: Site-to-Site Correlation in HBM Multi-Site Test

A critical challenge in multi-site HBM test is ensuring that a device tested on site 1 yields the same parametric results as an identical device on site 2. Systematic offsets arise from PCB trace length mismatch (causing tDQSS skew differences), per-site relay aging (increasing contact resistance asymmetrically), and DPS calibration drift. Best practice is to run a golden reference HBM stack across all sites weekly and apply per-site offset correction tables stored as calibration constants in the ATE program. JESD235C Annex A provides recommended measurement conditions that facilitate cross-site correlation when followed precisely.
