# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Sunday, May 17 2026*

*Module 1.1 — Foundations*

## Die Stack Overview

HBM (High‑Bandwidth Memory) consists of multiple DRAM dies bonded face‑to‑face on a silicon interposer. A typical HBM2E stack contains 8‑12 dies, each 1 mm × 1 mm, with a total stack height ≈ 200 µm. The stack is mounted on an interposer that provides TSV (Through‑Silicon Via) connections to the logic die and peripheral I/O.
Key parameters:
- **Die count**: 8 (HBM2), 12 (HBM2E), up to 16 (future HBM3)- **Die density**: 4 Gb per die (HBM2), 8 Gb per die (HBM2E)- **Pitch**: 45 µm TSV, 28 µm interconnect pitch on the interposer- **Operating voltage**: 1.2 V nominal (HBM2), 1.1 V (HBM3)

## Channel Architecture

Each HBM stack is divided into independent **channels**. A channel is a 128‑bit wide data path (plus 16‑bit ECC) and contains its own command/address bus (16‑bit) and clock domain.
Typical configurations:
- HBM2: 4 channels per stack, each 128‑bit data + 16‑bit ECC = 144‑bit total- HBM2E: 8 channels (two channels per die pair) – still 128‑bit effective data per channel- HBM3: 8 channels, but each can be split into two 64‑bit pseudo‑channelsAll channels share a common reference clock (e.g., 1.6 GHz for HBM2) but are clock‑synchronised via the PHY on the interposer.


## Pseudo‑Channel Concept

JEDEC introduced **pseudo‑channels** in JESD235C to increase flexibility for logical partitioning without adding physical I/O. A pseudo‑channel is a logical 64‑bit slice of a physical 128‑bit channel, accessed via a `PCFG` register in the DRAM controller.
When enabled:
- Two pseudo‑channels can operate with independent timing parameters (e.g., `tRCD`, `tRP`)- Address mapping uses bits `A[15:0]` for pseudo‑channel selection- Testing requires separate eye‑pattern and jitter analysis per pseudo‑channel because crosstalk differs from full‑width operationIn HBM3, pseudo‑channels are mandatory for **dual‑rank** operation, allowing simultaneous access to two halves of a die while keeping the 128‑bit physical bus.


## Implications for Test and Characterization

Senior test engineers must consider the following when building ATE test programs:
- Each physical channel needs a dedicated high‑speed I/O pair on the tester (e.g., Keysight M9495A). For pseudo‑channels, the same pair is reused but with distinct timing vectors.- Eye‑diagram specifications are defined per channel: `JESD235C 5.4.1` mandates ≥ 125 ps UI eye opening at 2 Gb/s per lane.- TSV‑to‑interposer resistance and inductance affect channel skew; measure using `DCV` and `ACR` tests on each die pair.- Channel‑to‑channel crosstalk is limited to –45 dB (max) per JESD235C 7.2; pseudo‑channel isolation is tighter (‑50 dB) because the same physical bus is time‑multiplexed.

## Key Registers and Timing Parameters

Relevant DRAM mode registers (per JEDEC JESD235C):
- `MR0[0:2]` – CAS latency (`tCL`) selection- `MR1[3:5]` – Write latency (`tWL`)- `MR2[0]` – Pseudo‑channel enable (0 = disabled, 1 = enabled)- `PCFG[7:0]` – Pseudo‑channel configuration (maps logical channel IDs to physical lanes)Typical timing for HBM2E at 2 Gb/s per lane:
- `tRCD` = 17 ns- `tRP` = 18 ns- `tRFC` = 260 ns (full stack)

## Key Takeaways

- HBM stacks are built from multiple thin DRAM dies on an interposer, each die pair forming a physical 128‑bit channel.
- Pseudo‑channels are logical 64‑bit subdivisions of a 128‑bit channel, controlled via MR/PCFG registers, enabling independent timing per half‑channel.
- Testing must address both physical channels and pseudo‑channels: separate vectors, eye‑diagram compliance, and crosstalk limits per JESD235C.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Standard — Section 4.2 (Channel Architecture), 5.4.1 (Eye Diagram), 7.2 (Crosstalk), 9.3 (Pseudo‑Channel Registers)
2. **[JEDEC]** JEDEC JESD235D – HBM3 Specification — Chapter 6 (Dual‑Rank & Pseudo‑Channel Operation)
3. **[IEEE]** M. Liu et al., “Design and Test of 8‑Channel HBM2E Interposer,” IEEE Transactions on Components, Packaging and Manufacturing Technology, 2022 — doi:10.1109/TCPMT.2022.3156789
4. **[Datasheet]** SK Hynix HBM2E Datasheet (2023) — Table 3‑4: Timing Parameters, Table 5‑1: Stack Organization
5. **[Web]** Keysight M9495A 5‑GSa/s 48‑Channel ATE User Manual — Section 2.3 – Mapping HBM Channels to Tester Resources
