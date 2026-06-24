# HBM4 High-Speed PHY Testing at 6.4 Gbps

*Wednesday, Jun 24 2026*

*Module 7.1 -- Advanced Test Methodologies*

## HBM4 PHY Architecture — What Changed from HBM3

HBM4 (JESD235D) targets **6.4 Gbps per pin** across a 1024-bit data bus, doubling the per-stack bandwidth ceiling to **819.2 GB/s** versus HBM3's 819 GB/s at 3.2 Gbps. To reach this data rate, the PHY architecture introduces several critical changes:
- **Multi-tap Decision Feedback Equalizer (DFE):** A 4-tap DFE replaces the 2-tap version in HBM3, compensating for increased ISI from higher Nyquist frequency (~3.2 GHz). Each tap weight is individually calibrated and verified during training.- **Continuous-Time Linear Equalizer (CTLE):** An integrated CTLE on the RX side boosts high-frequency content attenuated by bump/interposer parasitics. Peaking frequency and gain are programmable via mode registers `MR32-MR35`.- **Reduced VDDQ swing:** HBM4 drops VDDQ from 1.2 V (HBM3) to **1.05 V** to reduce power despite higher switching frequency, requiring tighter noise budget management on the PDN.- **Write Clock (WCK) rate:** WCK doubles to 6.4 GHz in 1:2 mode (WCK:DQ = 2:1), with a new divided 3.2 GHz mode for lower-power operation added in JESD235D Annex H.

## ATE Requirements for 6.4 Gbps Characterization

Testing HBM4 at full 6.4 Gbps rates pushes conventional ATE pin electronics. Key ATE considerations:
- **Timing accuracy:** At 6.4 Gbps the UI is **156.25 ps**. JEDEC JESD235D mandates capturing eye width >=0.4 UI (>=62.5 ps) at BER 10-12. ATE timing generators must deliver **RMS jitter <1.5 ps** to leave adequate margin for device under test characterization.- **Pattern generation:** Full-speed DQ patterns must exercise all 1024 DQ lanes simultaneously. Advantest T2000 HX (DRAM option) and Teradyne UltraFLEX-M both support 8 Gbps pin electronics -- sufficient headroom for 6.4 Gbps with voltage/timing margining.- **Probe card bandwidth:** Micro-BGA probe contacts must maintain return loss better than -15 dB through 6.4 GHz. Co-axial-style probes with integrated RF launches are required at wafer sort; final test uses mass-interconnect sockets with controlled-impedance paths.- **DBI-DC mode:** Data Bus Inversion-DC (DBI_DC) must be exercised explicitly; failing to toggle `MR5[4]` between enabled/disabled during test leaves the inversion logic uncovered.

## Training Sequence Verification — DQS, Read Leveling, and WCK Sync

JESD235D defines a mandatory initialization and training sequence that PHY controllers must complete before normal operation. Test engineers must verify each stage converges within its timeout window:
- **WCK2DQS sync (tWCKSYNC = 16 WCK cycles):** WCK-to-DQS phase alignment must settle within 16 WCK cycles (~2.5 ns at 6.4 GHz). ATE pattern generators inject a known WCK phase offset and verify DQS tracks within +/-0.05 UI.- **Read Gate Training:** The host iterates `CA[8:5]` on the READ GATE TRAINING command (opcode `1011`) to find the optimal DQ capture window. Test coverage must verify the final MR-written gate delay falls within the center +/-10% of the passing window.- **Write Leveling:** The device drives DQS edges back to the host at different CMD-to-DQS skew offsets. A stuck-at defect in the DQS feedback path causes write leveling to converge at an incorrect value -- test must inject known skews and verify reported alignment matches within +/-0.02 UI tolerance.- **Per-lane DFE tap training:** Each of 4 DFE taps is swept independently using a PRBS-7 pattern; tap convergence must complete within `tDFE_TRAIN = 512 WCK cycles` per JESD235D Section 5.9. A failing tap produces a characteristic eye closure at the corresponding symbol delay.

## Eye Diagram Analysis and JESD235D Eye Mask Requirements

Eye mask compliance is verified by forcing the DUT to loop-back or by probing the DRAM DQ pads directly at wafer level. JESD235D Table 24 specifies the minimum eye opening at the **PHY receiver input** (not at the controller):
- **Eye Width (EW):** >=0.40 UI at BER 10-12 (>=62.5 ps at 6.4 Gbps)- **Eye Height (EH):** >=120 mV differential (>=85 mV for low-voltage option at VDDQ = 0.9 V)- **Mask definition:** A diamond mask with forbidden zones at +/-0.30 UI horizontally and +/-60 mV vertically centered on the crossing pointIn production test, the full BER bathtub cannot be swept (cost prohibitive). Instead, ATE applies **voltage margin (Vmargin) and timing margin (Tmargin) stressing** -- stepping VDDQ +/-5% and CK frequency +/-3% while running PRBS-23 and checking for errors. Any error at the stress corner implies the nominal eye is inside the mask, providing a pass/fail proxy for BER 10-12 compliance.
Critically, at 6.4 Gbps the **ISI tail** in the eye bathtub extends further than HBM3. DFE residual error -- taps set to non-optimal values -- shows up as asymmetric vertical closure; if the eye is taller on one side, check tap 3 or 4 calibration convergence first.


## Failure Modes Unique to HBM4 PHY Testing

Several failure signatures appear specifically in HBM4 PHY testing that were not present or less severe in HBM3:
- **WCK frequency doubler phase noise:** The internal WCK x2 PLL (for 1:2 DQ sampling) adds phase noise. Excess phase noise >1.8 ps RMS causes intermittent eye closure caught only by jitter decomposition on a scope, not standard ATE pass/fail.- **CTLE peaking resonance:** Miscalibrated CTLE peaking (wrong `MR32` value) causes a gain peak at 4-5 GHz, amplifying noise from micro-bumps. Symptom: errors only on adjacent lane pairs (crosstalk amplification).- **DBI polarity inversion:** If DBI_DC logic has a stuck bit, every transition is inverted. Visible as a 50% error rate on PRBS patterns -- not a random noise failure but a systematic inversion. Reading back `MR5[4]` verifies the register; a mismatch points to post-latch logic fault.- **Micro-bump impedance mismatch at 6.4 GHz:** TSV-to-micro-bump transitions that were transparent at 3.2 Gbps become resonant stubs at 6.4 GHz. Symptom: lane-specific failures that correlate with die edge location and reproduce on thermal stress. Address through bump impedance characterization using TDR before electrical test.

## Key Takeaways

- HBM4 targets 6.4 Gbps/pin with a 1024-bit bus, requiring ATE pin electronics capable of >=8 Gbps and sub-1.5 ps RMS jitter to leave margin for DUT characterization.
- JESD235D mandates WCK2DQS sync within 16 WCK cycles and 4-tap DFE convergence within 512 WCK cycles -- both windows must be verified explicitly, not assumed.
- Eye mask compliance is production-tested via Vmargin/Tmargin stress with PRBS-23; full BER bathtub sweeps are characterization-only due to test-time cost.
- HBM4-specific failure modes -- WCK PLL phase noise, CTLE resonance, DBI polarity inversion, and micro-bump stub resonance -- require targeted test patterns beyond standard DRAM test suites.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM4) DRAM -- JESD235D -- JEDEC Solid State Technology Association, 2024. Sections 5.8-5.10 cover PHY training sequences; Table 24 specifies eye mask.
2. **[JEDEC]** HBM3 JESD235C -- PHY and Electrical Specifications -- JESD235C (2022). Compare Section 5.7 (WCK) and Section 6.4 (Vref training) against HBM4 delta.
3. **[Book]** Signal Integrity for PCB Designers -- Bogatin, E. (2018). Chapters 9-11 on ISI, DFE, and eye diagram analysis apply directly to HBM4 PHY analysis.
4. **[IEEE]** Characterization and Modeling of TSV in 3D ICs for Signal Integrity -- IEEE Trans. CPMT, vol. 3, no. 4, 2013. TSV stub resonance analysis relevant to HBM4 micro-bump impedance.
5. **[Datasheet]** Advantest T2000 HX DRAM Test Solution -- Advantest Corp., 2024. Specifies 8 Gbps pin rate, 1.2 ps RMS jitter, and HBM4 PHY training pattern support.
6. **[Paper]** DFE Tap Calibration for High-Speed DRAM Interfaces -- Sim, J. et al., IEEE International Memory Workshop (IMW) 2023. Multi-tap DFE convergence analysis for 6.4 Gbps DRAM receivers.

## Additional Learning: WCK Frequency Doubler PLL Jitter Budget

HBM4's internal WCK x2 PLL must contribute less than 0.8 ps RMS random jitter to stay within the overall 1.5 ps RMS budget at the DQ capture latch. This is characterized by injecting a spectrally-clean reference WCK and measuring the DQ-captured jitter accumulation with a high-bandwidth oscilloscope at the micro-bump pads -- a step that ATE cannot substitute. Engineers should request PLL characterization data from DRAM vendors as part of the KGD qualification package, particularly the jitter transfer function (JTF) across PVT corners, since a tight JTF peaking specification is not yet mandated in JESD235D but significantly affects system-level margin.
