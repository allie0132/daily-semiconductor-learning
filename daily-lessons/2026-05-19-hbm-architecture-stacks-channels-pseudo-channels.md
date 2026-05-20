# HBM Architecture: Stacks, Channels & Pseudo‑Channels

*Tuesday, May 19 2026*

*Module 1.1 — Foundations*

## Physical Stack Overview

HBM memory consists of multiple silicon dies bonded in a vertical stack using micro‑bump TSVs. A typical HBM2‑E device contains 8‑16 DRAM dies plus a separate logic die (IO and command decoder). The stack is encapsulated in an interposer or silicon bridge that routes high‑speed signals to the host processor.
- **Die count:** 8, 12, or 16 DRAM dies (each 1 Gb‑2 Gb) plus a 1 Gb logic die.- **TSV pitch:** 2.5 µm (typical) with 128‑256 TSVs per die for power/ground and 1024‑2048 data TSVs.- **Interposer:** Si‑interposer (e.g., 10 µm pitch) carries the `DVDD`, `VDDQ`, and high‑speed differential pairs.

## Channel Architecture

Each HBM stack is divided into independent **channels**. A channel is a 128‑bit (16‑byte) wide data path that operates at up to 3.2 GT/s per pin (HBM2‑E). The channel consists of:
- 16 data lanes (8‑bit per lane) per direction.- 2 address lanes and 2 command lanes (CK/CK#). - Separate VREF and ODT control.HBM2‑E typically provides 8 channels per stack, delivering up to 8 × 256 GB/s = 2 TB/s aggregate bandwidth.


## Pseudo‑Channel Concept

To simplify host controller design, the JEDEC spec defines **pseudo‑channels** as logical groupings of two physical channels that share a common command/address bus. This reduces the number of CA pins from 2 × 8 = 16 to 8, while maintaining independent data lanes.
- Each pseudo‑channel still provides 256‑bit effective data width (two 128‑bit channels).- Timing parameters (tRCD, tRP, tRC) are applied per physical channel; pseudo‑channel alignment must be verified in test.- Memory controllers may interleave accesses across the two physical channels to balance load and improve eye‑diagram margin.

## Signal Integrity & Timing Considerations

High‑speed operation across the interposer requires careful control of loss and jitter:
- `tCK` for HBM2‑E is as low as 0.78 ns (1.28 GHz). - Eye‑width specifications: 70 % UI aperture, 30 % UI jitter tolerance (JESD235C §4.3).- Impedance control: 50 Ω differential pair, ±5 % tolerance.- Termination: On‑die termination (ODT) programmable per channel; must be calibrated during BIST.

## Testing Implications

From a test engineer perspective, the stack‑level architecture dictates test flow:
- Per‑die BIST (March, MARCH‑C) runs on each DRAM die before stack integration.- Channel‑level stress tests (e.g., BLISS, per‑channel pattern) validate timing margins.- Pseudo‑channel validation requires coordinated CA sequencing across the paired channels; mismatch is a common failure mode.

## Key Takeaways

- HBM stacks are composed of multiple DRAM dies plus a logic die bonded via TSVs on an interposer.
- Each physical channel is a 128‑bit wide data path; up to 8 channels give multi‑TB/s bandwidth.
- Pseudo‑channels logically merge two physical channels to reduce CA pins while preserving data width.
- Signal integrity (impedance, ODT, jitter) must be validated per channel and per pseudo‑channel.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2E Specification — Section 4.2‑4.5, 2022
2. **[JEDEC]** JEDEC JESD79-4 – HBM2 Specification — Rev. 1.0, 2015
3. **[IEEE]** M. Sharf et al., "HBM2E Stack Design and Testing," IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 13, no. 4, 2023. — doi:10.1109/TCPMT.2023.3290145
4. **[Datasheet]** Micron HBM2E 8‑Gb/s 1.2 V DDR Memory Datasheet — MT53E256M32D2NL‑1G, Rev B, 2023
5. **[Web]** AMD Infinity Fabric and HBM Integration Guide — https://developer.amd.com/hbm‑integration‑guide

## 🔍 Additional Learning: HBM3 Pseudo‑Channel Enhancements

HBM3 introduces optional 4‑lane pseudo‑channels, allowing eight physical channels to be grouped into four logical units with independent CA lanes, improving scalability for 8 TB/s classes of GPUs and AI accelerators.
