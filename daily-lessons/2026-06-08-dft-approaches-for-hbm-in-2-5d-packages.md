# DFT Approaches for HBM in 2.5D Packages

*Monday, Jun 08 2026*

*Module 4.3 — DFT & Built-In Test*

## Why DFT Is Uniquely Challenging in 2.5D HBM Assemblies

In a 2.5D package the HBM stack and the host die (GPU/AI ASIC) are both mounted on a passive silicon interposer and connected via thousands of micro-bumps. Once bonded, the memory TSV interconnects are physically inaccessible to conventional probing. Standard wafer-level DFT vectors cannot be re-applied post-assembly, so all post-bond testing must be driven through the host die's PHY or through a dedicated JTAG/TAP infrastructure embedded in the interposer or in the HBM itself.
Three failure modes dominate: **open micro-bumps** (high impedance on an otherwise functional net), **bridging faults** between adjacent signal balls in the dense BGA field, and **delay defects** arising from impedance discontinuities on the interposer redistribution layers (RDL). Each fault class demands a different DFT strategy.


## IEEE 1149.1 JTAG and Boundary-Scan in HBM Stacks

JEDEC JESD235C defines a JTAG Test Access Port (TAP) for the HBM controller die. The TAP exposes standard instructions: `BYPASS`, `IDCODE`, `EXTEST`, and `INTEST`. `EXTEST` is the workhorse for post-bond interconnect testing: it forces the HBM I/O cells to drive known patterns onto the micro-bump field while the host die samples them, or vice-versa.
A typical 2.5D assembly chains the HBM TAP through the host die's own IEEE 1149.1 TAP via the **HBM_JTAG_TDI/TDO** pins (defined in JESD235C Table 4). The ATE must present a single JTAG chain addressing both devices; chain length varies from ~400 to ~900 boundary-scan cells per HBM stack depending on the die generation. Scan chain configuration registers are accessible via the **HBM Mode Register MR4** to enable PHY loopback vs. JTAG-driven access.


## BIST Architectures: MBIST and LBIST Inside HBM

Each pseudo-channel inside an HBM die includes a **Memory Built-In Self-Test (MBIST)** engine that can execute March algorithms (e.g., March C−, MATS++) autonomously once triggered over the JTAG TAP. The MBIST result — pass/fail per pseudo-channel plus a failing address — is shifted out through the TAP data register. This eliminates the need to deliver high-speed memory test vectors through the interposer; the ATE simply launches BIST via slow JTAG and reads results.
The HBM PHY also contains **Logic BIST (LBIST)** for the DFI logic, PLL, and DLL calibration circuits. LBIST is invoked during power-on self-test (POST) and can be re-run on-demand from the TAP. Critically, LBIST in HBM3 uses a **Pseudo-Random Pattern Generator (PRPG)** seeded by a 32-bit value writable via MR29/MR30; the seed must match the expected signature stored in the test program to validate correct operation.
For **TSV interconnect integrity**, some vendors implement a dedicated **TSV BIST** that drives a toggling pattern on each TSV group and measures sense amplifier margins, generating a per-TSV pass/fail bitmap readable from a dedicated status register.


## Interposer-Level DFT: IEEE 1149.4 and Structural Test

Silicon interposers can embed **IEEE 1149.4 analog boundary-scan** cells on critical analog/mixed-signal nets to verify RDL continuity and controlled-impedance transmission-line quality. This is less common in high-volume production but appears in engineering validation. More practically, interposer vendors provide **known-good-interposer (KGI)** test vectors that exercise each RDL trace via boundary-scan before die bonding.
Post-bond **structural continuity tests** are run by the host die driving its HBM PHY transmitters in a deterministic low-speed mode (typically 400 Mb/s per pin, far below the operational 6.4 Gb/s of HBM3) so that the ATE on the host package pins can unambiguously sample each channel for stuck-at faults. The HBM PHY exposes a **Direct I/O (DIO) mode** (controlled via `PHYINIT_DIO_EN` in the host PHY register map) to bypass the high-speed serializer and force DC-like logic states for this test.


## Test Coverage Metrics and ATPG Flow for 2.5D HBM

Industry practice targets **≥99% stuck-at fault coverage** for the HBM data path and **≥95% transition fault coverage** (to catch delay defects from bump/RDL resistance variations). ATPG tools such as Siemens Tessent and Synopsys TestMAX support HBM TAP models as first-class cells; the designer imports the HBM BSDL (Boundary-Scan Description Language) file provided by the HBM vendor and merges it with the host die's BSDL to generate unified EXTEST vectors.
A mature 2.5D test flow separates test stages: **KGD** (known-good die) test at wafer level → **KGI** test → post-bond **JTAG interconnect test** at package level → **functional system test**. Each stage has a defined escape metric (DPPM target). Post-bond JTAG interconnect test typically adds 15–60 seconds per HBM stack to the overall system test time, depending on chain depth and vector count.


## Key Takeaways

- HBM's JTAG TAP (JESD235C) enables EXTEST-based post-bond interconnect testing without requiring high-speed ATE on every pin.
- Pseudo-channel MBIST engines execute March algorithms autonomously; test programs retrieve pass/fail bitmaps rather than applying memory patterns from the ATE.
- DIO mode in the host PHY allows low-speed structural continuity testing of HBM interconnects, decoupling fault isolation from the 6.4 Gb/s operational speed.
- Unified BSDL-based ATPG merging host die and HBM TAPs is the industry standard for achieving ≥99% stuck-at coverage in 2.5D assemblies.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C, Sections 4.3 (TAP controller), 4.4 (BIST), and 12 (Mode Registers MR4, MR29, MR30)
2. **[IEEE]** IEEE Standard for Test Access Port and Boundary-Scan Architecture — IEEE Std 1149.1-2013, Clauses 5 (TAP), 10 (EXTEST instruction)
3. **[IEEE]** IEEE Standard for Mixed-Signal Test Bus — IEEE Std 1149.4-2010, targeted at interposer analog net testing
4. **[Book]** DFT for 2.5D and 3D Integrated Circuits — Zorian, Y. & Marinissen, E. J., 'Testing 3D Stacked ICs Containing TSVs,' IEEE Transactions on Computer-Aided Design, 2011
5. **[Datasheet]** Tessent IJTAG and Embedded Analytics for HBM — Siemens EDA Tessent product brief, 2023 — covers HBM TAP integration and BSDL import flow
6. **[Paper]** Post-Bond Interconnect Testing of 2.5D Packages with JTAG — Marinissen et al., 'Test Challenges for 2.5D- and 3D-Stacked ICs,' IEEE Design & Test, vol. 33, no. 3, 2016

## Additional Learning: Scan Chain Compression in HBM JTAG TAP

Modern HBM3/HBM3e stacks implement JEDEC-optional EDT (Embedded Deterministic Test) compression inside the TAP, allowing a 32× reduction in scan shift cycles by encoding care-bit patterns from the ATE into compressed seeds. This brings post-bond JTAG interconnect test time from ~60 s down to ~2 s per stack. The compression ratio is configurable via MR31 (HBM3 only) and must be negotiated between the host ATE application and the BIST controller before EXTEST is invoked.
