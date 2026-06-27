# CXL-Attached HBM Memory Testing

*Saturday, Jun 27 2026*

*Module 7.7 — Advanced Test Methodologies*

## CXL Protocol Stack and HBM Memory Expander Architecture

Compute Express Link (CXL) enables cache-coherent, high-bandwidth memory expansion over PCIe 5.0 physical layer. In HBM memory expander configurations, a CXL Type 3 device (memory expander) houses HBM2E or HBM3 stacks accessible via the `CXL.mem` sub-protocol. The host CPU issues `MemRd` and `MemWr` transactions over the Flex Bus, with the CXL controller translating these to HBM AXI or DRAM-style commands. Key architectural elements include the CXL HDM (Host-managed Device Memory) decoder, which maps device physical address (DPA) to host physical address (HPA) regions, and the mailbox interface (CXL 2.0 spec §8.2.8) used for firmware/configuration commands. HBM stacks behind a CXL controller may be exposed as volatile memory with ECC via `CXL.mem H2D Req` / `D2H Resp` flits at 256-byte granularity.


## LTSSM State Validation and Link Training Compliance

CXL link training follows the PCIe 5.0 LTSSM (Link Training and Status State Machine) with CXL-specific extensions. Test engineers must validate state transitions through: **Detect → Polling → Configuration → Recovery → L0**, as specified in CXL 2.0 §4.2 and PCIe Base Spec 5.0 §4.2.6. Critical compliance checks include:
- TS1/TS2 ordered set exchange with CXL-specific symbol `CXL_TS1` carrying Alt Protocol Negotiation (APN) bits- Equalization (EQ) phase completion within 24 ms timeout (PCIe 5.0 §4.2.6.4.1)- Data Rate identifier validation: Gen5 (32 GT/s) with 128b/130b encoding, achieving `~256 GB/s` aggregate on x16 CXL link- DLLP (Data Link Layer Packet) ACK/NAK timer compliance per §4.4.3 — NAK timeout must be ≤ 100 µs- FTS (Fast Training Sequence) count verification during Recovery.EqualizationATE-based LTSSM validation uses protocol analyzers (e.g., Teledyne LeCroy CXL exerciser) to force link into Recovery and measure re-entry time to L0 active state; specification allows ≤ 1 ms from Recovery.Idle to L0.


## CXL.mem Protocol Compliance Testing

`CXL.mem` operates over the M2S (Master-to-Subordinate) and S2M (Subordinate-to-Master) channels using 68-byte flits. Test categories include:
- **HDM Decoder validation:** Write to HDM Decoder Capability Structure (`DVSEC offset 0x10`) and verify DPA-to-HPA mapping correctness via `MemRd` loopback. Decoder must honor `Interleave Granularity` fields (64B to 16KB, per CXL 2.0 §8.2.4.19)- **Poison handling:** Inject address-specific poison via `M2S BISnp` with `MemInv` opcode and confirm `S2M NDR` response carries `poison` bit asserted- **ECC scrubbing:** Trigger background patrol scrub via mailbox command `Scan Media` (opcode `0x43`) and verify `Media Error Log` entries in `CEL`/`UEL` registers- **Back-pressure (credit starvation):** Withhold M2S Request credits and confirm the device stalls without timeout or link error — credit return must resume within credit return timer (≤ 4096 ns at 32 GT/s)

## Latency Verification Methodology

End-to-end CXL-to-HBM latency is a primary datapath quality metric. For a CXL Type 3 device with HBM3, typical measured latencies are:
- CXL transaction layer overhead: ~80–120 ns (flit packetization + HDM decode)- HBM3 row-hit latency via PHY: ~35–40 ns (tRCD + tCL at 6.4 Gbps/pin)- Total read latency (L0, cache-miss): ~120–180 ns vs. ~75 ns for on-package HBMLatency test methodology uses timestamp injection via CXL FLIT header `TS` fields or external pattern generators. On ATE (e.g., Advantest T2000 with CXL option), configure **Memory Access Latency Test** with 64B sequential and 4KB random stride patterns. Measure `tCXL` — the delta from `MemRd` flit departure at host TX to valid data completion at host RX. Key compliance thresholds per CXL 2.0 Annex D:
- Single-device latency SLO: ≤ 200 ns for direct-attached Type 3 device- P99 latency under load (80% BW utilization): ≤ 500 ns

## Failure Modes and Debug Techniques

Common CXL-HBM test failures and root causes:
- **LTSSM hang at Polling.Compliance:** Usually caused by HBM PHY power-up sequencing missing `VDDH` before `VDDC`; verify power rail sequencer timing vs. HBM3 JEDEC spec §3.2 Table 2- **CRC errors on S2M flits:** Indicate HBM controller retimer misconfiguration; check CTLE and TX FIR tap coefficients — Gen5 at 32 GT/s requires 3-tap FFE with c(-1)=0.1, c(0)=0.8, c(1)=0.1 as starting point- **HDM decoder range violation (completion timeout):** Host receives `CA` (Completion Abort) status — check `DVSEC Capability Register` `HDM_D Valid` bit and base/size alignment (must be 256 MB-aligned for interleaved configs)- **Excessive ECC CE rate:** CE rate &gt; 1e-9 per bit per hour triggers `DRAM Event Record` log via CXL FLIT event message; cross-correlate with HBM die temperature (DRAM thermal sensor via mailbox opcode `0x57`) as HBM3 DRAM CE rate doubles per 10°C above 85°C junctionProtocol trace analysis with tools like Keysight's CXL Analyzer GUI correlates LTSSM state, flit-level decode, and HBM DRAM timing simultaneously, reducing MTTD from days to hours.


## Key Takeaways

- CXL Type 3 HBM memory expanders use CXL.mem with 68-byte flits; HDM decoder correctness (DPA→HPA mapping and 256 MB alignment) is the first compliance gate
- LTSSM validation must confirm state transitions through Recovery.Equalization with TS1/TS2 APN bits and equalization completion within 24 ms; link re-entry to L0 must be ≤ 1 ms
- CXL-attached HBM3 adds ~80–120 ns protocol overhead vs. on-package HBM; P99 latency under 80% load must be ≤ 500 ns per CXL 2.0 Annex D compliance targets

## References

1. **[Web]** CXL Specification Revision 2.0 — CXL Consortium, 2020 — §4.2 LTSSM, §8.2.4.19 HDM Decoder, §8.2.8 Mailbox Interface, Annex D Latency Targets. cxlmemory.org
2. **[Web]** CXL Specification Revision 3.0 — CXL Consortium, 2022 — §9.13 CXL.mem Flit Format, §7.3 Credit Management. cxlmemory.org
3. **[JEDEC]** JEDEC JESD235C — High Bandwidth Memory (HBM) DRAM — JESD235C (2021) — §3.2 Power-Up Sequencing, §6 ECC Requirements. jedec.org
4. **[Web]** PCI Express Base Specification 5.0 — PCI-SIG, 2019 — §4.2.6 LTSSM State Machine, §4.4.3 DLLP ACK/NAK Timers, §8.3.3 Gen5 Equalization. pcisig.com
5. **[JEDEC]** HBM3 JESD238A — High Bandwidth Memory 3 — JESD238A (2022) — §3.4 Thermal Characteristics, Table 2 CE Rate vs. Temperature. jedec.org
6. **[Paper]** Memory-Semantic SSD and CXL Memory Expander Latency Analysis — Gouk et al., USENIX ATC 2023 — Measured latency comparison of CXL Type 3 devices vs. on-package DRAM; discusses HDM decoder overhead contribution.

## 🔍 Additional Learning: CXL 3.0 Peer-to-Peer HBM Sharing and Fabric Testing

CXL 3.0 introduces multi-level switching (CXL fabric) enabling multiple hosts to share a single HBM memory expander via Shared Memory (SM) regions. Testing this configuration requires verifying the Global Fabric Attach (GFA) protocol: each host must independently pass LTSSM negotiation to the CXL switch, and the switch must correctly arbitrate MemRd/MemWr ownership via the Bias State machine (Host Bias → Device Bias transitions, §9.14.1). A common failure mode is bias state desynchronization when two hosts simultaneously issue MemWr to the same HBM physical page — verify with concurrent traffic generators and confirm no data corruption via read-back CRC over at least 1M 256B cache lines per host.
