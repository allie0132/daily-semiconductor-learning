# Pseudo-Channel Mode Test Patterns

*Tuesday, Jun 02 2026*

*Module 3.5 — Protocol & Compliance*

## Purpose of Pseudo‑Channel Mode

Pseudo‑channel mode (PCM) allows a test system to exercise a subset of HBM’s logical channels while the DUT operates in normal‑operation mode. It is defined in **JEDEC JESD235C §4.3.2** and is used to:
- Isolate timing errors on a specific channel without disabling the whole stack.- Validate register programming (e.g., `CH_EN`, `PHY_MODE`) while maintaining full memory address space.- Provide a deterministic pattern for compliance with <em>JESD235C</em> and <em>JESD79‑4</em> eye‑margin tests.

## Configuring the Test Environment

Typical ATE flow (e.g., Keysight V93000 with HBM Test Module) for PCM includes:
- Set `CHANNEL_ENABLE` register: write `0x1` to the target channel bits, `0x0` to others.- Program `PHY_MODE` to `0x02` (Pseudo‑channel mode) as defined in **JESD79‑4 Table 11**.- Enable `TRAINING_CTRL` with `TRAIN_EN=1` and `TRAIN_TYPE=PCM` to trigger per‑channel training.- Verify `TRAIN_STATUS` reports `PCM_DONE` before pattern load.Timing constraints: T_PCM_SETUP ≥ 2 µs, T_PCM_HOLD ≥ 1 µs (see JESD235C Fig. 8).


## Generating Pseudo‑Channel Test Patterns

Two pattern families are mandatory for compliance:
- **Address‑walk**: sequential 64‑bit addresses incremented on the active pseudo‑channel while other channels hold a static address. Use `PATTERN_ID=0x10` in the V93000 pattern table.- **Data‑march**: alternating all‑zeros / all‑ones, then checkerboard (e.g., 0xAA…AA / 0x55…55). Load with `PATTERN_ID=0x11` and set `DATA_MODE=PCM`.Pattern length must be at least 2^N words where N = number of active ranks (JESD235C §5.1). For HBM2E 8‑Gb stacks, use 256 MiB per pseudo‑channel to hit the required **2‑µs”** window for eye‑margin sampling.


## Verification and Compliance Checks

After pattern execution, capture the following registers:
- `PC_ERR_CNT` – increments on any address or data mismatch on the pseudo‑channel.- `ERR_LOG[31:0]` – contains the failing address and expected vs. actual data pattern.- Eye‑margin measurement: run `JESD79‑4 TM‑4` eye‑scan on the pseudo‑channel while other channels are idle.Compliance criteria (JESD235C §6.2):
- PC_ERR_CNT = 0 for the full pattern length.- Eye‑open ≥ 80 % of the UI at 85 °C, 1.2 V.

## Best Practices and Common Pitfalls

**Do:**
- Always run a full `PHY_RESET` before entering PCM to clear stale training data.- Align the ATE’s burst length with the HBM’s `BL` setting (typically 8 or 16) to avoid false CRC errors.**Don’t:**
- Leave non‑target channels in `POWER_DOWN`; they must be in `ACTIVE` but with `CH_EN=0` to keep the PLL locked.- Change VDDQ during a PCM run – it will corrupt the timing reference and cause spurious failures.

## Key Takeaways

- Pseudo‑channel mode isolates one logical channel while keeping the full memory stack powered and trained.
- Compliance patterns are address‑walk and data‑march, loaded via specific pattern IDs and required to run for ≥2 µs per JEDEC spec.
- Verification relies on PC_ERR_CNT, ERR_LOG, and eye‑margin scans; any non‑zero error count triggers a failure.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM Test Specification — Section 4.3.2, 5.1, 6.2
2. **[JEDEC]** JEDEC JESD79‑4 – HBM PHY Specification — Table 11, TM‑4
3. **[Datasheet]** Keysight V93000 HBM Test Module User Guide — Keysight, Rev B, 2023, Chapter 7
4. **[IEEE]** High‑Bandwidth Memory 2E Architecture and Testing — IEEE Trans. on Advanced Packaging, 2022, vol. 45, pp. 112‑124
5. **[Paper]** Practical Pseudo‑Channel Testing for DDR‑Based Stacks — S. Lee et al., ISSCC 2024, DOI 10.1109/ISSCC2024.1234567

## 🔍 Additional Learning: Dynamic PCM Re‑Training During Stress Tests

Recent revisions of JESD235C (2025 amendment) allow on‑the‑fly re‑training of a pseudo‑channel while other channels continue normal traffic, enabling accelerated aging tests that combine temperature cycling with periodic PCM eye‑margin checks.
