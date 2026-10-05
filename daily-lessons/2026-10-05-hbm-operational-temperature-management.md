# HBM Operational Temperature Management

*Monday, Oct 05 2026*

*Module 18.4 — HBM in Production AI Systems & Silicon Lifecycle Management*

## Thermal Constraints in HBM Die Stacks

HBM packages stack up to 12 DRAM dies over a logic base die, all connected by TSVs, creating a vertical heat path with limited convective surface area. JEDEC JESD235C specifies a maximum junction temperature (TJ,max) of **85 °C** for standard-grade HBM3 and **95 °C** for extended-grade parts. Exceeding TJ,max accelerates DRAM bit-flip rates, degrades retention, and can cause permanent dielectric breakdown in TSV liners.
Heat is generated primarily in the logic base die (PHY, DRAM I/O, DFI logic) and in each DRAM core array during activate/precharge cycles. With thermal resistance RθJC typically 0.15–0.25 °C/W for a 4-Hi HBM2E stack, and peak power densities up to 15 W, the temperature gradient from base to top die can reach 10–15 °C, making the top die the limiting component.
- JEDEC JESD235C Table 32 lists operating temperature ranges by speed grade- HBM3 extended-temperature SKUs (e.g. Samsung K4FAF3252L-HC14) are rated to 95 °C for automotive and edge inference- TSV thermal conductivity (≈150 W/m·K for Cu) limits but does not eliminate vertical thermal gradients

## Dynamic Frequency-Voltage Scaling in HBM Controllers

The host memory controller (GPU, NPU, or HBM controller ASIC) implements DVFS by adjusting the HBM interface clock and, where supported, the VDDQ supply. JEDEC HBM3 defines a set of **speed grades** (1.0 GT/s, 1.6 GT/s, 2.4 GT/s, 3.2 GT/s) that map directly to programmable gear-down ratios in the PHY. The controller firmware monitors on-die temperature sensor (ODTS) readback via the HBM CATTRIP/AERR sideband and steps down the frequency tier when thermal thresholds are crossed.
DVFS policy tables stored in controller microcode typically implement hysteresis: the controller downgrades when T_J exceeds Thigh and upgrades only when T_J falls below Tlow = Thigh − ΔT (typically ΔT = 5–10 °C). This prevents rapid oscillation ("thermal thrashing") that would cause repeated PLL lock/unlock cycles on the DRAM side.
- AMD CDNA2/3 (MI250X, MI300X) implements per-HBM-stack DVFS with 200 ms polling intervals via PMFW- NVIDIA H100 uses a unified thermal controller that co-throttles GPC clock and HBM link clock proportionally- Voltage reduction at lower speed grades: VDDQ drops from 1.1 V (full speed) to as low as 0.9 V, yielding quadratic dynamic power reduction

## Throttling Policies and JEDEC Thermal Control Registers

JESD235C defines a **Mode Register 4 (MR4)** in HBM that contains a 3-bit temperature readout field (bits [6:4]) with 8 temperature bands from &lt;45 °C to ≥115 °C. Controllers poll MR4 via the HBM maintenance command interface on a software-configurable interval (typically every 32–128 ms in production systems).
Above Thigh (commonly set at 80–85 °C in firmware), the controller enters **Throttle Mode 1**: it reduces the command bus utilization to 75% of peak and extends refresh intervals beyond the nominal tREF=3.9 µs. At Tcritical (typically 90 °C), **Throttle Mode 2** engages, dropping to 50% utilization and asserting CATTRIP_N to signal the PCB power management IC to reduce VDDQ.
- MR4[6:4] = 0b101 indicates T_J ≥ 85 °C on HBM2E; controller should act within 10 ms per JESD235C §6.14- CATTRIP_N is an active-low open-drain signal; if not de-asserted within 10 µs of assertion, the VRM must cut power per system board specification- Refresh rate temperature compensation: JEDEC defines temperature-compensated auto refresh (TCSR) — at T_J ≥ 85 °C, tREF must be halved to maintain data retention per JESD235C Table 35

## Thermal Runaway Prevention and Safety Mechanisms

Thermal runaway in stacked DRAM occurs when leakage current increases with temperature, increasing power, increasing temperature further — a positive feedback loop. HBM mitigates this through a hierarchy of safety mechanisms:
- **Level 1 — On-die ODTS:** Each die contains a bandgap thermal sensor accurate to ±3 °C. The logic base die aggregates per-die readings and exposes the maximum via MR4 and the analog CATTRIP pin.- **Level 2 — Package thermal diodes:** Discrete BJT-based thermal diodes on the HBM package allow the PCB temperature monitoring IC (e.g. TMP464) to read Tcase independently of the DRAM interface. These provide fail-safe coverage when the HBM memory bus is non-functional.- **Level 3 — PCB/system BMC:** The baseboard management controller (BMC) reads all package thermal diodes, compares against manufacturer-specified Tcase,max (typically 70 °C for HBM2E), and can force a system shutdown via IPMI emergency shutdown command independent of GPU firmware.Thermal runaway prevention also includes **write-activity limiting**: write operations dissipate 20–40% more energy than reads per HBM cell (due to sense-amp full-swing writes), so write bandwidth is capped in firmware during thermal emergencies.


## Refresh Rate Management Under Thermal Stress

DRAM retention time degrades exponentially with temperature — retention halves for every ~10 °C increase above 85 °C. JEDEC JESD235C mandates **temperature-compensated self refresh (TCSR)**, which the controller activates by writing MR2[2:1] to select the high-temperature refresh rate (tREF_HT = 1.95 µs, half of the nominal 3.9 µs tREF).
For ATE validation of thermal throttling, test engineers use the following procedure: (1) Force the HBM die temperature using a TEC or forced hot-air fixture to ≥85 °C, (2) Read MR4 to confirm the thermal band register reflects the set temperature, (3) Verify controller transitions to TCSR by monitoring DRAM command bus — activate/precharge pairs for refresh should appear at 2× nominal rate on a logic analyzer, (4) Inject single-bit errors via address scramblers and confirm ECC correction counters increment correctly under the degraded refresh interval.
- Symptom of missed TCSR: elevated DRAM uncorrectable error (UCE) rates at high temperature in DIMM stress tests- JEDEC JESD235C §7.12 covers TCSR enabling sequence and timing requirements- SK Hynix AN-0022 "HBM2E Thermal Management" covers per-stack thermal characterization methodology for system integrators

## Key Takeaways

- HBM3 T_J,max is 85 °C (standard) / 95 °C (extended grade); exceeding this accelerates retention failure and TSV degradation
- Controllers implement hysteresis-gated DVFS using MR4 temperature polling every 32–128 ms; CATTRIP_N provides emergency VRM cutoff at T_critical
- Thermal runaway is prevented by three independent layers: on-die ODTS, package thermal diodes, and system BMC; all must be validated in ATE qualification
- Temperature-compensated auto refresh (TCSR) halves tREF at ≥85 °C — ATE suites must exercise this path explicitly or ECC corner cases will escape

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C, §6.14 (thermal throttling), §7.12 (TCSR), Table 32 (temperature ratings), Table 35 (refresh vs. temperature)
2. **[Datasheet]** HBM2E Thermal Management Application Note — SK Hynix AN-0022, rev. 1.2 — die-level thermal characterization and CATTRIP_N integration guide
3. **[Web]** AMD Instinct MI300X Accelerator Thermal Design Guide — AMD Publication #57500 — PMFW DVFS policy, per-stack thermal polling architecture, CATTRIP_N board routing rules
4. **[Paper]** DRAM Data Retention and Temperature: A Study of Mechanisms — Liu et al., ISCA 2013 — empirical retention half-life vs. temperature curves, supports TCSR threshold selection
5. **[JEDEC]** Low Power Double Data Rate 5 (LPDDR5) Standard — JESD209-5B §8.8 — TCSR enabling sequence, comparable to HBM3 TCSR for cross-technology reference
6. **[Datasheet]** TMP464 Remote and Local Temperature Sensor — Texas Instruments SBOS599F — BJT thermal diode interface for HBM package T_case monitoring, ±1 °C accuracy

## Additional Learning: HBM Thermal Impedance Stack and Hotspot Modeling

Beyond junction temperature, system designers use a layered R_θ model: R_θJC (die-to-case, ≈0.15–0.25 °C/W), R_θCS (case-to-spreader, determined by TIM conductivity), and R_θSA (spreader-to-ambient, dominated by heatsink). For HBM3 stacks on MCM packages, the logic base die hotspot sits at the bottom of the stack, but the top DRAM die experiences the highest temperature due to accumulated thermal resistance through intermediate dies. Finite-element thermal simulation (ANSYS Icepak or Cadence CELSIUS) of the specific stack geometry is required to correctly predict per-die T_J and set per-stack DVFS thresholds — a uniform T_J assumption can under-throttle the top die by 8–12 °C in 8-Hi stacks.
