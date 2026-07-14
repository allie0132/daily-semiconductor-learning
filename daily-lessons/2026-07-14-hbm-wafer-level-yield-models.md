# HBM Wafer-Level Yield Models

*Tuesday, Jul 14 2026*

*Module 10.1 — Yield Optimization & Failure Analysis*

## Why Classical Yield Models Matter for HBM

HBM stacks 4–16 DRAM dies using Through-Silicon Vias (TSVs). Because a single defective die can kill an entire assembled stack, the economics of HBM production depend heavily on accurate wafer-level yield prediction before dicing and stacking.
Two models dominate: the **Poisson model**, which assumes spatially random defects, and the **Murphy model**, which accounts for defect clustering — the physically more accurate scenario in real semiconductor fabs.


## Poisson Yield Model

The Poisson model gives die yield as:
`Y = e^(−A × D)`
where **A** is die area (cm²) and **D** is defect density (defects/cm²). This derivation assumes defects follow a Poisson distribution across the wafer surface — each unit area is equally likely to contain a defect, independent of neighbors.
- Simple, closed-form, easy to use in spreadsheet yield modelling- Works reasonably well for small die sizes or very low defect densities- For an HBM3 DRAM die (~78 mm²) at D=0.05/cm²: `Y = e^(−0.78 × 0.05) ≈ 0.962`For a stack of N identical dies, Poisson predicts stack yield as `Y_stack = Y_die^N`, e.g., 8-die stack: `0.962^8 ≈ 73%`. However, the Poisson model is often **pessimistic** at larger chip areas because real defects cluster.


## Murphy Yield Model

Murphy (1964) recognized that defect density across a wafer is not spatially uniform — defects cluster near wafer edges, around particle sources, and in proximity to existing defects. Murphy modeled the defect density as a triangular distribution, resulting in:
`Y = [(1 − e^(−A×D)) / (A×D)]²`
For the same HBM3 die at D=0.05/cm²:
- `A×D = 0.039`- `Y = [(1 − e^(−0.039)) / 0.039]² ≈ [0.9808]² ≈ 0.962`- At small A×D, Poisson and Murphy converge — the difference becomes important only above ~0.5For a 200 mm² base die (HBM logic die) at D=0.1/cm², Murphy gives `Y ≈ 0.82` vs. Poisson's `0.78` — a meaningful 4-point gap that affects cost-per-stack projections.
Murphy's model is preferred for large dies and advanced nodes where defect clustering from CMP non-uniformity, EUV stochastic defects, and edge exclusion zones is well documented.


## Extending Models to Multi-Die HBM Stacks

For an HBM stack of N dies (DRAM) plus 1 base die (logic), the overall stack yield without screening is:
`Y_stack = Y_base × Y_dram^N`
Applying Murphy to a realistic HBM3 8H configuration (D_dram=0.04/cm², A_dram=78mm²; D_base=0.08/cm², A_base=198mm²):
- `Y_dram ≈ 0.969`, `Y_base ≈ 0.854`- `Y_stack = 0.854 × 0.969^8 ≈ 0.854 × 0.774 ≈ 66%`This means roughly **one-third of stacks fail** if dies are assembled blindly. The solution is **Known-Good Die (KGD)** pre-selection: test and characterize each DRAM die at wafer level before dicing, then only assemble die that pass. KGD converts `Y_die` from a statistical variable into a near-unity effective yield for the stack assembly step, dramatically improving final stack yield and reducing CoO.


## Practical Impact on Test Strategy

Yield modelling directly shapes the test plan for HBM production:
- **Wafer Sort (WS) completeness:** KGD requires high-coverage electrical test at wafer level. JEDEC JESD235C defines minimum test requirements, but production test aims for >99% defect coverage on DRAM core, TSV continuity, and ECC logic.- **Burn-in trade-offs:** Wafer-Level Burn-In (WLBI) identifies latent defects before dicing. Murphy model informs which die sizes benefit most — larger dies with higher A×D gain disproportionately from WLBI yield uplift.- **Redundancy budgeting:** Row/column repair at wafer sort allows marginally defective die to be rescued. The repair yield uplift is modeled by subtracting repaired fault density from D before applying Murphy, e.g., `D_eff = D − D_repaired`.- **Stack-level repair post-bonding:** SK Hynix HBM3E and Micron HBM3 both incorporate post-bond repair via pseudo-channel mode — modeled as a second yield recovery pass on top of KGD yield.

## Key Takeaways

- Poisson model (Y = e^−AD) assumes uniform random defects; it understimates yield for large dies where defect clustering is dominant.
- Murphy model accounts for defect clustering and is preferred for HBM DRAM and base-die yield at ≥28nm nodes with real-world non-uniformity.
- Stack yield without KGD screening collapses exponentially with die count — even 97% die yield gives only 77% yield on an 8-die DRAM stack.
- KGD pre-selection at wafer sort is the single most important lever to raise HBM stack assembly yield and reduce CoO.
- Test strategy decisions (WLBI, repair enable, coverage targets) must be grounded in Murphy model projections specific to die area and process defect density.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) JEDEC Standard — JESD235C — sections 6 (electrical) and Annex A (test modes), defines KGD test requirements
2. **[IEEE]** Murphy, B.T. — Cost-Size Optima of Monolithic Integrated Circuits — Proceedings of the IEEE, vol. 52, Dec. 1964, pp. 1537–1545 — original Murphy yield model derivation
3. **[Book]** Yield Models for Integrated Circuit Fabrication — Muroga, S., VLSI System Design, Wiley, 1982 — ch. 2 covers Poisson, Murphy, and Seeds models with worked examples
4. **[Datasheet]** HBM3E Product Brief — SK Hynix 24GB HBM3E — SK Hynix, 2024 — 12H stack, 1.18 TB/s, post-bond repair architecture described in product white paper
5. **[Paper]** IEEE EDS — Wafer-Level Known-Good-Die Testing for 3D Stacked ICs — Marinissen et al., IEEE Design & Test vol. 29 no. 4, 2012 — quantitative KGD yield impact on multi-die stacks
6. **[Paper]** Stochastic Defect Density Modeling in EUV Lithography — Galloway et al., Proc. SPIE 10957, 2019 — shows defect clustering exacerbation at EUV nodes relevant to HBM3/3E DRAM

## Additional Learning: Seeds Model: Bridging Poisson and Murphy

The Seeds (1961) yield model extends Murphy by using a gamma distribution for defect density, parameterized by a clustering factor α: Y = (1 + A×D/α)^(−α). As α→∞ it converges to Poisson; at α≈1–2 it matches empirical data for advanced DRAM nodes. HBM yield engineers sometimes fit α from wafer map data using spatial autocorrelation analysis, then plug the calibrated Seeds model into stacked-die yield projections for better accuracy than either Poisson or Murphy alone.
