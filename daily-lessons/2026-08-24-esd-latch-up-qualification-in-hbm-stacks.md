# ESD & Latch-Up Qualification in HBM Stacks

*Monday, Aug 24 2026*

*Module 15.4 — Reliability & Qualification Testing*

## Why HBM Breaks the Classic HBM-ESD-Model Assumptions

The historical **Human Body Model (HBM)** ESD test (JS-001) was built around discrete-pin packages with modest pin counts and relatively long, resistive ESD current paths through package leadframes. HBM (High Bandwidth Memory) stacks invert nearly every one of those assumptions: thousands of microbumps and **TSVs (through-silicon vias)** per channel, ultra-low-inductance vertical interconnects, and pitches as tight as 30-40um in HBM3/HBM3E. The result is that classic HBM-model qualification (typically ±500V-±2000V per JS-001) tells you almost nothing about failure modes that actually occur during handling, socketing, and pick-and-place of an HBM cube on an interposer.
Because TSVs stack directly atop each other with minimal lateral resistance, a single ESD event injected at one microbump can propagate vertically through multiple dies before it reaches a clamp, stressing gate oxides on interior dies that the test engineer never directly probes.


## CDM: The Dominant Real-World Threat for HBM

**Charged Device Model (CDM)** testing per **JS-002 (ANSI/ESDA/JEDEC JS-002)** simulates the device itself accumulating charge (via triboelectric contact with tooling, tape-and-reel, or automated handlers) and then discharging through a single pin to a grounded surface in nanoseconds. This is the dominant field-failure mechanism for HBM because:
- Wafer thinning to 30-50um for TSV reveal increases triboelectric charging during die handling and thermocompression bonding (TCB).- Peak CDM currents are extremely high (multiple amps) over sub-nanosecond rise times, so package/interposer parasitic inductance dominates the voltage overshoot seen at the gate oxide — unlike HBM-model events which are current-limited by the 1.5kOhm/100pF RC network.- Base-die PHY I/O cells (DFI-mapped, JEDEC JESD238 for HBM3) sit closest to the microbump field and are the most CDM-exposed nodes.Typical component-level CDM qualification targets for fine-pitch HBM I/O are in the 125V-250V range (small package, field-induced small IC) — dramatically lower than HBM-model voltage classes — because the charge available on a small, thin die is limited, but the discharge impedance is nearly zero.


## HBM Model Testing: Still Required, Different Role

JS-001 HBM-model testing remains part of the qual matrix for the **interposer, substrate, and system-level connector interfaces** — i.e., anywhere a human or grounded fixture can contact package pins during board assembly or socket insertion, rather than the die-to-die microbump network. Class 2 (1kV-2kV) per JEDEC/JEP155/JS-001 is common for HBM controller-side ASIC pins that route to the interposer's RDL (redistribution layer).
- HBM-model events discharge through a 1500Ohm resistor with a 100pF source capacitor — long RC time constant (~150ns) that stresses different failure sites (metal fusing, junction thermal breakdown) than CDM's field-induced fast transient.- For 2.5D/3D HBM-on-interposer assemblies, HBM-model stress is most relevant at the C4 bump interface to the interposer and at wire-bond/RDL fan-out regions, not at TSV microbumps.- Distinguishing the two in a qual report matters: an ESD-induced fail traced to a TSV keep-out violation is a CDM/layout issue; a fail at the substrate ball is more likely HBM-model-relevant.

## Latch-Up Coupling with ESD Qualification

Latch-up qualification per **JESD78 (latest revision JESD78F)** is tested independently of ESD but the two share root causes in HBM stacks: parasitic PNPN thyristor structures activated by transient injection. In a 3D stack, TSV-adjacent wells experience higher substrate current density due to the vertical current return path through lower dies' power/ground TSVs.
- JESD78 I-test and V-test are applied per supply pin at 1.5x Vdd(max) trigger current thresholds, but for HBM base-die logic, additional guard-ringing around TSV landing pads is required because CDM-induced transients can pre-condition (heat/inject) the substrate immediately before a latch-up trigger event during burn-in or system power cycling.- Latch-up holding voltage margin must stay above the lowest core Vdd rail used across the stack (e.g., HBM3E core rails down to ~1.1V) — a shrinking margin as process nodes scale, since holding voltage drops faster than logic Vdd.- Package-level TSV-to-TSV spacing and n-well/p-well tap density around the microbump array are the primary layout levers for both CDM robustness and latch-up immunity — they are co-optimized, not solved separately.

## Qualification Flow on ATE and Bench

Practical qual flow for an HBM stack combines wafer-level CDM screening with assembled-stack HBM-model and latch-up testing:
- **Wafer-level CDM** (per JS-002) on base-die I/O cells before stacking, since a CDM fail found post-TCB requires scrapping the entire cube.- **Post-stack HBM-model** testing at the package pins/interposer interface after TCB and molding, verifying the assembly process itself hasn't introduced new discharge paths (e.g., via exposed TSV stubs).- **JESD78F latch-up** at both room temp and Tmax (typically 125degC) since HBM operates at elevated junction temps under sustained bandwidth load, and latch-up trigger current drops with temperature.- ATE correlation: post-ESD/latch-up stress, run the full JESD235-series functional and DC parametric suite (IDD, leakage, DQ eye) to catch latent gate-oxide damage that passes a simple continuity check but degrades BER over time.

## Key Takeaways

- CDM (JS-002) is the dominant real-world ESD threat for HBM TSV/microbump structures due to thin die and near-zero discharge impedance, typically qualified at 125V-250V — far lower than HBM-model voltage classes.
- HBM-model testing (JS-001) remains relevant for interposer/substrate/connector interfaces, not the TSV microbump field, and stresses different failure sites via its longer RC discharge.
- Latch-up (JESD78F) and ESD qualification share root causes in 3D stacks — TSV spacing and well-tap density around microbumps must be co-optimized for both, especially as holding voltage margin shrinks at scaled core Vdd.

## References

1. **[JEDEC]** Charged Device Model (CDM) ESD Test Method — ANSI/ESDA/JEDEC JS-002
2. **[JEDEC]** Human Body Model (HBM) ESD Test Method — ANSI/ESDA/JEDEC JS-001
3. **[JEDEC]** IC Latch-Up Test — JESD78F
4. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM Standard — JESD238
5. **[IEEE]** ESD Protection Design for TSV-based 3D-IC — Ker, M.-D. et al., IEEE Trans. Device and Materials Reliability
6. **[JEDEC]** Recommended ESD Target Levels for HBM I/O — JEP155 (Failure Mechanism Based Stress Test Qualification)

## 🔍 Additional Learning: Socketed CDM Testing for Known-Good-Die (KGD) Flows

Because a wafer-level CDM fail on an HBM base die can only be caught before TCB, many fabs now run 'socketed' or small-IC CDM per JS-002 directly on singulated KGD prior to stack assembly, using dedicated field-plate test heads sized for sub-100um pad pitch. This adds cycle time but avoids scrapping an entire 8-Hi or 12-Hi cube for a single CDM-induced gate rupture discovered only at final stack test.
