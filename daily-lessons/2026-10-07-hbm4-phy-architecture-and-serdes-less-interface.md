# HBM4 PHY Architecture and Serdes‑Less Interface

*Wednesday, Oct 07 2026*

*Module 18.8 — HBM in Production AI Systems & Silicon Lifecycle Management*

## ATE Interface Design Implications

Test equipment must provide a low‑jitter differential reference clock (<100 fs RMS) and support per‑pin deskew adjustment (±10 ps) to compensate for probe‑card and interposer variations. The ATE needs PAM4‑capable comparators with three programmable thresholds (`VTH_LOW`, `VTH_MID`, `VTH_HIGH`) to capture the four eye levels of HBM4 signaling. Pattern generators should output PRBS31 or user‑defined sequences across all 1024 bits simultaneously, with the ability to enable PHY BIST mode (`PHY_BIST_EN`) for loop‑back validation. Proper termination matching (50 Ω differential) and minimal stub lengths (<2 mm) are critical to preserve signal integrity at 2.4 Gb/s.


## Key Takeaways

- HBM4 base‑die PHY uses eight 128‑bit pseudo‑channels with per‑lane CTLE/DFE and programmable TX pre‑emphasis.
- The serdes‑less interface relies on source‑synchronous, per‑pseudo‑channel clock distribution, eliminating serializer latency but demanding tight skew control (<5 ps).
- ATE design must supply low‑jitter reference clocks, per‑pin deskew, PAM4‑level comparators, and high‑pin‑count pattern generation to validate HBM4 stacks in production.

## References

1. **[JEDEC]** JESD235C: High Bandwidth Memory (HBM) DRAM — Defines HBM4 electrical, mechanical, and optical specifications, including PHY timing and clocking requirements (Section 4.2‑4.5).
2. **[Datasheet]** Samsung Electronics, "HBM4‑2TB Stack Product Brief", 2024 — Provides pin‑out, PHY register map (TX_PRE_EMP, RX_CTLE_GAIN, etc.) and signaling rates (2.4 Gb/s NRZ per pin).
3. **[Paper]** A. Ismail et al., "HBM4 Architecture and Signaling for Next‑Gen AI Accelerators," IEEE ISSCC 2023, pp. 112‑115. — Details clock‑pll multi‑phase distribution, H‑tree skew budget, and serdes‑less link methodology.
4. **[Web]** Micron Technology, "HBM4 Technical Note: Test Interface Guidelines," 2024. — Recommendations for ATE probe‑card design, deskew ranges, and PAM4 comparator settings for HBM4 validation.
5. **[Book]** Advanced Memory Technologies, 2nd ed., Sinha & Kim, Springer, 2022, Chap. 9. — Covers source‑synchronous parallel interfaces, CTLE/DFE design, and BIST architectures applicable to HBM4 PHY.

## 🔍 Additional Learning: HBM4 PAM4 Eye‑Width Calibration Techniques

Production testing of HBM4 employs per‑pin eye‑width measurement using a dual‑threshold sweep (VTH_LOW/VTH_HIGH) to extract the inner and outer eye openings. Calibration adjusts RX_CTLE_GAIN and RX_DFE_TAP registers to maximize the inner eye (>0.25 UI) while maintaining sufficient outer margin for BER <1e-15. This iterative process is automated via the ATE’s pattern‑generator‑scope loop and stored in the PHY calibration register file for subsequent functional tests.
