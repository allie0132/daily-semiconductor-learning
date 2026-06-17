# HBM Burn‑In & HTOL Reliability Screening

*Wednesday, Jun 17 2026*

*Module 5.7 — ATE & Production*

## Why Burn‑In & HTOL for HBM?

HBM stacks contain multiple DRAM dies, TSVs, microbumps, and an interposer. Early‑life failures (infant mortality) often stem from dielectric breakdown, micro‑cracks in TSVs, or solder joint fatigue. Burn‑in and High‑Temperature Operating Life (HTOL) accelerate these mechanisms to screen out weak parts before shipment.
**Key failure mechanisms:**
- Electromigration (EM) in TSV copper pillars- Time‑Dependent Dielectric Breakdown (TDDB) in low‑k dielectrics- Solder joint creep and micro‑crack propagation- Stress‑induced leakage current (SILC) in gate oxides of peripheral logic

## Burn‑In Test Flow on Modern ATE

Typical flow on a Teradyne UltraFLEX or Advantest T2000:
- `Pre‑test`: Apply 0.9 V to VDDQ, run a full memory test (March‑C, BIST) for 10 s to verify functionality.- `Stress phase`: Ramp VDDQ to 1.15× nominal (≈1.15 V for DDR5‑HBM2E) and temperature to 125 °C (or 130 °C for low‑k). Keep active refresh cycles (e.g., 64 ms refresh) and a mixed read/write pattern (70 % read, 30 % write) for 48 h.- `Post‑stress`: Return to room temperature, repeat full memory test. Log any address failures, ECC error count, and eye‑diagram drift on the command/address bus.Note: For HBM2E, JEDEC JESD235C recommends a minimum 72 h burn‑in at 150 °C for stacked dies, but many fabs use 48 h at 125 °C to balance throughput.


## HTOL Stress Conditions Specific to HBM

HTOL differs from burn‑in by extending time and adding voltage overstress. Recommended conditions (per JEDEC JESD236B):
- **Voltage:** 1.3× VDDQ for DRAM cores; 1.2× VDD for logic and PHY.- **Temperature:** 150 °C ±5 °C for >1 000 h (typical 1 020 h) on a temperature‑controlled oven.- **Pattern:** Pseudo‑random read/write with periodic full‑array refresh; include 2‑ns toggling on DQ pins to stress I/O drivers.- **Power cycling:** 10 % duty‑cycle power‑off/on every 12 h to accelerate thermal‑mechanical fatigue.Data collection includes retention failure count, DRAM band‑width degradation, and on‑die temperature sensor (TSENSOR) drift.


## Data Analysis & Acceptance Criteria

Use Weibull analysis on time‑to‑failure (TTF) data. For HBM, the industry target is a 10‑year MTBF at 85 °C/85 % RH, which translates to a Weibull slope (β) > 1.5 and a characteristic life (η) > 5 000 h under HTOL conditions.
- Calculate acceleration factor (AF) via Arrhenius model: `AF = exp[(E_a/k)(1/T_use - 1/T_stress)]`, with activation energy E_a ≈ 0.7 eV for copper TSV EM.- Apply AF to convert HTOL TTF to use‑phase TTF.- Reject parts with any failure before 100 h at stress or with >0.01 % ECC error rate increase.

## Practical Tips for ATE Integration

HBM test sockets must maintain **≤5 mΩ** contact resistance to avoid heating hot‑spots. Use compliant micro‑bump adapters with `Au‑Sn` alloy to match solder‑ball CTE. Calibrate on‑die temperature sensors against a calibrated RTD on the socket before each batch.
When programming the ATE, employ `SGP` (stress‑generation pattern) macros that stagger refresh commands across the four channels to evenly load the interposer.


## Key Takeaways

- Burn‑in and HTOL are complementary: burn‑in catches early surface failures, HTOL stresses long‑term mechanisms.
- JEDEC JESD235C/JESD236B define voltage, temperature, and time targets; adhere to them for qualified reliability data.
- Weibull analysis with proper acceleration factors converts HTOL results to field MTBF predictions.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM2E Standard, Section 6.5 Burn‑In — JESD235C, 2022
2. **[JEDEC]** JEDEC JESD236B – Stress Test Methodology for DRAM — JESD236B, 2021
3. **[IEEE]** High‑Temperature Operating Life of 3D‑Stacked DRAM — IEEE Trans. Device Mol. Syst., 2023, vol. 12, pp. 145‑152
4. **[Paper]** Thermal‑Mechanical Modeling of TSVs in HBM — K. Lee et al., IEDM 2022, pp. 381‑384
5. **[Web]** Teradyne UltraFLEX HBM Test Solution User Guide — https://www.teradyne.com/ultraflex-hbm-guide.pdf

## 🔍 Additional Learning: Machine‑Learning‑Based Failure Prediction for HBM HTOL

Recent work integrates real‑time sensor data (on‑die temperature, voltage ripple) with a convolutional neural network to predict imminent failure 12 h before the first error, enabling early cut‑off and yield improvement.
