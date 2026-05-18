# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Monday, May 18 2026*

*Module 1.1 — Foundations*

## 1. Die Stacking Fundamentals

HBM (High‑Bandwidth Memory) uses vertical 3‑D integration of DRAM dies bonded through **TSVs (Through‑Silicon Vias)** and micro‑bumps to a silicon interposer. A typical HBM2‑X module comprises 4‑8 DRAM stacks; each stack contains 8‑16 dies (e.g., 8 × 1 Gb per die for a 1 TB/s module).
Key parameters:
- `Die thickness`: ~100 µm per die, total stack height 0.8–1.2 mm.- `TSV pitch`: 9–12 µm, `via diameter` 5 µm, supporting >3 Gb/s per pin.- `Interposer material`: Si, with `die‑to‑die routing` of 25 µm line/space.JEDEC JESD235C specifies the mechanical stack limits and thermal impedance budgets (≤ 2 °C/W per stack).


## 2. Channel Architecture

Each HBM stack exposes **four independent memory channels**. A channel consists of a `DQ` bus (128 bits) and accompanying `CK/CK#` (clock) and `CMD` signals. The nominal data rate per channel is 2–3.2 GT/s for HBM2 and up to 6.4 GT/s for HBM2‑E.
Channel breakdown per stack:
- `128‑bit data path` → 16 bytes per transfer.- `4‑bit CAS, RAS, WE, ODT` control per channel.- Latency defined in JEDEC JESD235C §4.3: t<sub>RCD</sub>≈12 ns, t<sub>RP</sub>≈12 ns, t<sub>CL</sub>≈16 ns at 1.6 Gb/s.In testing, each channel is probed as a separate high‑speed differential pair, requiring ≤ 15 ps skew matching on the ATE.


## 3. Pseudo‑Channel Concept

To double effective bandwidth without increasing physical pins, HBM splits each physical channel into two **pseudo‑channels**. The memory controller interleaves accesses between them using the `CA[3:0]` address bits as a selector.
Characteristics:
- Each pseudo‑channel half‑width: 64 bits (8 bytes).- Timing identical to full channel; however, `tRCD` and `tRP` are shared, so effective burst length is halved per pseudo‑channel.- JEDEC JESD235C §5.2 defines the `PC_EN` signal used in HBM2‑E to enable pseudo‑channel mode.For ATE, pseudo‑channels require an extra `PC_EN` vector and careful alignment of the 64‑bit data eye across the two sub‑buses.


## 4. Implications for Test Strategy

When configuring ATE for HBM:
- Map each of the four physical channels to separate high‑speed ports; for pseudo‑channel mode, split the port into two 64‑bit sub‑ports.- Apply JEDEC‑defined `INIT` sequence (JESD235C §6.4) with `MODE_REG` writes to enable/disable pseudo‑channels and set `TC` (training count) parameters.- Validate TSV integrity via `IDDQ` and `JTAG BIST` before high‑speed traffic.- Monitor per‑channel eye diagrams; each must meet 80 % eye‑height and ≤ 20 ps jitter (per IEEE 1588‑2008 ATE spec).

## 5. Sample Register Map (HBM2‑E)

Key registers used to control channels and pseudo‑channels:
- `0x0010 – MODE`: bit[0] = CH0_EN, bit[1] = CH1_EN, … bit[7] = PSEUDO_EN.- `0x0024 – TIMING_CTRL`: fields for `tRCD`, `tRP`, `tCL`.- `0x0038 – DLL_CONF`: sets `DLL_EN` per channel, critical for DQ alignment.These registers are programmed via the JEDEC-standard `MDQ` (Management Data Queue) interface on pins `MDQ[0:3]`.


## Key Takeaways

- HBM stacks are built from DRAM dies linked by TSVs on a silicon interposer, with strict thermal and mechanical limits.
- Each stack provides four 128‑bit physical channels; each channel can be split into two 64‑bit pseudo‑channels for higher effective bandwidth.
- Test engineers must configure ATE ports per physical channel, manage the PC_EN signal for pseudo‑channel mode, and obey JEDEC timing specs for reliable eye‑measurements.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory (HBM) Specification — Section 4.2‑5.3, 2021
2. **[Paper]** HBM2‑E Architecture and Design Guideline — M. Shur et al., IEEE Trans. on VLSI Systems, vol. 30, no. 4, 2022
3. **[IEEE]** TSV‑Based 3D Integration for HBM — K. Liu, IEEE J. of Solid‑State Circuits, 2020
4. **[Datasheet]** Micron 8‑Gb DDR4‑HBM2‑X Datasheet — Micron Tech, Rev 2.4, 2023, www.micron.com
5. **[Book]** High‑Speed Test Strategies for 3D Stacked Memory — J. Kim, "Advanced Semiconductor Test", 2nd ed., 2021, Chap. 7

## 🔍 Additional Learning: Emerging HBM3 Pseudo‑Channel Enhancements

HBM3 introduces a 3‑level pseudo‑channel hierarchy, adding a <code>PC2_EN</code> flag that allows 3‑way interleaving of 42‑bit sub‑buses, increasing per‑stack bandwidth by ~30 % while keeping pin count unchanged.
