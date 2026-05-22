# HBM Power Architecture: VDD Domains & Power Gating

*Friday, May 22 2026*

*Module 1.7 — Foundations*

## Power Domains in an HBM Stack

HBM devices are partitioned into three primary supply domains:
- **VDD_CORE** – Supplies the internal core logic (PHY, controller, CRC). Typical range 0.8‑1.0 V.- **VDDQ_TX / VDDQ_RX** – Separate analog/digital supplies for the transmit and receive data I/O buffers. Each lane pair is powered by its own VDDQ domain (e.g., VDDQ_TX0, VDDQ_RX0) to reduce simultaneous switching noise (SSN).- **VPP (optional)** – High‑voltage bias for certain write‑assist features in some JEDEC‑compliant stacks.Each domain is isolated by on‑die LDOs or external PMIC regulators, enabling independent sequencing per JESD235‑C (Section 4.2).


## VDDQ Architecture and Timing

VDDQ is split per‑channel to support the 2 Gbps–4 Gbps per‑lane data rates defined in JESD235. The following registers control VDDQ sequencing (see Micron HBM2E datasheet, Table 5‑3):
- `VDDQ_TX_EN[n]` – Enables the transmit driver for channel <em>n</em>.- `VDDQ_RX_EN[n]` – Enables the receive driver for channel <em>n</em>.- `VDDQ_TURNON_T` – Minimum 10 ns turn‑on time before first data strobe.- `VDDQ_TURNOFF_T` – Minimum 5 ns hold after last transaction.Timing must satisfy the **tVDDQ_ON** and **tVDDQ_OFF** constraints to avoid DQ‑eye pattern violations during power‑up/down.


## Power‑Gating Schemes

Two principal gating strategies are used in HBM:
<ol>- **Fine‑grained per‑channel gating** – Each VDDQ_TX/RX pair can be independently disabled when a channel is idle, reducing standby power by up to 30 % (JEDEC JESD236‑B, Fig. 2‑12).- **Coarse‑grained core gating** – Entire VDD_CORE is power‑gated via a high‑Vt sleep transistor. Wake‑up latency is bounded by `tCORE_WAKE` ≤ 150 ns (HBM3 spec, Section 5.4).</ol>Implementation typically uses an external PMIC with separate enable pins for each domain, coordinated by the memory controller’s power‑management state machine.


## Impact on Test and Validation

During ATE validation, verify the following:
- Correct sequencing of `VDD_CORE` → `VDDQ_TX/RX` per JEDEC power‑up order.- Compliance of `tVDDQ_ON/TURNON_T` and `tVDDQ_OFF` with timing windows using high‑resolution (<1 ns) scope probes.- Leakage current of gated domains < 1 µA after full power‑down (per Micron HBM2E spec, Table 6‑1).- Absence of voltage droop on adjacent channels during simultaneous VDDQ turn‑on (SSN < 50 mV).Automated test patterns should toggle `VDDQ_EN` bits while capturing eye diagrams to confirm no degradation.


## Design Guidelines for Power Integrity

Key considerations to maintain signal integrity while using power gating:
- Route VDDQ supply planes with < 10 mΩ·cm resistance and < 2 mm decoupling spacing.- Place bulk‑decoupling capacitors (< 1 µF) within 200 µm of each VDDQ pin to meet `tVDDQ_ON` limits.- Use separate PDN domains for VDD_CORE and VDDQ to prevent cross‑talk; isolation capacitors (10 nF) recommended at the PMIC‑package interface.Follow JEDEC JESD235‑C power‑grid recommendations for stack‑level IR‑drop analysis.


## Key Takeaways

- HBM splits power into VDD_CORE and per‑channel VDDQ_TX/RX domains for noise isolation.
- JEDEC defines strict turn‑on/turn‑off timing (tVDDQ_ON/TURNON_T, tVDDQ_OFF) that must be met during gating.
- Fine‑grained per‑channel gating yields the highest power savings, but requires precise controller sequencing and PDN design.

## References

1. **[JEDEC]** JEDEC JESD235‑C: High‑Bandwidth Memory (HBM) Standard — Section 4.2 Power Domains, Section 5.4 Power‑Gating Timing
2. **[JEDEC]** JEDEC JESD236‑B: Low‑Power HBM Power Management — Figure 2‑12 Power‑Gating Architectures
3. **[Datasheet]** Micron HBM2E Datasheet — Table 5‑3 Register Map, Table 6‑1 Leakage Specs
4. **[Web]** Samsung HBM3 Product Brief — https://www.samsung.com/semiconductor/global/images/technology/hbm3.pdf
5. **[IEEE]** K. Wu et al., “Power‑Gating Techniques for 3D‑Stacked DRAM,” IEEE JSSC, 2023 — pp. 1125‑1134

## 🔍 Additional Learning: Dynamic VDDQ Voltage Scaling for Energy‑Efficient Operation

Recent HBM3 revisions allow the memory controller to down‑scale VDDQ_TX/RX in steps of 50 mV during low‑traffic periods, reducing dynamic power by up to 15 % without compromising eye‑height. Implementations require real‑time monitoring of link utilization and adaptive voltage regulation via a fast‑response PMIC.
