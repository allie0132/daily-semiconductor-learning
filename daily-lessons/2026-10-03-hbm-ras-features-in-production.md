# HBM RAS Features in Production

*Saturday, Oct 03 2026*

*Module 18.2 — HBM in Production AI Systems & Silicon Lifecycle Management*

## Address Poisoning: Propagating Uncorrectable Errors

Address poisoning is a JEDEC-defined RAS mechanism (JESD235C §3.17) that marks a memory address as **permanently faulty** after a hard, uncorrectable error. Once an address is poisoned, any subsequent read from it returns a **Poison indicator** rather than corrupted data, allowing the memory controller and OS to detect and isolate the fault rather than silently propagating bad data into computations.
In HBM2e/HBM3 stacks the poison bit propagates through the PHY as a sideband flag on the data bus. The host stack must set `MRS[15]` (Mode Register Set, Poison Enable) to activate poisoning. If the register is left unset the DRAM simply delivers corrupted bits — a far worse outcome for AI inference workloads where a single misclassification may never be caught.
- **Soft poison**: set on a correctable (single-bit) error that has been repaired; the address is flagged for monitoring but remains accessible.- **Hard poison**: set on an uncorrectable (multi-bit) error; the address is retired and any future access returns the poison indicator.- GPUs implementing HBM3 (e.g., H100, MI300X) surface address-poisoned pages via `nvidia-smi` / ROCm SMI `ras_enabled` counters, which can trigger page retirement at the driver level.

## Row Hammer Fundamentals in HBM Stacks

Row hammer is the phenomenon where repeated activation of DRAM rows (**aggressor rows**) induces bit-flips in adjacent **victim rows** via capacitive and charge-coupling effects. In HBM3 the tight 3D-stacked geometry and higher row-activation rates in AI workloads make HBM more susceptible to hammer effects than traditional DDR.
The JEDEC standard (JESD235C §3.14, Alert_n pin) mandates that HBM devices signal the host when an internal row-activation counter exceeds a **Refresh Mitigation Threshold (RMT)**. The host is then required to issue a Targeted Refresh command to the victim row within a specified window.
- **Hammer threshold (HC_first)**: varies by process node; for 1Ynm HBM3 dies, typical values are 1000–4000 row activations before a victim-row refresh is mandatory.- **Alert_n latency budget**: the host must service the Alert_n interrupt and issue the targeted refresh within `tRASmax` to guarantee no bit-flip.- AI training kernels with highly sequential access patterns (e.g., transformer attention head sweeps) can inadvertently hammer the same aggressor row billions of times per second.

## TRR and PARA Mitigation Schemes

**Target Row Refresh (TRR)** is an on-die countermeasure introduced in HBM2e and refined in HBM3. Each bank maintains an internal counter per row; when a row's activation count reaches the RMT, the DRAM die autonomously issues a **same-bank refresh** to physically adjacent rows without host intervention. TRR operates transparently but consumes timing budget — each implicit refresh adds latency equivalent to a `tRFC` cycle.
**Probabilistic Adjacent Row Activation (PARA)** is a host-side mitigation. After each row activation the memory controller probabilistically activates adjacent rows with a low probability <em>p</em> (typically 1/256 to 1/512). PARA avoids the need for the DRAM to maintain per-row counters and requires no Alert_n interrupt handling, but introduces small, non-deterministic latency jitter.
- HBM3 JEDEC spec requires TRR compliance; host-side PARA is additive and commonly deployed in GPU memory controllers for defense-in-depth.- `tRFC` for HBM3 16-Hi stack: approximately 350–450 ns, and a TRR-triggered implicit refresh consumes the same window.- In production AI clusters, TRR-induced latency spikes show up as **tail-latency outliers** in memory-bandwidth profiling; the signature is periodic ~400 ns stalls at regular activation intervals.- Both TRR and PARA are rendered ineffective if the host over-drives the row-activation rate beyond what the RMT threshold can keep pace with — validating tCCD_L and tRRD_L compliance is essential during ATE testing.

## Patrol Scrub: Scheduling and Coverage

Patrol scrub is a background ECC correction sweep that proactively reads every memory address at a regular interval, corrects single-bit errors in place, and logs multi-bit errors before they accumulate into uncorrectable events. For HBM stacks in AI inference servers — where DRAM may hold activations in memory for hours — scrub must complete a full coverage pass within the **DRAM retention interval** (typically 64 ms at operating temperature, down to 32 ms above 85°C junction).
Scheduling a patrol scrub involves two competing constraints: **coverage rate** (bytes/s) must exceed total capacity / retention interval, and **bandwidth overhead** must stay below the system budget. For an 80 GB HBM3 device with a 64 ms retention interval, the scrub engine must sustain at least 1.25 TB/s just to keep up — already close to the 3.35 TB/s peak bandwidth of HBM3.
- **Idle-time scrubbing**: throttles scrub bandwidth when memory traffic is high; acceptable for inference clusters with well-characterized idle periods between batches.- **Continuous scrubbing**: maintains a fixed scrub rate regardless of traffic; guarantees coverage but imposes ~3–8% bandwidth tax depending on row size and ECC latency.- JEDEC JESD235C §5.3 defines the `ALERT_n` mode that can also be used to signal a scrub-detected correctable error requiring software-level logging.- In production GPU nodes (H100 SXM5, MI300A), scrub scheduling is exposed via driver APIs and can be tuned: `nvidia-smi --gpu-reset-ecc-errors` resets counters but does not affect scrub scheduling; scrub rate is set at driver initialization from VBIOS tables.

## Integration and Test Considerations

Validating RAS features on ATE (e.g., Advantest T2000, Teradyne Magnum) requires specific test modes. Address poisoning is verified by deliberately injecting an error into a row (using the DRAM's **Write-DQ fault injection** mode), then confirming the Poison indicator appears on subsequent reads. TRR is validated by driving aggressor-row activation bursts above the HC_first threshold and confirming no victim-row bit-flip occurs within spec time.
- **Poison injection test sequence**: Issue MPR (Multi-Purpose Register) access to enable fault injection → write with forced error → read and verify Poison flag on ALERT_n → confirm host poison-handling ISR fires within the alert latency budget.- **Row-hammer stress test**: Run aggressor-row loop at maximum tRC rate for 10× HC_first activations; verify zero victim-row fails across all temperature corners (0°C, 85°C).- **Patrol scrub rate test**: Measure scrub coverage using internal DRAM diagnostic mode; confirm full address space is covered within 1× retention interval at Tjunction = 95°C.- Post-silicon bring-up teams should monitor `ras_events` counters across burn-in (&gt;24 h at Vmax+5%, Tjunction = 105°C) to catch latent defects that only manifest after stress.

## Key Takeaways

- Address poisoning (JESD235C §3.17) prevents silent data corruption by flagging faulty addresses rather than returning bad data; MRS[15] must be set in production.
- TRR (on-die) and PARA (host-side) are complementary row-hammer mitigations; TRR adds ~400 ns tRFC-equivalent latency stalls visible as tail-latency outliers in GPU profiling.
- Patrol scrub must sustain ≥1.25 TB/s coverage for an 80 GB HBM3 device at 64 ms retention, competing directly with application bandwidth — scrub scheduling is a tunable production parameter.

## References

1. **[JEDEC]** JEDEC JESD235C: High Bandwidth Memory (HBM) DRAM — §3.14 (Row Hammer), §3.17 (Address Poison), §5.3 (Alert_n modes) — JEDEC Solid State Technology Association, 2021
2. **[Paper]** Kim et al., Flipping Bits in Memory Without Accessing Them — ISCA 2014 — Yoongu Kim, Ross Daly, Jeremie Kim, et al.; original row-hammer characterization paper
3. **[Datasheet]** NVIDIA H100 GPU Memory Architecture White Paper — NVIDIA, 2022 — §4: HBM3 RAS features including ECC, address retirement, and scrub scheduling in H100 SXM5
4. **[Datasheet]** AMD MI300 Series Accelerator Architecture Guide — AMD, 2023 — §6: HBM3 RAS implementation, patrol scrub API, and poison-enable configuration in ROCm driver
5. **[Paper]** Mutlu & Kim, RowHammer: A Retrospective — IEEE T-CAD, 2019 — Onur Mutlu, Jeremie S. Kim; comprehensive survey of mitigation schemes including TRR and PARA
6. **[Book]** Hennessy & Patterson, Computer Architecture: A Quantitative Approach, 6th ed. — Morgan Kaufmann, 2017 — Appendix B: Memory hierarchy and DRAM reliability/RAS features

## Additional Learning: HBM3E Refresh Management (RFM) Command

HBM3E introduces the Refresh Management (RFM) command as a host-initiated mechanism to supplement on-die TRR. Rather than relying solely on the DRAM's internal row counters, the host memory controller tracks per-bank activation budgets via the Alert_n Management Table and issues RFM commands before reaching the RMT, proactively triggering adjacent-row refreshes. This eliminates the unpredictable latency spike of Alert_n interrupts and allows the host to schedule RFM during known low-traffic windows, providing deterministic row-hammer protection critical for latency-sensitive AI inference SLAs.
