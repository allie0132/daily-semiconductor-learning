# HBM vs DDR5 and GDDR6: Bandwidth, Power, and Density Tradeoffs

*Wednesday, May 20 2026*

*Module 1.3 — Foundations*

## Interface Architecture: Wide-and-Slow vs Narrow-and-Fast

The fundamental architectural divide between HBM and conventional DRAM is the signaling philosophy. HBM (JESD238/JESD238A) uses a **1024-bit-wide pseudo-channel bus** running at 3.6 Gbps per pin for HBM3, while DDR5 (JESD79-5B) uses a **64-bit bus** running at up to 6400 MT/s per channel. GDDR6 (JESD250D) sits between the two: 32 bits per channel at up to 18 Gbps, arranged in 8–16 independent channels per device.
HBM achieves its wide bus through **Through-Silicon Vias (TSVs)** and placement on a silicon interposer, keeping trace lengths under 1 mm. This dramatically relaxes signal integrity constraints — no DLL, DFE, or complex ODT schemes are required at the DRAM interface. DDR5 and GDDR6 by contrast must combat ISI, stub reflections, and cross-talk over PCB traces of 50–100 mm, requiring complex equalization and multi-Gbps SerDes-like signaling.
The practical consequence for test engineers: HBM requires **functional testing through the ATE TSV probe** or via the host SoC, while DDR5/GDDR6 are tested as standalone packages with standard boundary-scan and JEDEC SHMOO patterns.


## Bandwidth Comparison: Specs and Real-World Numbers

Peak bandwidth figures from current-generation devices:
- **HBM3e (JESD238A):** 1024-bit bus × 3.6 Gbps/pin = ~461 GB/s per stack; 2-stack configs (e.g., H100 SXM5) reach ~3.35 TB/s aggregate- **HBM3 (JESD238):** 819 GB/s per stack at 3.2 Gbps/pin- **HBM2e (JESD235B):** up to 460 GB/s per stack at 3.6 Gbps/pin (Samsung Flashbolt)- **GDDR6X (PAM4, NVIDIA A100/H100 PCIe):** 21 Gbps × 384-bit bus = ~1.008 TB/s (RTX 4090)- **GDDR6 (JESD250D):** 16 Gbps × 384-bit = ~768 GB/s on high-end GPUs- **DDR5-6400 (JESD79-5B):** 51.2 GB/s per channel; dual-channel = 102.4 GB/sKey insight: a **4-stack HBM3e system** delivers roughly **32× the bandwidth** of a dual-channel DDR5 platform. Even a single HBM stack outperforms all but the widest GDDR6 configurations, while consuming substantially less board area.


## Power and Energy-Per-Bit Analysis

Power efficiency is HBM's most decisive advantage at scale. The metric of interest is **energy-per-bit (pJ/bit)**, which normalizes for data rate:
- **HBM3:** ~1.0–1.2 pJ/bit (0.9V core I/O, short traces, no equalization overhead)- **GDDR6X:** ~3.5–4.0 pJ/bit (PAM4 signaling adds CDR and DFE power; 1.35V VDDQ)- **GDDR6:** ~2.8–3.2 pJ/bit- **DDR5:** ~10–15 pJ/bit (long PCB traces, ODT termination losses, 1.1V VDDQ but high-frequency SSO current)At AI training workloads requiring sustained 1 TB/s of memory bandwidth, the difference between HBM3 and DDR5 translates to **tens of watts of memory I/O power alone**. HBM's low-voltage, short-trace interface also benefits from reduced EMI and the elimination of on-board decoupling capacitor arrays needed for DDR5 simultaneous switching noise (SSN).
For test engineers: HBM IDD testing (JESD238 Section 5) specifies VDD=1.05V and VDDQ=1.05V rails, significantly lower than DDR5's VDDQ=1.1V and VPP=1.8V, simplifying ATE power supply requirements per stack.


## Memory Density and Capacity Comparison

Memory technology density is measured in both **die area efficiency (Gb/mm²)** and **system-level capacity**:
- **HBM3e:** Up to 64 GB per stack (12-Hi × 24 Gb dies + base die); stacks typically 30 mm² footprint on interposer- **HBM3:** Up to 24 GB per stack (8-Hi × 24 Gb), 9.6 mm × 7.7 mm stack footprint- **GDDR6:** 16 Gb per die standard; 24 Gb dies emerging; packages are 14 mm × 10 mm BGA- **DDR5 DIMM:** Up to 128 GB per DIMM using 3DS or monolithic 32 Gb dies; LRDIMMs extend to 256 GBGDDR6 and DDR5 benefit from **independent package form factors** — they can be soldered directly on PCB without interposer infrastructure, enabling simpler system integration at lower cost. HBM requires a **silicon or organic interposer** (Intel EMIB, TSMC CoWoS, Samsung X-Cube), adding $300–$1000 per package to substrate cost. This is the primary reason AI accelerators are expensive: a single CoWoS-L reticle substrate for an H100 exceeds the silicon cost.


## Application Selection Matrix and Test Implications

Choosing the right memory type involves balancing bandwidth, power, capacity, cost, and testability:
- **HBM:** AI/ML accelerators, HPC GPU, networking ASICs (bandwidth-critical, power-constrained, cost-insensitive)- **GDDR6/6X:** Consumer and prosumer GPUs, automotive vision SoCs (high bandwidth, moderate power, cost-sensitive, no interposer)- **DDR5:** CPU main memory, storage controllers, general-purpose compute (capacity-critical, latency-sensitive, cost-optimized)For ATE test strategy, each type requires different infrastructure: HBM demands **high pin-count probe cards** (2000+ pins for a 4-stack device), GDDR6 uses standard BGA contactors with 50-ohm transmission line calibration, and DDR5 requires **DFT-aware LPDDR5/DDR5 protocol-aware ATE channels** with ≥6.4 Gbps timing accuracy.
HBM cannot be tested in isolation post-assembly — the JEDEC JESD235/238 burn-in and characterization tests must occur either at the DRAM level (pre-stack) or through the host SoC's memory controller, making co-design of test access mechanisms (TAM) and BIST critical for yield learning.


## Key Takeaways

- HBM's 1024-bit wide bus at low per-pin data rate delivers 5–30× more bandwidth than DDR5 with ~10× better energy-per-bit efficiency, at the cost of silicon interposer integration.
- GDDR6/6X occupies a practical middle ground — higher bandwidth than DDR5 with PCB-level integration, but 3–4× worse energy-per-bit than HBM and limited to GPU-style workloads.
- HBM density tops out at ~64 GB/stack while DDR5 DIMMs reach 256 GB; capacity-critical workloads (LLM inference serving) may require multi-stack HBM or hybrid HBM+DDR5 topologies.
- Test engineers must account for HBM's unique post-assembly test constraints: no standalone package test, requiring embedded BIST and TAM access through the host SoC or via interposer probe.
- The true system cost of HBM includes the silicon/organic interposer ($300–$1000+), making DDR5 and GDDR6 strongly preferred for cost-sensitive designs despite the bandwidth penalty.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM Standard — JESD238 — defines HBM3 electrical interface, timing parameters, power states, and test modes
2. **[JEDEC]** High Bandwidth Memory (HBM3E) DRAM Standard — JESD238A — extends JESD238 to 3.6 Gbps/pin, 12-Hi stack configurations, and expanded BIST modes
3. **[JEDEC]** DDR5 SDRAM Standard — JESD79-5B — DDR5 electrical interface, 6400 MT/s data rates, on-die ECC, and power management
4. **[JEDEC]** Graphics Double Data Rate 6 (GDDR6) SGRAM Standard — JESD250D — GDDR6 interface definition, 16 Gbps per pin, channel architecture, and ZQ calibration
5. **[IEEE]** Energy Efficiency Analysis of HBM vs GDDR6 in AI Accelerators — IEEE Hot Chips 35 (2023) — NVIDIA H100 memory subsystem power breakdown; ~1.1 pJ/bit HBM3 vs 3.6 pJ/bit GDDR6X
6. **[Paper]** CoWoS Advanced Packaging for HBM Integration — TSMC Technology Symposium 2023 — CoWoS-L interposer design rules, HBM bump pitch, and signal integrity at 3.2 Gbps

## Additional Learning: HBM Pseudo-Channel Architecture and Its Test Impact

HBM3 divides each 1024-bit interface into 16 independent 64-bit pseudo-channels (PCs), each with its own command/address bus, row/column decode, and refresh controller. This pseudo-channel independence allows BIST to target individual PCs for fault isolation, which is critical because a single TSV fault in one PC does not necessarily fail the stack — repair fuses can remap defective columns. For ATE test development, this means per-PC March algorithms run in parallel with independent pass/fail results, dramatically reducing test time compared to monolithic 1024-bit wide patterns, and enabling yield binning at the PC granularity per JESD238 Section 8.
