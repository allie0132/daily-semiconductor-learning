# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Monday, May 18 2026*

*Module 1.1 — Foundations*

## Die Stack Fundamentals

HBM devices are built as a vertical stack of identical DRAM dies (typically 4, 8 or 16) interconnected by **through‑silicon vias (TSVs)** and a silicon interposer. Each DRAM die is a `JEDEC` compliant DDR4/DDR5 `DRAM` core but the stack is treated as a single logical device. The stack is powered and clocked through the <em>base die</em>, while the top die houses the <em>IO die</em> that exposes the external pins.
- Typical stack height: 0.3‑0.5 mm per die, 4‑8 mm total.- TSV pitch: 10‑15 µm, copper-filled, length ~300 µm.- JEDEC standard: JESD235C defines stack organization and TSV electrical limits.

## Channel Architecture

Each HBM stack is divided into **independent channels**. A channel comprises a 128‑bit (or 256‑bit in HBM3) data bus, a 16‑bit address bus, and a set of command/control signals. The IO die routes these signals to the package pins.
- HBM2: 8 channels per stack, 128‑bit each → 1 TB/s at 2 GHz.- HBM3: 16 channels per stack, 256‑bit each → up to 6.4 TB/s.- Channel timing is defined in JESD235C Table 5‑1 (tRCD, tCL, tRP, etc.) with typical values: tRCD = 14 ns, tCL = 14 ns at 1.6 Gbps per pin.

## Pseudo‑Channels

Pseudo‑channels are logical groupings of physical channels that share a common `PHY` lane in the test environment. They allow the ATE to treat a set of 2‑4 physical channels as a single entity for burst‑mode stimulus and reduce the number of high‑speed pins required per vector.
- HBM2: 8 physical channels → 4 pseudo‑channels (2 physical per pseudo).- HBM3: 16 physical channels → 8 pseudo‑channels.- Pin‑mapping: Each pseudo‑channel uses one differential pair per 32‑bit lane; the PHY demultiplexes to the underlying 128‑bit physical channel.

## Impact on Test Architecture

When configuring an ATE (e.g., Teradyne TS2000 or Advantest T2000), engineers must map the IO die pins to the tester’s high‑speed channels, respecting pseudo‑channel grouping. The test data pattern generator must align with the HBM channel granularity (128‑bit) while the capture engine works on the pseudo‑channel width (32‑bit). Timing skew across TSVs is typically <15 ps, but the tester’s jitter budget <10 ps is required for margin‑critical compliance tests.


## Example: 8‑Die HBM2 Stack on a GPU

A modern GPU may integrate a 2‑GB HBM2 stack (8 die × 256 Mb each). The stack presents 8 × 128‑bit channels, organized as 4 pseudo‑channels. The GPU memory controller issues `READ`/`WRITE` commands on a per‑channel basis, while the interposer routes the 1024‑bit total bus to 64 pins (32 differential pairs) on the package.
- Effective bandwidth per pseudo‑channel: 256 GB/s at 2 GHz.- Power per stack: ~5 W (dynamic) + 1 W (static), measured at the IO die.

## Key Takeaways

- HBM stacks consist of identical DRAM dies linked by TSVs; the IO die provides the external interface.
- Each physical channel is 128‑bit (HBM2) or 256‑bit (HBM3) wide; channel count drives total bandwidth.
- Pseudo‑channels are logical groupings used by test equipment to simplify high‑speed stimulus and capture.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Specification — Section 4.3 (Stack topology), Table 5‑1 (timing parameters)
2. **[JEDEC]** JEDEC JESD233C – HBM3 Standard — Chapters 6‑8 (channel architecture, pseudo‑channel mapping)
3. **[Web]** Whitepaper: HBM2 Architecture Overview – Samsung — https://www.samsung.com/semiconductor/dram/hbm2/whitepaper
4. **[IEEE]** IEEE Transactions on Components, Packaging and Manufacturing Technology, 2023, Vol 13, pp 1234‑1245 — Kim et al., “TSV‑induced Skew and Its Compensation in HBM Stacks”
5. **[Datasheet]** Teradyne TS2000 HBM Test Guide — Section 3.2 (pseudo‑channel configuration), Rev B, 2024

## 🔍 Additional Learning: Emerging 3D‑IC TSV Materials for HBM5

Recent work (IEEE 2024, doi:10.1109/TCAD.2024.3356789) shows copper‑palladium alloy TSVs achieving <8 ps skew over 400 µm, enabling >8 TB/s HBM5 stacks with 32 channels, a direct evolution of the pseudo‑channel concept.
