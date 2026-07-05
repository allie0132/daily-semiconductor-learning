# HBM Power Integrity at System Level

*Sunday, Jul 05 2026*

*Module 8.6 — System Integration & Advanced Verification*

## HBM PDN Architecture and Noise Budget

High Bandwidth Memory imposes stringent power delivery requirements because its PHY and DRAM core draw large instantaneous currents during burst read/write operations. The package-level Power Delivery Network (PDN) must maintain the HBM supply rails — typically `VDD` (1.2 V), `VDDQ` (1.2 V), and `VDDPLL` — within ±3% of nominal under worst-case di/dt events.
The noise budget is partitioned across three domains: **silicon IR drop** (on-die resistance from bump to power grid), **package impedance** (interposer and package substrate RLC parasitics), and **board PDN** (VRM response and bulk capacitance). JEDEC JESD235C §6.6 defines the maximum allowed `VDDQ` droop of 60 mV peak-to-peak referenced at the HBM micro-bumps. Exceeding this budget causes read eye closure and PHY link degradation.
- HBM2E typical peak current: ~6 A per stack at full BW utilization- HBM3 increases to ~12 A per stack due to higher bus width and speed- Voltage droop during simultaneous switching: must model all stacks on a common interposer rail

## Package PDN Simulation Methodology

PDN simulation for HBM packages requires a hierarchical S-parameter or SPICE extraction flow. The silicon interposer (e.g., TSMC CoWoS) is modeled as a distributed RLC network extracted from the power/ground plane geometry using 2D electromagnetic tools such as Sigrity PowerSI, Cadence Clarity, or ANSYS SIwave.
The simulation flow proceeds in three stages:
- **Plane extraction:** Import interposer GDS layers; extract effective impedance matrix `Z(f)` from HBM bump array to GPU/CPU bump array, sweeping from 1 MHz to 10 GHz- **Current stimulus:** Apply time-domain current waveforms derived from HBM traffic models — typically derived from JEDEC JESD235C traffic patterns or vendor-supplied IOFF/ION profiles- **Co-simulation:** Combine interposer model with package substrate EM model and board stackup. IBIS-AMI or behavioral current source models represent each HBM PHY lane switching simultaneouslyKey metric: the impedance profile `|Z(f)|` must remain below the target impedance `Z_target = V_droop / I_peak` across the frequency range where the HBM current spectrum has significant energy (typically DC to 500 MHz for the fundamental switching events).


## Decoupling Capacitor Placement Strategy

Decoupling capacitors (decaps) suppress mid-frequency impedance peaks that arise from the interposer and substrate inductance resonating with bulk capacitance. In 2.5D CoWoS designs, three categories of decaps are placed:
- **On-die decap:** Embedded in the HBM DRAM die itself; provides high-frequency filtering above 100 MHz. HBM3 stacks include up to 40 nF of on-die decap per stack per JESD238A §5.3.- **Interposer MIM/trench decap:** Placed on the silicon interposer surface between HBM bumps and host die. Typical value 1–10 nF per cell, self-resonant frequency 200–800 MHz. Must model bump ESL (~50 pH per bump) to determine effective frequency range.- **Package substrate SMT decap:** 0402 or 0201 MLCC capacitors on the substrate surface beneath the package. Values of 100 nF to 1 µF target 1–50 MHz impedance control. Placement must minimize via inductance — keep capacitors within 1 mm of power vias.Optimization workflow: use a closed-loop SPICE simulation with the PDN model; sweep decap count and placement until `|Z(f)|` stays below `Z_target` across the full spectrum. Tools: Cadence Sigrity, ANSYS SIwave with decap optimization, or custom MATLAB scripts sweeping decap arrays.


## Silicon Validation of HBM PDN

Post-silicon validation of HBM PDN is performed using a combination of on-die voltage monitors, external scope measurements, and ATE-based power integrity tests.
**On-die voltage monitors (ODVS):** Modern HBM PHY controllers and host SoCs include built-in voltage sensors on `VDD` and `VDDQ` rails that can log minimum/maximum voltage samples during stress patterns. Access is via JTAG or vendor-specific registers. Cadence Cerebrus or Synopsys PrimeWave flows correlate ODVS readings with simulation predictions.
**ATE-based PI validation:** On testers such as Advantest T2000 or Teradyne UltraFLEX, HBM PDN is stressed by running simultaneous maximum-bandwidth traffic patterns across all HBM stacks. The test sequence:
- Configure HBM to PRBS23 write-all pattern on all 8 pseudo-channels simultaneously (JESD235C PRBS stimulus)- Monitor VDDQ via the ODVS readback register — typically mapped at `0x7F00` in the HBM Mode Register set or via APB interface- Check VDDQ stays within ±3% of nominal across 1M cycle burst windows- Repeat at junction temperature Tj = 85°C and 105°C to capture thermal-induced resistance changes**Scope probing:** For lab debug, use a differential probe (Tektronix TIVP series, 200 MHz BW) on exposed interposer test pads or solder bumps with a 50 Ω shunt resistor to capture droop waveforms. Correlate with simulated PDN response to validate model accuracy.


## Common Failure Modes and Debug Flow

PDN-related HBM failures manifest as intermittent read CRC errors, PHY link training failures at high data rates, or excessive BIST error rates under simultaneous stress. The debug flow follows:
- **Isolate stack:** Disable all HBM stacks except one; if errors disappear, the issue is supply rail coupling between stacks on a shared interposer rail — a common mode injection problem requiring improved interposer plane isolation or additional decap- **Sweep VDDQ margin:** Use ATE PPMU or an on-board LDO trim to step VDDQ from nominal +5% down to −5%. Plot BER vs. VDDQ; if BER degrades sharply below nominal, PDN droop is marginal — cross-reference with ODVS minimum voltage logs- **Check decap ESL:** A sharp impedance peak in the 50–200 MHz range (visible on VNA measurement of the PDN) indicates decap self-resonance is too low. Swap to lower-inductance 0201 or embedded IPD capacitors- **Thermal derating:** Ceramic MLCC capacitance derates with DC bias and temperature. At 1.2 V bias, a nominal 100 nF X5R 0402 may measure only 40 nF. Re-run PDN simulation with derated values to ensure compliance remainsResolution typically requires a combination of additional interposer decap tiling, substrate layout changes to reduce via inductance, or adjusting VRM bandwidth to improve low-frequency transient response.


## Key Takeaways

- HBM PDN noise budget per JESD235C limits VDDQ droop to ±60 mV peak-to-peak at the micro-bumps; this drives the target impedance specification for interposer and substrate PDN design.
- Hierarchical PDN simulation (plane extraction → current stimulus → co-simulation) is required to accurately model impedance from board VRM through substrate, interposer, and into the HBM die.
- Three decap tiers — on-die, interposer MIM, and substrate SMT — must be co-optimized; decap capacitance derating under DC bias and temperature must be included in simulation to avoid sign-off risk.
- Silicon validation combines on-die voltage sensors (ODVS registers), ATE simultaneous maximum-BW stress patterns at temperature, and scope probing of exposed PDN nodes to close the loop between simulation and silicon.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) DRAM Standard — JESD235C §6.6 (VDDQ droop specification), §5 (electrical characteristics), §8 (PRBS traffic patterns). Available at jedec.org.
2. **[JEDEC]** JEDEC JESD238A: High Bandwidth Memory 3 (HBM3) Standard — JESD238A §5.3 (on-die decoupling capacitance requirements for HBM3 stacks).
3. **[Datasheet]** Cadence Sigrity PowerSI: Power Integrity Analysis — Cadence Design Systems, Sigrity PowerSI product documentation — S-parameter extraction and target impedance analysis for 2.5D/3D packages.
4. **[Paper]** Kim et al., 'Power Integrity Analysis of 2.5D HBM2 Package Using Silicon Interposer' — IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 10, no. 3, 2020. doi:10.1109/TCPMT.2020.2971234
5. **[Book]** Rao, S., 'Power Delivery Network Design for High Bandwidth Memory in Advanced Packaging' — In: Advanced Packaging Technologies, Springer, 2022, Ch. 9, pp. 211–248.
6. **[Datasheet]** ANSYS SIwave: Signal and Power Integrity Analysis — ANSYS Inc., SIwave product brief — decap optimization, resonance analysis, and HBM package PDN co-simulation. Available at ansys.com.

## Additional Learning: VRM Bandwidth and HBM PDN Low-Frequency Response

While decaps handle mid- and high-frequency droop, low-frequency PDN response (DC to ~1 MHz) is dominated by the Voltage Regulator Module (VRM) bandwidth. A VRM with too narrow a control bandwidth (e.g., 50 kHz crossover frequency) cannot respond fast enough to suppress droop from HBM burst activity patterns that repeat at memory refresh intervals (~7.8 µs for standard 64 ms refresh). Designers should target VRM crossover frequencies of 200–500 kHz for HBM supply rails, verified by measuring the closed-loop output impedance with a Bode 100 or similar network analyzer. The transition frequency where VRM response hands off to board bulk capacitance is a common design gap that causes low-frequency impedance peaks missed in simulation if VRM is modeled as an ideal voltage source.
