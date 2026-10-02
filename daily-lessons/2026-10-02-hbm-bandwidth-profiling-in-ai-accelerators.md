# HBM Bandwidth Profiling in AI Accelerators

*Friday, Oct 02 2026*

*Module 18.1 — HBM in Production AI Systems & Silicon Lifecycle Management*

## The Roofline Model — Foundational Framework

The roofline model, introduced by Williams et al. (2009), characterizes application performance as bounded by either peak compute throughput (FLOP/s) or peak memory bandwidth (GB/s). For HBM-equipped AI accelerators, the roofline ceiling is defined by two lines: the compute roof (e.g., 312 TFLOP/s for BF16 on H100 SXM5) and the memory bandwidth roof (3.35 TB/s for HBM3e on H100).
Arithmetic intensity (AI) — measured in FLOP/byte — determines which ceiling applies. At the ridge point intersection (~93 FLOP/byte for H100), operations transition from memory-bound to compute-bound. Typical LLM inference decode phases operate at 1–10 FLOP/byte, firmly in the memory-bound regime, making HBM bandwidth the primary performance limiter and the primary test target.
- **Memory-bound region:** Performance ∝ bandwidth; attainable GFLOP/s = AI × BW- **Compute-bound region:** Performance ∝ compute; HBM bandwidth is underutilized- **Ridge point:** AI = Peak FLOP/s ÷ Peak BW (H100: ~93 FLOP/byte)

## HBM Bandwidth Measurement Methodologies

Accurate bandwidth profiling requires distinguishing achieved bandwidth from theoretical peak. NVIDIA's NSight Compute reports `l1tex__t_bytes_pipe_lsu_mem_global_op_ld.sum` and equivalent store metrics, aggregated across all SMs. For HBM3e on H100, the 5120-bit bus at 6.4 GT/s yields 3.35 TB/s theoretical; production silicon typically achieves 93–97% of this in streaming kernels.
Test engineers should profile three bandwidth regimes: **peak streaming** (sequential 256-byte transactions, all channels loaded), **random access** (64-byte scattered reads testing page hit/miss ratios), and **mixed read/write** (simulating attention mechanism access patterns). The JEDEC HBM3 specification (JESD238A) defines tRCD, tCL, and tRP parameters that directly impact random-access bandwidth — deviations from spec manifest as bandwidth degradation in non-streaming workloads.
- Streaming BW test: `cudaMemcpy` throughput benchmark or DGEMM with large leading dimensions- Random BW test: Pointer-chasing microbenchmark (bucket size = 4KB to exceed row buffer)- Mixed test: Transformer attention kernel with Q×K^T matmul (memory-bound at sequence length &gt;512)

## ATE-Level Bandwidth Validation

At wafer sort and final test, ATE bandwidth validation uses pattern-based approaches rather than live AI workloads. The Advantest T2000 and Teradyne Magnum Series support burst-mode HBM test patterns that stress all 8 channels simultaneously at full data rate. Key ATE test parameters for bandwidth coverage include:
- **Channel utilization:** All 8 channels (HBM3) or 16 pseudo-channels active simultaneously; test patterns must achieve &gt;90% bus utilization to stress bandwidth ceiling- **Row buffer hit rate control:** Alternate between sequential (same row) and random (cross-row) address patterns to exercise both tCL-dominated and tRCD-dominated latency paths- **Refresh interference:** Schedule tREFI boundary crossings during sustained bandwidth patterns to measure bandwidth degradation during refresh (typically 1–3% BW loss)- **Temperature sweep:** Bandwidth degrades ~0.5% per 10°C above 85°C junction temperature due to DRAM cell leakage effects on timing marginsBandwidth test coverage should include a **walking-ones column address test** to detect stuck-at faults on data lines that only manifest under full-width burst access.


## Memory-Bound vs Compute-Bound Diagnostic Techniques

Distinguishing bandwidth bottlenecks from compute bottlenecks is critical for post-silicon validation. Hardware performance counters provide the primary diagnostic path. On AMD Instinct MI300X (HBM3, 5.3 TB/s), the `rocprofv2` tool exposes `TCC_EA_RDREQ_32B` and `TCC_EA_WRREQ_32B` counters that measure actual HBM transaction counts.
For a workload at known arithmetic intensity AI<sub>measured</sub>, the test engineer computes: **Expected BW = FLOP_count ÷ AI_measured**. If measured HBM bandwidth significantly exceeds this, the workload has unexpected memory traffic — a signal for cache thrashing, ECC scrubbing activity, or address mapping inefficiency. If measured bandwidth is below theoretical peak for a memory-bound kernel, suspect: channel imbalance (uneven row address distribution), tRFC refresh stalls, or thermal throttling reducing DRAM clock.
- Channel balance diagnostic: Compare per-channel transaction counts; &gt;10% imbalance indicates address hashing deficiency- ECC scrub traffic: SECDED correction events add read-modify-write cycles that inflate measured bandwidth beyond application demand- Thermal throttle detection: Monitor DRAM temperature sensor (HBM3 exposes per-stack temp via JEDEC Mode Register MR4)

## Production Test Correlation: ATE to System-Level

Correlating ATE bandwidth pass/fail with system-level AI workload performance is a key discipline for HBM test engineers. A common failure mode is **bandwidth-marginal silicon**: parts that pass ATE go/no-go limits but underperform in production AI systems due to timing margin loss at elevated temperatures.
Establishing correlation requires defining ATE bandwidth limits relative to system-level bandwidth requirements. For an H100-class device requiring 3.0 TB/s minimum at 80°C junction, the ATE test at 25°C ambient must account for thermal derating. Empirical correlation across multiple wafer lots typically yields a 2–4% bandwidth derating factor per 55°C junction temperature rise.
The recommended correlation methodology: (1) characterize bandwidth vs. temperature on a golden unit across the full operating range; (2) establish ATE pass limits at 25°C that guarantee spec compliance at worst-case temperature; (3) validate the model quarterly against system-level field data from production AI servers using hardware telemetry (GPU NVML or AMD ROCm SMI bandwidth counters).
- JEDEC JESD235D (HBM3) Annex A provides timing derating tables for temperature correlation- MR4[3:0] temperature range bits allow in-system DRAM temperature readback without external sensors

## Key Takeaways

- The roofline model's ridge point (FLOP/s ÷ GB/s) determines whether HBM bandwidth or compute is the bottleneck — LLM inference decode is firmly memory-bound at 1–10 FLOP/byte
- ATE bandwidth tests must exercise all channels simultaneously at >90% bus utilization with both sequential and random address patterns to cover real workload behavior
- Bandwidth-marginal silicon passes ATE at 25°C but fails system requirements at operating temperature — thermal derating correlation (2–4% per 55°C) must be built into ATE limits
- Per-channel transaction counter imbalance >10% and ECC scrub traffic are leading indicators of bandwidth shortfall in production AI systems

## References

1. **[Paper]** Roofline: An Insightful Visual Performance Model for Floating-Point Programs and Multicore Architectures — Williams, Waterman, Patterson — CACM 2009, Vol 52 No 4, pp 65–76
2. **[JEDEC]** JESD238A — High Bandwidth Memory (HBM3) DRAM Standard — JESD238A, October 2022, sections 4 (Electrical), 8 (AC Timing Parameters)
3. **[Datasheet]** NVIDIA H100 SXM5 GPU Architecture Whitepaper — NVIDIA Corporation, 2022 — HBM3 bandwidth specs, NVLink/PCIe topology, memory subsystem architecture
4. **[Datasheet]** AMD CDNA3 Architecture — MI300X Technical Reference — AMD Publication #57647 Rev 1.0, 2023 — HBM3 configuration, 5.3 TB/s aggregate bandwidth, UMC controller
5. **[IEEE]** Demystifying the Roofline Model for HBM-Based AI Accelerators — IEEE Hot Chips 34, 2022 — Practical roofline analysis for transformer workloads on HBM3 hardware
6. **[JEDEC]** JESD235D — High Bandwidth Memory (HBM) DRAM — JESD235D, 2023, Annex A — AC timing derating tables for temperature and voltage variation

## 🔍 Additional Learning: Effective Bandwidth vs. Peak Bandwidth: The 70% Rule

In production AI training clusters, sustained HBM effective bandwidth rarely exceeds 70% of peak due to non-unit-stride access patterns, ECC overhead, and refresh interference. This '70% rule of thumb' is empirically validated across H100 and MI300X deployments at hyperscalers. Test engineers should calibrate ATE bandwidth limits to 75% of theoretical peak as a practical production floor — silicon achieving only 68–70% of peak in streaming tests warrants marginal-bin classification even if it technically passes the JEDEC minimum.
