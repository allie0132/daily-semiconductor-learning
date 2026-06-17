# HBM Multi-Site Parallel Testing Architecture

*Wednesday, Jun 17 2026*

*Module 5.6 -- ATE & Production*

## Why Multi-Site Matters for HBM Production Economics

HBM devices command high ASP but also carry substantial test time cost due to their wide interface width. A single HBM2E stack presents **1024 data pins** per channel pair (2×512-bit channels), plus command/address, power, and JTAG signals — often exceeding 1200 pins per DUT. At a typical wafer-level or KGD (Known-Good Die) test step, single-site testing is economically unacceptable at volume.
Multi-site parallel testing (MSPT) addresses this by simultaneously contacting and stimulating <em>N</em> DUTs. For HBM, **2-site and 4-site** are common production configurations; 8-site is emerging for HBM3. The cost-per-second of ATE time is amortized across all active sites, directly reducing Cost of Test (CoT) roughly by factor <em>N</em> when test time is the bottleneck.
- A single HBM3 die requires ~1200+ tester channels at full-channel parallel testing.- 4-site HBM3 demands >4800 tester channels — placing this at the boundary of current ATE pin capacity.- Test engineers must balance site count against channel budget, probe card complexity, and yield learning needs.

## ATE Architecture Requirements for HBM Parallel Test

HBM's pseudo-channel (PC) architecture (JESD235C, Section 3.2) means each 128-bit pseudo-channel must be independently addressable. ATE systems must provide **per-pin parametric measurement units (PMUs)**, per-site timing calibration, and independent per-site pattern generation to avoid cross-contamination of results.
Key ATE architectural requirements:
- **Per-site independent timing domain:** HBM2E operates at 2400 MT/s (1200 MHz data rate); HBM3 reaches 6400 MT/s. Each site's WRDQS/RDQS strobe must be independently de-skewed and calibrated. Shared timing across sites introduces systematic timing error that masks real device margining.- **Per-pin VREF control:** HBM uses internal VREFDQ (range ~0.25×VDDQ to 0.45×VDDQ). ATE must sweep VREFDQ via Mode Register Write to `MR04[6:0]` (HBM2E) or equivalent MRS independently per site.- **Per-site power supply islands:** VDDQ (1.2V nominal for HBM2E, 1.05V for HBM3) and VPP (1.8V) must be independently forced and measured per site. Shared power rails cause IR-drop coupling between sites, corrupting IDD measurements.- **Pattern memory depth:** Long march-pattern sequences for DRAM cell testing require pattern memory depths of 128M vectors or more per site on modern ATE (e.g., Advantest T2000, T5503, or Teradyne UltraFLEX with HBM option cards).The Advantest T5503 uses a distributed pin electronics (DPE) architecture where each pin card handles 128 channels with on-board FPGA pattern generation, enabling near-zero skew within a site by minimising signal path length differences.


## Signal Integrity Constraints and Probe Card Design

At HBM3 data rates (up to 6.4 Gbps per pin), probe card signal integrity is the dominant limiting factor for MSPT. HBM is tested at wafer level on the die before 2.5D integration (KGD flow), requiring a **full-array wafer probe card** contacting the microbump array. Bump pitch for HBM3 is 25 µm C4 bumps on a 55 µm grid — necessitating MEMS-style cantilever or vertical probe technologies.
- **Channel-to-channel crosstalk:** At 6.4 Gbps, adjacent probe needles on a shared substrate act as coupled transmission lines. Aggressor-victim coupling can degrade eye opening by 30–50 mV if probe card layout is not optimised. Ground shielding pins between signal groups are essential.- **Stub length control:** Any unterminated stub on the probe card creates a resonance. For HBM3, stubs longer than ~5 mm at 6.4 Gbps begin to cause significant reflection. Probe card designs use **matched-length, low-loss substrate routing** with controlled impedance (typically 50Ω ±10%).- **Per-site isolation:** In a 4-site probe card, each site's signal cluster must be RF-isolated. Shared ground planes can carry return currents that couple between sites. Segmented ground planes with stitched vias are used to contain return paths.- **Thermal uniformity:** Multi-site probe cards with active DUTs can develop thermal gradients >10°C across the card surface, causing differential thermal expansion that shifts contact force. Thermal sensors and active chuck compensation are required.Vendors such as FormFactor (Pyramid Probe) and Japan Electronic Materials (JEM) offer HBM-specific probe cards with per-site impedance characterisation reports and S-parameter models for ATE-to-card correlation.


## Synchronisation, Calibration, and Site-to-Site Timing Correlation

The fundamental challenge in MSPT is ensuring that results from Site 2, Site 3, Site N are statistically equivalent to results from Site 1 — i.e., the tester does not introduce systematic site-to-site offsets. For HBM this requires a rigorous calibration sequence before production insertion.
**Timing calibration (TDBI — Tester Data Bus Integrity):** Each site's data strobe (WRDQS/RDQS) relative to the reference clock must be aligned to within ±5 ps to maintain HBM2E `tDQSCK` margin compliance (JESD235C Table 27, `tDQSCK` = ±225 ps max at 2400 MT/s, but tester contribution must be <10% of that budget). This is done using a loopback stimulus on a calibration DUT or precision reference board inserted at the probe card interface.
**VREF calibration per site:** Since `MR04` VREFDQ sweep is used for data eye centering, any ATE forcing voltage offset between sites shifts the apparent optimal VREF and causes false margin variation. PMU offset nulling to <1 mV is required.
**Pattern synchronisation:** All sites must receive their first valid CK/CK# edge simultaneously (within 1 UI = 416 ps at 2400 MT/s). ATE systems use a **star-topology clock distribution** from a master clock source to each site's pin card, with matched-length clock cables or electronic delay compensation.
- Advantest T5503 implements <em>Inter-Site Sync</em> via a dedicated hardware synchronisation bus separate from data channels.- Teradyne UltraFLEX uses a <em>Digital Sync Module</em> that aligns pattern start across sites to within 1 cycle.- Post-calibration, a golden-device correlation run across all sites is required; acceptance criterion is typically <±3σ Cpk offset between sites on key parametrics (IDD1N, tRC, VREFDQ_OPT).

## Practical Production Implementation: Site Configuration and Bin Split Strategy

Production HBM multi-site testing is implemented as a sequence of test phases, each exploiting parallel execution differently depending on the test type:
- **DC parametrics (IDDQ, continuity, leakage):** Fully parallel across all sites. PMU per pin measures simultaneously. No inter-site dependency.- **Functional memory test (march patterns, MBIST):** Parallel per site, but pattern must be identical per site and synchronised start is required. Typical HBM2E full-array march test (e.g., March C-) at 1200 MHz takes 8–12 seconds per site; MSPT reduces this proportionally.- **AC margining (timing shmoo, VREFDQ shmoo):** Each site sweeps independently. Results are per-site per-pin. This phase is the primary differentiator of MSPT efficiency because shmoo loops are computationally expensive — running 4 sites in parallel cuts total shmoo time by ~4×.- **Temperature-forced test:** Multi-site at cold (–20°C) and hot (+85°C) is complicated by thermal gradients on the chuck. Engineers must validate that all sites reach target temperature within ±1°C before test start, using thermocouple arrays embedded in the chuck surface.**Bin split and per-site yield tracking:** Each site is assigned an independent bin register in the ATE software (e.g., in Advantest ATML or Teradyne IG-XL `site_num` variable). Soft-bin to hard-bin mapping must be consistent across sites. A common failure mode in early MSPT bringup is a misconfigured site mask that silently passes failing devices on Site 2+ while Site 1 bins correctly.
**Site dropout handling:** If a probe needle fails mid-lot (detectable by continuity check or sudden yield cliff on one site), the ATE must support <em>site disable</em> without halting the lot — continuing in N-1 mode. This requires pre-validated test program site-mask logic and Lot Traveller documentation of the site dropout event for yield analysis.


## Key Takeaways

- HBM multi-site testing requires fully independent per-site timing domains, VREF control, and power supply islands — shared resources introduce systematic measurement errors that corrupt parametric data.
- Probe card SI at HBM3 speeds (6.4 Gbps) is the dominant constraint for 4-site and beyond; crosstalk, stub resonance, and thermal gradients must all be engineered at the probe card level, not compensated in software.
- Site-to-site calibration (timing TDBI, VREF nulling, pattern sync) is a mandatory production qualification gate — acceptance requires <±3σ Cpk offset between sites on critical parametrics before volume insertion.
- AC shmoo and MBIST march patterns deliver the largest CoT reduction under MSPT because their long execution times are directly parallelised; DC parametrics gain less due to their inherently short measurement times.
- Site dropout handling logic must be explicitly validated in the test program — silent pass of failing devices on a masked site is a known early-bringup failure mode that can ship defective KGD.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard -- JESD235C, Sections 3.2 (pseudo-channel architecture), Table 27 (AC timing parameters tDQSCK), MR04 VREFDQ definition. JEDEC Solid State Technology Association, 2021.
2. **[JEDEC]** HBM3 DRAM Standard -- JESD238A, Section 4 (electrical specifications, 6.4 Gbps signalling), Section 8 (mode register definitions). JEDEC, 2022.
3. **[Paper]** Multi-Site Test Efficiency and Correlation for Advanced Memory Devices -- Proceedings of the International Test Conference (ITC), 2019. Authors: K. Huang et al. Covers per-site calibration methodology and site correlation metrics for wide-bus memory ATE.
4. **[Datasheet]** Advantest T5503 Memory Test System Technical Overview -- Advantest Corporation, T5503 Product Brief, 2022. Documents distributed pin electronics (DPE) architecture, Inter-Site Sync bus, and HBM channel count scalability. Available via Advantest partner portal.
5. **[Book]** Signal Integrity for High-Speed Digital Design -- S. Hall and H. Heck, 'Advanced Signal Integrity for High-Speed Digital Designs,' Wiley-IEEE Press, 2009. ISBN 978-0-470-19235-1. Chapters 6–8 cover transmission line stubs, crosstalk, and probe card modelling.
6. **[Datasheet]** FormFactor Pyramid Probe HBM Wafer Probe Card -- FormFactor Inc., Pyramid Probe Product Line for HBM KGD Testing, 2023. Documents per-site impedance control, MEMS probe technology for 25 µm bump pitch, and S-parameter characterisation methodology.

## Additional Learning: Compressed Pattern Execution for HBM MSPT Throughput

Modern ATE platforms for HBM multi-site testing increasingly use <strong>on-card FPGA-based pattern compression</strong> (e.g., Advantest T5503 DPE FPGA, Teradyne SmartScale) to reduce pattern memory bandwidth — the critical bottleneck at 4-site 6.4 Gbps. A compressed march-C pattern for a 16 Gb HBM3 stack can be stored as a procedural loop structure consuming <1% of the raw vector equivalent memory, enabling deeper pattern sets within the same SRAM budget. The practical implication for senior engineers is that transition to HBM3 8-site testing does not necessarily require a full ATE platform upgrade if the existing system supports procedural pattern engines — the limiting constraint shifts from memory depth to pin electronics bandwidth and probe card SI, which must then be re-evaluated separately.
