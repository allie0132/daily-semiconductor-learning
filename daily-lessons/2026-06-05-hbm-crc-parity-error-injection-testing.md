# HBM CRC & Parity Error Injection Testing

*Friday, Jun 05 2026*

*Module 3.10 — Protocol & Compliance*

## Why CRC & Parity Matter in HBM

HBM (JEDEC JESD235) uses a 32‑bit CRC for each data burst and a 1‑bit parity per DQ lane to detect transmission errors. The CRC protects the entire 128‑bit payload plus command header, while parity catches single‑bit flips on the physical lane. A failure triggers `BC_ERR` and forces the controller to re‑issue the transaction.


## Injection Points and Mechanisms

Most ATE platforms (e.g., Advantest V93000, Teradyne T2000) provide
- **Bit‑flip injection** via programmable data mask registers (DMR) on the DUT or on the test head.- **CRC seed manipulation** using the `HBM_CRC_SEED` register (offset 0x8004) to force a mismatch.- **Parity error forcing** by toggling the `PAR_ERR_EN` bit in the `HBM_ERR_CTRL` register (offset 0x8010).Inject at the start of a burst to avoid re‑synchronization delays.


## Test Flow and Timing

Typical flow (per JEDEC JESD236 §5.3):
<ol>- Configure the memory controller for a known pattern (e.g., `0xAA55AA55`).- Read back the pattern to verify baseline CRC/parity pass.- Enable error injection: set `DMR[i]=1` for the target bit or write a mismatched seed.- Issue a READ command; capture `BC_ERR` flag and `ERR_STATUS` register values.- Clear injection, repeat for each lane and CRC polynomial variant.</ol>Timing: the error must be presented within the `tRC` window (max 10 ns after `CKE` de‑assert) to be caught by the internal CRC engine.


## Analyzing Results

Use the following registers to confirm detection:
- `HBM_ERR_STATUS[15:0]` – bit‑mask of failing lanes.- `HBM_CRC_ERR_CNT` – increments only on CRC mismatches.- `HBM_PAR_ERR_CNT` – increments on parity failures.Cross‑check the ATE’s capture of the transmitted burst against the expected CRC (polynomial 0x04C11DB7) to verify that the injected error is the one reported.


## Best Practices & Pitfalls

**Do not inject errors on the same lane consecutively** – some controllers debounce multi‑error flags.
**Verify clock jitter** before injection; excessive jitter can mask CRC failures (see JESD235 §4.4).
**Document the seed value** used for each test vector; reproducibility requires the same `HBM_CRC_SEED` across runs.


## Key Takeaways

- HBM CRC (32‑bit) and per‑lane parity are mandatory error‑detect mechanisms defined in JESD235.
- Error injection is performed via data‑mask registers, CRC seed overrides, or parity‑error enable bits.
- Validate detection using HBM_ERR_STATUS, CRC_ERR_CNT, and PAR_ERR_CNT registers, ensuring timing within tRC.

## References

1. **[JEDEC]** JEDEC JESD235C – HBM Standard — Section 4.2 (CRC), Section 5.3 (Error Handling)
2. **[JEDEC]** JEDEC JESD236 – HBM Protocol Compliance — Section 5 (Test Methodology)
3. **[Web]** Advantest V93000 HBM Test Guide — https://www.advantest.com/hbm-testing-guide
4. **[IEEE]** IEEE 802.3 – CRC Polynomial Usage — IEEE Std 802.3-2018, Clause 3.5
5. **[Book]** Memory System Design, 2nd Ed., R. Quarles — Chapter 7, CRC & Parity in High‑Bandwidth Memory

## 🔍 Additional Learning: Dynamic CRC Rerun for Fault Isolation

Recent HBM 3.0 controllers support a ‘CRC rerun’ command (JESD235 §6.2) that recomputes the CRC on a stored burst without a full read, enabling fast isolation of transient vs. permanent faults.
