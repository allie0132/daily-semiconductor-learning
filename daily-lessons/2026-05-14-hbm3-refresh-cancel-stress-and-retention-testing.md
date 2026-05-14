# HBM3 Refresh‑Cancel Stress and Retention Testing

*Thursday, May 14 2026*

## Background and Objectives

The JEDEC JESD235C standard defines the `REFRESH_CANCEL` command used by the controller to abort a scheduled refresh. Improper handling can cause data loss or timing violations, especially when operating near the limits of the **VDDQ** and temperature range.
This lesson covers a systematic stress test to verify that the memory array retains data when refreshes are cancelled under worst‑case conditions.


## Test Overview and Flow

1. **Initialize** the HBM3 stack at the target temperature (e.g., -40 °C, 125 °C).<br>2. Write a known pattern (e.g., `0xAA55AA55`) to all addresses using the `WRITE` command.<br>3. Issue `REFRESH_CANCEL` after the `tRFC` timer expires but before the actual refresh begins.<br>4. Wait for a programmable interval (e.g., 10 ms to 1 s) to simulate multiple missed refresh windows.<br>5. Issue a full `REFRESH` burst and read back the data.<br>6. Log any bit errors and capture timing traces via the ATE’s high‑resolution scope.


## ATE Configuration and Register Settings

Use a Keysight 33600‑A/32000‑A platform with a 5 GHz sampling clock. Configure the following registers on each DRAM channel:
- `REG_0x0100 (REFRESH_INTERVAL)` – set to maximum allowed value (e.g., 7.8 µs) to stretch refresh windows.- `REG_0x0114 (REFRESH_CANCEL_EN)` – enable command.- `REG_0x0208 (VDDQ_TUNE)` – program to low‑voltage corner (0.8 V typ).- `REG_0x030C (TEMP_SENSE)` – read back temperature for verification.Enable `TRACE_MODE = ON` to capture the `tRC` and `tRFC` edges with 20 ps resolution.


## Data Analysis and Pass/Fail Criteria

Analyze error maps per die:
- If **BER ≤ 1e‑12** after 100 ms of cancelled refresh, the die passes.- Any single‑bit error occurring within the first 10 ms indicates a failure to retain charge.- Check that the controller re‑issues a `REFRESH` after the cancel and that `tRFC` meets the spec (≤ 350 ns typical for HBM3). Document the worst‑case corner that produced errors for root‑cause analysis.


## Mitigation Strategies

If failures are observed, consider the following actions:
- Increase `REFRESH_INTERVAL` safety margin by 10 %.- Adjust `VDDQ_TUNE` to high‑voltage corner (+0.05 V) for marginal dies.- Implement controller firmware that limits consecutive `REFRESH_CANCEL` commands to three per 100 µs.

## Key Takeaways

- Refresh‑cancel must be exercised at extreme voltage/temperature to expose latent retention failures.
- JEDEC JESD235C timing margins (tRFC, tRC) are critical when refresh is aborted.
- ATE must capture sub‑nanosecond timing to verify that the controller correctly re‑issues refresh after cancel.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM3 Standard — Section 4.5.2 Refresh Cancel, Section 5.3 Timing
2. **[IEEE]** IEEE Tran. on VLSI Systems, 2022, "Refresh Management in 3D Stacked DRAM" — doi:10.1109/TVLSI.2022.3156789
3. **[Datasheet]** Micron HBM3 Datasheet, Rev. B — Table 2‑8: VDDQ ranges, Table 3‑12: Refresh timing
4. **[Web]** Keysight 33600‑A ATE User Guide — https://www.keysight.com/pdf/33600A_UG.pdf
5. **[Book]** High‑Performance Memory Systems, 2nd Ed., S. Marculescu, 2020 — Chapter 7: DRAM Refresh Schemes
