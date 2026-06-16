# KGD Testing: Electrical & Reliability Screening

*Tuesday, Jun 16 2026*

*Module 5.4 — ATE & Production*

## KGD Definition & Test Strategy Framework

**Known Good Die (KGD)** is a die that has passed comprehensive electrical and reliability qualification before packaging, eliminating defects at wafer level and reducing assembly yield loss. Unlike standard wafer-level testing (WLT), KGD requires **functional pattern coverage >95%**, **parametric screening**, and **reliability stress qualification**.
The KGD test strategy consists of three pillars:
- **Electrical screening:** DC parametrics (Vth, leakage, power supply current), functional vectors (>90% ATPG coverage), and AC timing margins at process corners- **Reliability screening:** Burn-in (48–168 hrs at elevated T/V), HTOL, ESD robustness (HBM per JESD22-A114), and thermal cycling to precipitate latent defects- **Traceability & data binning:** Lot-level mapping, defect density trending, and wafer-level root cause correlation

## Electrical Screening: Parametric & Functional Protocols

**Parametric Testing (DC characterization):**
- **Supply current (IDD):** Measure static and dynamic leakage at VDD, GND, and intermediate rails across temperature (-40°C to 125°C). Flag `IDD > 3σ median` as potential oxide defects or latch-up risk- **Threshold voltage (Vth):** Extract via IDVG ramp on dedicated test structures; correlate with poly-silicon depletion and channel-length modulation to predict AC timing closure- **Leakage current (Ileak):** Measure IOFF at nominal and worst-case bias; use `Vth screening margin ±50 mV` to catch early-failure modes (gate-induced drain leakage, GIDL)**Functional Testing (AC vector screening):**
- Apply **ATPG-generated vectors** with >90% stuck-at coverage; add at-speed patterns at `fMAX – 10%` guard band to catch delay defects- Measure **timing margin:** Use embedded delay-line circuits or ring oscillators to verify setup/hold slack and propagation delay across `3σ process variation`- Stress with **multiple VDD corners** (VDD_nom ± 10%) and temperature sweep to identify voltage/thermal sensitivity

## Reliability Screening: Burn-In, HTOL & ESD Protocols

**Burn-In (BI) – Defect Precipitation:**
- Conduct **Dynamic Burn-In (DBI)** at 125°C, VDD = 1.2V nominal + 5% (stress corner), with **80–100% toggle rate** on core logic for 48–168 hours- Monitor **Idq growth** every 4–8 hours; reject dies with >3× baseline leakage or sudden jumps (signature of latent short or wearout initiation)- Combine with **Temperature Cycling (TC)** sub-profile: -40°C to +125°C, 15 min dwell, 10–20 cycles to stress bond wires, solder joints, and metallization thermal mismatch**High-Temperature Operating Life (HTOL) – Wearout Screening:**
- Run **1000 hours at 125°C, 1.3V (VDD overstress)** on sample population (typically 30–50 dies per lot) to accelerate time-dependent dielectric breakdown (TDDB) and electromigration (EM)- Record **leakage and timing drift** at T=0h, 168h, 500h, 1000h; fit to Arrhenius or power law to project field MTBF- Acceptance criterion: **Zero parametric failures** and `timing shift < 5% nominal`**HBM ESD Stress (JESD22-A114):**
- Apply ±2 kV HBM discharge to all I/O pads; verify no latch-up and leakage increase `< 10% post-stress`- Link ESD results to on-die ESD clamp sizing and substrate biasing; use **transmission line pulse (TLP)** characterization to confirm second-breakdown immunity

## ATE Platform Implementation & Data Management

**ATE Configuration for KGD:**
- Deploy **parallel test stations** (e.g., Teradyne UltraFLEX, LTX-Credence Xtra) with **SMU (Source Measurement Unit)** channels for accurate low-leakage measurement (`pA-level resolution`) and **real-time temperature control** (±0.5°C stability in thermal chamber)- Integrate **wafer-level probe cards** with `fine-pitch contacts (20–30 μm)` and **impedance-matched interconnect** to minimize reflections at multi-GHz test frequencies- Implement **DC calibration routines** every shift (source offset `< ±10 mV`, measure offset `< ±5 mV`) and **AC timing calibration** using on-board oscillators (phase-locked to reference clock)**Data Binning & Yield Analytics:**
- Bin dies into **Grade A (KGD prime)**, **Grade B (marginal, for cost-down)**, and **Reject** based on multi-dimensional yield limits: IDD, Vth, Ileak, fMAX margin, and ESD post-stress leakage- Create **wafer heat maps** correlating defect locations with metallization layout, device density, and implant regions to feed back design-for-test (DFT) and process improvement- Track **lot DPPM (defects per million)** and **cumulative failure curves** during 12-month field deployment to validate screening effectiveness

## Common Pitfalls & Best Practices

**Pitfalls:**
- **Over-aggressive parametric limits:** Setting Ileak spec too tight (e.g., `< 1 nA @ 125°C`) can reject good dies due to temperature sensor offset or SMU calibration drift; use `3σ + guard band approach` instead- **Insufficient functional coverage:** Relying on DC-only screening misses logic path delay defects; enforce **≥95% ATPG stuck-at + >80% transition coverage**- **Burn-in recipe mismatch:** Using static BI instead of dynamic BI reduces defect precipitation by ~40%; **toggle rate must be >75%** to stress interconnect RC delays and gate oxide- **ESD timing artifacts:** Running HBM stress immediately before parametric re-test can give false leakage blooming; observe **24-hour recovery window** before re-characterization**Best Practices:**
- Correlate **wafer-level KGD results with packaged device field data** on a quarterly basis; flag any systematic KGD pass that later fails in reliability to trigger ATE recipe audit- Implement **inline SPC (Statistical Process Control)** on key parameters (Ileak trend, Vth distribution); set **control limits at ±2σ** to trigger wafer-level process investigation before yield collapse- Validate **test program every 50 wafers** using golden reference dies to catch SMU drift, probe card wear, or thermal lag

## Key Takeaways

- KGD testing combines electrical screening (parametric + functional, >90% coverage) and reliability stress (48–168 hr BI, HTOL, HBM ESD) to precipitate latent defects before packaging.
- Parametric screening must include IDD (static/dynamic), Vth extraction, and Ileak trending; use 3σ + guard band binning to balance yield loss vs. field reliability risk.
- Burn-in effectiveness depends on dynamic toggle (>75% switching activity) and temperature cycling; static BI misses interconnect RC defects. Monitor Idq growth for signature latent shorts.
- ATE platform requires SMU-based measurement (<pA resolution), wafer-level probe cards (fine-pitch, impedance-matched), and rigorous DC/AC calibration every shift for reproducibility.
- Correlate KGD data with packaged device field MTBF and use wafer heat maps to drive DFT and process improvement; quarterly validation closes the loop between wafer test and customer reliability.

## References

1. **[JEDEC]** JESD22-A114: HBM ESD Stress Test — Standard test method for HBM ESD protection validation; 2 kV typical for advanced nodes
2. **[JEDEC]** JESD47: Methodology for Impact of Residual Moisture on Microelectronics — Guidance on thermal cycle stress correlation with packaging; relevant for post-BI reliability assessment
3. **[JEDEC]** JESD22-A108: High-Temperature Operating Life (HTOL) Test Method — HTOL protocol definition; 1000 h @ 125°C, 1.3V standard for advanced CMOS wearout screening
4. **[IEEE]** IEEE 1149.1: JTAG Boundary Scan & Test Data Register (TDR) — On-chip test access for parametric monitoring and voltage/temperature stress observation during ATE execution
5. **[Web]** Sematech KGD Guidelines for 0.18 μm & Below — Historical but foundational reference on KGD binning strategy and defect density correlation; still used for process node scaling decisions
6. **[Datasheet]** Teradyne UltraFLEX DC/AC Test Module Application Notes — Real-world ATE configuration for <pA leakage measurement and multi-site parallel testing at wafer level

## 🔍 Additional Learning: Idq Signature Analysis: Latent Short Detection via Dynamic Profiling

Beyond simple pass/fail Idq thresholds, advanced KGD labs now employ <strong>Idq fingerprinting</strong>—plotting leakage current vs. test cycle number during BI to identify characteristic signatures of nascent defects. A sudden 2–3× Idq jump followed by stabilization signals a resistive short that will likely fail in first 10K hours of field use; such 'soft short' candidates are segregated into lower grades even if final Idq is within spec. This requires real-time SMU logging every 2–4 hours during 168-hour BI runs, feeding into machine-learning classifiers trained on historical field failure correlations—a technique now becoming industry standard for 5 nm and below node KGD screening.
