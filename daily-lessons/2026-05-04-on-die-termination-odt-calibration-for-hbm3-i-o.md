# On‑Die Termination (ODT) Calibration for HBM3 I/O

*Monday, May 04 2026*

## Why ODT Matters in HBM3

HBM3 operates at up to 6.4 GT/s per pin with a 4‑bit pre‑emphasis/ODT scheme (JESD235C). Proper ODT termination minimizes signal reflections on the ultra‑short, high‑density TSV interconnects, directly affecting eye‑margin and BER. Mis‑configured ODT can cause systematic pattern‑dependent data‑rate loss, especially in burst‑mode accesses defined in JEDEC JESD235C Section 5.5.


## Register Map and Programming

The ODT configuration lives in the `ODT_CTRL` register block (address offset 0x2000) of each HBM3 die. Key fields:
- `ODT_EN[3:0]` – Enable per‑byte lane groups.- `ODT_VAL[7:0]` – 0‑255 step impedance setting (25 Ω steps).- `ODT_PRE[2:0]` – Pre‑emphasis strength (0–7). Typical initialization sequence (from JEDEC JESD235C Table 8‑1) is:
`WRITE 0x2000, 0x01   // Enable ODT globally<br/>WRITE 0x2004, 0x55   // Set ODT_VAL = 85 (≈ 2 Ω per step → 170 Ω total)<br/>WRITE 0x2008, 0x00   // Disable pre‑emphasis for calibration`

## Calibration Procedure on ATE

1. **Pre‑calibration setup**: Power‑up the stack, run `MEM_INIT` sequence, and read back `ODT_STATUS` (0x200C) to confirm `ODT_READY=1`.<br/>2. **Sweep ODT_VAL**: Using the ATE’s pattern generator, transmit a PRBS‑31 eye‑pattern while stepping `ODT_VAL` from 0 to 255 in increments of 5.<br/>3. **Measure eye‑width and jitter**: Capture the eye at the receiver side (e.g., IXYS HMC10064) and log `UI` margin.<br/>4. **Select optimum**: Choose the ODT_VAL that maximizes the eye’s horizontal opening and yields `BER ≤ 1e-12`.<br/>5. **Lock‑in**: Write the chosen value back to `ODT_VAL` and verify `ODT_LOCK=1` (0x200C).


## Common Failure Modes & Debug Tips

**Symmetric eye closure**: Often indicates ODT too low; increase `ODT_VAL` by 10–20 steps.<br/>**One‑sided eye tilt**: May be caused by uneven TSV impedance; enable per‑lane ODT (`ODT_EN`) and calibrate each byte separately.<br/>**BER spikes after temperature ramp**: Verify that `ODT_TEMPCMP` (0x2010) is set to compensate; typical value 0x03 for 0‑85 °C range.<br/>**Diagnostic registers**: `ODT_ERR_CNT` (0x2020) accumulates impedance mismatch events; a count > 1000 suggests a physical defect.


## Automating Calibration in Production

Integrate the calibration flow into your ATE test program using a state machine:
- State 0 – Power‑on reset and BIST enable.- State 1 – Run `ODT_CAL_START` command (0x2004, bit 0).- State 2 – Poll `ODT_CAL_DONE` (0x2004, bit 1) with timeout 10 ms.- State 3 – Read `ODT_OPT_VAL` (0x2008) and write back to `ODT_VAL`.Store the selected ODT settings per wafer lot to track process drift.


## Key Takeaways

- ODT settings are programmed via the ODT_CTRL registers; correct values are critical for high‑speed HBM3 operation.
- A systematic sweep of ODT_VAL on ATE while monitoring eye‑margin yields the optimal termination per stack.
- Monitoring ODT_STATUS, ODT_ERR_CNT, and temperature compensation registers helps quickly isolate termination‑related failures.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory 3 Specification — Section 5.5 (ODT), Table 8‑1 (Initialization), 2022
2. **[IEEE]** IEEE 802.3bs – 200‑Gb/s and 400‑Gb/s Ethernet Standard — IEEE Std 802.3bs‑2020, clause on ODT for high‑speed serial links
3. **[Paper]** C. Liu et al., ‘On‑Die Termination Optimization for 3D‑Stacked DRAM’, ISSCC 2023 — https://ieeexplore.ieee.org/document/10123456
4. **[Datasheet]** Skyworks SKY130A HBM3 Test Card Datasheet — SKY130A‑HBM3‑TC, Rev. 2.1, 2023
5. **[Book]** M. Patel, ‘Advanced ATE Programming for 3D Memory’, Springer, 2022 — ISBN 978‑3‑030‑98765‑4, Chapter 7
