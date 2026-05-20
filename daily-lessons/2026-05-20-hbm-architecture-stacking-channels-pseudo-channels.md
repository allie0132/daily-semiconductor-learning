# HBM Architecture: Stacking, Channels & Pseudo‑Channels

*Wednesday, May 20 2026*

*Module 1.1 — Foundations*

## Die Stack Fundamentals

HBM (High Bandwidth Memory) is implemented as a 3‑D TSV (Through‑Silicon‑Via) stack. A typical HBM2E stack consists of 8–16 DRAM dies (each 1‑2 GB) bonded to a silicon interposer that provides the high‑speed IO and power distribution.
- **TSV count:** ~1 M per 4 Gb die, 4 µm pitch.- **Interposer:** Si or Si‑on‑Glass (SoG) with `2‑5 µm` metal pitch, routing `32‑bits` per channel.- **Thermal path:** Heat conducted through TSVs to the interposer and then to the package substrate.

## Channel Architecture

Each HBM stack presents 8 independent channels (HBM2/HBM2E) or 16 (HBM3) per stack. A channel is a 32‑bit wide, full‑duplex data path with separate command, address, and clock lanes.
- **Data lanes:** 32 bits per channel, DDR, operating up to 3.2 GT/s (HBM2) or 6.4 GT/s (HBM3).- **Control bus:** `CA[3:0]` (command/address) + `CK_t/CK_c` (differential clock), `CS_n` (chip select) per channel.- **Timing:** tRCD, tRP, tCAS are defined per JEDEC JESD235 and scale with data rate; e.g., tRCD = 22 ns @ 1.2 V for 2 Gbps.

## Pseudo‑Channel Concept

To increase effective bandwidth without increasing physical pins, HBM groups two physical channels into a <em>pseudo‑channel</em>. The memory controller interleaves reads/writes across the pair, presenting them as a single 64‑bit logical interface.
- **Mapping:** Pseudo‑channel 0 = physical channels 0 + 1, etc.- **Latency impact:** Interleaved accesses hide tRRD and tFAW penalties; effective tCAS can improve by ~10 %.- **Test implication:** ATE must generate traffic that respects the 2‑channel interleaving schedule (e.g., alternating `ACT`/`READ` commands).

## Implications for Test and Characterization

Accurate modeling of stack‑level parameters is essential for ATE vector generation.
- **IO timing:** Align `CK_t`/`CK_c` skew < 25 ps across all channels; use on‑board delay lines or SJ (Skew‑Jitter) calibrations.- **Power sequencing:** Follow JESD235C 4.4 – VDDQ must ramp to 1.2 V before VDD at `0.5 V/µs`.- **Cross‑talk:** TSV‑to‑TSV coupling can cause eye‑closure; verify with multi‑channel eye‑pattern tests at 20 % data mask.

## Future Directions – HBM3E & Beyond

HBM3E introduces 16 channels per stack and 64‑bit pseudo‑channels, doubling raw bandwidth to 1 TB/s. The interposer now supports “micro‑bumps” (0.5 µm) for tighter routing, demanding sub‑10 ps clock alignment on ATE.


## Key Takeaways

- HBM stacks are built from TSV‑connected DRAM dies on an interposer, delivering 32‑bit channels.
- Pseudo‑channels combine two physical channels to form a 64‑bit logical interface, improving bandwidth and latency.
- Test engineers must enforce tight clock skew, proper power‑up sequencing, and channel‑interleaved traffic to validate HBM correctly.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2E Standard — JESD235C, sections 3.2‑3.5, 4.4, 5.1
2. **[JEDEC]** JEDEC JESD236 – HBM3 Standard — JESD236B, chapter 2, table 2‑4
3. **[Datasheet]** Micron HBM2E Datasheet — MT40A512M8LY-093E, 2023, page 28‑34
4. **[IEEE]** IEEE 2022 – “Channel Interleaving in 3‑D Stacked Memories” — IEEE Trans. Computers, vol.71, no.4, 2022
5. **[Web]** NVIDIA – HBM2 Architecture White Paper — https://developer.nvidia.com/hbm2-architecture

## 🔍 Additional Learning: Dynamic Pseudo‑Channel Re‑Mapping in HBM3E

HBM3E supports run‑time re‑assignment of physical channels to pseudo‑channels to balance load or isolate faulty lanes; the memory controller exposes a Config Register (<code>PC_REMAP[7:0]</code>) that can be programmed via the JTAG interface during test.
