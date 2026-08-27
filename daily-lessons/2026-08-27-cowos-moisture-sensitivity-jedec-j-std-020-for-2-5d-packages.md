# CoWoS Moisture Sensitivity & JEDEC J-STD-020 for 2.5D Packages

*Thursday, Aug 27 2026*

*Module 15.7 — Reliability & Qualification Testing*

## Why 2.5D Packaging Demands Special Moisture Treatment

Chip-on-Wafer-on-Substrate (CoWoS) integrates an HBM stack and a host die (GPU/ASIC) side-by-side on a passive silicon interposer, which is then attached to an organic package substrate via C4 solder bumps. This architecture introduces at least four critical moisture-sensitive interfaces: (1) the microbump interfaces between HBM cubes and the interposer, (2) the underfill encapsulant beneath each HBM die, (3) the C4 underfill between interposer and organic substrate, and (4) the mold compound / EMC used over the assembly.
Unlike a monolithic flip-chip BGA where a single material system dominates, CoWoS stacks polymeric underfills with different coefficients of thermal expansion (CTEs) and differing moisture diffusion coefficients. The interposer itself is low-CTE silicon (~2.6 ppm/°C), sandwiched by high-CTE organic materials. Moisture absorbed into the underfill layers creates hygroscopic swelling stress that, during reflow, converts to high-pressure steam — the classic **popcorning** mechanism, but at finer-pitch and more vulnerable interfaces than traditional packages.


## JEDEC J-STD-020: MSL Classification Methodology

JEDEC J-STD-020 (revision E, 2014, and update D.1) defines Moisture Sensitivity Levels (MSL) 1 through 6 for non-hermetic SMD packages. The classification procedure soaks test specimens under controlled temperature/humidity conditions for a prescribed duration (the **soak floor time**), then subjects them to three reflow cycles at the peak temperature appropriate to their body size and lead style (260 °C for Pb-free packages above 1.6 mm body thickness per IPC/JEDEC J-STD-020 Table 5-2).
- **MSL 1:** Unlimited floor life at ≤30 °C / 85% RH. Soak: 85 °C / 85% RH for 168 h.- **MSL 2:** Floor life 1 year at ≤30 °C / 60% RH. Soak: 85 °C / 60% RH for 168 h.- **MSL 2a:** Floor life 4 weeks. Soak: 30 °C / 60% RH for 696 h.- **MSL 3:** Floor life 168 h (1 week). Soak: 30 °C / 60% RH for 192 h.- **MSL 4:** Floor life 72 h. Soak: 30 °C / 60% RH for 96 h.- **MSL 5:** Floor life 48 h. Soak: 30 °C / 60% RH for 72 h.- **MSL 5a:** Floor life 24 h. Soak: 30 °C / 60% RH for 48 h.- **MSL 6:** TOL (Time on Label) — bake before use. Soak: customer-defined.CoWoS packages typically classify at **MSL 3** due to the thick interposer-substrate assembly trapping moisture at depth. Some large CoWoS-S variants (full-reticle interposers, >1800 mm² package area) have been reported at **MSL 2a**, reflecting extended moisture diffusion paths in thicker substrates.


## Preconditioning Test Flow for CoWoS Reliability

The full preconditioning sequence per J-STD-020 Section 8 for a CoWoS assembly is:
- **Step 1 — Initial electrical test:** Baseline continuity and parametric capture. For HBM, use the JEDEC JESD235C self-test (BIST) mode to confirm all DQ, CA, and clock paths pass before moisture exposure.- **Step 2 — Bake:** 125 °C / ≤5% RH for 24 h (or 40 °C / ≤5% RH for 96 h for moisture-sensitive laminate substrates). This brings all package materials to a known dry baseline.- **Step 3 — Moisture soak:** Per MSL (e.g. 30 °C / 60% RH / 192 h for MSL 3). Temperature uniformity within ±2 °C and RH within ±3% RH per J-STD-020 Section 7.4.- **Step 4 — Reflow simulation (×3 cycles):** IR or convection reflow to 260 °C peak, ramp rate ≤3 °C/s, time above liquidus 20–40 s. For CoWoS this is critical — the silicon interposer acts as a heat spreader, slowing the topside thermal ramp; profile verification with a thermocouple on the package corner is mandatory.- **Step 5 — Post-reflow inspection:** C-SAM (scanning acoustic microscopy) at ≥15 MHz to detect delamination at all critical interfaces. Cross-section SEM on failing units to characterize crack path (underfill cohesive, interfacial, or silicon fracture).- **Step 6 — Electrical re-test:** Full JESD235C BIST plus leakage checks between adjacent HBM channels (looking for ionic contamination paths).

## Critical Failure Modes in CoWoS Moisture Preconditioning

Several failure mechanisms are unique or amplified in 2.5D integration:
- **Interposer-substrate C4 underfill delamination:** The C4 underfill is stressed by CTE mismatch between the silicon interposer (~2.6 ppm/°C) and the organic substrate (~17 ppm/°C). Absorbed moisture plasticizes the underfill and reduces its glass transition temperature (Tg), lowering the critical stress at the interface precisely when reflow thermal excursion is greatest.- **HBM microbump underfill delamination:** 55 µm-pitch copper microbumps on 30 µm height specifications (JESD235C Table 10) have very thin underfill standoff. Moisture-induced delamination here appears as ≥5 µm voids on C-SAM, often at the Cu/epoxy interface.- **Silicon interposer cracking:** Steam pressure generated in interposer-level underfill can nucleate and propagate cracks in the silicon interposer itself — a brittle failure mode absent in organic-only packages. Fracture toughness of silicon (~0.7 MPa·m½) is far lower than typical underfill polymers in tension, making crack arrest difficult once initiated.- **Package warpage amplification:** Moisture uptake differential between the thick organic substrate and the silicon interposer produces a moisture-driven warpage component that adds to the thermally-driven warpage at reflow. For CoWoS-S packages with 2× full-reticle interposers, shadow moiré measurements show 150–300 µm additional warpage contribution from moisture alone.

## Test Engineering Implications: Handling, Baking, and ATE Integration

For a test engineer, J-STD-020 MSL rating has direct implications across the product lifecycle:
- **Post-singulation handling:** CoWoS packages must be placed in dry-pack (MBB + desiccant + HIC card) immediately after strip test on the tester. Exceeding the floor life without rebaking invalidates MSL qualification and can cause field failures at the customer's SMT line.- **ATE socket thermal stress:** Test sockets on high-power HBM ATE (e.g. Advantest T2000 or Teradyne UltraFlex) apply contact forces of 50–100 gf per ball on LGA/BGA pads and operate at elevated DUT temperatures (75–85 °C junction for HBM burn-in). The combination of mechanical stress and moderate heat in a post-moisture-soak package can cause latent delamination detectable only by subsequent C-SAM — a subtle reliability risk if pre-test bake is skipped.- **Incoming quality control:** For subcon test houses receiving CoWoS packages from TSMC CoWoS-S or CoWoS-R lines, the HIC (Humidity Indicator Card) inside the dry-pack must show <10% RH at all three indicator spots before opening. If any spot is pink (>10%), a 125 °C / 24 h bake is mandatory before socket loading.- **Rebake limits:** J-STD-020 Section 9.3 specifies a maximum of 3 total bake cycles to avoid laminate delamination and underfill degradation in the package substrate itself. Track bake count in the device traveler for CoWoS high-mix lots.

## Key Takeaways

- CoWoS 2.5D packages classify at MSL 3 (or MSL 2a for large interposers) due to complex multi-material interfaces that trap moisture at depth.
- J-STD-020 preconditioning requires a full bake → soak → 3× reflow sequence; C-SAM inspection after reflow is mandatory to catch interposer-level delamination.
- Moisture plasticizes underfill below its Tg during reflow, promoting C4 underfill and microbump delamination — the dominant CoWoS failure mode in MSL testing.
- Test engineers must enforce dry-pack handling, HIC checks, and bake-count tracking to preserve MSL compliance across the test floor lifecycle.

## References

1. **[JEDEC]** Moisture/Reflow Sensitivity Classification for Nonhermetic Solid State Surface Mount Devices — J-STD-020E, IPC/JEDEC, 2014 — Sections 7, 8, 9 define soak conditions, preconditioning flow, and floor life limits
2. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, 2021 — Section 10: mechanical dimensions including microbump pitch and underfill height
3. **[JEDEC]** Handling, Packing, Shipping and Use of Moisture/Reflow Sensitive Surface Mount Devices — J-STD-033D, IPC/JEDEC, 2018 — Dry-pack requirements, HIC specification, bake procedures
4. **[Paper]** Reliability of CoWoS-S: Thermal Cycling, Moisture Preconditioning, and Drop Tests — TSMC / ECTC 2022 — MSL classification results for full-reticle CoWoS-S; C-SAM delamination rates vs. underfill material
5. **[IEEE]** Moisture-Induced Failures in 2.5D IC Packaging — IEEE Trans. Components, Packaging and Manufacturing Technology, vol. 13, no. 4, 2023 — Steam pressure modeling and silicon interposer crack propagation
6. **[Book]** Advanced Packaging Reliability Handbook — Lau, J.H., 'Advanced MEMS Packaging,' McGraw-Hill, 2010 — Chapter 8: moisture sensitivity, CTE mismatch, and underfill selection for 2.5D

## Additional Learning: Shadow Moiré Warpage and MSL Interaction in CoWoS

Moisture absorption in CoWoS packages produces a warpage component orthogonal to the thermally-driven warpage measured in standard reflow profiles. Full-field shadow moiré measurements (per IPC-TM-650 2.4.25) on CoWoS-S packages after J-STD-020 MSL 3 soak show warpage contributions of 150–300 µm from moisture alone at room temperature, which then superpose with the 300–500 µm thermal warpage peak at 260 °C reflow. This combined warpage pushes some large-body CoWoS packages beyond the 150 µm total warpage budget assumed in SMT coplanarity specs (IPC-7093), meaning MSL qualification and warpage characterization must be co-optimized with underfill selection — not treated as independent qualification modules.
