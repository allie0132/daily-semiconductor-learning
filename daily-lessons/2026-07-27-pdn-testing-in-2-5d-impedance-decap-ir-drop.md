# PDN Testing in 2.5D: Impedance, Decap & IR Drop

*Monday, Jul 27 2026*

*Module 12.4 — Heterogeneous Integration & Advanced Packaging Test*

## Why PDN Testing in 2.5D Is Uniquely Challenging

In conventional monolithic packages, the power delivery network is relatively straightforward: PCB planes, package capacitors, and on-die decoupling work in a well-understood hierarchy. In 2.5D heterogeneous integration—where a GPU or CPU die sits alongside one or more HBM stacks on a silicon or organic interposer—the PDN topology becomes multi-domain and extremely sensitive.
Key challenges include:
- **Interposer transmission line impedance:** The redistribution layers (RDL) on a silicon interposer have parasitic inductance and resistance that must be characterized at operating frequencies (typically 100 MHz–5 GHz for noise analysis).- **Multiple voltage domains crossing the interposer:** HBM operates at VDDQ (1.2 V for HBM2E/HBM3), VDD core, and VDDC, each with independent PDN paths requiring separate characterization.- **Micro-bump and TSV parasitics:** Each HBM PHY interface traverses C4 bumps, interposer RDL, and micro-bumps, introducing distributed L and R that shift the PDN anti-resonance frequency.- **Thermal coupling:** As HBM and GPU die temperatures rise under load, IR-drop increases due to copper resistance increases (~0.39%/°C), making static IR-drop measurements at room temperature insufficient.

## PDN Impedance Measurement with VNA

The standard method for PDN characterization is 2-port vector network analyzer (VNA) measurement using the S-parameter to Z-parameter conversion. The target PDN impedance `Z_target = ΔV_ripple / I_transient`.
For HBM3 with a 1.2 V VDDQ rail and a 5% ripple spec (60 mV), driving 10 A transients, the target is `Z_target = 60 mV / 10 A = 6 mΩ`.
Measurement procedure:
- Use a Keysight E5063A or similar 2-port VNA with 50 Ω calibration (SOLT or LRRM).- Apply a probe fixture or soldered SMA launchers directly on the interposer power plane or test pads near the HBM PHY power pins.- Convert S11 or differential S-parameters to impedance: `Z = Z0 × (1 + S11) / (1 - S11)`.- Sweep from 1 MHz to 3 GHz; plot on a log-log scale and identify resonance peaks (where PDN impedance exceeds Z_target).- Anti-resonance peaks appear at frequencies where package inductance and interposer decap capacitance form an LC tank—typically 50–500 MHz range.On-wafer or KGD (Known Good Die) PDN tests prior to 2.5D assembly use a probe station with calibrated RF probes to measure the bare interposer PDN before die attachment, providing a baseline for post-assembly delta analysis.


## Decap Tuning on the Interposer

Decoupling capacitors on a silicon interposer serve to suppress mid-frequency (10 MHz–500 MHz) PDN impedance spikes. Unlike PCB-level decaps, interposer decaps are passive IPD (Integrated Passive Devices) or discrete 0402/0201 capacitors mounted on the interposer surface.
Placement strategy:
- **Near HBM PHY power pins:** Place decaps within 200–500 µm of the HBM micro-bump field to minimize loop inductance. Inductance of a 500 µm trace at typical widths contributes ~50–150 pH, shifting resonance above 1 GHz.- **On-interposer IPD capacitors:** Integrated trench or MIM capacitors in the silicon interposer provide very low ESL (~10 pH) and capacitances from 1–100 nF. These are characterized by the foundry but must be verified post-dicing.- **Tuning iteration:** After first-pass VNA measurement, simulate with SPICE PDN models (e.g., Sigrity PowerDC or Ansys RedHawk-SC). Add or remove decap values in SPICE to flatten the impedance profile, then verify on the next hardware spin.ESR (equivalent series resistance) tuning is also critical: a decap with ESR near Z_target provides active damping of the anti-resonance peak. Too low ESR leaves a sharp resonance; too high ESR defeats the capacitor's charge delivery role. Target `ESR ≈ Z_target / 2` for a critically damped response.


## IR Drop Measurement Methodology

IR drop (ΔV = I × R_pdn) across the HBM PHY power rails is measured both statically and dynamically. Static IR drop reflects the DC resistance of power traces and vias; dynamic IR drop adds inductive effects during fast current transients (e.g., DRAM array activate commands with slew rates >1 A/ns).
**Static IR drop** is measured using:
- 4-wire Kelvin measurement from the VRM (voltage regulator module) output to test points adjacent to HBM VDDQ balls, using a Keithley 2602B or similar SMU.- Force known DC currents representing typical HBM read/write power (e.g., 2–5 A per HBM stack) and measure voltage differential. Compare against PDN simulation output from tools such as Ansys RedHawk-SC or Cadence Voltus.**Dynamic IR drop** is measured using:
- A high-bandwidth oscilloscope (Tektronix DPO70000 or Keysight UXR series, ≥20 GHz BW) with a differential active probe (e.g., Tektronix P7520A) placed on VDDQ test pads near HBM power pins.- Stimulus: run JEDEC JESD235C compliance traffic patterns (e.g., WCK-synchronized row activates across all banks) to generate worst-case simultaneous switching current.- Capture voltage waveforms; peak droop amplitude should remain within JEDEC-defined VDDQ AC tolerance bands (±80 mV for HBM3 VDDQ = 1.2 V).Thermal derating: perform IR drop sweeps at elevated junction temperature (90–105 °C using a thermal chuck or forced-air heating) to capture the worst-case condition. Add a 15–20% margin for production guard-band.


## Test Automation and Pass/Fail Criteria

PDN testing in 2.5D production environments requires automation at ATE to scale across high-volume packages. Typical integration approaches:
- **Impedance spot checks at ATE:** Rather than full VNA sweeps, production tests inject a known AC current stimulus at a critical frequency (e.g., 100 MHz, near the expected anti-resonance) and measure the AC voltage response. The ratio gives a single-frequency impedance that can be binned against Z_target.- **Parametric IR drop test:** ATE forces a programmable DC current through the HBM VDDQ plane (using a high-current PPMU or an external active load) and measures the resulting voltage sag. Fail limits are typically ≤50 mV drop from VRM to HBM PHY balls under full-load current conditions.- **Functional stress correlation:** Any package that passes structural PDN limits is further stressed with JEDEC Maximum Power Traffic (worst-case simultaneous switching) to ensure no latent failures from borderline PDN at speed.Pass/fail criteria summary:
- PDN impedance at 100 MHz: ≤ Z_target (e.g., ≤6 mΩ for HBM3 VDDQ 10A rail)- Static IR drop: ≤ 40 mV from VRM to HBM VDDQ balls at max operating current- Dynamic VDDQ droop: ≤ 80 mV peak during worst-case switching transients- At 105 °C: all limits derated by +15% to account for temperature coefficient of resistance

## Key Takeaways

- PDN impedance in 2.5D packages must be characterized with VNA from 1 MHz to 3 GHz; anti-resonance peaks above Z_target cause VDDQ droop failures under HBM switching transients.
- Interposer decap placement within 500 µm of HBM PHY micro-bumps is critical—loop inductance from longer traces shifts anti-resonance into the HBM3 WCK operating window (1–2 GHz).
- IR drop must be validated both statically (Kelvin 4-wire at DC) and dynamically (oscilloscope differential probe during JEDEC worst-case traffic) with thermal derating at 105 °C junction temperature.
- Production ATE PDN tests use spot-frequency impedance injection and parametric IR drop (PPMU or active load) rather than full VNA sweeps, with pass limits traceable to JESD235C VDDQ AC tolerance bands.

## References

1. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM Standard — JESD235C §6.4–6.6: VDDQ DC and AC specifications, VDDQ ripple limits, and PHY power delivery requirements
2. **[Datasheet]** Ansys RedHawk-SC — Power Integrity Analysis for Advanced Packaging — Ansys RedHawk-SC product documentation, 2024; covers 2.5D/3D-IC PDN simulation methodology and IR-drop flow
3. **[Paper]** S. Sandhu et al., 'PDN Design and Validation for HBM2 in a High-Performance GPU Package' — Hot Chips 2019; presents interposer PDN impedance budgeting, decap co-optimization, and silicon measurement results
4. **[Web]** Keysight E5063A ENA Vector Network Analyzer — Application Note: PDN Impedance Measurements — Keysight application note 'Power Integrity Measurements Using a Vector Network Analyzer', Part No. 5992-2850EN
5. **[IEEE]** Kim et al., 'On-Package Power Delivery Network Analysis for 2.5D IC' — IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 9, No. 5, May 2019, pp. 893–902, DOI: 10.1109/TCPMT.2019.2898012
6. **[Datasheet]** Tektronix P7520A TriMode Differential Probe User Manual — Tektronix P7520A, 20 GHz differential active probe; recommended for HBM VDDQ dynamic IR drop waveform capture on 2.5D packages

## Additional Learning: On-Die PDN Sensors for Real-Time IR Drop Monitoring

Modern HBM-connected SoCs increasingly embed on-die voltage droop sensors (also called eSensor or DVFS monitors) that sample VDDQ at the PHY boundary with sub-nanosecond resolution. These sensors—implemented as ring-oscillator-based voltage monitors or analog bandgap references—report droop events to the power management unit, enabling adaptive clock throttling before VDDQ falls below the minimum operating point. In 2.5D packages, these sensors augment external ATE measurements by providing in-situ PDN health visibility during production test and field operation, and their readout via scan or JTAG is increasingly included in JEDEC HBM3E compliance test plans.
