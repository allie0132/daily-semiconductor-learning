# HBM Mode Registers & Configuration Testing: MR0-MR15

*Wednesday, Jun 03 2026*

*Module 3.6 — Protocol & Compliance*

## Mode Register Architecture and Access Protocol

HBM mode registers (MRs) are accessed via the **Mode Register Set (MRS)** command on the command/address (CA) bus. In HBM3 (JESD235C), the MRS command drives a 3-bit register address on CA[2:0] and an 8-bit data payload on CA[10:3], targeting a specific pseudo-channel. The **Mode Register Read (MRR)** command returns the current register value on the DQ bus during the subsequent read latency window.
Registers MR0-MR15 are individually addressable. HBM3 uses **per-channel** mode registers - each of the 8 channels (16 pseudo-channels) maintains an independent MR state, requiring full coverage testing across all pseudo-channels. The MRS command must comply with **tMRD** (minimum 4 nCK between successive MRS commands) to prevent register metastability.
- MRS command takes effect after tMRD (4 nCK in HBM3)- MRR data appears on DQ after tMRR read latency offset- All MRS/MRR must occur with **CKE HIGH** and device in idle state

## MR0-MR5: Core Timing, Latency, and Data Path Configuration

**MR0** is the most critical register, controlling **Burst Length (BL)** and **CAS Latency (CL)**. In HBM3, BL is fixed at 4 (MR0[1:0]=00), and CL is encoded in MR0[5:2] with valid values from CL=6 to CL=17 depending on operating frequency. An incorrect CL setting causes systematic read failures - commonly seen as a fixed-offset alignment error in captured eye diagrams.
**MR1** configures **Write Latency (WL)** and **Additive Latency (AL)**. WL must match the PHY write-path delay; mismatches appear as DQS-to-DQ alignment errors in ATE timing closure reports. **MR2** and **MR3** control read/write preamble and postamble lengths - critical for eye margin at data rates above 3.2 Gbps/pin.
- **MR4**: DBI-WR enable (bit 3) and DBI-RD enable (bit 2) - Data Bus Inversion reduces simultaneous switching noise- **MR5**: ODT impedance settings - affects signal integrity margin testing

## MR6-MR10: ECC, Temperature Sensor, and RAS Feature Control

**MR8** is the ECC control register in HBM3. Bit 0 enables/disables SECDED ECC; bit 1 enables the **ECC error log**, which accumulates correctable error counts accessible via MRR. Test strategy: write MR8[0]=1, inject single-bit errors via deliberate data inversion during write, then verify ECC correction via MRR readback of error log registers MR14 and MR15.
**MR6** holds the temperature sensor output in read-only mode - MRR of MR6 returns the on-die thermal sensor reading with 1 degree C LSB resolution. Cross-correlate against chuck temperature at ATE: a deviation greater than 5 degrees C flags a sensor calibration failure. **MR7** controls CATTRIP threshold programming in applicable HBM implementations - writing above the thermal limit triggers CATTRIP pin assertion, which ATE must capture as a forced test interrupt.
- **MR9**: Refresh rate control (1x, 2x, 4x) - test at all three settings to verify tREFI compliance- **MR10**: CRC enable - enables per-burst CRC on the read data path per JESD235C Section 6.3

## MR11-MR15: HBM3 Extensions, Error Logs, and Reserved Fields

**MR14 and MR15** are read-only **ECC error log registers** in HBM3. MR14[7:0] reports correctable (single-bit) error counts; MR15[7:0] reports uncorrectable (double-bit) detection events. After each DRAM stress pattern, MRR of MR14/MR15 validates error injection and ECC hardware function. Error log counters are **sticky** - they persist across refresh cycles until explicitly cleared via MR8[3]=1.
**Reserved bit testing** is a JEDEC compliance requirement: JESD235C mandates that RFU-labeled bits must return 0 on MRR regardless of what was written via MRS. ATE patterns must write 0xFF to registers containing reserved fields, then perform MRR and mask-compare against the defined bit pattern. Any non-zero return on an RFU bit is a compliance failure.
- MR11-MR13: Vendor-specific or HBM3e-extended features (PHY training status, vendor ID)- Boundary-value testing: write 0x00 and 0xFF to each MR; verify defined bits behave per spec

## ATE Mode Register Test Implementation and Coverage Strategy

A complete MR test suite on Advantest V93000 or Teradyne UltraFLEX requires three layers: **(1) Walk test** - write each valid value to each MR and verify via MRR, covering all defined bits. **(2) Interaction test** - stress timing interactions with CL+WL combinations near min/max valid pairs. **(3) Retention test** - verify MR values survive a self-refresh entry/exit cycle (tPD hold) unchanged.
MRR data is captured as a **functional read** on ATE - the DQ return is compared against expected bit patterns using per-bit expect (PBE) masks. A critical pitfall: MRR data appears on DQ at the CAS Latency offset from the MRR command, so ATE strobe timing must align to the CL programmed in MR0. Misaligned strobe captures are the #1 debug failure mode during first-silicon MR test bring-up.
- Test all 16 pseudo-channels independently - channel-to-channel MR isolation is a common RTL bug- Verify **reset-state**: after power-on-reset or ZQCal init, all MRs must match JEDEC-defined reset values- Automate MR sweep via parametric loops in the ATE test program; avoid hardcoded single-value tests

## Key Takeaways

- MR0 (CAS Latency, Burst Length) and MR1 (Write Latency) are the highest-impact registers - incorrect values cause systematic functional failures that mimic electrical defects
- Reserved/RFU bits must return 0 on MRR regardless of MRS write value; any non-zero RFU readback is a JEDEC JESD235C compliance failure
- ECC control (MR8) and error log (MR14/MR15) testing requires deliberate error injection to validate end-to-end SECDED hardware function
- All 16 pseudo-channels must be tested independently for MR state isolation - shared register state bugs are common in first-silicon HBM controller integration
- ATE MRR capture requires strobe alignment to the CL programmed in MR0; strobe timing mismatch is the #1 bring-up failure mode for mode register testing

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM - JESD235C — JEDEC Standard JESD235C, Section 4 (Mode Registers), Table 4-1 through Table 4-15; Section 6.3 (CRC)
2. **[JEDEC]** HBM2 Standard - JESD235A Mode Register Definitions — JEDEC JESD235A, Section 4.4 - MR0-MR8 definitions and power-on reset values
3. **[Datasheet]** SK Hynix HBM3 HBMC Series Datasheet — Mode Register Map section; MRS/MRR timing diagrams; tMRD specification (Rev 1.0)
4. **[Datasheet]** Micron HBM2e Mode Register Programming Technical Note TN-HBM-01 — Programming sequences, boundary conditions, and ATE implementation guidance for MR0-MR10
5. **[Web]** Advantest V93000 HBM Test Library Application Note AN-V93K-HBM-003 — MRR capture alignment, PBE mask programming, and pseudo-channel parallel MR sweep patterns
6. **[JEDEC]** JEDEC JESD79-4B DDR4 Specification — Section 3.5 - MRS/MRR protocol heritage shared with HBM command bus; cross-reference for tMRD timing

## 🔍 Additional Learning: HBM3e MR Extensions: New Registers in JESD235D

HBM3e (JESD235D) adds new mode register definitions extending coverage beyond JESD235C, including enhanced refresh management registers and per-channel RFM (Refresh Management) control bits. HBM3e also expands PHY training status readback registers (MR11-MR13) to expose per-pseudo-channel read/write DQ training results, enabling ATE to diagnose marginal PHY calibration without oscilloscope captures. Test engineers targeting HBM3e must update MR test suites to include these extended registers and validate that HBM3 legacy mode correctly masks or ignores HBM3e-exclusive MR fields.
