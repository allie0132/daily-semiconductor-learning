# Adaptive Test Insertion

*Saturday, Aug 15 2026*

*Module 14.1 — Production Test Automation & Cost Optimization*

## What Adaptive Test Insertion Is

Adaptive Test Insertion (ATI) — also called Adaptive Test or Test Optimization — is a methodology that uses upstream parametric data collected at an earlier test step to predict which tests at a downstream step are redundant for a given die, and conditionally skips them. For HBM, the canonical ATI flow exploits wafer-sort (WS) measurements to reduce final-test (FT) time at the package level. Rather than running the full HBM FT flow for every unit, ATI dynamically selects a test subset based on the individual die's WS signature.

The core insight is that wafer-sort data and final-test data are statistically correlated: a die whose WS AC timing margins are centered and well within spec is very unlikely to fail AC timing at FT. If a logistic regression or decision-tree model trained on historical WS→FT correlation data can predict with 99.9%+ confidence that a specific test will pass, that test can be legally skipped for that die — yielding test-time savings of 15–40% in HBM production flows. SEMI Standard E142 ("Specification for Substrate Mapping") and the Semiconductor Test Consortium (STC) ATI guidelines define the required traceability and documentation framework.

## Statistical Models Used in ATI

ATI models learn the mapping from upstream feature vectors to downstream pass/fail outcomes. For HBM, the feature vector at wafer sort typically includes 30–200 parameters: DC measurements (IDD active/standby at multiple VDD points, VREF calibration offsets, leakage per pseudo-channel), AC measurements (tAA, tRCD, tRP, eye margin at 3.2 Gbps and 6.4 Gbps), and DFT results (MBIST fail bitmap density per bank). Three model classes dominate production use:

- **Logistic Regression**: The simplest and most interpretable. Fits a sigmoid function P(fail at FT) = σ(β₀ + β₁x₁ + … + βₙxₙ). Works well when WS→FT correlation is linear in log-odds. Coefficients are auditable; IATF 16949 automotive customers often require this model class for traceability. Typical AUC: 0.92–0.96 for HBM DC tests.
- **Gradient Boosted Trees (XGBoost/LightGBM)**: Handles non-linear interactions between parameters (e.g., tAA degrades faster when IDD is also elevated, suggesting thermal or process corner coupling). Typical AUC: 0.96–0.99 for HBM AC timing tests. Requires careful cross-validation to avoid overfit; a holdout set of ≥50k die is standard practice.
- **Neural Networks (shallow MLP)**: Used when feature space is very high-dimensional (full MBIST bitmap fingerprints, 10k+ features). Computationally expensive to train but inference runs in <1 ms per die on ATE controllers. Requires the most data — typically >500k historical die records to generalize reliably.

All models must produce a calibrated probability output, not just a binary prediction. The ATI skip decision is made by comparing P(fail) against a **guard-band threshold** — typically 0.001 to 0.01 (0.1% to 1% predicted fail probability) — set to keep the ATI-induced FPY loss below the customer's acceptable limit (often <10 DPPM).

## HBM-Specific ATI Considerations

HBM's multi-die stacked architecture introduces traceability requirements not present in monolithic DRAM. Each DRAM die in an HBM stack is tested individually at wafer sort before stacking, and the ATI model must track per-die-layer WS data through the stacking and package assembly process to the correct FT unit identity. This requires die-level traceability (SEMI E142 substrate maps) and lot-genealogy linking in the data management system.

Key HBM-specific ATI opportunities and constraints:

- **TSV continuity tests at FT**: TSV opens and shorts detected at WS (via JEDEC JESD235C-mandated TSV access mode) have extremely high correlation to FT TSV failures. ATI can skip redundant TSV continuity at FT for die with clean WS TSV maps — typical time savings: 8–12 s per unit on a 4096-TSV HBM3E stack.
- **MBIST at FT**: Full-array MBIST (March C− or MATS+ algorithms across 8 pseudo-channels × 16 banks × 8 Gb) consumes 30–90 s at FT. ATI can scope the FT MBIST to targeted regions based on WS fail bitmap — or skip entirely for die with zero WS MBIST fails and centered IDD/Vref parameters.
- **AC timing margin tests**: tAA, tRCD, tRP measured with setup/hold sweeps at FT are highly correlated to WS AC margin data. ATI typically reduces AC test coverage from ±25% margin sweep to a spot check at nominal VDD for die with WS margin >15%.
- **Post-stack parametrics**: Some FT tests (e.g., microbump resistance, per-channel IDD after stacking) cannot be predicted from individual die WS data because they reflect the stacking process, not the die itself. These are ATI-ineligible and always run at FT.

## ATE Integration Architecture

ATI is implemented as a real-time decision engine running on the ATE controller (e.g., Teradyne UltraFLEX `IG-XL` test executive or Advantest T2000 ATML framework). The integration requires three components:

- **Data pull at test start**: At the beginning of each FT unit's test sequence, the ATE controller queries the factory data management system (FDMS) via a RESTful API or ODBC connection, pulling the WS feature vector for that die's lot/wafer/site ID. Latency must be <500 ms to avoid introducing overhead that negates ATI savings. On-site SQLite or Redis caches pre-loaded from FDMS batch exports are common for high-throughput sites (>2000 units/hour per handler).
- **Model inference**: The pre-trained model (serialized as ONNX or a pickled scikit-learn pipeline) runs on the ATE controller CPU. Inference takes 0.5–5 ms per die. The output is a per-test-group skip/run decision vector — for example: `{DC_leakage: RUN, AC_timing: SKIP, MBIST_full: SKIP, TSV_continuity: RUN}`.
- **Skip execution**: The test executive branches past skipped test groups using conditional flow in the test plan (IG-XL `goto` or T2000 `test_suites_disabled` API). Skipped tests are logged with result code `BYPASSED_ATI` rather than PASS, ensuring traceability. The ATI decision, model version, and input feature values are all written to the STDF SDR/DTR records for each unit.

Model refresh cadence matters: HBM process drifts (litho overlay, etch rate variation, CMP uniformity) shift the WS→FT correlation. Models trained on data more than 90 days old or more than 500k production die without re-training can develop prediction drift. Production ATI systems monitor **model accuracy KPIs** — specifically false-negative rate (ATI-passed units that fail at system-level test) — with an automatic fallback to full-test if the rolling false-negative rate exceeds a configurable threshold (typically 50 DPPM).

## Guard-Banding and Risk Management

The central risk in ATI is escaping a truly failing die by predicting it will pass. The guard-band threshold sets the P(fail) cutoff below which tests are skipped; tightening the threshold reduces escapes but also reduces ATI coverage (fewer tests skipped). The optimal threshold balances:

- **Customer DPPM requirements**: HBM for AI accelerator SoCs typically requires <10 DPPM field return rate. ATI-induced escapes must remain a small fraction of this budget — typically <3 DPPM allocated to ATI risk.
- **ATI coverage (test-time reduction)**: Coverage is the fraction of total FT test time that can be skipped. At threshold P(fail) < 0.001, typical HBM ATI coverage is 35–50% of FT test time for a mature, stable process with high WS→FT correlation.
- **Process excursion robustness**: A sudden process shift (e.g., a new wafer lot with anomalous oxide thickness) can invalidate the model's predictions for affected lots. ATI systems use **SPC monitors on WS feature distributions** (Hotelling T² control chart on the multivariate WS feature space) to detect excursions and automatically suspend ATI for affected lots until the model is re-validated.

A standard industry practice is to reserve 2–5% of units as a **golden sample set** that always runs full FT regardless of ATI decisions. The golden sample's pass rates serve as a real-time ground truth for ATI accuracy monitoring. Intel's 2019 VLSI paper (Liu et al.) reported a 38% FT test-time reduction on a DRAM product with <5 DPPM ATI-induced escape rate using this exact guard-banding approach.

## Key Takeaways

- ATI uses wafer-sort parametric data to predict and skip redundant final-test items per die, achieving 15–40% FT test-time reduction in HBM production with <10 DPPM escape risk when properly guard-banded
- For HBM stacks, ATI is most effective on TSV continuity and full-array MBIST; post-stack microbump and channel-level tests are ATI-ineligible because they reflect assembly, not individual die state
- Production ATI systems require real-time FDMS data pull (<500 ms latency), ONNX model inference on ATE controller, STDF BYPASSED_ATI logging for traceability, and SPC-triggered automatic full-test fallback on process excursions

## References

1. **[JEDEC]** High Bandwidth Memory (HBM3) Standard — JESD235C, 2022 — Section 5.3 Test Access Mode, TSV Continuity Test Requirements
2. **[SEMI]** Specification for Substrate Mapping — SEMI E142, 2016 — Die-level traceability format for ATI and wafer-sort-to-final-test correlation
3. **[IEEE]** Adaptive Test: The Next Generation of Intelligent Test — Burns, M. & Roberts, G., IEEE Design & Test of Computers, vol. 31, no. 4, pp. 46–55, 2014
4. **[Paper]** Machine Learning for Adaptive Test Insertion in DRAM Manufacturing — Liu, Y. et al., IEEE VLSI Test Symposium (VTS), 2019 — 38% test-time reduction with <5 DPPM escape
5. **[Book]** Essentials of Electronic Testing for Digital, Memory and Mixed-Signal VLSI Circuits — Bushnell, M.L. & Agrawal, V.D., Springer, 2000 — Chapter 18: Test Economics and Optimization
6. **[Web]** Semiconductor Test Consortium ATI Guidelines — STC Technical Report TR-2021-01: Adaptive Test Insertion Methodology and Guard-Banding Framework

## 🔍 Additional Learning: Virtual Metrology — Extending ATI to Predict Wafer-Sort from In-Line Process Data

Virtual metrology extends the ATI concept one step further upstream: rather than using wafer-sort data to skip final-test items, it uses in-line process tool data (etch rate, deposition thickness, overlay error) collected during fabrication to predict wafer-sort outcomes before any electrical test is performed. For HBM, virtual metrology models trained on CVD, CMP, and lithography tool logs have been shown to predict MBIST row-repair counts with R²>0.85, enabling proactive yield disposition and capacity planning before the wafers even reach sort. SK Hynix and Samsung have published results (IITC 2022, IEDM 2023) demonstrating virtual metrology integration into HBM manufacturing for TSV fill ratio prediction, which correlates directly to TSV resistance outliers at sort.
