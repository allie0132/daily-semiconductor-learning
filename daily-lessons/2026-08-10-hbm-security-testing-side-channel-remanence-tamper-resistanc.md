# HBM Security Testing: Side-Channel, Remanence & Tamper Resistance

*Monday, Aug 10 2026*

*Module 13.3 — Emerging Technologies & Future Directions*

## 1. Side-Channel Vulnerabilities in HBM Stacks

HBM stacks present a unique side-channel attack surface because the logic die and DRAM dies share a tight power delivery network through the TSV interconnect fabric. **Differential Power Analysis (DPA)** and **Electromagnetic Analysis (EMA)** can leak cryptographic key material processed by a logic die when DRAM accesses create correlated power transients on the shared PDN.
Key test vectors include: measuring power supply current on the `VDDQ` rail (1.2V, nominal) during repetitive row activations (`ACT`) aligned to known plaintext operations, capturing EM emissions with a near-field probe over the die stack, and cross-correlating traces with Hamming-weight models of intermediate cipher values. JEDEC JESD235C does not yet mandate DPA countermeasures, but JEDEC JEP106 and SEMI E187 reference test houses using Riscure Inspector and Langer RF-R 50-1 probes for HBM2e/HBM3 security characterisation.
- Power trace acquisition: oscilloscope bandwidth ≥ 1 GHz, sample rate ≥ 4 GS/s on VDDQ shunt resistor (50 mΩ, low inductance)- Number of Traces to Disclosure (NTD) metric used to rank vulnerability severity- Correlation Electromagnetic Analysis (CEMA) is especially sensitive on HBM3 due to dense TSV pitches (55 µm) acting as micro-antennas

## 2. DRAM Data Remanence: Physical and Electrical Mechanisms

**Data remanence** in DRAM refers to residual charge or polarisation state that persists in storage cells after a nominal erase or power-down cycle. In HBM, the storage capacitor (embedded in each DRAM die, ~10 fF for 1α-node LPDDR-based cells) retains charge proportional to the last written value; the decay time constant at room temperature is on the order of seconds, but at cryogenic temperatures (e.g., 77 K used in cold-boot attacks) it can extend to hours.
JEDEC JESD79-5B (DDR5 qualification annex, referenced by HBM3 security supplements) defines a **Data Remanence Test** sequence: write a checkerboard pattern, power-cycle for a defined interval T<sub>rem</sub>, restore power, and perform a full-array read without issuing a refresh. Bit-failure distribution across retention intervals characterises remanence vulnerability. For HBM3, the reference `T<sub>rem</sub>` window is typically 1 s at 85 °C and 10 s at 25 °C.
- 1α and 1β node DRAM cells show improved remanence due to thinner capacitor dielectric, accelerating self-discharge- At sub-zero temperatures, attackers can extend remanence to minutes — a concern for HBM in AI accelerators in physically accessible edge deployments- Mitigation: mandatory `RESET` pin assertion (HBM3 PHY), scrub-on-powerdown, or active zeroization prior to VDD rail collapse

## 3. Tamper Resistance Qualification Methods

Tamper resistance for HBM is evaluated under four threat categories defined by FIPS 140-3 (ISO/IEC 19790) for physical security levels 3 and 4, cross-mapped to JEDEC JEP140 (Memory Security) guidance: **passive observation**, **active manipulation**, **fault injection**, and **reverse engineering**.
For HBM packages, tamper qualification focuses on the **epoxy-mold compound (EMC)** layer and underfill. SEMI M1-0618 specifies cross-section and SEM/FIB inspection criteria. Qualification lots undergo: (a) mechanical probing resistance—verify that EMC hardness (Shore D 80–85) prevents micro-probe needle penetration without detectable layer delamination; (b) optical inspection under 1064 nm near-IR to detect substrate-layer trace exposure; (c) X-ray tomography (Zeiss Xradia 620 Versa class) for non-destructive via-network mapping.
- Active shield mesh: fine metal routing in the top redistribution layer (RDL) signals intrusion if continuity breaks — validated by ATE continuity scan at 100 µA- Environmental stress: tamper mesh continuity verified post-HTOL (1000 h, 125 °C), post-TC (500 cycles, −55/+125 °C), and post-uHAST (96 h, 130 °C, 85% RH)- Fault injection hardening: laser fault injection (LFI) at 1064 nm, 10 ns pulse width — quantify number of pulses required to induce a detectable bit-flip in control registers

## 4. ATE Integration for Security Test

Security test patterns for HBM must be integrated into the standard production flow without exposing sensitive intermediate states. On Advantest T2000 or Teradyne UltraFLEX platforms, security test is typically inserted as a **dedicated test mode** entered via the HBM3 `MRS` (Mode Register Set) sequence, with `MR0[7:4]` reserved bits used in some vendor-specific implementations to gate access to security diagnostic registers.
The test flow at wafer level (KGD) differs from package test: wafer-level probing via probe card on 55 µm TSV pitch requires shielded triaxial probe needles to minimise EMI coupling to measurement equipment. The tester's **PMU (Parametric Measurement Unit)** is reconfigured with a 50 mΩ series sense resistor on VDDQ to capture power traces. Pattern throughput must balance security trace acquisition time (typically 10,000 traces per DUT for DPA pre-screening) against cost of test.
- Test time for DPA pre-screen: ~4 min/device at 10 k traces — adds significant COT; often sampling-based (1 in 1000 units) rather than 100% screen- Result classification: NTD &gt; 10,000 → Pass; NTD 1,000–10,000 → marginal (flag for further characterisation); NTD &lt; 1,000 → Fail- Secure test data handling: trace files encrypted with AES-256-GCM before transmission from tester to analysis server; tester operators never see raw keying material

## 5. Qualification Standards and Certification Pathways

HBM security qualification does not yet have a dedicated JEDEC standard, but the ecosystem borrows from multiple frameworks: **FIPS 140-3 / ISO 19790** for cryptographic module validation, **Common Criteria (CC) EAL4+** for system-level security assurance, and **JEDEC JEP140** for memory-specific security characterisation. Vendors supplying HBM for government and defence applications increasingly face **CMMC Level 2/3** requirements that mandate documented physical security test evidence.
A typical HBM security qualification package includes: FIPS 140-3 boundary definition drawing, DPA/EMA test report (TVLA — Test Vector Leakage Assessment per ISO 17825), data remanence characterisation report, tamper mesh continuity data post-reliability stress, and an independent third-party lab review. Riscure, Brightsight, and Underwriters Laboratories (UL Verification Services) are the primary labs conducting HBM-specific security evals as of 2025.
- TVLA criterion: |t| &lt; 4.5 across all sample points → no first-order leakage detected (ISO 17825 pass threshold)- EAL4+ augmented (ALC_FLR.3) is the most common CC target for HBM in secure enclave applications- JEDEC JEP140A (2024 draft) proposes standardised memory security test methodology for LPDDR5, HBM3, and GDDR7

## Key Takeaways

- HBM's shared TSV-based PDN creates a power side-channel coupling path; DPA/CEMA require ≥1 GHz capture bandwidth on VDDQ with a low-inductance shunt
- Data remanence in 1α/1β DRAM cells extends to seconds at 25 °C but hours at cryogenic temperatures — zeroization before power collapse is the primary mitigation
- Tamper resistance qualification combines mechanical, optical, and X-ray inspection with active-shield mesh continuity tests across HTOL, TC, and HAST stress conditions
- Security test on ATE uses sampling-based DPA pre-screening (NTD > 10,000 = pass) due to high trace-acquisition cost (~4 min/device)
- JEDEC JEP140A (2024 draft) is moving toward standardised HBM security test methodology aligned with FIPS 140-3 and ISO 17825 TVLA criteria

## References

1. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM — JESD235C, 2021 — Sections 2.4 (reset), 6.1 (MRS), Annex A (electrical characteristics)
2. **[JEDEC]** JEDEC JEP140 — Memory Security Characterization Guideline — JEP140 / JEP140A 2024 draft — defines DPA, remanence, and tamper test methodology for volatile memory devices
3. **[IEEE]** ISO/IEC 17825 — Testing Methods for the Mitigation of Non-Invasive Attack Classes Against Cryptographic Modules — ISO 17825:2016 — TVLA methodology; |t| < 4.5 pass threshold for first-order leakage
4. **[Web]** FIPS 140-3 / ISO/IEC 19790 — Security Requirements for Cryptographic Modules — NIST FIPS 140-3, 2019 — Physical security levels 3 and 4 requirements mapped to HBM tamper qualification
5. **[Paper]** Kocher et al., 'Differential Power Analysis', CRYPTO 1999 — Kocher, Jaffe, Jun — CRYPTO 1999, Springer LNCS 1666, pp. 388–397; foundational DPA theory and NTD metric
6. **[Paper]** Halderman et al., 'Lest We Remember: Cold Boot Attacks on Encryption Keys', USENIX Security 2008 — Halderman et al. — USENIX Security 2008; quantified DRAM remanence time constants vs. temperature

## Additional Learning: TVLA-Guided Design-for-Security (DfS) Feedback into HBM PHY

When TVLA testing reveals first-order power leakage (|t| ≥ 4.5) from the HBM PHY's command decoder, the standard remediation loop feeds results back to RTL: inserting balanced logic (dual-rail pre-charge, constant-time address decode), adding on-die decoupling capacitance on VDDQ to flatten burst current signatures, and inserting random dummy row activations (noise injection). A second TVLA pass on the corrected silicon determines whether the leakage point has been suppressed below threshold. This DfS feedback loop is now being formalised in the JEDEC JEP140A working group as a mandatory 'leakage fix verification' step before final security qualification sign-off.
