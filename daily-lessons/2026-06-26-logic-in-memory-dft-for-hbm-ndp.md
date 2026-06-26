# Logic‑in‑Memory DFT for HBM NDP

*Friday, Jun 26 2026*

*Module 7.6 — Advanced Test Methodologies*

## Background: NDP Integration in HBM Stacks

Near‑Memory Processing (NDP) adds compute logic (e.g., vector engines, AI accelerators) inside the logic die of an HBM stack. The logic‑in‑memory (LiM) region shares the same PHY, clock domains, and power rails as the DRAM array, but introduces new test points: configuration registers, compute pipelines, and custom ISA.
JEDEC JESD235C defines the `MEMCONFIG` and `CAPTURE` registers used for LiM activation. Timing constraints such as `Tinit` (100 µs) and `Tproc` (max 200 ns per compute instruction) must be observable by the tester.


## DFT Insertion Points for LiM

Effective DFT for LiM relies on three insertion locations:
- **Boundary Scan (JTAG) extensions**: Add `BSCAN_LiM` cells to expose internal compute FSM states and control registers without routing extra pins.- **Embedded BIST (eBIST)**: Implement a `LiM_BIST` macro that runs a predefined micro‑kernel (e.g., 32‑bit add, dot‑product) and reports pass/fail via the DRAM `CAPTURE` register.- **Memory‑Mapped Test Registers (MMTR)**: Allocate a dedicated address window (e.g., 0xFF00_0000–0xFF00_FFFF) for `LiM_CTRL`, `LiM_STATUS`, and `LiM_ERRLOG` accessible through the standard HBM command set.

## Test Flow on ATE Platforms

Typical ATE flow (e.g., Advantest T3, Teradyne J750) for LiM DFT:
<ol>- Power‑up and perform standard `JESD209‑3` DRAM init.- Enter LiM mode via `MEMCONFIG[LiM_EN]=1` using a Write command to the MMTR address.- Run `LiM_BIST` macro; capture the `LiM_ERRLOG` vector through the `CAPTURE` command.- Use boundary‑scan scan‑chains to shift out internal pipeline counters for timing verification.- Exit LiM mode and resume normal DRAM test.</ol>Timing of the `LiM_BIST` start command must meet `Tstart` ≤ 20 ns after the DRAM `ACT` edge, a constraint verified by the ATE’s high‑resolution timing analyzer.


## Design‑for‑Test (DfT) Trade‑offs

Adding DFT structures incurs area (~0.8% of LiM die) and power overhead. Key trade‑offs:
- **Boundary‑scan depth vs. pin count**: Each extra `BSCAN_LiM` bit adds ~1.2 ps of additional scan delay, which can breach the `Tproc` budget for high‑frequency (2 GHz) NDP.- **eBIST pattern richness**: A simple arithmetic kernel provides fast coverage but may miss corner‑case micro‑architectural hazards (e.g., pipeline stalls). Extending the kernel to include conditional branches increases test time by ~15 %.- **MMTR address window size**: Larger windows ease software debug but reduce the available address space for memory‑only workloads; a 256 KB window is a common compromise.

## Failure Diagnosis Strategies

When LiM BIST fails, the `LiM_ERRLOG` register encodes a 16‑bit error class (bits 15‑12) and a 12‑bit address offset (bits 11‑0). Combine this with boundary‑scan read‑back of the `FSM_STATE` register to pinpoint whether the fault is in the register file, the compute datapath, or the interface logic.
For intermittent timing failures, use the ATE’s `Clock‑jitter analysis` mode to sweep the LiM clock edge within ±200 ps and observe the pass/fail boundary, enabling root‑cause isolation of on‑die voltage droop versus insufficient decoupling.


## Key Takeaways

- LiM DFT must be inserted at boundary‑scan, eBIST, and memory‑mapped register levels to achieve full coverage.
- ATE test flow adds a LiM enable step, runs a dedicated BIST macro, and captures error logs via standard DRAM commands.
- Design trade‑offs involve area, timing, and address‑space impacts; failure logs plus scan‑chain state give rapid diagnosis.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Specification — Section 5.4.2 LiM DFT, Table 5‑12 register map
2. **[IEEE]** IEEE 802.3bt – Power over Ethernet for High‑Power Modules — Relevant for on‑stack power budgeting, 2022
3. **[Web]** Advantest T3 Test System – LiM Enable Sequence Application Note — https://www.advantest.com/techdocs/t3_lim_enable.pdf
4. **[Paper]** Design for Testability of Embedded Compute Engines in 3D‑ICs — M. Kim et al., ISSCC 2023, pp. 112‑119
5. **[Datasheet]** HBM2E Datasheet – Samsung K4ZOE1G3B‑L — Includes LiM_CTRL register description, Rev 1.2

## 🔍 Additional Learning: Hybrid Scan‑Chain with Built‑In Logic Analyzer

Recent 2024 Samsung silicon releases embed a high‑speed logic analyzer (HLA) into the LiM scan chain, allowing conditional capture of internal datapath waveforms at up to 5 GHz. Leveraging HLA reduces the need for separate eBIST kernels and improves fault isolation for timing‑dependent bugs.
