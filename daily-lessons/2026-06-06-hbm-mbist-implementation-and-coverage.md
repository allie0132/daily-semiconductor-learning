# HBM MBIST Implementation and Coverage

*Saturday, Jun 06 2026*

*Module 4.1 — DFT & Built-In Test*

## MBIST Architecture in HBM

HBM integrates Memory Built-In Self-Test (MBIST) circuitry within each DRAM die of the stack. Unlike external ATE-driven pattern generation, the MBIST controller is instantiated per pseudo-channel and has direct access to the row decoder, sense amplifiers, and data-path logic. In HBM2E and HBM3, each DRAM die contains two pseudo-channels per channel and two channels, yielding four MBIST controllers per ×128 die. The controller shares the internal memory bus with the normal read/write path, guaranteeing complete array coverage including spare rows reserved for Post-Package Repair (PPR).
MBIST activation is gated through the HBM JEDEC-defined Mode Register (MR) interface. Writing to `MR32` (MBIST Control) with the appropriate opcode initiates a test sequence. The controller runs autonomously; the host polls `MR34` (MBIST Status) for completion and pass/fail. This separation of initiation and readback is essential for in-system self-test without tying up the ATE serial link.


## MBIST Algorithms: MARCH Variants and Pattern Sequences

HBM MBIST implements a subset of classical MARCH algorithms optimized for DRAM cell physics. The dominant algorithm is a **MARCH C−** variant with six operations applied across every cell address in ascending then descending order:
- **⇑(w0)** — write 0 to all cells ascending- **⇑(r0,w1)** — read 0, write 1 ascending- **⇑(r1,w0)** — read 1, write 0 ascending- **⇓(r0,w1)** — read 0, write 1 descending- **⇓(r1,w0)** — read 1, write 0 descending- **⇓(r0)** — read 0 descendingThis sequence detects **stuck-at faults (SAF)**, **transition faults (TF)**, **coupling faults (CF)**, and **address decoder faults (AF)**. HBM3 vendors also implement a **MARCH SS** variant adding diagonal coupling patterns to catch sense-amplifier-bridging defects introduced by tight pitch in 8H stacking. Pattern data is stored in compact on-die ROM, reducing area overhead to under 0.3% of the DRAM array die footprint (Samsung HBM3 roadmap, ISSCC 2023).


## Mode Register Interface and Test Control

JEDEC JESD235D defines the MBIST control registers in the HBM Mode Register map. Key registers for MBIST operation:
- `MR32[3:0] = MBIST_MODE` — selects algorithm (0x1=MARCH, 0x2=checkerboard, 0x3=walking 1s)- `MR32[5:4] = COVERAGE_SEL` — 00: data array only; 01: include PPR rows; 10: full array with ECC- `MR32[6] = REPAIR_EN` — enable automatic hard-repair row substitution during MBIST- `MR33[7:0] = MBIST_SEED` — 8-bit LFSR seed for pseudo-random pattern extensions- `MR34[0] = MBIST_DONE` — set by controller on completion- `MR34[1] = MBIST_FAIL` — asserted if any comparison mismatch occurred- `MR34[7:2] = FAIL_BANK[5:0]` — one-hot encoding of failing banksThe host issues MR writes over the HBM CA bus using the **MRS** command, latency-padded by `tMRD` (8 nCK minimum per JESD235D §3.6). For a 4 Gb pseudo-channel at 3.2 Gbps, a full MARCH C− pass runs approximately **25 ms**.


## Coverage Metrics and Fault Models

MBIST coverage in HBM is quantified against four primary fault models:
- **Stuck-At Fault (SAF)**: cell permanently reads 0 or 1. MARCH C− achieves 100% SAF coverage.- **Transition Fault (TF)**: cell fails to transition 0→1 or 1→0. Covered by alternating write/read operations.- **Coupling Fault (CF)**: write to aggressor cell disturbs victim. MARCH C− detects inversion and idempotent CFs; MARCH SS extends to state-coupling faults.- **Address Decoder Fault (AF)**: multiple cells activated by one address, or unreachable cell. Ascending/descending traversal guarantees every address is exercised.One limitation is **retention fault coverage**: autonomous MBIST does not insert the long pause required to stress weak cells. ATE-assisted retention testing (write, power-down, read back after ≥64 ms) remains an external operation. Some HBM3 implementations add a configurable **pause timer** in `MR35` to support retention MBIST, but this is vendor-specific and not in JESD235D.


## MBIST and Post-Package Repair (PPR) Integration

HBM supports two repair mechanisms that interact with MBIST: **Hard PPR (hPPR)** and **Soft PPR (sPPR)**. When `MR32[6]=1` (REPAIR_EN), the MBIST controller automatically substitutes a failing row with a spare upon detection of SAF or TF, writing the row address to the on-die fuse register via a shadow latch. This is the standard **BISR (Built-In Self-Repair)** flow: <em>MBIST run → fail detect → repair write → re-run MBIST on repaired address</em>.
SK Hynix HBM2E datasheets disclose 2 spare rows per 16 Kb row-width bank. MBIST must be re-run after repair to confirm the substitute row is defect-free. For **sPPR** (volatile row remapping), the MBIST controller writes the failing row address to `MR36–MR37` and asserts `MR38[0]=sPPR_ACT`. Remapping takes effect within `tPGM` (~150 ns). sPPR is useful for characterization without consuming the one-time-programmable hard repair budget.


## Key Takeaways

- HBM MBIST uses MARCH C− algorithm via MR32/MR34 mode registers, running autonomously per pseudo-channel at ~25 ms per full pass for 4 Gb devices at 3.2 Gbps.
- Coverage targets SAF, TF, CF, and AF faults; retention fault coverage requires ATE-assisted external flow not captured by standard on-die MBIST.
- BISR integration allows MBIST to trigger automatic hPPR or sPPR row substitution, but a confirmation re-run pass is mandatory after repair.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235D, 2023 — Sections 3.6 (MRS timing), 4.5 (MBIST Mode Registers MR32–MR38), 5.2 (PPR)
2. **[Paper]** A 12-High 3DS HBM3 DRAM with 819 GB/s Bandwidth and Built-In MBIST Supporting BISR — Kim et al., ISSCC 2023, pp. 420–422 — On-die MBIST area overhead and BISR flow
3. **[Book]** Memory Systems: Cache, DRAM, Disk — Jacob, Ng, Wang — Morgan Kaufmann 2007, Chapter 4: DRAM fault models and MARCH algorithms
4. **[IEEE]** An Efficient BIST Architecture for HBM Memory — IEEE VLSI-TSA 2020 — Pseudo-channel MBIST partitioning and coverage analysis
5. **[Datasheet]** HBM2E Product Brief: MBIST and Repair Specifications — SK Hynix HBM2E 8GB (H5VR8GABHK) Product Brief Rev 1.2 — sPPR/hPPR spare row count and timing
6. **[Paper]** MARCH SS: A Test Algorithm Targeting Sense Amplifier Coupling Faults — Hamdioui et al., DATE 2006 — MARCH SS algorithm formulation and coupling fault model coverage

## Additional Learning: MBIST Scan-Out via JTAG in 3D-Stacked HBM

While standard HBM MBIST results are read back through MR34 over the CA bus, some HBM implementations expose MBIST fail-address logs through an IEEE 1149.1 JTAG TAP in the base logic die. This allows per-cell fail bitmap readout (not just per-bank pass/fail), enabling precise FFA coordinates without ATE pattern replay. The JTAG data register is typically 256 bits wide (one HBM row of column addresses) and requires the host SoC or ATE to connect the JTAG chain through dedicated TSV columns defined in JEDEC JEP122H.
