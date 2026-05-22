# HBM Timing Basics: tRCD, tCL, tRP & Bandwidth

*Friday, May 22 2026*

*Module 1.6 — Foundations*

## HBM Timing Architecture Overview

HBM uses a standard DDR-based DRAM core organized into pseudo-channels (PCs), each 64 bits wide. Timing parameters control the sequencing of ACTIVATE, READ/WRITE, and PRECHARGE commands within each bank. JESD235C (HBM2E) and JESD238 (HBM3) define the minimum timing intervals in nanoseconds; the controller converts these to clock cycles based on the operating frequency.
Three parameters dominate access latency: **tRCD** (row-to-column delay), **tCL** (CAS latency / read latency), and **tRP** (row precharge time). Together they set the worst-case open-page read latency: `t_total = tRCD + tCL + tRP` — the cost of opening a new row, reading, and closing it.


## tRCD — Row-to-Column Delay

**tRCD** is the minimum interval between an ACTIVATE command and a subsequent READ or WRITE to the same bank. Physically it is the time for the sense amplifiers to latch and amplify the selected row's bitline voltage to a stable logic level. Issuing a column command before tRCD expires catches the sense amps mid-swing and reads corrupted data.
- HBM2E (JESD235C): tRCD = 14–18 ns depending on speed grade (e.g., 14 ns at 3.2 Gbps)- HBM3 (JESD238A): tRCD typically 15–18 ns; exact value in MRS register set- On ATE (e.g., Advantest T2000 / Teradyne UltraFLEX): tRCD is swept during timing characterisation by shrinking the ACT→CAS delay until first-fail; guard-band is typically 0.5–1 ns from hard-fail boundary- A tRCD failure manifests as data errors only on the first access to a freshly activated row — subsequent accesses to the same open row are unaffected

## tCL — CAS Latency (Read Latency)

**tCL** (called <em>Read Latency, RL</em> in HBM nomenclature) is the number of clock cycles from the rising edge of a READ command to the first DQ data burst appearing on the interface. It is a pipeline latency — the DRAM core is already open; tCL is the column decode, sense-amp output, and IO driver pipeline depth.
- HBM2E at 1 GHz (2 Gbps): RL = 7 ck (7 ns); at 1.6 GHz (3.2 Gbps): RL = 14 ck (8.75 ns)- HBM3 at 3.2 GHz (6.4 Gbps): RL programmed 15–20 ck via MRS7/MRS8 per JESD238 Table 11- Write Latency (WL) = RL − differential; HBM2E WL = RL/2 rounded to even integer- On ATE, CL is validated by confirming DQ data-valid window aligns with expected strobe (RDQS) position; mis-programmed RL causes a fixed offset failure across all DQs`Effective tCL (ns) = CL_cycles / F_ck` — lower frequency = more cycles for same ns budget; testers must recalculate per DUT speed bin.


## tRP — Row Precharge Time

**tRP** is the minimum time the controller must wait after issuing a PRECHARGE command before issuing the next ACTIVATE to the same bank. Precharging returns bitlines to `VDD/2` (equalization) and disables the sense amplifiers. If tRP is violated, the next ACTIVATE finds bitlines not fully settled, causing incomplete sensing — typically manifesting as weak-cell fails on the lowest-voltage cells in the new row.
- HBM2E: tRP = 14–18 ns (same as tRCD; shares the same physical path in many designs)- HBM3: tRP ≈ 15–18 ns per JESD238A- tRC (row cycle time) = tRAS + tRP; represents the minimum time to activate a row, complete a transfer, precharge, and reactivate — critical for refresh scheduling- ATE tip: tRP violations produce fails on the <em>second</em> access to a bank (the access after the close), making them easy to distinguish from tRCD fails

## Bandwidth Calculation: Formula and Real Numbers

Peak memory bandwidth is the fundamental figure-of-merit for HBM stacks in GPU and HPC contexts. The formula is straightforward:
`BW (GB/s) = (Bus_width_bits × Data_rate_Gbps_per_pin) / 8`
- **HBM2 (JESD235B):** 1024-bit bus, 2 Gbps/pin → 256 GB/s per stack- **HBM2E:** 1024-bit bus, 3.2 Gbps/pin → 410 GB/s per stack (e.g., NVIDIA A100: 5 stacks = 2.0 TB/s)- **HBM3 (JESD238):** 1024-bit bus, 6.4 Gbps/pin → 819 GB/s per stack (NVIDIA H100 SXM5: 5 stacks = 3.35 TB/s)- **HBM3E:** 1024-bit bus, 9.6 Gbps/pin → 1.2 TB/s per stack (AMD MI300X: 8 stacks = 5.3 TB/s at launch spec)For test purposes, **effective bandwidth** — measured as sustained DMA throughput on ATE — is always lower than peak due to refresh overhead (~3.9%), command/address latency, and bus utilisation efficiency. A well-characterised HBM2E stack achieves ~92–95% of theoretical peak in a burst-mode test pattern.


## Key Takeaways

- tRCD, tCL, and tRP form the open-page access latency triangle; violating any one causes deterministic data errors traceable to specific command-pair timing.
- HBM Read Latency (tCL) is programmed in MRS registers and must be recalculated in clock cycles for each speed bin — a common ATE setup bug is using cycle counts from a different frequency.
- Peak bandwidth scales linearly with both bus width and data rate; HBM3E's 9.6 Gbps/pin delivers 3× the per-stack bandwidth of HBM2 at the same 1024-bit bus width.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — JESD235C, Sections 3.4 (Timing Parameters) and 6.2 (AC Specifications); defines tRCD, tRP, RL for HBM2E
2. **[JEDEC]** High Bandwidth Memory (HBM3) DRAM — JESD238A — JESD238A, Table 11 (Read/Write Latency Settings) and Table 14 (AC Timing Specifications)
3. **[Datasheet]** NVIDIA H100 Tensor Core GPU Architecture Whitepaper — NVIDIA, 2022; Section 2.3 — HBM3 memory subsystem, 3.35 TB/s aggregate bandwidth derivation
4. **[Datasheet]** AMD Instinct MI300X Accelerator Product Brief — AMD, 2023; 192 GB HBM3, 8-stack configuration, 5.3 TB/s memory bandwidth specification
5. **[Book]** DRAM Circuit Design: Fundamental and High-Speed Topics — Brent Keeth et al., IEEE Press/Wiley, 2008; Chapter 5 covers sense amplifier timing and tRCD/tRP fundamentals
6. **[Paper]** Characterization of HBM2 Memory Using High-Speed ATE — Kim et al., IEEE International Test Conference (ITC) 2018; timing margin analysis for tRCD/RL at 2 Gbps

## Additional Learning: tFAW: The Four-Activation Window Constraint

Beyond tRCD/tRP, HBM imposes <strong>tFAW</strong> (Four Activation Window), a rolling time window within which no more than four ACTIVATE commands may be issued across all banks. This limits instantaneous current draw during multiple row openings and is critical in TSV-based HBM where IR drop across the micro-bump array can affect sense-amp margins. In JESD235C, tFAW = 30–35 ns depending on speed grade; ATE bandwidth stress tests that ignore tFAW can cause transient power-supply-induced soft fails that are difficult to reproduce at the board level.
