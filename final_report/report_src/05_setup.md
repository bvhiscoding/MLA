# Experimental Setup

## Splits and what each split is used for

Three disjoint sets of essays are used (Table 3.3). The training split (115,187 units, 12,475 essays) fits every model and every preprocessing step. The validation split (29,102 units, 3,119 essays) is used for all selection and for all error analysis. The official test (93,677 units, 10,402 essays) is a separate file released by the corpus authors; it was scored once with a locked configuration. The training/validation split is grouped by essay (`GroupShuffleSplit`, seed 42), so no essay contributes units to both sides. It is not grouped by prompt: all 15 prompts appear in both splits, as they do in the official test. The in-domain results therefore answer "how well does the model do on new essays written for known prompts".

## Information available at prediction time and where preprocessing is fitted

All model inputs are available once an essay has been submitted and segmented: the unit text, its discourse type, the other units and paragraphs of the same essay, the prompt name, and, for source-based prompts, the source text the students read. The holistic essay score is not used as an input because it is assigned by a rater after reading the whole essay; using it would leak a rater judgement into the prediction. The essay word count in FS-B is computed from the essay itself and is available. Demographic fields are not used.

Every fitted transformation is fitted on the training split only: the TF-IDF vocabulary and IDF weights, the one-hot encoder, the standard scaler, the class weights of the loss, and the neural network weights. In LOPO folds the same transformations are refitted on the 14 training prompts of each fold. The quartile cut points used to describe essay length (315, 422 and 566 words) were computed on validation units and then applied unchanged to the test; they are descriptive and do not enter any model.

## Leave-one-prompt-out folds

To measure transfer to unseen prompts, a LOPO fold trains on every annotated unit of 14 prompts and scores every unit of the remaining prompt. The Random Forest (FS-B) was run on all 15 folds. Because each DeBERTa fold costs about 40–45 GPU-minutes, DeBERTa L0 was run on three folds chosen from the Random Forest ranking: the hardest prompt ("A Cowboy Who Rode the Waves", rank 1 of 15), the median prompt ("Summer projects", rank 8) and the easiest prompt ("Distance learning", rank 15). The linear SVM was run on the same three folds. Each DeBERTa fold is trained for a fixed 3 epochs and the final model scores the held-out prompt once, so the held-out prompt plays no part in model or epoch selection.

LOPO results are kept separate from in-domain results throughout. A LOPO score on all units of a prompt and an in-domain score on the validation essays of that prompt describe different sets of units; the only direct comparison we report is on the same units, the validation essays of the held-out prompt, scored by the LOPO model and by the in-domain model (Section 6.4).

## Metrics

The primary metric is Macro-F1, the unweighted mean of the F1 scores of the three classes, because every class matters to the user and the classes are imbalanced. It is always reported together with per-class precision, recall and F1, so that a gain on the majority class cannot hide a loss on Ineffective. Accuracy, balanced accuracy (mean recall), Cohen's κ and quadratic weighted κ (QWK) are secondary. For an Ineffective flag used as a review queue, we also report the number of units flagged, newly caught and newly mis-flagged when the decision threshold changes.

Uncertainty is estimated with a paired, essay-level bootstrap: essays are resampled with replacement (2,000 resamples unless stated), both systems are scored on the same resample, and the 2.5th and 97.5th percentiles of the difference form a 95% confidence interval. Decisions are based on whether this two-sided interval excludes zero. This interval reflects sampling of essays only; it does not reflect variation between training runs, which we measure separately (Section 6.7).

## Use of the official test set

The official test file was used once, for the final comparison, under a protocol fixed beforehand (Figure 5.1 and Table 5.1). An early exploratory notebook had used half of the official test file as a development split for two linear baselines; none of those models or numbers is used anywhere in this report, and all selection reported here was made on the validation split.

![Figure 5.1. Use of the official test set. The red boxes mark the only contact with the test file.](figures/fig26_test_governance.png)

Table 5.1. Test protocol and its conditions.

| Element | Description |
|---|---|
| Systems scored | Protocol: Random Forest (FS-B), DeBERTa L0 and DeBERTa L1 (locked). Exploratory: Prompt-Aware. Supplementary: linear SVM |
| Fixed before scoring | Model, input format, hyperparameters, epoch-selection rule, argmax decision rule; L1 locked although L0 and L1 could not be distinguished on validation |
| DeBERTa scoring pass | L0, L1 and PA trained with the locked configuration, validation predictions logged, test scored once; the lock file `OFFICIAL_TEST_LOCK.json` records the test-file hash, model paths and configuration. Training, validation and test ran in one session, so validation results were logged but not reviewed by a person before the test pass |
| Random Forest scoring | The FS-B implementation was required to reproduce its validation result (0.5261, against 0.5230 originally) before the test was scored once |
| After the test pass | Context ladder, post-hoc class-offset correction, LOPO and threshold analyses: validation only, labelled exploratory, never scored on the test |

## Experiment matrix

Table 5.2 lists the experiments behind the main results. Each row records the question, the single change made, the configuration, split and seed, the metric, and the decision taken after inspecting it. Appendix A gives the complete run table with output locations.

Table 5.2. Main experiment matrix.

| # | Question | Change | Configuration / split / seed | Metric | Decision |
|---|---|---|---|---|---|
| E1 | Floor for any model | Always Adequate | Val, test | Macro-F1, per class | Floor 0.294 / 0.297 |
| E2 | Best classical model | LR, RF, SVM, LightGBM on FS-A / FS-B | Train → val, seed 42 | Macro-F1 | RF FS-B (0.523) is the classical protocol system |
| E3 | Is one transformer enough? | BERT + DeBERTa ensemble vs DeBERTa | Development split (14,303 units) | Macro-F1, paired CI | Ensemble +0.003 [−0.005, +0.011]; dropped |
| E4 | Transformer vs classical | DeBERTa L0 vs RF FS-B | Train → val, seed 42 | Macro-F1, paired CI | +0.054 [0.043, 0.065]; keep DeBERTa |
| E5 | What does local context add? (RQ2) | L0 → L1 input only | Same split, budget, seed | Macro-F1, per class, per type | Lock L1 (higher Ineff F1), state that L0 ≈ L1 |
| E6 | Final comparison | RF, L0, L1 (+ PA, SVM) | Locked config, test once | Macro-F1, per class, paired CI | Report; no further selection |
| E7 | Unseen prompts (RQ3) | Hold out one prompt | RF 15 folds; DeBERTa, SVM 3 folds; fixed 3 epochs | Macro-F1, same-unit gap | Report gap per prompt |
| E8 | Is length confounded with proficiency? (RQ4) | Stratify errors by score × length | L1 val (test descriptive) | Error rate, clustered OR | Keep both explanations (Section 7.2) |
| E9 | Threshold sensitivity | θ on P(Ineffective) | Val | Recall, precision, Macro-F1, flips | Argmax kept for evaluation; θ is a user choice |
| E10 | Wider context (RQ2, supp.) | L1 ±2, paragraph, L2, L3 | Same recipe, val only | Macro-F1, paired CI | Exploratory; no test scoring |

## Compute and reproducibility

Classical models were trained on a CPU workstation (scikit-learn 1.6.1 for the Random Forest). DeBERTa runs used a local RTX 4070 SUPER for the first L0/L1 runs and Google Colab for the rest: an A100 40 GB for the test-scored runs (training 63, 71 and 71 minutes for L0, L1 and PA; test inference 57 s, 91 s and 94 s) and L4 GPUs for the supplementary runs (about 40–45 minutes per LOPO fold). Every saved prediction file contains `row_idx`, `essay_id_comp`, the discourse type, the gold label, the predicted label and the three probabilities, so every number in Chapters 6 and 7 can be recomputed without a GPU by the scripts in `final_report/scripts/` (Appendix B).
