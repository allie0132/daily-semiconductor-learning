# Multi-Die Package Test: EMIB, Foveros & CoWoS Interposer Access

*Friday, Jul 24 2026*

*Module 12.1 — Heterogeneous Integration & Advanced Packaging Test*

## Why Multi-Die Packaging Changes the Test Paradigm

Traditional SoC test assumes a single die with full boundary scan access and a single set of I/O pads. Heterogeneous integration shatters this model: a finished package may contain 3–8 distinct dies from different process nodes, different foundries, and different vendors — each requiring **Known-Good Die (KGD)** qualification before assembly and **package-level interconnect verification** after bonding.
The three dominant 2.5D/3D interposer architectures — **Intel EMIB**, **Intel Foveros**, and **TSMC CoWoS** — impose fundamentally different test challenges because they differ in signal routing density, inter-die bandwidth, and the physical accessibility of die-to-die interconnects. A test strategy that works for CoWoS will not work for Foveros, and vice versa.
The core test challenges are: (1) achieving electrical access to embedded die pads after assembly, (2) structural testing of micro-bumps and hybrid bonds that cannot be probed directly, and (3) diagnosing failures localized to a single die vs. an interconnect layer vs. the package substrate.


## EMIB: Embedded Multi-die Interconnect Bridge

EMIB is Intel's 2.5D approach that replaces a full silicon interposer with a small silicon bridge embedded in the organic package substrate. High-density routing (line/space ~1 µm) exists only in the bridge area between adjacent dies; the rest of the substrate uses conventional organic routing.
Test implications: - Die-to-die interconnects cross the bridge in metal layers not accessible to external probing — test must rely on loopback structures and boundary scan via the **IEEE 1149.1 JTAG** chain that spans both dies.- Intel's implementation uses **IEEE 1500 Embedded Core Test** (ECT) wrappers on each chiplet, with a primary JTAG TAP that can serialize access to all wrappers across the bridge.- Bridge bump pitch is typically 55 µm — tighter than package bumps (~180 µm C4) but too coarse to individually probe after assembly. Resistance and continuity must be inferred from **die boundary scan loopback** or built-in self-test (BIST) of the inter-die link PHY.- Pre-bond die testing at wafer probe must exercise all EMIB-facing I/Os at speed, because any marginal bump that passes DC test may fail at the 32+ Gbps die-to-die link rate used in Ponte Vecchio / Meteor Lake architectures.
EMIB packages are tested with a two-phase strategy: **Phase 1** — full die test at wafer level using temporary probe pads; **Phase 2** — package-level JTAG loopback plus high-speed link BER testing after assembly.


## Foveros: 3D Face-to-Face Die Stacking

Foveros is Intel's 3D stacking technology where an active base die (bottom) is stacked with one or more top dies via copper micro-bumps at ~36–50 µm pitch, with through-silicon vias (TSVs) in the base die connecting to the package substrate below. This is a **face-to-face** or **face-to-back** orientation depending on the product generation.
Test challenges are more severe than EMIB:- **No direct probe access to the top die pads** after stacking — all test stimulus and response for the top die must route through the base die's TSVs and its JTAG infrastructure.- The base die must therefore implement a **test access mechanism (TAM)** per IEEE 1838 (<em>Standard for Die-to-Die and Die-to-Package Interconnect Test</em>), which defines a scalable wrapper architecture for 3D stacked dies.- Micro-bump opens and shorts between base and top die are tested using **IEEE 1838 die wrapper boundary scan** at the micro-bump interface — each micro-bump net has a capture/shift/update boundary scan cell on both the base-die pad and the top-die pad.- The base die's TSVs are tested pre-bond using **TSV probe-to-ring** structures and post-bond using resistance measurement through the package substrate path.- Thermal test (burn-in) of the stacked die is done at package level; local on-die temperature sensors (typically ring-oscillator based) accessible via JTAG scan are used to monitor junction temperature during burn-in.
Micro-bump continuity failures in Foveros are particularly hard to isolate: an open on a power micro-bump may appear as a functional failure in the top-die logic, not as an interconnect fault. BIST of on-die voltage regulators (VRs) and current-sense circuits helps separate power delivery failures from logic failures.


## CoWoS: Chip-on-Wafer-on-Substrate

TSMC's CoWoS places multiple dies side-by-side on a full-reticle (or stitched multi-reticle) passive silicon interposer, which then sits on an organic/ceramic package substrate. The interposer provides ultra-dense routing (CoWoS-S: ≥10,000 wires/mm at M1) and is itself a silicon die with no active transistors — test access to interposer metal layers is via the dies' I/O cells, not via independent scan chains in the interposer.
Key test considerations for CoWoS:- The passive interposer has no JTAG; all structural testing of interposer wiring is done indirectly through **boundary scan of the ICs mounted on it** (HBM PHY I/Os driving/sensing the interposer metal).- HBM stacks mounted on CoWoS have their own IEEE 1149.1 JTAG (available via JEDEC JESD235 Section 8, the DQ/CA test mode) — but the JTAG clock and data signals themselves route through the interposer metal, so interposer continuity must be validated before HBM JTAG can even be activated.- A common bootstrap sequence: apply VDD/VSS, force CA/CS test-mode entry via the HBM `MRS` command (register `MR2` bit 4 = PASR / test-mode flag), verify DQ loopback at low speed (80 MHz), then escalate to full-rate BIST (up to 6.4 Gbps for HBM3E) once interposer metal is confirmed good.- Micro-bump pitch between HBM and interposer is 55 µm (CoWoS-S generation 3+); between GPU/compute die and interposer it may be 130 µm. These require different bump continuity test approaches — the fine-pitch HBM bumps are tested via HBM DQ loopback BIST; the coarser compute-die bumps can be individually addressed via boundary scan.- **Interposer capacitance** (typically 8–15 pF/mm² for the dense redistribution layers) affects high-frequency loopback test sensitivity — test patterns must account for signal attenuation at 6+ Gbps through long interposer metal runs (&gt;10 mm).


## IEEE 1838 and the Unified 3D Test Access Framework

IEEE Std 1838-2019 (<em>Standard for Test Access Architecture for Three-Dimensional Stacked Integrated Circuits</em>) is the reference standard for all three architectures discussed above. It defines:- A **die wrapper** with inward-facing (toward inter-die interconnect) and outward-facing (toward substrate/package) test ports.- A **test elevator** — the mechanism by which test commands travel from the package substrate through stacked dies to reach the target die.- A **1838.1 compliance standard** for how dies enumerate their test capabilities to an external controller (ATE).
In practice, IEEE 1838 test access is serialized through a small number of physical pins on the package (typically 4–8 JTAG-style pins: TCK, TMS, TDI, TDO plus optional TRST and test-power pins). The ATE controller uses 1838 **segment insertion bits (SIBs)** to open or close segments of the wrapper chain, selectively bypassing dies not under test to reduce scan chain length and test time.
ATE implications: modern testers (Advantest V93000, Teradyne UltraFLEX) support IEEE 1838 test through dedicated Digital Pin Module (DPM) resources that can drive up to 1.6 Gbps on JTAG pins — critical for fast scan because a 12-module HBM3 stack with full die wrappers may have a scan chain length exceeding 200,000 bits at 1149.1 rates, requiring &gt;125 ms per pattern at 1 MHz TDO without SIB bypass.
Thermal test during 3D package burn-in uses **in-situ temperature monitoring via ring oscillators** accessible through the 1838 test access. Burn-in temperatures of 125–140°C are applied with the ATE running functional BIST on all dies simultaneously to maximize power density and accelerate early-life failure modes (electromigration, TDDB) in both logic and HBM DRAM layers.


## Key Takeaways

- EMIB, Foveros, and CoWoS each require distinct DFT insertion strategies because die-to-die interconnect accessibility, bump pitch, and routing layers differ fundamentally across architectures.
- IEEE 1838 provides the unified test elevator and die wrapper standard for 3D stacked packages — its SIB-based chain management is essential for managing scan chain length across multi-die stacks.
- KGD qualification at wafer probe must cover all package-facing I/Os at near-operating speed; marginal micro-bump performance missed at DC-only probe will cause package-level failures after assembly.

## References

1. **[IEEE]** IEEE Std 1838-2019: Test Access Architecture for 3D Stacked ICs — IEEE 1838-2019, Sections 5–8 (die wrapper, test elevator, SIB architecture)
2. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) DRAM Standard — JESD235C Section 8.3 — JTAG/Boundary Scan test access for HBM stacks
3. **[Paper]** Intel EMIB Technology Overview — Mahajan, R. et al., 'Embedded Multi-Die Interconnect Bridge (EMIB) — A High Density, High Bandwidth Packaging Interconnect,' IEEE ECTC 2016, pp. 557–565
4. **[Paper]** Intel Foveros 3D Stacking Architecture — Stow, D. et al., 'Cost and Profit Analysis of Heterogeneous Manycore Processors,' IEEE DAC 2017; Intel Foveros technical brief, 2022
5. **[Paper]** TSMC CoWoS Technology — Yu, C.H. et al., 'Chip-on-Wafer-on-Substrate (CoWoS) Technology for Integrated High Performance Computing,' IEEE ECTC 2012, pp. 1381–1385
6. **[Datasheet]** Advantest V93000 Multi-Die Package Test Application Note — Advantest AN-0042: 'Hierarchical Test Access for 2.5D/3D Multi-Chip Modules using IEEE 1838'

## Additional Learning: Hybrid Bonding DFT Challenges in Next-Gen 3D Integration

While micro-bumps (36–55 µm pitch) are tested via boundary scan loopback, next-generation <strong>hybrid bonding</strong> (SoIC, Cu-Cu direct bond) shrinks pitch to 1–10 µm — far below the resolution of any boundary scan cell. At these pitches, individual net access is impossible; instead, test relies on <strong>electrical continuity matrices</strong> (a checkerboard pattern of shorted vs. open pad pairs) and <strong>4-wire Kelvin resistance measurement</strong> through stacked functional paths to infer bond quality. TSMC's SoIC and imec's Besi hybrid bond processes target contact resistance below 10 mΩ per bond; production test must screen for opens (&gt;1 Ω) and marginal bonds (10–100 mΩ range) that cause speed degradation without hard failure.
