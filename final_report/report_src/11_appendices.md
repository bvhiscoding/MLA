# Appendix A. Run Table {.appendix}

Table A.1 lists every run behind a number in this report, with its split, configuration and output location.

Table A.1. Run table.

| Run | Model and input | Evaluated on (training data) | Configuration / seed | Main output | Status |
| --- | --- | --- | --- | --- | --- |
| R01 | BERT + DeBERTa ensemble | 14,303-unit development split; trained on the training part | — | `Ensemble_BERT_DeBERTa_A003/` | Dropped (gain CI contains 0) |
| R02 | LR, LR + thresholds, calibrated SVM, RF, LightGBM on FS-A / FS-B | 29,102 val; trained on 115,187 | Seed 42, sklearn 1.6.1 | `outputs/` | Used (RF FS-B = classical system) |
| R03 | DeBERTa-v3 L0 | 29,102 val; trained on 115,187 | Table 4.3 (fp16, RTX 4070 SUPER) | `person2_output/` | Used (DeBERTa vs RF on validation) |
| R04 | DeBERTa-v3 L0 and L1, first run | 29,102 val; trained on 115,187 | Table 4.3 | `week10_full_person2/`, `outputs/` | Used (run-to-run comparison, ten cases) |
| R05 | RF FS-B LOPO, 15 folds | Held-out prompt; trained on 14 prompts each | 150 trees, depth 35 | `outputs/` | Used |
| R06 | DeBERTa L0, L1, PA | 29,102 val; 93,677 test once; trained on 115,187 | Table 4.3, A100, bf16 | `Week11_Person3_…/` | Used (test pass, lock file) |
| R07 | RF FS-B | 29,102 val (gate 0.5261), then test once; trained on 115,187 | 200 trees, depth 35, sklearn 1.6.1 | `outputs/` | Used |
| R08 | Linear SVM, TF-IDF | Test; val 0.485; trained on 144,289 (115,187 for val) | — | `outputs/` | Supplementary |
| R09 | Linear SVM LOPO, 3 folds | Held-out prompt; trained on 14 prompts | — | `outputs/` | Supplementary |
| R10 | DeBERTa L0 LOPO, 3 folds | Held-out prompt, once; trained on 14 prompts | Fixed 3 epochs, final model, transformers 4.57.6, L4 | `week11_lopo_rerun/` | Used |
| R11 | L1 ±2 (2 runs), paragraph, L2 (2 runs), L3 3 ep, L3 7 ep | 29,102 val only; trained on 115,187 | L1 recipe, L4, bf16 | `week11_context_levels/`, `outputs/` | Exploratory |
| R12 | Post-hoc class-offset correction and ensembles | Val, 2-fold cross-fitting by essay | Grid −2.0 … +1.5 | `outputs/` | Exploratory |
| R13 | LR FS-B (interpretable reference) | 29,102 val; trained on 115,187 | C = 1, balanced, sklearn 1.9 | `final_report/` | Used (Tables 4.1, 6.1) |

# Appendix B. Reproducibility and Execution Instructions {.appendix}

## B.1 Data

1. Download the PERSUADE 2.0 training and test CSV files from the links in the corpus repository (github.com/scrosseye/persuade_corpus_2.0; the test archive password is given in its README).
2. Place them at `data/persuade_raw/persuade_corpus_2.0_train.csv` and `data/persuade_raw/persuade_corpus_2.0_test.csv`. Do not open and re-save them in a spreadsheet program.
3. The files used in this report have SHA-256 `f61319edd8bf16a982711ea0399fad59c05afaec05cdf0767f16a2c05c467e23` (train) and `8b4cbbda471b313e5d11da10d4fc2659defa1a8f710639e98d011e1c7141d3a6` (test). Script 01 checks both hashes. A freshly downloaded file may differ in its numeric ID columns (ours were altered by a spreadsheet program); `essay_id_comp`, texts and labels are what matter, and script 01 checks them.

## B.2 Environments

Table B.1. Software environments.

| Purpose | Environment |
|---|---|
| Final-report scripts (data checks, tables, figures, LR reference) | Python 3.14, pandas 3.0, NumPy, SciPy, statsmodels 0.15, scikit-learn 1.9, matplotlib 3.11; CPU only |
| Classical models (RF FS-B) | Python 3.10, scikit-learn 1.6.1 (the RF result is reproduced exactly only with this version) |
| DeBERTa | Google Colab, Python 3.13, PyTorch 2.11 + CUDA 13, transformers 4.57.6 (not 5.x), bf16; A100 for R06, L4 for R10–R11 |
| Diagrams | Mermaid CLI with the configuration in `final_report/diagrams/` |

## B.3 Commands that rebuild the report's numbers and figures

From the repository root, without a GPU (about three minutes):

```
python final_report/scripts/01_data_checks_eda.py        # checks C1-C7, EDA tables D*, E*
python final_report/scripts/02_results_from_predictions.py  # tables R1-R7 from saved predictions
python final_report/scripts/03_ten_cases.py              # table R8 (ten cases with IDs)
python final_report/scripts/05_lr_interpretable_reference.py # LR reference, tables L1-L3
python final_report/scripts/06_subgroup_ell.py           # table R9
python final_report/scripts/07_export_split_ids.py       # clean split files keyed by essay_id_comp / row_idx
python final_report/scripts/04_figures.py                # all data figures
```

To retrain models (GPU): `Week11_Person3_DeBERTa_OfficialTest/07_person3_prompt_aware_official_test.ipynb` (L0, L1, PA and the test pass; it refuses to score the test twice), `week11_lopo_rerun/11_lopo_rerun_L0.ipynb` (LOPO), `week11_context_levels/*.ipynb` (context ladder), `Person1/run_rf_official_test.py` (RF FS-B with the validation gate), `Person1/script_holistic_length_table.py` (length × score tables and regression), `script_threshold_tuning_and_case8.py` (threshold table), `script_lopo_same_units_gap.py --rerun` (same-unit LOPO gaps). Every notebook is saved with its outputs.

## B.4 Seeds, splits and identifiers

All splits and models use seed 42; the random raw-record sample in Table 3.5 uses seed 2026. The train/validation assignment is defined by the `row_idx` values in `val_predictions_L1.csv` (validation) and their complement (training); `final_report/tables/split_essays.csv` (one row per essay, keyed by `essay_id_comp`) and `final_report/tables/split_units.csv.gz` (one row per unit, keyed by `row_idx`) store the assignment for all three sets; they are produced and checked by `final_report/scripts/07_export_split_ids.py`. The older `outputs/split_assignments.csv` is keyed by the spreadsheet-rounded `essay_id` and should not be used for joins. Every prediction file stores `row_idx`, `essay_id_comp`, discourse type, gold label, predicted label and the three probabilities. Never join on `discourse_id`.

## B.5 Files behind the main tables

Table B.2. Where each main result comes from.

| Report element | Source file(s) |
|---|---|
| Table 3.4–3.5, data checks | `final_report/evidence/data_checks_log.txt`, `tables/D*.csv` |
| Table 6.1 | `tables/R1_validation_per_class.csv`, `tables/L1_lr_validation.csv` |
| Tables 6.2–6.4 | `tables/R4a`, `R4b`, `R4c` |
| Table 6.5, Figure 6.3 | `tables/R2_test_per_class.csv`, `Week11_…/outputs/official_test_deberta_bootstrap.csv`, `outputs/official_test_bootstrap_deberta_vs_rf.csv` |
| Tables 6.6–6.7 | `outputs/lopo_*`, `tables/R5_lopo_vs_indomain_per_class.csv` |
| Table 6.8 | `outputs/ineffective_threshold_tuning_table.csv` |
| Table 6.10 | `outputs/context_levels_validation_summary.csv`, `context_levels_posthoc_bias_ensemble.csv` |
| Tables 7.1–7.3 | `tables/R7`, `outputs/holistic_score_x_length_quartile_error_rates.csv`, `outputs/length_within_score_regression.csv` |
| Tables 7.4–7.5 | `tables/R8_ten_cases.csv` |

## B.6 Data that are not shared

The PERSUADE CSV files (licence and size) and the source articles used for Level 2 (copyright) are excluded from the repository by `.gitignore`. Model checkpoints (about 2.2 GB) are not shared; all predictions behind the tables are.

# Appendix C. Individual Contributions {.appendix}

Roles were assigned per week in the planning files `HUONG_DAN_PHAN_CONG_TUAN_9.md`, `WEEK10_PLAN_AND_ASSIGNMENTS.md` and `WEEK11_PLAN_AND_ASSIGNMENTS.md` as Member 1 (data and classical models), Member 2 (transformer and context) and Member 3 (error analysis, LOPO and test governance). The person holding a role changed between weeks; the names below are filled in by the group from its own records. Table C.1 lists the work and the evidence; detailed decision logs per role, written in the course's format (date, question, assumption before the run, output, change), are kept in the repository.

Table C.1. Contributions by role and week.

| Week | Role 1 | Role 2 | Role 3 |
|---|---|---|---|
| Name | [name for Wk 9] / [name for Wk 10–11] | [name] | [name for Wk 9] / [name for Wk 10–11] |
| Before Wk 9 | (member who later held Role 1 in Week 9) Literature search (papers R01–R03), dataset selection, prototype pipeline (`discourse_effectiveness_pipeline.py`), BERT + DeBERTa ensemble run A003 (`Ensemble_BERT_DeBERTa_A003/`) | [to be completed by the group] | [to be completed by the group] |
| Wk 9 | Data pipeline, essay-grouped split (115,187 / 29,102), classical baselines on FS-A/FS-B, label-mapping check for LR (`01_Data_Pipeline_Classical_Baseline.*`, `week9_person1_outputs/`) | Single DeBERTa vs RF on the same units with essay bootstrap, calibration check, decision to drop the ensemble (`person2_output/`) | Ten failure cases, errors by type and prompt, ELL audit, literature mapping (`outputs/10_ineffective_case_studies.md`, `error_breakdown_*.csv`) |
| Wk 10 | Label × prompt × length tables; RF LOPO for 15 prompts (`week10_output_person1/`) | Controlled L0 vs L1 ablation; re-check of the ten cases (`week10_full_person2/`) | DeBERTa LOPO on 3 prompts; Week 10 report (`week10_person3_full/`) |
| Wk 11 | Holistic score × length table and regression; RF FS-B test with validation gate (`Person1/`) | Threshold analysis and case counting; linear SVM on test and LOPO (`Person2Khoa/`, `script_threshold_tuning_and_case8.py`) | Retraining of L0/L1/PA, locked test pass, bootstrap (`Week11_Person3_…/`); audit of code and report (`RA_SOAT_…md`); LOPO rerun; context ladder (`week11_lopo_rerun/`, `week11_context_levels/`) |
| Final report | [to be completed by the group] | [to be completed by the group] | Data verification scripts, recomputed tables and figures, report text (`final_report/`) |

Decisions that each role can show evidence for are recorded in Table 7.6 and in the repository.

# Appendix D. Use of AI Tools {.appendix}

AI assistants were used while preparing the project. None is part of the studied pipeline: no model output in this report was produced by prompting a language model. Table D.1 lists the uses we know of; members complete it for their own work.

Table D.1. AI assistance and how it was checked.

| Tool | Used for | How the output was checked |
|---|---|---|
| Claude Code (Anthropic) | Running Colab GPU jobs through a command-line client; generating and debugging notebooks for the GPU runs; an audit of code and report; data-verification and figure scripts and drafting of this final report | Every number recomputed from raw data or saved predictions by scripts in the repository; assertions on row alignment and labels; the audit's findings were checked against the code and data before any change; report text checked against the tables |
| OpenAI Codex (command-line agent) | Regenerating notebooks from corrected scripts; building the Word and PDF versions of reports | Notebooks re-executed; generated documents compared with the Markdown source |
| Gemini / Antigravity IDE | Coding assistance and drafting | [members to describe] |
| [other tools used by members] | [ ] | [ ] |

Where the AI-assisted audit pointed to a problem in code or data, the group verified it by rerunning code on the data before changing anything. Explanations that AI tools suggested but that could not be verified against data were not used. AI detectors were not used.

# Appendix E. Supplementary Tables {.appendix}

Table E.1. Official test results by discourse type: locked L1 and Random Forest (table R6).

| Type | Units | Gold Ineff | L1 Macro-F1 | L1 F1 Ineff / Adeq / Eff | RF Macro-F1 | RF F1 Ineff |
|---|---:|---:|---:|---|---:|---:|
| Lead | 5,792 | 304 | 0.590 | 0.344 / 0.811 / 0.614 | 0.516 | 0.140 |
| Position | 10,250 | 368 | 0.544 | 0.293 / 0.889 / 0.450 | 0.400 | 0.129 |
| Claim | 32,375 | 910 | 0.518 | 0.292 / 0.836 / 0.427 | 0.409 | 0.068 |
| Counterclaim | 3,717 | 114 | 0.513 | 0.281 / 0.849 / 0.409 | 0.424 | 0.100 |
| Rebuttal | 2,880 | 112 | 0.508 | 0.226 / 0.816 / 0.482 | 0.480 | 0.173 |
| Evidence | 29,885 | 1,956 | 0.622 | 0.419 / 0.836 / 0.612 | 0.542 | 0.251 |
| Concluding Statement | 8,778 | 461 | 0.609 | 0.391 / 0.837 / 0.597 | 0.551 | 0.258 |

Table E.2. L1 error rate (%) by holistic score and length quartile, all cells, validation and official test (essay-bootstrap 95% CI; N = units / essays).

| Score | Split | Q1 (≤315) | Q2 (316–422) | Q3 (423–566) | Q4 (≥567) |
|:---:|---|---|---|---|---|
| 1 | Val | 39.6 [32.6, 45.6]; 356/91 | 22.2 [12.9, 32.7]; 63/19 | 33.8 [15.8, 51.1]; 74/13 | 34.8 [16.7, 64.3]; 23/4 |
| 1 | Test | 32.0 [28.7, 35.2]; 1,065/311 | 29.3 [21.7, 37.1]; 239/65 | 31.7 [20.6, 44.1]; 101/26 | 26.3 [9.8, 42.9]; 57/16 |
| 2 | Val | 23.2 [21.3, 25.1]; 3,200/493 | 31.4 [27.1, 35.6]; 722/91 | 33.2 [26.3, 39.5]; 295/34 | 38.8 [27.9, 51.0]; 80/11 |
| 2 | Test | 23.7 [22.8, 24.7]; 13,060/2,054 | 25.7 [23.2, 28.3]; 2,141/279 | 25.9 [22.1, 29.6]; 858/98 | 26.8 [21.8, 31.8]; 418/50 |
| 3 | Val | 19.3 [17.7, 21.1]; 3,517/424 | 21.8 [20.0, 23.9]; 3,743/404 | 22.9 [19.8, 26.0]; 1,465/143 | 28.2 [22.1, 34.3]; 472/40 |
| 3 | Test | 17.6 [16.8, 18.5]; 13,684/1,662 | 20.8 [19.7, 21.9]; 10,596/1,150 | 22.3 [20.8, 24.1]; 4,597/459 | 29.2 [26.2, 32.3]; 1,618/154 |
| 4 | Val | 19.6 [13.4, 26.6]; 260/29 | 22.0 [19.9, 23.9]; 2,622/260 | 28.5 [26.5, 30.5]; 3,984/379 | 31.1 [28.2, 33.9]; 1,961/174 |
| 4 | Test | 23.1 [19.4, 26.8]; 1,267/139 | 22.4 [21.3, 23.7]; 9,131/910 | 25.1 [24.0, 26.2]; 11,755/1,101 | 29.7 [27.8, 31.5]; 4,404/387 |
| 5 | Val | — | 29.1 [21.3, 38.0]; 127/12 | 30.3 [26.9, 34.0]; 1,391/120 | 31.7 [29.6, 34.0]; 3,336/277 |
| 5 | Test | — | 23.0 [18.2, 27.8]; 418/37 | 29.3 [27.6, 31.0]; 4,836/430 | 31.2 [29.9, 32.5]; 9,012/748 |
| 6 | Val | — | — | 23.5 (n.a.); 17/1 | 26.8 [24.2, 29.7]; 1,394/100 |
| 6 | Test | — | — | 25.2 [14.2, 36.3]; 123/11 | 30.1 [28.0, 32.1]; 4,297/315 |

Table E.3. Prediction transitions from Level 0 (rows) to Level 1 (columns), same units.

| Split | L0 prediction | L1 Ineffective | L1 Adequate | L1 Effective |
|---|---|---:|---:|---:|
| Validation | Ineffective | 1,057 | 630 | 10 |
| Validation | Adequate | 697 | 17,489 | 1,294 |
| Validation | Effective | 7 | 1,974 | 5,944 |
| Test | Ineffective | 3,024 | 2,016 | 11 |
| Test | Adequate | 2,276 | 59,170 | 4,052 |
| Test | Effective | 16 | 5,853 | 17,259 |

Table E.4. Logistic Regression (FS-B) features with the largest weight for each class relative to the class average (table L2).

| Class | Top features (weight) |
|---|---|
| Ineffective | witch (+3.22), plant (+3.13), on whether (+3.10), aliens (+2.97), positive and (+2.86), on that (+2.82), story (+2.68), discussing (+2.65), venus (+2.62) |
| Adequate | many advantages (+1.91), driving (+1.89), selves (+1.81), forget (+1.80), play sport (+1.78), mesa (+1.68), phones (+1.65), mission (+1.64) |
| Effective | of (+3.88), trash (+3.80), and (+3.27), students (+2.66), to (+2.61), does not (+2.49), community (+2.40), exploration (+2.39), safety (+2.35) |

# Appendix F. Alignment with the Assessment Criteria {.appendix}

Table F.1. Where each criterion of the report rubric is addressed.

| Criterion (points) | What the rubric asks | Where in this report |
|---|---|---|
| Question and scope (4) | User, decision, input/output, prediction time; measurable question; population limits | §1.2 (Table 1.1), §1.3, §8.5 item 8 |
| Understanding the data (8) | Source and use conditions, row unit and groups, labels, distributions, missingness, duplicates, sample trace, measurement limits | §3.1–3.8, Tables 3.1–3.7 |
| Methods and model selection (8) | Baseline, two families, features, loss, assumptions, selection, preprocessing fitted on training data | §4.1–4.4, §5.2 |
| Experiments and comparisons (6) | Same data, budget and metrics; configurations saved; controlled check; stability | §5.7, §6.1–6.3, §6.7, App. A |
| Error analysis and original work (6) | ≥ 10 cases by a stated rule; grouped errors; hypothesis tested on development data; decisions recorded | §7.2–7.4, Tables 7.4–7.6 |
| Reproducibility and evidence (4) | Commands, versions, seeds, splits, IDs, predictions, environment; contributions | App. B, App. C |
| Report quality and responsible use (4) | Problem → question → method → data → result → interpretation; sources support claims; limitations, permissions and AI use | Chapters 1–9, §3.1, §8.5, App. D |
