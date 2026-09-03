# HBM Test Escape Analysis & ATPG for PHY Defects

*Thursday, Sep 03 2026*

*Module 16.7 — HBM Test Program Development & Characterization*

## What Is a Test Escape in HBM Context?

A **test escape** is a defective device that passes production test and reaches the field. In HBM, escapes are particularly costly because a single failing stack can bring down an entire AI accelerator or HPC node. The escape rate is quantified as **Defect Level (DL)**, measured in Defects Per Million (DPPM).
The classical relationship between fault coverage and defect level is:
`DL = (1 − FC)^Y_d`
where **FC** is fault coverage and **Y_d** is the yield loss due to defects. For HBM in server-class applications, the escape target is typically &lt;10 DPPM. Latent escapes — devices that pass test but fail in the field due to marginal defects — are the hardest to control and require guard-banding on timing margins and retention tests.


## Fault Coverage Metrics for HBM

HBM test programs must achieve high fault coverage across multiple fault models. The key models are:
- **Stuck-at fault (SAF):** Node permanently logic-0 or logic-1. Industry baseline; 99%+ SAF coverage is standard.- **Transition fault (TF):** Captures slow-to-rise or slow-to-fall defects — critical for HBM PHY DQ and DQS paths where timing violations cause bit errors at speed.- **Path delay fault (PDF):** Sensitizes complete timing paths end-to-end; exposes process-corner marginal paths not caught by TF.- **Cell internal fault (CIF):** Models intra-cell bridging and open defects in standard cells missed by I/O-level SAF models.- **DRAM-specific March faults:** March C-, March SS, and March LR algorithms target coupling faults and retention faults unique to DRAM cell arrays.Fault coverage is computed as: `FC (%) = (detected_faults / fault_list_size) × 100`. JEDEC JESD235C implicitly requires high FC through its mandatory post-package-test (PPT) and built-in self-test (BIST) requirements.


## ATPG for HBM PHY Structures

The HBM PHY (Physical Interface Layer) connects the DRAM stack to the base logic die through microbumps and silicon interposer traces. It contains serializer/deserializer (SerDes) blocks, clock trees, DFI interface logic, and power management circuits — all with limited scan observability due to the high-speed serial nature of the DQ interface.
ATPG challenges unique to HBM PHY:
- **Controllability:** Internal PHY nodes behind SerDes stages cannot be directly driven from ATE pins without scan chain support.- **Observability:** Defects in clock distribution within the PHY stack propagate through multiple serialization stages, masking fault responses.- **At-speed patterns:** PHY delay faults require functional ATPG patterns running at operational frequency (up to 6.4 Gbps for HBM3E), demanding ATE timing accuracy &lt;10 ps RMS jitter.Industry ATPG tools used: **Synopsys TetraMAX ATPG** and **Siemens Tessent**. Both support HBM-specific scan compression and transition fault targeting for deep-submicron PHY logic. Scan chain insertion is area- and power-constrained in HBM die, typically achieving 20–50× compression ratios.


## PHY Defect Models and Fault Classes

HBM PHY defects follow distinct physical failure mechanisms that require tailored fault models:
- **TSV open faults:** Broken through-silicon vias, including resistive opens (&lt;50 Ω nominal) that appear marginal at DC but fail under AC stress. These require transition-fault ATPG or dedicated BIST current sensing.- **Microbump bridging:** Adjacent microbump shorts due to solder collapse or misalignment in the HBM stack assembly. Spacing is typically 40–55 µm, making bridging faults statistically significant.- **Clock tree skew defects:** Process variations in HBM DRAM clock trees (H-tree or fishbone topology) cause intra-die DQS–DQ skew, producing intermittent bit errors under thermal stress.- **Retention faults:** Charge leakage in DRAM cell due to junction leakage; detected by extended retention time test (typically 64–256 ms at elevated temperature per JEDEC standards).- **Via bridging in RDL:** Redistribution layer (RDL) vias in the base die connecting PHY to microbumps can bridge due to copper CMP non-uniformity.

## Escape Analysis Methodology and Feedback Loop

Test escape analysis is a closed-loop process that feeds field failures back into test program improvement:
- **Step 1 — DPPM tracking:** Systematically log field returns by lot, wafer, die coordinates, and test program version.- **Step 2 — FA correlation:** Physical failure analysis (PFA) on returned units using SEM, TEM, FIB, and X-ray tomography to identify defect location and mechanism.- **Step 3 — Fault simulation replay:** Re-simulate the escape defect against the production test patterns using stuck-at or delay fault simulation to confirm which patterns should have detected it.- **Step 4 — Coverage gap identification:** Determine whether the escape is a gap in the fault model (e.g., not modeled) or a gap in the pattern set (modeled but untargeted).- **Step 5 — Pattern augmentation:** Add targeted ATPG patterns or BIST sequences addressing the specific fault class; re-qualify and release updated test program.JEDEC JESD47 (Stress-Test-Driven Qualification) provides the reliability framework that contextualizes which escapes are acceptable versus which trigger corrective action workflows.


## Key Takeaways

- Achieving >99% stuck-at fault coverage is necessary but not sufficient for HBM — transition and path-delay fault models must also be targeted to catch PHY timing escapes.
- HBM ATPG complexity is driven by limited scan observability behind SerDes blocks; scan compression at 20–50× is typical, and at-speed patterns require ATE timing resolution below 10 ps RMS.
- Each field escape should trigger a full FA-to-simulation correlation loop, resulting in test program updates that prevent recurrence of the same fault class.

## References

1. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM — Section 6.3 — DFT and post-package test (PPT) requirements for HBM stack
2. **[JEDEC]** JEDEC JESD47 — Stress-Test-Driven Qualification of Integrated Circuits — Reliability qualification framework relevant to escape analysis thresholds
3. **[IEEE]** IEEE Std 1500-2005 — Embedded Core Test — Standard for scan-based testing of embedded IP cores including PHY logic
4. **[Datasheet]** Synopsys TetraMAX ATPG User Guide — Transition and cell-internal fault models for advanced node PHY ATPG
5. **[Web]** Siemens Tessent — HBM DFT Solution — Tessent MemoryBIST and ScanCompression for HBM PHY and DRAM array test
6. **[Paper]** M. Tehranipoor et al., 'Test and Testability of 3D Integrated Circuits' — IEEE VLSI Test Symposium 2019 — covers TSV fault models and ATPG strategies

## Additional Learning: AC ATPG for Resistive TSV Opens in HBM

Resistive TSV opens — partial disconnections presenting 50–500 Ω resistance rather than a full break — are notoriously difficult to catch with DC stuck-at ATPG because the node can still be driven to a valid logic level under slow stimulus. AC ATPG patterns apply fast transitions and measure propagation delay through the TSV path: a resistive open manifests as increased RC delay, which a delay-fault pattern set captures as a transition fault. Modern ATE platforms such as the Teradyne UltraFLEX-Plus and Advantest T2000 support per-pin timing resolution below 5 ps, enabling in-situ delay measurement of TSV paths within the assembled HBM stack at functional speeds up to 6.4 Gbps for HBM3E.
