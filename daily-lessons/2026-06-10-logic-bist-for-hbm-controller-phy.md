# Logic BIST for HBM Controller & PHY

*Wednesday, Jun 10 2026*

*Module 4.8 — DFT & Built-In Test*

## Why Logic BIST is Mandatory for HBM

HBM stacks operate at >2.4 GHz I/O and 8‑12 Gb/s per lane, making manual pattern testing impractical. Logic BIST (Built‑In Self‑Test) provides:
- Fast coverage of **controller state machines** (command decoder, address mapper, arbiter).- Automatic verification of **PHY lane alignment, DQS/DQ timing, and per‑lane equalization** under nominal and stressed conditions.- Deterministic fault injection points for yield learning and field diagnostics.

## BIST Architecture Overview

A typical HBM controller BIST consists of three blocks:
- **Pattern Generator (PG)**: configurable LFSR/PRBS7, PRBS15, or custom command sequences, instantiated in the controller RTL.- **Signature Analyzer (SA)**: MISR (Multiple‑Input Shift Register) that compresses the response stream; final MISR value is compared to a golden signature stored in eFuse.- **Control & Observation Interface**: JTAG or ATE‑specific DFT pins (e.g., `TBIST_EN`, `TBIST_MODE`, `TBIST_SIG`) that start/stop BIST, select pattern, and read back signatures.The PHY BIST mirrors this structure but operates on the high‑speed serdes side, using built‑in eye‑margin monitors (EMMs) and PRBS checkers per lane.


## Integration with JEDEC HBM Test Flows

JEDEC JESD235C defines the <em>HBM Controller Test Specification</em> and mandates BIST coverage of at least 95% of controller FSM states. Key registers:
- `HBM_BIST_CTRL` (0x8000_0010) – bits 0: enable, 1: select PRBS7/PRBS15, 2‑4: lane mask.- `HBM_BIST_STATUS` (0x8000_0014) – bits 0: busy, 1: fail, 2‑7: error code.- `HBM_BIST_SIG_REF` (0x8000_0018) – reference MISR signature per pattern.During ATE pre‑qualification, the test program writes `HBM_BIST_CTRL`, polls `HBM_BIST_STATUS`, then reads back the computed signature via `HBM_BIST_SIG_REF` for comparison.


## PHY‑Level BIST Considerations

PHY BIST must be able to test both the transmitter (TX) and receiver (RX) paths:
- TX BIST inserts a PRBS pattern into the `PHY_TX_DATA` registers and monitors eye‑margin using the internal `EMM` block. Failure thresholds are defined in JESD235‑B §4.3 (e.g., eye width ≥ 0.8 UI at 1e‑12 BER).- RX BIST captures incoming traffic, runs a parallel PRBS checker, and reports lane‑by‑lane error counts via `PHY_RX_ERR_CNT[15:0]`.- Cross‑connect BIST loops TX to RX within the same die for calibration without external memory.Timing: BIST runs at the maximum supported data rate (e.g., 3.2 Gb/s per lane for HBM3) and must complete within 10 µs to meet test‑time budgets.


## Debug and Failure Isolation

When a BIST signature mismatch occurs, the following hierarchy isolates the fault:
<ol>- **Controller Signature Compare** – mismatch indicates FSM or address translation error.- **PHY Lane Error Counter** – non‑zero `PHY_RX_ERR_CNT` points to serdes or PCB‑trace issues.- **EMM Margin Report** – eye‑margin below spec identifies equalization or Vref mis‑settings.</ol>All BIST results can be streamed over the `TBIST_LOG` interface to the ATE for root‑cause analysis, reducing debug cycles from days to hours.


## Key Takeaways

- Logic BIST provides deterministic, high‑coverage testing of HBM controller and PHY at full data rates.
- JEDEC JESD235C registers and signatures must be integrated into the ATE flow for automated pass/fail.
- PHY BIST combines PRBS generation, eye‑margin monitoring, and loopback to isolate link‑level defects quickly.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM Controller Test Specification — Section 4.2, 4.3, 5.1 (2023).
2. **[IEEE]** IEEE Std 1500‑2022 – Embedded Core Test (ECT) Standard — Provides guidelines for MISR and BIST integration.
3. **[Datasheet]** SK Hynix HBM3 Datasheet – PHY BIST Features — Rev 1.2, pages 56‑62, 2024.
4. **[Paper]** M. Gupta et al., “High‑Speed PHY BIST for Multi‑Stack HBM3,” IEEE Transactions on VLSI Systems — Vol. 32, no. 5, 2024.
5. **[Web]** Cadence Design Systems, “Designing Logic BIST for DDR & HBM Controllers,” Application Note AN-1225 — https://www.cadence.com/an-1225

## 🔍 Additional Learning: On‑Chip Adaptive BIST for Run‑Time Health Monitoring

Recent HBM3 revisions embed an Adaptive BIST engine that continuously samples lane eye‑margin during normal operation and raises a hot‑spot flag when margins dip below 0.6 UI, enabling proactive fail‑over without external test.
