# HBM Channel Architecture: 8-Channel & Pseudo-Channel

*Thursday, May 21 2026*

*Module 1.4 — Foundations*

## HBM Channel Organization Overview

HBM2E (JESD235B/C) implements **8 independent channels** per DRAM die, each carrying a **128-bit data bus** (DQ[127:0]). Channels CH0–CH7 each have their own dedicated command/address (CA) bus, data bus, and control signals. They are physically isolated through the TSV array in the stack.
Aggregate per-stack bandwidth example for an 8-Hi HBM2E stack at 3.2 Gbps per pin:
- `8 channels × 128 bits × 3.2 Gbps / 8 = 409.6 GB/s`- Each channel contributes `128 × 3.2G / 8 = 51.2 GB/s`Channel independence is critical for test: a defect in CH3 does not affect CH5. ATE must independently stress-test all 8 channels with independent timing closure per channel.


## Pseudo-Channel Architecture (JESD235C §3.7)

Introduced in HBM2 (JESD235A), the **pseudo-channel (PC)** splits each 128-bit channel into two independent **64-bit pseudo-channels** — PC0 and PC1. Each pseudo-channel has its own:
- Row/column address space- Bank and bank-group selects- 64-bit data bus with independent DBI and ECC (64b data + 8b ECC = 72b physical)Commands are time-multiplexed on the shared CA bus using **CAS_A** and **CAS_B** slots. `CS_n[1:0]` differentiates PC0 vs PC1 targeting within the same channel. This effectively doubles the addressable bank count from the host memory controller's perspective, improving bank-level parallelism.
Pseudo-channel mode is enabled via **MR3[3]=1**. Most production stacks have this fused on; test programs must verify MR state before applying PC-aware address patterns.


## Bank & Bank-Group Structure Per Pseudo-Channel

Within each pseudo-channel, HBM2E organizes DRAM cells into **bank groups** to enable back-to-back access without full bus turnaround:
- 4 bank groups (BG0–BG3) × 4 banks each = **16 banks per pseudo-channel**- Total per channel: **32 banks** (2 PC × 16)- `tRRD_L` (same bank group): 3 nCK minimum- `tRRD_S` (different bank group): 2 nCK minimum- `tCCD_L` (same PC, different BG): 2 nCK- `tCCD_S` (different PC): 2 nCKBank-group interleaving allows pipelining `ACT → RD → ACT → RD` across groups without stalling on `tRAS` or `tRP`. This is the key mechanism enabling sustained peak bandwidth.


## Command/Address (CA) Bus Encoding

Each HBM channel uses a **7-bit CA bus** (CA[6:0]) clocked at the command rate. Commands use 2-cycle encoding:
- **ACT (Activate):** CA[5:0] carries row address RA[14:0] across two clock edges; CA6 selects bank group high bit- **RD/WR:** CA[6:0] encodes column address CA[4:0], auto-precharge flag, and bank selects- **MRS:** Mode Register address on CA[6:2], data on CA[1:0] extended to data pinsThe pseudo-channel select uses `CS_n[1]` for PC1 and `CS_n[0]` for PC0 within the channel. Both can be asserted simultaneously for broadcast writes (e.g., during ZQ calibration or MRS broadcast). Timing of CA setup/hold to CK_t/CK_c is specified as `tIS`/`tIH` in the JEDEC AC parameter table.


## Test Strategy: Per-Channel & Per-Pseudo-Channel Verification

For a complete HBM stack test, the ATE must independently exercise all 8 channels and both pseudo-channels within each:
- **Channel isolation:** Apply patterns to one channel at a time; verify no coupling on adjacent channels via `DQ` leakage checks- **PC isolation:** Assert `CS_n[0]` only, then `CS_n[1]` only; confirm independent bank-state tracking and no cross-PC address aliasing- **Bank-group boundary timing:** Sweep `tRRD_L` and `tRRD_S` at ±10% margin; failures indicate sense-amp sharing or BG decode faults- **ZQ calibration:** Run independently per channel — `ZQCAL` is a per-channel broadcast; verify `ZQ` pin impedance converges within ±10% of target (typically 40 Ω pull-down)- **Vref calibration:** Per-pseudo-channel `VREFDQ` training must be performed independently; shared Vref errors cause asymmetric bit failures- **Row hammer stress:** Target bank-group boundaries within a PC to maximize aggressor-victim row adjacency across the wordline decoder

## Key Takeaways

- HBM2E provides 8 independent 128-bit channels per die, each split into two 64-bit pseudo-channels via JESD235C pseudo-channel mode (MR3[3]=1).
- Pseudo-channels share the CA bus through time-multiplexed CAS_A/CAS_B slots and CS_n[1:0] select, while maintaining independent data paths, ECC, and bank-group structures (16 banks per PC, 32 per channel).
- ATE test programs must independently verify all 8 channels and both pseudo-channels: channel isolation, bank-group timing margins (tRRD_L/S, tCCD_L/S), ZQ, and per-PC Vref calibration are the critical test axes.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM JESD235C — JEDEC Standard JESD235C (2021), Sections 3.7 (pseudo-channel), 4.2 (CA bus encoding), 5.3 (AC parameters tRRD, tCCD)
2. **[Paper]** HBM2E Architecture and Performance Characterization — Lee et al., IEEE Journal of Solid-State Circuits, Vol. 56, No. 1, 2021 — channel organization, bank-group timing, pseudo-channel ECC implementation
3. **[Datasheet]** SK Hynix HBM2E Product Specification (H5VR32ESM) — SK Hynix, Rev. 1.1, 2020 — per-channel AC/DC parameters, ZQ calibration procedure, MR3 pseudo-channel enable
4. **[Book]** Memory Systems: Cache, DRAM, Disk — Jacob, Ng, Wang — Elsevier/Morgan Kaufmann, 2008, Chapter 11 — bank-group architecture principles (foundational for HBM extensions)
5. **[Paper]** HBM Testing Challenges on Modern ATE Platforms — Aitken et al., IEEE International Test Conference (ITC) 2020 — per-channel parametric test coverage, pseudo-channel isolation methodology
6. **[Datasheet]** Samsung HBM2E (K4ZAF325BM) Datasheet — Samsung Electronics, Rev. 1.0, 2020 — 8-channel TSV assignment map, per-channel Vref training algorithm, ECC architecture

## Additional Learning: Pseudo-Channel ECC: Per-PC Protection and Fault Isolation

Each 64-bit pseudo-channel in HBM2E carries its own 8-bit ECC field, forming a 72-bit SEC-DED (Single Error Correct, Double Error Detect) codeword per pseudo-channel. This means a single-bit fault in PC0 is corrected independently of PC1 — the error syndrome is computed over 64 data bits plus 8 check bits within that half-channel. During ATE test, injecting known single-bit errors via write-invert patterns and verifying the ECC correction register (accessible via MR32 readback) is the standard method to validate ECC hardware function per pseudo-channel without relying on the system-level error log.
