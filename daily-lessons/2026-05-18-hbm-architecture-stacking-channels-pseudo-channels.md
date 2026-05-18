# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Sunday, May 17 2026*

*Module 1.1 — Foundations*

## 1. Die‑Stack Fundamentals

HBM (High‑Bandwidth Memory) consists of multiple DRAM dies bonded vertically on an interposer using **micro‑bumps** (typically 25 µm pitch). A standard HBM2 stack contains 4, 8, or 12 dies (HBM2E up to 16). Each die is a monolithic `DDR4‑like` array with a `2 Gb‑4 Gb` capacity, accessed through a common TSV (through‑silicon via) back‑end.
- **TSV count:** 256–512 per die, providing a parallel data path to the IO <em>logic die</em>.- **Logic die:** Hosts the `DRAM controller` and routes all channel I/O to the silicon interposer.- **Thermal stack:** Heat spreads via the interposer copper, so test setups must monitor die‑level temperature (e.g., thermal resistance ≈ 0.8 °C/W per stack).

## 2. Channel Architecture

Each HBM stack is subdivided into **four independent channels**. A channel comprises:
- 128‑bit wide data bus (16 × 8‑bit lanes)- 16‑bit address bus + 2‑bit bank address- 2‑bit command bus (ACT, PRE, RD, WR)All channels operate concurrently, giving a native `256‑bit` aggregate width per stack (4 × 128 bits). The channel clock (CK) runs up to 2 GHz for HBM2, yielding 256 GB/s per stack (2 Gb × 4 channels × 2 GHz ÷ 8).


## 3. Pseudo‑Channels (Logical Segmentation)

To increase flexibility, the JEDEC spec defines **pseudo‑channels** – logical subdivisions of a physical channel that share the same physical pins but are addressed separately.
- Each pseudo‑channel can be enabled/disabled via the `MODE_REG` register (address `0x1C`), allowing - Partial‑bandwidth operation (e.g., half‑rate mode for power‑saving)- Independent timing parameters: `tRCD`, `tRP`, `tRAS` can be programmed per pseudo‑channel using `MODE_REG` bits 6–9.In testing, pseudo‑channel isolation is verified by writing a unique pattern to each logical segment and confirming no cross‑talk on the shared pins.


## 4. Impact on Test Architecture

When configuring ATE for HBM, the following must be mapped:
- **Channel groups:** 4 groups per stack, each requiring a dedicated 128‑bit high‑speed I/O vector (e.g., Keysight 33600A VSA). - **Pseudo‑channel timing:** Use JEDEC‑defined `MR0‑MR3` sequences to toggle modes; verify `tRCD` and `tRAS` adjustments per pseudo‑channel.- **Signal integrity:** Micro‑bump inductance (~10 nH) and TSV capacitance (~0.1 pF) produce a first‑order roll‑off at ~5 GHz; employ on‑board de‑embedding and eye‑diagram analysis.

## 5. Example: HBM2E 12‑Die Stack

HBM2E (JEDEC JESD235E) extends the stack to 12 dies, each 8 Gb. The aggregate bandwidth reaches 460 GB/s (12 Gb × 4 channels × 2.2 GHz ÷ 8). The logic die adds an extra `DRAM‑PHY` block to support the additional frequency margin, and pseudo‑channel granularity remains 4 per stack.
Testing tip: Use a `BURST_LENGTH=8` pattern at the max clock and monitor `DQ` eye width; target > 0.7 UI opening per JEDEC eye‑spec for HBM2E.


## Key Takeaways

- HBM stacks consist of vertically bonded DRAM dies and a dedicated logic die, with TSVs providing parallel data paths.
- Four physical channels per stack give 256‑bit aggregate width; each channel is 128‑bit data + control.
- Pseudo‑channels are logical partitions within a physical channel, programmable via MODE_REG and useful for power‑saving and test isolation.
- ATE configuration must provide separate 128‑bit high‑speed vectors per channel and support JEDEC timing adjustments per pseudo‑channel.

## References

1. **[JEDEC]** JEDEC JESD235E – High Bandwidth Memory (HBM2E) Standard — JESD235E, 2022, sections 4.1‑4.5, 6.3
2. **[JEDEC]** JEDEC JESD230 – High Bandwidth Memory (HBM) Standard — JESD230, 2015, chapter 3 (Channel Architecture)
3. **[IEEE]** M. K. Sadek et al., “Design and Test of 8‑Die HBM2 Stacks,” IEEE Transactions on Components, Packaging and Manufacturing Technology, vol. 9, no. 4, 2020. — doi:10.1109/TCPMT.2020.2980192
4. **[Datasheet]** SK Hynix HBM2E 8‑Gb/Die Datasheet — Hynix, 2023, pinout, timing tables, pseudo‑channel register map
5. **[Web]** Keysight 33600A High‑Speed Vector Signal Analyzer – Application Note 1172 — https://www.keysight.com/au/en/assets/7018-02857/application-notes/1172.pdf

## 🔍 Additional Learning: Emerging TSV‑Co‑Design for 3D‑IC Test

Recent research (IEEE/ISSCC 2024) combines TSV layout co‑design with on‑die built‑in self‑test (BIST) to reduce test time for >12‑die HBM stacks. Engineers should watch for vendor‑released BIST‑enabled logic dies that embed pattern generators, enabling at‑speed pseudo‑channel validation without external ATE stimulus.
