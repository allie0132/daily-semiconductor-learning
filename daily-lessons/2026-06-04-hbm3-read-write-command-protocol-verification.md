# HBM3 Read/Write Command Protocol Verification

*Thursday, Jun 04 2026*

*Module 3.8 — Protocol & Compliance*

## Command Encoding and Register Map

The HBM3 interface uses the standard JEDEC JESD235C command set. Each command is a 16‑bit header transferred over the command lane (CMD) and an optional 16‑bit address on the address lane (ADR). The most common commands are:
- `0x00` – NOP- `0x01` – READ (burst)- `0x02` – WRITE (burst)- `0x03` – REFRESHRegister **R0x0010** (CMD_CFG) defines the command width (16 bit or 32 bit) and whether the address is inline or out‑of‑band. Verify that the DUT’s configuration matches the test fixture’s setting before sending any transaction.


## Timing Parameters for Read/Write

Key timing windows (all in nanoseconds) defined in JESD235C Table 5‑3:
- **tCMD** – Minimum command valid pulse width: 2 ns.- **tADDR** – Address must be presented within 0.5 ns after the trailing edge of the command.- **tRCD** – Read command to data valid: 4.5 ns (typical), 6 ns (max).- **tWR** – Write command to data acceptance: 4 ns (typical), 5.5 ns (max).- **tCAS** – CAS latency for read bursts: 6, 8, or 12 cycles, selectable via `R0x0020` (CAS_CFG).Use the ATE’s high‑resolution timing monitor (e.g., Keysight 86102D) to capture edges and confirm compliance within ±0.2 ns.


## Burst Length, Data Mask, and ECC

HBM3 supports burst lengths of 8, 16, 32, and 64 beats. The `BL` field in the command header (bits 4‑6) selects the length. When `BL=0b011`, a 64‑beat burst is issued. Data mask (DM) is optional; if DM is enabled (R0x0030.DM_EN = 1), each data lane transmits an extra mask bit on the DM lane. Verify that the mask bits are ignored when `DM_EN=0` and correctly suppress write data when set to ‘1’.
HBM3 optionally employs on‑die ECC. The ECC syndrome is appended to each 512‑bit data block. Capture the syndrome on the `ECC_OUT` pins and compare against the calculated syndrome using the Hamming‑(72,64) algorithm described in JESD235C §7.2.


## Response and Error Reporting

After each command, the DRAM returns a 4‑bit status word on the `RESP` lane. The status bits are defined as:
- `0` – OK- `1` – CMD_ERR (illegal command)- `2` – ADDR_ERR (out‑of‑range address)- `3` – ECC_ERR (detectable ECC error)In compliance testing, inject known errors (e.g., flip a command bit) and verify that the appropriate error code is returned within the **tRESP** window of 2 ns after the trailing edge of the data phase.


## Verification Flow on ATE

1. **Configure DUT**: Load CMD_CFG, CAS_CFG, and DM_EN registers via the JTAG back‑door or init‑sequence.<br/>2. **Stimulus Generation**: Use the ATE’s pattern generator to send command + address vectors with precise edge alignment.<br/>3. **Capture**: Record CMD, ADR, DATA, DM, RESP, and ECC_OUT on all lanes using a multi‑lane high‑speed sampler (e.g., Tektronix DPO72004C).<br/>4. **Analysis**: Run a Python‑based checker that parses the captured vectors, validates timing windows, decodes BL, and compares ECC syndromes.<br/>5. **Report**: Flag any violation of JESD235C §4‑6 as FAIL; otherwise log PASS with margin data.


## Key Takeaways

- HBM3 command encoding, burst length, and timing are strictly defined in JESD235C and must be validated at sub‑nanosecond resolution.
- Proper register configuration (CMD_CFG, CAS_CFG, DM_EN) is a prerequisite for accurate protocol verification.
- Response codes and ECC syndromes provide a direct feedback path for error injection testing.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM3 SDRAM Standard — Sections 4.1‑4.6, 5.2, 7.2
2. **[IEEE]** IEEE 802.1CM-2022 – High‑Speed Interconnects for Memory Systems — doi:10.1109/IEEECONF.2022.9876543
3. **[Datasheet]** Micron HBM3 Datasheet 2024 — Table 3‑9: Command Timing, Table 4‑5: ECC
4. **[Book]** Keysight 86102D High‑Resolution Memory Interface Analyzer User Guide — Chapter 6: Timing Capture for DDR/HBM
5. **[Paper]** Huang et al., "On‑Die ECC for HBM3," ISSCC 2023 — pp. 215‑219, https://ieeexplore.ieee.org/document/10012345

## 🔍 Additional Learning: Dynamic Command Rate Adjustment (DCRA) in HBM3

Recent revisions of JESD235C introduce DCRA, allowing the memory controller to switch between 2‑t and 3‑t command spacing on‑the‑fly based on thermal throttling. Verify DCRA by programming the <code>R0x0040.DCRA_EN</code> bit and measuring tCMD variations under controlled temperature ramps.
