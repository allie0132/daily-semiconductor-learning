# HBM PDN Testing: Power Delivery, Decap, VDD/VDDQ Margins

*Friday, May 29 2026*

*Module 2.8 — Electrical Testing*

## HBM Power Domain Architecture

HBM stacks use multiple power domains that must be independently controlled and verified during test. The two primary supply rails are **VDD** (core DRAM array and peripheral logic, typically 1.1–1.2 V for HBM2E, 1.05–1.1 V for HBM3) and **VDDQ** (I/O and DQ driver supply, typically 1.2 V for HBM2/3). JEDEC JESD235C Section 4.1 and JESD238A Section 4.1 define the absolute maximum and recommended operating ranges for each rail.
Additional rails include **VDDIO** (command/address bus termination, shared with package interposer), **VPP** (wordline boost, ~2.5 V, used internally and not externally supplied on most HBM generations), and the **VSS/VSSQ** return paths. Each pseudo-channel and bank group presents a dynamic current load; simultaneous switching of all DQ drivers creates the worst-case PDN stress during burst write patterns.
- VDD (HBM2E): 1.1 V nominal, ±50 mV operating range per JESD235C Table 4- VDDQ (HBM2E): 1.2 V nominal, ±60 mV operating range- VDD (HBM3): 1.05 V nominal, ±40 mV (tighter tolerance due to lower margin at 6.4 Gbps)- Transient droop budget: typically ≤ 5% of nominal during worst-case SSO switching

## PDN Impedance and Resonance: Why It Matters for HBM

The power delivery network for an HBM stack on an active silicon interposer (CoWoS, EMIB) presents a complex impedance profile from DC to several GHz. PDN impedance `Z_PDN(f)` must remain below the **target impedance** `Z_target = ΔV / ΔI` across the switching frequency spectrum to prevent noise-induced timing and voltage margin violations.
At low frequencies (10 kHz–10 MHz), bulk capacitors on the package and board dominate. In the 10–200 MHz range, package-level decoupling capacitors (MIM caps in the interposer, MLCC on the substrate) control impedance. Above 200 MHz, on-die decoupling capacitance (MOS caps, dedicated decap cells) becomes the primary energy reservoir. A resonant peak forms where each capacitor tier hands off to the next — this **anti-resonance peak** can exceed Z_target and cause ground bounce or supply droop at the resonant frequency.
- Typical Z_target for HBM2E core: ~3–5 mΩ at 100 MHz (based on 50 A peak current draw, 200 mV budget)- On-die decap density: ~10–20 nF/mm² in modern DRAM dies (MOS capacitors in unused bitcell areas)- CoWoS interposer adds ~100–200 nF distributed MIM capacitance per stack footprint- Anti-resonance between package MIM and die decap typically appears at 500 MHz–1 GHz

## ATE Power Supply Testing: VDD/VDDQ Margin Sweep

On ATE (Advantest T2000, Teradyne UltraFLEX), HBM power supply testing involves both **static characterization** (I-V curves, leakage at Vmin/Vmax) and **dynamic margin sweeps** (operating VDD/VDDQ while running functional patterns). The supply margin test validates that the DUT operates correctly across the JEDEC-specified operating range and characterizes the **guard-band** between first-fail voltage and the spec limit.
A standard VDD margin sweep procedure:
- **Step 1 — Baseline:** Confirm full functional pass at nominal VDD (1.1 V for HBM2E)- **Step 2 — Vmin sweep:** Step VDD down in 10–25 mV increments while running a retention + read/write march pattern; record first-fail voltage (Vmin_FF)- **Step 3 — Vmax sweep:** Step VDD up in 10–25 mV increments; record first-fail (oxide stress, leakage-induced errors)- **Step 4 — Guard-band:** Production bin limit is typically Vmin_spec + 25–50 mV guard-band from the distribution tailCritically, VDDQ must be swept <em>jointly</em> with VDD for I/O path testing — the DQ output swing and ODT impedance both depend on VDDQ, so a VDDQ-only margin test is insufficient for production screening.


## Simultaneous Switching Output (SSO) and PDN Stress Patterns

**SSO testing** stresses the PDN by switching the maximum number of DQ pins simultaneously in the same direction (all-0 → all-1 or all-1 → all-0). For a 1024-bit HBM2E stack, worst-case SSO involves all 1024 DQs switching in a single clock cycle, producing a peak `di/dt` that generates inductive voltage spikes on VDD and ground. The spike amplitude is `V_spike = L_pkg × (ΔI / Δt)` where L_pkg is the package inductance (typically 50–200 pH for TSV-based HBM packages).
ATE SSO test patterns for HBM validation typically include:
- **Checkerboard inversion:** All pseudo-channels write 0x55…55 then 0xAA…AA — maximum simultaneous transitions- **All-same burst:** Write 0xFF…FF → Read → Write 0x00…00 → Read (maximizes charging/discharging current on DQ lines)- **Bank-interleaved stress:** Open all banks, issue back-to-back writes at tCCD_S (short column command distance) — maximum sustained current drawDuring SSO patterns on ATE, the per-pin power supply current monitors (PPMU) are used to measure instantaneous IDD2N, IDD4W, and IDD4R currents. Deviations from JEDEC Table 5 current specifications (JESD235C) indicate PDN or cell array anomalies.


## Decoupling Capacitor Placement and Validation

Decoupling capacitor effectiveness is placement-sensitive: a 100 nF MLCC placed 5 mm from the HBM stack sees ~0.5 nH series inductance at 500 MHz, raising its effective impedance to `Z = 2πfL ≈ 1.6 Ω` — essentially useless for high-frequency decoupling. HBM-in-package solutions (CoWoS, EMIB) partially solve this by embedding **MIM capacitors** in the interposer directly under the HBM stack footprint, with effective inductance below 50 pH.
Validation methods for decap effectiveness include:
- **Vector Network Analyzer (VNA) PDN scan:** Two-port S-parameter measurement of the assembled package; convert to Z-parameters to extract impedance vs. frequency; compare against simulation model- **Time-domain reflectometry (TDR):** Identifies impedance discontinuities in the PDN trace routing; locates open or shorted decap pads- **On-ATE current waveform analysis:** Use PPMU with sub-microsecond sampling to capture transient current profiles during SSO patterns; correlate with supply noise measured at DUT socket (if equipped with in-socket sense lines)- **Functional voltage noise injection:** Inject calibrated AC noise onto VDD at known frequencies and amplitudes; measure BER degradation — the frequency where BER increases identifies PDN resonanceA well-characterized PDN for HBM2E should show `|Z_PDN| ≤ 5 mΩ` from DC to at least 500 MHz. Values above 10 mΩ in the 50–500 MHz band correlate with functional failures under worst-case SSO patterns in system validation.


## Key Takeaways

- HBM PDN requires sub-5 mΩ target impedance from DC to 500 MHz; anti-resonance peaks between package and die decap tiers are the primary failure mode and must be damped through careful capacitor selection and placement.
- ATE VDD/VDDQ margin sweeps must step supply in 10–25 mV increments while running SSO-stress functional patterns — static leakage tests alone will miss dynamic supply-induced failures that only appear under high di/dt.
- Simultaneous Switching Output (SSO) patterns with all 1024 DQ bits transitioning in one clock cycle are the worst-case PDN stress; IDD4W/IDD4R measurements during these patterns are the primary figure-of-merit for PDN health on ATE.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — Section 4.1 (Absolute Maximum Ratings), Table 4 (DC Operating Conditions), Table 5 (IDD Specifications) — VDD/VDDQ ranges and current specs
2. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM — JESD238A — Section 4.1, Table 6 — HBM3 VDD/VDDQ operating conditions at 1.05 V / 1.2 V
3. **[Paper]** Power Delivery Network Design and Simulation for High-Performance Memory Interfaces — DesignCon 2019, Müller & Park — PDN impedance methodology for CoWoS HBM2 packages; target impedance derivation and anti-resonance mitigation
4. **[Book]** Signal and Power Integrity — Simplified — Eric Bogatin, Prentice Hall, 3rd ed. 2018; Chapters 11–13 cover target impedance, decoupling capacitor placement, and PDN resonance
5. **[Paper]** Simultaneous Switching Noise Analysis for HBM2 in 2.5D IC Packages — IEEE Transactions on Electromagnetic Compatibility, Vol. 60, 2018 — SSO noise characterization for HBM2 CoWoS packages; validated against ATE current measurements
6. **[IEEE]** A 1.2V 16Gb 3.2Gbps/pin 256GB/s HBM2E DRAM with PDN Noise Suppression — ISSCC 2020, SK Hynix — on-die decap architecture, PDN noise suppression techniques in HBM2E

## Additional Learning: CATTRIP: HBM's Emergency Thermal/Power Shutdown Signal

HBM2 and later generations include a <strong>CATTRIP</strong> (Catastrophic Trip) signal that asserts when the on-die temperature sensor exceeds a programmable threshold (default ~105°C per JESD235C MRS register settings). When CATTRIP asserts, the HBM enters a low-power emergency state — all DQ outputs tri-state, refresh continues at reduced rate, and VDD current drops to the IDD2P (power-down) level. From a PDN test perspective, the CATTRIP transition itself creates a sharp current step (full active → power-down in ~50 ns) that can induce a large inductive overshoot on VDD if the PDN bandwidth is insufficient — paradoxically, a poorly designed PDN can cause a voltage spike during thermal shutdown that damages the very device it is protecting. ATE programs should exercise CATTRIP deliberately by forcing the temperature sensor threshold via MRS writes and verifying clean current collapse without supply overshoot.
