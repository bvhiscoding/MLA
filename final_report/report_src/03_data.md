# Data

## Source, licence and permitted use

We use the PERSUADE 2.0 corpus (Crossley et al., 2024), distributed through the authors' repository (github.com/scrosseye/persuade_corpus_2.0) as two CSV files: a training file and a password-protected test file. The corpus is released under the Creative Commons BY-NC-SA 4.0 licence, which permits non-commercial academic use with attribution and share-alike. Our use (a course project, no redistribution of the data, no commercial purpose) is within these terms. Because the CSV files are large and licensed, they are not committed to the project repository; `.gitignore` excludes them, and Appendix B gives the download instructions and the SHA-256 hashes that identify the exact files used.

The corpus also contains demographic fields (gender, race/ethnicity, ELL status, economic disadvantage, disability status). They are used only to describe performance for one pre-defined subgroup (ELL status, Section 6.6); they are never model inputs. Source texts of the source-based prompts are copyrighted articles and are not part of the CSV (the `source_text` column holds only their titles); the texts we used for Level 2 are kept locally and excluded from the repository.

## Unit of observation and labels

The unit of observation is one annotated discourse unit: a contiguous span of a student essay that a trained annotator labelled with one of seven discourse types. Each unit carries one effectiveness label. Table 3.1 gives the official definitions, condensed from the rubric shipped with the corpus (`argumentation_effectiveness_rubric.pdf`).

Table 3.1. Discourse types and effectiveness labels (condensed from the PERSUADE effectiveness rubric).

| Discourse type | What it does | Effective | Ineffective |
|---|---|---|---|
| Lead | Opens the essay | Grabs attention and strongly points toward the position | May not grab attention and may not point to the position |
| Position | States the writer's stance | Clear stance closely related to the topic | Not relevant to the topic and/or no clear stance |
| Claim | Supports the position | Closely relevant to the position, with specific points; valid | Irrelevant to the position; weak or not acceptable |
| Counterclaim | States an opposing view | Reasonable, relevant, a valid objection | Neither reasonable nor relevant |
| Rebuttal | Answers the counterclaim | Directly answers and refutes the counterclaim | Does not answer the counterclaim (Adequate: answers indirectly or weakly) |
| Evidence | Supports a claim | Closely relevant; concrete facts, examples or studies; sound reasons | Irrelevant to the claim; few valid examples; unacceptable assumptions |
| Concluding Statement | Closes the essay | Restates the claims in a new way and strengthens the position | Does not restate or support the position |

Adequate lies between the two: in the corpus paper's words, the writer "sufficiently fulfilled the function of the element" (Crossley et al., 2024, Section 2.1). Two properties of these definitions matter for modelling. First, the label is relational: a Claim is judged against the Position, a Rebuttal against the Counterclaim, Evidence against the Claim it supports, and a Position against the prompt. Information needed to judge a unit can therefore lie outside the unit, which is the motivation for the context experiments (RQ2). Second, the label is a rater judgement with limited reliability (κ = 0.316 between raters before adjudication; Section 2.2), so the gold label is a proxy for effectiveness, not ground truth.

We map the labels to integers once, explicitly: Ineffective = 0, Adequate = 1, Effective = 2. This fixed mapping matters because scikit-learn orders string classes alphabetically (Adequate, Effective, Ineffective); code that assumes a different column order silently swaps the classes.

## Independent groups

Units are nested in essays, essays in prompts, and each essay was written by one student. Three consequences follow. Units of the same essay must never be split between training and evaluation; confidence intervals must resample essays, not units; and claims about new prompts require holding out whole prompts. The corpus provides one essay per student in our data, so essay and student groups coincide.

## From raw records to annotated units

Figure 3.1 shows the filtering and splitting pipeline. The same rule is applied to both files: keep records that have an effectiveness label and non-empty text, strip whitespace, and number the remaining units in file order. The resulting position, `row_idx`, is the key that every prediction file uses (Section 3.5).

![Figure 3.1. From raw CSV records to the training, validation and official test units. The official test was opened once.](figures/fig02_data_pipeline_split.png)

Table 3.2. Record filtering (script `final_report/scripts/01_data_checks_eda.py`, table D2).

| File | Raw records | Records without an effectiveness label | Of which typed "Unannotated" | Annotated units | Essays |
|---|---:|---:|---:|---:|---:|
| Training file | 173,266 | 28,977 | 28,973 | 144,289 | 15,594 |
| Test file | 112,117 | 18,440 | 18,437 | 93,677 | 10,402 |

The records without a label are almost entirely text that annotators did not assign to any discourse element ("Unannotated"); seven records of other types have an empty label and are dropped as well.

The 144,289 training-file units were split with `GroupShuffleSplit` (80/20, grouped by essay, seed 42). Table 3.3 gives the result. All 15 prompts occur in both training and validation, so this split measures generalisation to new essays on known prompts; generalisation to new prompts is measured separately (Section 5.3).

Table 3.3. Units, essays and label distribution by split.

| Split | Units | Essays | Ineffective (%) | Adequate (%) | Effective (%) | Role |
|---|---:|---:|---:|---:|---:|---|
| Train | 115,187 | 12,475 | 4.46 | 78.44 | 17.11 | Fit all models and preprocessing |
| Validation | 29,102 | 3,119 | 4.56 | 78.68 | 16.76 | Model, epoch and threshold selection; all error analysis |
| Official test | 93,677 | 10,402 | 4.51 | 80.45 | 15.04 | One scoring pass with a locked configuration |
| All annotated | 237,966 | 25,996 | 4.49 | 79.26 | 16.25 | — |

![Figure 3.2. Label distribution by split. The test file contains slightly more Adequate units than the training file.](figures/fig05_label_distribution_by_split.png)

## Data verification

Before any result is interpreted, the identifier joins and the label loading must be shown to be correct on raw examples. The script `final_report/scripts/01_data_checks_eda.py` re-reads both raw CSV files and runs the checks in Table 3.4; its full log is in `final_report/evidence/data_checks_log.txt`. All checks passed.

Table 3.4. Data verification checks (all passed on 15 November 2026).

| ID | Check | Result |
|---|---|---|
| C1 | SHA-256 of the training and test CSV equal the hashes logged by the training run and by the test lock file | Equal (f61319ed…, 8b4cbbda…) |
| C2 | Filtering reproduces 173,266 → 144,289 and 112,117 → 93,677 | Reproduced |
| C3 | Label vocabulary is exactly {Adequate, Effective, Ineffective}; every unit gets an integer label; type vocabulary is the seven discourse types | Confirmed in both files |
| C4 | Identifier integrity | `discourse_id` has only 728 distinct values for 144,289 units; `essay_id_comp` is intact (15,594 + 10,402 essays) |
| C5 | Each of 17 saved prediction files agrees with the raw data, row by row, on essay, discourse type and gold label | 0 mismatches in about 699,000 rows |
| C6 | Split integrity: no essay in two splits; no training or validation essay in the test; all prompts in both training and validation; each LOPO fold scores every unit of exactly one prompt | Confirmed |
| C7 | Six raw records traced from the CSV to the prediction file (Table 3.5) | All agree at every step |

The identifier check (C4) records the most important data risk we found. The CSV files we worked from had been opened and saved in a spreadsheet program at some point, which converted the numeric `discourse_id` to scientific notation (for example `1.62144E+12`). As a result, one stored `discourse_id` value can be shared by up to 932 units from 93 different essays. Any join on `discourse_id` silently attaches the wrong essay's attributes to a unit. The numeric `essay_id` is also partly corrupted (one stored value covers two essays), while `essay_id_comp`, a hexadecimal string, is intact. Every analysis in this report therefore joins units by `row_idx` or by `essay_id_comp`, and each join is checked against discourse type and gold label before use.

Table 3.5 traces six records end to end: five drawn at random from the validation split (seed 2026) and the case used throughout the report (row_idx 108613). For each, the label string in the raw file, the integer loaded by our code, and the gold label stored in the prediction file agree.

Table 3.5. Six raw records traced from the CSV to the prediction file (table D7). "Raw record" is the 0-based record number in the training CSV; the stored discourse_id shows the spreadsheet corruption. The label column follows one unit from the raw string to the integer loaded by our code and to the gold label stored in the prediction file.

| row_idx | Raw record | essay_id_comp | Stored discourse_id | Type | Label: raw → loaded → file | L1 prediction |
|---:|---:|---|---|---|---|---|
| 93085 | 111932 | A1B2F28757E3 | 1.61513E+12 | Claim | Adequate → 1 → 1 | Ineffective |
| 53101 | 64465 | 6D1D5D542E08 | 1.61956E+12 | Claim | Adequate → 1 → 1 | Adequate |
| 25444 | 31612 | 7D378AEFD0C3 | 1.62005E+12 | Claim | Adequate → 1 → 1 | Adequate |
| 123137 | 146304 | 8AE119913109 | 1.62197E+12 | Concluding Statement | Effective → 2 → 2 | Effective |
| 3642 | 4088 | E0ACC902891D | 1.62252E+12 | Claim | Adequate → 1 → 1 | Adequate |
| 108613 | 130257 | FE3141FA4163 | 1.62015E+12 | Claim | Ineffective → 0 → 0 | Adequate |

Two further observations came out of the checks. On a random sample of 3,000 units, the unit text was always found inside the essay's `full_text`, but it started exactly at the stored `discourse_start` offset only 27% of the time. Offsets are therefore approximate; our context inputs use the order of units within an essay, not character offsets. Second, one prompt name is stored with surrounding quotation marks in the raw file ("A Cowboy Who Rode the Waves") but without them in our prediction files; the check normalises this before comparing.

## Missing values and duplicates

Among the 237,966 annotated units, holistic score, essay word count, prompt, task type and `discourse_start` are never missing. Grade level is missing for 4.67% of units and ELL status is missing or blank for 5.12%; neither is a model input. Fifty-one units repeat exactly within the same essay. Across essays, 423 distinct unit texts occur in two or more essays (1,338 units, mostly short formulaic sentences such as "summer projects should be student-designed", which appears 54 times); 85 of these texts carry different labels in different essays, a direct illustration that the label depends on the surrounding essay. 415 such short texts also occur in the test file. We kept all of them: they are genuine, independently written units, and removing them would bias the data towards longer units.

## Exploratory data analysis

### Label imbalance and discourse types

Effectiveness is heavily imbalanced: Ineffective units are 4.5% of the data and Adequate 79.3%. A model that always predicts Adequate reaches 78.7% accuracy on validation and 80.5% on test while never finding a weak unit. Accuracy is therefore not a useful headline metric for this task (Section 5.4).

The Ineffective rate varies by discourse type (Figure 3.3). Evidence has the highest rate (6.9%) and Claim the lowest (2.9%); Claim and Evidence together make up two thirds of all units. Discourse type alone is only weakly associated with the label (Cramér's V = 0.075; Table 3.6).

![Figure 3.3. Label mix by discourse type, training and validation units (n = 144,289).](figures/fig06_label_mix_by_discourse_type.png)

### Prompts and task type

The label mix differs strongly between prompts (Figure 3.4). The four prompts with the most Ineffective units are all source-based: "Does the electoral college work?" (11.5%), "Exploring Venus" (11.4%), "The Face on Mars" (9.9%) and "Facial action coding system" (9.2%). Several independent prompts have fewer than 1% Ineffective units but 20–30% Effective units. A model can therefore learn prompt-specific priors, which is one reason to test prompt transfer (RQ3).

![Figure 3.4. Label mix by prompt (train and validation). An asterisk marks source-based prompts.](figures/fig07_label_mix_by_prompt.png)

### Unit length

Effective units are much longer than the others (median 52 words against 25 for Adequate and 29 for Ineffective; Figure 3.5). Ineffective units are not simply short: their median is slightly above that of Adequate units, and the interquartile ranges overlap. Length is a useful but weak cue, and a model that relied on it would mistake long but off-topic units (case 2 in Section 7.3) for Effective ones.

![Figure 3.5. Unit length by label, all annotated units (log scale).](figures/fig08_unit_length_by_label.png)

### Essay length, holistic score and class mix

Before any error is attributed to lost context, we check whether essay length is associated with the holistic score and with the class mix. It is, strongly. At the essay level, length and holistic score have a Spearman correlation of 0.76 (n = 25,996 essays; Figure 3.6): the median essay with score 2 has 229 words, the median essay with score 6 has 824.

![Figure 3.6. Essay length by holistic score, all essays. Dashed lines mark the essay-length quartile cut points used throughout the report.](figures/fig09_essay_length_vs_holistic_score.png)

The class mix moves with both variables (Figure 3.7). In essays with holistic score 1, 59.8% of units are Ineffective; in essays with score 6, 0.2% are Ineffective and 53.8% Effective. Across length quartiles, the Ineffective share falls from 8.7% (Q1, ≤315 words) to 1.4% (Q4, ≥567 words) while the Effective share rises from 5.4% to 34.5%, and the mean holistic score rises from 2.39 to 4.66. Table 3.6 compares the strength of these associations: the holistic score is the variable most strongly associated with the unit label (Cramér's V = 0.386), followed by essay length (0.221) and prompt (0.188).

![Figure 3.7. Label mix (a) by holistic score and (b) by essay-length quartile, train and validation units.](figures/fig10_label_mix_by_score_and_length.png)

Table 3.6. Association of each variable with the unit label (train + validation units; χ² test of independence, all p < 10⁻¹⁰⁰; table E6d).

| Variable | χ² | Cramér's V |
|---|---:|---:|
| Holistic score (1–6) | 43,093 | 0.386 |
| Essay-length quartile | 14,152 | 0.221 |
| Prompt (15) | 10,218 | 0.188 |
| Task type (independent / source-based) | 3,786 | 0.162 |
| Discourse type (7) | 1,643 | 0.075 |

Within the same holistic score the class mix changes much less, but not uniformly (Figure 3.8). For scores 4 and 5, the Effective share rises only slightly with length (score 4: 11.5% → 18.8%). For score 2, the Ineffective share rises with length (10.6% in Q1 to 25.3% in Q3), so long essays with a low score contain more weak units than short ones. This matters for Chapter 7: a rising error rate across length quartiles could reflect a changing class mix rather than a harder task, and we must compare errors within the same score and class before blaming lost context.

![Figure 3.8. Share of Ineffective and Effective units by essay-length quartile within the same holistic score (cells with at least 200 units).](figures/fig11_label_mix_within_score_by_length.png)

### Essays, units per essay and subgroups

Essays contain on average 9.2 annotated units (median 9, range 1–29). 20.8% of essays contain at least one Ineffective unit, but only 3.4% contain both an Ineffective and an Effective unit: weak and strong units rarely co-occur in the same essay, which is consistent with the dependence of unit labels on writer proficiency. ELL status is recorded as "Yes" for 1,062 training, 268 validation and 914 test essays (about 9%); ELL essays contain far more Ineffective units (12.2% on validation) and fewer Effective units (4.8%) than other essays.

## One unit traced through the pipeline

We use one validation unit throughout the report to show the full path from data to prediction (Table 3.7). It is one of the ten failure cases studied in Section 7.3 (case 8).

Table 3.7. Case 8 traced from raw record to prediction.

| Step | Value |
|---|---|
| Raw record / row_idx | Record 130257 of the training CSV / row_idx 108613; validation split |
| Essay | essay_id_comp FE3141FA4163; prompt "Cell phones at school" (independent); holistic score 2; 169 words |
| Unit | Claim: "Some kids will ask there parents to transfer school" (9 words) |
| Gold label | Ineffective (id 0) |
| Level 0 input | `Claim [SEP] Some kids will ask there parents to transfer school` |
| Level 1 input | `Claim [SEP] Previous: They will hide them from the teachers … You will just make all the kids mad. [SEP] Target: Some kids will ask there parents to transfer school [SEP] Next: If you chose policy one you will make the student happy.` (95 tokens, no truncation) |
| Prompt-Aware input | `Prompt: Cell phones at school [SEP]` + Level 1 input |
| Majority baseline | Adequate |
| Logistic Regression (FS-B) | P = 0.052 / 0.916 / 0.032 → Adequate (Section 4.2 traces the weights) |
| Random Forest (FS-B) | P = 0.286 / 0.485 / 0.229 → Adequate |
| DeBERTa L0 / L1 / PA | P(Ineffective) = 0.017 / 0.058 / 0.217 → Adequate in all three |
| Outcome | All models miss this unit; context raises P(Ineffective) but not above the other classes |

The unit is a bare prediction with no reason. Its weakness is visible to a reader who knows that a Claim should support the position with a specific point; none of the models flags it under the argmax rule. Section 6.5 shows what a lower threshold on P(Ineffective) would change for this unit and for the whole validation set.
