# ATE Test Program Structure for HBM

*Friday, Aug 28 2026*

*Module 16.1 — HBM Test Program Development & Characterization*

## Overview: Why HBM Demands a Structured Test Program

HBM stacks present a unique challenge for ATE test programs: a single device may contain 4–16 DRAM dies, hundreds of gigabytes of addressable space, proprietary PHY interfaces, and multiple independent channels — all driven through a narrow bump field on a silicon interposer. Ad-hoc or flat program architectures that work for DDR4 break down quickly at HBM3E densities.
A well-structured HBM test program separates concerns into three orthogonal axes: the **test flow** (what runs and in what order), the **pattern library** (how stimulus is encoded), and the **timing domain set** (how fast the bus edges are placed). Getting these three axes independent is what allows a single test program to serve characterization, production screening, and reliability stress with only parameter changes.


## Test Flow Design: Hierarchical Flow Control

Modern HBM test programs on platforms such as Advantest T2000/93000 or Teradyne Magnum/UltraFlex use a hierarchical flow model. The top-level flow sequences major test phases: power-on and initialization, connectivity, functional memory, AC margin, and power-off. Each phase is itself a sub-flow containing bins, branching logic, and pass/fail collection.
- **Phase 0 — Power sequencing:** applies VDDQ (1.1 V for HBM2E, 1.05 V for HBM3/3E), waits for power-on reset settling, then applies the reference clock. Sequence timing follows JEDEC JESD235C Table 7 reset timings (tINIT1 through tINIT5).- **Phase 1 — PHY initialization:** drives mode-register writes over the CA bus (Command-Address lane, 14-bit for HBM2E, 8-bit per pseudo-channel for HBM3). Verifies DRAM Ready (RDQS) assertion within tINIT4 window (≤ 200 μs).- **Phase 2 — Functional coverage:** marching patterns, checkerboard, galloping columns — sequenced from fastest to longest to allow early exit on hard fails.- **Phase 3 — AC margin sweeps:** tRCD, tRP, tRC margin using timing guardbands derived from characterization data.Branching uses per-die soft bins that are mapped to hard bins at flow end, preserving die-level resolution for yield analysis.


## Pattern Organization: Libraries, Subroutines, and Pseudo-Channel Parallelism

HBM test patterns are organized as a library of reusable subroutines rather than a single flat vector file. Each subroutine addresses a specific access type: mode-register reads/writes, row activate/precharge, burst read/write with known data, and refresh-related sequences.
HBM3/3E introduces **pseudo-channel (PC) mode**: each 64-bit HBM channel is split into two independent 32-bit pseudo-channels, each with its own command and data path. Pattern subroutines must therefore be written in PC-aware form, issuing back-to-back commands to PC0 and PC1 within the same tCCD_L window (≥ 4 nCK at 6.4 Gbps).
- **JEDEC test modes (MR41, MR43):** HBM3E exposes BIST and MISR mode registers. Patterns that write known data, then read back through the internal MISR (Multiple-Input Shift Register), can verify entire rows in a fraction of the vector count required by external scan — critical for reducing tester time on 24 GB HBM3E stacks.- **Data inversion (DBI_WR/DBI_RD):** Patterns must toggle the DBI pin and include both inverted and non-inverted strobes. DBI-aware subroutines ensure eye diagrams are measured on worst-case transitions.

## Timing Sets: Multi-Domain Clocking and Edge Placement

An HBM ATE test program maintains multiple timing sets (also called timing domains or timing configurations) that can be switched between phases without reloading patterns. Three domains are typical:
- **Functional timing set:** edges placed at nominal specification — e.g., 6.4 Gbps data rate (156.25 ps UI), with DQ/DQS skew budgeted from JESD235C AC timing table (tDQSQ ≤ 15 ps, tQSH ≥ 45% UI).- **Shmoo timing set:** relaxed setup/hold margins, used as a starting point for 2D shmoo plots (frequency vs. VDDQ). The tester sweeps reference-clock frequency and supply voltage while the program streams patterns from the functional pattern library.- **Stress timing set:** edges pushed inside the nominal eye to accelerate aging in HTOL (High Temperature Operating Life) characterization. Margins are deliberately tightened by 10–20% of UI to expose marginal cells.On Advantest T2000, timing sets are expressed as `.tim` parameter blocks; on Teradyne ETS-800/UltraFlex they appear as timing waveform tables (TWT). Switching timing sets within a flow costs zero additional vector time on most modern platforms — the tester caches multiple sets and re-arms edge generators between test phases.


## Practical Considerations: Parallelism, Binning, and Data Logging

Production HBM test programs run multiple stacks in parallel (multi-site) using a tester head with replicated instrument channels. Practical parallelism for HBM on leading testers is 2–4 sites per channel card set, limited by pin count and signal integrity of the loadboard. Flow-level site synchronization must account for per-site power-on jitter and CA bus contention.
Binning strategy for HBM follows a **hierarchical repair-then-bin** model: failing rows and columns identified in functional phases are passed to the post-redundancy map; only devices where repair is exhausted exit to a failing hard bin. Soft bins track repair usage percentage, enabling yield learning without hiding cells behind redundancy.
- **DataLog:** AC margin results (shmoo data), MISR signatures, and per-die temperature readings (from internal Tj sensors accessed via MR) are logged to STDF files for SPC dashboards.- **Tester memory depth:** at 6.4 Gbps, even a 4 Gbit DRAM die requires &gt;200 M vectors for a full March-C pass; waveform memory depth on the tester is often the binding constraint, requiring pattern compression or on-the-fly generation via algorithmic pattern generators (APG).

## Key Takeaways

- HBM test programs must separate flow control, pattern libraries, and timing sets into independent axes to serve both characterization and production from one program.
- HBM3/3E pseudo-channel mode requires PC-aware subroutines and careful tCCD_L management to maintain throughput without command collisions.
- Tester memory depth — not pattern logic — is typically the binding constraint; MISR-based BIST modes and APG are essential for 24 GB HBM3E at production speed.
- Three timing sets (functional, shmoo, stress) cover the full test lifecycle without requiring separate programs or pattern reloads.
- STDF-based DataLog of AC margins, MISR signatures, and Tj readings enables closed-loop yield learning directly from the tester.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C, Section 4 (Initialization), Section 9 (AC Electrical Characteristics), Table 7 (tINIT timing), 2023
2. **[JEDEC]** HBM3E Standard Addendum — JESD235D, Pseudo-Channel Architecture and Mode Register MR41/MR43 BIST definitions, 2024
3. **[Datasheet]** Advantest T2000 ATE Platform — Application Guide for Wide I/O Memory — Advantest Corporation, T2000 Memory Test Solution, Timing Set (.tim) Reference, Rev 3.1
4. **[Paper]** March Tests for Diagnosis of Static Faults in Memories — Karpovsky, M. & Leshkovtsev, A., IEEE Transactions on Computers, Vol. 50, No. 3, 2001
5. **[Web]** Standard Test Data Format (STDF) Specification — Teradyne STDF v4 specification, https://www.inheritedcode.com/stdf-specification.html
6. **[Book]** Test Engineering — A Concise Practical Guide — Turino, J., Kluwer Academic Publishers, 2nd ed., Chapter 6 (Digital Memory Test), 1998

## 🔍 Additional Learning: APG vs. Stored-Vector Tradeoff in HBM Testing

Algorithmic Pattern Generators (APGs) solve the tester memory depth problem for HBM by computing address and data on the fly in hardware at full rate, rather than streaming pre-stored vectors. On Teradyne UltraFlex, the APG engine supports March algorithms natively, enabling a full 16 Gbit pseudo-channel pass in under 90 seconds with near-zero waveform memory consumption. The tradeoff is reduced flexibility: APG algorithms are parameterized but fixed, so defects that require irregular addressing sequences — such as activating adjacent rows to stress sense amplifiers — still require stored patterns. Production programs typically blend both: APG for bulk March passes, stored vectors for initialization, shmoo, and JEDEC mandatory test modes.
