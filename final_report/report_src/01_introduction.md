# Introduction

## Background and motivation

Argumentative writing is a core outcome of secondary education. A student must state a position, support it with claims and evidence, anticipate counterclaims and answer them. National assessments in the United States report that only about a quarter of students' argumentative essays reach a competent level (Crossley et al., 2024, citing the 2012 NAEP report). Teachers who want to help such students face a practical bottleneck: detailed feedback requires reading every essay closely, and a single class can produce several hundred discourse units per assignment.

Automated writing evaluation (AWE) systems have traditionally produced a holistic score for the whole essay. A holistic score tells the student how good the essay is, but not which part to revise. The PERSUADE 2.0 corpus (Crossley et al., 2024) makes a finer-grained task possible: each discourse unit of an essay has been rated by trained raters as Ineffective, Adequate or Effective. A model that predicts these ratings could point a teacher towards the units most likely to need attention.

The course frames every project as a support tool for a human teacher or learner, never as an automatic grader. This framing shapes the whole report: our output is a ranking of units for review, the human remains the decision-maker, and the main risk we study is a model that looks accurate on average while missing the weak units a teacher most needs to see.

## Problem statement, user and prediction time

Table 1.1 states the problem in the form required by the course: who uses the result, which decision it informs, what goes in and comes out, and when the prediction is made.

Table 1.1. Problem formulation.

| Element | Definition in this project |
|---|---|
| User | A teacher of English argumentative writing (grades 6–12) reviewing a set of submitted essays |
| Decision supported | Which discourse units to read and comment on first; whether a unit should be flagged as possibly ineffective |
| Unit of observation | One annotated discourse unit: a span of an essay with a discourse type (Lead, Position, Claim, Counterclaim, Rebuttal, Evidence, Concluding Statement) |
| Input | The unit text and its discourse type; for context levels, also neighbouring units, the paragraph, the prompt name, a source passage or the whole essay (Section 4.3.3) |
| Output | Probabilities for Ineffective, Adequate and Effective; a predicted label under an argmax rule or a teacher-chosen threshold on P(Ineffective) |
| Prediction time | After the essay is submitted and segmented into typed units. All inputs are available at that moment. Holistic scores, rater identities and demographic fields are not used as inputs |
| Target population | Essays like those in PERSUADE 2.0: U.S. students in grades 6–12, 15 prompts, independent and source-based tasks. Conclusions do not extend to other populations, languages or prompts without new evidence |
| What the tool must not do | Assign grades, replace teacher judgement, or use demographic attributes in its decision |

Figure 1.1 shows where the model sits in the teacher's workflow. Segmentation is taken from the human annotation in PERSUADE; a deployed system would need an upstream segmentation model, whose errors would propagate (Stab & Gurevych, 2017; Ding et al., 2023). This is a deliberate scope limit, stated again in Chapter 8.

![Figure 1.1. Intended use: the model ranks discourse units for a teacher's review; every feedback decision stays with the teacher.](figures/fig01_user_decision_workflow.png)

## Research questions

The project asks one main question and four sub-questions. Each sub-question has a pre-specified comparison and metric.

Main question. How well can a model predict the rater-assigned effectiveness of a discourse unit, on unseen essays from the same population, compared with simple and classical baselines, when every class matters?

- RQ1 (model families). On the same units and metrics, does a fine-tuned transformer (DeBERTa-v3-base) outperform a majority baseline and classical models (Logistic Regression, Random Forest) on Macro-F1 and on each class, especially Ineffective?
- RQ2 (controlled context check). Holding model, data split and training budget fixed, what does adding the neighbouring units (Level 1) add to the unit alone (Level 0), on the same units, per class and per discourse type? Do wider inputs (paragraph, source passage, whole essay) help further?
- RQ3 (prompt transfer). How much performance is lost when the prompt was never seen in training (leave-one-prompt-out), compared with an in-domain model scored on the same units?
- RQ4 (errors). Are errors associated with essay length, and if so, is that association explained by writer proficiency (holistic score) and class mix before any explanation in terms of missing context is offered? What do individual high-confidence failures show?

## Scope and contributions

The project does not propose a new architecture. DeBERTa on single units is the common starting point of the Kaggle Feedback Prize competition on this data (Crossley et al., 2024), so we treat it as a baseline, not as a contribution. Our contribution is a careful, reproducible evaluation:

1. a fair comparison of a majority baseline, an interpretable Logistic Regression, a Random Forest and DeBERTa on the same 29,102 validation units and the same 93,677 official test units, with per-class results and essay-level bootstrap intervals;
2. a controlled context ladder in which only the transformer input changes, analysed on the same units and per discourse type;
3. leave-one-prompt-out results kept separate from in-domain results, with an explicit map of which prompts each model covers;
4. an error analysis that first separates essay length from proficiency and class mix, then reads ten failure cases with recorded IDs;
5. a reproducibility package in which scripted checks trace every reported number back to the raw data and the saved per-unit predictions.

## Structure of the report

Chapter 2 reviews related work. Chapter 3 describes the data, the checks we ran on it and the exploratory analysis. Chapter 4 presents the models and the context representations. Chapter 5 gives the experimental protocol, including how the test set was used. Chapter 6 reports results. Chapter 7 analyses errors. Chapter 8 discusses what the results do and do not answer, and Chapter 9 concludes. The appendices contain the run table, reproduction instructions, individual contributions, the AI-use disclosure and supplementary tables.
