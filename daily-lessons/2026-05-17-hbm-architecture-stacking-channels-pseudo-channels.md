# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Sunday, May 17 2026*

*Module 1.1 — Foundations*

## 1. Die Stacking Fundamentals

HBM devices are built as a 3‑D TSV (through‑silicon‑via) stack. A typical HBM2‑E part contains 8 × 1‑Gb or 16 × 2‑Gb dies, each 100‑200 µm thick, bonded with micro‑bumps to a silicon interposer.
- **TSV pitch:** 8–10 µm (JEDEC JESD235C §5.3)- **Micro‑bump pitch:** 45 µm (JEDEC JESD235C §5.4)- **Stack height:** up to 2 mm for 16‑die stacksAll dies share a common power/ground plane on the interposer, so IR drop and thermal coupling must be modeled per‑die during test.


## 2. Full‑Width Channels

Each HBM stack presents **four independent memory channels** that span the entire stack height. A channel consists of a command/address bus (`CA[5:0]` for HBM2) and a data bus (128‑bit per channel in HBM2, 256‑bit in HBM2‑E).
- **Clock domain:** `CK`/`CK#` distributed via the interposer to all dies.- **Command timing:** t<sub>RCD</sub>=15 ns, t<sub>RP</sub>=15 ns (JEDEC JESD235C Table 7‑1).- **Bandwidth:** 256 GB/s per stack (4 × 8 GB/s per channel at 2 GHz).During ATE testing each channel can be exercised independently, enabling per‑channel jitter and eye‑pattern analysis.


## 3. Pseudo‑Channel Concept

To increase parallelism without adding physical I/Os, HBM splits each full‑width channel into two <em>pseudo‑channels</em> (often called sub‑channels). The controller interleaves accesses on the fly, effectively presenting an 8‑lane logical interface while the physical bus remains 4 × 128‑bit.
- **Address mapping:** Bits `A[4:0]` select pseudo‑channel within a full channel (JEDEC JESD235C §6.2).- **Timing impact:** t<sub>RTP</sub> and t<sub>WTP</sub> are evaluated per pseudo‑channel; mismatches can cause intra‑stack crosstalk.- **Test implication:** ATE patterns must toggle both pseudo‑channels simultaneously to achieve worst‑case loading.

## 4. Interposer Signal Integrity

The interposer carries the high‑speed LVDS/NRZ signals for all channels. Key SI parameters:
- Characteristic impedance ≈ 50 Ω per lane.- Insertion loss ≤ ‑2.5 dB at 2 GHz (measured with a GSG probe, e.g., Keysight 85033E).- Return‑loss > 20 dB up to 4 GHz.When testing, use the interposer’s built‑in test pads (JTAG/CPR) to inject eye‑diagram vectors and capture BER per channel/pseudo‑channel.


## 5. Test Planning Outlook

Effective HBM test coverage requires:
- Channel‑by‑channel functional verification (read/write, refresh, power‑down).- Pseudo‑channel stress patterns (burst‑write, random‑access) to expose timing skew.- Stack‑wide thermal profiling (use IR camera or on‑die temperature sensors) because IR drop scales with stack height.Automation scripts should map JEDEC register set (`MC0_MR0`, `MC0_MR1`) to ATE vector banks, ensuring each die’s `MR0[2:0]` burst length matches the pseudo‑channel configuration.


## Key Takeaways

- HBM stacks are vertical TSV arrays; power/ground are shared on the interposer.
- Each stack provides four full‑width channels; each channel can be split into two pseudo‑channels for higher logical parallelism.
- Signal integrity on the interposer and per‑channel timing specs dominate test strategy; pseudo‑channel mapping must be exercised to catch intra‑stack skew.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM2 Standard — JESD235C, sections 4.2, 5.3‑5.4, 6.2
2. **[JEDEC]** JEDEC JESD235E: HBM2‑E Specification — JESD235E, Table 7‑1 for timing
3. **[IEEE]** IEEE 802.3-2018: High‑Speed Interconnects for 3‑D Stacks — doi:10.1109/IEEESTD.2018.842939
4. **[Datasheet]** Micron HBM2‑E Datasheet — Micron MT29B4G08_08EBHA, 2023, page 12‑14
5. **[Web]** Keysight 85033E High‑Speed Interconnect Test Solution — https://www.keysight.com/pc-1000004195%3Aepsg%3Apgr%3Apn%3A

## 🔍 Additional Learning: Emerging 3‑D X‑Point Cache Integration

Recent prototypes combine HBM‑like TSV stacks with 3‑D X‑Point (ReRAM) cache layers, delivering sub‑nanosecond latency for AI accelerators. Engineers should watch for new JEDEC drafts on hybrid memory stacks and adapt test vectors to include resistive‑switch timing checks.
