# CODE DIRECTORY — Group 06, CLC02

This directory contains reproduction scripts, analysis pipelines, executed Jupyter notebooks, and configuration metadata.

---

## 1. Quick Reproduction (1 Command, ~5 Seconds)

To reproduce the core empirical findings of the project (Table 1, Table 2, and Table 3 in the paper) directly from the saved prediction artifacts:

```bash
cd Code
python reproduce_results.py
```

This self-contained script computes:
1. **Table 1:** Validation and Official Test per-class F1, Macro-F1, Accuracy, and QWK for all model families (Majority Baseline, Random Forest Feature Set B, DeBERTa-v3 L0, DeBERTa-v3 L1 locked, and DeBERTa-v3 Prompt-Aware).
2. **Table 2:** Context ablation differences (Level 1 minus Level 0) evaluated on identical units.
3. **Table 3:** Leave-one-prompt-out (LOPO) generalization gap on held-out unseen prompts.

---

## 2. Dependencies (`requirements.txt`)

Install the required Python environment using:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `numpy`, `pandas`, `scipy`, `scikit-learn`: Data processing and evaluation metrics.
- `matplotlib`, `seaborn`: Visualization and figure generation.
- `torch`, `transformers`, `datasets`: Model definitions for transformer notebooks.
- `python-docx`, `PyMuPDF`: Academic report formatting and PDF compilation checks.

---

## 3. Directory Contents

### A. Scripts (`scripts/`)

- `common.py`: Shared path configurations, label mappings, and metric evaluation routines.
- `01_data_checks_eda.py`: Performs verification checks C1–C7 and generates EDA tables (E1–E9).
- `02_results_from_predictions.py`: Comprehensive metrics pipeline generating result tables R1–R7.
- `03_ten_cases.py`: Assembles the qualitative analysis table of the 10 highest-confidence Ineffective failure cases (Table R8).
- `04_figures.py`: Generates all 26 figures in 300 DPI PNG format.
- `05_lr_interpretable_reference.py`: Trains balanced Logistic Regression reference model for lexical feature attribution.
- `06_subgroup_ell.py`: Evaluates subgroup performance across English Language Learner (ELL) statuses (Table R9).
- `07_export_split_ids.py`: Generates clean essay and unit split CSV tables.
- `assemble_report.py`: Merges markdown chapter files into the unified report.
- `build_docx_pdf.py`: Compiles Word documents and PDFs with strict academic formatting checks (`--paper` builds the 8-page main paper).

### B. Executed Notebooks (`notebooks/`)

All notebooks contain preserved output cells documenting model training, loss progression, and test evaluations:

1. `01_deberta_prompt_aware_official_test.ipynb`: Official test run under locked configuration (DeBERTa-v3 L0, L1, Prompt-Aware).
2. `02_lopo_rerun_deberta_L0.ipynb`: Leave-one-prompt-out evaluation across 3 held-out prompts.
3. `03_random_forest_official_test.ipynb`: Random Forest Feature Set B reproduction and official test scoring.
4. `04_svm_official_test.ipynb`: Linear SVM baseline evaluation.
5. `05_threshold_tuning_and_case8.ipynb`: Decision threshold sensitivity analysis for Ineffective recall trade-offs.
6. `06_context_ablation_L1w2.ipynb` to `09_context_ablation_L3_whole_essay.ipynb`: Supplementary wider context explorations (±2 units, paragraph, source passage, whole essay).

### C. Configurations (`configs/`)

- `OFFICIAL_TEST_LOCK.json`: Test set integrity lock documenting SHA-256 signatures, configuration parameters, and timestamp.
- `deberta_run_metadata.json`: DeBERTa-v3 training parameters (learning rate 2e-5, effective batch size 32, seed 42, warm-up 10%).
- `rf_run_metadata.json`: Random Forest hyperparameters (200 trees, max depth 35, balanced class weights).
- `lopo_run_metadata.json`: Settings for leave-one-prompt-out cross-validation folds.
