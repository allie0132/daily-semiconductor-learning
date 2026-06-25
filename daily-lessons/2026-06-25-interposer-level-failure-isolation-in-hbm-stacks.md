# Interposer-Level Failure Isolation in HBM Stacks

*Thursday, Jun 25 2026*

*Module 7.3 — Advanced Test Methodologies*

## Why Interposer-Level Isolation Matters

In 2.5D integration, the silicon interposer is the critical interconnect fabric linking HBM stacks to the logic die. A fault anywhere on the interposer — broken TSV, delaminated micro-bump, open RDL trace — manifests identically at the package pins as a DRAM access failure. Without dedicated interposer test strategies, root-causing yield loss between the interposer, the HBM stack, and the logic die is essentially impossible without destructive cross-sectioning.
JEDEC JESD235C identifies the interposer as a distinct test boundary, and leading OSATs now require interposer-level known-good-die (KGD) qualification before KGD stacks are bonded. Isolating failures at this level saves re-work cost and prevents good DRAM stacks from being scrapped alongside a faulty interposer.


## Passive Interposer Test Strategies

Passive strategies test the interposer as a bare, unpowered substrate before any die is attached. They rely on external test equipment making contact directly with interposer pads or via a dedicated test socket.
- **TSV Continuity / 4-wire Kelvin:** Force current through each TSV top-to-bottom via probe; measure resistance. A broken or voided TSV shows >5 Ω vs. the nominal &lt;0.5 Ω specification. This catches Cu void defects introduced during Via-Middle or Via-Last TSV processes.- **RDL Open/Short:** Parametric tester applies a voltage to each RDL segment and detects capacitive or resistive discontinuities. Flying-probe or pogo-pin fixtures are used when pitch allows; fine-pitch RDL (&lt;2 µm) requires e-beam inspection instead.- **Leakage / Isolation:** Apply voltage between adjacent signal TSVs or between TSV and substrate; measure leakage. Fails indicate incomplete oxide liner deposition (Via-Middle) or metallic bridging from CMP residue.- **Time-Domain Reflectometry (TDR):** Inject a fast-edge signal into a TSV or RDL net and measure the reflected waveform. Impedance discontinuities from delamination, copper hillocks, or partial opens appear as distinct reflection events with ps-level time resolution.Passive strategies are fast and cheap per unit but require a dedicated probe card or socket, and they cannot detect failures that only manifest under thermal or signal-integrity stress at operating frequencies.


## Active Interposer Test Strategies

Active strategies exercise the interposer after partial or full assembly using embedded or exogenous test circuitry. They catch defects that only appear when the interposer is under realistic electrical load.
- **JTAG / IEEE 1149.1 Boundary-Scan:** If the interposer contains any active devices (e.g., SerDes PHY tiles or power-management blocks), boundary-scan cells on each I/O can be loaded and captured to verify connectivity to the bonded die. Interconnect defects manifest as stuck-at faults captured in the boundary-scan register. JESD235C Annex A recommends boundary-scan coverage for any active interposer element.- **BIST-driven TSV Loopback:** In heterogeneous assemblies where the logic die is attached first (die-last flow), the logic die's built-in self-test (BIST) engine drives signals through HBM channel micro-bumps, down through interposer TSVs, and back via the loopback path. Pass/fail per bump-pair isolates opens to the specific TSV or micro-bump. SK Hynix and Samsung HBM3 characterisation reports describe loopback BIST structures that verify all 1024-bit channel interconnects at 1600 MT/s.- **Thermal Cycling Under Bias (TCUB):** Active stress with a powered ATE stimulus while cycling temperature from –40 °C to +125 °C; captures intermittent opens caused by CTE mismatch at the Cu–oxide TSV interface. ATE systems such as the Advantest T2000 and Teradyne UltraFlex support temperature-forcing during scan test.- **High-Speed Eye Diagram:** For interposers carrying differential links or HBM PHY lanes, a pattern generator drives PRBS-15 or PRBS-31 at target rate; a sampling oscilloscope or on-die scope captures the eye. Eye height and width below the mask limits identify ISI from RDL stub resonance or TSV capacitance mismatch.

## Failure Signature Differentiation

A critical practitioner skill is distinguishing interposer-origin failures from HBM stack failures given the same symptom (e.g., `CATTRIP` assertion or uncorrectable ECC). The following heuristics are used at major OSATs:
- **Single-column vs. single-bit fail:** A HBM DRAM cell failure typically yields a single-bit or single-row/column failure in functional test. An interposer TSV open yields all bits on the same DQ net — spanning rows, columns, and banks — because the physical data path is severed at the package level.- **Temperature dependency:** Interposer micro-bump delamination failures typically worsen sharply above 85 °C due to CTE-mismatch stress. HBM cell retention failures show the opposite trend (improve at elevated temperature in most DRAM failure modes).- **Resistance profiling:** Before destroying the unit, probing accessible interposer test points (if designed in) with a μΩ-resolution 4-wire bridge localizes a high-resistance TSV versus a known-good reference, narrowing the fault to the interposer without decapping.

## Design-for-Testability (DfT) for Interposers

Mature interposer DfT practice embeds structures that support both passive KGD screening and post-assembly active test:
- **Test access ports (TAPs):** Dedicated probe pads on the interposer top surface, accessible before die attach, connected directly to TSV groups. These allow pre-bond resistance measurement without contaminating the final bump pads.- **Loopback TSV pairs:** Adjacent TSVs shorted at the bottom via the redistribution layer form a U-shaped loopback. An external tester drives current in one TSV and measures it out the other, confirming both vias and the RDL bridge are intact in a single vector.- **ESD-protected test pads:** Dedicated Kelvin probing pads with ESD clamps prevent electrostatic damage to sensitive FinFET gate stacks on the logic die during bare-interposer high-voltage continuity testing.- **Thermal test structures:** Daisy-chain serpentine RDL resistors placed at corners of the die-attach zone measure TCR-based temperature and detect thermal gradients that correlate with micro-bump voiding.The IEEE P1838 multi-die test standard (2021) provides a unified framework for TAP hierarchy across chiplet and interposer layers, and its adoption in HBM4 designs is expected to significantly reduce root-cause cycle time.


## Key Takeaways

- Passive interposer tests (TSV continuity, TDR, RDL open/short) screen bare substrates pre-bond and are fast but miss stress-dependent failures.
- Active strategies (BIST loopback, JTAG boundary-scan, TCUB) catch defects that only appear under realistic electrical and thermal load, with BIST loopback localizing failures to individual TSV/micro-bump pairs.
- Failure signature analysis — column-wide vs. single-bit, temperature polarity, resistance profiling — differentiates interposer-origin faults from HBM stack faults without destructive analysis.
- DfT structures (loopback TSV pairs, Kelvin probe pads, daisy-chain thermal resistors) are essential for cost-effective interposer KGD qualification at high volume.
- IEEE P1838 and JEDEC JESD235C together define the evolving standards framework for multi-die and interposer testability in HBM assemblies.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — JESD235C, sections 4 and Annex A — PHY architecture, boundary scan, and test access requirements
2. **[IEEE]** IEEE P1838 Standard for Test Access Architecture for Three-Dimensional Stacked ICs — IEEE P1838-2021 — TAP hierarchy, die-level and interposer-level test access port structure
3. **[Paper]** TSV Reliability and Characterization for 3D IC Integration — Ranganathan N. et al., IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 8, 2018
4. **[Paper]** HBM3 Test Architecture and BIST Loopback Characterization — SK Hynix, Hot Chips 34 (2022) — describes loopback BIST at 1600 MT/s for 1024-bit channel verification
5. **[Datasheet]** Advantest T2000 HBM Test Solution — Application Note — Advantest Corp., AN-T2000-HBM-001 — temperature-forcing during scan test, TCUB methodology
6. **[Paper]** 2.5D/3D IC Assembly and Test: Known Good Interposer Qualification — Lau J.H., Microelectronics Reliability, Vol. 55, 2015 — passive and active KGD strategies for organic and silicon interposers

## Additional Learning: Micro-bump Open Detection via AC Impedance Spectroscopy

A promising extension of passive interposer testing uses AC impedance spectroscopy (EIS) rather than DC resistance to characterize micro-bump integrity. By sweeping frequency from 1 kHz to 1 GHz across a bump pair, the complex impedance spectrum distinguishes a fully open bump (purely capacitive, no resistive component) from a partially delaminated bump (series RC with a distinctive inflection frequency around 10–100 MHz). This technique, adapted from MEMS packaging characterization, has been demonstrated in research settings to detect sub-micron delaminations in Cu-pillar solder-cap micro-bumps before they progress to a hard open — providing a leading indicator that DC continuity testing misses entirely.
