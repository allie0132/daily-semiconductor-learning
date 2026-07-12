# HBM4 ECC Enhancements: SECDED, Multi-bit ECC & Scrubbing

*Sunday, Jul 12 2026*

*Module 9.6 — HBM4 & Next-Generation Technologies*

## SECDED Review and Its Limitations in HBM4

SECDED (Single Error Correct, Double Error Detect) is the classic Hamming-based ECC scheme used in DDR4, LPDDR5, and HBM2e. For a 64-bit data word it adds 8 check bits (72-bit codeword), correcting any single-bit error and detecting—but not correcting—any 2-bit error. The check bits are computed as XOR parity across overlapping bit subsets defined by the Hamming matrix H.
In HBM3 and earlier, SECDED is applied per pseudo-channel (16 data bits + 2 ECC bits on a 128-bit burst). This works well against isolated bit failures but is insufficient for the multi-cell failure modes emerging in sub-10 nm DRAM arrays: **row hammering**, **charge leakage clusters**, and **retention-time drift** can corrupt entire rows or multiple adjacent cells simultaneously, exceeding SECDED's correction capability.
HBM4 (JESD235D) therefore mandates extended ECC coverage—specifically, the ability to correct multi-bit errors within a DRAM row or across multiple cells on the same bitline, something SECDED fundamentally cannot do.


## Multi-bit ECC Architectures in HBM4

HBM4 introduces two principal multi-bit ECC strategies, both standardized in JESD235D Annex B and the associated JEDEC test mode spec JESD79-5B:
- **BCH (Bose–Chaudhuri–Hocquenghem) codes:** A BCH(t) code over GF(2<sup>m</sup>) can correct up to <em>t</em> arbitrary bit errors per codeword. HBM4 vendors typically implement BCH(4) or BCH(8) over 512-bit codewords, providing 4× or 8× the correction capability of SECDED with a moderate check-bit overhead (~10-15%).- **Chipkill-Correct / Symbol-Correct ECC:** Rather than operating on individual bits, symbol-correct ECC treats each x4 or x8 DRAM die output as a symbol and applies Reed-Solomon coding. A single die failure (all bits on one die wrong) is corrected as a single symbol error. This mirrors the x4 SDDC (Single Device Data Correction) used in server DIMMs but is adapted to HBM's die-stacked topology.Both schemes increase the number of check bits per burst: where SECDED adds ~11%, BCH(8) adds ~16% overhead and RS chipkill adds ~25% overhead. HBM4 allocates additional ECC storage in the base die SRAM and uses dedicated ECC pseudo-channels in the PHY layer to carry this overhead without reducing user bandwidth.


## Scrubbing Strategies: Patrol, Demand, and Background

Even with powerful multi-bit ECC, accumulated correctable errors (CEs) that go uncorrected will eventually exceed the code's correction capability and become uncorrectable (UCE). <em>Memory scrubbing</em> proactively reads and rewrites memory to reset corrected-but-not-repaired cells before they degrade further.
- **Patrol scrubbing:** The memory controller sweeps through the entire address space on a fixed schedule (typically every 24 hours in server platforms, controlled by BIOS/firmware registers). Each row is read, the ECC engine corrects any errors, and the corrected data is rewritten. Patrol scrub rate is a key reliability parameter—too slow and errors accumulate, too fast and bandwidth is stolen from compute traffic.- **Demand scrubbing:** Triggered when a CE is detected on a normal read. The controller rewrites the corrected data immediately. Adds ~1 extra write per CE event but keeps the data clean without a dedicated scrub sweep.- **Background (post-package repair) scrubbing:** Specific to HBM, the base die can execute a `PPR` (Post-Package Repair) sequence (defined in JESD235D section 4.17) that permanently remaps a failing row to a spare row using internal antifuse. PPR is invoked offline after ECC telemetry identifies a hard-fail row.HBM4 also defines a new **Soft PPR (SPPR)** mode that performs row remapping using volatile latches rather than antifuses, enabling in-field repair without a power cycle—a significant reliability advance for always-on AI accelerator deployments.


## ECC Telemetry and JEDEC Register Interfaces

HBM4 exposes ECC status through Mode Register reads accessible via the JTAG/APB interface on the base die. Key registers (per JESD235D Table 25):
- `MR16[7:0]` — CE count per pseudo-channel (8-bit saturating counter)- `MR17[1:0]` — UCE flag and FIFO overflow flag- `MR18[7:0]` — Address of last CE (row address bits [7:0])- `MR19[3:0]` — Failing device/column nibble selectorThe system controller reads these registers via the HBM PHY's APB slave at a polling interval set by the BIOS (typically 1–10 ms in production). When CE counts exceed a threshold (often 256 CEs/24h per JEDEC's RAS guidance), the system logs a predictive failure alert and schedules SPPR or workload migration.
For ATE test, the ECC engines must be bypassed using test mode register `TM_ECC_BYPASS` (vendor-specific, typically Mode Register Write 0xFF to set) to allow raw error injection and direct verification of the underlying DRAM array without the ECC masking marginal failures.


## ATE Test Implications for HBM4 ECC

Testing HBM4 ECC on ATE requires a deliberate strategy because the on-die ECC will mask array defects during standard DRAM march tests. Standard practice on Advantest T2000/V93000 platforms:
- **ECC bypass mode:** Force `TM_ECC_BYPASS=1` before running March C- or MATS+ patterns. This exposes raw bit failures without correction, enabling full bit-error-rate (BER) characterization and yield binning.- **ECC functional test:** With ECC active, inject single-bit and multi-bit errors via the Write Leveling or Direct DRAM Access (DDA) test mode, then verify CE/UCE flags in MR16/MR17 respond correctly. Confirms the ECC engine itself is functional.- **Scrubbing latency test:** Measure time from CE injection to CE correction and rewrite (demand scrub latency) using the ATE timing engine; spec is typically &lt;100 ns from error detection to rewrite completion.- **PPR validation:** Execute the full Hard PPR sequence (set MPR[0], write repair address to MR4/MR5, apply VPP pulse, verify with post-repair march test) to confirm antifuse programming yield. SPPR is verified by toggling power and confirming repair does NOT persist.ECC test coverage must be explicitly specified in the test plan—many early HBM3 test programs omitted ECC functional tests and shipped parts with silent ECC engine failures.


## Key Takeaways

- HBM4 upgrades from SECDED to BCH multi-bit ECC and chipkill-correct schemes to handle multi-cell failure modes in sub-10 nm DRAM arrays.
- Scrubbing (patrol, demand, and Soft PPR) is essential to prevent accumulated correctable errors from escalating to uncorrectable events.
- ATE test programs must explicitly bypass on-die ECC for raw array characterization, then separately validate the ECC engine with controlled error injection.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM JESD235D — JESD235D, sections 4.17 (PPR), 4.20 (SPPR), Annex B (ECC), Table 25 (ECC registers)
2. **[JEDEC]** JEDEC DDR5 ECC White Paper — Extending Error Correction for Future DRAM — JEDEC JEP106 / JEP122 companion white paper, 2023; BCH vs RS ECC tradeoff analysis
3. **[Paper]** Memory Scrubbing to Prevent Memory Errors in High-Reliability Systems — Saleh et al., IEEE Transactions on Reliability, 1990 — foundational scrub-rate vs. UCE-rate model
4. **[Paper]** HBM4 Reliability Enhancement Through In-Situ ECC and Scrubbing — Kim et al., ISSCC 2024, Session 15.2 — Samsung HBM4 die-level ECC architecture details
5. **[JEDEC]** JEDEC JESD79-5B: DDR5/HBM Test Mode Register Specification — JESD79-5B, section 9.3: TM_ECC_BYPASS and DDA register map for ECC test
6. **[Datasheet]** Advantest T2000 HBM Test Solution Application Note — Advantest Corp., AN-T2000-HBM-ECC-2023; ECC bypass and PPR validation flow for HBM3/4

## Additional Learning: Row-Hammer Mitigation and ECC Interaction in HBM4

Row-hammer attacks—where repeated activations of an aggressor row disturb adjacent victim rows—create correlated multi-bit errors that BCH ECC may still fail to correct if the number of disturbed bits exceeds the code's correction radius. HBM4 therefore pairs its enhanced ECC with a dedicated Target Row Refresh (TRR) counter in the base die (JESD235D section 4.14), which tracks activation counts and issues preventive refreshes to at-risk rows before ECC thresholds are reached. On ATE, row-hammer susceptibility is characterized by running a 'hammering' pattern (N activations of an aggressor row, typically N = 70,000 per JEDEC recommendation) and measuring victim row BER both with and without TRR enabled, confirming the TRR+ECC stack provides the required RBER margin.
