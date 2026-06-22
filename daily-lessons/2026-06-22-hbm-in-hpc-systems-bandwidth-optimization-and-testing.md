# HBM in HPC Systems: Bandwidth Optimization and Testing

*Monday, Jun 22 2026*

*Module 6.6 -- Advanced Topics*

## HBM Bandwidth Architecture in HPC

High-bandwidth memory achieves its extraordinary throughput through a combination of a wide parallel interface, 3D stacking, and short interconnect distances via silicon interposer or embedded bridge. A single HBM2e stack exposes a **1024-bit** wide interface organized as 8 channels x 128 bits, with each channel subdivided into two 64-bit pseudo-channels in HBM2e/HBM3. Operating at up to 3.6 GT/s per pin, a single HBM2e stack delivers ~460 GB/s; HBM3 reaches ~665 GB/s per stack at 6.4 GT/s.
In HPC system designs, multiple stacks are placed in a 2.5D or 3D configuration around a compute die. AMD MI300X integrates 8 HBM3 stacks for an aggregate **5.3 TB/s** of memory bandwidth, while NVIDIA H100 SXM5 achieves **3.35 TB/s** with 6 HBM3 stacks. The critical metric for test engineers is not peak bandwidth but <em>sustained bandwidth efficiency</em> -- the ratio of effective throughput to peak rated bandwidth under realistic workload patterns.
The PHY layer implements DLL-based timing calibration on a per-channel basis. JEDEC JESD235C specifies `tRCD`, `tCL`, and `tRP` timing parameters that bound worst-case bandwidth: a column access latency of CL=14 at 3.2 GT/s means 8.75 ns of latency overhead per DRAM transaction, emphasizing the importance of burst mode and access coalescing for HPC efficiency.


## Bandwidth-Bound Workloads and the Roofline Model

The **roofline model** (Williams et al., 2009) provides a quantitative framework for determining whether an HPC kernel is compute-bound or memory-bandwidth-bound. It plots achievable FLOP/s against arithmetic intensity (FLOPs per byte of DRAM traffic). The model defines two performance ceilings:
- **Compute ceiling**: peak FLOP/s of the processor (e.g., 989 TFLOPS FP8 for H100)- **Bandwidth ceiling**: peak_BW x arithmetic_intensity (GB/s x FLOP/byte)Kernels with arithmetic intensity below the <em>ridge point</em> (compute_ceiling / bandwidth_ceiling) are bandwidth-bound. For H100 SXM5, the ridge point is 989 TFLOPS / 3.35 TB/s ~= 295 FLOP/byte. Matrix-vector multiplication at ~2 FLOP/byte is deeply bandwidth-bound; dense GEMM at ~512 FLOP/byte is compute-bound.
For HBM test engineers, this model dictates the test stimulus design: HPC systems running bandwidth-bound AI inference, graph analytics, or genomics workloads will saturate HBM bandwidth continuously, creating sustained high-current conditions that GDDR-based systems rarely encounter. ATE patterns must replicate these access profiles to expose thermal and margin failures that only appear under sustained bandwidth load.


## Memory Access Pattern Optimization for Peak Bandwidth

Achieving close to peak HBM bandwidth in HPC applications requires disciplined management of access patterns at multiple levels:
- **Access coalescing**: HBM channels have a minimum burst length of BL4 (32 bytes per pseudo-channel, 64 bytes per full channel). Scattered 4-byte reads activate a full 64-byte cache line while consuming only 4 bytes -- 16x bandwidth waste. Coalescing adjacent thread accesses into aligned 128-byte transactions maximizes bus utilization.- **Bank group interleaving**: HBM3 implements 4 bank groups x 4 banks per pseudo-channel. Sequential addresses should map across bank groups to exploit `tCCDS_BG` (2 cycles) vs. `tCCDS` (4 cycles) timing advantage, raising effective bandwidth by up to 30%.- **Row buffer locality**: Keep consecutive accesses within the same DRAM row (8 KB per HBM row) to exploit open-page policy; avoid mixed sequential/random patterns that force excessive ACT/PRE cycles.- **Pseudo-channel symmetry**: Balance traffic evenly between the two pseudo-channels of each channel to avoid arbitration stall -- asymmetric loading reduces effective bandwidth by 10-25% in measured HPC traces.Software tools such as AMD `rocm-bandwidth-test` and NVIDIA `bandwidthTest` provide first-order validation; production profiling requires hardware performance counters exposed via `perf`, NVIDIA Nsight, or ROCProfiler to measure <em>HBM read/write bandwidth utilization</em> at the controller level.


## Multi-Stack Topology and NUMA Effects

Systems with multiple HBM stacks present a Non-Uniform Memory Access (NUMA) topology even within a single chip. Each compute cluster or CU group has lower-latency, higher-bandwidth access to its local HBM stack than to remote stacks accessed via the on-die interconnect fabric. This intra-chip NUMA effect is significant: on AMD MI300X, local HBM access latency is ~100 ns while remote HBM (across the die-to-die interface) incurs ~180-220 ns, reducing effective bandwidth for cross-stack traffic.
HPC software must implement topology-aware data placement -- the GPU driver and runtime (HIP, CUDA) expose APIs for explicit memory placement on specific HBM partitions. For test engineers validating multi-stack HBM systems:
- Test patterns must exercise **all cross-stack traffic combinations** to detect interconnect defects not visible in single-stack tests- Concurrent multi-stack access patterns stress the shared NoC (Network-on-Chip), potentially exposing arbitration bugs at peak bandwidth that do not appear in sequential per-stack validation- Power delivery must be validated under simultaneous multi-stack read bursts -- peak current draw can reach 150+ A for an 8-stack configuration at full BW utilization

## Testing Methodology for HBM in HPC Systems

Validating HBM for HPC deployment extends well beyond JEDEC compliance testing. The test strategy must cover three regimes:
**1. Characterization (wafer / KGD)**: Full JEDEC parametric testing per JESD235C -- AC/DC specs, timing margins (`tRCD`, `tRAS`, `tRP`), address/data eye diagrams, and DQ receiver sensitivity. Critical HPC-specific additions: measure <em>sustained bandwidth efficiency</em> over 60-second thermal soak at Tj = 85 C to catch self-heating-induced margin loss.
**2. System-level functional test (post-assembly)**: After 2.5D/3DIC integration, run stress patterns that replicate production HPC workloads: sequential streaming (STREAM benchmark equivalent), random-access patterns (GUPS), and mixed read/write at 70%/30% ratio typical of ML inference. Pattern duration should exceed thermal equilibration time (~30 s for a fully integrated package).
**3. Burn-in and reliability screening**: HBM in HPC runs hotter and at higher average utilization than consumer workloads. Elevated-voltage burn-in at VDD = 1.2V (nominal 1.1V for HBM3), junction temperature 95 C, combined with worst-case access patterns for 48-96 hours screens latent defects. The ATE must provide per-stack current monitoring at millisecond resolution to flag transient overcurrent events indicative of weak cell arrays.
Key ATE measurements: `IDD4R` (active read current), `IDD4W` (active write current), and `IDD6` (self-refresh) vs. temperature. Compare against JEDEC maximum ratings and flag units exceeding 5% of spec as marginal.


## Key Takeaways

- HBM's 1024-bit wide interface enables 460-665 GB/s per stack; HPC systems aggregate multiple stacks to reach multi-TB/s bandwidth that GDDR cannot match.
- The roofline model identifies bandwidth-bound HPC kernels (arithmetic intensity < ridge point); ATE patterns should mirror these sustained high-utilization access profiles.
- Access coalescing, bank group interleaving, and pseudo-channel balance are the primary software levers to close the gap between peak and effective HBM bandwidth.
- Multi-stack HPC configurations introduce intra-chip NUMA effects; test coverage must include all cross-stack traffic combinations and concurrent multi-stack stress patterns.
- HPC burn-in must run at elevated VDD and junction temperature with production-representative access patterns for 48-96 hours to screen latent defects not visible in standard JEDEC testing.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard -- JESD235C -- Sections 6 (AC specs/timing), 7 (pseudo-channel mode), 8 (electrical characteristics)
2. **[IEEE]** Roofline: An Insightful Visual Performance Model for Multicore Architectures -- Williams, Waterman, Patterson -- Communications of the ACM, Vol. 52 No. 4, 2009
3. **[Datasheet]** NVIDIA H100 SXM5 GPU Architecture Whitepaper -- NVIDIA 2022 -- HBM3 6-stack configuration, 3.35 TB/s aggregate bandwidth specification
4. **[Datasheet]** AMD Instinct MI300X Accelerator Architecture -- AMD 2023 Technical Reference -- 8x HBM3 stacks, 5.3 TB/s, multi-die NUMA topology
5. **[Paper]** HBM PHY Architecture and High-Speed Testing Challenges -- Synopsys -- DesignCon 2023; covers PHY DLL calibration, eye margin measurement methodology
6. **[Book]** Memory Systems: Cache, DRAM, Disk -- Jacob, Ng, Wang -- Morgan Kaufmann 2007; DRAM timing parameter analysis, Chapters 6-8

## Additional Learning: Pseudo-Channel Mode and Bandwidth Testing Implications

HBM2e and HBM3 introduce pseudo-channel (PC) mode, splitting each 128-bit channel into two independent 64-bit pseudo-channels that share a common command/address bus but have separate data buses and independent bank state machines. This halves the minimum transaction granularity from 256 bytes (full channel, BL4) to 128 bytes per PC, improving bandwidth efficiency for the sparse, irregular access patterns common in graph analytics and genomics workloads. For ATE validation, pseudo-channel mode requires that test patterns independently stress each PC -- including concurrent conflicting accesses to the shared CA bus -- to expose arbitration logic bugs where one PC starves the other under asymmetric load, a failure mode that is invisible in single-channel sequential test patterns.
