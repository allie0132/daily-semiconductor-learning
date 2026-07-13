# HBM Chiplet Ecosystem: Open Standards & Multi-Vendor Stacking

*Monday, Jul 13 2026*

*Module 9.7 — HBM4 & Next-Generation Technologies*

## Die Disaggregation and the Chiplet Paradigm in HBM Systems

Die disaggregation decouples monolithic SoC design into discrete functional tiles—compute dies, I/O dies, HBM stacks, and analog chiplets—connected via high-density 2.5D or 3D interconnects. For HBM, this manifests as the memory stack (DRAM dies + base die) being a discrete chiplet mounted alongside compute on a silicon interposer or bridge. This paradigm emerged from economic pressure: at advanced nodes (&lt;5 nm), large monolithic dies face exponential yield loss, whereas combining optimized smaller chiplets—each fabbed at its ideal node—can recover system yield while reducing cost-per-function.
The HBM base die (also called the logic die) aggregates all DRAM interface logic, the PHY, and acts as the internal vertical interconnect hub via through-silicon vias (TSVs). In a chiplet HBM system, the base die's `CA` (command/address), `DQ`, and `DRAM_CLK` interfaces fan out to the interposer, where they rendezvous with the SoC or ASIC die. JEDEC JESD235D (HBM3) and JESD238 (HBM3E) precisely define the ball map and electrical interface, enabling any compliant HBM stack to pair with any compliant host.
Test implication: when disaggregating, each chiplet must be characterized independently as **Known-Good Die (KGD)** before assembly. Reworking a stacked package post-bond is largely impractical, so pre-bond wafer-level testing and KGD certification are critical cost gates.


## Open Interconnect Standards: UCIe, AIB, and Bunch-of-Wires

Three competing—and sometimes complementary—open die-to-die interconnect standards govern how chiplets communicate on an interposer or organic substrate:
- **UCIe (Universal Chiplet Interconnect Express) 1.1**: Industry-standard (promoted by Intel, AMD, ARM, TSMC, Samsung) defining both a physical layer (Advanced and Standard bump pitches: 25 µm and 55 µm respectively) and a protocol layer stack mapping PCIe or CXL protocol traffic over die-to-die links. UCIe is NOT used for the HBM–host interface itself—HBM uses its own JEDEC-defined PHY—but UCIe may connect a disaggregated HBM controller chiplet to the compute die.- **AIB (Advanced Interface Bus)**: Intel's open standard (v2.0), using a 2-mm pitch bump array and FIFO-based architecture. AIB underpins Intel's EMIB (Embedded Multi-die Interconnect Bridge), offering 2 Tb/s/mm bandwidth density. AIB is technology-node agnostic, enabling, e.g., a 5 nm compute tile to connect to a 7 nm I/O tile without ESD or level-translation overhead at the die edge.- **BoW (Bunch of Wires)**: Open Compute Project (OCP) standard for extremely short-reach (&lt;2 mm) die-to-die links, targeting &lt;1 pJ/bit energy. BoW defines signal integrity requirements for 1–16 Gbps per lane with minimal encoding overhead, making it attractive for chiplet fan-out at 10–40 µm bump pitch.For HBM specifically, the **HBM PHY interface** defined in JESD235/238 is distinct from all three—it is a parallel, pseudo-open-drain bus operating at 3.2–6.4 Gbps/pin (HBM3E), using DBI (Data Bus Inversion) and CRC. The interposer wiring between HBM PHY bumps and SoC PHY bumps must meet tight impedance (**~50 Ω differential, ±10%**) and length-matching (&lt;0.1 mm skew) requirements specified in the JESD235D electrical appendix.


## JEDEC Standards Enabling Multi-Vendor HBM Interoperability

JEDEC's HBM standardization chain directly enables the multi-vendor ecosystem:
- **JESD235D (HBM3)**: Defines the 64-bit channel architecture, 1024-bit wide interface (16 channels × 64 DQ), ball map for 2-hi through 12-hi stacks, timing parameters (`tCK` min = 312.5 ps for 3.2 Gbps), and Mode Register (MR) address map.- **JESD238 (HBM3E)**: Extends HBM3 to 6.4 Gbps/pin DDR signaling. New fields in MR32/MR33 expose per-channel per-side temperature sensors, and MR40 adds `RD_PREAMBLE` control for half-cycle read latency trim.- **JESD235-1 (HBM2E)**: Still widely deployed (A100 GPU, MI200 APU). Defines 2.4 Gbps per pin and 8-hi max stack with 307.2 GB/s/stack bandwidth.The ball map standardization is particularly powerful: an HBM3 stack from Samsung, SK Hynix, or Micron will present identical `CA`, `DQ`, `VDDQ`, `VSS`, `ZQ`, and `AREF` bump locations to the interposer. However, **Mode Register defaults, BIST engine capability, and DFT (Design for Test) vendor extensions differ**—this means an ATE program targeting Samsung HBM3 may need conditional branches to handle Hynix's different MR30 `VENDOR_ID` response and slightly different MBIST sequence ordering.
JEDEC JEP106 (Manufacturer ID standard) provides the `MANUFACTURER_ID` field readable at MR26[7:0] in HBM3, allowing automated test firmware to branch on vendor identity and apply vendor-specific BIST invocations.


## Known-Good-Die (KGD) Test Methodology for Multi-Vendor Stacking

Multi-vendor chiplet stacking makes KGD testing the most critical yield lever. Stacking a defective DRAM die onto a known-good SoC results in a worthless assembly costing 10–30× the DRAM die alone in interposer, substrate, and assembly charges. The KGD flow for HBM involves three test stages:
- **Wafer sort (pre-dicing):** Full functional test at wafer level using a wafer probe card making contact to the micro-bumps (top TSV pads) or the base die C4 bumps. ATE applies the **HBM JTAG TAP** (defined in JESD235 section 8) for boundary scan of all I/O cells, then runs `MBIST` (on-die memory BIST) via Mode Register commands `MR13` (HBM3) to stimulate address/data patterns. Parametric tests include `IDD` profiling, ZQ calibration convergence (&lt;512 cycles to lock), and DBI functionality verification.- **Burn-in at stack level (pre-package):** After DRAM die stacking but before host SoC attachment, the HBM stack undergoes compressed voltage/temperature stress. HTOL (High-Temperature Operating Life) at **125°C, VDDQ +10%** for 48–96 hours screens for infant mortality in the TSV fill and microbump solder.- **Post-assembly system-level test (SLT):** After CoWoS or EMIB package assembly, the full stack is exercised via the host SoC DRAM controller. Marginal interconnects that passed wafer-level test may fail post-assembly due to interposer stress, underfill-induced microbump fatigue, or thermal mismatch. SLT uses the same ATE `HBM functional patterns` but now accessed through the SoC register interface rather than direct probe.Industry benchmark: HBM KGD yield typically requires &gt;99.8% die-level pass rate to keep assembly loss below 0.4% (assuming 2-HBM-stack + SoC, and CoWoS substrate cost of ~$2000).


## Multi-Vendor Stacking Challenges: Assembly Tolerance and Supply Chain

Even with fully JEDEC-compliant HBM stacks, multi-vendor stacking raises practical engineering challenges:
- **Microbump pitch tolerances:** HBM microbumps are specified at **55 µm pitch (C2 bumps)** on the base die. However, Samsung, SK Hynix, and Micron use different bump metallurgy (Cu-pillar + SnAg, vs. Cu-pillar + In-solder) affecting solder collapse height by ±2–5 µm—critical for interposer design rules. OSAT (Outsourced Assembly &amp; Test) vendors must qualify each HBM vendor's bump profile separately.- **Thermal resistance (θJC) variation:** The thermal stack (DRAM dies + mold compound + TIM1) varies by ±15% between HBM vendors for the same stack height, affecting how the cooling solution is designed. GPU vendors like NVIDIA and AMD must thermal-characterize each HBM supplier's stack using JEDEC JESD51 measurement methodology.- **Vendor-specific BIST extensions:** SK Hynix HBM3 exposes a `REPAIR_ENTRY` mode via MR28[3:0] (vendor-reserved) that allows post-package **row repair** via laser fuse. Samsung uses a different MR encoding for the same capability. Test programs must abstract these differences behind a vendor-specific shim layer in the ATE pattern set.- **Supply chain qualification cycles:** Qualifying a new HBM vendor from scratch typically requires 6–12 months of characterization, interoperability testing, and reliability qualification, creating significant lead-time risk for hyperscaler AI chip programs.The industry is moving toward **JEDEC JEP30** part marking and **shared characterization data formats** (analogous to IBIS models for memory) to reduce per-vendor qualification burden, but no formal standard exists yet for HBM chiplet characterization data exchange.


## Key Takeaways

- JEDEC JESD235D/JESD238 ball-map standardization enables multi-vendor HBM sourcing, but vendor-specific MR extensions and BIST sequences require conditional ATE branches keyed on MR26 MANUFACTURER_ID.
- UCIe, AIB, and BoW are die-to-die chiplet interconnect standards used for chiplet-to-chiplet links; the HBM–host interface itself is governed exclusively by the JEDEC HBM PHY specification.
- KGD test yield must exceed 99.8% at wafer sort to keep multi-chiplet assembly loss economically viable, requiring full MBIST, ZQ calibration, and HTOL burn-in before host integration.
- Microbump metallurgy differences between HBM vendors (SnAg vs. In-solder) affect bump collapse height by ±5 µm, requiring per-vendor OSAT qualification even for JEDEC-compliant parts.
- Vendor-specific row-repair MR encodings and thermal resistance variations make multi-vendor HBM programs significantly more complex than single-vendor sourcing strategies.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) SDRAM Standard — JESD235D, JEDEC Solid State Technology Association, 2022 — Sections 4 (signal interface), 8 (JTAG), Annex A (ball map)
2. **[JEDEC]** High Bandwidth Memory (HBM3E) SDRAM Standard — JESD238A, JEDEC Solid State Technology Association, 2023 — Sections 6 (MR map), 9 (electrical spec at 6.4 Gbps)
3. **[Web]** Universal Chiplet Interconnect Express (UCIe) Specification 1.1 — UCIe Consortium, 2023 — uciexpress.org — Sections 2 (physical layer), 5 (protocol stack)
4. **[Web]** Advanced Interface Bus (AIB) 2.0 Specification — Intel / CHIPS Alliance open-source release, 2020 — github.com/chipsalliance/aib-protocols
5. **[Web]** Bunch of Wires (BoW) Interface Specification 1.0 — Open Compute Project (OCP), 2019 — opencompute.org, HW Management subproject
6. **[Paper]** CoWoS Technology and Chiplet Integration for HBM — C.-S. Yeh et al., 'CoWoS-S Technology for Advanced Chiplet Integration,' IEEE IEDM 2022, pp. 14.1.1–14.1.4
7. **[JEDEC]** JEDEC JEP106: Standard Manufacturer's Identification Code — JEP106BL — used for MR26 MANUFACTURER_ID field in HBM3/HBM3E: Samsung=0xCE, SK Hynix=0xAD, Micron=0x2C

## Additional Learning: HBM4 and the Shift to Monolithic Base Die with UCIe

HBM4 (targeting 2025–2026 production) is expected to introduce a significantly redesigned base die that integrates the PHY and partial memory controller logic, blurring the line between HBM stack and compute chiplet. Early JEDEC HBM4 drafts (JESD235E, in ballot as of 2024) propose optional UCIe-compatible die-to-die interface pads on the base die periphery, enabling future configurations where HBM logic is directly wired to an adjacent compute chiplet without passing through the interposer metal layers. This would reduce interposer routing congestion by ~30% for 4-stack configurations and allow tighter latency budgets—but it would also require UCIe PHY silicon area on the base die, directly competing with DRAM array density.
