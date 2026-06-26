# HBM Vendor Qualification Testing

*Friday, Jun 26 2026*

*Module 7.5 — Advanced Test Methodologies*

## Overview of HBM Vendor Qualification

HBM vendor qualification is the systematic process by which a system integrator or OSAT validates that a specific DRAM vendor's HBM production lots meet the electrical, physical, and reliability requirements for integration into a 2.5D or 3DIC product. Three major HBM DRAM vendors — SK Hynix, Samsung, and Micron — each produce HBM to JEDEC JESD235C but with vendor-specific implementations of PHY training sequences, mode register sets, and post-package repair (PPR) flows.
Qualification operates at two distinct levels:
- **Design qualification (DQ)**: One-time validation that a new device revision meets all JEDEC specs and product-specific reliability targets. Typically requires 3 lots, 77 units per lot minimum per JESD47 statistical confidence requirements.- **Production monitoring (PM)**: Ongoing lot-level surveillance using reduced sample sizes and accelerated screens to confirm that process shifts have not degraded device quality between qualification events.The qualification plan must explicitly define which JEDEC tests are required (`JESD22` reliability suite), which are waived with rationale, and which vendor-specific tests supplement the standard. HBM KGD (Known Good Die) qualification adds wafer-sort margin tests not present in packaged DRAM qualification flows.


## Acceptance Criteria for HBM Lots

Electrical acceptance criteria for incoming HBM lots derive from JESD235C and are tightened by the integrator's design margin requirements. Key parameters with their JEDEC limits and typical integrator guardbands include:
- **DC specs**: `VDD` = 1.2V ±60mV (JESD235C), integrators typically screen at ±40mV. `IDD4R` (active read current) must not exceed the vendor datasheet maximum; lots showing >3% elevation vs. historical average are flagged.- **AC timing**: `tRCD`, `tCL`, `tRP` measured at nominal VDD and at 85°C junction temperature. Integrators require a minimum **10% timing margin** beyond JEDEC limits to accommodate interposer launch degradation and thermal variation in the final assembly.- **Yield gate**: Minimum wafer-sort KGD yield threshold — typically **99.85%** or better per die (after redundancy repair) to keep assembled 4-die stack yield above 99.4%.- **Parametric Cpk**: Process capability index Cpk ≥ 1.33 required on all critical speed margin parameters (read latency, DQ setup/hold). Lots with Cpk between 1.0 and 1.33 are quarantined for engineering review; Cpk &lt; 1.0 triggers automatic lot rejection.Acceptance sampling follows **ANSI/ASQ Z1.4** (attribute data). For HBM applications, AQL 0.065 to 0.1 is standard, using Code Letter J or K depending on lot size, requiring zero defects in the sample for lot acceptance.


## Lot Qualification Process

Each incoming HBM production lot undergoes a gated qualification sequence before release to assembly:
**Gate 1 — Incoming Inspection (IQC)**: Visual/dimensional inspection per vendor drawing, certificate of conformance review, JEDEC mark verification. Wafer map data files (WDF) are reviewed for spatial yield patterns — edge die clustering exceeding 3-sigma is flagged as a potential process excursion.
**Gate 2 — Electrical Sample Test**: AQL sample drawn and tested at ATE (Advantest T2000 or Teradyne Magnum Epic are typical). Test coverage includes full JEDEC compliance, all mode registers (MR0–MR15), DRAM initialization sequence, pseudo-channel mode verification, and per-bank parametric measurements. Temperature cycling during test: nominal 25°C, then 0°C and 85°C corners.
**Gate 3 — Reliability Lot Monitor**: One lot per quarter (or one lot per qualification interval) subjected to accelerated reliability screens:
- HTOL (High Temperature Operating Life): JESD22-A108, 125°C/1000h, 77 devices minimum- ELFR (Early Life Failure Rate): Burn-in per JESD47 to screen infant mortality- Thermal Shock: JESD22-A106, −55°C to +125°C, 200 cycles- Autoclave / HAST: JESD22-A102, 121°C/100% RH/2atm, 96h for moisture resistance**Gate 4 — Statistical Release**: Lot data entered into SPC system. Western Electric rules applied to control charts. Any point outside ±3σ or two consecutive points outside ±2σ initiates a CAPA (Corrective and Preventive Action) before the lot can be released.


## PPAP Flows Adapted for HBM Supply Chain

The Production Part Approval Process (PPAP), originally defined in the automotive AIAG standard (4th Edition), has been adapted by the advanced packaging industry to manage first-article approval of HBM suppliers. The adapted HBM PPAP package typically requires the following elements:
- **Part Submission Warrant (PSW)**: Vendor declaration that all qualification requirements have been met. Must include lot traceability to the qualification lot, firmware/microcode revision, and PHY training parameter file version.- **Design Records**: JEDEC JESD235C compliance matrix, vendor datasheet (all AC/DC tables), and interposer bump map with pitch tolerances.- **Design FMEA (DFMEA)**: Risk analysis covering TSV open/short failure modes, bump bridging, and thermal delamination. All items with RPN > 100 must have associated design controls documented.- **Process FMEA (PFMEA) and Control Plan**: Manufacturing process controls for die-to-wafer bonding, underfill, and wafer sort. Control plan specifies inspection frequency, measurement method, and reaction plan for each critical characteristic (CC).- **Measurement System Analysis (MSA)**: Gauge R&R study on the ATE parametric measurements used for acceptance. Gage R&R &lt; 10% of tolerance required for critical parameters; 10–30% requires engineering justification.- **Initial Process Study (Cpk)**: First 3 qualification lots must demonstrate Cpk ≥ 1.67 on critical parameters before transitioning to production monitoring level.- **Sample Parts and Master Sample**: Retention samples from each qualification lot, stored at controlled conditions (25°C/50% RH), held for minimum 5 years or product life, whichever is longer.PPAP submission level (typically Level 3 for new suppliers) determines which documents are submitted vs. retained at the vendor site. Level 3 requires all elements to be submitted to the customer for approval before production shipments commence.


## KGD Qualification and Post-Package Repair Validation

HBM KGD qualification extends conventional DRAM qualification by adding wafer-level margin tests that must detect failures before die stacking — since rework of a bonded 2.5D stack is economically impractical. Key KGD-specific qualification elements:
**Wafer-Level Burn-In (WLBI)**: Elevated voltage stress at wafer sort (VDD = 1.35V, 125°C, 48h) to screen early-life failures that would otherwise escape to post-stack test. WLBI requires precision wafer chucks with per-die power delivery; current monitoring catches cell array defects invisible to DC parametric tests.
**TSV Continuity Qualification**: Statistical validation that TSV resistance distribution is within spec (typically &lt; 0.5Ω per TSV per the vendor datasheet). TSV opens detected at ≥10 ppm rate are a PPAP hold condition.
**Post-Package Repair (PPR) Validation**: JESD235C defines a PPR flow using mode registers `MR13` and `MR14` to program hard repair of failed rows into spare rows. PPR qualification must demonstrate that repair latency (tPPR ≤ 150ms) is met and that repaired units pass all functional tests with equivalent margin to unrepaired units.
**Configuration Register Audit**: All Mode Register reads (MR0–MR15) compared against the vendor golden reference file as part of incoming lot accept/reject. Any deviation in device ID, manufacturer ID (`MR4[7:5]`), or density field (`MR4[3:2]`) constitutes a non-conformance that requires immediate hold and supplier notification.


## Key Takeaways

- HBM lot qualification combines design qualification (3 lots, JESD47 confidence) with ongoing production monitoring via AQL 0.065–0.1 sampling and quarterly reliability lot monitors.
- Acceptance criteria require Cpk ≥ 1.33 on critical speed parameters and KGD wafer-sort yield ≥ 99.85% before lots are released to 2.5D assembly.
- The adapted HBM PPAP package must include PSW, DFMEA/PFMEA, Control Plan, Gauge R&R (< 10% of tolerance), and initial Cpk ≥ 1.67 from the first 3 qualification lots.
- TSV continuity, PPR flow validation, and Mode Register audits are KGD-specific qualifications that have no equivalent in conventional packaged DRAM qualification flows.
- HTOL (JESD22-A108, 125°C/1000h) and ELFR burn-in are the two mandatory reliability screens; thermal shock and HAST complete the standard qualification matrix.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C — Mode Registers MR0–MR15, PPR flow (Section 3.9), AC/DC specs (Section 6)
2. **[JEDEC]** Stress-Test-Driven Qualification of Integrated Circuits — JESD47 — Lot acceptance sampling, reliability qualification sample size requirements
3. **[JEDEC]** Temperature, Bias, and Operating Life — JESD22-A108 — HTOL test method, 125°C/1000h conditions for DRAM qualification
4. **[Web]** Sampling Procedures and Tables for Inspection by Attributes — ANSI/ASQ Z1.4 — AQL sampling plans, Code Letters and OC curves for incoming inspection
5. **[Book]** Production Part Approval Process (PPAP) 4th Edition — AIAG 2006 — 18 PPAP elements, submission levels 1–5, PSW requirements
6. **[JEDEC]** Highly Accelerated Stress Test (HAST) — JESD22-A110 — 130°C/85% RH/2atm conditions for moisture resistance qualification of HBM packages

## 🔍 Additional Learning: Adaptive Cpk Gates and SPC in HBM Lot Release

Modern HBM procurement contracts increasingly specify adaptive Cpk gates: the initial qualification threshold is Cpk ≥ 1.67, but lots shipped after 6 months of production history can be accepted at Cpk ≥ 1.33 if no excursions have been recorded — and must revert to 1.67 for 90 days if any CAPA is opened against that product family. Integrators implement this via real-time SPC dashboards that ingest per-lot parametric data from vendor-provided wafer acceptance test (WAT) reports, flagging shifts using Western Electric rules before individual measurements breach the 3σ limit. This early-warning capability typically detects process drift 2–4 lots earlier than conventional accept/reject testing, preventing escapes into 2.5D assembly.
