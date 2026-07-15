# Post-Stacking Yield Recovery in HBM

*Wednesday, Jul 15 2026*

*Module 10.3 — Yield Optimization & Failure Analysis*

## Why Post-Stacking Yield Recovery Matters

HBM stacks are assembled by bonding 4–12 DRAM dies to a logic base die using microbumps and TSVs. Even when individual dies pass pre-bond wafer-level test (WLT), the stacking process introduces new defect modes: microbump open/short, TSV cracking, delamination, and assembly-induced ESD. Post-stacking test on the ATE therefore reveals failures that did not exist at wafer level.
Because the HBM stack is already embedded in an advanced package (CoWoS, Foveros, SoIC), the only repair strategy available is **electrical redundancy**: on-die spare rows and columns that can be substituted for failing ones. Repair decisions made during final test must be permanently programmed into the device before shipment.
JEDEC JESD235C formalises the repair interface through the **Repair Register Set (RRS)**, allowing the host controller or ATE to read post-repair configuration and to programme fuse-based repair maps in a standardised way.


## Redundancy Architecture — Spare Rows and Columns

Each HBM DRAM die contains dedicated spare wordlines (row spares) and spare bitline segments (column spares). Typical implementations allocate **1–2 spare rows per sub-array bank group** and a shared column spare pool per pseudo-channel. The ratio of spares to primaries is a design trade-off: more spares increase yield but reduce effective die area and bandwidth.
HBM2E and HBM3 dies use a **distributed repair architecture** where spares are co-located with the failed address region rather than in a centralised redundancy array. This minimises timing skew after repair because the activated wordline length does not change.
- **Row spare activation:** a failing row address is mapped to a spare row by blowing a fuse or programming an eFuse latch; on ACTIVATE, the address decoder routes to the spare wordline instead.- **Column spare activation:** a failing column address (DQ lane segment) is replaced by asserting a column redundancy enable signal; the column MUX selects the spare bitline pair.- **Shared spares:** some implementations bank multiple defective columns against a single spare using a priority encoder — effective only when defects per bank stay below the spare count.

## Row and Column Replacement Flow on ATE

Post-stacking repair proceeds in a well-defined sequence on the ATE after the initial **Known Good Stack (KGS)** test:
- **Full functional test:** march algorithms (March C−, March LR) identify all failing row and column addresses across all pseudo-channels and dies. Results are stored in the tester's fail memory as a per-address fail bitmap.- **Repair algorithm:** the tester host (or an on-board repair processor) runs a covering algorithm to assign spare rows/columns to failing addresses. JEDEC does not specify the algorithm, but greedy first-fit and minimum-cost-flow solvers are common. The algorithm must respect hardware constraints: one spare per bank group, no cross-channel sharing.- **Repair map download:** the computed repair map is written to the HBM via the IEEE 1149.1 JTAG TAP or through a proprietary BIST/MRS interface defined in the die's datasheet. For HBM3, the `RRS_WRITE` command sequence programs the RRS latches.- **Fuse programming:** the tester applies the fuse-blow sequence (see Section 4) to lock the repair map permanently.- **Post-repair verification:** a targeted re-test of all previously failing addresses, plus a neighbourhood stress, confirms that the repair is effective and has not introduced new failures.

## Fuse Programming — eFuse and Laser Trim

HBM devices use one of two permanent repair storage technologies: **laser fuses** (blown during wafer probe before assembly) or **electrical eFuses** (one-time programmable polysilicon or silicide links blown by current pulse on the final packaged device).
Post-stacking repair exclusively relies on **eFuses** because the die is no longer accessible by laser after stacking. eFuse programming on ATE requires precise control of three parameters:
- `V_PROG`: programming voltage, typically 1.8 V–2.5 V depending on technology node (specified per die vendor in the product datasheet).- `T_PROG`: pulse width, usually 1–10 µs. Too short → incomplete blow; too long → adjacent fuse damage or metal migration.- `I_PROG`: current compliance, typically 10–30 mA. ATE must source this through the power supply pin; verify via Kelvin sense that no voltage drop along the probe card exceeds 50 mV.The ATE applies the `FUSE_PROGRAM` MRS command sequence, then reads back the `FUSE_STATUS` register to confirm a successful blow (a bit transition from 0 to 1). A failed blow is **irreversible** — the address is permanently assigned to the spare even if the blown fuse state is ambiguous. Most ATE flows therefore require 100% read-back verification before moving to the next fuse address.
Die vendors provide a **fuse programming window** characterisation in their qualification reports (typically a Weibull plot of blow probability vs. V_PROG × T_PROG). ATE engineers must ensure operating conditions stay within the rated window across junction temperature (typically 25 °C ± 10 °C during programming).


## Post-Repair Verification and Acceptance Criteria

After fuse programming, JEDEC JESD235C Section 7.3 requires a **two-step post-repair verification**:
- **Repair integrity test:** cold power-up (fuses must reload correctly from the blown state into the on-die latch array) followed by a targeted read/write sweep of all repaired addresses. A repaired address that still fails indicates a fuse misread or a repair-map collision.- **Neighbourhood stress:** a write-disturb pattern (e.g., hammer stress on adjacent rows) verifies that the spare row's sense amplifiers meet the same margin as primaries. Spare rows that were not fully characterised during pre-bond test are more susceptible to marginal performance.Acceptance criteria at the CoWoS/final package level typically require:
- Zero remaining functional failures after repair.- Fuse read-back match rate ≥ 99.99% across all programmed bits (vendor-specified).- No post-repair retention failures at 85 °C bake for 96 h (per JESD47 lot acceptance).Yield data from the repair step feeds directly into the **stacked yield model**: each successfully repaired die contributes to the Known Good Stack (KGS) pool, while unrepaired defective dies are scrapped or downgraded to lower-speed SKUs if the vendor supports partial-channel disable.


## Key Takeaways

- Post-stacking HBM repair relies entirely on electrical eFuse programming because laser trim is inaccessible after 3D integration; precise V_PROG, T_PROG, and I_PROG control on ATE is critical.
- JEDEC JESD235C defines the Repair Register Set (RRS) interface that standardises how repair maps are written to the HBM and read back for verification.
- A two-phase post-repair verification — cold power-up integrity test plus write-disturb neighbourhood stress — is required to confirm both fuse permanence and spare-row margin.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, Section 7 (Repair Register Set and Fuse Programming), 2021
2. **[Paper]** A 1.2 V 8 Gb 8-Channel 128 GB/s HBM DRAM with Defect Tolerance Scheme and Bond-Wire I/O — Lee D. et al., IEEE ISSCC 2016, Session 11.1
3. **[Datasheet]** HBM3 Gen2 Product Brief — Repair Architecture and eFuse Specification — SK Hynix HBM3E Product Engineering Note, Rev 1.1 (2023)
4. **[Book]** Semiconductor Memory Testing — van de Goor A.J., Chapter 8 (Redundancy and Repair), Kluwer Academic, ISBN 0-7923-9313-X
5. **[JEDEC]** Standard for Lot Acceptance Procedures for High-Reliability Semiconductors — JESD47L, Section 6 (Burn-in and Retention Test), 2023
6. **[IEEE]** IEEE Standard for Test Access Port and Boundary-Scan Architecture — IEEE 1149.1-2013, used as repair map download interface in pre-HBM3 stacks

## 🔍 Additional Learning: Algorithmic Repair: Minimum-Cost-Flow vs. Greedy Solvers

While greedy first-fit repair solvers are fast and ATE-friendly, they can miss feasible repair solutions when defect clusters span multiple bank groups that share a spare pool. Minimum-cost-flow (MCF) algorithms model the repair problem as a bipartite matching between failing addresses and available spares with capacity constraints; they are guaranteed to find a solution if one exists and can reduce unnecessary spare consumption by 10–15% on clustered defect distributions (Tsai et al., IEEE TCAD 2019). HVM ATE platforms typically implement MCF as an off-line host-side computation with the solution downloaded to the tester pattern set, adding less than 200 ms per device to the overall test time.
