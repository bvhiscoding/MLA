# Machine Learning Applications (61FIT4MLA / 62FIT4MLA) — Final Project Submission

## Project: Predicting the Effectiveness of Argumentative Discourse Units in Student Essays
**Class:** CLC02  
**Group:** 06  
**Lecturer:** Bùi Quốc Khánh  
**Submission Date:** November 2026  

---

## 1. Group Members and Individual Contributions

| Role | Member Name | Student ID | Primary Responsibilities & Contributions |
|:---:|:---|:---:|:---|
| **Role 1** | [Student Name 1] | [Student ID 1] | **Data Pipeline & Classical Modeling:** Data cleaning, row index tracking, Feature Set B construction (TF-IDF 15k, one-hot discourse types, 5 structural features), Random Forest model validation and official test pass, essay length vs. holistic score confound analysis. |
| **Role 2** | [Student Name 2] | [Student ID 2] | **Transformer Models & Context Ablation:** DeBERTa-v3-base fine-tuning pipeline, context ablation (Level 0 vs Level 1), supplementary wider-context ladder (±2 units, paragraph, source passage, whole essay), decision threshold sensitivity tuning, Linear SVM baseline. |
| **Role 3** | [Student Name 3] | [Student ID 3] | **Error Analysis, Generalization & Test Governance:** Leave-One-Prompt-Out (LOPO) prompt generalization protocol across 15 prompts, qualitative analysis of 10 high-confidence Ineffective failure cases, paired essay-level bootstrap uncertainty estimation (2,000 resamples), official test governance and lock verification. |

*(Please replace placeholders `[Student Name ...]` with exact group member names and student IDs).*

---

## 2. Project Overview & Main Findings

Teachers of argumentative writing need granular feedback on which discourse components of an essay are ineffective, rather than only an overall holistic score. This project investigates how well machine learning and transformer models can predict the rater-assigned effectiveness (**Ineffective**, **Adequate**, **Effective**) of argumentative discourse units on the **PERSUADE 2.0** corpus (237,966 units across 25,996 essays; 4.5% Ineffective minority class).

### Key Research Questions and Findings:
1. **Model Comparison on Identical Units (RQ1):**  
   On the official test set (93,677 units, scored once with locked configurations), fine-tuned **DeBERTa-v3-base (Level 1)** achieved **Macro-F1 0.577** and Ineffective-F1 0.368, significantly outperforming the strongest classical model (**Random Forest FS-B: Macro-F1 0.510**, Ineffective-F1 0.202) by **+0.068 [0.061, 0.075]**, while the majority baseline achieved Macro-F1 0.297.
2. **Context Ablation (RQ2):**  
   Supplying immediate neighbouring units (Level 1: preceding and succeeding units) improves test Macro-F1 by **+0.016 [0.012, 0.021]** over the unit alone (Level 0), with the largest gains observed on relational discourse types (Counterclaims +0.037, Rebuttals +0.028). The gain is comparable in magnitude to run-to-run variation.
3. **Prompt Transfer & Unseen Prompts (RQ3):**  
   Under Leave-One-Prompt-Out (LOPO) evaluation, unseen prompts suffer a Macro-F1 drop between **0.025 and 0.092** compared to in-domain training, with the largest drop on source-based narrative prompts.
4. **Length and Proficiency Confound (RQ4):**  
   Essay length strongly correlates with student proficiency (Spearman 0.76 with holistic score). Within the same score band, error rates still rise with length (odds ratio 1.19 per length quartile), confirming a residual length/complexity effect rather than mere "loss of context".

---

## 3. Submission Package Organization

This folder is organized in accordance with the official course submission requirements:

```
MLA_Final/
├── README.md               # Group contributions, run instructions, and project summary (this file)
├── Report/                 # Academic report documents (PDF and editable Word)
│   ├── Final_Report.pdf                 # Main research paper (8 pages, standard format)
│   ├── Group06_CLC02_Final_Paper.pdf    # Main research paper (8 pages)
│   ├── Group06_CLC02_Final_Paper.docx   # Word source of main paper
│   ├── Group06_CLC02_Final_Report.pdf   # Comprehensive Supplementary Report (86 pages)
│   └── Group06_CLC02_Final_Report.docx  # Word source of Supplementary Report
├── Code/                   # All reproduction scripts, notebooks, and configurations
│   ├── README.md                        # Execution documentation
│   ├── requirements.txt                 # Python dependencies
│   ├── reproduce_results.py             # Single-command reproduction script (~5s)
│   ├── scripts/                         # Modular analysis and report-building scripts (01-07)
│   ├── notebooks/                       # 9 executed Jupyter notebooks with saved outputs
│   └── configs/                         # Locked test configurations and hyperparameters
├── Results/                # All saved outputs, tables, and publication figures
│   ├── README.md                        # Documentation of tables, figures, and logs
│   ├── tables/                          # 35 CSV tables (D*, E*, R*, L*)
│   ├── figures/                         # 27 publication-quality figures (300 DPI)
│   ├── predictions/                     # 16 per-unit prediction CSV files
│   └── logs/                            # Integrity verification and build QA logs
└── Data/                   # Data documentation, split tables, and verification samples
    ├── DATA_README.md                   # Source, version, license, links, and preparation steps
    ├── rubrics/                         # Official PERSUADE 2.0 rubric PDFs
    ├── splits/                          # Split mappings (split_essays.csv, split_units.csv.gz)
    └── samples/                         # Approved unit metadata sample (_units_slim.csv.gz)
```

---

## 4. Setup and Reproduction Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.10–3.12)
- Operating System: Windows, Linux, or macOS

### Step 1: Environment Setup
```bash
# Clone or open the MLA_Final directory
cd MLA_Final/Code

# Install required dependencies
pip install -r requirements.txt
```

### Step 2: Reproduce Main Empirical Results (~5 Seconds)
To recompute the main empirical tables reported in the paper (Table 1, Table 2, and Table 3) directly from the saved prediction files:
```bash
python reproduce_results.py
```

### Step 3: Run Full Analysis Pipeline (Optional, ~3 Minutes)
To rerun the complete modular analysis pipeline and regenerate all result tables, figure assets, and verification checks:
```bash
python scripts/02_results_from_predictions.py
python scripts/03_ten_cases.py
python scripts/04_figures.py
python scripts/05_lr_interpretable_reference.py
python scripts/06_subgroup_ell.py
python scripts/07_export_split_ids.py
```

*Note on Full Raw Data:* To rerun `scripts/01_data_checks_eda.py` from raw 1GB CSV files, download `persuade_corpus_2.0_train.csv` and `persuade_corpus_2.0_test.csv` following the instructions in `Data/DATA_README.md` and place them in `Data/`.

---

## 5. Test Set Governance Protocol

- **Single Test Pass:** The official test set (93,677 units) was scored exactly once under locked parameters.
- **Lock File:** The test hash and configuration are cryptographically recorded in `Code/configs/OFFICIAL_TEST_LOCK.json`.
- **Validation Gate:** The classical Random Forest model was required to reproduce its validation performance (Macro-F1 0.523) before being evaluated on the test set.
- **Independence:** All model hyperparameter selection and threshold tuning decisions were conducted exclusively on the validation set.
