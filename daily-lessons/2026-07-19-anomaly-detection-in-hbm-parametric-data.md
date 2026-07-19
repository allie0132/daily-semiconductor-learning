# Anomaly Detection in HBM Parametric Data

*Sunday, Jul 19 2026*

*Module 11.2 — Machine Learning for Test Optimization*

## Why Unsupervised Anomaly Detection for HBM

HBM parametric test data spans thousands of per-channel measurements: **Vref trim codes, ZQ calibration residuals, DRAM Vdd/Vss sense readings, temperature-compensated tRCD/tRP margins, and per-PHY eye widths**. Traditional SPC limits (±3σ on univariate distributions) miss correlated failures — a die whose voltage and timing margins are each individually within spec but whose joint distribution places it far from the cluster centroid.
Unsupervised methods operate without labelled defect classes. They model the <em>normal</em> population from production data, then score each die by its distance from that model. This is critical in HBM qualification where known-bad examples are scarce early in ramp and failure modes are not fully enumerated.


## DBSCAN for Wafer-Map Spatial Outliers

**DBSCAN (Density-Based Spatial Clustering of Applications with Noise)** groups die by density in feature space. Points in low-density regions — i.e., not reachable from any core point — are labelled noise (class −1). Two key hyperparameters are `eps` (neighbourhood radius in normalised feature space) and `min_samples` (minimum neighbours to form a core point).
For HBM data, a typical workflow normalises each parametric column to zero mean and unit variance, then applies DBSCAN in the resulting N-dimensional feature space. DBSCAN noise points map back to physical die (x, y) coordinates on the wafer map, revealing spatial patterns — edge die, reticle-corner die, or isolated electrical outliers — that bin-based pass/fail maps often miss until downstream reliability.
- Set `eps` via k-nearest-neighbour distance elbow plot (k = `min_samples`)- Typical `min_samples`: 5–15 for wafer populations of 500–2000 die- Noise die flagged as **soft-bin 90x** for disposition review, not hard-fail**

## Isolation Forest for High-Dimensional Scoring

**Isolation Forest** exploits the observation that anomalies are <em>few and different</em>: they are isolated by fewer random axis-aligned splits than normal points. Each tree partitions the feature space randomly; the average path length to isolate a sample across the forest becomes an anomaly score. Shorter average path → higher anomaly score.
For HBM test data with 50–200 parametric columns, Isolation Forest scales well (O(n log n) training) and handles correlated features without dimensionality reduction preprocessing. Key tuning parameters:
- `n_estimators`: 100–300 trees; score variance drops below 1% beyond 200- `contamination`: expected outlier fraction — set to 0.01–0.05 for mature HBM processes; influences decision threshold but not training- `max_features`: sub-sampling features per split (default `1.0`); reducing to `0.5` improves detection of local anomalies in high-dimensional dataIsolation Forest anomaly scores correlate well with **infant-mortality HTOL fail rate** in empirical HBM correlation studies, making them a practical early-warning signal before burn-in.


## PCA Reconstruction Error as Anomaly Score

Principal Component Analysis retains the top-K eigenvectors capturing the dominant variance in the training population. For each production die, project its parametric vector into the K-dimensional subspace, reconstruct it, and compute the **reconstruction error** (squared Euclidean distance between original and reconstructed vectors). Anomalous die — those whose correlation structure deviates from the norm — have high reconstruction error because the retained PCs do not span their feature direction.
Practical steps for HBM data:
- Fit PCA on a golden reference population (first-pass yield &gt; 99%): typically K = 10–20 PCs explain 90–95% of variance- Threshold reconstruction error at the 99th percentile of the training set- Monitor PC score drift (Hotelling T² statistic) across wafer lots to detect process shifts- Decompose reconstruction error per feature to identify <em>which</em> parameter is anomalous — critical for debugPCA reconstruction error is **interpretable** — a key advantage over black-box methods when root-cause engineering review is required for JEDEC qualification lots.


## Integration into ATE Flow and Disposition

Anomaly detection integrates into the ATE flow as a **post-test computational step** executed on the tester host or in a near-real-time cloud pipeline. The workflow:
- **Data ingestion**: parametric STDF records (PTR/FTR) parsed per wafer lot; each die becomes one feature vector- **Scoring**: apply pre-trained model (updated weekly or on process change); each die receives an anomaly score 0–1- **Disposition map**: score &gt; threshold → soft-bin 90x; pass through to standard pass/fail bins below threshold- **Feedback loop**: soft-bin 90x die sampled to reliability at 5–10% rate for model calibration; confirmed fails retrain the modelUnder JEDEC JESD235C, lot qualification requires demonstration of **parametric distribution stability**. Anomaly scores provide a compact, auditable metric for this requirement. HBM vendors including SK Hynix and Micron have disclosed ML-assisted outlier screening in qualification presentations at the HBM Summit and ISSCC.


## Key Takeaways

- DBSCAN identifies spatial and feature-space density outliers without requiring a pre-set number of clusters, making it robust to non-spherical HBM failure clusters.
- Isolation Forest scores anomalies by isolation path length — shorter paths mean higher outlier probability — and scales efficiently to 100+ parametric dimensions.
- PCA reconstruction error provides an interpretable per-feature anomaly breakdown essential for engineering disposition and JEDEC qualification evidence.
- Anomaly scores from unsupervised models correlate with infant-mortality reliability metrics, enabling pre-burn-in yield protection.
- Soft-bin disposition with reliability sampling closes the feedback loop, continuously calibrating the model to process drift.

## References

1. **[JEDEC]** High Bandwidth Memory (HBM) DRAM Standard — JESD235C — sections 4.3 (parametric limits), 8 (qualification requirements)
2. **[Paper]** A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise — Ester, Kriegel, Sander, Xu — KDD 1996; foundational DBSCAN reference
3. **[Paper]** Isolation Forest — Liu, Ting, Zhou — IEEE ICDM 2008; doi:10.1109/ICDM.2008.17
4. **[Paper]** Principal Component Analysis Applied to Semiconductor Test Data for Outlier Detection — Draper et al. — IEEE Trans. Semiconductor Manufacturing, vol. 24, no. 3, 2011
5. **[Web]** Scikit-learn: Machine Learning in Python — Pedregosa et al. — JMLR 12:2825-2830, 2011; sklearn.ensemble.IsolationForest, sklearn.cluster.DBSCAN, sklearn.decomposition.PCA
6. **[Book]** HBM Parametric Test and Reliability Qualification — Jeddeloh & Keeth — Hot Chips 2012 presentation; SK Hynix HBM3E characterisation, ISSCC 2024

## Additional Learning: Mahalanobis Distance as a Parametric Outlier Score

Mahalanobis distance generalises the z-score to multivariate data by normalising with the full covariance matrix: d = sqrt((x−μ)ᵀ Σ⁻¹ (x−μ)). Unlike Euclidean distance in PCA space, Mahalanobis distance accounts for all inter-parameter correlations without discarding variance in the lower PCs. For HBM data with strongly correlated voltage and timing parameters, Mahalanobis scoring is more sensitive to joint-distribution anomalies than per-column SPC. The squared Mahalanobis distance follows a chi-squared distribution with p degrees of freedom under multivariate normality, giving a principled p-value threshold for outlier calls rather than an empirical percentile.
