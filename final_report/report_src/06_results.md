# Results

All numbers in this chapter are recomputed from the saved per-unit prediction files by `final_report/scripts/02_results_from_predictions.py`, unless another source is named. Every table reports per-class results next to Macro-F1.

## Model families compared on the same validation units (RQ1)

Table 6.1 compares every family on the same 29,102 validation units from 3,119 essays. Figure 6.1(a) shows the per-class F1 scores.

Table 6.1. Validation results, same units for every system. P/R/F1 = precision / recall / F1. Logistic Regression is the reference refitted for this report (argmax decision); the other rows come from the saved predictions of the runs named.

| System | Macro-F1 | Accuracy | Balanced acc. | QWK | Ineffective P / R / F1 | Adequate F1 | Effective F1 |
|---|---:|---:|---:|---:|---|---:|---:|
| Majority (always Adequate) | 0.294 | 78.7% | 33.3% | 0.000 | 0 / 0 / 0 | 0.881 | 0.000 |
| Logistic Regression, FS-B | 0.489 | 62.7% | 61.3% | 0.349 | 0.159 / 0.576 / 0.249 | 0.732 | 0.486 |
| Random Forest, FS-B | 0.523 | 77.2% | 51.2% | 0.369 | 0.267 / 0.215 / 0.238 | 0.859 | 0.471 |
| DeBERTa-v3 L0, unit only | 0.572 | 72.9% | 62.4% | 0.433 | 0.335 / 0.428 / 0.376 | 0.816 | 0.526 |
| DeBERTa-v3 L1, ±1 unit (locked) | 0.581 | 74.2% | 62.8% | 0.445 | 0.337 / 0.447 / 0.385 | 0.827 | 0.532 |
| DeBERTa-v3 Prompt-Aware | 0.586 | 74.1% | 64.3% | 0.455 | 0.328 / 0.488 / 0.393 | 0.825 | 0.539 |

Three points stand out. First, the majority baseline has the highest accuracy and the highest Adequate F1 of all systems but a Macro-F1 of 0.294, so accuracy rewards ignoring the minority classes. Second, the two classical models make opposite trade-offs: the balanced Logistic Regression flags many units as Ineffective (recall 0.576, precision 0.159), while the Random Forest stays close to the majority class (Ineffective recall 0.215, accuracy 77.2%). Third, DeBERTa beats both classical models on Macro-F1 and on the two minority classes at once: its Ineffective F1 is 0.38–0.39 against 0.24–0.25. In an earlier run on the same validation units, DeBERTa L0 exceeded the Random Forest by +0.054 Macro-F1 (95% essay-bootstrap CI 0.043 to 0.065, 2,000 resamples). DeBERTa pays for this with lower Adequate F1 and accuracy, because the class-weighted loss moves Adequate units into the Effective and Ineffective classes.

![Figure 6.1. Per-class F1 and Macro-F1 of the main systems (a) on the 29,102 validation units and (b) on the 93,677 official test units.](figures/fig12_per_class_results_val_test.png)

## Level 0 versus Level 1 on the same units (RQ2)

Level 1 differs from Level 0 only in its input: it adds the preceding and the following unit of the same essay (Section 4.3.3). Both models were trained on the same 115,187 units with the same configuration and seed, and both are evaluated on the same validation units and the same test units. Table 6.2 and Figure 6.2 give the per-class differences with paired essay-bootstrap intervals.

Table 6.2. Level 1 minus Level 0 on the same units (models scored on the test; 2,000 essay-bootstrap resamples).

| Metric | Validation (29,102 units) | Official test (93,677 units) |
|---|---|---|
| Macro-F1 | +0.0087 [+0.0015, +0.0161] | +0.0159 [+0.0115, +0.0205] |
| F1 Ineffective | +0.0091 [−0.0097, +0.0278] | +0.0292 [+0.0185, +0.0408] |
| F1 Adequate | +0.0108 [+0.0074, +0.0145] | +0.0098 [+0.0080, +0.0117] |
| F1 Effective | +0.0061 [−0.0017, +0.0136] | +0.0087 [+0.0040, +0.0135] |

![Figure 6.2. Level 1 minus Level 0, per class, on the same validation and test units (95% essay-bootstrap CI).](figures/fig14_L1_minus_L0_per_class.png)

On the official test, Level 1 is better than Level 0 on every class, and the largest gain is on Ineffective (+0.029 F1). On validation the direction is the same but only the Macro-F1 and Adequate intervals exclude zero. A first training run of the same comparison gave +0.0022 Macro-F1 on validation with an interval containing zero ([−0.006, +0.011]), while its Ineffective F1 rose by +0.019. The two runs agree on direction but not on size, and the difference between them (0.0065) is of the same order as the effect (Section 6.7).

Table 6.3 shows what the extra context changes unit by unit. Context changes the predicted label of about 15% of units. Most changes move units between Adequate and Effective in both directions, and the gains only slightly outnumber the losses: on the test, 7,615 units become correct and 6,401 become wrong. For gold Ineffective units the balance is clearer: on the test, 519 are newly recognised and 335 are lost.

Table 6.3. Paired outcomes of Level 0 and Level 1 on the same units (table R4b).

| Outcome | Validation | Official test |
|---|---:|---:|
| Units | 29,102 | 93,677 |
| Same prediction | 24,490 | 79,453 |
| Prediction changed | 4,612 (15.8%) | 14,224 (15.2%) |
| Wrong under L0, correct under L1 | 2,452 | 7,615 |
| Correct under L0, wrong under L1 | 2,084 | 6,401 |
| Gold Ineffective newly recognised by L1 | 144 | 519 |
| Gold Ineffective recognised by L0 but missed by L1 | 118 | 335 |

Table 6.4 breaks the comparison down by discourse type. On the test, the gain is largest for the relational types whose definition refers to another unit: Counterclaim (+0.037 Macro-F1; Ineffective F1 0.201 → 0.281), Rebuttal (+0.028; 0.154 → 0.226) and Claim (+0.028; 0.237 → 0.292). It is smallest for Lead, Evidence and Position (+0.008). On validation, Position went the other way (−0.029), as it had in the first training run (Ineffective F1 −0.055). Validation subsets are small for rare types (34 Ineffective Rebuttals, 39 Ineffective Counterclaims), so per-type validation differences of this size can change sign between runs; the test subsets are about three times larger.

Table 6.4. Macro-F1 and Ineffective F1 of Level 0 and Level 1 by discourse type, same units (table R4a).

| Type | Val n (Ineff) | Val Macro-F1 L0 → L1 | Val Ineff F1 L0 → L1 | Test n (Ineff) | Test Macro-F1 L0 → L1 | Test Ineff F1 L0 → L1 |
|---|---|---|---|---|---|---|
| Lead | 1,902 (66) | 0.566 → 0.559 | 0.305 → 0.300 | 5,792 (304) | 0.583 → 0.590 | 0.322 → 0.344 |
| Position | 3,089 (100) | 0.559 → 0.530 | 0.358 → 0.279 | 10,250 (368) | 0.536 → 0.544 | 0.283 → 0.293 |
| Claim | 10,135 (317) | 0.509 → 0.528 | 0.280 → 0.302 | 32,375 (910) | 0.490 → 0.518 | 0.237 → 0.292 |
| Counterclaim | 1,148 (39) | 0.480 → 0.499 | 0.238 → 0.239 | 3,717 (114) | 0.476 → 0.513 | 0.201 → 0.281 |
| Rebuttal | 868 (34) | 0.513 → 0.515 | 0.326 → 0.292 | 2,880 (112) | 0.480 → 0.508 | 0.154 → 0.226 |
| Evidence | 9,249 (667) | 0.625 → 0.633 | 0.444 → 0.458 | 29,885 (1,956) | 0.615 → 0.622 | 0.401 → 0.419 |
| Concluding Statement | 2,711 (105) | 0.585 → 0.592 | 0.305 → 0.351 | 8,778 (461) | 0.597 → 0.609 | 0.355 → 0.391 |

The answer to the first part of RQ2 is therefore: neighbouring units add a small, consistent improvement, concentrated on the minority Ineffective class and on Claim, Counterclaim and Rebuttal units, whose quality is defined relative to an adjacent unit. The size of the improvement (about 0.01–0.02 Macro-F1) is comparable to run-to-run variation, so we do not state it more precisely than "small".

## Official test, one pass (RQ1)

Table 6.5 gives the results of the single scoring pass on the official test. The three protocol systems are the Random Forest (FS-B), DeBERTa L0 and the locked DeBERTa L1; Prompt-Aware and the linear SVM are labelled as extra systems.

Table 6.5. Official test results (93,677 units, 10,402 essays; one pass).

| System | Role | Macro-F1 | Accuracy | Balanced acc. | QWK | Ineffective P / R / F1 | Adequate F1 | Effective F1 |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Majority (always Adequate) | floor | 0.297 | 80.5% | 33.3% | 0.000 | 0 / 0 / 0 | 0.892 | 0.000 |
| Random Forest, FS-B | protocol | 0.510 | 78.5% | 49.8% | 0.350 | 0.246 / 0.172 / 0.202 | 0.870 | 0.457 |
| DeBERTa-v3 L0 | protocol | 0.561 | 74.4% | 60.9% | 0.422 | 0.311 / 0.372 / 0.339 | 0.831 | 0.514 |
| DeBERTa-v3 L1 | protocol, locked | 0.577 | 75.7% | 62.2% | 0.442 | 0.330 / 0.415 / 0.368 | 0.841 | 0.523 |
| DeBERTa-v3 Prompt-Aware | exploratory | 0.581 | 75.4% | 63.4% | 0.446 | 0.331 / 0.442 / 0.379 | 0.838 | 0.526 |
| Linear SVM, TF-IDF ¹ | supplementary | 0.482 | 74.4% | — | — | — / — / 0.204 | 0.844 | 0.398 |

¹ Trained on training + validation units (144,289); the same configuration trained on the 115,187 training units scores 0.485 on validation. The first, mis-specified RF test run (0.483) is not shown; see Table 5.1.

![Figure 6.3. Paired essay-bootstrap differences in Macro-F1 on the official test. Blue: interval above zero; grey: interval contains zero. Comparisons with RF use 1,000 resamples, the others 2,000.](figures/fig15_official_test_paired_bootstrap.png)

Validation and test agree closely (L1 0.581 vs 0.577; L0 0.572 vs 0.561; RF 0.526 vs 0.510 for the re-implemented FS-B), so no system was overfitted to validation in a way that collapsed on unseen essays. All three DeBERTa systems beat the Random Forest by 0.05–0.07 Macro-F1 with intervals far from zero (Figure 6.3); the gain comes from the minority classes (Ineffective F1 0.34–0.38 against 0.20; Effective F1 0.51–0.53 against 0.46), while the Random Forest keeps the highest accuracy and Adequate F1. Level 1 beats Level 0 (+0.016 [0.012, 0.021]). Prompt-Aware and Level 1 cannot be distinguished: the two-sided interval [−0.0002, +0.0074] contains zero, although the one-sided bootstrap proportion is 0.03; we base decisions on the two-sided interval.

![Figure 6.4. Confusion matrices on the official test (rows: gold label; cells: count and row percentage).](figures/fig13_confusion_matrices_test.png)

The confusion matrices (Figure 6.4) show the remaining problem. Even the locked system recognises only 41.5% of gold Ineffective units (1,755 of 4,225) and labels 2,358 of them Adequate; precision for Ineffective is 0.33, so two of every three Ineffective flags are wrong. Ineffective is almost never confused with Effective (112 and 33 units), which is consistent with an ordinal scale. Most errors lie between Adequate and Effective (11,953 + 4,799 units), the difficulty that dominates long essays (Section 7.2). Per discourse type, the locked system ranges from Macro-F1 0.508 (Rebuttal) to 0.622 (Evidence) on the test, and beats the Random Forest on every type (Appendix E, Table E.1).

## Prompt transfer: leave-one-prompt-out, kept separate from in-domain results (RQ3)

Figure 6.5 maps which prompts each system covers. In-domain systems (trained with all 15 prompts present) are evaluated over all prompts at once. LOPO systems are evaluated prompt by prompt: the Random Forest on all 15 prompts, the linear SVM and DeBERTa L0 on three. No LOPO number is averaged with, or placed in the same column as, an in-domain number.

![Figure 6.5. Prompt coverage of every system. Left: in-domain systems, which see every prompt in training. Right: leave-one-prompt-out Macro-F1 on all units of the held-out prompt.](figures/fig16_prompt_coverage_indomain_vs_lopo.png)

The Random Forest LOPO results (Figure 6.6) range from 0.350 ("A Cowboy Who Rode the Waves") to 0.501 ("Distance learning"), with a mean of 0.430 (standard deviation 0.041). Four of the five hardest prompts are source-based. These rankings selected the three prompts for the expensive DeBERTa folds.

![Figure 6.6. Random Forest (FS-B) leave-one-prompt-out Macro-F1 on each of the 15 held-out prompts. Blue bars mark the three prompts also run with DeBERTa.](figures/fig18_rf_lopo_15_prompts.png)

Table 6.6 compares the three families on the same LOPO folds, using all units of each held-out prompt. DeBERTa (fixed 3 epochs) scores highest on every prompt, but on "Summer projects" only narrowly (0.438 vs 0.434). Its Ineffective F1 stays low (0.11–0.24), and on "Summer projects", where only 0.9% of units are Ineffective, every family nearly fails on that class.

Table 6.6. Leave-one-prompt-out results on all units of the held-out prompt (Macro-F1 / Ineffective F1).

| Held-out prompt | Units / essays | Gold Ineff | Linear SVM | Random Forest | DeBERTa L0 |
|---|---|---:|---|---|---|
| A Cowboy Who Rode the Waves | 5,158 / 688 | 4.3% | 0.337 / 0.103 | 0.350 / 0.109 | 0.402 / 0.152 |
| Summer projects | 9,855 / 875 | 0.9% | 0.427 / 0.041 | 0.434 / 0.000 | 0.438 / 0.107 |
| Distance learning | 18,526 / 1,498 | 1.5% | 0.469 / 0.062 | 0.501 / 0.065 | 0.538 / 0.244 |

Table 6.6 compares families; it does not measure how much each family loses when a prompt is unseen, because the classical models have no in-domain score per prompt. Table 6.7 measures that loss for DeBERTa directly, on the same units: the validation essays of each held-out prompt, scored by the LOPO model and by the in-domain L0 model, which saw the prompt through other essays.

Table 6.7. DeBERTa L0, prompt unseen (LOPO) versus prompt seen (in-domain), on the same validation essays of the held-out prompt (gap with 2,000-resample essay-bootstrap CI; table R5).

| Held-out prompt | Units / essays | Setting | Macro-F1 | Ineff F1 | Adequate F1 | Effective F1 | Gap in Macro-F1 [95% CI] |
|---|---|---|---:|---:|---:|---:|---|
| A Cowboy Who Rode the Waves | 1,030 / 134 | in-domain | 0.476 | 0.235 | 0.882 | 0.309 | |
| | | LOPO | 0.384 | 0.135 | 0.777 | 0.240 | −0.092 [−0.132, −0.049] |
| Summer projects | 2,074 / 177 | in-domain | 0.508 | 0.231 | 0.714 | 0.578 | |
| | | LOPO | 0.483 | 0.250 | 0.639 | 0.560 | −0.025 [−0.052, +0.011] |
| Distance learning | 3,533 / 283 | in-domain | 0.576 | 0.275 | 0.800 | 0.652 | |
| | | LOPO | 0.528 | 0.210 | 0.754 | 0.620 | −0.048 [−0.078, −0.019] |

![Figure 6.7. DeBERTa L0 in-domain versus leave-one-prompt-out on the same validation essays of each held-out prompt.](figures/fig17_lopo_vs_indomain_same_units.png)

An unseen prompt costs DeBERTa Macro-F1 on two of the three prompts. The largest loss is on "A Cowboy Who Rode the Waves" (−0.092), a source-based narrative prompt whose essays refer to the people and events of one story; the loss is spread over all three classes. For "Summer projects" the interval includes zero, and its Ineffective F1 rests on 13 gold Ineffective units. With three prompts and one run per fold, the link between source-based prompts and larger losses is an interpretation, not a tested cause.

## Decision threshold for the Ineffective flag (sensitivity check)

The argmax rule is not the only way a teacher could use the model. A teacher who wants to see more of the weak units could flag every unit whose P(Ineffective) exceeds a threshold θ. Table 6.8 and Figure 6.8 show the trade-off for the locked L1 model on validation.

Table 6.8. Flagging units with P(Ineffective) ≥ θ, locked L1 model, validation (1,328 gold Ineffective units).

| Rule | Units flagged | Recall Ineff | Precision Ineff | F1 Ineff | Macro-F1 | Newly caught / new false alarms vs argmax | Ten cases flipped |
|---|---:|---:|---:|---:|---:|---|:---:|
| argmax | 1,761 | 44.7% | 33.7% | 0.385 | 0.581 | — | 0 |
| θ = 0.30 | 2,584 | 54.4% | 27.9% | 0.369 | 0.570 | 128 / 695 | 0 |
| θ = 0.20 | 3,253 | 60.0% | 24.5% | 0.348 | 0.558 | 203 / 1,289 | 0 |
| θ = 0.15 | 3,802 | 63.8% | 22.3% | 0.330 | 0.548 | 253 / 1,788 | 1 |
| θ = 0.10 | 4,633 | 69.6% | 19.9% | 0.310 | 0.535 | 330 / 2,542 | 3 |
| θ = 0.05 | 6,495 | 75.9% | 15.5% | 0.258 | 0.500 | 414 / 4,320 | 5 |

![Figure 6.8. Recall, precision and Macro-F1 for the Ineffective flag as the threshold on P(Ineffective) changes (locked L1, validation). Dotted lines: argmax rule.](figures/fig22_threshold_tradeoff.png)

Lowering θ from argmax to 0.10 raises Ineffective recall from 45% to 70%, but every additional correct flag costs about eight false alarms, and Macro-F1 falls monotonically. A threshold does not make the classifier better; it moves the operating point along a fixed trade-off. Whether a teacher prefers to read 4,633 flagged units to see 70% of the weak ones, or 1,761 to see 45%, is a product decision for the user, which we did not make on the test. Case 8 (P(Ineffective) = 0.058 under this model) is flagged only when θ ≤ 0.058.

## Pre-defined subgroup: ELL status

Following Baffour et al. (2023), we describe the locked model separately for essays whose writers are recorded as English language learners. ELL status is never an input. Table 6.9 gives the results.

Table 6.9. Locked L1 model by recorded ELL status (table R9).

| Split | ELL status | Units / essays | Gold Ineff / Eff | Macro-F1 | Ineff P / R / F1 | Effective F1 |
|---|---|---|---|---:|---|---:|
| Validation | No | 25,308 / 2,685 | 4.0% / 17.8% | 0.573 | 0.320 / 0.422 / 0.364 | 0.535 |
| Validation | Yes | 2,246 / 268 | 12.2% / 4.8% | 0.561 | 0.403 / 0.553 / 0.466 | 0.357 |
| Test | No | 81,288 / 8,984 | 4.1% / 16.1% | 0.571 | 0.321 / 0.386 / 0.351 | 0.528 |
| Test | Yes | 7,577 / 914 | 10.5% / 4.7% | 0.543 | 0.364 / 0.554 / 0.439 | 0.319 |

The model recognises Ineffective units better in ELL essays (test recall 55% vs 39%) and Effective units worse (F1 0.32 vs 0.53). Both differences track the very different class mix of the two groups (10.5% vs 4.1% Ineffective; 4.7% vs 16.1% Effective), so they cannot be read as bias or its absence without conditioning on the label and proficiency. We report them as a description; a fairness audit would need the rater-level data and a pre-registered criterion, and we do not recommend any group-specific threshold.

## Stability and calibration

Two sources of uncertainty are not captured by the bootstrap intervals. The first is training randomness. The same L0 and L1 configurations trained twice gave validation Macro-F1 0.5768 and 0.5723 for L0 (−0.0045) and 0.5790 and 0.5809 for L1 (+0.0019), so the L1 − L0 gap moved from +0.0022 to +0.0087. Two supplementary configurations trained twice with the same seed differed by 0.0025 (L2) and 0.0039 (L1 ±2). Differences between DeBERTa variants below about 0.005–0.01 Macro-F1 should therefore not be interpreted as model differences. With one seed per configuration (GPU budget), we did not run the three seeds the course suggests; this is a limitation (Section 8.5).

The second is calibration. The class-weighted loss shifts probabilities towards the minority classes: the locked L1 model predicts Ineffective for 6.1% of validation units, against 4.6% gold. In an earlier check, temperature scaling fitted on 20% of validation (T = 1.124) did not improve the expected calibration error measured on the other 80% (0.0153 before, 0.0166 after), and that aggregate measure is dominated by the Adequate class. The probabilities are therefore used for ranking and thresholds, not as calibrated risks.

## Beyond Level 1: wider context (RQ2, supplementary, validation only)

After the official test pass we trained four further inputs with the Level 1 recipe (Table 4.2). They were never scored on the test and their epochs were chosen on validation, so they are explorations. Table 6.10 and Figure 6.9 give the results.

Table 6.10. Context ladder on validation (29,102 units). Δ vs L1 with paired essay-bootstrap CI (2,000 resamples).

| Input | Macro-F1 | Δ vs L1 [95% CI] | Ineff P / R / F1 | Effective F1 | Accuracy | Units flagged Ineffective |
|---|---:|---|---|---:|---:|---:|
| L0, unit only | 0.572 | −0.009 [−0.016, −0.001] | 0.335 / 0.428 / 0.376 | 0.526 | 72.9% | 5.8% |
| L1, ±1 unit (locked) | 0.581 | — | 0.337 / 0.447 / 0.385 | 0.532 | 74.2% | 6.1% |
| Prompt-Aware | 0.586 | +0.005 [−0.002, +0.011] | 0.328 / 0.488 / 0.393 | 0.539 | 74.1% | 6.8% |
| L1 ±2 units | 0.587 | +0.006 [−0.001, +0.013] | 0.332 / 0.498 / 0.398 | 0.536 | 74.1% | 6.8% |
| Paragraph | 0.569 | −0.012 [−0.020, −0.005] | 0.296 / 0.566 / 0.388 | 0.525 | 70.4% | 8.7% |
| L2, source passage | 0.579 | −0.002 [−0.010, +0.005] | 0.289 / 0.544 / 0.378 | 0.541 | 73.1% | 8.6% |
| L3, whole essay, 3 epochs | 0.576 | −0.005 [−0.014, +0.003] | 0.313 / 0.587 / 0.408 | 0.531 | 70.3% | 8.6% |
| L3, whole essay, 7 epochs | 0.570 | −0.011 [−0.020, −0.002] | 0.350 / 0.430 / 0.386 | 0.508 | 72.7% | 5.6% |

![Figure 6.9. Context ladder on validation: Macro-F1 difference from L1 (a) with the argmax decision and (b) after the same cross-fitted class-offset correction for every model.](figures/fig19_context_ladder_validation.png)

Under the argmax rule, no input beyond Level 1 is clearly better on Macro-F1. The wider inputs (paragraph, source passage, whole essay) shift the models towards Ineffective: recall rises to 54–59% and Ineffective F1 to 0.38–0.41, but precision and accuracy fall. Because every model was trained with the same class weights, argmax Macro-F1 mixes two properties: how well a model separates the classes and how its probabilities are shifted. To separate them we applied the same correction to every model: offsets added to the log-probabilities of Ineffective and Effective, chosen to maximise Macro-F1 on one half of the validation essays and applied to the other half, then swapped. After this correction (Figure 6.9b), the 3-epoch whole-essay model exceeds L1 by +0.025 [0.016, 0.035] (Macro-F1 0.619; Ineffective F1 0.434 vs 0.382), and an average of L1, L1 ±2 and L3 reaches 0.623. The paragraph and source inputs gain nothing.

This is the first result in the project that supports the hypothesis that whole-essay information helps to judge a unit, but three cautions apply: it is post-hoc and on validation, which also chose each model's epoch; it rests on one of the two L3 runs, the 7-epoch run having overfitted (training loss fell from 0.88 to 0.27 while validation Macro-F1 oscillated between 0.55 and 0.57); and no L3 model has been scored on the test. For Level 2, the 11 prompts without a source text received exactly the L1 input and serve as a control for run-to-run change: the difference-in-differences estimate of the source effect is −0.014 [−0.029, +0.002]. With crude retrieval, summaries instead of full texts for two prompts and no text for three, this shows that adding a retrieved passage this way did not help; it does not show that sources are irrelevant.
