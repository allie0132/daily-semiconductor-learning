# HBM Command Truth Table & Illegal Command Testing

*Thursday, Jun 04 2026*

*Module 3.7 — Protocol & Compliance*

## HBM Command Bus Architecture and CA Encoding

HBM uses a **command/address (CA)** bus that is 10-bits wide (CA[9:0]) per pseudo-channel, clocked on both rising and falling edges of CK (DDR command bus). Each command is defined by a specific encoding of `CA[9:0]` sampled at the rising edge, with select commands using a two-cycle encoding sequence called **CMD0/CMD1**. The **command truth table** (JESD235C Table 5-1) specifies valid CA[9:0] values for every DRAM command: ACTIVATE, READ, WRITE, PRECHARGE, REFRESH, MODE REGISTER SET/READ, SELF REFRESH ENTRY/EXIT, and POWER DOWN.
Commands are grouped into four categories: **bank commands** (require bank address BA[3:0] and row/column address), **all-bank commands** (e.g., REFab applies to all banks simultaneously), **per-bank commands** (e.g., REFpb targets one bank), and **NOP**. The encoding of CA[9] serves as the command-group discriminator: CA[9]=0 selects the first command set (ACT, NOP, DES), while CA[9]=1 selects the extended set.
- CA[9:7] decode the primary command opcode- CA[6:0] carry bank address, row/column address, or mode register payload depending on command- Two-cycle commands latch CMD0 at rising edge, CMD1 at falling edge of the same CK cycle

## Valid Command Sequences and Timing Constraints

The JESD235C command truth table defines not only the bit encodings but also the **valid predecessor commands**. Commands have mandatory inter-command gaps governed by timing parameters: **tRCD** (ACT to READ/WRITE), **tRP** (PRECHARGE to ACT), **tRAS** (minimum ACT-to-PRECHARGE), and **tRC** (row cycle time = tRAS + tRP). Violating any of these by issuing a follow-on command too early is the definition of an **illegal command sequence**.
A critical distinction: an **illegal command encoding** (undefined CA bit pattern) differs from an **illegal command sequence** (valid command issued at wrong time or wrong bank state). Both must be tested, but they trigger different DRAM behaviors. JESD235C Section 11 (Command Sequencing Rules) defines the complete state machine, including which commands are valid from each bank state: **Idle, Active (row open), Precharge Pending**.
- **ACT to ACT same bank**: requires tRC gap — violation is an illegal sequence- **WRITE to READ**: requires Write Latency + Burst Length + tWTR gap- **READ to PRECHARGE**: requires CAS Latency + Burst Length + tRTP- Issuing REFab while any bank is Active is an illegal sequence per JESD235C Table 11-1

## Illegal Command Encoding: Undefined CA Patterns

Not all 1024 possible CA[9:0] values are assigned in the HBM command truth table. Undefined encodings are designated **reserved commands (RFU)**. Per JESD235C Section 5.4, a DRAM receiving a reserved command encoding must treat it as a NOP — it must neither corrupt internal state nor trigger an error flag. This is a **compliance requirement**, not a vendor suggestion.
ATE illegal-command-encoding tests inject each reserved CA pattern into a single pseudo-channel while the device is in a known idle state (all banks precharged, CKE HIGH). The expected response is: DQ bus remains high-Z (no spurious data output), no self-refresh entry, no mode register corruption. Verify by issuing a valid MRR immediately after the illegal encoding and confirming MR values are unchanged.
- Reserved CA patterns to test: all combinations not listed in JESD235C Table 5-1- Inject during bank-active state too — illegal encodings must still be absorbed as NOP when a row is open- Watch for **DQS glitch** on illegal command injection — a hardware bug can cause spurious DQS toggle- Use ATE per-cycle CA force capability (e.g., V93000 HBM CATC option) for single-cycle injection

## Illegal Sequence Testing: Timing Violations and State Machine Abuse

Illegal sequence testing exercises the DRAM controller's input filter and state machine resilience. Three primary test categories cover the specification space:
**1. Timing violation sequences**: Issue valid commands with inter-command gaps below the JEDEC minimums. Example: ACT to READ with tRCD-1 (one nCK short). Per JESD235C, the DRAM is not required to report an error, but must not return corrupted data on the subsequent burst. ATE captures the read data and compares to the known-good write pattern — any mismatch is a failure.
**2. State machine violations**: Issue READ or WRITE while all banks are in Precharge state (no row open). The DRAM must absorb the command without corrupting the precharge state, verified by a subsequent ACT→READ→PRECHARGE sequence returning clean data.
**3. CKE violation sequences**: Toggle CKE LOW during an active command sequence. JESD235C Section 4.9 defines the required CKE hold times (tCKEL, tCKEH). Violating CKE timing during a READ burst tests the robustness of the power-management state machine.
- All illegal sequence tests must use per-cycle ATE CA forcing — not pattern memory playback- Log ATE functional failures per pseudo-channel to isolate state machine bugs to specific banks

## ATE Implementation: Command Truth Table Coverage on V93000 and UltraFLEX

Implementing a complete command truth table test on **Advantest V93000** requires the HBM CATC (Command/Address Test Controller) option, which provides single-cycle CA bus forcing independent of the pattern sequencer. The test flow: (1) load the CA forcing table with all valid command encodings and their expected DQ response windows, (2) add reserved-encoding injection vectors with null DQ expects, (3) run the sequence across all 16 pseudo-channels in round-robin, capturing per-cycle CA and DQ data.
On **Teradyne UltraFLEX**, the HBM test module's **CA Forcing Mode** in the digital subsystem achieves the same capability. Key ATE setup requirement: **disable the command bus correctness checker** during illegal command injection — the ATE hardware's own command bus monitor will flag illegal encodings as test errors before they reach the DRAM if the checker is active. Re-enable after each injection vector completes.
- Verify command bus setup/hold margins during illegal injection — CA metastability at the DRAM must be ruled out as a failure cause- Capture ATE event logs: correlate DRAM response to the exact CA cycle that carried the illegal encoding- Include both **single-shot** (one illegal command) and **burst** (consecutive illegal commands) test vectors- Temperature sweep at illegal-command tests: hot silicon (105°C) has slower internal state machine recovery — margin differences surface at elevated temperature

## Key Takeaways

- The HBM command truth table (JESD235C Table 5-1) defines every valid CA[9:0] encoding — all other patterns are RFU and must be absorbed as NOP without corrupting DRAM state
- Illegal command types are distinct: undefined CA encodings vs. valid commands issued in violation of timing (tRCD, tRP, tRC) or bank-state (READ with no open row)
- DRAM must return clean data after absorbing illegal sequences — ATE must verify post-illegal-command data integrity, not just absence of visible error flags
- ATE CA forcing mode must disable the on-tester command correctness checker during illegal encoding injection, or the tester itself will block the vectors from reaching the DUT
- Illegal command testing at elevated temperature (105°C) is mandatory — state machine recovery margin degrades at hot silicon conditions and is the most common first-silicon failure mode

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM - JESD235C — JESD235C Section 5 (Command Truth Table, Table 5-1), Section 11 (Command Sequencing Rules, Table 11-1), Section 4.9 (CKE Timing)
2. **[JEDEC]** JEDEC JESD235B HBM2 Command Encoding Specification — Table 5-1 and Table 5-2 — two-cycle command encoding (CMD0/CMD1), bank address mapping, and reserved encoding definitions
3. **[Datasheet]** SK Hynix HBM3 Product Datasheet — Section 6 (Command Truth Table); timing parameter definitions for tRCD, tRP, tRAS, tRC, tWTR, tRTP (Rev 1.1)
4. **[Web]** Advantest V93000 HBM Application Note AN-V93K-HBM-005 — HBM CATC option: single-cycle CA forcing, illegal command injection, and per-pseudo-channel event logging
5. **[JEDEC]** Jedec JESD79-4C DDR4 SDRAM Command Truth Table — Section 4.5 — DDR4 command encoding heritage and illegal command handling rules; cross-reference for HBM CA bus lineage
6. **[IEEE]** Lee et al., 'High Bandwidth Memory PHY and Controller Design for AI Accelerators,' IEEE JSSC 2023 — Section IV: command bus filtering and illegal command absorption in HBM3 controller RTL; doi:10.1109/JSSC.2023.3240012

## 🔍 Additional Learning: HBM3e LFSR-Based Command Bus Scrambling and Its Impact on Illegal Command Coverage

HBM3e introduces optional command bus scrambling using a per-channel LFSR to reduce EMI from repetitive CA patterns during high-bandwidth streaming. When scrambling is enabled, the physical CA[9:0] values observed on the bus are XOR-masked with the LFSR output, meaning that a logically valid command appears as an apparently-illegal encoding at the physical layer. ATE illegal command test suites must account for this: tests must either disable scrambling via MR configuration before running physical-layer CA injection, or apply the same LFSR sequence to deskramble the injected patterns. Failure to handle scrambling causes false-positive illegal command failures during bring-up of HBM3e devices.
