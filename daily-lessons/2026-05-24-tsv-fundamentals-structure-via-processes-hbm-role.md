# TSV Fundamentals: Structure, Via Processes & HBM Role

*Sunday, May 24 2026*

*Module 1.9 — Foundations*

## TSV Structure and Geometry

A Through-Silicon Via (TSV) is a vertical electrical interconnect that passes completely through a silicon die, forming the backbone of 3D-IC integration. In HBM devices, TSVs are cylindrical copper conductors surrounded by a dielectric liner (typically `SiO₂` or polymer) and a diffusion barrier (Ta/TaN or TiN) to prevent copper migration into the silicon substrate.
HBM TSV dimensions are tightly specified: diameter ranges from **8–12µm** for via-middle processes, with aspect ratios (depth:diameter) of **8:1 to 12:1**. The TSV pitch in current HBM3 stacks is **40µm**, enabling the 1024-bit wide interface per die stack. The via depth equals the thinned die thickness — typically **50–80µm** for HBM, compared to 200–700µm for unthinned wafers.
- **Liner:** 100–300nm SiO₂ grown by TEOS CVD — provides electrical isolation and CTE mismatch buffering- **Barrier:** 20–50nm TaN/Ta PVD — blocks Cu diffusion, ensures adhesion- **Seed:** 100nm Cu PVD — enables bottom-up electroplating fill- **Fill:** Electroplated Cu, bottom-up superconformal to minimize voids

## Via Formation Processes: First, Middle, and Last

TSVs can be formed at three different points in the die fabrication flow, each with distinct tradeoffs for HBM manufacturing:
**Via-First:** TSVs are etched before FEOL transistor fabrication. This avoids thermal budget conflicts but the TSV must survive all subsequent high-temperature steps (&gt;1000°C). Not used in HBM due to incompatibility with advanced CMOS nodes.
**Via-Middle:** TSVs are formed after FEOL (transistors complete) but before BEOL (metal interconnect layers). This is the **dominant process for HBM DRAM dies**. Thermal budget is limited to BEOL-compatible temperatures (&lt;400°C). TSV etch uses deep reactive ion etching (DRIE) with Bosch process — alternating SF₆ etch and C₄F₈ passivation cycles to achieve vertical sidewalls with &lt;2° taper.
**Via-Last:** TSVs are formed after all BEOL interconnects are complete, then the wafer is thinned from the backside to expose the via bottoms. Used in logic interposers and some 3D integration schemes. Allows TSVs to be added to finished chips but has the narrowest thermal budget constraint.
- HBM DRAM stacks use **via-middle** for the memory dies- The base die (logic die) may use via-last for integration flexibility- Bosch DRIE achieves 10:1 aspect ratio with &lt;±5% diameter uniformity across 300mm wafer

## TSV Role in HBM Die Stacking

HBM achieves its extraordinary bandwidth by stacking up to 12 DRAM dies vertically, connected through TSVs at a pitch far too fine for wire bonding. Each TSV carries one signal bit, power, or ground through the die stack. JEDEC JESD235C specifies the HBM3 interface as **1024 bits wide per stack**, requiring hundreds of TSVs per die.
The TSV signal path through a 4-die HBM stack sees each via as a transmission line stub. At HBM3's **6.4 Gbps/pin** data rate, the TSV capacitance (~50fF per via) and inductance (~100pH) must be characterized and accounted for in signal integrity modeling. Via-to-via coupling (crosstalk) between adjacent TSVs at 40µm pitch is managed through ground shield vias interspersed in the array.
- HBM3 stack: up to 12 DRAM dies + 1 base die = 13 thinned die layers- Micro-bump (Cu pillar + SnAg) pitch: **25µm** between die-to-die connections- TSV landing pad on backside: slightly larger than via diameter to accommodate wafer thinning overlay- Power delivery: dedicated TSVs for VDD, VSS, VDDQ reduce IR drop across die stack

## Electrical Characteristics and Parasitics

Each TSV is modeled as an RLC element plus substrate coupling capacitance. For a via-middle TSV (10µm dia, 60µm deep, Cu fill):
- **Resistance:** ~5–10mΩ (bulk copper resistivity 1.7µΩ·cm, adjusted for grain structure)- **Capacitance:** ~40–80fF (dominated by liner capacitance: C = 2πεL / ln(r_ox/r_cu))- **Inductance:** ~50–150pH (loop inductance, depends on return path)- **Substrate coupling:** The Si substrate acts as a lossy dielectric; the depletion region around the TSV liner creates a voltage-dependent capacitance (MOS-like behavior)The **keep-out zone (KOZ)** around each TSV must be free of active transistors due to mechanical stress from CTE mismatch between Cu (17ppm/°C) and Si (2.6ppm/°C). Typical KOZ radius is **2–5µm** from via edge — a significant area penalty that must be accounted for in die floorplanning and directly affects the cost of TSV density.
At HBM3 frequencies, TSV impedance is dominated by capacitance (~1.3Ω at 3.2GHz for 50fF), making TSV termination and equalization design critical for achieving &lt;1% BER at 6.4 Gbps.


## Wafer Thinning and Backside Processing

TSV exposure requires aggressive wafer thinning — one of the highest-risk steps in HBM manufacturing. Starting from a 300mm wafer at 775µm thickness, the process grinds and CMP the backside to 50–80µm, exposing TSV copper bottoms (called **via reveal** or backside via exposure).
The thinning sequence: **(1) Coarse grind** to ~100µm using diamond grinding wheel; **(2) Fine grind** to ~60µm; **(3) CMP/etch back** to reveal TSV bottoms with controlled protrusion (1–3µm Cu protrusion enables reliable micro-bump bonding); **(4) Backside passivation** with SiN or polymer; **(5) RDL** (redistribution layer) if needed for pad routing.
- Thinned dies at 50µm are mechanically fragile — handling requires **temporary bonding to carrier wafers** using thermoplastic or UV-release adhesives- Warpage becomes critical: 50µm Si with 8µm Cu TSVs creates significant bow (&gt;500µm on 300mm wafer) due to CTE mismatch — managed by stress-balancing backside films- Wafer-level testing (probe) typically occurs before thinning; post-thinning testing uses specialized thin-wafer chucks with vacuum backside support

## Key Takeaways

- Via-middle TSV process is standard for HBM DRAM dies: formed after FEOL transistors but before BEOL metal, using Bosch DRIE at 8–12µm diameter and 8:1–12:1 aspect ratio
- TSV parasitics (40–80fF capacitance, 50–150pH inductance) must be modeled for SI at HBM3's 6.4 Gbps; keep-out zones (2–5µm) impose a die area penalty around each via
- HBM stacking requires thinning dies to 50–80µm to expose TSV bottoms, creating warpage and handling challenges that dominate yield loss in 3D integration

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C (HBM3), Section 3 — Electrical Interface and TSV Array Specification, 2022
2. **[IEEE]** Through-Silicon Via Technology for 3D Integration — Banijamali et al., IEEE Transactions on Advanced Packaging, Vol. 41, No. 1, 2018 — TSV process flows and reliability
3. **[Book]** 3D IC Integration: TSV Process and Reliability — Lau, J.H., 'Through-Silicon Via (TSV) for 3D Integration', McGraw-Hill, 2013, Chapters 3–5
4. **[Datasheet]** SK Hynix HBM3 Process White Paper — SK Hynix HBM3 Product Brief, 2022 — 12-die stack, via-middle TSV, 1024-bit interface
5. **[Paper]** TSV Electrical Modeling for High-Speed 3D-IC — Xu et al., 'Compact RLC Model for TSV in 3D IC', IEEE Transactions on Electron Devices, Vol. 60, No. 3, 2013
6. **[JEDEC]** SEMI 3D Packaging Standards — Wafer Thinning — SEMI G86-0303E — Specification for 300mm Wafer Backgrinding and CMP Thinning Requirements

## Additional Learning: TSV Stress-Induced Mobility Shift and KOZ Optimization

The Cu-filled TSV generates thermo-mechanical stress in the surrounding silicon due to the 6.5× CTE mismatch between Cu and Si. This stress modifies carrier mobility via the piezoresistive effect — NMOS transistors within 5µm of a TSV can show up to 15% Idsat variation depending on orientation relative to the via. Advanced KOZ optimization uses finite-element stress simulation to place pull-up PMOS (which benefit from compressive stress) closer to the via than pull-down NMOS, reducing effective KOZ from 5µm to 2–3µm and recovering significant die area in dense TSV arrays.
