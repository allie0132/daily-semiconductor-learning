# HBM Defect Mechanism Analysis: EM, TDDB, Retention

*Wednesday, Jun 24 2026*

*Module 7.2 — Advanced Test Methodologies*

## Electromigration in TSVs and Microbumps

Electromigration (EM) induces void formation in high‑current TSVs and Cu microbumps, leading to increased resistance and open circuits. Failure is modeled by Black's equation: MTTF = A·J^−n·exp(Ea/kT). In HBM2E/3, typical current density J > 10^6 A/cm^2 in TSVs under peak I/O bursts. Monitoring via IDDQ stress and resistance drift during burn‑in is standard.
- Critical TSV dimensions: 5‑10 µm diameter, aspect ratio >10:1.- Failure criteria: ΔR > 20% or open detection at Vtest > 1.2 V.

## Time‑Dependent Dielectric Breakdown (TDDB) in Deep‑Trench Capacitors

The deep‑trench capacitor dielectric (SiO2/SiON stack) experiences TDDB under repeated activation pulses. Breakdown follows Weibull distribution with slope β≈1.2. Acceleration factor AF = exp[(Ea/E0)(1/Eox - 1/Eox0)]. For HBM3, Eox ≈ 1.5 MV/cm during refresh, giving TDDB lifetime >10^12 s at 85°C.
- Test method: constant voltage stress (CVS) at 1.8 V for 10^4 s, monitor leakage increase.- Acceptance: ΔIleak < 10 nA after stress.

## Charge Retention Failure in Stacked DRAM Cells

Retention loss stems from charge leakage through the access transistor and capacitor dielectric, exacerbated by temperature and data pattern sensitivity. Retention time t_ret = C·V / I_leak. In HBM2E, typical I_leak ≈ 1‑5 fA/cell at 85°C, giving t_ret > 64 ms. Failures appear as pattern‑dependent bits after extended refresh intervals.
- Refresh margin test: reduce tREFI to 16 ms, capture error bits.- Pattern worst‑case: 0xAAAA (alternating) maximizes leakage path.

## Combined Stress Test Flow for HBM Stacks

A typical production test flow combines EM, TDDB, and retention stressors: (1) High‑temperature operating life (HTOL) at 125 °C, 1.35 V VDDQ for 168 h to accelerate EM/TDDB; (2) Post‑HTOL IDDQ and resistance measurement; (3) Low‑voltage retention test at 85 °C with tREFI = 32 ms; (4) Failure analysis via EBIC and TEM on suspect TSVs.
Equipment: Advantest V93000 with SMU modules, Keithley 2400 for IV, and Thermotron thermal chambers.


## Failure Diagnosis Techniques

When a defect is detected, combine electrical signatures with physical analysis: - EM: rising resistance + IR‑drop localization via microprobe scanning.- TDDB: sudden leakage jump at constant voltage, corroborated by TDDB Weibull plot.- Retention: data‑dependent errors refreshed at reduced tREFI, verified by charge‑pumping measurements.


## Key Takeaways

- EM in TSVs follows Black's equation; monitor resistance drift during burn‑in.
- TDDB in deep‑trench capacitors is Weibull‑distributed; use constant‑voltage stress to qualify.
- Retention failures are pattern‑ and temperature‑sensitive; reduced tREFI stress reveals weak cells.
- Integrated HTOL + IDDQ + retention test flow efficiently screens all three mechanisms.
- Failure diagnosis requires correlation of electrical drift with micro‑probe EBIC/TEM.

## References

1. **[JEDEC]** JESD235C: High Bandwidth Memory (HBM) DRAM — Section 4.2 – Electrical specifications and stress test conditions
2. **[Paper]** Black's Equation for Electromigration Reliability — J. Appl. Phys. 1969, 30, 1303
3. **[IEEE]** TDDB Modeling of Deep‑Trench Capacitors in 3D‑DRAM — IEEE TED, vol. 68, no. 4, pp. 2100‑2109, 2021
4. **[Datasheet]** HBM3 Reliability White Paper — Samsung Electronics, Rev. 1.0, 2023, Section 5.1 – EM/TDDB/Retention
5. **[Book]** Failure Analysis of 3D‑Stacked DRAM using EBIC and TEM — Springer, "Advanced Semiconductor Packaging", Chap. 7, 2022
6. **[Web]** Advantest V93000 SMU Module Application Note — https://www.advantest.com/appnote/v93000_smu_hbm

## 🔍 Additional Learning: In‑situ Resistance Monitoring During HTOL

Recent HBM3 production lines embed on‑die sense resistors adjacent to TSVs to capture real‑time EM‑induced resistance shift during high‑temperature operating life. This enables dynamic adjustment of test duration and early detection of outliers before final test, reducing yield loss by up to 15%.
