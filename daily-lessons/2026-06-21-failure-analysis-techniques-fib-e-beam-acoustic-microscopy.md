# Failure Analysis Techniques — FIB, e-beam, Acoustic Microscopy

*Sunday, Jun 21 2026*

*Module 6.5 — Advanced Topics*

## Focused Ion Beam (FIB) Cross-Sectioning for Defect Localization

**FIB fundamentals:** Focused ion beam systems use Ga+ or Xe+ ions accelerated at 5–30 keV to mill precise cross-sections through die, interconnects, and packaging materials. Ion currents range from sub-picoampere (imaging) to microampere (milling) for high material removal rates.
- **Imaging mode:** Secondary electron (SE) or secondary ion (SI) detection at sub-50 nm resolution reveals interconnect opens, voids in solder bumps, and metal migration paths.- **Milling mode:** Trenches etched at controllable depth (typically 50–500 nm/pass) enable layer-by-layer analysis of interconnect stacks, revealing current crowding, electromigration damage, and wire bond delamination at metal/dielectric interfaces.- **Gallium implantation:** Residual Ga+ implantation (typically 10¹⁴–10¹⁶ cm⁻³ near surface) degrades electrical properties; platinum deposition protects critical features during milling.**Practical tip:** For HBM-failed parts, cross-section at the die edge corner where current density peaks (approximately 3–5× bulk density under ESD stress). Use dual-beam FIB with in-situ SEM to observe milling in real-time and avoid over-milling thin gate oxides.


## Scanning Electron Microscopy (SEM) and e-beam Analysis

**SEM for failure root-cause:** High-resolution SEM (15 keV primary beam, 1–2 nm spot size) detects metallurgical signatures: grain boundaries, voids, intermetallic thickness anomalies, and corrosion products that correlate to failure mechanisms.
- **Energy-Dispersive X-ray (EDX) spectroscopy:** Point or line-scan analysis identifies elemental composition at failure sites. Example: Cu-Sn intermetallic (Cu₆Sn₅) thickness &gt;3 µm in solder joints indicates thermal cycling fatigue risk; Al-Cu intermetallic at wire bond interface suggests corrosion initiation.- **Electron Backscatter Diffraction (EBSD):** Maps crystallographic orientation and grain size. Recrystallized grains (&lt;1 µm) in solder after thermal shock indicate plasticity exhaustion; preferred &lt;100&gt; orientation in Cu traces suggests electromigration-induced grain boundary motion.- **Charge contrast imaging:** Biasing the sample at +1–5 kV reveals subsurface defects (cracks, voids) within 100–200 nm depth without destructive milling; useful for detecting latent defects in underfill or molding compound.**Critical parameter:** Accelerating voltage selection: 5 keV for near-surface work (top 50 nm), 15–20 keV for bulk analysis (500 nm–2 µm depth penetration).


## Acoustic Microscopy for Subsurface Void & Delamination Detection

**Scanning Acoustic Microscopy (SAM) principles:** A pulsed ultrasonic transducer (typically 75–230 MHz frequency) launches acoustic waves through the package; reflected signals map mechanical impedance boundaries. Voids, delaminations, and moisture-saturated regions exhibit acoustic mismatch and appear as dark regions in C-scan images.
- **Frequency selection:** 75 MHz (10 µm wavelength) penetrates through substrate and reveals die-attach voids, solder ball voids; 230 MHz (4 µm wavelength) resolves fine features in molding compound but with limited depth (1–2 mm).- **Time-of-flight (ToF) gating:** Pulse-echo timing isolates reflections from specific layers. Example: setting ToF window to 2.0–2.5 µs captures interface between molding compound and substrate; voids in die-attach return earlier echoes (1.2–1.8 µs).- **Delamination criterion (JESD035):** Acoustic signal loss &gt;6 dB relative to bonded area indicates incipient delamination risk; &gt;12 dB loss is failure-critical. Maps show location, size (&gt;0.5 mm²), and progression between thermal cycles.- **Moisture ingress detection:** Water-saturated molding has ~40% reduced acoustic impedance vs. dry molding, creating distinct contrast. Sensitivity reaches ~5% moisture content by mass.**Limitation:** Cannot distinguish void types (gas vs. moisture); requires correlation with other techniques (SEM-EDS, thermomechanical FEA).


## Integrated Failure Analysis Workflow

**Sequential multi-technique approach:** Acoustic microscopy → SEM baseline imaging → FIB cross-section → SEM-EDX/EBSD at failure site.
- **Stage 1 — Acoustic baseline:** SAM scan entire package to map macroscopic voids, delaminations, and moisture zones without material destruction. Identify highest-risk regions for targeted cross-sectioning.- **Stage 2 — SEM surface prep:** Cross-section sample at SAM-flagged location using precision saw + mechanical polishing (0.25 µm diamond finish) or ion milling to remove polishing artifacts that obscure true defect morphology.- **Stage 3 — FIB targeted milling:** Use SEM images to navigate to defect; FIB mill perpendicular to failure feature (e.g., mill across a suspected interconnect open to expose the break plane). Pt deposition protects bond pad corners.- **Stage 4 — Compositional mapping:** EDX line-scan across failure site captures elemental redistribution (e.g., Cu depletion near void, Sn accumulation in adjacent intermetallic). EBSD quantifies grain boundary character (low-angle vs. high-angle boundaries correlate to resistance to crack propagation).**Cost optimization:** Acoustic microscopy is fast (2–5 min/part) and non-destructive; prioritize SAM for lot screening, then selective destructive analysis (FIB/SEM) on confirmed failures.


## Common Failure Signatures and Diagnostic Patterns

**Electromigration (HBM/ESD failure):** FIB reveals void formation at anode (where Cu atoms deplete), filament or whisker formation at cathode. SEM-EBSD shows high-angle grain boundaries aligned perpendicular to current flow (exacerbated migration path). EDX detects Cu₂S corrosion product (sulfur ingress from moisture) at void boundary — diagnostic of combined moisture + current stress.
**Solder joint fatigue (thermal cycling):** SAM shows delamination initiating at die-attach interface; FIB cross-section reveals transgranular cracks in solder bulk. EBSD maps large recrystallized grains (Pb-free solder: Sn grains &gt;50 µm indicate low creep resistance). EDX measures Cu₆Sn₅ intermetallic thickness; &gt;4 µm indicates excessive reflow temperature or long dwell time.
**Wire bond lift-off (corrosion):** SAM shows acoustic mismatch at bond interface. FIB cross-section at bond heel reveals Au-Al intermetallic (AuAl₂) thickness variance; non-uniform thickness indicates underestimated intermetallic growth, reducing bond shear strength (JESD22-B117 pull test baseline &gt;90 g-force for 1 mil wire; corroded bonds fail &lt;50 g).
**Underfill delamination (moisture + thermal shock):** SAM shows dark regions expanding between reflow cycles; FIB cross-section reveals microcracks at underfill–molding interface perpendicular to stress axis. SEM charge contrast imaging (5 kV, unbiased sample) reveals subsurface crack network before catastrophic fracture.


## Key Takeaways

- FIB milling (5–30 keV Ga+/Xe+ ions) enables sub-50 nm cross-sectional analysis; Pt deposition essential to protect bond pad corners from ion implantation damage.
- SEM-EDX/EBSD reveals elemental composition and crystallographic texture; 15–20 keV accelerating voltage optimizes bulk defect penetration (500 nm–2 µm depth).
- Acoustic microscopy (75–230 MHz) non-destructively maps subsurface voids and delaminations with ~6 dB sensitivity threshold per JESD035; use time-of-flight gating to isolate specific layers.
- Sequential workflow (SAM screening → SEM baseline → FIB cross-section → EDX/EBSD mapping) maximizes cost-effectiveness and root-cause confidence in failure investigations.
- Diagnostic signatures: electromigration shows anode void + cathode whisker + Cu₂S corrosion; solder fatigue shows transgranular cracks + recrystallized grains; wire bond corrosion shows non-uniform AuAl₂ intermetallic thickness.

## References

1. **[JEDEC]** JESD035 (Acoustic Microscopy Scan Criteria) — JESD035F: Acoustic microscopy for void detection; defines &gt;6 dB signal loss as delamination threshold, &gt;12 dB as failure-critical.
2. **[JEDEC]** JESD22-B117 (Wire Bond Pull Test) — Pull test baseline &gt;90 g-force for 1 mil Au wire; establishes bond strength acceptance criteria for failure analysis correlation.
3. **[Book]** Microelectronic Failure Analysis: Desk Reference (6th Edition) — ASM International, 2018. Chapters 3–5: FIB cross-sectioning technique, SEM-EDS defect characterization, acoustic microscopy layer mapping.
4. **[Book]** Focused Ion Beam Systems: Fundamentals and Applications — Orloff, J., Czabatur, M., Utlaut, L., Springer, 2003. Section 2.4: Ion milling physics, secondary emission yield, Ga+ implantation depth profile calculations.
5. **[Book]** Scanning Electron Microscopy and X-ray Microanalysis (3rd Edition) — Goldstein, J. et al., Springer, 2003. Chapters 8–9: EDX quantitative analysis, EBSD crystallographic mapping, charge contrast imaging for subsurface void detection.
6. **[Paper]** IEEE Transaction on Semiconductor Manufacturing 35(2): 'Acoustic Microscopy Signal Enhancement for Moisture Detection in Advanced Packages' — 2022. Demonstrates 5% moisture mass fraction detection sensitivity via impedance mismatch; validates SAM for reliability prediction in 3D-IC and chiplet assemblies.

## 🔍 Additional Learning: In-situ TEM-FIB Lamella Preparation for Atomic-Resolution Defect Analysis

Advanced failure labs increasingly prepare electron-transparent TEM lamellae directly from FIB cross-sections (200 keV Xe+ final polish reduces ion damage vs. Ga+). This enables atomic-resolution imaging of void nucleation sites, stacking fault density near intermetallic interfaces, and Cu/Sn interdiffusion profiles — revealing failure mechanisms at sub-nanometer scale. Critical for understanding why certain grain boundaries nucleate cracks under electromigration while others remain stable.
