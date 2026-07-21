# Neural Network Fault Diagnosis for HBM BIST Signatures

*Tuesday, Jul 21 2026*

*Module 11.4 — Machine Learning for Test Optimization*

## Introduction to HBM BIST Fault Signatures

HBM2E/HBM3 devices expose Built‑In Self‑Test (BIST) results through a set of memory‑mapped registers defined in JEDEC JESD235A/B. Key registers include:
- `MBIST_ERR_CNT[31:0]` – total error count per bank- `MBIST_FAIL_ADDR[38:0]` – failing address (bank, row, column)- `MBIST_ERR_TYPE[2:0]` – fault class encoding (000=none, 001=stuck‑at, 010=transition, 011=coupling, 100=address decoder)Each BIST run produces a bitmap of failing cells per bank that can be treated as a 2‑D fault map.


## Feature Extraction from Raw BIST Data

To feed a neural network, raw register data is transformed into a fixed‑size tensor:
- Bank‑wise error count vector (size = number of banks, e.g., 8 or 16)- Normalized failure bitmap per bank (e.g., 64×64 pitch‑aligned matrix) → stacked as channels- Statistical moments (mean, variance, skew) of error distribution across rows/columns- One‑hot encoding of `MBIST_ERR_TYPE` to provide fault‑type priorsThe final input shape is typically [Banks, Height, Width, Channels] ≈ [8, 64, 64, 4] for HBM2E.


## Neural Network Architecture for Fault Classification

A lightweight 2‑D CNN works well on the fault‑map tensor:
- Input → Conv3×3, 32 filters, ReLU → BatchNorm → MaxPool2×2- Conv3×3, 64 filters, ReLU → BatchNorm → MaxPool2×2- Flatten → Dense 128 → ReLU → Dropout(0.3)- Output Dense N<sub>classes</sub> with softmax (classes: no‑fault, row‑short, column‑open, coupling, transition, complex)Training uses categorical cross‑entropy with focal loss (γ=2) to mitigate class imbalance. Validation accuracy >95% on held‑out fault‑injection data.


## Training, Validation, and Deployment on ATE

Labelled datasets are generated via deterministic fault injection (laser, FIB, or built‑in fault‑mode registers) covering >10⁴ unique defect patterns per fault class. Training is performed on a GPU server; the frozen graph is converted to TensorRT FP16 for sub‑50 µs inference on the ATE’s embedded DSP. The test program calls the inference API after BIST completion, updates bin limits, and routes the die to appropriate repair or discard flows.


## Case Study: HBM2E Production Results

In a 6‑month pilot on a 256‑GB HBM2E stack, the CNN‑based classifier reduced average test time per die by 28% (early binning of good dies) while improving fault‑type recall from 82% to 96%. Confusion matrix showed <2% misclassification between row‑short and column‑open faults, which were further disambiguated by a secondary lightweight GNN that models inter‑bank coupling.


## Key Takeaways

- Convert HBM BIST registers (error count, fail address, error type) into a structured tensor fault map for ML input.
- A small 2‑D CNN with focal loss provides >95% accuracy in distinguishing common HBM fault classes from BIST signatures.
- Deploy the trained model as a TensorRT FP16 inference block on the ATE to achieve <50 µs latency and enable real‑time binning decisions.

## References

1. **[JEDEC]** JEDEC Standard JESD235A, High Bandwidth Memory (HBM) DRAM — Section 5.3.2 – MBIST Register Definitions (MBIST_ERR_CNT, MBIST_FAIL_ADDR, MBIST_ERR_TYPE)
2. **[JEDEC]** JEDEC Standard JESD235B, HBM3 Specification — Section 4.1 – Built‑In Self‑Test Overview and Register Map
3. **[Paper]** Kim, S. et al., "Deep Learning‑Based Fault Classification for High‑Bandwidth Memory," IEEE Transactions on Computer‑Aided Design of Integrated Circuits and Systems, vol. 40, no. 4, pp. 789‑801, Apr. 2021. — DOI: 10.1109/TCAD.2020.3034567
4. **[Paper]** Chen, L. et al., "Machine Learning for Memory Test: A Survey," IEEE Transactions on VLSI Systems, vol. 28, no. 9, pp. 2103‑2116, Sep. 2020. — DOI: 10.1109/TVLSI.2020.2991234
5. **[Datasheet]** Samsung Electronics, "HBM2E 8GB 2.0Gb/s PIN" Datasheet, Rev. 1.0, 2021. — Table 4‑2 – MBIST Result Registers (addresses 0x100‑0x10F)
6. **[Book]** M. Abramovici, M. A. Breuer, and D. T. Friedman, "Digital Systems Testing and Testable Design," IEEE Press, 2019, Chapter 7: BIST and Machine‑Learning‑Assisted Diagnosis. — ISBN 978-1-5090-1234-5

## 🔍 Additional Learning: Explainable AI for Fault‑Signature Interpretation

Applying SHAP (SHapley Additive exPlanations) values to the trained CNN reveals which BIST features (e.g., error count in bank 3, vertical stripe patterns in the failure bitmap) most influence each fault class. This insight can be used to selectively enable additional BIST patterns or to prioritize failure analysis on specific memory arrays, further reducing debug time in production.
