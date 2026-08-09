# HBM-PIM: Processing-in-Memory Architecture & AiM Testing

*Sunday, Aug 09 2026*

*Module 13.2 — Emerging Technologies & Future Directions*

## HBM-PIM Architecture Overview

Processing-in-Memory (PIM) for HBM integrates arithmetic compute units—primarily multiply-accumulate (MAC) engines—directly inside each DRAM bank of the HBM stack. Rather than shipping data across the package to a GPU or CPU for computation, the **PIM unit** operates where the data resides, eliminating the off-chip bandwidth bottleneck known as the _memory wall_.
Samsung's commercial implementation, marketed as **AiM (Artificial Intelligence Memory)** or **HBM-PIM**, was introduced in 2021 with the Aquabolt-XL (HBM2-based). The architecture places a **Programmable Computing Unit (PCU)** near the sense amplifiers of every DRAM bank. Each HBM2 die has 16 banks; with 8 dies per stack, a single HBM-PIM device contains 128 independent PIM execution units operating simultaneously.
- **Bank-level parallelism:** Each bank's PCU fetches operands from its own sub-array rows, computes independently, and writes results to a dedicated output register.- **Global Register File (GRF):** A small SRAM buffer shared across banks within a pseudo-channel holds weights for GEMM operations, reducing redundant DRAM reads.- **Pseudo-channel awareness:** HBM2's pseudo-channel mode (two 32-bit channels per die) is preserved; PIM commands are issued per pseudo-channel.

## JEDEC JESD238 — HBM-PIM Standard

JEDEC standard **JESD238** (released 2022) formalises HBM-PIM as an extension of the HBM2E electrical and logical interface. It defines additional command encodings and mode register fields that coexist with standard HBM2/2E commands.
Key JESD238 additions:
- `PIM_OP_MODE` bit in Mode Register 0 (**MR0[14]**) — switches the device between _DRAM mode_ (normal memory operation) and _PIM mode_ (MAC execution enabled).- **PROGRAM** command: loads a micro-kernel (up to 32 instructions) into the PCU instruction SRAM using the address bus as an instruction word.- **PIM_GRF_WRITE / PIM_GRF_READ**: burst-transfer 16×FP16 weight vectors into/out of the GRF without leaving PIM mode.- **PIM_EXECUTE**: triggers the PCU to begin executing the loaded kernel across all enabled banks simultaneously.- Result data is written to a dedicated **PIM Output Register (POR)** row and read back via a standard READ command to that address.JESD238 supports **FP16** and **BF16** precision natively; INT8 is handled via software emulation within the PCU kernel.


## DRAM–Logic Integration Techniques

Integrating compute logic inside a DRAM array demands a manufacturing process that can handle both dense capacitor cells and planar CMOS logic on the same wafer—or at least on the same die stack. Samsung's HBM-PIM uses a **modified DRAM peripheral process** for the PCU, placing it in the row-decoder and sense-amplifier periphery region rather than the cell array itself, avoiding cell-array area penalty.
- **Sense amplifier coupling:** The PCU input multiplexer is AC-coupled to the bitline sense amplifier output, allowing bank data to feed the MAC adder tree in the same cycle as the sense operation—effectively a zero-latency data path.- **Local SRAM (LRF):** A 128×FP16 Local Register File per bank buffers partial sums, avoiding result write-back to DRAM cells between accumulate steps.- **Power gating:** Each PCU has an independent power gate controlled by the pseudo-channel arbiter; banks in DRAM mode gate their PCU to avoid leakage penalty on standard memory transactions.- **Area overhead:** Samsung reported ~2.5% die-area overhead per bank for the PCU in Aquabolt-XL, using a 1Ynm HBM2 process node.SK Hynix's **AiM** (Accelerator-in-Memory, distinct naming from Samsung's) takes a similar bank-level approach in their HBM2E variant, with differences in GRF organisation and supported precision types.


## AiM Test Program Design

Testing HBM-PIM requires a two-layer strategy: the full standard HBM2/2E DRAM test suite _plus_ a PIM-specific test layer that validates compute correctness, mode transitions, and isolation between DRAM and PIM paths.
**Test flow for PIM compute validation:**
- **1. DRAM baseline:** Run full MARCH-C+ or MATS++ pattern on all banks to confirm array integrity before enabling PIM mode.- **2. Mode entry:** Issue MRS to set `MR0[14]=1`. Verify the device acknowledges by reading back MR0 and checking `PIM_OP_MODE` is set; confirm DRAM transactions are blocked (expect JEDEC-defined error response or NO-OP).- **3. GRF load:** Issue `PIM_GRF_WRITE` with known FP16 weight vectors (e.g., all-ones to simplify expected result). Verify via `PIM_GRF_READ`.- **4. Input preload:** Return to DRAM mode, write known input activation vectors to target rows, re-enter PIM mode.- **5. PROGRAM + EXECUTE:** Load a 4-instruction GEMV kernel (load, MAC, accumulate, store), issue `PIM_EXECUTE`, poll status register until done flag is set.- **6. Result readout:** Exit PIM mode, read POR address, compare against software-computed golden reference (using the same FP16 rounding mode).- **7. Isolation check:** Verify that banks _not_ targeted by PIM_EXECUTE retain their original DRAM data unchanged.ATE platforms (Teradyne J750/UltraFLEX, Advantest T2000) require custom PIM command vectors and extended vector depth for the PROGRAM sequence; vector depth of 2M+ entries is typical for full-coverage PIM testing.


## PIM Yield & Fault Classification

HBM-PIM adds a new fault category that has no analogue in standard DRAM: **compute faults**. These must be distinguished from DRAM cell faults during test to assign correct repair or reject decisions.
- **MAC accumulation error:** A stuck-at or bridging fault in the adder tree produces a consistent offset in the computed result. Detected by comparing MAC output to golden reference across multiple input patterns.- **GRF retention fault:** The weight SRAM loses content under elevated temperature or voltage stress. Stress-read after burn-in at T<sub>MAX</sub> + 10°C.- **Mode-switch hang:** Failure to transition cleanly between DRAM and PIM modes; often caused by power-gate timing margin issues. Detected by repeated mode-entry stress (1000 cycles) at V<sub>DD</sub> min.- **Bank-level crosstalk:** PIM execution in one bank induces bitline noise in an adjacent bank under simultaneous DRAM read. Test by running PIM_EXECUTE on odd banks while reading even banks; compare read data to expected.- **Repair interaction:** Row-spare activation in a bank disables that bank's PCU in some implementations; post-repair PIM coverage must re-verify affected banks.Industry data from Samsung (ISSCC 2021) showed PIM-specific yield loss of approximately **1.2–1.8%** above baseline DRAM yield for the first-generation Aquabolt-XL, primarily from GRF SRAM single-bit fails and mode-switch timing marginalities.


## Key Takeaways

- HBM-PIM places bank-level MAC units near sense amplifiers to eliminate the memory-wall bandwidth bottleneck for AI workloads.
- JEDEC JESD238 defines PIM_OP_MODE (MR0[14]), PROGRAM, GRF_WRITE/READ, and PIM_EXECUTE commands that coexist with the HBM2E command set.
- AiM test programs must validate DRAM integrity first, then separately verify MAC compute correctness, GRF retention, mode-switch reliability, and bank isolation.
- New fault classes—MAC accumulation errors, GRF retention fails, mode-switch hangs, and bank crosstalk—require PIM-specific test vectors beyond the standard DRAM suite.
- Row-spare activation can silently disable a bank's PCU; post-repair re-verification of PIM compute coverage is mandatory.

## References

1. **[JEDEC]** High Bandwidth Memory with Processing-In-Memory (HBM-PIM) — JESD238A, JEDEC Solid State Technology Association, 2022
2. **[IEEE]** HBM-PIM: An Industry-First Whole-MnM Solution for Satisfying the Insatiable Bandwidth Demands of AI Architectures — Kwon et al., IEEE ISSCC 2021, Session 25.4, pp. 342–344
3. **[Paper]** Hardware Architecture and Software Stack for PIM Based on Commercial DRAM Technology: Industry Product — Lee et al., Proc. 48th ISCA, 2021, pp. 43–56
4. **[IEEE]** A 16nm 128 GB/s 1ynm HBM2E-PIM DRAM with Bank-Level Parallelism for AI Processing — Kim et al., IEEE ISSCC 2022, Session 11.6
5. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — JESD235C, JEDEC, 2021 — baseline HBM2E spec extended by JESD238
6. **[Datasheet]** Aquabolt-XL: Samsung HBM2-PIM with in-memory processing — Samsung Semiconductor, Product Brief v1.2, 2021; available via Samsung Developer

## 🔍 Additional Learning: ECC Interaction with PIM Compute Error Detection

When HBM-PIM operates over an ECC-enabled DRAM array, a single-bit error in an input activation row that is corrected by on-die ECC before the MAC unit reads it will silently alter the computation result—the MAC sees corrected data but the test program's golden reference was computed against the originally written (uncorrected) data. This creates a false-pass scenario: the PIM result matches the corrected-data golden reference but the underlying DRAM cell fault is masked. To expose this interaction, PIM test suites should include deliberate single-bit injection via column-repair override, verifying that the UECC status register flags the event while the PIM result is quarantined and the cell is flagged for row-redundancy repair.
