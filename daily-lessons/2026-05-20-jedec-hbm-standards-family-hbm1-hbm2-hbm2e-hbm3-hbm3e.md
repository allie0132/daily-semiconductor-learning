# JEDEC HBM Standards Family: HBM1 through HBM3e

*Wednesday, May 20 2026*

*Module 1.2 — Foundations*

## JEDEC JESD235 and the HBM Standard Lineage

The HBM standard family is governed by JEDEC under the JESD235 series. Each generation introduces a new revision: JESD235 (HBM1), JESD235A (HBM2), JESD235B (HBM2e), JESD235C (HBM3), and the forthcoming HBM3e addendum. Understanding which revision applies to a device under test is the first decision point in any HBM test program — register maps, timing parameters, mode register fields, and protocol state machines all differ across generations.

## HBM1 — The Foundation (JESD235, 2013)

HBM1 introduced the 1024-bit wide interface organized as 8 channels × 128-bit, with a maximum of 4 DRAM dies per stack (4 GB). Signaling is CMOS-level (not differential), running at 1 Gbps per pin, yielding 128 GB/s peak bandwidth per stack. VDD is 1.2 V; VDDQ is 1.2 V. HBM1 used a simple row-column command structure with no pseudo-channel mode. From a test perspective, HBM1 stacks are fully tested at wafer sort before integration — a KGD requirement driven by the irreversibility of TSV bonding. Key JEDEC reference: JESD235, Section 3 (electrical specifications) and Section 6 (AC timing).

## HBM2 and HBM2e — Doubling Bandwidth (JESD235A/B)

HBM2 (JESD235A, 2016) doubled the per-pin data rate to 2 Gbps while keeping the 1024-bit bus, achieving 256 GB/s per stack. Die count increased to 8 dies per stack (8 GB), and pseudo-channel mode was introduced: each 128-bit channel is subdivided into two 64-bit pseudo-channels operating semi-independently, enabling finer-grained row activation and improving effective bandwidth utilization. VDD dropped to 1.2 V / VDDQ 1.2 V (unchanged), but power efficiency per bit improved significantly. HBM2e (JESD235B, 2019) extended the data rate to 3.2 Gbps (410 GB/s per stack) and allowed up to 16 DRAM dies and 16 GB per stack. New mode registers (MR4, MR8) were added for per-die temperature readout (CATTRIP threshold, TEMP_SENSOR). Test implication: pseudo-channel addressing must be validated independently — row hits in one pseudo-channel do not guarantee hits in the paired pseudo-channel.

## HBM3 — Protocol Overhaul (JESD235C, 2022)

HBM3 is a significant architectural revision. Per-pin rate increases to 6.4 Gbps, delivering 819 GB/s per stack (32 GB capacity). The channel count doubles from 8 to 16, each 64-bit wide — the pseudo-channel split is now native to the base channel definition rather than an overlay. Command encoding changes substantially: HBM3 uses a packetized command/address structure with dedicated command and address word (CAWORD) timing, replacing the HBM2 row/column command approach. New features include: link ECC (SECDED per pseudo-channel), per-channel CATTRIP, refresh management improvements (tREFI2 and per-bank refresh), and RFM (Refresh Management) support for rowhammer mitigation. VDD/VDDQ is now 1.1 V. Mode register space expands to MR0–MR15 with mandatory readback verification at initialization. The JEDEC JESD235C Section 4 defines the new state machine with Init, Idle, Active, Refresh, and Power-Down states — all must be exercised in a compliant test program.

## HBM3e — Current Production Node

HBM3e is an addendum to JESD235C that pushes per-pin rates to 9.6 Gbps (1.2 TB/s per stack) with up to 36 GB capacity (12-die stacks). SK Hynix and Micron both ship HBM3e for AI accelerator platforms (NVIDIA H200, AMD MI300X). The electrical interface is backward-compatible with HBM3 at the package level but requires tighter timing margins — tDQSCK and tDS/tDH specs tighten by ~15% vs HBM3. From a test standpoint, HBM3e devices require ATE systems capable of driving 9.6 Gbps DRAM patterns with sub-5 ps RMS jitter on the data strobe. Teradyne UltraFLEX+ and Advantest T2000-HBM3 loadboards are the current production platforms.

## Key Takeaways

- Each HBM generation maps to a specific JEDEC JESD235 revision — confirm the revision before writing test plans
- Pseudo-channel mode was introduced in HBM2 (JESD235A) and became the native channel width in HBM3
- HBM3 introduced packetized CA encoding, link ECC, and RFM — all require new test pattern suites vs HBM2e
- HBM3e runs at 9.6 Gbps per pin and demands sub-5 ps strobe jitter from ATE systems
- VDD trended from 1.2 V (HBM1/2) to 1.1 V (HBM3/3e) — verify loadboard power delivery specs per generation

## References

1. **[JEDEC]** JESD235 — High Bandwidth Memory (HBM) DRAM Standard, 2013
2. **[JEDEC]** JESD235A — HBM2 Standard, 2016, Section 3.4 (pseudo-channel definition)
3. **[JEDEC]** JESD235B — HBM2e Standard, 2019, Section 4.2 (MR4 temperature sensor)
4. **[JEDEC]** JESD235C — HBM3 Standard, 2022, Section 4 (state machine), Section 6 (AC timing)
5. **[Paper]** Jeddeloh, J. & Keeth, B. — "Hybrid Memory Cube New DRAM Architecture Increases Density and Bandwidth", IEEE VLSI 2012
6. **[Datasheet]** SK Hynix HBM3e Product Brief, 2024 — 9.6 Gbps, 36 GB per stack specs

## 🔍 Additional Learning: RFM (Refresh Management) — Rowhammer Mitigation in HBM3

HBM3 introduced Refresh Management (RFM) commands as a mandatory mechanism to mitigate rowhammer-style bit-flip attacks in high-density DRAM stacks. The host controller tracks row activation counts via an Alert_n assertion from the DRAM when a per-bank activation threshold (RAAIMT — Rowhammer Activation Alert Injection Maximum Threshold) is reached. Upon receiving Alert_n, the controller must issue an RFM command within tRFMreq (max 180 ns), which triggers targeted refresh of victim rows adjacent to the aggressor row. In HBM3 test programs, RFM compliance requires injecting sustained activation bursts above RAAIMT on a single bank and verifying Alert_n assertion timing and proper victim-row refresh — a test not present in any prior HBM generation.
