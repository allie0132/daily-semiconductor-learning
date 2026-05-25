# HBM Capacity and Density Evolution: HBM1 to HBM3E

*Monday, May 25 2026*

*Module 1.10 — Foundations*

## HBM1: Establishing the Standard (2013–2015)

HBM1, standardized as **JESD235** in 2013, introduced the 3D-stacked DRAM architecture that defines the HBM family. A stack consists of four active DRAM dies plus a base logic die, bonded through **through-silicon vias (TSVs)** and micro-bumps. The bus width is 1024 bits (8 channels × 128 bits), operating at **1 Gbps/pin** for a peak bandwidth of **128 GB/s**.
Maximum per-stack capacity at launch was **1 GB** (Samsung), later extended to **2 GB** using 29 nm DRAM dies. The strict area and power constraints of the era limited die density; each active die contributed 256 Mb (1 GB stack) or 512 Mb (2 GB stack). AMD Fiji (R9 Fury X, 2015) was the first commercial product, stacking four HBM1 packages on an active interposer for 4 GB total.
- Stack height: 4-Hi (4 DRAM + 1 base)- TSV diameter: ~6 µm, pitch 55 µm- Micro-bump pitch: 55 µm- Max capacity: 2 GB/stack; 4 GB with 4 stacks

## HBM2 and HBM2E: Scaling Capacity and Bandwidth (2016–2021)

**HBM2 (JESD235A, 2016)** doubled the per-pin data rate to **2 Gbps** and introduced **8-Hi** stacking, lifting per-stack capacity to **4 GB (4-Hi) or 8 GB (8-Hi)**. NVIDIA V100 (2017) used four 8-Hi stacks for 32 GB at **900 GB/s**. The standard also added a `AWORD` CRC mode, per-channel ECC, and the **cattrip** over-temperature emergency shutdown signal.
**HBM2E** is not a separate JEDEC revision but a vendor-extended specification (JESD235B covers some improvements) that pushed per-pin rate to **3.2–3.6 Gbps**. SK Hynix Flashbolt (2020) reached **16 GB/stack** at **460 GB/s** by using 1x-nm DRAM dies. Micron's HBM2E similarly reached 16 GB. The base die PHY had to be redesigned for higher DQ swing control and tighter ZQ calibration to support the increased data rate.
- HBM2 peak: 8 GB/stack, 256 GB/s- HBM2E peak: 16 GB/stack, 460 GB/s- New in HBM2: per-DRAM addressing (PDA), mode register write (MRW), RD/WR preamble training

## HBM3: Architectural Reinvention (2022–2023)

HBM3, standardized as **JESD238** in 2022, represents the most significant architectural change since HBM1. The channel structure was redesigned: each physical channel is now 64 bits wide, but logically split into two **pseudo-channels (PC)** sharing command/address but with independent data buses and CRC engines. This yields **16 physical channels × 2 PCs = 32 pseudo-channels per stack**, enabling narrower, more efficient transactions.
Per-pin data rate increased to **6.4 Gbps**, with stack capacity reaching **16 GB (8-Hi)** to **24 GB (12-Hi)** using 1-α nm DRAM dies. Samsung's HBM3 (introduced in NVIDIA H100, 2022) operates at **819 GB/s** per stack. JEDEC JESD238 also defined a new **DBI-AC** (data bus inversion for AC noise) scheme and extended **read/write leveling** training sequences to compensate for longer TSV propagation delays in taller stacks.
- Peak bandwidth: 819 GB/s/stack- Max capacity: 24 GB/stack (12-Hi, 2 GB/die)- New features: pseudo-channels, CRC-per-PC, AC-DBI, enhanced training

## HBM3E: Current Density Frontier (2023–2025)

HBM3E extends HBM3 to **9.6 Gbps/pin** (some vendor roadmaps show 12 Gbps), achieving **1.2 TB/s per stack**. The maximum per-stack capacity rose to **36 GB** (12-Hi using 3 GB dies) with SK Hynix Shinebolt used in NVIDIA H200 (2024). Samsung and Micron both ship HBM3E in volume; Micron's HBM3E uses a 1-β nm node targeting 3 GB per die.
Taller stacks increase TSV aspect ratio demands. At 12-Hi, TSV depth exceeds 70 µm in thinned dies (~50 µm post-grind), requiring **high-aspect-ratio TSV etching (AR ≥ 14:1)** and void-free tungsten or copper fill. Micro-bump pitch has tightened to **~25–36 µm**, and wafer bonding yield management is critical — a single defective die in a 12-Hi stack scraps the entire assembly.
- SK Hynix Shinebolt: 36 GB, 1.2 TB/s (H200)- Micron HBM3E: 36 GB, 1.2 TB/s (announced MI300X configurations)- Samsung HBM3E: 24 GB, 1.15 TB/s- Micro-bump pitch: ~25–36 µm (down from 55 µm in HBM1)

## TSV and Die-Thinning Technology Enabling Capacity Scaling

The ability to stack more dies per package is gated by **TSV density**, **die thickness**, and **bonding yield**. DRAM dies are thinned to **~40–60 µm** post-grind to keep total stack height under ~720 µm (HBM3E 12-Hi). The TSV must extend through the full thinned die; tighter pitch allows more signal TSVs within the fixed footprint (roughly 5.5 mm × 7.7 mm for a standard HBM stack).
Each generation has also improved DRAM die density independently of stacking. Moving from 29 nm (HBM1) to 1α nm (HBM3) increased cell density ~4× per die, while stack height grew from 4-Hi to 12-Hi — a combined ~12× increase in bits per package footprint. Yield challenges compound with stack height: the compound yield for an N-Hi stack scales as `Y_die^N`, so a 97% single-die yield gives only 69% stack yield at 12-Hi, making **known-good-die (KGD)** testing at wafer level mandatory before stacking.
- Die thickness: ~700 µm bulk → ~40–60 µm post-grind- TSV pitch trend: 55 µm (HBM1) → ~40 µm (HBM2/3)- KGD yield model: Y_stack ≈ Y_die^N × Y_assembly

## Key Takeaways

- Per-stack capacity grew ~9× from HBM1 (4 GB) to HBM3E (36 GB), driven by both taller stacks (4-Hi → 12-Hi) and higher per-die density (29 nm → 1x nm nodes).
- Bandwidth scaled from 128 GB/s (HBM1, 1 Gbps/pin) to 1.2 TB/s (HBM3E, 9.6 Gbps/pin), requiring major PHY redesigns and new training sequences each generation.
- Known-good-die (KGD) testing before stacking is critical — compound yield at 12-Hi collapses rapidly with even modest single-die defect rates, making wafer-level burn-in and electrical screening economically necessary.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — primary HBM2/2E standard; section 3 covers stack architecture and capacity configurations
2. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM — JESD238A — HBM3 standard; section 4 defines pseudo-channel architecture and 6.4 Gbps signaling
3. **[IEEE]** A 1.1V 36GB 4-Hi HBM3E with 1.2TB/s Bandwidth and Enhanced RAS Features — ISSCC 2024, SK Hynix — Shinebolt die architecture, TSV pitch, and PHY design details
4. **[IEEE]** A 16-Gb 640-GBps HBM3 DRAM with 1-Gbit/pin 2-Mb/bank Sub-array and Compiler-Optimized OTP for Cost Reduction — ISSCC 2022, Samsung — HBM3 die design, pseudo-channel implementation
5. **[IEEE]** A 16GB 8Hi HBM2E DRAM with 460GB/s Bandwidth and 26Gbps Serdes Interface — ISSCC 2021, SK Hynix Flashbolt — HBM2E capacity and signal integrity details
6. **[Paper]** 3D-IC Packaging with HBM: TSV Aspect Ratio and Known-Good-Die Testing — IEEE Transactions on Components, Packaging and Manufacturing Technology, Vol 13, 2023 — compound yield modeling for tall stacks

## 🔍 Additional Learning: Pseudo-Channel Architecture and Its ATE Test Implications

HBM3 introduced pseudo-channels (PC) where each 64-bit physical channel is divided into two 32-bit pseudo-channels that share address/command buses but maintain independent data paths, CRC engines, and error status. This means a test program must independently exercise all 32 PCs per stack for march algorithms, BIST, and CRC verification — a single physical channel failure can appear as either one or two PC failures depending on whether the fault is in the shared address decoder or in an independent data path. On ATE, pattern time nearly doubles versus HBM2E for equivalent coverage, and per-PC training (tDQSCK, ODT, ZQ) must be serialized, adding significant test-time overhead that vendors manage through concurrent multi-stack testing on high-pin-count testers such as the Advantest T2000 HBM.
