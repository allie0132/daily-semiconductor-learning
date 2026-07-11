# Hybrid Bonding for HBM: Cu-Cu Direct Bonding

*Saturday, Jul 11 2026*

*Module 9.5 — HBM4 & Next-Generation Technologies*

## What Is Hybrid Bonding?

Hybrid bonding (also called direct bonding or Cu-Cu thermocompression-free bonding) is an advanced wafer- or die-level interconnect technology that forms metallic copper-to-copper bonds between two surfaces without solder or micro-bumps. The bonding stack consists of a dielectric-to-dielectric oxide bond (SiO₂ or SiCN) formed at room temperature via surface activation, followed by a copper-to-copper diffusion bond anneal typically at 200–400 °C.
For HBM, hybrid bonding is the critical enabling technology for **HBM4** and beyond. The JEDEC HBM4 specification (JESD235D, under development) targets a base-die-to-DRAM interface pitch of **≤ 1 µm**, far below the 40 µm micro-bump pitch used in HBM2E and the 25–30 µm pitch in HBM3. This pitch reduction increases I/O density by 100× over conventional flip-chip micro-bumps while simultaneously eliminating the stand-off height that limits heat transfer.
The key industry implementations include TSMC's **SoIC (System on Integrated Chips)**, Samsung's **X-Cube**, and Intel's **Foveros Direct**. All three use the same underlying mechanism: chemical-mechanical planarization (CMP) to sub-nanometer roughness, plasma surface activation, room-temperature dielectric pre-bond, then thermal anneal for Cu grain growth and diffusion bonding.


## Process Flow and Critical Parameters

The hybrid bonding process for HBM stacking follows these steps:
- **Surface preparation:** CMP to achieve surface roughness Ra &lt; 0.5 nm and dishing of Cu pads &lt; 5 nm below the dielectric surface. Under-recess is critical — Cu must be slightly recessed before bonding to allow for thermal expansion during anneal.- **Activation:** N₂ plasma or chemical activation of both SiO₂/SiCN surfaces to generate Si-OH bonds that enable room-temperature van der Waals pre-bond.- **Alignment and pre-bond:** Die-to-wafer (D2W) or wafer-to-wafer (W2W) placement with &lt; 200 nm overlay accuracy (sub-100 nm for 1 µm pitch nodes). Bond wave propagates spontaneously upon contact.- **Anneal:** 200–400 °C for 30–120 minutes. Cu expands to fill the recessed gap, grains interdiffuse across the interface. Target bond strength &gt; 1 J/m².- **Thinning:** Donor wafer/die thinned to 3–10 µm via back-grinding + CMP after bonding to reveal TSVs.Key process monitors include bond void density (X-ray or SAM), Cu pad resistance continuity, and dielectric bond energy (blade insertion test). Voids &gt; 2 µm diameter at the Cu interface are yield killers — they create open circuits or reliability failures under thermal cycling (JESD47).


## Yield Implications

Hybrid bonding introduces yield loss mechanisms absent in micro-bump stacking:
- **Pad-level opens:** Cu recess non-uniformity across a die (&gt; ±5 nm variation) causes some pads to fail to form a continuous Cu-Cu bridge after anneal. At 1 µm pitch with thousands of signal pads per DRAM die, a single-pad open rate of 10 ppm accumulates to measurable yield loss per stack.- **Dielectric voids:** Particles &gt; 50 nm between bonding surfaces prevent oxide bond formation. ITRS defect density requirements tighten to &lt; 0.05 defects/cm² for hybrid bonding versus ~0.5 defects/cm² for micro-bump flip-chip.- **Alignment-induced shorts:** At sub-micron pitch, 200 nm overlay error causes adjacent-pad bridging. W2W bonding achieves better alignment than D2W but requires both wafers to have identical die layout and matching yield.- **KGD (Known-Good Die) leverage:** Unlike micro-bump HBM stacking where post-bond test can detect opens electrically, hybrid-bonded stacks are extremely difficult to debond for rework. KGD screening at the individual DRAM wafer level becomes economically mandatory — each die must be tested to near-final quality before commit to bonding.Stacked yield for an 8-die HBM4 stack at 98% individual die yield = 0.98⁸ ≈ 85%, and hybrid bond interface yield (per die interface) must exceed 99.9% to keep total stack yield above 80%. This drives aggressive pre-bond wafer-level electrical test (WLBI and probe) requirements.


## Test Access Challenges

Hybrid bonding fundamentally changes ATE test strategy:
- **No physical probe access post-bond:** Hybrid-bonded stacks have no accessible pads between the DRAM dice and the base die — the interface is fully buried. All test access must occur either pre-bond (wafer probe) or post-stack through the base die's HBM PHY interface.- **JEDEC boundary scan limitations:** HBM3 and earlier support IEEE 1149.1 JTAG and JESD235-defined BIST for post-stack interconnect test (PHY loopback, per-channel PRBS test). HBM4 extends this with finer-granularity per-TSV test modes, but Cu-Cu bonded I/Os between DRAM layers lack the TAP infrastructure present on conventional bump interfaces.- **MISR/BIST reliance:** Because direct probing of inter-die Cu-Cu nets is impossible, embedded BIST (Multiple Input Signature Registers, March C- memory algorithms) running through the base die PHY is the primary post-bond verification path. Any BIST failure must be root-caused through FIB cross-section or acoustic microscopy — there is no electrical rework path.- **Burn-in constraints:** Traditional clamshell burn-in sockets cannot apply per-die stress to a hybrid-bonded stack. Board-level burn-in at package level using HBM controller stimulus is required. Temperature uniformity across the stack (ΔT &lt; 5 °C between top and bottom DRAM) is critical for HTOL (High-Temperature Operating Life) equivalence per JESD47.ATE patterns for HBM4 pre-bond wafer test must achieve parametric coverage of all TSV signal nets at &gt; 99.9% fault coverage, since post-bond repair is not feasible. Teradyne UltraFlex and Advantest T2000 platforms are extending probe card pin counts to 10,000+ for HBM4 wafer probe at sub-micron pitch.


## Industry Adoption and Roadmap

Hybrid bonding for HBM is transitioning from research to production:
- **HBM3E (2024):** Still uses micro-bump stacking at 25–30 µm pitch. Hybrid bonding is used in TSMC SoIC for logic-on-logic integration (e.g., N3 on N6) but not yet for DRAM stacking in production HBM.- **HBM4 (2025–2026 ramp):** First HBM generation targeting hybrid bonding for DRAM-to-DRAM interfaces. SK Hynix, Samsung, and Micron all have disclosed hybrid bonding roadmaps. JEDEC JESD235D (HBM4) standardizes the electrical interface; the physical stacking method is vendor-defined.- **Pitch roadmap:** HBM4 targets 1 µm Cu-Cu pad pitch → HBM4E at 0.5 µm → beyond 2028 at sub-0.5 µm. Each half-pitch node roughly doubles I/O bandwidth density.- **Chiplet ecosystems:** UCIe 2.0 and BoW (Bunch of Wires) interconnect standards are incorporating hybrid bonding as an optional physical layer for die-to-die distances &lt; 10 µm, directly impacting how HBM base dies connect to GPU/CPU logic tiles.For test engineers, the key near-term impact is the shift of quality gates earlier in the flow — from final stack test to pre-bond wafer-level test — and the increased reliance on embedded DFT structures for post-bond interconnect verification where probe access is impossible.


## Key Takeaways

- Hybrid bonding (Cu-Cu direct bonding) enables ≤1 µm pitch for HBM4, replacing 25–40 µm micro-bumps and increasing interconnect density 100×.
- Pre-bond KGD screening is mandatory since hybrid-bonded stacks cannot be debonded — single-die probe coverage must exceed 99.9% fault coverage.
- Post-bond test access relies entirely on the base die PHY interface and embedded BIST/MISR; direct probing of Cu-Cu bonded inter-die nets is not physically possible.
- Bond void density (SAM/X-ray) and Cu pad recess uniformity (CMP) are the primary process yield knobs; voids >2 µm are reliability killers under thermal cycling.
- ATE strategy for HBM4 requires board-level burn-in and HTOL since per-die clamshell sockets cannot access individual DRAM dice in a hybrid-bonded stack.

## References

1. **[JEDEC]** JESD235D — High Bandwidth Memory (HBM4) DRAM Standard — JEDEC Solid State Technology Association, draft 2025 — defines HBM4 electrical interface, BIST modes, and DFT requirements for hybrid-bonded stacks
2. **[Paper]** Direct Bond Interconnect (DBI) Technology for 3D Integration — Enquist P. et al., IEEE ECTC 2019 — foundational paper on Cu-Cu hybrid bonding process parameters and bond strength vs. anneal temperature
3. **[Web]** TSMC System on Integrated Chips (SoIC) Technology — TSMC Technology Symposium 2023 whitepaper — describes SoIC-WoW (wafer-on-wafer) and SoIC-WoD (wafer-on-die) hybrid bonding for HBM integration
4. **[IEEE]** IEEE JTAG 1149.1-2013 — Boundary-Scan Architecture Standard — IEEE Std 1149.1-2013 — defines TAP controller and boundary-scan cells referenced in HBM post-stack interconnect test
5. **[JEDEC]** JESD47K — Stress-Test-Driven Qualification of Integrated Circuits — JEDEC JESD47K — HTOL and thermal cycling requirements applicable to hybrid-bonded HBM stacks during qualification
6. **[Book]** Known Good Die (KGD) Strategies for Advanced Packaging — Lau J.H., 'Semiconductor Advanced Packaging', Springer 2021, Chapter 9 — covers KGD testing methodologies for 3D stacked packages

## Additional Learning: SAM vs. X-Ray for Hybrid Bond Void Detection

Scanning Acoustic Microscopy (SAM) at 230 MHz can resolve voids ≥ 2 µm at the Cu-Cu interface but requires liquid couplant and struggles with the acoustic impedance mismatch in ultra-thin (3–5 µm) bonded layers. Synchrotron X-ray tomography offers sub-100 nm void resolution without couplant constraints but is limited to R&D sampling — not inline production. High-resolution inline X-ray (≥ 130 kV micro-focus) at 1–2 µm pixel resolution is the current production compromise for HBM4 hybrid bond inspection, with AXI tools from Comet Yxlon and Nikon Metrology qualifying systems for ≤ 2 µm void detection in stacked die configurations.
