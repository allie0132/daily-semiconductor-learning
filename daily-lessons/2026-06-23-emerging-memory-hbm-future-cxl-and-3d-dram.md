# Emerging Memory & HBM Future: CXL and 3D DRAM

*Tuesday, Jun 23 2026*

*Module 6.8 — Advanced Topics*

## CXL Memory: Protocol Overview and Memory Semantics

**Compute Express Link (CXL)** is a cache-coherent interconnect built on PCIe physical layer. CXL.mem (Type 3 devices) exposes a host-managed device memory (HDM) range directly into the host's physical address space. Unlike HBM—which is tightly coupled on-package—CXL memory is disaggregated: it can reside on an add-in card or a rack-scale fabric. For test engineers, the critical difference is that CXL memory latency (~150–300 ns unloaded vs. ~10 ns for HBM on-package) creates a new class of latency-sensitivity verification. JEDEC CXL 3.1 adds 256-link fabric support, enabling memory pooling across multiple hosts. The DCMHS (Datacenter Modular Hardware Specification) physical form factor defines CXL memory modules (CMMs), replacing DDR5 DIMMs in some server designs by 2026.


## 3D DRAM Stacking: CMOS-Under-Array and Die-to-Die Bonding

The HBM roadmap beyond HBM4 converges with monolithic 3D DRAM research. Two distinct approaches are emerging:
- **CMOS-Under-Array (CUA):** Samsung's approach places peripheral CMOS logic under the DRAM cell array, reclaiming array area and enabling higher density without a larger footprint. SK Hynix uses a variant called CMOS-bonded-to-array (CBA).- **Backside power + hybrid bonding:** TSMC's 3Dblox and Intel's EMIB use direct Cu-Cu hybrid bonding at sub-10 µm pitch. For HBM4 and beyond, die-to-wafer hybrid bonding targets &lt;1 µm pitch versus HBM3E's ~55 µm microbump pitch.From a test standpoint, **buried interconnects** in CUA structures are inaccessible to standard probe; boundary scan and BIST become the only viable structural test paths.


## HBM4 and HBM4E: Specification Trajectory

JEDEC **JESD238** defines HBM4, expected to be finalized in 2025-2026. Key projected parameters:
- **I/O width:** 2048-bit per stack (up from 1024-bit in HBM3E)- **Data rate:** ≥6.4 Gbps/pin, targeting 8 Gbps in HBM4E- **Bandwidth per stack:** ~1.6 TB/s at 6.4 Gbps with 2048-bit interface- **Die count:** Up to 16-Hi stacks under discussion (HBM3E is 12-Hi in production)- **Power:** 15–20W per stack; thermal impedance Rth becomes a first-class specificationThe 2048-bit interface demands that **ATE channel count** scale proportionally. A dual-stack HBM4 device requires 4096+ DQ pins; current high-pin-count testers are being redesigned to support this density at wafer sort.


## CXL + HBM Convergence: Pooled HBM Architecture

A forward-looking architecture combines HBM stacks connected via CXL fabric, enabling **memory pooling** without tight host coupling. A CXL switch aggregates multiple HBM-bearing tiles; any attached host CPU can map any tile into its address space.
Test implications are significant:
- CXL.mem HDM range test requires exercising CXL FLIT (68-byte) integrity, not just raw DRAM patterns- ECC operates at two levels: HBM internal SECDED per 128-bit burst and CXL link-level retry (LLR) buffers- Latency distributions must be verified under loaded fabric conditions; a single-device spec is insufficient

## ATE Implications and Test Strategy for Next-Generation Memory

Higher bandwidth, larger die stacks, and new interconnect protocols force re-evaluation of test insertion points:
- **Known-Good Die (KGD):** With 16-Hi stacks, stacking a defective die compounds cost exponentially; full electrical KGD at wafer sort is mandatory. This requires probe card access at HBM4's full 2048-bit width.- **Post-bond test via JTAG/BIST:** IEEE 1149.1 boundary scan and IEEE 1500 wrappers are extended by JEDEC-defined MBIST for stacked die. HBM PHY BIST (JESD235C Section 8) allows partial stack test after bonding.- **CXL protocol-layer test:** ATE vendors are adding CXL endpoint emulation to generate valid FLITs and verify latency, error injection, and hot-plug sequencing.- **Thermal stress during test:** At 15–20W per HBM4 stack, delta-T across a 300 mm wafer with multiple stacks active can reach 15–20°C without active temperature forcing.

## Key Takeaways

- CXL.mem disaggregates memory from compute, introducing latency-domain testing that HBM ATE flows were not originally designed for
- HBM4's 2048-bit interface and potential 16-Hi stacks require proportional ATE channel scaling and full KGD test at wafer sort
- CMOS-Under-Array and hybrid bonding eliminate optical probe accessibility; BIST and boundary scan become the primary structural test paths beyond HBM4

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM — JESD235C — HBM3/3E architecture and PHY BIST (Section 8); JESD238 (HBM4 draft, 2025)
2. **[Web]** Compute Express Link (CXL) Specification — CXL Consortium, CXL 3.1 Specification (2024) — CXL.mem HDM ranges, fabric port counts, memory pooling semantics
3. **[IEEE]** CMOS-Under-Array DRAM: Density and Test Implications — Kang et al., 'A 10nm-class DRAM with CMOS-Under-Array Architecture,' ISSCC 2022, pp. 220-222
4. **[IEEE]** IEEE Standard for Boundary-Scan Architecture — IEEE Std 1149.1-2013 — JTAG boundary scan; IEEE P1838 extends this for 3D stacked die test access
5. **[Paper]** 3D Stacked Memory Test Access Architecture — Marinissen et al., 'A Test Access Architecture for 3D Stacked ICs,' DATE 2010 — foundational reference for IEEE P1838
6. **[Paper]** Ultra-High-Density Probe Card for HBM Wafer Sort — Hayashi et al., ITC 2023 — thermal and tip-count constraints for 2048-bit wide HBM interfaces at wafer sort

## Additional Learning: CXL Memory Tiering and NUMA Distance Validation

Operating systems expose CXL memory as a high-latency NUMA node (typically node 1+) via ACPI SRAT/SLIT tables. Test plans for CXL memory modules must verify that SLIT latency values match measured round-trip latency. Critically, BIOS/firmware must correctly populate the CFMWS (CXL Fixed Memory Window Structure) in the ACPI CEDT table; a misconfigured CFMWS causes the OS to either miss the CMM or place it in the wrong NUMA domain, silently degrading performance — a firmware-level validation gap that test engineers increasingly need to own.
