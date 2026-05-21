# HBM Electrical Interface: AWORD, DWORD, Cmd/Addr

*Thursday, May 21 2026*

*Module 1.5 — Foundations*

## 1. AWORD and DWORD Definitions

HBM uses two parallel data channels per stack:
- **AWORD** (Address Word) – 128‑bit wide, carries address and command information.- **DWORD** (Data Word) – 128‑bit wide, carries payload data for read/write operations.Both are synchronous to the same clock domain (CK), but AWORD is multiplexed with command/info symbols while DWORD carries the payload data stream.


## 2. Command/Address Signal Mapping on AWORD

The AWORD lane is subdivided into 8 sub‑words of 16 bits each. JEDEC JESD235C defines the mapping:
- Bits&nbsp;[127:120] – `CKE` (Clock Enable)- Bits&nbsp;[119:112] – `CS_N` (Chip Select)- Bits&nbsp;[111:96] – `CMD[15:0]` (Command opcode)- Bits&nbsp;[95:0] – `ADDR[95:0]` (Row/Column address fields)All signals are DDR, sampled on both clock edges. The command opcodes are defined in Table 5 of JESD235C (e.g., 0x01 = ACTIVATE, 0x02 = READ, 0x03 = WRITE).


## 3. Timing Relationship between AWORD and DWORD

Key timing parameters (all in nanoseconds unless noted) are:
- **tCK** – Clock period, typically 0.8 ns for DDR4‑HBM (1.25 GHz). Both AWORD and DWORD toggle on each CK edge.- **tAA** – Address to data latency (tRCD in DDR terminology); JEDEC specifies 6 CK cycles for HBM2E.- **tDQSQ** – Data‑strobe qualification window; must align within ±0.25 tCK of the data edge.During a read, the controller drives AWORD with the command/address, then after `tAA` the DWORD lanes present data aligned to the DQ/DQS pair. Write operations follow the same latency before the controller must present data on DWORD.


## 4. Signal Integrity Considerations

Because AWORD carries high‑frequency command transitions, impedance control and length matching are critical:
- Target differential impedance: 100 Ω ± 10 % for both AWORD and DWORD pairs (JEDEC JESD235C §6.3).- Skew budget: **±5 ps** intra‑pair, **±20 ps** inter‑pair across the 8‑bit sub‑words.- Use back‑drill or micro‑via stitching to minimize stub resonances above 20 GHz.ATE probing must respect these limits; most modern HBM test platforms (e.g., Advantest T3‑700) provide `±2 ps` jitter control and on‑board pre‑emphasis to meet the spec.


## 5. Practical ATE Configuration Example

Example setup for an Advantest V6000 testing a 4‑stack HBM2E device:
- Clock source: 1.25 GHz DDR, `CK` and `CK#` driven with 20 mV differential swing.- Pattern generation: 128‑bit AWORD vector composed of `{CKE,CS_N,CMD,ADDR}` fields using `STIL` syntax `DW = {CKE,CS_N,CMD,ADDR}`.- Data capture: 128‑bit DWORD captured on both CK edges, applying `DDRIO` mode with 100 % eye‑mask compliance.Verification of `tAA` is performed by inserting programmable delay cycles (0‑15 CK) and checking data eye closure at the required latency.


## Key Takeaways

- AWORD (128 bit) carries command/opcode and address fields; DWORD (128 bit) carries payload data.
- Command/opcode mapping is defined in JESD235C; timing such as tAA = 6 CK cycles governs AWORD‑to‑DWORD latency.
- Signal integrity (impedance, skew, jitter) is tighter on AWORD due to high‑frequency command transitions.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) Standard — Section 4.2, 5.1, 6.3 – command/address mapping, timing, impedance
2. **[JEDEC]** JEDEC JESD79‑4B: DDR4 SDRAM Specification — Used for reference timing parameters (tCK, tRCD) adapted to HBM
3. **[Datasheet]** Advantest V6000 HBM Test Platform User Manual — Chapter 7 – AWORD/DWORD configuration, jitter specs
4. **[IEEE]** J. Lee et al., "Signal Integrity in HBM Stacked Packages," IEEE Transactions on Components, Packaging and Manufacturing Technology, 2023 — doi:10.1109/TCPMT.2023.3268457
5. **[Datasheet]** Samsung HBM2E Datasheet, 2022 — Electrical characteristics, command opcodes, timing tables

## 🔍 Additional Learning: Dynamic Command Width Scaling in HBM3

HBM3 introduces optional 256‑bit AWORD modes that halve command latency by delivering two command words per CK cycle; adoption requires ATE firmware that can generate packed command vectors and verify widened DQS windows.
