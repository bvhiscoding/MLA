# Methods

Figure 4.1 gives an overview of the modelling pipeline. Two model families from the course are compared against a trivial baseline: classical models on engineered sparse features (Logistic Regression and Random Forest) and a fine-tuned transformer encoder (DeBERTa-v3-base). Changing hyperparameters within one family is not counted as a second family.

![Figure 4.1. Modelling pipeline. All feature transformers are fitted on the training split only; all systems are evaluated on the same units with the same metrics.](figures/fig03_ml_pipeline.png)

## Baseline

The majority-class baseline predicts Adequate for every unit. It needs no training and sets the floor that any useful model must beat on Macro-F1 (0.294 on validation, 0.297 on test). Its accuracy (78.7% and 80.5%) shows why accuracy cannot be the headline metric.

## Classical family: features, Logistic Regression and Random Forest

### Feature Set B

Both classical models use Feature Set B (FS-B), defined in `01_Data_Pipeline_Classical_Baseline.py`:

1. word unigram and bigram TF-IDF of the unit text (at most 15,000 features, minimum document frequency 2, sublinear term frequency);
2. a one-hot encoding of the discourse type (7 columns);
3. five structural features, standardised: unit length in characters, unit length in words, essay length in words, relative start position of the unit in the essay, and the ratio of unit length to essay length.

The TF-IDF vocabulary, the one-hot encoder and the scaler are fitted on the 115,187 training units only and then applied to validation and test units. All FS-B features are available at prediction time. Note that essay length is itself a feature; given the strong association between essay length and proficiency (Section 3.7.4), the classical models can exploit proficiency indirectly.

### Logistic Regression (interpretable reference)

Multinomial Logistic Regression models the class probabilities as a softmax of linear scores, P(y = k | x) ∝ exp(w_k · x + b_k), and is fitted by minimising the cross-entropy loss with L2 regularisation (C = 1). Its assumptions are that the log-odds between classes are linear in the features and that units are conditionally independent given the features. We use class weights inversely proportional to class frequency so that errors on the rare Ineffective class cost more. The model is interpretable: the contribution of each feature to the score of each class is its weight times its value.

Table 4.1 shows the trace of case 8 through a Logistic Regression refitted for this report on the training split (scikit-learn, argmax decision; validation Macro-F1 0.489, matching the original classical benchmark, 0.488). The words "kids will", "ask", "parents" and "kids" push the unit towards Adequate rather than Ineffective, the short unit and the Claim type push slightly the same way, and the total log-odds of Ineffective versus Adequate is −2.87, giving P(Ineffective) = 0.052. The weights are lexical: nothing in the model can represent that the claim lacks a reason.

Table 4.1. Logistic Regression trace for case 8: the largest contributions to logit(Ineffective) − logit(Adequate) (table L3).

| Feature | Value (TF-IDF or standardised) | Contribution |
|---|---:|---:|
| "kids will" | 0.378 | −0.785 |
| "ask" | 0.216 | −0.567 |
| "parents" | 0.249 | −0.484 |
| "kids" | 0.216 | −0.471 |
| "there parents" | 0.410 | −0.341 |
| "school" | 0.147 | −0.292 |
| "some kids" | 0.331 | +0.245 |
| unit/essay length ratio | −0.511 | −0.239 |
| type = Claim | 1 | −0.232 |
| unit characters | −0.787 | −0.222 |
| Intercept difference | — | +0.798 |
| Total log-odds (all features) | — | −2.870 |

The largest positive weights for Ineffective (relative to the average class) include "witch", "plant", "aliens", "venus" and "story" (table L2). These are topic words of particular prompts with many Ineffective units ("The Face on Mars", "Exploring Venus"), which confirms that a lexical model partly learns prompt priors rather than argument quality. This is one motivation for the prompt-transfer experiment.

### Random Forest

The Random Forest (Breiman, 2001) averages 200 decision trees (maximum depth 35, minimum 5 samples per split, `class_weight = "balanced"`, seed 42), each trained on a bootstrap sample with a random subset of features at each split. It makes no linearity assumption and captures interactions such as "short unit and Position type", at the cost of interpretability. It was the strongest classical model on validation (Macro-F1 0.523, against 0.509 for Logistic Regression with thresholds tuned on validation and 0.487 for LightGBM) and is the classical system in the test protocol. Figure 4.2 shows a what-if trace for case 8: correcting the spelling, adding a reason or lengthening the essay lowers P(Ineffective); re-typing the unit as Evidence raises it; no single change flips the prediction from Adequate.

![Figure 4.2. Random Forest what-if trace for case 8 (row_idx 108613): P(Ineffective) after one controlled change to the input. The prediction stays Adequate in every case.](figures/fig27_rf_what_if_case8.png)

### Linear SVM (supplementary)

A linear support vector machine on word TF-IDF features was run as a supplementary classical system on the official test and on the three LOPO folds. It belongs to the same linear family as Logistic Regression and is reported for completeness only.

## Transformer family: DeBERTa-v3-base

### Architecture and loss

DeBERTa-v3-base (He et al., 2023) is a 12-layer transformer encoder with disentangled attention over content and relative position, pre-trained with replaced-token detection. We add a linear classification head on the first-token representation and fine-tune all weights. The model maps an input text to three logits; the softmax of the logits gives the class probabilities. Training minimises class-weighted cross-entropy,

$$\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\,\log p_\theta(y_i \mid x_i), \qquad w_k = \frac{N}{3\,N_k},$$

where N_k is the number of training units of class k. On the training split this gives w = (7.48, 0.43, 1.95) for Ineffective, Adequate and Effective. The weights trade accuracy on the majority class for recall on the minority classes; they also shift the predicted probabilities away from the true base rates, which is why probabilities are not used as calibrated risks without checking (Section 6.7).

### Why this model suits the data

The label depends on meaning (relevance to the position, soundness of reasons) rather than on surface words, and the input is natural text of 10–300 words. A pre-trained encoder brings knowledge of syntax and semantics that a bag-of-n-grams model lacks, and it can read the unit together with its context in a single input. Its assumptions are that the pre-trained representation transfers to student writing and that units are exchangeable given their input text. Its costs are a GPU requirement, sensitivity to the training run (Section 6.7), and opaque predictions.

### Context representations

The context ladder changes only the text that the encoder reads. Figure 4.3 shows the variants and Table 4.2 defines them. Level 0 and Level 1 form the planned comparison; the other inputs are supplementary.

![Figure 4.3. Context representations used in the transformer experiments. Solid boxes: protocol systems scored on the official test (L0, L1) and the exploratory Prompt-Aware system; dashed boxes: supplementary validation-only runs.](figures/fig04_context_levels.png)

Table 4.2. Inputs of the context ladder. All variants use the same split, model, optimiser and epoch selection unless stated.

| Level | Input to the encoder | What it adds over the previous level | Status |
|---|---|---|---|
| L0 | `type [SEP] unit` | — (unit alone) | Protocol, scored on test |
| L1 | `type [SEP] Previous: u(j−1) [SEP] Target: u(j) [SEP] Next: u(j+1)`; `[NONE]` at essay boundaries | The immediately preceding and following units of the same essay | Protocol, locked, scored on test |
| Prompt-Aware (PA) | `Prompt: <prompt name> [SEP]` + L1 input | The task the essay responds to | Exploratory, scored on test |
| L1 ±2 | Two units on each side, each capped at 600 characters | A wider local window | Validation only |
| Paragraph | Target, then the whole paragraph containing it with the target marked « … » | The paragraph as a unit of thought | Validation only |
| L2 | Most similar passage of the source text (TF-IDF retrieval, ≤ 90 words) + L1 input | The reading the student was asked to use | Validation only; 4 of 7 source-based prompts (full text for 2, a summary for 2); other prompts keep the L1 input |
| L3 | The whole essay with typed markers around every unit, up to 1,536 tokens; each unit represented by the mean of its token states; one forward pass per essay | The whole argument (e.g. whether a counterclaim is ever answered) | Validation only; 3-epoch and 7-epoch runs |

What Level 1 adds to Level 0. Level 1 gives the model the two units that physically surround the target in the essay. For a Claim, the previous unit is often the Position or another Claim and the next is often its Evidence; for a Counterclaim, the next unit is often the Rebuttal. Level 1 can therefore show whether a claim is followed by support or a counterclaim by an answer when that support or answer is adjacent. It cannot show anything that lies further away, such as a rebuttal three paragraphs later or the content of the source article. The comparison of L0 and L1 is made on exactly the same units, splits and training budget (Section 6.2).

### Training configuration

Table 4.3 lists the configuration of the runs that were scored on the official test. The supplementary runs used the same configuration on an L4 GPU, except where Table 4.2 states otherwise.

Table 4.3. DeBERTa training configuration (`Week11_Person3_DeBERTa_OfficialTest/outputs/week11_person3/run_metadata.json`).

| Setting | Value |
|---|---|
| Backbone | microsoft/deberta-v3-base |
| Maximum input length | 512 tokens (L3: 1,536) |
| Batch | 8 per device × 4 gradient-accumulation steps = 32 |
| Optimiser and schedule | AdamW, learning rate 2 × 10⁻⁵, linear schedule with 10% warm-up |
| Epochs and selection | 3 epochs; checkpoint with the best validation Macro-F1 |
| Loss | Class-weighted cross-entropy, weights 7.48 / 0.43 / 1.95 |
| Seed | 42 |
| Precision and hardware | bf16 on one NVIDIA A100 40 GB (Google Colab); supplementary runs on L4 |
| Software | Python 3.13, PyTorch 2.11, transformers 4.57.6 (version 5.x did not train DeBERTa-v3 correctly) |

## Model selection

All model choices were made on the validation split: the feature set and classical model, the decision to drop a BERT + DeBERTa ensemble, the epoch of each DeBERTa run, and the choice of Level 1 as the locked system. Level 1 was locked because of its higher Ineffective F1 on validation (+0.019), not because its Macro-F1 was clearly higher: in the first training run, L1 − L0 was +0.002 with a confidence interval containing zero. The official test played no part in any choice (Section 5.5).
