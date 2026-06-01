# HBM Init & Training Sequence Testing

*Monday, Jun 01 2026*

*Module 3.3 — Protocol & Compliance*

## Overview of the HBM Init/Training Flow

The HBM initialization sequence consists of Power‑On Reset (POR), DRAM Reset, PHY Reset, DRAM Init, DFI Init, and the Training phases (Write Leveling, Read‑Leveling, Eye‑Height, and Data‑eye). Each step is defined in JESD235C §5 and must be exercised in the exact order to achieve a compliant link.


## Key Registers and Timing Parameters

Critical registers accessed via the DFI (DisplayPort Frame Interface) include:
- `DFI_INIT_COMPLETE` – set by PHY after `DFI_INIT_START` is asserted.- `DRAM_MODE_REG[0‑3]` – mode‑register programming for burst length, CAS latency, etc.- `TRAINING_CTRL` – bits 0–3 select training type (WL, RL, etc.).Key timing values (JESD235C §5.3):
- t\_RST\_POR = 100 µs minimum.- t\_INIT = 2.5 ms max for DRAM init.- t\_WL\_MAX = 16 UI for write‑leveling.

## Test Vector Generation and Sequencing

Use ATE patterns that drive the DFI host controller to:
- Assert `DFI_INIT_START`, poll `DFI_INIT_COMPLETE`.- Program mode registers via `MRS` command bursts.- Initiate training by writing `TRAINING_CTRL` with the appropriate sub‑mode.- Capture eye‑margin data from the PHY’s built‑in BIST (BIST\_STATUS, BIST\_ERR\_COUNT).All vector timing must respect the UI‑grained delays defined in JESD235C Table 19 (e.g., t\_WL\_setup = 4 UI).


## Verification Metrics and Pass/Fail Criteria

After each training loop, evaluate:
- Write‑Leveling DQD alignment error < 1 UI (JESD235C 5.6.1).- Read‑Leveling DQS eye > 6 UI (minimum margin). - Eye‑Height > 0.8 Vref and eye‑width > 8 UI.- BER ≤ 10⁻⁹ measured over 10⁶ bits at each speed bin.If any metric fails, repeat the training loop with adjusted timing offsets (t\_WL\_inc/t\_WL\_dec) until convergence or declare a defect.


## Common Pitfalls and Debug Strategies

Typical failure modes include:
- Insufficient POR time causing incomplete DRAM reset – increase t\_RST\_POR.- Incorrect mode‑register values – verify against the device data sheet.- PHY PLL lock instability – monitor `PLL_LOCK` and ensure VDDIO meets spec.Use the ATE’s high‑resolution time‑domain capture to overlay DFI command timing with PHY clock edges, pinpointing skews that exceed the 0.1 UI jitter budget.


## Key Takeaways

- Follow the exact JESD235C order: POR → DRAM reset → PHY init → DRAM init → training.
- Validate all timing margins against the UI‑based limits in the standard.
- Leverage built‑in PHY BIST and eye‑monitoring to close training loops efficiently.

## References

1. **[JEDEC]** JEDEC JESD235C: HBM2E Physical Layer Specification — Section 5 (Init & Training), Table 19 (timing), 2023
2. **[Datasheet]** Micron HBM2E Datasheet – MT62K256M32L — MMB‑15‑0001, timing tables, mode register map
3. **[IEEE]** IEEE 2022 – “Low‑Power Calibration Techniques for HBM PHYs” — doi:10.1109/TCAD.2022.3157092
4. **[Book]** Cadence Incisive Xpress – DDR PHY Verification Guide — Cadence Press, 2021, Ch. 8
5. **[Web]** TSMC 2.5‑Die‑Stack HBM Integration Note — https://www.tsmc.com/english/die-stack/hbm_note.pdf

## 🔍 Additional Learning: ML‑Based Adaptive Training for HBM2E

Recent research (IEEE Access 2024) demonstrates a reinforcement‑learning controller that dynamically adjusts WL/RL offsets during runtime, reducing training iterations by 30 % while maintaining BER <10⁻⁹. Integrating such an algorithm into the ATE’s pattern generator can automate convergence checks.
