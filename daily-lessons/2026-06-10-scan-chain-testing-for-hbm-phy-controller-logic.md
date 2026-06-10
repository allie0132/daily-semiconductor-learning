# Scan Chain Testing for HBM PHY & Controller Logic

*Wednesday, Jun 10 2026*

*Module 4.7 — DFT & Built-In Test*

## Scan Cell Architecture and Chain Insertion in the Base Die

Every sequential element in the HBM base-die controller and PHY digital logic is replaced during synthesis with a **mux-D scan flip-flop**: a 2:1 multiplexer feeds either the functional data path (`D`) or the scan-in (`SI`) signal to the flop's data input, selected by `SE` (scan enable). When `SE=1`, every flop in the design becomes a stage in one or more long shift registers — the scan chains.
DFT tools (e.g., Tessent, DFT Compiler) stitch these cells into balanced chains during place-and-route, minimizing routing congestion. Because the base die contains multiple asynchronous clock domains — per-channel PHY byte clocks, the core controller clock, a JTAG TCK domain, and DFD (debug) clocks — scan chains are **partitioned per clock domain**, with **lockup latches** inserted at every domain-crossing boundary in the chain to prevent shift-clock skew from corrupting data as it crosses domains.
- Typical base-die scan chain count: tens to low hundreds, balanced to within a few flops of each other to minimize shift-cycle overhead.- Lockup latches (transparent during one clock phase) absorb clock-skew-induced race conditions between adjacent domains in the same chain.- Scan chains are wrapped per IEEE 1500-style core boundary so the PHY and controller cores can be tested independently of each other and of the DRAM array.

## Test Compression: Reducing Pattern Volume for Multi-Million-Gate Logic

An HBM base die's controller and PHY logic can exceed tens of millions of gate-equivalents across 16+ channels. Full, uncompressed scan (one ATE channel per chain) would require impractical pin counts and pattern depth. Instead, designs use **embedded deterministic test (EDT)**-style compression: an on-chip **decompressor** fans a small number of external scan-in channels out to hundreds of internal chains, and a **compactor** (typically an XOR/MISR-based network) folds hundreds of chain outputs back down to a few external scan-out channels.
Compression ratios of 100:1 to 1000:1 are common, dramatically cutting both ATE channel requirements and test time. The compactor's XOR network means a single failing scan cell can corrupt multiple compacted output bits, so designs add **X-masking** logic to block unknown (X) values — from uninitialized RAMs, analog macros, or asynchronous CDC paths — from propagating into the compactor and masking real failures.
- Decompressor/compactor ratio is chosen during DFT architecture planning, balancing ATE pin count against pattern count and diagnostic resolution.- X-bounding logic (clamping muxes) is inserted at known X-sources: PLLs, analog PHY macros, and memory BIST interfaces.

## Fault Models and ATPG: Stuck-At and At-Speed Transition Testing

Automatic Test Pattern Generation (ATPG) targets two primary fault models for HBM controller/PHY logic:
- **Stuck-at faults**: each net modeled as permanently stuck at 0 or 1. This is the baseline DC fault model; production targets typically exceed **99% stuck-at coverage** of testable faults.- **Transition (delay) faults**: each net modeled as having an extra rising or falling delay large enough to cause a capture violation at the functional clock period. This catches resistive vias, marginal timing paths, and small-delay defects that stuck-at patterns miss entirely — critical for PHY logic operating near multi-GHz boundaries.At-speed transition testing uses either **launch-on-capture (LOC)** or **launch-on-shift (LOS)** sequencing: the pattern shifts in at a slow scan-shift frequency (often 10-50 MHz, limited by ATE channel bandwidth and lockup-latch timing), then two fast clock pulses at the **functional period** launch and capture the transition before the result is shifted out. Coverage targets for transition faults are typically **92-97%**, lower than stuck-at because many paths are untestable due to false paths or multicycle exceptions.


## On-Chip Clock Controllers for At-Speed Capture in PHY Domains

The HBM PHY operates its DQ/DBI lanes at multi-Gbps rates (6.4-9.6 Gbps for HBM3/3E), far faster than any practical scan-shift clock. To apply transition patterns at the true functional rate, the base die includes an **on-chip clock controller (OCC)** — a small state machine fed by the PHY's PLL/DLL — that generates exactly two (or a short burst of) at-speed pulses on the functional clock during the capture window, then returns control to the slow shift clock.
Each clock domain in the design (core logic, per-channel PHY, command/address domain) typically has its own OCC, and ATPG must be domain-aware: a pattern launching a transition in the PHY domain while capturing in the core domain requires both OCCs to be sequenced correctly relative to each other (multi-clock or 'skewed-load' ATPG). Asynchronous CDC paths between the PHY SerDes domain and the core controller are usually **excluded from scan ATPG** entirely — these are validated instead through functional BIST loopback (PRBS pattern generators/checkers) rather than structural scan, because no static timing relationship exists to generate a valid at-speed scan pattern.
- OCC pulse generators are themselves DFT-testable structures and must be verified first via a low-speed 'OCC functional check' before at-speed patterns are trusted.- A **scan flush / chain-integrity test** (shift a known pattern through every chain at slow speed with no capture) is always run first to confirm chain continuity before applying compressed at-speed patterns.

## Scan Diagnostics and Per-Channel Yield Learning

When a compressed scan pattern fails, the ATE logs the failing pattern number, cycle, and compactor output bit(s). **Volume diagnosis** software (e.g., Tessent Diagnosis, Synopsys SpyGlass) inverts the compression network to back-trace the failure to a small candidate set of physical scan cells, then cross-references the design's layout database to produce ranked physical defect locations for failure analysis (FA) — including TSV-adjacent cells, where stacking-induced mechanical stress is a common systematic defect source.
Because the HBM base die replicates PHY and controller logic per channel (and per pseudo-channel for HBM3+), scan chains are often instantiated **per channel**, allowing the ATE to isolate a fault to a specific channel's logic — directly correlating with which DRAM channels later fail functional or MBIST testing. This per-channel structural test runs at wafer sort, before known-good-die (KGD) determination, alongside MBIST (array test) and LBIST (logic self-test) to build a complete digital test coverage picture prior to stacking.


## Key Takeaways

- HBM base-die scan chains use mux-D scan cells partitioned per clock domain with lockup latches at domain crossings, then compressed 100:1-1000:1 via an EDT-style decompressor/compactor to make tens of millions of gates testable within ATE channel limits.
- ATPG targets both stuck-at (>99% coverage) and at-speed transition faults (92-97% coverage); transition patterns require an on-chip clock controller (OCC) per clock domain to generate functional-rate capture pulses, since shift clocks run far slower than the multi-Gbps PHY.
- Asynchronous CDC paths between the PHY SerDes domain and core logic are excluded from scan ATPG and instead verified via functional PRBS loopback BIST; per-channel scan chain instantiation enables direct correlation of structural failures to specific HBM channels for yield learning.

## References

1. **[IEEE]** IEEE Standard Testability Method for Embedded Core-based Integrated Circuits — IEEE 1500-2005 — core test wrapper and test access architecture, applied to HBM base-die PHY/controller cores
2. **[Book]** Essentials of Electronic Testing for Digital, Memory, and Mixed-Signal VLSI Circuits — Bushnell & Agrawal — Chapters 7-8: scan design, ATPG fault models, and at-speed delay testing
3. **[Datasheet]** Tessent Scan and ATPG User's Guide — Siemens EDA — Embedded Deterministic Test (EDT) compression architecture and on-chip clock controller (OCC) configuration
4. **[Datasheet]** DFTMAX / TestMAX Compression Architecture — Synopsys — scan compression ratios, X-masking, and multi-domain at-speed pattern generation for SoC and PHY designs
5. **[Paper]** Cost-Effective At-Speed Test Generation Using On-Chip Clock Controllers — IEEE International Test Conference (ITC) — PLL-based capture clock generation and multi-clock skewed-load ATPG

## 🔍 Additional Learning: Cell-Aware Test for Advanced-Node HBM Base Die Logic

Standard stuck-at and transition fault models only target a cell's primary input/output pins, missing realistic defects — resistive bridges and opens — buried inside the transistor-level cell layout, which become more probable at the 5-7 nm nodes now used for HBM4-class base dies. Cell-aware ATPG runs SPICE-level fault simulation on each library cell to generate extra patterns targeting these intra-cell defects; this typically adds only 1-3% to overall fault coverage but catches defect classes that conventional scan test escapes and that would otherwise surface as latent field failures.
