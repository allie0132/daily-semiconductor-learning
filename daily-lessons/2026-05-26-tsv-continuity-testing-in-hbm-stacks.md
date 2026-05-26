# TSV Continuity Testing in HBM Stacks

*Tuesday, May 26 2026*

*Module 2.2 — Electrical Testing*

## Why TSV Continuity Testing Is Critical in HBM

Through-Silicon Vias (TSVs) are the vertical interconnect backbone of HBM stacks, carrying power, ground, data, and command signals between the base logic die and up to 12 DRAM layers in HBM3E devices. A single open or high-resistance TSV can render an entire channel or pseudo-channel inoperable.
Unlike solder bump failures that may be detectable through optical or X-ray inspection, TSV defects are buried within the silicon stack and are electrically invisible unless specifically targeted by test. Failure modes include:
- **Open TSVs** — caused by voiding during Cu fill (superconformal or bottom-up plating failures), barrier/seed delamination, or CMP-induced damage at the TSV landing pad.- **High-resistance TSVs** — partial voids, copper oxidation at bonding interfaces, or incomplete anneal of the Cu damascene fill introduce resistance above the 1–3 ohm specification window.- **Leakage TSVs** — TSV-to-substrate or TSV-to-TSV leakage through insufficient liner oxide thickness, especially problematic in via-middle TSV integration where the oxide liner may be under 100 nm.At HBM3E data rates exceeding 9.6 Gbps per pin, even a marginal TSV resistance increase of a few ohms introduces reflections and eye closure that cause functional failures well before a hard open is detectable.


## TSV Test Structures: Daisy Chains and KGD Considerations

The primary vehicle for TSV continuity measurement is the **daisy-chain test structure**. In a daisy chain, TSVs are connected in series through metal routing on alternating dies, so a single 4-wire (Kelvin) resistance measurement covers many TSVs at once. The total measured resistance divided by the number of TSVs in the chain gives the per-TSV resistance.
JEDEC defines Known-Good-Die (KGD) requirements for HBM DRAM stacks, requiring that each individual die be electrically qualified before bonding. TSV continuity is a KGD gate test performed at wafer level prior to dicing and stacking. This is essential because post-stack rework is cost-prohibitive and practically impossible in TC-NCF (Thermocompression Non-Conductive Film) bonded assemblies.
- **Via-middle TSVs** (formed after front-end, before back-end) are tested through dedicated probe pads on the wafer front side, accessing top and bottom landing pads of each TSV.- **Daisy-chain serpentines** in scribe-lane test vehicles allow process monitoring but do not replace in-die TSV testing on product wafers.- **Per-TSV resistance target** is typically 0.5–2.0 ohms for a 10 um diameter, 50–100 um deep Cu TSV. Values exceeding 3 ohms are typically flagged as marginal; values above 10 ohms indicate hard opens or severe voids.After stacking, individual TSV access is no longer possible. Test must rely on functional continuity paths exposed through the HBM PHY bump interface on the base die.


## Wafer-Level TSV Probing and 4-Wire Kelvin Measurement

At wafer level, TSV continuity is measured using **4-wire Kelvin (force-sense) resistance measurement** to eliminate probe contact resistance from the measurement. This is mandatory because probe contact resistance on small TSV landing pads (often 8–15 um diameter) can be 0.5–2 ohms — comparable to the TSV resistance itself — rendering 2-wire measurements unreliable.
ATE implementation on platforms such as Advantest T2000, Teradyne UltraFLEX, or dedicated wafer-level probe stations uses parametric measurement units (PMUs) or precision source-measure units (SMUs) configured in Kelvin 4-terminal mode:
- **Force High / Force Low**: Force terminals drive a known DC current (typically 1–10 mA) through the daisy-chain structure via two probes.- **Sense High / Sense Low**: Sense terminals measure the voltage drop across the structure via two additional probes, drawing negligible current (&lt;1 nA input bias).- `R_TSV = V_sense / I_force` — resistance is calculated from the ratio with probe contact resistance effectively removed.Probe card design for TSV wafer test requires careful attention to probe tip force and material. Tungsten carbide or palladium alloy tips are preferred on Cu/oxide landing pads to avoid pad damage and ensure low, stable contact resistance. Overdrive must be controlled to prevent TSV landing pad deformation which can cause stacking bond failures.
Current levels must also be controlled to avoid self-heating within the narrow TSV conductor. At 10 mA through a 2-ohm TSV, power dissipation is only 0.2 mW — negligible — but stacked daisy chains of 200+ TSVs can accumulate enough resistive heating to cause measurement drift if forced currents are too high.


## Post-Stack Continuity Verification via HBM PHY Interface

Once the HBM stack is bonded to the interposer and the complete 2.5D package is assembled, direct TSV probe access is lost. Post-stack TSV continuity is verified **indirectly** through the HBM PHY interface exposed on the package substrate balls. JEDEC JESD235C defines specific test modes accessible through the HBM PHY that support continuity and connectivity verification.
Key test modes used for post-stack continuity assessment include:
- **ZQ Calibration and Loopback Tests** — the HBM PHY includes on-die termination (ODT) and ZQ calibration circuits; anomalous ZQ values can indicate TSV resistance degradation on power or ground TSV columns.- **JTAG Boundary Scan** — HBM3 and HBM3E implementations include IEEE 1149.1-compatible boundary scan chains that traverse signal TSVs, allowing open and short detection on data, command, and address paths.- **Built-In Self-Test (BIST) and Pseudo-Channel Mode** — functional BIST patterns exercising all DQ, CA, and CK paths through the full TSV column provide a high-coverage continuity check. A pseudo-channel failure isolated to a single column of 8 DQ TSVs is a strong indicator of a TSV open in that column.- **AC continuity / High-Speed JTAG** — emerging test methods apply controlled AC signals at the package ball interface and use time-domain reflectometry (TDR) techniques through the ATE channel to localize opens within the stack, though spatial resolution is limited by the short electrical length of TSV interconnects.ATE fixture parasitics — particularly transmission line impedance discontinuities in the socket and interposer — must be de-embedded when interpreting post-stack continuity measurements. Board-level calibration structures mimicking the HBM stack impedance profile are essential for accurate baseline reference.


## Test Coverage Strategy and Pass/Fail Limits

A robust TSV continuity test strategy for HBM stacks is hierarchical, spanning multiple test insertion points:
- **T0 — Incoming Wafer Probe (DRAM Wafer)**: Individual die TSV daisy-chain Kelvin resistance; flag dies with per-TSV R above 2 ohms or chain continuity failures. This is the KGD gate for stacking eligibility.- **T1 — Post-Stack Wafer Probe (Base Die Exposed Bumps)**: Functional continuity through HBM PHY using boundary scan and BIST. Detects stacking-induced TSV damage and microbump open/short defects introduced during TC-NCF bonding.- **T2 — Package Final Test (2.5D or 3D Assembled)**: Full functional HBM test including memory cell, timing characterization, and TSV-path integrity validation through all channels and pseudo-channels.- **T3 — System-Level Test (SLT)**: Stress-accelerated continuity checks under thermal cycling conditions to screen latent marginal TSVs that pass cold but degrade under thermal expansion.Pass/fail binning guidelines used in industry practice:
- Per-TSV chain resistance **below 1.5 ohms**: Pass, green bin.- Per-TSV chain resistance **1.5–3.0 ohms**: Marginal bin — subject to thermal re-test or downgrade.- Per-TSV chain resistance **above 3.0 ohms or open**: Hard fail, reject.- TSV-to-substrate leakage exceeding **1 nA at 1V**: Reject (liner integrity failure).Correlation between T0 wafer-level Kelvin resistance and T2 functional failures is a critical yield learning metric. A strong correlation validates the T0 test as a sufficient KGD screen; poor correlation indicates either probe-induced damage at T0 or TCB process-induced TSV degradation during stacking.


## Key Takeaways

- 4-wire Kelvin measurement is mandatory for accurate per-TSV resistance — probe contact resistance is comparable to TSV resistance and cannot be ignored in 2-wire configurations.
- KGD wafer-level TSV continuity testing before stacking is the most cost-effective gate; post-stack rework is practically impossible in TC-NCF HBM assemblies.
- After stacking, TSV continuity is verified indirectly through JTAG boundary scan, HBM BIST, and functional pseudo-channel isolation — direct TSV probe access no longer exists.
- A hierarchical T0/T1/T2/T3 test strategy spanning wafer probe through system-level test is required to catch both hard opens and marginal high-resistance TSVs that may fail only under thermal stress.
- Per-TSV resistance above 3 ohms is a hard fail threshold; even marginal values of 1.5–3 ohms merit thermal re-test because signal integrity degrades at HBM3E speeds before a true open is observable.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) DRAM Standard — JESD235C, JEDEC Solid State Technology Association, 2021 — defines HBM3 PHY interface, test modes, boundary scan requirements, and ZQ calibration used for post-stack continuity verification.
2. **[JEDEC]** JEDEC JESD79-5B: LPDDR5 / HBM KGD Testing Guidelines — JESD79-5B and associated HBM application notes define Known-Good-Die electrical qualification criteria including TSV continuity thresholds for stacking eligibility.
3. **[IEEE]** IEEE Std 1149.1-2013: Standard for Test Access Port and Boundary Scan Architecture — IEEE 1149.1-2013 — foundational boundary scan standard implemented in HBM3/3E for post-stack signal TSV continuity testing through the PHY interface.
4. **[Paper]** Through-Silicon Via (TSV) Technology: Process, Reliability, and Testing — Lau, J.H., 'Overview and Outlook of Through-Silicon Via (TSV) and 3D Integrations,' Microelectronics International, Vol. 28 No. 2, 2011 — covers TSV formation, resistance characterization, and test structure design for daisy-chain continuity measurement.
5. **[Book]** 3D IC and TSV Interconnects — Springer Handbook — Garrou, P., Bower, C., Ramm, P. (Eds.), 'Handbook of 3D Integration,' Wiley-VCH, 2014 — Chapter 14 covers TSV electrical test methods including Kelvin probing, daisy-chain design, and ATE integration for wafer-level KGD qualification.
6. **[Datasheet]** Advantest T2000 HBM Test Application Note — Advantest Corporation, 'HBM2E/HBM3 Test Solution on T2000 Platform,' Application Note AN-T2000-HBM-2022 — describes ATE hardware configuration for 4-wire TSV resistance measurement and HBM boundary scan test implementation.

## Additional Learning: TSV Kelvin Probing: Guard Ring Technique

When measuring TSV daisy-chain resistance on product wafers with via-middle TSVs surrounded by active circuitry, leakage currents through the substrate can corrupt Kelvin measurements. A guard ring biasing technique — applying a driven shield voltage equal to the force voltage to surrounding substrate tie-downs — reduces substrate leakage below 100 fA, making it negligible relative to the 1–10 mA force current and enabling accurate sub-0.1 ohm resolution on per-TSV resistance extraction. This is especially critical on lightly-doped substrates where TSV-to-substrate leakage paths are resistive rather than junction-blocked.
