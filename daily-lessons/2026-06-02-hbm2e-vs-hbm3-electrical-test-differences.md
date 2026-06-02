# HBM2e vs HBM3 Electrical Test Differences

*Tuesday, Jun 02 2026*

*Module 3.4 — Protocol & Compliance*

## Data Rate, VDDIO, and Signaling Margin

HBM2e (JESD235B</code>) tops out at **3.6 Gbps/pin** with VDDIO = 1.2V</code> and VDDC/VDD = 1.1V</code>. HBM3 (JESD238A</code>) pushes to **6.4 Gbps/pin** while dropping VDDIO</code> and VDDQ</code> to **1.1V**, with the core supply VDDQL/VDD</code> trimmed toward 1.05V. The reduced supply swing combined with nearly 2x the Nyquist frequency (1.8 GHz → 3.2 GHz) collapses the available voltage and timing eye.
- HBM3 transmit uses an **NRZ** scheme but mandates tighter tDQSCK</code> and reference-voltage placement.- The tester must drive/sense at 1.1V rails on every DQ, DQS, and CA pin — existing HBM2e load boards calibrated for 1.2V VDDIO levels are not reusable without re-characterization of the pin electronics (PE) VOH/VOL/VREF DAC range.- Per-pin DC level accuracy budget shrinks: at 6.4 Gbps the unit interval is ~156 ps, so PE deskew and edge placement must hold to single-digit picosecond accuracy.

## Channel Architecture: Pseudo-Channel vs Native Channel

HBM2e organizes the stack as **8 channels**, each split into two **pseudo-channels** sharing the same CA bus but with independent **64-bit** data, giving the familiar **128-bit per channel** (per pseudo-channel pair) interface and a 1024-bit stack DQ width.
HBM3 doubles to **16 channels**, each natively **64-bit**, again split into two 32-bit pseudo-channels, but the overall stack remains 1024 DQ. The test impact is structural:
- Twice as many independent CA</code>/CK</code> domains to align and leveling-train — the pattern generator must source **16 independent command streams** instead of 8.- Per-channel ECC</code>/severity and **RAS** features (e.g., on-die ECC, ECS error-check-and-scrub) expand the protocol vector space that must be exercised during compliance.- Address mapping and channel-to-DUT-pin mapping on the probe card / load board must be regenerated; reusing HBM2e channel maps causes silent miscompare on the doubled CA fan-out.

## Equalization, ZQ Calibration, and Read/Write Leveling

At 3.6 Gbps HBM2e generally closes the eye without receiver equalization. At **6.4 Gbps HBM3 requires DFE** (decision-feedback equalization) on the read path and adds **per-pin / per-DWORD** training to compensate channel ISI through the silicon interposer.
- **ZQ calibration:** HBM3 refines the ZQ</code> external reference and on-die termination (ODT) calibration with finer driver-strength steps; the tester must allow the device to run its ZQCAL</code> long/short sequences and verify ODT</code> Ron/Rtt codes via mode-register readback (MR</code> reads).- **Write/Read leveling:** both generations need tDQSS</code> write leveling and DQS-to-DQ centering, but HBM3 specifies tighter **eye-width and eye-height** compliance masks (data-eye must be validated per-pin, not per-byte-lane), driving 2D shmoo (VREF vs phase) on every DQ.- The ATE must support hardware DFE tap emulation or rely on the DUT internal equalizer settings read back from the mode registers — passive load boards alone cannot present a clean 6.4 Gbps eye.

## CA Bus, Mode Registers, and JTAG/Boundary Scan

HBM3 reworks the **command/address** protocol: the per-channel CA</code> bus widens/re-times relative to HBM2e's Row/Column command structure, and the mode-register space grows to cover DFE taps, ECC controls, refresh management (RFM), and duty-cycle adjustment (DCA</code>/DCM</code>).
- Compliance vectors must cover new/relocated MR</code> fields — directly reusing HBM2e MRS</code> sequences will set wrong fields on HBM3.- **IEEE 1500** wrapper and **IEEE 1149.1 (JTAG)** boundary-scan/DWORD</code> test access expand: HBM3 adds more internal test/observability registers (per-channel TAP, more MISR</code>/loopback modes) for stack and TSV testing.- The **IEEE 1838** 3D-IC test framework becomes more relevant for the 16-channel stack — boundary-scan chains and the test-access port instruction set differ from HBM2e, so existing IEEE 1149.1 patterns need regeneration.

## ATE Pin-Count and Tester-Resource Implications

Although total stack DQ stays at 1024, the doubling of **independent channels (8 → 16)** roughly doubles the independent CK</code>/CA</code>/control resources and the number of synchronized timing domains the tester must manage.
- **Pin electronics:** every DQ/DQS pin now needs 6.4 Gbps-capable PE with per-pin DFE/timing calibration — often forcing a higher-end ATE pin card (e.g., Advantest V93000 Smart Scale / EXA Scale or Teradyne UltraFLEXplus) versus HBM2e-class cards.- **Resource pressure:** 16 independent command engines, more VREF DACs, and 2D eye-shmoo per pin inflate test time and multisite limits; parallelism per ATE head often drops, raising cost-of-test.- **Power and thermal:** 1.1V rails at higher toggle rates increase di/dt on the load board; DPS channels and decoupling must be re-sized, and thermal control on the stack tightens because HBM3 runs hotter at 6.4 Gbps.

## Key Takeaways

- HBM3 doubles to 16 native 64-bit channels (vs HBM2e's 8 channels with 128-bit pseudo-channel pairs), doubling independent CA/CK domains the tester must train and align.
- Dropping VDDIO/VDDQ from 1.2V to 1.1V while raising data rate to 6.4 Gbps collapses the eye, mandating DFE and per-pin 2D (VREF vs phase) eye-width compliance shmoo.
- HBM3 needs 6.4 Gbps-capable pin electronics, expanded mode-register/ZQ/ODT vectors, and updated IEEE 1500/1149.1/1838 boundary-scan chains, raising ATE resource count and cost-of-test.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM2E) DRAM — JESD235B, JEDEC Solid State Technology Association, 2021
2. **[JEDEC]** High Bandwidth Memory DRAM (HBM3) — JESD238A, JEDEC Solid State Technology Association, Jan 2023 — VDDIO/VDDQ 1.1V, 6.4 Gbps, 16-channel
3. **[IEEE]** IEEE Standard Testability Method for Embedded Core-based ICs — IEEE Std 1500-2005 (core wrapper); IEEE Std 1149.1-2013 (JTAG)
4. **[IEEE]** IEEE Standard for Test Access Architecture for 3D Stacked ICs — IEEE Std 1838-2019
5. **[Datasheet]** SK hynix / Samsung HBM3 Component Datasheet — Vendor HBM3 8-Hi/12-Hi stack datasheet, channel/MR/ZQ and AC timing tables
6. **[Datasheet]** Advantest V93000 / Teradyne UltraFLEXplus High-Speed Digital Instrument Manuals — Pin-electronics data-rate, per-pin DFE and timing calibration specs

## Additional Learning: Why DFE Becomes Non-Negotiable at 6.4 Gbps

At 6.4 Gbps the ~156 ps unit interval over a silicon-interposer microbump channel accumulates enough ISI that the first post-cursor alone can close a meaningful fraction of the eye, which is why HBM3 moves equalization on-die rather than relying on the tester's passive path. As a test engineer you validate the device's trained DFE tap settings via mode-register readback and then prove margin with a 2D VREF-vs-phase shmoo per DQ pin — a step that was usually unnecessary on HBM2e's 3.6 Gbps interface.
