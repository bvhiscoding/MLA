# Discussion

## What the results answer and what they do not

RQ1, model families. On the same units and metrics, the fine-tuned transformer is clearly better than the classical models and the trivial baseline on Macro-F1 and on both minority classes (official test: 0.577 vs 0.510 for the Random Forest and 0.297 for the majority baseline; Ineffective F1 0.368 vs 0.202). The classical models keep higher accuracy only because they predict the majority class more often. What the results do not show is that the transformer understands argument quality: it recognises fewer than half of the Ineffective units, and two of every three Ineffective flags are wrong.

RQ2, context. Adding the neighbouring units gives a small improvement that is consistent in direction across two training runs, the validation set and the test, and is largest for Ineffective units and for Claim, Counterclaim and Rebuttal. Its size is of the order of run-to-run variation, so the evidence supports "local context helps a little" and not a precise effect. Wider inputs did not improve Macro-F1 under the argmax rule; after an identical calibration correction for every model, one whole-essay run separated the classes better than Level 1 (+0.025). This is the strongest evidence in the project for the hypothesis that a unit's effectiveness depends on the whole essay, but it is post-hoc, validation-only and from one of two runs. The results do not answer whether source texts help, because the source material and retrieval were too limited.

RQ3, unseen prompts. A transformer that never saw the prompt lost 0.048 to 0.092 Macro-F1 on two of three prompts, measured on the same units as an in-domain model. The results do not say how large the loss is for the other twelve prompts, nor why the source-based "Cowboy" prompt lost most.

RQ4, errors. Essay length is strongly associated with proficiency and with the class mix, and that association explains why the kind of error changes with length and why Macro-F1 stays flat across length quartiles. Within the same holistic score and gold label, longer essays still have more errors. The analysis therefore supports both a class-mix explanation and a residual length effect, and it shows that neither should be reported as "lost context" without this check.

## Comparison with the sources read

Our findings agree with the corpus paper (Crossley et al., 2024) that Ineffective units are the hardest and are mostly predicted as Adequate: 2,358 of the 2,470 Ineffective units the locked model misses are labelled Adequate. They agree in direction with Ding et al. (2023), who found that the argument type, the prompt and the whole essay each raised QWK for BERT (0.42 → 0.46 with the prompt, 0.47 with the whole essay). Our corresponding validation QWK values are 0.433 for L0, 0.445 for L1, 0.455 for Prompt-Aware and 0.447 for the 3-epoch whole-essay model; the prompt effect is of similar size, but our whole-essay effect is smaller under the argmax rule. The settings differ: Ding et al. used a random split of the 4,192-essay Kaggle subset, BERT rather than DeBERTa-v3, and averaged folds; we used an essay-grouped split of the full corpus and paired intervals. Our post-hoc result, where the whole-essay model gained only after a calibration correction, suggests one reason why whole-essay context can look less useful than it is: wider inputs shift probabilities towards the minority classes, and an argmax evaluation penalises that shift.

Schaller et al. (2025) found that models relying on whole-essay context are fragile when context is limited. We saw a related fragility: the 7-epoch whole-essay model overfitted and lost the gain, and the paragraph input lowered Macro-F1. Baffour et al. (2023) reported moderate demographic differences in Feedback Prize effectiveness models; our ELL description shows large differences in per-class results that follow the class mix, which illustrates why such differences need careful conditioning before they are called bias.

## Model–rater agreement and rater–rater agreement answer different questions

A model's κ against the labels is easily mistaken for a rater's κ. Figure 8.1 places the two side by side only to show that they are different quantities.

![Figure 8.1. Two different agreement statistics. (a) Rater–rater κ reported for PERSUADE 2.0 before adjudication. (b) Cohen's κ between the locked L1 model and the adjudicated label on the official test. They are shown in separate panels because they are not on a common scale.](figures/fig24_rater_rater_vs_model_rater_agreement.png)

Rater–rater κ (0.316 overall; 0.165–0.432 by type) answers the question: how consistently do two trained humans, working independently, assign the same label to the same segment? It describes the reliability of the measurement. It was computed by Crossley et al. on 159,228 segments where the two raters' segmentations overlapped by at least 50%, before a third rater adjudicated disagreements, with a weighted κ, on the whole corpus.

Model–rater κ (0.372 for the locked L1 model on the test; 0.27–0.44 by type) answers a different question: how well does the model reproduce the final adjudicated label, which is the label the model was trained to imitate? It is computed on our test units, with the gold segmentation, after adjudication, unweighted.

The two numbers differ in what is compared (two noisy humans vs a model and a consensus label), in the label (single ratings vs adjudicated), in the units (overlapping segments vs gold units), in the weighting, and in the data. A model κ above the rater κ therefore does not mean the model is "better than a rater" or "at human level". What the rater κ does tell us is that the label itself is uncertain: when two experts agree only at κ = 0.32, part of what we count as model error is disagreement about the label, and no model can be expected to reach a high agreement with any one rating. The per-type pattern is consistent with this (Claim and Counterclaim are the least reliable for raters and among the hardest for the model), but with seven types this is an observation, not a test.

## Implications for the intended user

For a teacher, the locked model is usable at most as a way to order the reading, not as a filter. Under the argmax rule it flags about 6% of units, of which one third are truly Ineffective, and it misses more than half of the Ineffective units. A teacher who lowers the threshold to see 70% of the weak units must read about 2.6 times as many flags (4,633 instead of 1,761 on validation), four of every five of them false alarms. The human must therefore read the essay before giving feedback, and the tool should never show a student a label that a teacher has not confirmed. Because performance drops on unseen prompts, a teacher using a new prompt should expect weaker rankings than those reported in Table 6.5. Demographic attributes must stay out of both the input and the decision rule.

## Limitations

1. Label reliability. Effectiveness labels have low inter-rater agreement (κ = 0.316). Our gold labels are adjudicated consensus labels, a proxy for effectiveness, not ground truth. Results are statements about agreement with these labels.
2. Gold segmentation and types. All models receive human-annotated units and types. A deployed system would have to segment essays itself, and its errors would lower performance (Ding et al., 2023).
3. One training run per configuration. Differences below about 0.005–0.01 Macro-F1 between DeBERTa variants are within observed run-to-run variation. The bootstrap intervals cover sampling of essays only.
4. Test-pass conditions. Training, validation and test ran in one session, so validation results were logged but not reviewed by a person before the test pass (Table 5.1).
5. LOPO coverage. DeBERTa and SVM LOPO cover 3 of 15 prompts with one run per fold; the Random Forest covers all 15.
6. Supplementary context runs. They were trained after the test pass, evaluated on validation only, which also chose their epochs, and the source passages covered 4 of 7 source-based prompts (two as summaries).
7. Length mechanism. The residual length effect is an association; its cause is untested.
8. Population. Results apply to U.S. grade 6–12 essays on 15 prompts. They do not establish effectiveness for other learners, languages or prompts, and they say nothing about learning outcomes.
9. Data integrity. The CSV files had been altered by a spreadsheet program before we received them. We verified the essay-level identifiers, labels and text against our predictions, but cannot rule out other silent changes in columns we did not use.
