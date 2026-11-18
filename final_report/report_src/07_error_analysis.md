# Error Analysis

The error analysis proceeds in two steps: first check whether errors are associated with variables that also change the class mix (essay length, proficiency), and only then read individual cases and ask what information the model lacked. All analysis uses the validation split unless stated; test numbers are descriptive and no choice depends on them.

## Where the errors are

Under the locked L1 model, 25.8% of validation units and 24.3% of test units are misclassified. On the test (Figure 6.4), 74% of all errors are confusions between Adequate and Effective (16,752 of 22,783), 26% are confusions between Ineffective and Adequate (5,886), and fewer than 1% are Ineffective↔Effective (145). The errors that matter most to a teacher, missed Ineffective units, are 2,470 of the 4,225 gold Ineffective test units (58.5%).

## Errors and essay length: length or proficiency? (RQ4)

### The question

The error rate rises with essay length. Two explanations predict this. Hypothesis A: something about long essays makes their units harder to classify (longer units, more complex arguments, more truncation). Hypothesis B: long essays are written by stronger writers (Section 3.7.4); their units are more often Adequate or Effective, and the Adequate/Effective boundary is harder than the Adequate/Ineffective one. Hypothesis B is a change in the class mix, not a change in task difficulty, so it must be ruled in or out before any error is attributed to lost context.

### Without controlling for proficiency

Table 7.1 shows the L1 error rate by essay-length quartile. It rises from 22.0% to 30.5% on validation and from 21.1% to 30.4% on the test. Over the same quartiles the gold Ineffective share falls from 9.0% to 1.3% and the Effective share rises from 5.3% to 32.8%, and the share of errors that are Adequate↔Effective confusions rises from 48% to 92% (Figure 7.1a).

Table 7.1. Locked L1 errors by essay-length quartile (table R7).

| Quartile (words) | Val units / essays | Gold Ineff / Eff | Val error rate | Errors that are Adequate↔Effective | Val Macro-F1 | Val F1 Ineff / Adeq / Eff | Test error rate | Test Macro-F1 |
|---|---|---|---:|---:|---:|---|---:|---:|
| Q1 (≤315) | 7,333 / 1,037 | 9.0% / 5.3% | 22.0% | 47.5% | 0.532 | 0.430 / 0.868 / 0.298 | 21.1% | 0.532 |
| Q2 (316–422) | 7,277 / 786 | 5.0% / 10.7% | 23.0% | 67.1% | 0.551 | 0.366 / 0.858 / 0.427 | 22.0% | 0.530 |
| Q3 (423–566) | 7,226 / 690 | 2.9% / 18.3% | 27.9% | 83.8% | 0.552 | 0.365 / 0.812 / 0.480 | 25.5% | 0.548 |
| Q4 (≥567) | 7,266 / 606 | 1.3% / 32.8% | 30.5% | 92.0% | 0.526 | 0.192 / 0.743 / 0.642 | 30.4% | 0.566 |

![Figure 7.1. (a) L1 error rate and the share of errors that are Adequate↔Effective confusions, by essay-length quartile; (b) per-class F1 and Macro-F1 by quartile (validation).](figures/fig21_error_composition_by_length.png)

Figure 7.1b shows a pattern that a single error rate hides. Macro-F1 hardly changes across quartiles (0.53–0.55 on validation; 0.53–0.57 on test). What changes is which class is hard: Effective F1 rises from 0.30 to 0.64 as Effective units become common, while Ineffective F1 falls from 0.43 to 0.19 as they become rare. Much of the rising error rate is therefore the class mix moving towards the harder Adequate/Effective boundary, which supports Hypothesis B.

### Within the same holistic score

To separate length from proficiency we compare length quartiles within the same holistic score. Table 7.2 and Figure 7.2 show the result.

Table 7.2. L1 error rate (%) by length quartile within the same holistic score, validation. 95% CI from 1,000 essay-level bootstrap resamples; N = units / essays. Cells with fewer than 20 essays are shown in Appendix E only.

| Holistic score | Q1 (≤315) | Q2 (316–422) | Q3 (423–566) | Q4 (≥567) |
|:---:|---|---|---|---|
| 2 | 23.2 [21.3, 25.1]; 3,200/493 | 31.4 [27.1, 35.6]; 722/91 | 33.2 [26.3, 39.5]; 295/34 | — (80/11) |
| 3 | 19.3 [17.7, 21.1]; 3,517/424 | 21.8 [20.0, 23.9]; 3,743/404 | 22.9 [19.8, 26.0]; 1,465/143 | 28.2 [22.1, 34.3]; 472/40 |
| 4 | 19.6 [13.4, 26.6]; 260/29 | 22.0 [19.9, 23.9]; 2,622/260 | 28.5 [26.5, 30.5]; 3,984/379 | 31.1 [28.2, 33.9]; 1,961/174 |
| 5 | — | — (127/12) | 30.3 [26.9, 34.0]; 1,391/120 | 31.7 [29.6, 34.0]; 3,336/277 |

![Figure 7.2. L1 error rate by essay-length quartile within the same holistic score: (a) validation, where decisions are made; (b) official test, descriptive only.](figures/fig20_error_within_score_by_length.png)

Within the same score, the error rate still rises with length. For score-3 essays it goes from 19.3% to 28.2% on validation (17.6% to 29.2% on the test); for score-4 essays from 19.6% to 31.1%. Table 7.3 summarises the trend with a logistic regression of unit error on length quartile (coded 0–3), with standard errors clustered by essay.

Table 7.3. Odds ratio of a unit error per length quartile, locked L1 model (essay-clustered 95% CI; `outputs/length_within_score_regression.csv`).

| Specification | Validation OR [95% CI] | Test OR [95% CI] |
|---|---|---|
| Length quartile only | 1.17 [1.14, 1.21] | 1.18 [1.16, 1.20] |
| + holistic score | 1.19 [1.14, 1.25] | 1.16 [1.13, 1.19] |
| + holistic score + gold label + discourse type | 1.17 [1.11, 1.23] | 1.13 [1.10, 1.16] |
| Score-3 essays only | 1.15 [1.06, 1.24] | 1.21 [1.16, 1.26] |
| Score-4 essays only | 1.27 [1.17, 1.37] | 1.17 [1.11, 1.23] |

Controlling for holistic score does not shrink the length effect, and controlling also for the gold label and discourse type shrinks it only slightly. The same pattern holds for DeBERTa L0 (OR 1.16 after controlling for score) and for the Random Forest (1.31).

### Answer

Both hypotheses are needed. Proficiency and class mix explain why the type of error changes with length and why Macro-F1 stays flat while the error rate rises (Hypothesis B). They do not explain the whole rise: within the same score and gold label, units of longer essays are still about 17% more likely per quartile to be misclassified, so Hypothesis A is not ruled out. We have not identified its mechanism. Truncation is an unlikely main cause, because only 0.62% of Level 1 inputs exceed 512 tokens. Plausible remaining explanations, none tested, are that units in long essays are longer and more elaborate, that raters judge a unit against the rest of a long, developed essay that a local model cannot see, and that the six-level holistic score leaves residual proficiency differences within each level.

## Ten high-confidence Ineffective failures

### Selection rule

Before any context model was trained, we selected the ten gold-Ineffective validation units that the DeBERTa L0 model misclassified with the highest confidence (probability of the predicted class above 0.94). The rule targets the failures that a teacher relying on the tool would never see. Because the cases were selected as extreme failures of one model, later models are expected to score them somewhat less extremely (regression to the mean); individual outcomes are illustrations, not estimates. Each case was read by the group together with the whole essay and, where relevant, the prompt and source.

Table 7.4. The ten cases: identifiers and P(Ineffective) under Level 0, the first Level 1 run and the locked Level 1 model (table R8). All ten have gold label Ineffective; every model predicts Adequate for all of them, except case 2, which is predicted Effective.

| Case | row_idx | essay_id_comp | Prompt | Type | Unit (start) | P(Ineff) L0 / L1 first / L1 locked |
|:---:|---:|---|---|---|---|---|
| 1 | 2467 | 6BF54A9F8383 | Phones and driving | Counterclaim | "There are many reason on why texting while driving is very useful" | 0.022 / 0.029 / 0.027 |
| 2 | 10303 | BFDD411D610F | Car-free cities | Evidence | "To provide reasonings to my strong point, brings me back to paragraph 36. …" | 0.000 / 0.001 / 0.008 |
| 3 | 25520 | 1CE967B8E5C9 | A Cowboy Who Rode the Waves | Position | "I think you shouldn't join the Seagoing Cowboys" | 0.022 / 0.010 / 0.006 |
| 4 | 105080 | 326DEFF8D486 | Cell phones at school | Counterclaim | "Not allowing students to use there phones at all" | 0.038 / 0.090 / 0.170 |
| 5 | 86267 | 8C10A8ABF46D | Driverless cars | Position | "The Driverless people can cause problems." | 0.028 / 0.151 / 0.103 |
| 6 | 114270 | C75B9C4FFEAD | Distance learning | Counterclaim | "But Sometimes it could be a distraction from you doing all your work." | 0.031 / 0.040 / 0.035 |
| 7 | 110025 | 53858BE44997 | Cell phones at school | Position | "I reconsider that are principal should let us eight graders bring are cell phones …" | 0.035 / 0.097 / 0.052 |
| 8 | 108613 | FE3141FA4163 | Cell phones at school | Claim | "Some kids will ask there parents to transfer school" | 0.021 / 0.124 / 0.058 |
| 9 | 83105 | 81B0FFE6659F | Driverless cars | Lead | "The future is near and the talk about driverless cars is upon us" | 0.045 / 0.080 / 0.143 |
| 10 | 9735 | 7D59699BB70F | Car-free cities | Claim | "Another cars is a bad idea is because of its gas." | 0.039 / 0.032 / 0.039 |

Table 7.5. Our reading of each case and the information a rater would need.

| Case | What we observed after reading the unit, the essay and (where relevant) the source | Information needed to judge it |
|:---:|---|---|
| 1 | A counterclaim ("texting while driving is very useful") that the essay never answers; read alone it is a fluent sentence | Whole essay |
| 2 | An accurate quotation of paragraph 36 of the source set (verified: the set has 43 paragraphs and paragraph 36 contains the quoted sentence), followed by off-topic reasoning about learner's permits and driving tests that does not support the point | The unit itself (the weakness is visible in it); the model was probably misled by length, an explicit quotation and connectives such as "Furthermore" (untested) |
| 3 | A bare stance with no reason (8 words) | The unit itself |
| 4 | A sentence fragment; no opposing argument is actually stated | The unit itself |
| 5 | A vague position that may conflict with the source article | Source and task |
| 6 | A counterclaim with no rebuttal anywhere in the essay | Whole essay |
| 7 | A thesis whose scope is unclear relative to the prompt | Prompt / task |
| 8 | An unsupported prediction; the neighbouring units do not supply a reason | Local context |
| 9 | A generic hook that does not engage the prompt | Prompt / task |
| 10 | A claim with no support and a garbled reason | The unit itself |

### Grouping and hypothesis check

The readings fall into four groups by the information a rater would need: the unit itself (cases 2, 3, 4, 10), local context (case 8), the whole essay (cases 1, 6) and the prompt or source (cases 5, 7, 9). This grouping led to a testable hypothesis on development data: if missing information causes these failures, giving the model that information should move the corresponding cases towards Ineffective. Figure 7.3 shows P(Ineffective) for every case under every context level.

![Figure 7.3. P(Ineffective) for the ten failure cases under each context level (validation). An asterisk marks a prediction of Ineffective.](figures/fig23_ten_cases_by_context_level.png)

The result is mixed. Under Level 1, none of the ten cases changes its argmax prediction, although P(Ineffective) rose in 8 of 10 in the first L1 run. Wider inputs do move some cases: case 2 becomes Ineffective under the paragraph (P = 0.83), source-passage (0.54) and both whole-essay models (0.73 and 0.92); case 1, the unanswered counterclaim, becomes Ineffective only under the 3-epoch whole-essay model (0.71), and so does case 5 (0.55). Because the wider models flag more units overall, we checked whether these flips are only a shift of the threshold: lowering Level 1's threshold until it flags as many units as each wider model still flips none of the ten. The cases that need only the unit itself (3, 4, 10) are not repaired by any input, which points to a limit of the model or of the labels rather than of the context.

The hypothesis is therefore partly supported for the whole-essay group and not tested adequately for the source group (source texts were available for only 4 of 7 source-based prompts). Ten selected cases cannot establish an effect; the aggregate test is the post-hoc whole-essay result in Section 6.8, which is itself exploratory.

## Decisions changed by the error analysis

Table 7.6 records the decisions that the analyses in this chapter led to. Each row is traceable to a file in the repository.

Table 7.6. Decisions taken after inspecting errors.

| Question | Assumption before running | Output | Decision |
|---|---|---|---|
| Why are the most confident failures wrong? | Model weakness on short units | Most of the ten cases need information outside the unit | Design the controlled context ladder (L0 vs L1) |
| Does local context repair the cases? | Several cases would be repaired | 0 of 10 flip; Ineffective F1 rises slightly | Lock L1 for its Ineffective F1 while stating that L0 and L1 cannot be distinguished on validation |
| Is the rising error with length about difficulty? | Longer essays are more complex | Class mix shifts strongly with length | Compare errors within the same holistic score |
| Within the same score, does error rise with length? | No | Yes, OR ≈ 1.17–1.19 per quartile | Keep both hypotheses |
| Would a lower threshold catch the cases? | Case 8 flips at θ = 0.10 | Not for the locked model (P = 0.058); about 8 false alarms per extra catch | Keep argmax for evaluation; present θ as a user choice |
| Does wider context help? | Whole essay and sources should help | Argmax: no; after equal calibration correction: whole essay +0.025 (one run) | Report as exploratory; recommend a pre-registered test |
