# HBM AC/DC Parametric Testing

*Wednesday, May 27 2026*

*Module 2.4 — Electrical Testing*

## AC/DC Parametric Testing Overview

AC/DC parametric testing verifies that an HBM device's electrical characteristics — supply currents, voltage levels, and timing — conform to JEDEC specification limits under defined conditions. Unlike functional tests that exercise data paths end-to-end, parametric tests isolate individual DC operating points and AC timing relationships, producing pass/fail margins that predict field reliability and interoperability with the Logic die.
JESD235C defines three test categories: **DC parametrics** (static supply currents IDD1/IDD3/IDD5/IDD6, input threshold levels VIH/VIL, output drive IOH/IOL), **AC timing parametrics** (setup/hold tDS/tDH, access time tAC, clock parameters tCK/tCKHZ), and **power-state transition timings** (tXP exit-from-power-down, tCPHED clock-present-to-host-enable-done). ATE patterns for each category differ substantially in pin forcing, load conditions, and measurement resolution requirements.


## IDD Current Measurements — Categories and Limits

HBM3 defines seven IDD operating-current categories per JESD238A. Each requires a specific traffic pattern and a stabilized measurement window after pattern onset:
- **IDD1** — Active Read/Write: all banks cycling at maximum rate. HBM3 8-Hi spec &lt;380 mA at VDD=1.2V ±5%.- **IDD3N** — Active Standby (CKE high, no command): measures leakage plus DLL power. Typically 25–60 mA for HBM3.- **IDD4W / IDD4R** — Burst Write/Read: shorter burst window isolates channel driver current from bank-activation overhead.- **IDD5** — Refresh (REF command): captures peak current during row-address strobe in all banks. Critical for thermal budgeting in 2.5D packages.- **IDD6** — Self-Refresh: the lowest-power retention state; spec'd in µA. Measured after tCKESR self-refresh entry hold time expires.ATE measurement technique: force VDD via a precision SMU in **voltage-force / current-measure** mode. Apply the stimulus pattern, wait for IDD settling (&gt;10 µs), then integrate current over a 50 µs window using the ATE's per-pin parametric measurement unit (PMU) or an external current amplifier. Average at least 16 windows to reduce noise below 1 mA.


## Timing Margin Testing — Setup, Hold, and Access Times

Timing parametrics characterize the AC interface between the Logic die's PHY and the HBM DRAM. Key parameters from JESD235C Table 19:
- **tDS / tDH** (data setup/hold to RDQS strobe): minimum 30 ps / 30 ps for HBM3 at 6.4 Gbps. Measured by strobe-to-data skew sweep ("shmoo") on ATE.- **tDQSCK** (RDQS output access time from CK): window spec ±175 ps max. Failing margin here indicates DLL lock or power-integrity issues.- **tCK** (clock period): 312.5 ps nominal at 3.2 GHz per pseudo-channel. Jitter mask requires cumulative jitter &lt;11 ps RMS.- **tRCD / tRP / tRAS**: internal DRAM timing enforced by Mode Register settings. HBM3 default tRCD = 20 ns, tRP = 20 ns, tRAS min = 34 ns.Shmoo methodology: ATE sweeps the write-data edge relative to WCK in 5 ps steps across a ±200 ps window. The resulting 2-D eye diagram is compared against the JEDEC mask. **Timing margin = measured eye opening − minimum spec**. Typical ATE instruments (Advantest T2000/T5503, Teradyne UltraFLEX) achieve &lt;2 ps step resolution using DDS-based timing generators.


## Operating Voltage Limits — VDD, VDDQ, and VDDPLL

HBM3 operates at **VDD = 1.2 V ±5%** (1.14 V–1.26 V) and **VDDQ = 1.2 V ±5%** for the I/O domain. A third rail, **VDDPLL = 1.2 V**, powers the internal DLL/PLL and is highly sensitive to ripple (&lt;10 mVpp per JESD238A §6.3).
- **VDD min (1.14 V)**: verify retention and all-bank activate at corner. IDD1 typically rises 8–12% compared to nominal due to longer cell precharge times.- **VDD max (1.26 V)**: stress test for oxide reliability; IDD3N increases ~15%. Check that tDQSCK remains within spec — excess voltage can speed DLL faster than the timing window.- **VDDQ vs VDD mismatch**: if VDDQ lags VDD on power-up by &gt;50 mV, HBM I/O drivers may source latch-up current. Sequence order mandated: VDD before VDDQ, ramp ≤1 V/ms.ATE power sequencing is implemented via the instrument's PMU or a dedicated board-level sequencer with slew control. Voltage overshoot during hot-switching must be &lt;100 mV above nominal; validate with a differential probe on the DUT socket pins, not the SMU sense point, due to package inductance drop.


## ATE Test Flow and Guardbanding Strategy

A production HBM parametric test flow on an ATE (Advantest T5503 or Teradyne Magnum V) typically executes in this order:
- **1. Power-on and initialization**: apply power rails in sequence, issue RESET_n, load Mode Registers via CA bus (ZQ calibration, DLL enable, RX termination settings).- **2. DC parametrics**: IDD0→IDD6 current measurements, VIH/VIL input threshold tests using PMU force/measure, output leakage IOUT at tri-state.- **3. AC timing shmoo**: tDS/tDH sweep at 3 VDD corners × 3 temperature corners (−5°C, 25°C, 85°C for burn-in) = 9 corner combos.- **4. Frequency margining**: tCK sweep from spec minimum (312 ps) down to failure point; record frequency margin in MHz for binning.**Guardbanding**: production test limits are tightened by a <em>guardband factor</em> to account for ATE timing accuracy (typically ±5 ps systematic), temperature delta between socket and junction, and probe-card IR drop. A 10% guardband on IDD limits and 20 ps on timing limits is common practice. Guardband decisions are tracked against PPM returns to calibrate over product lifetime.


## Key Takeaways

- IDD current categories (IDD1–IDD6) each require a specific stimulus pattern and stabilized measurement window; use PMU current integration over ≥50 µs for repeatable results.
- Timing parametrics tDS/tDH and tDQSCK are measured by ATE shmoo sweeps in sub-5 ps steps; margins below 20 ps relative to the JEDEC mask trigger investigation of DLL lock or power-integrity root causes.
- VDD/VDDQ power sequencing (VDD first, ramp ≤1 V/ms) is mandatory to prevent I/O latch-up; validate overshoot at DUT socket pins rather than SMU sense lines to capture package inductance effects.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, Sections 4 (Electrical), 6 (AC/DC Operating Conditions), Table 19 (AC Parameters), 2021
2. **[JEDEC]** High Bandwidth Memory 3 (HBM3) DRAM Standard — JESD238A, Sections 6.3 (VDDPLL requirements), 7 (IDD definitions and test conditions), 2022
3. **[Book]** Memory Test: From Theory to Practice — M. Sachdev, Kluwer Academic, 2005 — Chapter 6: Parametric and DC Testing of DRAM
4. **[Datasheet]** T5503 HBM Test Solution Application Note — Advantest Corp., Doc. T5503-AN-HBM-001, 2023 — HBM3 IDD measurement methodology and guardband recommendations
5. **[Paper]** Power Integrity Challenges in 2.5D HBM Packages — Kim et al., IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol. 12, No. 4, pp. 612–621, 2022
6. **[Paper]** Timing Closure for HBM Interface in 7nm Logic — Chen & Park, Proceedings of the 58th DAC, Paper 14.2, 2021

## Additional Learning: ZQ Calibration Impact on IDD Measurements

ZQ calibration adjusts HBM output driver impedance (RON) and on-die termination (ODT) values via the ZQ pin resistor divider, targeting a nominal 240 Ω reference. Because driver impedance directly affects output short-circuit current, IDD4R and IDD4W measurements must always be taken after a completed ZQCL (ZQ Calibration Long) command sequence — skipping ZQ calibration before IDD tests can cause measurements to deviate by up to 15% from nominal. JEDEC JESD235C Appendix A3 specifies the mandatory ZQ calibration sequence and settling time (tZQCL = 1 µs minimum) before any IDD characterization begins.
