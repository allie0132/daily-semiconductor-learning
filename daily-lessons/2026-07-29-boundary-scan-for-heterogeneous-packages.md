# Boundary Scan for Heterogeneous Packages

*Wednesday, Jul 29 2026*

*Module 12.7 — Heterogeneous Integration & Advanced Packaging Test*

## IEEE 1149.1 Boundary Scan Fundamentals

IEEE 1149.1 (JTAG) defines a 4- or 5-pin Test Access Port (TAP): `TDI`, `TDO`, `TCK`, `TMS`, and optional `TRST#`. A 16-state FSM (the TAP Controller) governs instruction and data register operations. The Boundary Scan Register (BSR) places a cell at every I/O pin to capture, shift, and update logic states without physical probing.
- **EXTEST**: drives BSR values onto output pins and captures input pin values for interconnect test.- **SAMPLE/PRELOAD**: non-invasively samples pin state during normal operation.- **BYPASS**: routes TDI directly to TDO via a single-bit register to shorten chain length when a device is not under test.- **INTEST**: applies BSR values directly to core logic for internal test.BSDL (Boundary Scan Description Language) files formally describe each device's scan behavior and are consumed by ATE software and JTAG vector compilers.


## Limitations of 1149.1 in Heterogeneous Packages

In 2.5D and 3D-IC packages, standard 1149.1 boundary scan was designed for package-level I/Os and cannot directly access internal die-to-die interconnects such as Through-Silicon Vias (TSVs) or micro-bumps. Key challenges include:
- **Hidden interconnects**: TSV arrays and inter-die micro-bump grids are not exposed as package pins and therefore cannot be reached by conventional BSR EXTEST.- **Multiple TAP domains**: each die may implement its own 1149.1 TAP with different TCK frequency limits, complicating chain management.- **Power domain isolation**: dies in a stack may be powered sequentially (known-good-die bring-up), requiring selective TAP activation.- **PHY-level test**: high-speed die-to-die SerDes links (e.g., UCIe, AIB) require loopback and eye-diagram tests that BSR alone cannot exercise.These limitations drove the development of IEEE P1838 as a purpose-built standard for 3D-IC test access.


## IEEE P1838: Die-Level Test Access Architecture

IEEE P1838 defines a scalable die-level test infrastructure for 2.5D/3D-stacked ICs. At its core, each die is wrapped with:
- **Wrapper Boundary Register (WBR)**: analogous to the 1149.1 BSR but placed at the die edge (TSV/micro-bump interface) to capture and drive inter-die signals.- **Wrapper Instruction Register (WIR)**: selects between test modes (e.g., `WP_BYPASS`, `WP_EXTEST`, `WP_INTEST`, `WP_SAMPLE`).- **TAP Link Module (TLM)**: present in each die, it bridges the package-level 1149.1 TAP to the die's internal dieTAP, managing address decoding and topology configuration.P1838 supports three TAP topologies: **Series** (daisy-chain, lowest pin count), **Parallel** (concurrent access, faster test), and **Star** (hierarchical addressing). The interface width is reconfigurable between 1-bit (minimal pin overhead) and wider modes for performance.


## Pre-Bond, Mid-Bond, and Post-Bond Test Flows

P1838 explicitly supports three test phases that align with the 3D-IC assembly flow:
- **Pre-bond test**: each known-good die (KGD) is tested individually using its dieTAP and WBR before stacking. WBR cells drive TSV probe-contactable pads; structural ATPG patterns verify logic and TSV continuity.- **Mid-bond test (partial stack)**: after bonding a subset of dies, the TLM routes test access to the bonded stack, enabling interconnect verification of already-joined TSV/micro-bump interfaces before adding remaining dies.- **Post-bond test**: the fully assembled package is tested via the external package TAP. The TLM daisy-chains or addresses individual die WBRs to run `WP_EXTEST` patterns across all inter-die interfaces simultaneously or sequentially.This phased approach maximizes defect isolation and reduces yield loss by detecting failures at the earliest (cheapest) assembly stage.


## ATE Implementation and Practical Considerations

On production ATE platforms (Advantest V93000, Teradyne UltraFLEX), P1838-based test is implemented via standard JTAG digital channels:
- **TCK rate**: typically 50-200 MHz for scan shift; slower rates (&lt;10 MHz) may be used during TLM topology configuration to respect setup/hold margins across die power domains.- **Vector format**: STIL (Standard Test Interface Language) or JTAG SVF files describe the TAP sequences; ATE pattern compilers expand these into digital vectors.- **Chain validation**: a `BYPASS` sweep across all dies in the chain counts total BSR/WBR cells to detect missing or miswired dies before running full ATPG patterns.- **Die addressing**: in parallel P1838 topologies, each die has a unique address loaded into the TLM address register before WIR/WBR operations, preventing data collision.- **Thermal ramp testing**: for HBM stacks, P1838 WBR patterns are run at both cold (-20 C) and hot (+85 C) to catch TSV stress-induced opens that are temperature-dependent.BSDL extensions (P1838-specific attributes `TSV_CELL` and `DIE_WRAPPER`) are used by EDA tools to auto-generate WBR patterns from the netlist.


## Key Takeaways

- IEEE 1149.1 boundary scan cannot access inter-die TSV and micro-bump interconnects in heterogeneous packages — its BSR only covers package-level I/Os.
- IEEE P1838 wraps each die with a Wrapper Boundary Register (WBR) and TAP Link Module (TLM), enabling EXTEST across TSV/micro-bump interfaces in pre-, mid-, and post-bond test flows.
- P1838's reconfigurable Series/Parallel/Star TAP topology lets teams balance pin-count overhead against test throughput on production ATE at TCK rates up to 200 MHz.

## References

1. **[IEEE]** IEEE Std 1149.1-2013: Standard for Test Access Port and Boundary-Scan Architecture — IEEE, 2013 — defines TAP controller FSM, BSR, BSDL, and mandatory/optional instructions
2. **[IEEE]** IEEE P1838: Standard for Test Access Architecture for Three-Dimensional Stacked Integrated Circuits — IEEE P1838 Working Group — defines WBR, WIR, TLM, and pre/mid/post-bond test methodology
3. **[Paper]** Marinissen, E.J. et al., IEEE P1838: DfT Standard-in-Progress for 2.5D, 3D-SIC, and Other Heterogeneous Integration — IEEE International Test Conference (ITC), 2018 — topology options, WBR cell design, ATE mapping
4. **[Paper]** Aerts, J. et al., Scan Test Solution for 3D Stacked ICs Using IEEE P1838 Standard — DATE 2019 — practical TAP Link Module implementation and series vs. parallel trade-offs
5. **[Paper]** Marinissen, E.J., Challenges and Emerging Solutions in Testing TSV-Based 2- and 3-Dimensional Stacked ICs — Design, Automation and Test in Europe (DATE) 2012 — TSV defect models and WBR ATPG coverage
6. **[IEEE]** IEEE Std 1687-2014: Standard for Access and Control of Instrumentation Embedded within a Semiconductor Device (IJTAG) — IEEE, 2014 — SIB-based dynamic scan path reconfiguration; complements P1838 for embedded instrument access

## Additional Learning: IEEE 1687 IJTAG: Embedded Instrument Access Across Die Stacks

While P1838 defines the outer test access wrapper for each die, IEEE 1687 (IJTAG) navigates within a die's embedded instrument network using Segment Insertion Bits (SIBs) to dynamically include or bypass instruments (BIST engines, voltage monitors, PLL lock detectors) in the scan path. In a heterogeneous package, the TLM selects a target die via P1838, then IJTAG SIB sequences reconfigure that die's internal scan network to access only the required instrument, eliminating the need to shift through the entire WBR for every access. This IJTAG-over-P1838 layering reduces per-instrument access time from O(N_wbr) to O(N_instrument), a critical optimization when WBRs on TSV-dense dies can contain thousands of cells.
