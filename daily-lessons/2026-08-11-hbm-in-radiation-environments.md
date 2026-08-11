# HBM in Radiation Environments

*Tuesday, Aug 11 2026*

*Module 13.4 — Emerging Technologies & Future Directions*

## Single-Event Effects (SEE) Taxonomy in DRAM

Radiation-induced faults in DRAM fall into four categories defined in JEDEC JESD89C. A **Single-Event Upset (SEU)** is a bit-flip in a storage cell caused by a heavy ion or high-energy neutron depositing charge above the critical charge Q<sub>crit</sub> (~1–10 fC for 10 nm class DRAM). A **Single-Event Latch-up (SEL)** triggers the parasitic PNPN thyristor in bulk CMOS, creating a low-impedance path that can destroy the device if not current-limited. A **Single-Event Functional Interrupt (SEFI)** corrupts control logic (row/column decoders, refresh controllers), causing a mode error or reset requiring a complete power cycle. A **Single Hard Error (SHE)** produces a permanent stuck-at fault from oxide damage or dopant displacement.
- SEU cross-section σ (cm²/bit) is the primary metric, measured at linear energy transfer (LET) thresholds from 0.1 to 120 MeV·cm²/mg- DRAM cells shrink Q<sub>crit</sub> with each node, increasing SEU susceptibility — 10 nm HBM3 cells are ~3× more sensitive than 28 nm HBM1- TSV capacitive coupling in HBM can propagate transients across dies in the 3D stack, making SEFI propagation a unique concern vs. planar DRAM

## JESD89C Test Methodology

JEDEC JESD89C (<em>Measurement and Reporting of Alpha Particle and Terrestrial Cosmic Ray-Induced Soft Errors in Semiconductor Devices</em>) defines the qualification flow for ground-level and space environments. Two test regimes apply to HBM in radiation-tolerant systems:
- **Accelerated neutron testing** uses a spallation source (LANSCE at Los Alamos, TRIUMF) at &gt;10 MeV. The device is exercised in a read-write pattern while error counts are captured by an FPGA controller. The <em>Soft Error Rate</em> (SER) is reported in FIT (Failures In Time, faults per 10<sup>9</sup> device-hours) and normalized to sea level.- **Heavy-ion testing** at a cyclotron (GANIL, TAMU, MSU) sweeps LET from 1 to 120 MeV·cm²/mg. The SEU cross-section curve (σ vs. LET) is fit to a Weibull function to extract LETth (threshold) and saturation cross-section σ<sub>sat</sub> for error rate modeling.- **Alpha emission testing** measures spontaneous α particles from solder/package materials per JEDEC JESD221, critical for data-center SER budgets.For HBM in space, MIL-STD-883 Method 1080 and ESA ESCC 22900 complement JESD89C, adding total ionizing dose (TID) screen steps and displacement damage dose (DDD) requirements not covered by JESD89C alone.


## ECC Architecture and Scrubbing in HBM

HBM implements on-die ECC (ODECC) per the JESD235C specification, Section 4.7. Each 128-bit data burst is protected by a single-error-correcting, double-error-detecting (SECDED) Hamming code. The ECC engine resides in the base die logic and is transparent to the host.
- **ODECC limitations:** SECDED corrects 1 bit and detects 2 bits within the 128-bit codeword. It cannot handle multi-cell upsets (MCU) from a single heavy ion traversal, which can flip 4–16 adjacent bits in a DRAM row.- **Multi-bit interleaving:** HBM3 stacks interleave data across channels and dies so that a single ion track crossing one die affects only one bit per codeword. The physical column distance between interleaved bits must exceed the ion delta-ray range (~5–20 µm).- **Memory scrubbing:** The host controller must schedule periodic scrub reads to correct accumulated SEUs before a second error in the same codeword causes a DUE (Detected Uncorrectable Error). Scrub intervals for LEO orbit typically target &lt;10 minutes based on the predicted SEU rate from AP8/AE8 proton/electron models.- **Chipkill-equivalent:** At system level, multiple HBM stacks implement Chipkill or Chipkill-Correct using Reed-Solomon across devices, tolerating full-stack failures from a SEL-induced power shutdown.

## SEL Hardening Techniques

Latch-up immunity is the highest-priority hardening requirement for space-grade HBM because a SEL can be destructive and force a system reboot. Three complementary approaches are used:
- **Layout-level guard rings:** N+ guard rings around PMOS and P+ guard rings around NMOS suppress the lateral bipolar gain (β) of the parasitic thyristor. Radiation-hardened DRAM processes (e.g., TowerJazz CMOS8RF, GlobalFoundries 22FDX SOI) use fully-isolated SOI or deep-trench isolation to break the PNPN path entirely. Standard HBM processes on bulk CMOS rely on guard rings alone, which reduce but do not eliminate SEL susceptibility.- **Current-limited power supply (CLPS):** The HBM power rails (V<sub>DD</sub>, V<sub>DDQ</sub>) are driven through a series current limit (typically 3× rated I<sub>DD</sub>) implemented in the power management IC (PMIC). A SEL-induced current spike is sensed and the rail is crowbar-tripped and recycled, preventing thermal runaway. Trip latency must be &lt;1 µs to protect the HBM die before junction temperature exceeds 150°C.- **Power sequencing and SEL detection:** The PMIC monitors each HBM supply for over-current. On SEL detection, the sequence is: (1) assert RESET to freeze host DMA, (2) de-assert V<sub>DDQ</sub> (I/O), (3) de-assert V<sub>DD</sub> (core), (4) wait 10 ms for charge dissipation, (5) re-sequence power and re-initialize the stack. Total reboot cycle is &lt;100 ms for most rad-hard FPGA+HBM platforms.

## Space and Defense Qualification Flow

A full space-grade HBM qualification combines radiation testing with the standard semiconductor qualification flow (AEC-Q100 or equivalent MIL-PRF-38535 for Class Q/V). Key milestones:
- **TID screening:** HBM dies are irradiated to mission TID (typically 50–300 krad(Si) for MEO/GEO) using Co-60 gamma at 50–300 rad/s. JESD57 and ESA ESCC 22900 specify bias conditions during irradiation. Parametric measurements (I<sub>DD</sub>, V<sub>OH</sub>, access time) are taken at 0, 25%, 50%, 75%, and 100% TID dose points.- **Lot acceptance testing (LAT):** Per MIL-PRF-38535, radiation characterization is performed on sample lots before each production run. SEU cross-section must remain within 2× of the qualification baseline to maintain lot acceptability.- **Burn-in and HTOL:** Standard 125°C burn-in (168 h) per JESD22-A108 is combined with post-irradiation HTOL to screen latent oxide damage. TID-degraded oxide can accelerate time-dependent dielectric breakdown (TDDB) under normal operating voltage.- **Package radiation qualification:** The HBM interposer underfill and mold compound are tested for outgassing and radiation-induced embrittlement per ASTM E595 and ECSS-Q-ST-70-02C. Polymer cracking from proton damage can cause delamination of the TSV array under thermal cycling.

## Key Takeaways

- JESD89C defines the SEU/SEL test methodology; space systems additionally require TID (JESD57/ESCC 22900) and DDD characterization not covered by JESD89C.
- HBM ODECC (SECDED per JESD235C §4.7) corrects single-bit upsets but cannot handle multi-cell upsets — physical interleaving and system-level Chipkill are required for space-grade reliability.
- SEL hardening relies on three layers: radiation-hardened process (guard rings or SOI), current-limited power supplies with <1 µs trip time, and defined power re-sequence protocol.
- Scrub interval selection is radiation-environment dependent — LEO target intervals ≤10 min; deep-space missions use AP8/AE8 trapped-particle models to derive mission-specific scrub budgets.

## References

1. **[JEDEC]** JEDEC JESD89C — Measurement and Reporting of Alpha Particle and Terrestrial Cosmic Ray-Induced Soft Errors — JESD89C, August 2021, Sections 3–6 (test methodology and SER reporting)
2. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM — JESD235C, Section 4.7: On-Die ECC architecture and SECDED implementation
3. **[Book]** Petersen, E. — Single Event Effects in Aerospace — Wiley-IEEE Press, 2011 — Chapters 4–6: SEU cross-section models, Weibull fits, and rate prediction methodology
4. **[JEDEC]** MIL-PRF-38535 — Integrated Circuits, Microcircuits, General Specification For — Class Q and Class V requirements; Lot Acceptance Testing (LAT) for radiation-hardened devices
5. **[Web]** ESA ESCC 22900 — Total Dose Steady-State Irradiation Test Method — European Space Components Coordination, Issue 4 — TID methodology for space ICs including bias conditions and dose-rate effects
6. **[IEEE]** Schwank, J.R. et al. — Radiation Effects in MOS Oxides — IEEE Trans. Nuclear Science, Vol. 55, No. 4, 2008 — TID mechanisms in thin gate oxides relevant to DRAM process hardening

## Additional Learning: Proton-Induced SEU Rate Prediction in LEO HBM

In low Earth orbit, trapped protons (South Atlantic Anomaly) dominate the SEU rate for HBM rather than galactic cosmic rays. Proton-induced SEU cross-sections are measured at TRIUMF or Indiana University Cyclotron Facility across proton energies from 20–200 MeV. The proton SEU cross-section σ_p (cm²/bit) is convolved with the AP8/AE8 proton flux spectrum integrated over the mission orbit (inclination, altitude) to predict on-orbit SER. For a typical 600 km, 55° inclination orbit, HBM3 with σ_p ~10⁻¹⁵ cm²/bit yields a predicted SER of approximately 10⁻⁸ upsets/bit·day, setting the minimum scrub interval requirement.
