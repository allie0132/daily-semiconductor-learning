# HBM Roadmap Beyond HBM4E: Bandwidth & Post‑TSV

*Thursday, Aug 13 2026*

*Module 13.6 — Emerging Technologies & Future Directions*

## JEDEC Committee Work and HBM4E Baseline

The JEDEC JC-42.3 subcommittee maintains the HBM family standards, with HBM4E defined in `JESD236A` (released 2023) extending HBM4 to 6.4 Gbps per pin and 1024‑bit wide I/O.
- Defines timing parameters: **tCK** = 156.25 ps, **tRCD** = 13.75 ns, **tCL** = 14.- Specifies 8‑die stack, 16 GB total capacity, and per‑die TSV pitch of 55 µm.- Introduces optional `DFE` (Decision Feedback Equalizer) registers for high‑speed I/O.

## Bandwidth Scaling Limits – Pin Density, Data Rate, and Thermal

Beyond HBM4E, bandwidth growth is constrained by three interrelated factors:
- **Pin density**: TSV pitch limits I/O count; current 55 µm pitch yields ~1024 pins per die; further scaling requires `≤30 µm</pitch> TSVs or micro‑bump interconnects.- **Data rate ceiling**: Signal integrity and power‑noise coupling limit NRZ to ~8 Gbps; PAM‑4 pushes to ~12 Gbps but doubles comparator power.- **Thermal budget**: Stacked die power density > 15 W/mm² necessitates interposer‑level microfluidic cooling or silicon‑photonic thermal vias.These limits drive the JEDEC exploration of `HBM5` targeting 1.2 TB/s stack bandwidth via 16‑die stacks and 10‑Gbps PAM‑4 I/O.


## Post‑TSV Packaging Technologies – Interposer, FOWLP, and Hybrid Bonding

To circumvent TSV pitch limits, the industry is adopting:
- **Silicon interposer (CoWoS, InFO)**: Provides 2.5 µm line/space routing, enabling >2000 I/O with `≤10 µm` bump pitch.- **Fan‑Out Wafer‑Level Packaging (FOWLP)**: Redistribution layers (RDL) allow die‑to‑die routing without TSVs; used in Samsung’s HBM4E test chips.- **Hybrid bonding (die‑to‑die)**: Direct Cu‑Cu bonds at `≤1 µm` pitch achieve >10 TB/s interfacial bandwidth with minimal latency.JEDEC’s JC‑42.4 task group is drafting a <em>Post‑TSV Interconnect Specification</em> (working title JESD239) to define mechanical, electrical, and test requirements for these alternatives.


## Test Implications for ATE and Built‑In Self‑Test

HBM roadmap evolution impacts ATE architecture in three ways:
- **Channel count**: Moving from 1024‑pin to 2048‑pin interfaces requires ATE cards with ≥4 K pins per site; vendors are releasing modular `Flex‑IO` cards (e.g., Advantest V93000 EXA Scale).- **Signal integrity validation**: PAM‑4 eyes demand `≥30 dB` vertical eye opening; ATE must support `≥20 GS/s` real‑time sampling and `DFE` coefficient loading via `VREF` registers.- **BIST and MBIST**: HBM5 proposes an on‑die `LBIST` loop that cycles through `WRITE‑READ‑COMPARE` patterns at full speed, reducing external tester time by ~40 %.Test programs must now include `POST_TSV_CAL` sequences to verify interposer bump resistance (`≤15 mΩ`) and hybrid‑bond continuity (`≤5 mΩ`).


## Future Directions – HBM5, HBM6, and Chiplet Integration

Looking beyond HBM4E, JEDEC is scoping:
- **HBM5**: Target 1.2 TB/s stack bandwidth, 16‑die stack, 10 Gbps PAM‑4 I/O, optional `NVMe‑over‑PCIe` auxiliary interface.- **HBM6**: Exploration of silicon‑photonic I/O for >2 TB/s, reducing electrical pin count.- **Chiplet‑centric standards**: Joint work with UCIe to define a `HBM‑Chiplet Bridge` that exposes HBM memory as a UCIe‑compatible die, enabling heterogeneous integration with logic and AI accelerators.These directions will require new test fixtures capable of `optical‑eye` measurement and `thermal‑cycling` to validate photonic co‑packaging.


## Key Takeaways

- JEDEC’s HBM4E baseline (JESD236A) sets 6.4 Gbps NRZ, 1024‑bit I/O, and 8‑die stack limits that define today’s test envelope.
- Bandwidth scaling beyond HBM4E is constrained by TSV pitch, NRZ/PAM‑4 data‑rate ceilings, and thermal density, driving post‑TSV interconnect research.
- Emerging post‑TSV packages (silicon interposer, FOWLP, hybrid bonding) and forthcoming JEDEC Post‑TSV Spec will reshape ATE channel counts, signal‑integrity validation, and BIST strategies.

## References

1. **[JEDEC]** JESD236A – High Bandwidth Memory (HBM) DRAM – HBM4E — JEDEC Standard, released March 2023, defines 6.4 Gbps/pin, 1024‑bit I/O, 8‑die stack.
2. **[JEDEC]** JESD235C – High Bandwidth Memory (HBM) DRAM – HBM3 — Baseline for HBM3, provides timing parameters and TSV pitch reference.
3. **[Paper]** Scaling Limits of HBM Bandwidth: A Circuit‑Level Perspective — IEEE Transactions on Electron Devices, Vol. 70, No. 4, April 2023, pp. 2150‑2162.
4. **[Datasheet]** TSMC CoWoS® and InFO® Packaging Technologies for HBM — TSMC Technical Brief, 2022, describes 2.5 µm L/S routing and ≤10 µm bump pitch.
5. **[Datasheet]** Samsung HBM4E 16 GB 2‑High Stack Datasheet — Samsung Electronics, Rev. 1.0, September 2023, includes pinout, timing, and TSV specifications.
6. **[Paper]** Hybrid Bonding for Die‑to‑Die Interconnects in Advanced Packaging — IEEE International Electron Devices Meeting (IEDM) 2022, pp. 1‑4.

## 🔍 Additional Learning: Hybrid Bonding Impact on HBM Test Flow

Hybrid bonding enables sub‑micron Cu‑Cu interfaces, reducing interconnect resistance to <1 mΩ and eliminating TSV‑related parasitic capacitance. This shift requires ATE to measure low‑resistance bonds using Kelvin‑style four‑wire probing and to validate bond integrity through high‑frequency (>10 GHz) reflectometry before functional memory tests.
