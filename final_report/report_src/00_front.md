---
title: "Predicting the Effectiveness of Argumentative Discourse Units in Student Essays"
subtitle: "Classical and transformer models, controlled context ablation, prompt transfer and error analysis on PERSUADE 2.0"
course: "Machine Learning Applications (61FIT4MLA / 62FIT4MLA), class CLC02"
group: "Group 06"
lecturer: "Bùi Quốc Khánh"
institution: "Faculty of Information Technology, Hanoi University"
date: "November 2026"
---

<!-- TITLE PAGE (the build script renders this block as a separate, centred title page) -->

::: titlepage
HANOI UNIVERSITY
FACULTY OF INFORMATION TECHNOLOGY

MACHINE LEARNING APPLICATIONS (61FIT4MLA / 62FIT4MLA)
FINAL PROJECT REPORT

PREDICTING THE EFFECTIVENESS OF ARGUMENTATIVE DISCOURSE UNITS IN STUDENT ESSAYS

Classical and transformer models, controlled context ablation, prompt transfer and error analysis on PERSUADE 2.0

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

Teachers of argumentative writing need to know which parts of an essay are weak, not only how good the essay is overall. We study one measurable question: given a student essay that has already been segmented into discourse units (Lead, Position, Claim, Counterclaim, Rebuttal, Evidence, Concluding Statement), how well can a model predict whether each unit is Ineffective, Adequate or Effective, as judged by trained raters, and what information does the model need to do so? The prediction is made after the essay is submitted and segmented, and the output is meant to prioritise units for a teacher's review, not to grade students.

We use PERSUADE 2.0 (Crossley et al., 2024; CC BY-NC-SA 4.0), which contains 237,966 annotated units from 25,996 essays written by U.S. students in grades 6 to 12 on 15 prompts. The labels are highly imbalanced (4.5% Ineffective, 79.3% Adequate, 16.3% Effective). The 144,289 units of the official training file were split by essay into 115,187 training and 29,102 validation units; the official test file (93,677 units, 10,402 essays) was scored exactly once, with a locked configuration. We compare a majority-class baseline, two classical models on TF-IDF and structural features (an interpretable Logistic Regression and a Random Forest), and a fine-tuned DeBERTa-v3-base transformer, all on the same units and with per-class metrics. A controlled context ablation changes only the input of the transformer: the unit alone (Level 0), the unit with its neighbouring units (Level 1), and, as supplementary validation-only runs, wider windows, the paragraph, a source passage and the whole essay. Leave-one-prompt-out folds measure transfer to unseen prompts.

On the official test, the locked DeBERTa Level 1 system reached Macro-F1 0.577 (F1 Ineffective 0.368, Adequate 0.841, Effective 0.523), against 0.510 for the Random Forest and 0.297 for the majority baseline. Level 1 exceeded Level 0 by 0.016 Macro-F1 (95% essay-bootstrap CI 0.012 to 0.021); the gain came mostly from the Ineffective class (+0.029) and from Claim, Counterclaim and Rebuttal units, but two runs of the same configuration differed by as much as the gain on validation, so we read it as small. A model that never saw the prompt lost 0.048 to 0.092 Macro-F1 on two of three held-out prompts. Error analysis showed that essay length is strongly associated with the holistic score (Spearman 0.76) and with the class mix, so length must be separated from proficiency before errors are attributed to missing context; within the same holistic score, the error rate still rose with length (odds ratio 1.19 per length quartile). Ten high-confidence Ineffective failures were not repaired by local context; only whole-essay or source inputs moved some of them. The main limitations are label reliability (rater–rater κ = 0.316), one training run per configuration, LOPO on three prompts, and gold segmentation. The model is suitable at most as a review-prioritisation aid under teacher control.

Keywords: argument quality, discourse effectiveness, automated writing evaluation, DeBERTa, context ablation, leave-one-prompt-out, PERSUADE 2.0.

::: pagebreak
:::

::: toc
Table of Contents
:::

::: pagebreak
:::

::: lof
List of Figures
:::

::: lot
List of Tables
:::

::: pagebreak
:::

# List of Abbreviations {.unnumbered}

| Abbreviation | Meaning |
|---|---|
| AWE | Automated writing evaluation |
| CI | Confidence interval (95%, percentile, essay-level bootstrap unless stated) |
| DeBERTa | Decoding-enhanced BERT with disentangled attention (He et al., 2021, 2023) |
| ELL | English language learner (status as recorded in PERSUADE 2.0) |
| FS-B | Feature Set B: word TF-IDF + discourse-type one-hot + five structural features |
| L0, L1, L1 ±2, L2, L3 | Context levels of the transformer input (Section 4.3.3) |
| LOPO | Leave-one-prompt-out evaluation |
| LR | Logistic Regression |
| PA | Prompt-Aware input (Level 1 prefixed with the prompt name) |
| QWK | Quadratic weighted kappa |
| RF | Random Forest |
| SVM | Support vector machine (linear) |
| TF-IDF | Term frequency – inverse document frequency |
| Q1–Q4 | Essay-length quartiles (cut points 315, 422 and 566 words, fixed on validation) |

::: pagebreak
:::
