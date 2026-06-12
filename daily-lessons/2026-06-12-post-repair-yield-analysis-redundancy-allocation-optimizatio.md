# Post‑Repair Yield Analysis & Redundancy Allocation Optimization

*Friday, Jun 12 2026*

*Module 4.10 — DFT & Built-In Test*

## 1. Collecting Post‑Repair Yield Data

After a repair run (laser/EBI/laser‑cut), capture the following for each die:
- **Pre‑repair failure map** (bits failed, address, test vector ID)- **Post‑repair status** (repaired, still‑failed, newly‑failed)- **Repair cost** (repair time, energy, equipment wear)- **Yield impact** (yield_before, yield_after, net gain)Store data in a relational database or a JEDEC‑compliant `JEDEC 202‑2021` format to enable statistical analysis.


## 2. Failure Clustering & Root‑Cause Correlation

Use DFT built‑in test (BIT) signatures and `JTAG` scan‑chain diagnostics to group failures:
- Spatial clustering (same column, same rank, same TSV group)- Temporal clustering (failures that appear after a specific stress step)- Signature clustering (identical `BIST` failure patterns)Map clusters to physical redundancy resources (spare rows, spare columns, spare TSVs) defined in the design‑for‑test (DFT) plan (see JEDEC JESD209‑2 for HBM redundancy).


## 3. Redundancy Allocation Modeling

Build a Monte‑Carlo model using the empirical defect density (D) extracted from the clustered data:
<pre>`Yield = (1 - D)^(N_active) * (1 - P_repair_fail)^(N_spare)`</pre>Where `N_active` is the number of functional bits/rows and `N_spare` is the allocated redundancy. Adjust `N_spare` per cluster to maximize `Yield_gain = Yield_post – Yield_pre` while keeping `P_repair_fail` below the target (< 0.5 %).


## 4. Optimizing Repair Flow

Integrate the model into the ATE repair scheduler:
- Prioritize repairs that close a failure cluster with the fewest spare resources.- Limit repair attempts per die to a configurable budget (e.g., ≤3 laser cuts) to avoid diminishing returns.- Feed back the actual repair success rate to continuously recalibrate the Monte‑Carlo model.Resulting redundancy allocation tables are stored in the `JEDEC 191‑2022` redundancy map file for the next production lot.


## 5. Reporting & Continuous Improvement

Generate a daily KPI dashboard that includes:
- Yield_before / Yield_after per lot- Spare utilization percentage- Repair success probability per failure mode- Projected yield gain for next lot if redundancy is re‑distributedUse statistical process control (SPC) charts (X‑bar, R) to detect drift in defect density, triggering a redesign of redundancy allocation before the next tape‑out.


## Key Takeaways

- Post‑repair data must be captured in a standardized, searchable format.
- Clustering failures with DFT signatures reveals the most efficient redundancy targets.
- Monte‑Carlo yield models guide optimal spare allocation and repair budgeting.

## References

1. **[JEDEC]** JEDEC JESD209‑2: HBM3 Redundancy and Repair Guidelines — Section 5.4–5.7, 2022
2. **[JEDEC]** JEDEC JESD235C: Test and BIST Architecture for 3D‑Stacked Memory — Section 4.2, 2021
3. **[IEEE]** IEEE Transaction on Components, Packaging and Manufacturing Technology, "Yield Modeling for Redundant TSVs in HBM" — Vol. 13, No. 3, 2023
4. **[Datasheet]** Samsung HBM3 Datasheet, Rev. 1.2 — Includes spare row/column count and repair latency specifications
5. **[Paper]** "Statistical Methods for Redundancy Allocation" – K. L. Venkata, 2022 — Provides closed‑form solutions for N_spare optimization

## 🔍 Additional Learning: Machine‑Learning‑Based Failure Prediction for Redundancy Planning

Recent work (IEEE TCAD 2024) demonstrates a gradient‑boosted model trained on post‑repair datasets that predicts the optimal spare distribution with <2 % error compared to Monte‑Carlo, enabling near‑real‑time allocation adjustments during wafer sort.
