# HBM ECC Deep Dive: SEC-DED, Chipkill & Scrubbing

*Tuesday, Sep 08 2026*

*Module 17.4 — HBM Ecosystem & Cross-Domain Test Engineering*

## ECC Fundamentals in HBM Memory Systems

HBM implements Error Correcting Code (ECC) at the memory die level, using a **128-bit data word + 8-bit ECC syndrome** per access (JESD235C §3.14). This 136-bit internal bus provides the check bits required for SEC-DED without exposing additional pins on the PHY interface — the ECC computation occurs entirely within the HBM stack.
The primary motivation is DRAM cell instability at sub-20nm nodes: cosmic-ray soft errors, retention failures from charge leakage, and write-disturbance all produce single-bit upsets (SBUs). The raw DRAM uncorrectable bit error rate (UBER) before ECC at HBM2E densities (8-16 Gb per die) is on the order of 10<sup>-12</sup> per bit-hour; post-ECC SEC-DED reduces uncorrectable errors to those caused by multi-bit upsets (MBUs).
JESD235C mandates that the host SoC ECC subsystem be capable of detecting and reporting correctable errors (CE) and uncorrectable errors (UE) via the HBM pseudo-channel architecture, with error logging into the SoC MR register space accessible over JTAG or in-system debug interfaces.


## SEC-DED Hamming Code Architecture

SEC-DED (Single Error Correct, Double Error Detect) is built on extended Hamming codes. For a 128-bit data word, **8 check bits** are required: 7 bits satisfy Hamming's 2<sup>r</sup> ≥ n+r+1 condition (2<sup>7</sup>=128 ≥ 128+7+1=136 — barely met), plus 1 overall parity bit for the double-error detection extension.
The encoder XORs data bit subsets according to a parity-check matrix H. At read, the decoder recomputes the syndrome vector S = H·r (mod 2) over the received 136-bit word r. A zero syndrome indicates no error. A non-zero syndrome with overall parity = 1 means a correctable single-bit error; the syndrome directly indexes the error location. A non-zero syndrome with overall parity = 0 indicates a double-bit error — detected but uncorrectable.
HBM implementations typically use the **Hsiao SEC-DED code** (IBM 1970) rather than classical Hamming, because Hsiao's construction yields an H-matrix with all column weights odd and as equal as possible, minimising the maximum gate depth in XOR trees and improving timing closure at 2+ GHz PHY frequencies. Each pseudo-channel (PC) in HBM2/HBM2E/HBM3 operates a 64-bit data bus + 8-bit ECC per PC, so two PCs combine to form the logical 128+8 ECC word.
Key registers: `ECC_STATUS` (correctable count), `ECC_ERR_ADDR` (failing DRAM row/column), `ECC_SYNDROME` (8-bit value pinpointing the bit), accessible via vendor-specific SoC APB/AXI4 memory controller CSR maps.


## Chipkill: Die-Level Fault Tolerance

Standard SEC-DED protects only against SBUs. A full DRAM die failure — due to a defective TSV column, a die-to-die micro-bump open, or a power-delivery fault on one stack die — produces a **burst of correlated bit errors** spanning an entire access channel, which SEC-DED cannot correct.
**Chipkill** (IBM terminology) extends protection to full device failures by distributing the ECC codeword across <em>multiple physical dies</em>, such that losing one die contributes at most one symbol's worth of errors to any codeword. HBM Chipkill implementations typically use **Reed-Solomon (RS) codes** over GF(2<sup>8</sup>) or GF(2<sup>4</sup>) symbol fields, or symbol-correcting SEC-DED variants (also called SECDED with symbol interleaving).
In a practical HBM3 8-Hi stack, the 8 dies can be grouped such that each 72-bit ECC codeword (64 data + 8 check) draws **one nibble from each die**. Complete loss of one die corrupts exactly one 8-bit symbol per codeword; RS(9,8) over GF(2<sup>8</sup>) can correct any one-symbol error, giving true Chipkill capability.
The trade-off is ECC overhead and latency: RS decoding requires iterative Berlekamp-Massey or Euclidean algorithm hardware, adding 1-2 ns decode latency vs. SEC-DED's single-cycle XOR. High-Bandwidth applications (AI training, HPC) must budget this into their tRCD/tCL timing margins.


## Memory Scrubbing Algorithms and Timing

ECC corrects errors at read time, but a corrected (masked) SBU that is never rewritten remains latent. If a second SBU accumulates on the same word before the next natural read, the word now contains a double-bit error — uncorrectable. **Memory scrubbing** proactively reads and rewrites every memory location at a defined interval to eliminate latent corrected errors before a second fault can co-locate.
Scrubbing algorithms fall into two categories:
- **Background patrol scrub:** A low-priority DMA engine walks through all memory at a controlled rate, typically completing a full sweep in **24–72 hours** (system BIOS/firmware configurable via SPD/MR registers). At HBM3 bandwidth of ~1 TB/s, a 16 GB HBM stack can theoretically be scrubbed in 16 ms, but scrub engines are throttled to <1% bandwidth to avoid impacting application QoS. The scrub interval must be set shorter than the expected double-fault accumulation time, derived from the per-bit soft error rate (SER) and memory capacity.- **Demand scrub (on-detect):** When a CE is detected during a normal read, the corrected data is immediately written back to the same row, clearing the latent fault in real time. This is lower overhead but doesn't address unread pages.The scrub rate formula for reliability: given a soft error rate λ (FIT/Mbit) and memory size N bits, the probability of a double fault within scrub interval T is approximately P ≈ (λNT)<sup>2</sup>/2. For HBM3 16 GB and λ=1000 FIT/Mbit, T must be &lt;24h to keep P&lt;10<sup>-9</sup>/hour (typical system RAS target).
JEDEC JESD235C §4.5 specifies that `MR28` bits [5:4] control the per-die refresh rate (which also influences scrub window sizing in vendor implementations).


## ECC Error Injection for Validation

Validating that ECC logic functions correctly end-to-end — from DRAM cell through PHY through controller decode logic to OS error-handling firmware — requires deliberate fault injection. Three complementary approaches are used in HBM validation:
- **BIST register-based injection (in-stack):** Most HBM3 controllers expose a `ECC_ERR_INJECT` CSR (vendor-specific, e.g., at offset 0x300 in the MC APB map) that XORs a programmable mask into the write data path or the syndrome path. Writing `0x01` to bit 0 of this register forces a single-bit flip on the next write transaction, allowing the test to confirm that the CE counter increments and the corrected readback matches the original write data.- **Pattern-based row hammer injection:** Repeatedly accessing rows adjacent to a target row activates DRAM charge-coupling disturbance, producing authentic SBUs in the victim row. This tests the full ECC path under realistic physics rather than a synthetic gate-level flip.- **JTAG/DFT scan-based injection:** At silicon bring-up, scan chains can load arbitrary bit patterns into ECC check-bit registers, enabling die-level ECC path coverage measurement. Coverage targets typically require &gt;95% of ECC syndrome bits exercised.ATE-level HBM ECC validation on a tester (e.g., Advantest T2000, Teradyne UltraFLEX) uses the `WRITE_ECC` and `READ_ECC_STATUS` test steps in the HBM test program. The test writes a known pattern, uses the error-injection CSR to corrupt a single bit, reads back, checks the syndrome register for the expected value, verifies the corrected readback, then increments to a double-bit injection and confirms UE flagging and no silent data corruption.
Validation must cover all **136 possible single-bit positions** (128 data + 8 check bits) plus all 136-choose-2 = 9180 double-bit pairs — typically sampled via pseudorandom coverage rather than exhaustive enumeration, requiring a formal coverage plan reviewed against the Hsiao code's coverage theorem.


## Key Takeaways

- HBM uses 128+8 SEC-DED ECC per 128-bit word (JESD235C), computed inside the stack with no extra PHY pins; Hsiao code minimises XOR tree depth for GHz-range operation.
- Chipkill extends protection to full die failures by distributing ECC codewords across all stack dies using Reed-Solomon symbol codes, at the cost of 1-2 ns additional decode latency.
- Patrol scrubbing must complete a full memory sweep in under 24-72 hours to prevent double-fault accumulation; scrub engines are throttled to <1% of peak HBM bandwidth.
- ECC error injection using controller CSR masks, row-hammer physics, and JTAG scan chains validates the entire CE/UE detection and reporting path end-to-end.
- Proper ATE test coverage requires exercising all 136 single-bit positions and a statistically sampled subset of the 9180 double-bit pairs against the expected syndrome table.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C, §3.14 (ECC architecture), §4.5 (MR28 refresh/scrub controls)
2. **[Paper]** A Class of Optimal Minimum Odd-weight-column SEC-DED Codes — Hsiao, M.Y. — IBM Journal of Research and Development, Vol. 14, No. 4, 1970, pp. 395-401
3. **[Paper]** Chipkill Memory Systems: Tolerating Multiple-Bit Memory Faults — Shieh, M. et al. — HPCA 2012; also IBM Technical Report TR-00.3534 (1997) by T.J. Dell
4. **[Paper]** Memory Soft Error Rates and Scrubbing Policies for HPC Systems — Sridharan, V. & Liberty, D. — SC12 Proceedings, DOI 10.1109/SC.2012.91
5. **[Book]** Nanoscale Memory Repair — Horiguchi, M. & Itoh, K. — Springer, 2011, Ch. 6: ECC and Redundancy Architectures
6. **[Web]** HBM3 System ECC and RAS Architecture — Samsung HBM3 Product Brief, 2022 — memory.samsung.com/hbm3-ecc-ras (vendor application note)

## 🔍 Additional Learning: On-Die ECC (ODECC) vs. Controller ECC in HBM3E

HBM3E introduces On-Die ECC (ODECC), where the ECC engine moves fully inside the DRAM die rather than the host controller, reducing the ECC bits visible on the PHY from 8 to 0 — the full 128-bit bus carries data only. ODECC improves effective bandwidth efficiency but removes the controller's ability to read raw syndromes, complicating post-silicon debug: the host can only observe a CE/UE flag bit rather than the 8-bit syndrome. Engineers working on HBM3E validation must rely on additional in-stack diagnostic modes (enabled via Mode Register MR30 in the JEDEC HBM3E spec) and on SoC-level error counters rather than direct syndrome interrogation, requiring updated test programs and debug workflows compared to HBM2E.
