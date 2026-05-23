# 2.5D Packaging & Interposer Technology

*Saturday, May 23 2026*

*Module 1.8 — Foundations*

## What Is 2.5D Packaging?

2.5D packaging places multiple bare dies side-by-side on a shared **interposer** — an intermediate redistribution layer — rather than stacking them directly (3D). The interposer provides ultra-fine-pitch die-to-die wiring that organic substrates cannot achieve, enabling the high-bandwidth die-to-die links that HBM requires.
Three leading 2.5D technologies dominate advanced AI and HPC packaging:
- **CoWoS** (Chip-on-Wafer-on-Substrate) — TSMC's full-reticle silicon interposer- **EMIB** (Embedded Multi-die Interconnect Bridge) — Intel's localized silicon bridges embedded in an organic substrate- **SoIC / LIPINCON / FOVEROS** — vendor-specific hybrids adding 3D face-to-face bonding on top of 2.5D routingThe interposer pitch determines achievable HBM bandwidth density. Silicon interposers support 2–5 µm RDL lines; organic interposers are limited to ≥8 µm, which constrains HBM channel count per package.


## CoWoS Architecture — TSMC's Silicon Interposer

CoWoS uses a **passive silicon interposer** fabricated on 65 nm or 28 nm node with multi-layer metal RDL (typically 4–6 Cu layers). The logic die (GPU/ASIC) and HBM stacks are flip-chip bonded onto the interposer with **microbumps (μbumps)** at 55–45 µm pitch; the interposer itself is then C4-bumped to an organic BGA substrate.
- **CoWoS-S**: Single-reticle silicon interposer (~800 mm²); standard for A100-class GPUs with 6 HBM2e stacks- **CoWoS-L**: Multi-reticle stitched interposer (up to 2× reticle); enables H100/H200 with 80 GB HBM3, 8 stacks- **CoWoS-R**: Replaces silicon interposer core with a <em>RDL-based</em> organic-like layer, reducing warpage and cost while maintaining &lt;10 µm line/spaceTSVs are **not used in the interposer itself** for CoWoS-S/L — the interposer is passive and signals route laterally. TSVs appear only inside the HBM stack (connecting DRAM dies to the base die). μbump pitch between HBM base die and interposer is typically **55 µm**, with 1024 balls per HBM3 channel pair.


## EMIB — Intel's Embedded Bridge Approach

EMIB embeds a small, high-density silicon **bridge die** (≈4–12 mm²) into a cavity in the organic package substrate. Only the die-to-die interconnect zone uses the silicon bridge; the rest of the package is standard organic, reducing cost and warpage vs. a full silicon interposer.
Key EMIB characteristics:
- Bridge metal pitch: **55 µm bump pitch** on bridge, ~2 µm routing lines inside bridge- Organic substrate pitch: 130–100 µm for non-bridge zones- No TSVs through the bridge — signal routing is purely lateral within the bridge- Intel Ponte Vecchio (Xe-HPC) used EMIB to connect Xe compute tiles, HBM2e stacks, and Rambo cache chiplets in a single packageEMIB's limitation vs. CoWoS: **no contiguous high-density routing across the full die footprint**. For HBM, this means the HBM PHY must be positioned adjacent to the bridge landing zone, constraining floorplan flexibility on the logic die. EMIB bandwidth density across the bridge is ~2 Tb/s per mm of bridge width.


## HBM Placement on Interposers

HBM stacks are placed on the interposer perimeter surrounding the logic die. JEDEC JESD235C defines the HBM2/2E/3/3E base die bump map — 1024 differential pairs per pseudo-channel group — and the physical **footprint is fixed per generation** (HBM3: ~7.7 × 11.9 mm per stack).
Placement rules critical for test and signal integrity:
- **Channel skew**: HBM spec allows max 1.0 ns skew across the 64-bit data bus; interposer trace length matching is required to ±25 µm- **Power delivery**: VDDQ (1.05 V HBM3) is routed through the interposer RDL with dedicated PDN planes; IR drop budget &lt;30 mV- **Thermal relief**: HBM stacks must be within the GPU die shadow on the heat spreader; stacks &gt;10 mm from the die edge see 5–10 °C higher junction temp- **μbump reliability**: Interposer μbumps are under electromigration stress at &gt;20 mA/bump at 110 °C; JEDEC JEP122H covers EM guidelinesOn CoWoS-L (H100), NVIDIA places 8 HBM3 stacks in two columns of four flanking the 814 mm² GH100 die, with all 5120-bit aggregate bus routed through the stitched interposer in &lt;12 mm trace lengths.


## Test Engineering Implications for 2.5D Packages

2.5D packages present unique ATE challenges because the interposer is untestable in isolation after assembly; defects in μbump bonds or interposer RDL manifest as HBM training failures or elevated bit-error rates.
- **Known-Good Die (KGD)**: HBM stacks and logic dies must pass full wafer-level parametric test before bonding; post-bond rework is impossible on CoWoS packages- **Interposer continuity**: Kelvin 4-wire resistance measurement of μbump chains detects opens; typical μbump daisy-chain resistance spec is &lt;5 mΩ per joint- **HBM DRAM training at package level**: JESD235C Mode Register 8 (MR8) controls read/write training; training failure codes in MR32 pinpoint channel/pseudo-channel failures originating from interposer routing- **Thermal test at ATE**: HBM junction temp during ATE burn-in is controlled via TIM-less force-air cooling; package-level Tj must stay &lt;85 °C during HBM stress per JESD235C thermal guidelines- **SerDes eye scan**: For UCIe or LIPINCON chiplet links on the same interposer, bathtub eye margin &gt;0.35 UI at BER 1e-15 validates interposer signal integrity

## Key Takeaways

- CoWoS uses a full passive silicon interposer with stitched multi-reticle capability for 8-stack HBM3 packages; EMIB uses localized bridge dies embedded in organic substrates, constraining HBM PHY placement.
- HBM base-die μbumps land at 55 µm pitch on the interposer; trace length matching to ±25 µm is required to meet JESD235C 1.0 ns channel skew budget.
- All dies must be KGD before CoWoS bonding; post-bond μbump opens are detected via Kelvin daisy-chain resistance (<5 mΩ/joint) and confirmed through HBM training failure codes in MR32.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) DRAM Standard — JESD235C (2022), Sections 4 (electrical), 8 (training), Annex A (bump map)
2. **[Web]** TSMC CoWoS Technology Overview — TSMC Technology Symposium 2023, 'CoWoS-L and CoWoS-R Advanced Packaging Roadmap'
3. **[Paper]** Intel EMIB: Embedded Multi-Die Interconnect Bridge — R. Mahajan et al., IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 9, No. 10, 2019
4. **[Datasheet]** NVIDIA Hopper H100 White Paper — NVIDIA H100 Tensor Core GPU Architecture, 2022 — HBM3 interposer placement details pp. 14–17
5. **[JEDEC]** JEDEC JEP122H: Failure Mechanisms and Models for Reliability Simulation — JEP122H (2016), Section 3.2.3 — electromigration in µbump interconnects
6. **[Book]** Advanced Packaging Technologies: 2.5D and 3D Integration — E. Beyne, 'The Roadmap to Sub-10 nm Die-to-Die Interconnects,' ECTC 2021 Keynote

## Additional Learning: CoWoS Reticle Stitching and Interposer Yield

CoWoS-L stitches two or more reticle-sized silicon tiles (each ~820 mm²) using metal-bridge stitching in the RDL layers, requiring sub-micron alignment during wafer-to-wafer bonding. Interposer yield follows a defect-density model: at 0.05 defects/cm², a 1640 mm² stitched interposer yields ~44% before KGD screening — making interposer wafer cost, not logic die cost, the primary package cost driver for multi-stack HBM designs above 6 stacks.
