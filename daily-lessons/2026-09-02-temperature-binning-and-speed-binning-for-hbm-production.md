# Temperature-Binning and Speed-Binning for HBM Production

*Wednesday, Sep 02 2026*

*Module 16.6 — HBM Test Program Development & Characterization*

## Binning Dimensions in HBM Production

HBM production test assigns each die or stack to a **bin** — a combination of temperature-range grade and data-rate (speed) grade. These two axes are largely independent: a device may achieve the highest speed bin but only at commercial temperatures, or it may qualify for industrial temperature range at a lower speed bin.
JEDEC JESD235C defines HBM3 speed bins (up to 9600 Mbps per pin) and operating temperature limits (`Tj` 0 °C to 85 °C commercial, −40 °C to 105 °C industrial). Binning boundaries are set by AC timing tables in the standard (Table 53–54 of JESD235C for HBM3) and by device-specific datasheets from SK Hynix, Micron, and Samsung.
- **Speed bin**: maximum validated data rate in Mbps/pin at rated `VDD` and temperature corner- **Temp bin**: minimum/maximum junction temperature at which all AC and DC specs are met- A single test program typically covers all candidate bins; the ATE sorts the device after results are evaluated

## Temperature Binning: Corners, Specs, and ATE Forcing

Temperature binning requires testing at the **worst-case thermal corners** for the target grade. For commercial grade (0 °C to 85 °C), ATE typically tests at `T = 25 °C` (ambient) and `T = 85 °C` (hot). For industrial grade (−40 °C to 105 °C), additional cold (`−40 °C`) and extended-hot (`105 °C`) runs are mandatory.
ATE temperature forcing methods:
- **Thermal stream (forced-air)**: hot or cold air directed at the device under test (DUT) via a thermal head; typical setpoint accuracy ±2 °C, ramp rate 20–40 °C/min- **Thermostream controller** (e.g., Thermonics T-2500): nitrogen stream to −65 °C; used when cold soaking is required at wafer level- **Chuck-based (wafer probe)**: electrostatic or vacuum chuck with embedded Peltier elements holds wafer at setpoint; more uniform than forced-air for multi-site probingKey AC parameters that shift significantly with temperature include `tRCD` (RAS-to-CAS delay), `tCL` (CAS latency), and read/write DQ setup/hold windows. HBM3 specifies a **temperature compensation code (TCC)** register that the controller programs to adjust internal timing; ATE must program TCC correctly for each temperature setpoint before running AC tests.


## Speed Binning: AC Parametric Testing and Shmoo Plots

Speed binning determines the highest validated data rate. The production flow tests each device at the target speed bin's `tCK` (clock period) using the full HBM PHY protocol (Read, Write, Refresh, MRS sequences). A device passes its target bin if all timing margins are within spec across all enabled channels and pseudo-channels.
**Shmoo plots** sweep `tCK` vs. `VDD` (or `VDDQ`) to map the device's operating region. The ATE captures go/no-go results at each grid point; the resulting contour defines the speed-voltage operating space. In production, a <em>targeted shmoo</em> tests only the bin corners to minimise test time rather than sweeping exhaustively.
- HBM3: standard speed bins at 6400, 7200, 8000, 9600 Mbps/pin (JESD235C Table 52)- HBM2E: bins at 2400, 2800, 3200 Mbps/pin (JESD235B addendum, Table 56)- AC margin tests use strobe-edge placement via ATE timing generators; setup margin = strobe advance until first failure, hold margin = strobe retard until failure- Minimum margin guard-band at production: typically 20–30 ps added to the spec limit to account for tester timing uncertainty

## Guard-Banding and Tester Accuracy

ATE timing generators carry inherent jitter and systematic offsets. For HBM3 at 9600 Mbps (104 ps `tCK`), a tester with 2 ps RMS jitter represents ~2 % of the unit interval — non-trivial. Without guard-banding, devices right at the spec limit may pass on one tester and fail on another, producing **test escapes** or **overkill**.
Guard-band strategy:
- **Tighten applied spec by Δt**: if JESD235C requires tDQSS ≤ 0.45 UI, the ATE limit is set to 0.45 UI − Δt, where Δt accounts for tester repeatability (3σ) plus systematic offset measured during tester qualification- **Correlation wafers**: a set of corner devices is tested on all production testers; guard-bands are adjusted so all testers agree on pass/fail for every correlation unit- **Bin zero (reject) analysis**: devices failing only one tester but passing others are investigated to detect tester drift before it impacts production yieldThe Advantest T2000 and V93000 DRAM options publish **timing accuracy specifications** (differential channel-to-channel skew, cycle-to-cycle jitter) used to set guard-bands. Typical production guard-band for HBM3 speed testing is 5–15 ps per edge.


## Production Flow Integration and Yield Management

Binning is integrated into the ATE test program as a **multi-temperature, multi-condition flow**. A typical HBM production sort runs:
- DC parametric (leakage, short/open, IDDQ) at room temperature- Functional test at room temperature and nominal `VDD`- Speed shmoo at hot corner (85 °C or 105 °C) — eliminates slow devices early- Speed shmoo at cold corner (0 °C or −40 °C) — cold often limits worst-case timing for some paths- Bin assignment: highest speed bin passed at both corners assignedStatistical Process Control (SPC) charts track bin distribution shift across lots. A sudden increase in devices falling to a lower speed bin signals a process excursion (lithography CD shift, metal resistance change) before it becomes a yield crash.
- Wafer-level sort (WLS) assigns a preliminary bin; final-test (FT) after packaging may upgrade or downgrade based on package parasitics and thermal path- Known-good die (KGD) qualification for 2.5D integration requires WLS bin to be confirmed at FT with &lt;0.5 % re-bin rate to maintain supply chain confidence- Thermal resistance of the interposer stack shifts effective `Tj` at FT; the FT temperature setpoint must model this to avoid passing devices that will overheat in the target system

## Key Takeaways

- HBM binning is two-dimensional (temperature grade × speed grade); both axes require dedicated test conditions at process corners defined by JESD235C.
- Speed binning uses AC parametric shmoo plots sweeping tCK and VDD; production guard-bands of 5–15 ps per edge compensate for ATE timing uncertainty.
- Temperature binning mandates forcing the DUT to each corner (−40 °C, 25 °C, 85 °C, 105 °C) with correct TCC register programming before AC evaluation.
- Tester-to-tester correlation via correlation wafers is mandatory; guard-band widths are set from 3σ tester repeatability measured during tester qualification.
- SPC monitoring of bin distributions enables early detection of process excursions before full yield loss, and WLS-to-FT re-bin rate tracks KGD quality.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM — JESD235C — JEDEC Solid State Technology Association, 2022 — AC electrical characteristics Tables 52–54, temperature operating conditions Table 5
2. **[JEDEC]** High Bandwidth Memory (HBM2E) DRAM — JESD235B Addendum — JEDEC JESD235B addendum, 2020 — speed bin definitions Table 56, VDDQ/VDD requirements section 5.2
3. **[Datasheet]** Advantest T2000 DRAM Test Solution — HBM2E Application Note — Advantest Corporation, 2020 — timing accuracy specs, guard-band methodology for sub-100 ps tCK HBM testing
4. **[Datasheet]** Teradyne UltraFLEX+ Memory Test — HBM3 Technical Brief — Teradyne Inc., 2023 — channel-to-channel skew <1 ps, differential timing resolution 0.5 ps for HBM3 binning
5. **[Paper]** Kim et al., 'HBM3 DRAM for High-Performance AI Accelerators' — IEEE Symposium on VLSI Circuits, 2023 — speed bin characterisation methodology, temperature compensation register usage
6. **[JEDEC]** JEDEC JEP150 — Measuring the Effects of Solder Reflow on IC Parametric Performance — JEP150A — covers WLS-to-FT correlation methodology and re-bin rate acceptance criteria for KGD qualification

## Additional Learning: Voltage-Temperature (V-T) Interaction in HBM Speed Binning

HBM speed bins are not independent of supply voltage: a device that barely passes its speed bin at nominal VDD may fail at the low-VDD corner used to screen for long-term reliability (HTOL guard-band). Production programs therefore run a <strong>V-T interaction shmoo</strong> at each temperature corner, sweeping VDD across ±5–10 % of nominal. Devices that exhibit a non-monotonic pass region (e.g., failing at both low-VDD and high-VDD but passing at nominal) indicate marginal circuits susceptible to in-field variation and are typically downgraded to a lower speed bin regardless of their nominal-VDD result — a practice called <em>voltage-margin binning</em>.
