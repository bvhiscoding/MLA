---
title: "Predicting the Effectiveness of Argumentative Discourse Units in Student Essays"
version: "Main paper (6–8 pages). Full details: Supplementary Report (Group06_CLC02_Final_Report.pdf)"
---

::: titlepage
HANOI UNIVERSITY
FACULTY OF INFORMATION TECHNOLOGY

MACHINE LEARNING APPLICATIONS (61FIT4MLA / 62FIT4MLA)
FINAL PROJECT REPORT

PREDICTING THE EFFECTIVENESS OF ARGUMENTATIVE DISCOURSE UNITS IN STUDENT ESSAYS

Classical and transformer models, controlled context ablation, prompt transfer and error analysis on PERSUADE 2.0

Main paper. Full details are given in the Supplementary Report (Group06_CLC02_Final_Report.pdf).

Class: CLC02 · Group 06
Lecturer: Bùi Quốc Khánh

Group members (see Appendix C):
[Full name 1 – Student ID]
[Full name 2 – Student ID]
[Full name 3 – Student ID]

Hanoi, November 2026
:::

::: pagebreak
:::

# Abstract {.unnumbered}

Teachers need to know which parts of a student's argumentative essay are weak, not only the overall grade. We ask how well a model can predict the rater-assigned effectiveness (Ineffective, Adequate, Effective) of each discourse unit of an already segmented essay, and what information the model needs. We use PERSUADE 2.0 (237,966 annotated units, 25,996 essays by U.S. students in grades 6–12, 15 prompts; 4.5% Ineffective). The training file was split by essay into 115,187 training and 29,102 validation units; the official test (93,677 units) was scored once with a locked configuration. On the same units, a fine-tuned DeBERTa-v3-base reached test Macro-F1 0.577 (F1 Ineffective 0.368), against 0.510 for a Random Forest and 0.297 for the majority baseline. Adding the neighbouring units to the input (Level 1) improved Macro-F1 by 0.016 [0.012, 0.021], mostly on Ineffective units, an effect of the same order as run-to-run variation. A model that never saw the prompt lost 0.048–0.092 Macro-F1 on two of three held-out prompts. Essay length is strongly associated with proficiency and class mix; within the same holistic score, errors still rise with length. Labels are only moderately reliable (rater–rater κ = 0.316), so the model is suitable at most for ordering a teacher's review.

# Introduction

The user is a teacher of English argumentative writing who must decide which discourse units of submitted essays to read and comment on first. The input is one annotated unit (Lead, Position, Claim, Counterclaim, Rebuttal, Evidence or Concluding Statement), its type and, for context variants, other text of the same essay. The output is a probability for each effectiveness class and a label under an argmax rule or a teacher-chosen threshold. The prediction is made after an essay has been submitted and segmented; holistic scores and demographic fields are never inputs. The tool supports the teacher and never grades students.

We address one main question: how well can a model predict rater-assigned unit effectiveness on new essays from the same population, compared with simple and classical baselines, when every class matters? Four sub-questions follow. RQ1: does a fine-tuned transformer beat a majority baseline and classical models on the same units, per class? RQ2: holding model, split and budget fixed, what does adding the neighbouring units (Level 1) add to the unit alone (Level 0), and do wider inputs help? RQ3: how much is lost on a prompt never seen in training? RQ4: are errors associated with essay length, and is that association explained by proficiency and class mix before any error is attributed to missing context?

# Related Work

PERSUADE 2.0 (Crossley et al., 2024) adds holistic scores and unit-level effectiveness ratings to the discourse annotations of PERSUADE 1.0. Raters agreed on effectiveness only at κ = 0.316 (0.165 for Claim to 0.432 for Evidence), and the winning Feedback Prize models were least accurate on Ineffective units, which they mostly predicted as Adequate. Baffour et al. (2023) found moderate demographic bias in those models. Ding et al. (2023) showed that adding the argument type, the prompt and the whole essay to BERT raised QWK from 0.42 to 0.46–0.47 on the Kaggle subset; Schaller et al. (2025) found that context-dependent argument-mining models degrade when context is limited. Argument quality is subjective (Wachsmuth et al., 2017; Romberg et al., 2025), which limits any agreement a model can reach.

# Data and Method

## Data, units and labels

PERSUADE 2.0 is released under CC BY-NC-SA 4.0; our use is non-commercial and the data are not redistributed. The unit of observation is one annotated discourse unit. Its label follows the corpus rubric and is relational: a Claim is judged against the Position, a Rebuttal against the Counterclaim, Evidence against the Claim it supports. Effective means the unit fulfils its function well, Adequate sufficiently, Ineffective not; we map them to 0 = Ineffective, 1 = Adequate, 2 = Effective. Keeping records with a label and non-empty text gives 144,289 units from 15,594 essays in the training file and 93,677 units from 10,402 essays in the test file. Labels are imbalanced in every split (test: 4.5% / 80.5% / 15.0%). Units of one essay are not independent, so all splits and intervals operate at the essay level.

Seven scripted checks (Supplementary Report, Section 3.5) verify the data. The file hashes match those logged by the training and test runs, and the label and type vocabularies are exact. The numeric `discourse_id` had been rounded by a spreadsheet program to 728 distinct values, so it is never used as a join key; every join uses `row_idx` (position after filtering) or the intact `essay_id_comp`. All 17 saved prediction files agree with the raw data row by row on essay, type and gold label, and six raw records were traced from the CSV to the prediction file. One of them, validation unit `row_idx` 108613 (essay FE3141FA4163, prompt "Cell phones at school", holistic score 2), is the Claim "Some kids will ask there parents to transfer school", gold Ineffective. Its Level 0 input is `Claim [SEP] <unit>`; its Level 1 input adds the previous and next units. All models predict Adequate (DeBERTa P(Ineffective) = 0.017 for L0 and 0.058 for L1).

## Models

The majority baseline always predicts Adequate. The classical family uses Feature Set B: word unigram and bigram TF-IDF (15,000 features), a discourse-type one-hot encoding and five standardised structural features (unit length, essay length, relative position, length ratio), all fitted on training units only. Logistic Regression with balanced class weights is the interpretable reference: its largest weights for Ineffective are topic words of particular prompts ("aliens", "venus"), which shows that a lexical model partly learns prompt priors. The Random Forest (Breiman, 2001; 200 trees, depth 35, balanced class weights) was the strongest classical model on validation and is the classical system in the test protocol.

The transformer family fine-tunes DeBERTa-v3-base (He et al., 2023) with a linear head and class-weighted cross-entropy,

$$\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\,\log p_\theta(y_i \mid x_i), \qquad w_k = \frac{N}{3\,N_k},$$

which gives weights 7.48 / 0.43 / 1.95 for Ineffective / Adequate / Effective. Training uses a maximum of 512 tokens, an effective batch of 32, learning rate 2 × 10⁻⁵ with 10% warm-up, 3 epochs, seed 42, and the epoch with the best validation Macro-F1. Only the input changes between context levels. Level 0 is `type [SEP] unit`. Level 1 adds the preceding and following units of the same essay, so the model can see whether an adjacent claim has support or an adjacent counterclaim an answer, but nothing further away. Prompt-Aware prefixes the prompt name to the Level 1 input. Supplementary validation-only runs add two units on each side, the paragraph, a retrieved source passage (Level 2) or the whole essay (Level 3).

# Experimental Setup

The training file was split with scikit-learn's `GroupShuffleSplit` (Pedregosa et al., 2011) by essay (80/20, seed 42); all 15 prompts occur in both parts, so in-domain results concern new essays on known prompts. Unseen prompts are tested by leave-one-prompt-out (LOPO): train on 14 prompts, score every unit of the 15th. The Random Forest covers all 15 prompts; DeBERTa L0 and a linear SVM cover three prompts chosen from the Random Forest ranking (hardest, median, easiest). DeBERTa LOPO folds train for a fixed 3 epochs, and the held-out prompt plays no part in selection. LOPO results are reported separately from in-domain results, and the only direct comparison is on the same units.

Macro-F1 is the primary metric, always reported with per-class F1; QWK and accuracy are secondary. Uncertainty is a paired essay-level bootstrap (Efron & Tibshirani, 1993; 2,000 resamples) of the difference between two systems on the same units. All selection used validation. The test protocol (Random Forest, DeBERTa L0 and the locked L1, plus exploratory Prompt-Aware and a supplementary SVM) was fixed in advance and scored once; a lock file records the test-file hash and configuration. The Random Forest had to reproduce its validation result before its single test scoring. Training, validation and test ran in one session, so validation results were logged but not reviewed by a person before the test pass. An early exploratory notebook had used half of the test file for two linear baselines; none of those results is used. Scripts, seeds, split files and per-unit predictions are listed in Appendix B.

# Results

## Model families on the same units (RQ1)

Table 1 compares all systems on the same validation and test units. The majority baseline has the highest accuracy and a Macro-F1 below 0.30, so accuracy is not informative here. DeBERTa beats both classical models on Macro-F1 and on both minority classes; the Random Forest keeps the highest accuracy and Adequate F1 because it rarely leaves the majority class. On the test, DeBERTa L1 exceeds the Random Forest by +0.068 [0.061, 0.075]. The locked system still recognises only 41.5% of gold Ineffective test units, and two of three Ineffective flags are wrong.

Table 1. Per-class results on the same units (validation: 29,102 units, 3,119 essays; official test: 93,677 units, 10,402 essays; test scored once).

| Split | System | Macro-F1 | F1 Ineff | Recall Ineff | F1 Adeq | F1 Eff | Accuracy |
|---|---|---:|---:|---:|---:|---:|---:|
| Val | Majority (Adequate) | 0.294 | 0.000 | 0.0% | 0.881 | 0.000 | 78.7% |
| Val | Logistic Regression, FS-B | 0.489 | 0.249 | 57.6% | 0.732 | 0.486 | 62.7% |
| Val | Random Forest, FS-B | 0.523 | 0.238 | 21.5% | 0.859 | 0.471 | 77.2% |
| Val | DeBERTa L0 | 0.572 | 0.376 | 42.8% | 0.816 | 0.526 | 72.9% |
| Val | DeBERTa L1 (locked) | 0.581 | 0.385 | 44.7% | 0.827 | 0.532 | 74.2% |
| Test | Majority (Adequate) | 0.297 | 0.000 | 0.0% | 0.892 | 0.000 | 80.5% |
| Test | Random Forest, FS-B | 0.510 | 0.202 | 17.2% | 0.870 | 0.457 | 78.5% |
| Test | DeBERTa L0 | 0.561 | 0.339 | 37.2% | 0.831 | 0.514 | 74.4% |
| Test | DeBERTa L1 (locked) | 0.577 | 0.368 | 41.5% | 0.841 | 0.523 | 75.7% |
| Test | DeBERTa Prompt-Aware ¹ | 0.581 | 0.379 | 44.2% | 0.838 | 0.526 | 75.4% |

¹ Exploratory; not distinguishable from L1 (+0.004 [−0.0002, +0.007]). A supplementary linear SVM scored 0.482 on the test.

![Figure 1. Per-class F1 and Macro-F1 (a) on validation and (b) on the official test.](figures/fig12_per_class_results_val_test.png)

## Level 0 versus Level 1 on the same units (RQ2)

Table 2 compares Level 0 and Level 1, trained identically and scored on exactly the same units. On the test, Level 1 is better on every class, most on Ineffective (+0.029 F1). The gain is largest for relational types (Counterclaim +0.037, Rebuttal +0.028, Claim +0.028 Macro-F1) and smallest for Lead, Evidence and Position. A first training run of the same comparison gave only +0.002 on validation, so the effect is of the order of run-to-run variation. Wider inputs did not raise Macro-F1 under the argmax rule; after the same cross-fitted class-offset correction for every model, the 3-epoch whole-essay model exceeded Level 1 by +0.025 [0.016, 0.035] on validation, but this is post-hoc, from one of two runs, and was never scored on the test.

Table 2. Level 1 minus Level 0 on the same units (95% paired essay-bootstrap CI, 2,000 resamples).

| Metric | Validation (29,102 units) | Official test (93,677 units) |
|---|---|---|
| Macro-F1 | +0.0087 [+0.0015, +0.0161] | +0.0159 [+0.0115, +0.0205] |
| F1 Ineffective | +0.0091 [−0.0097, +0.0278] | +0.0292 [+0.0185, +0.0408] |
| F1 Adequate | +0.0108 [+0.0074, +0.0145] | +0.0098 [+0.0080, +0.0117] |
| F1 Effective | +0.0061 [−0.0017, +0.0136] | +0.0087 [+0.0040, +0.0135] |
| Units whose prediction changes | 4,612 (15.8%) | 14,224 (15.2%) |
| Gold Ineffective gained / lost by L1 | 144 / 118 | 519 / 335 |

## Unseen prompts (RQ3)

Table 3 keeps LOPO separate from in-domain results. On all units of each held-out prompt, DeBERTa scores highest of the three families, but only narrowly on "Summer projects". On the same validation essays of each held-out prompt, the LOPO model loses against the in-domain model on two of three prompts; the largest loss is on the source-based narrative prompt "A Cowboy Who Rode the Waves". With three prompts and one run per fold, the link to source-based prompts is an interpretation, not a tested cause. Across all 15 Random Forest folds, LOPO Macro-F1 ranges from 0.350 to 0.501 (mean 0.430).

Table 3. Leave-one-prompt-out results. Left: Macro-F1 on all units of the held-out prompt. Right: DeBERTa L0 on the same validation essays of that prompt, prompt unseen (LOPO) versus seen (in-domain).

| Held-out prompt | SVM | RF | DeBERTa | Units / essays (same set) | LOPO | In-domain | Gap [95% CI] |
|---|---:|---:|---:|---|---:|---:|---|
| A Cowboy Who Rode the Waves | 0.337 | 0.350 | 0.402 | 1,030 / 134 | 0.384 | 0.476 | −0.092 [−0.132, −0.049] |
| Summer projects | 0.427 | 0.434 | 0.438 | 2,074 / 177 | 0.483 | 0.508 | −0.025 [−0.052, +0.011] |
| Distance learning | 0.469 | 0.501 | 0.538 | 3,533 / 283 | 0.528 | 0.576 | −0.048 [−0.078, −0.019] |

# Error Analysis

Before attributing errors to missing context, we checked whether errors follow essay length, proficiency and class mix (RQ4). Essay length and holistic score correlate strongly (Spearman 0.76, 25,996 essays), and the class mix shifts with both: across length quartiles the Ineffective share falls from 8.7% to 1.4% and the Effective share rises from 5.4% to 34.5%. Table 4 shows the consequence for the locked model. The error rate rises from 22.0% to 30.5%, and in the longest quartile 92% of errors are Adequate↔Effective confusions, yet Macro-F1 stays nearly flat (0.53–0.55): the rising error rate largely reflects the changing class mix. Within the same holistic score, however, errors still rise with length (score 3: 19.3% to 28.2%; score 4: 19.6% to 31.1%). A logistic regression with essay-clustered errors gives an odds ratio of 1.19 [1.14, 1.25] per length quartile after controlling for score, and 1.17 [1.11, 1.23] after also controlling for gold label and discourse type. Proficiency explains the type of error, not the whole rise; a residual length effect remains, with an untested mechanism.

Table 4. Locked L1 errors by essay-length quartile, validation. Share A↔E: share of errors that are Adequate↔Effective confusions; score-3 and score-4 columns: error rate within that holistic score.

| Quartile (words) | Gold Ineff / Eff | Error rate | Share A↔E | Macro-F1 | Error, score 3 | Error, score 4 |
|---|---|---:|---:|---:|---:|---:|
| Q1 (≤315) | 9.0% / 5.3% | 22.0% | 47.5% | 0.532 | 19.3% | 19.6% |
| Q2 (316–422) | 5.0% / 10.7% | 23.0% | 67.1% | 0.551 | 21.8% | 22.0% |
| Q3 (423–566) | 2.9% / 18.3% | 27.9% | 83.8% | 0.552 | 22.9% | 28.5% |
| Q4 (≥567) | 1.3% / 32.8% | 30.5% | 92.0% | 0.526 | 28.2% | 31.1% |

![Figure 2. Locked L1 error rate by essay-length quartile within the same holistic score (95% essay-bootstrap CI).](figures/fig20_error_within_score_by_length.png)

We then read ten failure cases selected by a fixed rule: the gold-Ineffective validation units that DeBERTa L0 misclassified with the highest confidence (predicted-class probability above 0.94). Appendix E lists their IDs, texts and probabilities. By the information a rater would need, four can be judged from the unit itself (cases 2, 3, 4, 10), one needs local context (8), two the whole essay (1, 6: counterclaims never answered) and three the prompt or source (5, 7, 9). Under Level 1 none of the ten changes its prediction; the paragraph, source and whole-essay inputs flip case 2, and only the 3-epoch whole-essay model flips cases 1 and 5. Lowering Level 1's threshold to the same flag rate flips none, so these flips are not only a threshold shift. As a decision-threshold check, flagging units with P(Ineffective) ≥ 0.10 raises Ineffective recall from 45% to 70% on validation, but adds about eight false alarms per extra unit caught and lowers Macro-F1 from 0.581 to 0.535; the threshold is a choice for the teacher, not a model improvement.

# Discussion and Conclusion

The results answer RQ1 clearly: on the same units, the transformer beats the classical models and the baseline on Macro-F1 and on both minority classes. For RQ2, neighbouring units help a little and consistently, most for relational units; wider context is promising only after calibration correction, which is not yet a test-set finding. For RQ3, an unseen prompt costs up to 0.09 Macro-F1. For RQ4, length is entangled with proficiency and class mix, and a residual length effect remains. The results do not show that the model understands argument quality, how large the prompt-transfer loss is for the other twelve prompts, or whether source texts help.

As in Crossley et al. (2024), Ineffective units are hardest (2,358 of 2,470 missed Ineffective test units are labelled Adequate). As in Ding et al. (2023), context and prompt help: validation QWK rises from 0.433 (L0) to 0.445 (L1) and 0.455 (Prompt-Aware).

Model–rater and rater–rater agreement answer different questions. Rater–rater κ (0.316, computed by Crossley et al. on segments two raters both marked, before adjudication, weighted) measures how reliable the label is. Model κ against the adjudicated label (0.372 for L1 on the test, unweighted, on gold units) measures how well the model reproduces the consensus label it was trained on. Because they compare different things on different data, a model κ above 0.316 does not mean the model is better than a rater; the low rater κ means that part of the "model error" is disagreement in the labels themselves.

Limitations are label reliability, gold segmentation, one run per configuration, transformer LOPO on three prompts, validation-only explorations, and a population of U.S. grade 6–12 essays on 15 prompts. The model should only order a teacher's reading on familiar prompts, never grade students.

# References {.unnumbered}

Baffour, P., Saxberg, T., & Crossley, S. A. (2023). Analyzing bias in large language model solutions for assisted writing feedback tools: Lessons from the Feedback Prize competition series. In Proceedings of the 18th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2023) (pp. 242–246).

Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.

Crossley, S. A., Tian, Y., Baffour, P., Franklin, A., Benner, M., & Boser, U. (2024). A large-scale corpus for assessing written argumentation: PERSUADE 2.0. Assessing Writing, 61, Article 100865. https://doi.org/10.1016/j.asw.2024.100865

Ding, Y., Bexte, M., & Horbach, A. (2023). Score it all together: A multi-task learning study on automatic scoring of argumentative essays. In Findings of the Association for Computational Linguistics: ACL 2023 (pp. 13052–13063).

Efron, B., & Tibshirani, R. J. (1993). An introduction to the bootstrap. Chapman & Hall/CRC.

He, P., Gao, J., & Chen, W. (2023). DeBERTaV3: Improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing. In International Conference on Learning Representations (ICLR 2023).

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.

Romberg, J., Maurer, M., Wachsmuth, H., & Lapesa, G. (2025). Towards a perspectivist turn in argument quality assessment. In Proceedings of NAACL 2025 (Volume 1: Long Papers) (pp. 7458–7485).

Schaller, N.-J., Ding, Y., Jansen, T., & Horbach, A. (2025). Don't score too early! Evaluating argument mining models on incomplete essays. In Proceedings of the 20th Workshop on Innovative Use of NLP for Building Educational Applications (BEA 2025) (pp. 345–355).

Wachsmuth, H., Naderi, N., Hou, Y., Bilu, Y., Prabhakaran, V., Alberdingk Thijm, T., Hirst, G., & Stein, B. (2017). Computational argumentation quality assessment in natural language. In Proceedings of EACL 2017, Volume 1 (pp. 176–187).

# Appendix A. Run Table {.appendix}

Every number above comes from the runs below; the full run table with output locations is Appendix A of the Supplementary Report.

Table A.1. Runs behind the reported numbers.

| Run | Model and input | Evaluated on | Configuration | Status |
|---|---|---|---|---|
| R02 | LR, RF and other classical models on FS-B | Validation | Seed 42, scikit-learn 1.6.1 | Used (RF = classical system) |
| R04 | DeBERTa L0 and L1, first run | Validation | Section 3.2 | Run-to-run comparison, ten cases |
| R05 | RF FS-B, 15 LOPO folds | Held-out prompts | 150 trees, depth 35 | Used |
| R06 | DeBERTa L0, L1, Prompt-Aware | Validation; test once | Section 3.2, A100, bf16 | Used (lock file) |
| R07 | RF FS-B | Validation gate, then test once | 200 trees, depth 35 | Used |
| R08–R09 | Linear SVM, test and 3 LOPO folds | Test; held-out prompts | TF-IDF | Supplementary |
| R10 | DeBERTa L0, 3 LOPO folds | Held-out prompts, once | Fixed 3 epochs | Used |
| R11–R12 | Wider context levels; class-offset correction | Validation only | Level 1 recipe | Exploratory |
| R13 | LR FS-B interpretable reference | Validation | C = 1, balanced | Used |

# Appendix B. Reproduction {.appendix}

Download the PERSUADE 2.0 CSV files from the corpus repository (github.com/scrosseye/persuade_corpus_2.0) into `data/persuade_raw/`. The scripts in `final_report/scripts/` recompute every table and figure from the raw data and the saved per-unit predictions without a GPU (Supplementary Report, Appendix B). The split is stored in `final_report/tables/split_essays.csv` (keyed by `essay_id_comp`) and `final_report/tables/split_units.csv.gz` (keyed by `row_idx`); all runs use seed 42. Every prediction file stores `row_idx`, `essay_id_comp`, discourse type, gold label, prediction and the three probabilities.

```
python final_report/scripts/01_data_checks_eda.py
python final_report/scripts/02_results_from_predictions.py
python final_report/scripts/07_export_split_ids.py
```

# Appendix C. Individual Contributions {.appendix}

Roles and the work of each role per week are listed with evidence in the Supplementary Report, Appendix C. Members fill in their names: Role 1 (data and classical models) [name]; Role 2 (transformer and context) [name]; Role 3 (error analysis, LOPO and test governance) [name].

# Appendix D. Use of AI Tools {.appendix}

AI assistants (Claude Code, OpenAI Codex, Gemini) were used for running cloud jobs, writing and debugging scripts and notebooks, auditing code and drafting text; none is part of the studied pipeline. Every number was recomputed from data or saved predictions by scripts in the repository, and explanations that could not be verified against data were not used. Members complete their own entries in the Supplementary Report, Appendix D.

# Appendix E. Ten Failure Cases {.appendix}

Table E.1. The ten gold-Ineffective failure cases (validation). P = P(Ineffective) under L0 / the first L1 run / the locked L1; every model predicts Adequate except for case 2 (Effective).

| Case | row_idx | Type | Unit (start) | P (L0 / L1 / L1 locked) | Information needed |
|:---:|---:|---|---|---|---|
| 1 | 2467 | Counterclaim | "There are many reason on why texting while driving is very useful" | 0.022 / 0.029 / 0.027 | Whole essay |
| 2 | 10303 | Evidence | "To provide reasonings to my strong point, brings me back to paragraph 36. …" | 0.000 / 0.001 / 0.008 | Unit itself |
| 3 | 25520 | Position | "I think you shouldn't join the Seagoing Cowboys" | 0.022 / 0.010 / 0.006 | Unit itself |
| 4 | 105080 | Counterclaim | "Not allowing students to use there phones at all" | 0.038 / 0.090 / 0.170 | Unit itself |
| 5 | 86267 | Position | "The Driverless people can cause problems." | 0.028 / 0.151 / 0.103 | Source / task |
| 6 | 114270 | Counterclaim | "But Sometimes it could be a distraction from you doing all your work." | 0.031 / 0.040 / 0.035 | Whole essay |
| 7 | 110025 | Position | "I reconsider that are principal should let us eight graders bring are cell phones …" | 0.035 / 0.097 / 0.052 | Prompt / task |
| 8 | 108613 | Claim | "Some kids will ask there parents to transfer school" | 0.021 / 0.124 / 0.058 | Local context |
| 9 | 83105 | Lead | "The future is near and the talk about driverless cars is upon us" | 0.045 / 0.080 / 0.143 | Prompt / task |
| 10 | 9735 | Claim | "Another cars is a bad idea is because of its gas." | 0.039 / 0.032 / 0.039 | Unit itself |
