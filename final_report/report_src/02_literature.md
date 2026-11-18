# Literature Review

This chapter reviews the work that shaped our design decisions. For each strand we state what it established and which choice in our project it supports. Table 2.1 at the end of the chapter maps sources to decisions.

## Argument structure and argument quality

Most annotation schemes for student argumentation descend from Toulmin's (1958) model, in which a claim is supported by data and warrants and may be qualified or rebutted. Stab and Gurevych (2014, 2017) operationalised a Toulmin-like scheme for persuasive essays (major claims, claims, premises and their relations) and showed that argument components and relations can be identified automatically with useful accuracy. Their corpus, however, is small, written by adult learners, and does not rate the quality of each component.

Argument quality is a harder and more subjective notion than argument structure. Wachsmuth et al. (2017) organised quality into logical (cogency), rhetorical (effectiveness) and dialectical (reasonableness) dimensions and showed that annotators agree only moderately on many of them. Two recent position papers sharpen this point. Wachsmuth et al. (2024) argue that the diversity of quality notions and the subjectivity of their perception are the main obstacles to progress, and that context and background knowledge are needed for reliable assessment. Romberg et al. (2025) review argument-quality datasets and argue that, because several valid assessments can coexist, aggregated labels hide genuine disagreement and models should be evaluated with this in mind. For our project this means that the effectiveness label is a measurement with limited reliability, not ground truth, and that model–rater agreement must not be read as if it were rater–rater agreement (Section 8.3).

Two further strands treat quality as dependent on information outside the argument. Deshpande et al. (2024) contextualise each argument with generated knowledge (feedback, hidden assumptions, a counter-argument) and report gains in-domain and zero-shot. Liu et al. (2024) assess whether premises are sufficient for a conclusion through a causal, counterfactual formulation. Both support the hypothesis we test in RQ2: a unit's quality may not be readable from the unit alone.

## PERSUADE and the Feedback Prize

The PERSUADE 1.0 corpus (Crossley et al., 2022) annotated more than 25,000 essays by U.S. students in grades 6–12 for seven discourse elements, closely following the Toulmin tradition but adding Lead and Concluding Statement. PERSUADE 2.0 (Crossley et al., 2024) adds a holistic score (1–6) for every essay and an effectiveness rating (Effective, Adequate, Ineffective) for every discourse element. Ratings were made by trained raters in a double-blind process, with a third rater adjudicating disagreements. Two facts from that paper are central to our work.

1. Reliability. On 159,228 segments where two raters' segmentations overlapped by at least 50%, exact agreement was 0.718 but Cohen's κ was only 0.316 overall and between 0.165 (Claim) and 0.432 (Evidence) by element (Crossley et al., 2024, Section 2.1 and Table 1). The holistic scores were far more reliable (weighted κ = 0.745).
2. The Kaggle competition. About 80% of the corpus was released for the Feedback Prize "Predicting Effective Arguments" competition; more than 1,500 teams took part. The winning models were least accurate on Ineffective elements, which were usually predicted as Adequate (Crossley et al., 2024, Section 3 and Figure 1).

Baffour et al. (2023) analysed the winning Feedback Prize models and found minimal demographic bias for discourse-element detection but moderate bias for effectiveness prediction, with differences by race/ethnicity, economic status and English-language-learner status. This motivates our pre-defined subgroup description in Section 6.6, and our decision never to use demographic attributes as inputs or as decision thresholds.

## Context, prompt and argument type in effectiveness prediction

The closest work to ours is Ding, Bexte and Horbach (2023), who used the Kaggle subset of PERSUADE (4,192 essays, 15 prompts). With gold spans as input, they added three kinds of information to a Logistic Regression on TF-IDF n-grams and to a fine-tuned BERT: the argument type, the prompt, and the whole essay as context. Each piece of information helped individually. For BERT, quadratic weighted kappa rose from 0.42 for the argument alone to 0.46 with the prompt and 0.47 with the whole essay; for Logistic Regression it rose from 0.41 to 0.50 with all three (Ding et al., 2023, Table 3). Their data were split by random sampling, so every prompt appears in training and evaluation, and they reported accuracy and QWK averaged over folds rather than per-class results. They also showed that a multi-task model that predicts span, type and quality jointly outperforms a pipeline that segments first.

Schaller et al. (2025) evaluated argument-mining models on artificially fragmented essays from PERSUADE and the German DARIUS corpus. Token-level sequence taggers that rely on whole-essay context degraded sharply when context was limited or misleading, while sentence-level classifiers were more stable. Their result is a caution for our context ladder: more context can help, but a model that depends on it becomes sensitive to how that context is presented.

Favero et al. (2025) fine-tuned and prompted small open-source large language models on the Feedback Prize effectiveness data. Fine-tuned models outperformed baselines on segmentation and type classification, while few-shot prompting for quality assessment only matched the baselines. The course rules exclude LLM prompting as a model family; we cite this work to position our transformer baseline, not to compare against it.

Stahl et al. (2024) released a German school-student essay corpus annotated for both argumentative structure and quality and showed that structure and quality interact. This supports treating discourse type as an input feature.

## Models used in this project

DeBERTa (He et al., 2021) improves BERT (Devlin et al., 2019) with disentangled attention over content and relative position. DeBERTa-v3 (He et al., 2023) adds ELECTRA-style replaced-token-detection pre-training and was the standard backbone among top Feedback Prize solutions. We use DeBERTa-v3-base for all transformer runs. Random Forests (Breiman, 2001) average many decision trees trained on bootstrap samples with random feature subsets; they handle sparse TF-IDF features, mixed feature types and non-linear interactions without scaling, but their individual predictions are hard to explain. Logistic Regression on TF-IDF features is a linear model whose weights can be read directly; it serves as our interpretable reference.

## Evaluation methodology

Because units from the same essay share a writer, a prompt and a writing occasion, they are not independent. Splitting, resampling and confidence intervals must therefore operate at the essay level, and preprocessing (TF-IDF vocabularies, scalers) must be fitted on training data only; the scikit-learn documentation on common pitfalls and on grouped cross-validation states both rules (Pedregosa et al., 2011). We use the non-parametric bootstrap (Efron & Tibshirani, 1993) with essays as the resampling unit and report a confidence interval for the paired difference between two systems, which addresses "A versus B" directly. Cohen's κ (Cohen, 1960) and its quadratic-weighted variant measure agreement corrected for chance; for an ordinal three-class label, QWK penalises Ineffective↔Effective confusions more than adjacent ones. Calibration of neural-network probabilities is discussed by Guo et al. (2017); it matters here because any threshold on P(Ineffective) assumes that probabilities are meaningful.

## Research gap

Table 2.1 summarises how the literature shaped our design. Three gaps motivated the project. First, published results on PERSUADE effectiveness rarely report per-class performance, even though the minority Ineffective class is the one a teacher most needs. Second, the claim that context helps has been tested by adding the whole essay at once (Ding et al., 2023); a controlled ladder that changes one input at a time, on the same units and with essay-level uncertainty, was not available. Third, prompt transfer and the confound between essay length, proficiency and label mix have not, to our knowledge, been examined together with context effects on this corpus.

Table 2.1. How the sources read supported specific design decisions.

| Source | Finding used | Decision in this project |
|---|---|---|
| Crossley et al. (2024) | Effectiveness κ = 0.316; Ineffective hardest for Kaggle models | Macro-F1 and per-class F1 as primary metrics; label reliability stated as a ceiling on interpretation |
| Crossley et al. (2022); Stab & Gurevych (2017) | Discourse elements follow a Toulmin-like scheme; segmentation is a separate, error-prone step | Gold segmentation and type used as given; end-to-end use left out of scope |
| Ding et al. (2023) | Type, prompt and whole-essay context each raise QWK | Discourse type always in the input; Prompt-Aware and whole-essay (L3) inputs tested |
| Schaller et al. (2025) | Context-dependent models degrade when context is limited | Context added one step at a time; Level 0 kept as a control |
| Baffour et al. (2023) | Moderate demographic bias in effectiveness models | Demographics never used as input; ELL described as a pre-defined subgroup |
| Wachsmuth et al. (2017, 2024); Romberg et al. (2025) | Argument quality is subjective and context-dependent | Model–rater κ not compared with rater–rater κ; conclusions limited to "agreement with adjudicated labels" |
| Deshpande et al. (2024); Liu et al. (2024) | Quality may depend on knowledge outside the argument | Source passage (L2) and whole essay (L3) tested as hypotheses, not assumed |
| He et al. (2023) | DeBERTa-v3 is a strong encoder for this data | DeBERTa-v3-base as the transformer family |
| Pedregosa et al. (2011); Efron & Tibshirani (1993) | Fit preprocessing on training data; resample at the group level | Essay-grouped split; essay-level paired bootstrap |
