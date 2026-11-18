# Conclusion and Recommendations

## Conclusion

This project asked how well a model can predict the rater-assigned effectiveness of each discourse unit in a student essay, and what information it needs. Using PERSUADE 2.0 with an essay-grouped split and a single locked pass on the official test, we found that:

1. a fine-tuned DeBERTa-v3-base model clearly outperforms a majority baseline and classical models on Macro-F1 and on both minority classes (test Macro-F1 0.577 against 0.510 and 0.297), but still recognises fewer than half of the Ineffective units;
2. adding the neighbouring units to the input gives a small, consistent improvement, largest for Ineffective units and for Claim, Counterclaim and Rebuttal (test +0.016 Macro-F1, +0.029 Ineffective F1), of the same order as run-to-run variation;
3. wider inputs did not help under the argmax rule; a whole-essay model separated the classes better after an equal calibration correction (+0.025 on validation), which supports, but does not establish, the hypothesis that unit effectiveness depends on the whole essay;
4. an unseen prompt costs the transformer up to 0.09 Macro-F1 on the same units;
5. errors rise with essay length partly because the class mix changes with proficiency and partly for reasons that remain after controlling for the holistic score and gold label; length must be separated from proficiency before errors are blamed on missing context.

## Recommendations within scope

For the intended user: use the model only to order a teacher's reading of submitted essays on prompts similar to the training prompts, never as a grade or a filter; choose the threshold on P(Ineffective) according to how many units the teacher can review, knowing the false-alarm cost in Table 6.8; and keep demographic attributes out of inputs and decision rules.

For anyone extending the work: test the whole-essay model with a pre-registered protocol and at least three seeds on a fresh confirmation set; obtain the full source texts for all seven source-based prompts before testing source context again; run LOPO for all fifteen prompts with the transformer; and evaluate with predicted rather than gold segmentation.

## Future work

The most informative next experiment is the one our results point to but cannot settle: whether whole-essay information improves the separation of Ineffective units once calibration is held equal. A second direction is the residual length effect, which could be tested by controlling unit length and truncation directly. A third is label uncertainty: training with the individual raters' labels, if they can be obtained, would allow the model to represent disagreement instead of a single consensus label (Romberg et al., 2025).
