# RESULTS DIRECTORY — Group 06, CLC02

This directory contains all experimental outputs, saved predictions, computed metric tables, publication figures, and system verification logs.

---

## 1. Directory Structure

```
Results/
├── tables/         # 35 CSV tables covering data checks (D*), EDA (E*), results (R*), and LR (L*)
├── figures/        # 27 publication-quality PNG figures (300 DPI) and system architecture diagrams
├── predictions/    # Raw per-unit predictions from validation and official test passes
└── logs/           # Formal verification logs, experiment run logs, and document build validation
```

---

## 2. Key Result Tables (`tables/`)

All tables correspond directly to the findings presented in the main paper and supplementary report:

- **Primary Benchmark:**
  - `R1_validation_per_class.csv`: In-domain validation performance across all model families.
  - `R2_test_per_class.csv`: Single official test evaluation under locked configurations (Macro-F1, per-class F1, accuracy, QWK).
  - `R3_confusion_matrices.csv`: Confusion matrices on the official test set.

- **Context Ablation (Level 0 vs Level 1):**
  - `R4a_L1_vs_L0_same_units_deltas.csv`: Metric improvements of Level 1 over Level 0 on identical units, with 95% paired essay-level bootstrap confidence intervals (2,000 resamples).
  - `R4b_L1_vs_L0_paired_outcomes.csv`: Unit-level transition counts and win/loss tallies.
  - `R4c_L0_to_L1_prediction_transition_test.csv`: 3x3 prediction migration matrix on test data.

- **Leave-One-Prompt-Out Generalization (LOPO):**
  - `R5_lopo_vs_indomain_per_class.csv`: Performance on unseen prompts vs in-domain on identical validation units.

- **Error Analysis & Confound Checks:**
  - `R6_test_by_discourse_type.csv`: Breakdown across the 7 discourse types (Lead, Position, Claim, Counterclaim, Rebuttal, Evidence, Concluding Statement).
  - `R7_L1_errors_by_length_quartile.csv`: Error rates, A↔E confusion share, and class balance across essay length quartiles Q1–Q4.
  - `R8_ten_cases.csv`: Detailed case studies of the 10 highest-confidence Ineffective failure units.
  - `R9_ell_subgroups.csv`: Subgroup fairness audit across English Language Learner (ELL) status.

- **Data Integrity & Diagnostics:**
  - `D2_record_filtering.csv` – `D9_missingness.csv`: Verification checks C1–C7 confirming zero row mismatches, valid vocabularies, and correct hash signatures.
  - `L1_lr_validation.csv` – `L3_lr_case8_contributions.csv`: Interpretable Logistic Regression feature attribution weights.

---

## 3. Saved Predictions (`predictions/`)

Contains complete row-level predictions for every evaluated unit:

- `test_predictions_L0.csv`, `test_predictions_L1.csv`, `test_predictions_PA.csv`: DeBERTa-v3 official test outputs (93,677 units each) with predicted labels and class probabilities.
- `val_predictions_L0.csv`, `val_predictions_L1.csv`, `val_predictions_PA.csv`: DeBERTa-v3 validation outputs (29,102 units each).
- `test_predictions_rf_feature_set_b.csv`: Random Forest test predictions (Feature Set B).
- `strongest_baseline_predictions.csv`: Random Forest validation predictions.
- `predictions_fold1.csv`, `predictions_fold2.csv`, `predictions_fold3.csv`: DeBERTa-v3 LOPO predictions for the three held-out prompts.
- `val_predictions_L1w2.csv`, `val_predictions_L1para.csv`, `val_predictions_L2.csv`, `val_predictions_L3.csv`: Supplementary wider-context validation runs.

---

## 4. System Logs (`logs/`)

- `data_checks_log.txt`: Execution log of verification checks C1–C7.
- `results_log.txt`: Console output of full metrics recomputation.
- `official_test_run_log.txt`: Timestamped execution log of the official test run.
- `build_checks.json` & `build_checks_paper.json`: Document QA logs confirming page count, heading hierarchy, margins, and font consistency.
