# Predictive Yield Modeling via Wafer Map Correlation

*Tuesday, Jul 21 2026*

*Module 11.3 — Machine Learning for Test Optimization*

## Inline Metrology as Yield Predictors

Inline metrology captures process state at intermediate fabrication steps before electrical test is possible. Key measurement types used in yield prediction include:
- **CMP uniformity maps**: post-planarization thickness variation (WIWNU), measured by ellipsometry or reflectometry at 49-121 sites per wafer. Thickness non-uniformity directly impacts resistance and RC delay across die.- **Overlay error maps**: lithographic misalignment between layers measured in nm by optical overlay metrology (e.g., ASML Atlas-H). Overlay &gt;20% of critical dimension budget causes systematic pattern failures.- **Critical dimension (CD) maps**: gate or via width variation from CD-SEM or optical CD (OCD) tools. CD variation shifts Vt distributions and drives leakage spread.- **Defect density maps**: particle and scratch counts from inspection tools (KLA-Tencor Surfscan, KLARF output). Spatial clustering reveals tool-specific signatures.Each measurement type produces a spatial map across the 300 mm wafer. The regression target is the final wafer sort map from ATE: which dies pass, and at what parametric margin (e.g., Vmin, IDDQ, maximum test frequency).


## Wafer Map Registration and Feature Matrix Construction

Before regression can be applied, inline measurement grids must be registered to the die grid from the probe card layout. Critical alignment steps:
- **Coordinate system alignment**: wafer notch angle and map origin from SEMI M1 must match the ATE wafer map coordinate system (SEMI G85 format). A rotation or flip error misregisters all die-to-metrology assignments.- **Sparse-to-dense interpolation**: inline tools measure at 13, 49, or 121 sites per wafer, far fewer than the 500-2000 die on a 300 mm wafer. Spatial interpolation (bilinear, RBF, or kriging) expands the measurement grid to die resolution before feature extraction.- **Multi-layer temporal stacking**: overlay from lithography step N must be paired with CMP uniformity from step N-2 using lot/wafer/timestamp metadata from the MES. Mismatched layers corrupt the feature matrix.The result is a per-die feature matrix `X[die, feature]` where each column is an interpolated inline measurement, and the target vector `y[die]` is binary (pass/fail) or continuous (e.g., `IDDQ` or Vmin in mV). Typical feature counts range from 10 to several hundred parameters across all process steps.


## Regression Model Selection and Training

For binary yield (pass/fail), **logistic regression** is the baseline; for continuous parametric prediction (Vmin, leakage), ordinary least squares (OLS) or regularized variants are used.
- **Ordinary Least Squares (OLS)**: `y = X&#946; + &#949;`. Simple and interpretable but sensitive to multicollinearity when inline features are correlated (e.g., CMP thickness and overlay error often share spatial pattern). R-squared and adjusted R-squared are standard fit metrics.- **Ridge Regression (L2)**: adds penalty `&#955;||&#946;||&#178;` to the loss, shrinking correlated feature coefficients. Lambda is selected by k-fold cross-validation (typically k=5 or 10). Preferred when feature count exceeds ~20 or features are strongly correlated.- **Lasso Regression (L1)**: penalty `&#955;||&#946;||&#8321;` drives sparse solutions, automatically zeroing non-predictive features. Valuable for automatic feature selection from hundreds of inline parameters.- **Elastic Net**: linear combination of L1 and L2 penalties, controlled by mixing parameter `&#945;`. Best general choice when both feature selection and collinearity management are needed.For non-linear yield surfaces near systematic defect clusters, ensemble methods (XGBoost, LightGBM, random forests) capture interaction effects missed by linear models at the cost of interpretability.


## Model Evaluation Metrics for Yield Prediction

Models must be evaluated on held-out lots — never the training lot — to measure genuine predictive power. Key metrics in production use:
- **AUC-ROC**: for binary pass/fail prediction. AUC &gt; 0.80 is a practical threshold for production-quality yield prediction. Compute per wafer, then report mean ± std across a validation lot set.- **R&#178; (coefficient of determination)**: fraction of parametric variance explained. R&#178; &gt; 0.7 indicates useful predictive power for continuous targets such as IDDQ or Vmin.- **Lot-level yield correlation (&#961;)**: Pearson or Spearman correlation between predicted and actual die yield, reported at lot level to smooth within-wafer noise. This is the metric most relevant to production disposition decisions.- **Spatial residual map**: `y_actual - y_predicted` plotted as a wafer map. A good model leaves no systematic spatial pattern in residuals. Concentric ring or edge-heavy residuals indicate an unmodeled CMP or etch non-uniformity effect.Production deployment typically uses a prediction interval rather than a point estimate. If predicted lot yield falls below a control limit (e.g., mean - 2&#963;), the lot is flagged for engineering disposition before reaching probe, enabling early scrap or rework decisions.


## Closed-Loop Yield Learning and Model Maintenance

Predictive yield models degrade over time as process tools drift, consumables are replaced, or process recipes are optimized. Production-grade virtual metrology systems require:
- **Drift detection via SPC on residuals**: track prediction residuals (actual - predicted) using EWMA or Shewhart charts. A shift in residual mean or increase in variance signals process change requiring model retraining. EWMA with &#955;=0.2 is standard for slowly drifting processes.- **Rolling-window retraining**: ATE sort results feed back into the training pipeline via the MES. A 90-day rolling window is typical in high-volume production; shorter windows (30 days) are used after process changes or tool PM events.- **Confidence scoring via Mahalanobis distance**: lots with feature vectors far from the training distribution are flagged as low-confidence. Mahalanobis distance D&#178; = (x - &#956;)&#7488; &#931;&#8315;&#185; (x - &#956;) provides a scalar confidence metric. High-D lots should not be acted on autonomously without engineering review.- **Concept drift vs. data drift**: data drift (new tool with different absolute offset) is handled by feature normalization or recalibration. Concept drift (yield-metrology relationship changes after process optimization) requires full model retraining or domain adaptation techniques.The long-term goal is **virtual metrology**: predicting electrical yield at fab completion or after key inline steps, enabling early disposition and reducing cost-per-wafer at sort.


## Key Takeaways

- Inline metrology maps (CMP, overlay, CD) must be registered to die-grid coordinates and spatially interpolated to die resolution before regression modeling.
- Ridge or Lasso regression is preferred over OLS for yield prediction due to multicollinearity; Lasso additionally performs automatic feature selection.
- Model quality is evaluated by AUC-ROC (binary pass/fail) or R-squared (continuous), with spatial residual maps used to detect unmodeled systematic effects.
- Production models require EWMA-based drift monitoring and rolling retraining; Mahalanobis distance identifies out-of-distribution lots that should not be automatically dispositioned.

## References

1. **[JEDEC]** SEMI M1: Specification for Polished Single Crystal Silicon Wafers — SEMI M1 standard defining wafer flat/notch and coordinate system for 300 mm wafers — establishes map orientation used in metrology-to-die registration
2. **[JEDEC]** SEMI G85: ASCII Format for Semiconductor Die Results — Standard defining the wafer map interchange format used by ATE and MES for sort results; wafer bin map format for die-level pass/fail data
3. **[Paper]** Virtual Metrology for Semiconductor Manufacturing: A Review — Hung-En Tseng et al., IEEE Trans. Semiconductor Manufacturing, vol. 25, no. 1, pp. 132-144, 2012 — comprehensive review of VM regression methods and industrial deployment
4. **[Book]** The Elements of Statistical Learning — Hastie, Tibshirani, Friedman — Chapter 3 (Linear Methods for Regression) and Chapter 18 (High-Dimensional Problems); 2nd ed., Springer, 2009
5. **[Datasheet]** KLA KLARF 1.8 File Format Specification — KLA-Tencor KLARF (KLA Results File) v1.8 format documentation for defect map interchange between inspection tools and downstream analysis — key for defect density feature extraction
6. **[Paper]** Yield Prediction Using Inline Parametric Data in Semiconductor Manufacturing — L. Pelegrini et al., IEEE Trans. Semiconductor Manufacturing, vol. 20, no. 4, pp. 391-400, 2007 — case study of logistic regression for sort yield prediction from inline data

## Additional Learning: Kriging Interpolation for Sparse Metrology Upsampling

When inline metrology provides only 49 or 121 measurement sites across a 300 mm wafer but die count is 500-2000, interpolation quality directly impacts regression accuracy. Ordinary kriging — which models the spatial covariance structure (variogram) of the metrology field — outperforms bilinear interpolation for CMP thickness maps because it accounts for anisotropic spatial correlation, such as radial polish patterns from the CMP head rotation. The variogram fitting step estimates the nugget (measurement noise floor), sill (total process variance), and range (spatial correlation length) from the available measurement points; these parameters drive Best Linear Unbiased Prediction (BLUP) estimates at unsampled die locations. Kriging standard errors can also be used as per-die uncertainty weights when training the downstream regression model, down-weighting die whose interpolated feature values are less certain.
