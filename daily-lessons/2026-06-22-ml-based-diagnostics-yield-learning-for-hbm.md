# ML‑Based Diagnostics & Yield Learning for HBM

*Monday, Jun 22 2026*

*Module 6.7 — Advanced Topics*

## Why Machine Learning in HBM Test?

HBM stacks contain 4–8 dies, thousands of I/O pins, and complex JEDEC‑defined timing (e.g., `tRCD`, `tRP`, `tCL`). Traditional parametric binning struggles to correlate multi‑dimensional failure signatures with root causes. ML models can ingest high‑dimensional test vectors (eye‑diagram metrics, BER, latency counters) and discover non‑obvious patterns, reducing debug cycles by 30‑50%.


## Data Pipeline: From ATE to Model

1. **Acquisition**: Capture per‑bit eye‑diagram histograms, DRAM‑specific registers (e.g., `MR0‑MR6`), and built‑in self‑test counters on a Teradyne TSMC‑800 or Advantest V93000.
- Export as `.csv` or `.hdf5` with timestamps and lot identifiers.

2. **Pre‑processing**: Align data to JEDEC JESD235C timing windows, normalize eye‑height/width, and encode categorical fields (e.g., `DRAM type = HBM2E`) using one‑hot vectors.

3. **Feature Engineering**: Derive composite metrics such as `Eye‑Closure Ratio = (EyeHeight_min / EyeHeight_nominal)` and `Latency‑Spread = max(tRCD) - min(tRCD)` across all channels.

4. **Model Training**: Use Gradient Boosted Trees (XGBoost) for binary fault classification, and Gaussian Process Regression for wafer‑level yield prediction. Split data 80/20 for train/validation, retain a separate “new lot” set for out‑of‑sample testing.


## Fault Diagnosis Workflow

When a test fails, the ML service returns a ranked list of probable defect classes (e.g., <em>via crack</em>, <em>TN‑stack mis‑alignment</em>, <em>signal‑integrity degradation</em>). The probability vector is mapped to JEDEC‑defined `DIAG_CODE` fields for automatic report generation. Engineers can drill down to `EyeHistogram[LaneX][BitY]` to verify the suggested root cause.


## Yield Learning & Process Feedback

Gaussian Process models produce a posterior distribution of yield versus process knobs (e.g., anneal temperature, Cu post‑etch time). By conditioning on observed test outcomes, the model suggests optimal process windows that improve `Yield > 95%` while keeping `tRAS` within JESD235C limits. Integration with the fab’s MES system enables closed‑loop adjustment each lot.


## Deployment Considerations

• **Latency**: In‑line inference must complete < 200 ms per wafer to keep up with 2 s/chip ATE throughput.
- Deploy models as Docker containers on the ATE’s edge server (e.g., NVIDIA Jetson AGX).

• **Model Drift**: Retrain monthly or when a new wafer lot shows >5 % deviation in `BER` distribution.
• **Explainability**: Use SHAP values to present feature impact to test engineers, satisfying internal audit requirements.


## Key Takeaways

- ML can fuse eye‑diagram, register, and counter data to pinpoint HBM defects faster than rule‑based logic.
- A robust data pipeline—from ATE capture to feature engineering—is essential for reproducible models.
- Yield learning models close the loop between test diagnostics and fab process optimization.

## References

1. **[JEDEC]** JEDEC JESD235C – High Bandwidth Memory 2E Electrical Specification — Section 4.3 (Timing Parameters) & 6.2 (Built‑in Self‑Test)
2. **[IEEE]** X. Zhang et al., “Machine Learning for DRAM Test Data Mining,” IEEE Transactions on Computer-Aided Design, 2022 — doi:10.1109/TCAD.2022.3154879
3. **[Web]** Advantest V93000 Test Data Architecture Guide — https://www.advantest.com/solutions/v93000/architecture
4. **[Paper]** S. Lee & J. Kim, “Gaussian Process Yield Modeling for 3D‑Stacked Memories,” IEEE VLSI Test Symposium, 2023 — pp. 112‑119
5. **[Web]** NVIDIA Jetson AGX Developer Kit – Edge AI for Test — https://developer.nvidia.com/embedded/jetson-agx

## 🔍 Additional Learning: Transfer Learning from DDR5 to HBM Diagnostics

Recent work shows that a pre‑trained ResNet‑18 model on DDR5 eye‑diagram images can be fine‑tuned with <10 % of HBM data, cutting labeling effort dramatically while preserving >92 % fault‑classification accuracy.
