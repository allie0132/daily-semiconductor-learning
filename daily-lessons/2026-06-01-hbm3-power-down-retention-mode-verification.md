# HBM3 Power-Down & Retention Mode Verification

*Monday, Jun 01 2026*

*Module 3.2 — Protocol & Compliance*

## HBM3 Low-Power State Architecture & Compliance Boundaries

HBM3 introduces two distinct low-power operating modes beyond traditional dormant states: **Self-Refresh (SR)** and **Deep Power-Down (DPD)**. Unlike HBM2E, HBM3 mandates stricter retention voltage windows and tighter leakage specifications to support extended idle periods in AI/ML inference pipelines.
- **Self-Refresh Mode (SR):** Memory controller remains active; DRAM array is isolated via internal switches. Supply voltage constrained to V<sub>DDQ_SR</sub> range (typically 0.45V–0.65V nominal). Refresh cycles occur autonomously via on-die timer.- **Deep Power-Down (DPD):** Complete shutdown except retention logic. V<sub>DDQ_DPD</sub> window narrower (0.30V–0.50V). All sense amplifiers powered off; capacitive storage only. Exit latency ≥ 200 µs typical.- **Retention Voltage Windows:** JEDEC JESD238 defines per-rank V<sub>DQ</sub> and V<sub>DD</sub> retention windows. Device must maintain data integrity across process corners, temperature extremes (0°C–85°C), and lifetime stress.Critical compliance point: **data retention margin** must be verified across voltage sweep from V<sub>min</sub>–200mV to V<sub>nom</sub>+300mV to expose corner-case leakage and bitline capacitance weaknesses.


## ATE Instrumentation & Measurement Protocol for Leakage Qualification

Production HBM3 verification requires precision power delivery and ultra-low-noise sensing. Typical ATE setup uses **dedicated DC power modules** with &lt;100 ppm load-line regulation and **picoammeter-grade ammeter channels** for current measurement.
- **Current Measurement Instrumentation:** V<sub>DD</sub> and V<sub>DDQ</sub> leakage current measured separately. Modern ATE (e.g., Teradyne Magnum, LTX Credence Raptor) provides ≤1 µA resolution. Measurement period ≥ 100 ms post-mode entry to capture steady-state leakage after transients settle.- **Voltage Domain Isolation:** Separate SMU channels for V<sub>DD</sub> (core array logic) and V<sub>DDQ</sub> (I/O and retention logic). Cross-coupling between domains must be &lt; 2% to isolate leakage contributions.- **Temperature Profiling:** Compliance requires leakage spec verification at T<sub>min</sub> (0°C), T<sub>nom</sub> (25°C), and T<sub>max</sub> (85°C). Use ATE thermal chamber or test head with embedded TJ monitor. Exponential leakage temperature coefficient (~2–3× per 10°C) demands tight control.- **Mode Entry Sequence Timing:** DPD entry via MRW (Mode Register Write) command; measure current rise time and settling tolerance. Settling time typically 10–50 µs. Any current spike &gt; 3× steady-state indicates incomplete power gating or latch-up risk.**Key protocol:** Issue DPD command, wait 50 µs, then start 100 ms measurement window. Log min/max/mean I<sub>DD</sub> and I<sub>DDQ</sub>. Tolerance: ±10–15% from datasheet spec (typical ±8 µA at nominal voltage).


## Data Retention Verification & Bitline Capacitance Testing

Post-retention test requires functional verification to confirm no silent bit corruption during low-power idle. JEDEC JESD238 mandates retention patterns and timing.
- **Pattern Generation & Timing:** Fill entire array with checkerboard (0xAAAA/0x5555) or PRBS pattern. Enter SR or DPD. Retain at minimum V<sub>DD</sub> for duration T<sub>ret</sub> (typically 64 ms for SR, 1 s for DPD in accelerated test). Exit mode and read-compare.- **Voltage Sweep Strategy:** Perform retention test across V<sub>DD</sub> sweep: nominal, −200 mV, −100 mV to identify bitline leakage failure threshold. Bitcell capacitance (C<sub>cell</sub> ≈ 30–50 fF in 12nm processes) combined with off-state transistor leakage determines maximum retention time at minimum voltage.- **Temperature Margin Testing:** Repeat patterns at T<sub>min</sub>, T<sub>25</sub>, T<sub>max</sub>. Leakage doubles ~every 10°C; verify spec margin at high temperature (85°C) is &gt; 2× worst-case production leakage to ensure field reliability.- **Silent Bit Detection:** Use BIST (Built-In Self-Test) or ATE compare logic with per-bit logging. Flag any single-bit or multi-bit failures. Modern ATE generates failure maps; correlate spatial patterns with known process defects or ESD damage.Retention margin is defined as: **V<sub>margin</sub> = V<sub>fail</sub> − V<sub>min_spec</sub>**. Target margin ≥ 200 mV to account for aging, OCV, and temperature drift over device lifetime.


## Mode Transition Timing & State Machine Compliance

HBM3 defines strict timing windows for entry/exit from low-power states. Violations cause data corruption or incorrect resume-from-retention behavior.
- **Entry Timing (Active → SR/DPD):** Mode Register Write (MRW) command initiates transition. Internal state machine must complete clock shutdown and power-gating within T<sub>entry_max</sub> (typically 10–50 tCK clock cycles, where tCK is memory clock period). Measure via logic analyzer on test mode signals or ATE pattern timing.- **Exit Timing (SR/DPD → Active):** Exit command (e.g., NOP or CAS command) triggers wake-up. Clock and core voltages restore within T<sub>exit_max</sub> (50–200 µs typical). Data bus becomes valid after T<sub>exit_valid</sub>. **Critical spec:** Verify first read command after exit does NOT return stale data.- **Clock Gating Verification:** Use internal test mode or scan chain to verify clock dividers are gated during retention. Unintended clock activity increases leakage by 10–100× and invalidates retention margin. Measure via power supply transient injection: if clock is active, supply noise couples into on-die V<sub>DD</sub> sense points.- **Back-to-Back Mode Transitions:** Production test must verify rapid SR ↔ Active transitions (micro-sleep scenario). Issue 1000+ back-to-back MRW commands with 1 µs dwell in SR. Monitor for state machine latchup, incomplete power restoration, or timing race conditions.**ATE Implementation:** Use **timing parametric test** with precision delay generators. Capture time from MRW issuance to current drop; tolerance typically ±20% of spec mean.


## Practical Production Screening & Reliability Acceleration

Field failures in retention mode are costly (silent data loss in inference models). Production screening must be aggressive yet manufacturable.
- **Accelerated Retention Testing:** Spec retention time is 64 ms (SR) or 1 s (DPD) at nominal voltage. Production test uses **voltage-accelerated** method: reduce V<sub>DD</sub> by −100 to −200 mV, measure leakage current. Extrapolate time-to-failure via Weibull model. Devices failing early (within −150 mV) are screened out; typical acceptable criteria: &lt; 1 ppm defect level per 1M parts.- **Temperature Stress Combination:** Combine high-temperature (85°C) with low-voltage (−200 mV) to achieve ~10× acceleration factor. Run retention test for 10 s instead of 1 s. Sensitivity: exponential leakage scaling (~2.5× per 10°C and ~10× per 200 mV) gives ~25× total acceleration.- **Defect Binning:** Separate failing devices into **leakage fail** (I<sub>DD</sub> &gt; spec) vs. **retention fail** (bit errors post-retention). Leakage fail → likely gate oxide defect or subthreshold swing degradation; retention fail → likely bitline capacitance loss or refresh timing bug.- **Datalog & Analytics:** Log per-die I<sub>DD</sub>, I<sub>DDQ</sub>, voltage sweep curve, and bit failure map. Use statistical process control (SPC) to track mean leakage trending. Early warning of process shift (e.g., +10% leakage across lot) enables corrective action before yield loss.**Industry Practice:** Leading foundries (TSMC N5/N3 HBM3) require &lt; 5 µA V<sub>DD</sub> leakage and &lt; 1 µA V<sub>DDQ</sub> at nominal voltage for mass production sign-off.


## Key Takeaways

- HBM3 defines two retention modes (SR and DPD) with distinct V<sub>DD</sub> windows and leakage specs; compliance requires separate measurement of V<sub>DD</sub> and V<sub>DDQ</sub> current with picoammeter-grade ATE resolution.
- Data retention margin must be verified across voltage sweep (−200 mV to +300 mV) and full temperature range (0–85°C) to expose process-corner leakage weaknesses; target margin ≥ 200 mV from spec minimum.
- Mode transition timing violations (entry/exit) cause silent data corruption; back-to-back transition stress testing and state machine scan verification are mandatory for production screening.
- Voltage-accelerated and temperature-combined retention testing (−200 mV + 85°C) achieves ~25× acceleration; defect binning (leakage vs. retention fail) enables root-cause analysis and process improvement.

## References

1. **[JEDEC]** JEDEC JESD238-3: High Bandwidth Memory (HBM3) DRAM — Section 4.3 (Low-Power Modes), Table 6 (Retention Voltage Windows), Section 5.2 (Mode Entry/Exit Timing)
2. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM2E) DRAM — Section 3.4 (Power Management) — predecessor standard for context on evolution to HBM3 stricter specs
3. **[Datasheet]** Teradyne Magnum™ Family ATE Platform — Power Measurement Module Specifications — DC Power SMU channel ≤1 µA resolution, ±100 ppm load-line regulation; used for production HBM3 characterization
4. **[Paper]** Keysight 'Power Supply Noise and Data Retention in Advanced DRAM' — IEEE Transactions on Device and Materials Reliability, 2022 — bitline capacitance modeling and leakage failure mechanisms in sub-5nm nodes
5. **[Web]** Samsung 'HBM3 Memory Reliability: Retention Mode Acceleration & Screening Strategy' — Samsung Semiconductor White Paper, 2023 — production methodology for voltage/temperature-accelerated retention testing and defect binning
6. **[JEDEC]** JEDEC JC-45.3 Memory Test Methods Committee — JESD204G (Signal Integrity) and JESD79-4 (DDR4 Specification) foundational for low-power mode command sequencing and timing margins

## 🔍 Additional Learning: Bitline Capacitance & Leakage Scaling in 5nm HBM3 Nodes

Modern HBM3 at 5nm and below exhibits exponential leakage scaling due to reduced V<sub>th</sub> and increased subthreshold swing variability. Bitline capacitance shrinks to 30–50 fF per cell; combined with 10–100 pA per-transistor off-state current, retention time at minimum voltage (−200 mV) can drop to &lt; 100 ms in worst-case process corners. Advanced ATE must employ in-situ leakage binning during voltage sweep: measure dI<sub>DD</sub>/dV slope; steep slope (&gt; 50 µA/V) flags bitcell degradation and predicts field retention failures. Correlate Weibull shape parameters from acceleration testing to predict failure rates; shape factor &lt; 1.5 indicates random defects rather than wearout, guiding screening strategy.
