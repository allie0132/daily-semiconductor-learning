# Cattrip & Thermal Shutdown Verification in HBM

*Saturday, May 30 2026*

*Module 2.10 — Electrical Testing*

## What Is CATTRIP and Why It Matters

<p>CATTRIP (Catastrophic Temperature Trip) is a dedicated hardware protection mechanism in HBM2, HBM2E, and HBM3 devices that monitors on-die temperature in real time. When the die temperature exceeds the CATTRIP threshold — specified by JEDEC as T<sub>CATTRIP</sub>, typically 105 °C for HBM2E (JESD235C Table 5) — the CATTRIP pin asserts HIGH immediately, independent of the memory controller or any software path.</p>
<p>This hard-wired assertion is critical because HBM stacks are integrated in close thermal proximity to logic dies in 2.5D/3D packages. A runaway thermal condition can propagate across the silicon interposer before the system's thermal management firmware can respond. CATTRIP provides a microsecond-latency shutdown path that bypasses all protocol layers.</p>

## CATTRIP Pin Behavior and Electrical Specification

<p>The CATTRIP pin is an open-drain output on the HBM die, pulled to VDDQ externally by the host substrate or system board. Under normal operating conditions the pin is held LOW (asserted de-asserted). When T<sub>CATTRIP</sub> is exceeded the internal comparator releases the drain, pulling CATTRIP HIGH through the pull-up resistor.</p>
<ul>
<li><strong>Pin type:</strong> Open-drain, active-HIGH thermally-triggered interrupt</li>
<li><strong>VDDQ range:</strong> 1.2 V nominal; CATTRIP HIGH = VDDQ − I×R<sub>pullup</sub></li>
<li><strong>Response time:</strong> ≤ 1 µs from threshold crossing to pin assertion per JESD235C §7.4</li>
<li><strong>Hysteresis:</strong> ~5 °C implemented internally to prevent oscillation at threshold boundary</li>
<li><strong>Reset:</strong> CATTRIP de-asserts automatically once die cools below T<sub>CATTRIP</sub> − hysteresis; no register write required</li>
</ul>
<p>Multiple HBM stacks in a system can share a single CATTRIP net (wired-OR topology), simplifying system-level thermal detection — any stack exceeding threshold asserts the shared line.</p>

## ATE Verification Strategy

<p>Functional verification of CATTRIP on ATE (e.g., Advantest T2000, Teradyne UltraFLEX) requires controlled thermal stimulus since the threshold is temperature-driven, not electrically-programmed. The three primary approaches used in production test are:</p>
<ul>
<li><strong>Thermal forcing with thermal chuck/head:</strong> Ramp the DUT to T<sub>CATTRIP</sub> + margin (e.g., 110 °C) while monitoring the CATTRIP pin state. Confirm HIGH assertion. Cool below threshold and confirm de-assertion. This is the most direct method but requires a thermally controlled handler or prober.</li>
<li><strong>Self-heating via stress pattern:</strong> Drive the HBM array with worst-case simultaneous-switch patterns (all-ones, checkerboard at maximum bandwidth) at elevated ambient to exploit I²R and switching self-heating. Monitor CATTRIP and die temperature sensor readback via MRS register MR4[7:4] (thermal sensor output) to correlate CATTRIP assertion with sensor value.</li>
<li><strong>Indirect verification via MR4 sensor:</strong> At temperatures just below CATTRIP threshold, verify MR4 sensor bits increment predictably. Cross-check sensor code-to-temperature mapping against JESD235C Table 14. This validates the thermal sensing path even when thermal forcing to full CATTRIP is impractical on a given handler.</li>
</ul>
<p>Production test plans typically implement the MR4 correlation method at speed across the full temperature range of the temperature specification (−10 °C to 85 °C for industrial, 0 °C to 70 °C for consumer), reserving full CATTRIP assertion verification for qualification/characterization lots.</p>

## MR4 Thermal Sensor Readback

<p>HBM2E devices expose a 4-bit thermal sensor value in Mode Register 4 (MR4), bits [7:4]. This sensor is read via the maintenance port or through the host's memory controller using a Mode Register Read (MRR) command on the pseudo-channel. The sensor codes are defined in JESD235C Table 14:</p>
<ul>
<li><code>0b0000</code> — T &lt; 45 °C</li>
<li><code>0b0001</code> — 45 °C ≤ T &lt; 55 °C</li>
<li><code>0b0010</code> — 55 °C ≤ T &lt; 65 °C</li>
<li><code>0b0011</code> — 65 °C ≤ T &lt; 75 °C</li>
<li><code>0b0100</code> — 75 °C ≤ T &lt; 85 °C</li>
<li><code>0b0101</code> — 85 °C ≤ T &lt; 95 °C</li>
<li><code>0b0110</code> — 95 °C ≤ T &lt; 105 °C</li>
<li><code>0b0111</code> — T ≥ 105 °C (CATTRIP region)</li>
</ul>
<p>Test programs should verify the sensor transitions at each code boundary (±3 °C measurement tolerance) and confirm that MR4[7:4] = <code>0b0111</code> accompanies CATTRIP assertion. A mismatch between the sensor code and the CATTRIP pin state indicates either a failing sensor or a failing CATTRIP comparator — two distinct fault mechanisms requiring separate root-cause analysis.</p>

## Test Coverage and Failure Mode Analysis

<p>Complete CATTRIP test coverage must address four distinct failure modes:</p>
<ul>
<li><strong>Comparator stuck-LOW:</strong> CATTRIP never asserts even at T &gt; T<sub>CATTRIP</sub>. Results in unprotected thermal runaway in the field. Caught by thermal forcing above threshold.</li>
<li><strong>Comparator stuck-HIGH:</strong> CATTRIP asserts spuriously at normal operating temperature, causing unnecessary memory shutdowns. Caught by confirming CATTRIP is LOW at T &lt; T<sub>CATTRIP</sub> − hysteresis.</li>
<li><strong>Threshold out-of-spec:</strong> CATTRIP asserts at T<sub>CATTRIP</sub> + δ where δ exceeds JEDEC tolerance (±5 °C for HBM2E). Requires thermal sweep around nominal threshold for full characterization.</li>
<li><strong>Sensor readback mismatch:</strong> MR4 bits do not match actual temperature, causing misleading host-side thermal management. Verified by MR4 vs. chuck temperature correlation across all 8 codes.</li>
</ul>

## Key Takeaways

- CATTRIP is a hardware open-drain thermal interrupt that asserts within 1 µs when the die exceeds T<sub>CATTRIP</sub> (~105 °C), independent of firmware
- MR4[7:4] provides an 8-code thermal sensor readable via MRR that must be verified across all temperature boundaries
- Production ATE test uses MR4 sensor correlation at temperature; full CATTRIP assertion is verified during qualification using thermal forcing to T > T<sub>CATTRIP</sub>
- Four distinct failure modes (comparator stuck-HIGH/LOW, threshold out-of-spec, sensor mismatch) require separate, targeted test conditions

## References

1. **[JEDEC]** JESD235C High Bandwidth Memory (HBM) DRAM — §7.4 CATTRIP Specification and Table 14 Thermal Sensor Codes
2. **[JEDEC]** JESD235C Annex A: Mode Register Definitions — MR4[7:4] Thermal Sensor bits
3. **[JEDEC]** JESD209-5B LPDDR5/LPDDR5X — Thermal sensor architecture reference for cross-standard comparison
4. **[Datasheet]** SK Hynix HBM2E Product Brief H5VR16ESM4H — CATTRIP pin electrical characteristics and thermal thresholds
5. **[Paper]** Kim et al., "Thermal Management and Monitoring in High Bandwidth Memory Systems," IEEE ECTC 2021, DOI 10.1109/ECTC32696.2021.00156
6. **[Book]** Micron Technology, "HBM2E Design Guide," Application Note TN-46-12, Rev. B

## 🔍 Additional Learning: CATTRIP Wired-OR Topology in Multi-Stack Systems

When multiple HBM stacks share a single CATTRIP net (wired-OR), any one asserting device pulls the line HIGH. Test programs must distinguish per-stack CATTRIP from system-level CATTRIP by reading each stack's MR4 individually after a shared-line assertion — this per-device isolation step is essential for field RMA root-cause analysis and is commonly missed in first-pass test program development.
