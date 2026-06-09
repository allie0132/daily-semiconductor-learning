# Column Repair vs Row Repair Strategy and Fuse Allocation

*Tuesday, Jun 09 2026*

*Module 4.5 — DFT & Built-In Test*

## Redundancy Fundamentals in HBM

HBM devices embed spare rows and spare columns in each bank array to replace defective elements without scrapping the die. A **spare row** is an extra wordline that can substitute for any defective row address; a **spare column** is an extra bitline pair (with its sense amplifier) that replaces a defective column address. The decision of *which* type of redundancy to use — and how many of each — is the repair strategy, and it is fixed at design time based on expected defect distributions from process characterization.
In HBM stacks the memory die architecture is divided into banks and pseudo-channels. JESD235C defines up to 8 channels per die, with 16 banks per channel (HBM2E). Each bank independently holds its own row and column spare set, so repair resources do not cross bank boundaries. This independence simplifies address decoding but means spare allocation must be replicated across every bank — a significant area cost.


## Row Repair: Mechanism and Best-Fit Defects

A row repair replaces a defective wordline by programming fuses that encode the bad row address. During DRAM initialization the on-die row-repair comparator loads the fuse contents, and on every `ACT` command it compares the incoming row address with the stored defective addresses. On a match, the spare wordline is driven instead of the defective one — typically within one clock cycle of latency using a priority-encoded match tree.
Row repair is most effective for:
- **Stuck wordlines** — a gate-oxide short that holds an entire row open or closed- **Cell array defects** — a cluster of failing cells sharing the same row address (e.g., poly residue across a wordline)- **Coupling-driven failures** — adjacent-row coupling that degrades a specific row's retention but not the full bankEach spare row requires address fuses proportional to the log₂ of the row address space. For a 32K-row bank, 15 address bits plus one enable bit = 16 fuses per spare. A typical HBM bank allocates **4 spare rows** per bank.


## Column Repair: Mechanism and Best-Fit Defects

Column repair substitutes a spare bitline and sense amplifier for a defective column address. The comparator monitors the column address during a `READ` or `WRITE` command and steers data to or from the spare column. Because a single column address maps to one bitline-pair per bank in DRAM, a column defect typically causes a single-bit-per-access failure — yet because the same column address hits on every row, it affects an entire vertical stripe through the array.
Column repair is optimally suited for:
- **Sense amplifier failures** — an SA input-offset or latch defect that corrupts every cell connected to it- **Bitline shorts** — metal bridge between adjacent bitlines affecting one column globally- **Systematic column variation** — a process gradient (e.g., etch non-uniformity) that systematically degrades the same column address across multiple banks or diesColumn fuse count is similarly `log₂(columns) + 1 enable` bits per spare. HBM with 1K columns per bank needs 10 + 1 = 11 fuses per spare column. Typical allocation is **2–4 spare columns** per bank.


## Fuse Allocation: Architecture and Area Trade-offs

Fuse allocation drives a direct area-versus-yield trade-off. More spares mean more fuses, more fuse decoders, more spare array area, and additional routing — all of which reduce die area efficiency (and increase cost per die). The allocation is determined by statistical yield modeling: Poisson defect density simulations estimate what fraction of dies have defect counts exceeding the available spare set.
HBM vendors use a mix of **electrical fuses (e-fuses)** and **one-time-programmable (OTP)** cells. E-fuses are blown by passing a high current through a polysilicon or metal link, permanently altering resistance. Fuse programming is performed at wafer sort (pre-package) using an ATE-driven fuse-blow sequence. The JEDEC JESD235C specification does not mandate the fuse mechanism — it is vendor-defined — but it does define the register interface through which repair state affects functional behavior post-initialization.
A representative fuse budget for one HBM2 bank (4 row spares + 2 column spares):
- Row: 4 × (15 addr + 1 en) = 64 fuses- Column: 2 × (10 addr + 1 en) = 22 fuses- Per-bank total: ~86 fuses- Multiplied by 16 banks × 8 channels = ~11,000 fuses per dieWith fuse cell size ~0.1 µm² in advanced nodes, total fuse area remains small but the decoder logic and routing overhead can exceed the fuse cells themselves.


## Repair Decision Flow in ATE and Post-Sort Analysis

At wafer sort, the ATE executes a full memory test followed by a **repair analysis** step. The tester collects the failure bitmap (failing cell addresses), passes it to an on-host repair algorithm (often a Minimum Cost Repair or greedy covering algorithm), and determines the optimal assignment of spares to defects. The algorithm output specifies which fuses to blow for each die.
Key constraints the algorithm must respect:
- **Spare capacity** — cannot assign more defects than available spares per bank- **Bank independence** — a spare in bank 0 cannot cover a defect in bank 1- **Column-sharing** — some designs share a spare column across multiple rows; the algorithm must not double-assign itAfter repair, a **post-repair verification** pass confirms the repaired die is fully functional. Yield is measured as the percentage of dies that pass post-repair verification. Repair effectiveness (the fraction of initially failing dies rescued by repair) is a key metric for process health and spare allocation adequacy.
On HBM testers such as Advantest T2000 or Teradyne Magnum, the fuse-blow and post-repair verify are integrated into the sort flow. Repair data is tracked per wafer lot to monitor systematic defect patterns (e.g., consistent column failures at the die edge signaling a lithography issue).


## Key Takeaways

- Row repair targets wordline-oriented defects (stuck rows, cell clusters) while column repair targets bitline/sense-amplifier defects; matching repair type to defect root cause maximizes yield rescue.
- Fuse count per spare = log₂(address space) + 1 enable bit; total die fuse budget scales with banks × channels and must balance spare count against area overhead.
- ATE repair analysis uses a covering algorithm (min-cost or greedy) constrained by bank independence; post-repair verify confirms functional correctness before fuse data is committed to the lot record.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM JESD235C — JESD235C (2021), Section 3.9 Redundancy and Repair — defines MRS registers affecting repair initialization; fuse mechanism is implementation-defined
2. **[JEDEC]** High Bandwidth Memory (HBM3) JESD238A — JESD238A (2022), Section 4 — per-bank repair architecture, 16-channel topology, and initialization sequence for repair register loading
3. **[Paper]** Memory Repair Algorithm Using Minimum Cost Flow — Chen, C.-L. et al., 'An Efficient Repair Algorithm for Embedded Memories,' IEEE Trans. CAD, vol. 25, no. 1, 2006, pp. 36–44
4. **[Book]** DRAM Circuit Design: Fundamental and High-Speed Topics — Brent Keeth et al., Wiley-IEEE Press, 2nd ed. 2007 — Chapter 8 covers redundancy architecture, fuse circuits, and repair comparator design
5. **[Paper]** Advanced DRAM Technology — Redundancy and Yield Enhancement — Kim, J.S. et al., 'Redundancy Architecture for High-Density DRAM,' ISSCC 2019, pp. 244–245 — covers shared-spare column structures in sub-20nm nodes
6. **[Datasheet]** Advantest T2000 Memory Test Platform — Advantest T2000 DRAM Test Solution Datasheet (2022) — integrated repair analysis and fuse-blow flow for HBM sort applications

## 🔍 Additional Learning: Shared Spare Columns and Bank-Group Repair Sharing

Some HBM3 designs implement <em>shared spare columns</em> that can be assigned to any of several banks within a bank group, rather than being dedicated to a single bank. This reduces total fuse count (one set of address fuses serves multiple potential defect locations) at the cost of a more complex arbitration circuit that must resolve which bank's column the spare is covering. The repair algorithm must track which shared spare has been committed and to which bank, preventing double-assignment. Shared spares improve area efficiency by roughly 30–50% in spare array overhead while reducing the peak repairability per bank — a deliberate trade-off tuned to the expected within-bank-group defect correlation from process data.
