"""Locate the ten studied Ineffective failure cases in the raw data and assemble one table with IDs,
labels, predictions of every context level, and the group's recorded reading of each case.

Selection rule (fixed in week 9, before any context model existed): the ten gold-Ineffective validation
units that the week-9 DeBERTa L0 model mis-classified with the highest confidence (max of P(Adequate),
P(Effective) above 0.94). Readings are copied from the week-10/11 reports (group's own reading).
Output: final_report/tables/R8_ten_cases.csv
"""
import os

import pandas as pd

from common import OUT, TRAIN_CSV, annotated_units, load_raw, save, P3

cases = pd.read_csv(os.path.join(OUT, "context_ablation_case_study_recheck.csv"))
levels = pd.read_csv(os.path.join(OUT, "context_levels_10_cases.csv"))
tr = annotated_units(load_raw(TRAIN_CSV))
val_idx = pd.read_csv(os.path.join(P3, "val_predictions_L1.csv"))["row_idx"].to_numpy()
val = tr.loc[val_idx]

READING = {
    1: ("Whole essay", "Counterclaim that is never answered later in the essay; the unit alone reads as a fluent sentence."),
    2: ("Unit itself", "Accurate quotation of source paragraph 36, followed by off-topic reasoning (learner's permit, driving test) that does not support the point."),
    3: ("Unit itself", "Bare stance with no reason; eight words."),
    4: ("Unit itself", "Sentence fragment; no opposing argument is actually stated."),
    5: ("Source / task", "Vague position that may conflict with the source article; cannot be judged without the source."),
    6: ("Whole essay", "Counterclaim with no rebuttal anywhere in the essay."),
    7: ("Task / prompt", "Thesis whose scope is unclear relative to the prompt."),
    8: ("Local context", "Unsupported prediction; neighbouring units do not supply a reason."),
    9: ("Task / prompt", "Generic hook that does not engage the prompt."),
    10: ("Unit itself", "Claim with no support and a garbled reason."),
}
rows = []
for _, c in cases.iterrows():
    hit = val.index[val["discourse_text"].str.startswith(c["target_snippet"].strip()) & (val["discourse_type"] == c["discourse_type"])]
    assert len(hit) == 1, (c["case_id"], len(hit))
    u = tr.loc[hit[0]]
    lv = levels.set_index("case").loc[c["case_id"]]
    rows.append({
        "case": int(c["case_id"]), "row_idx": int(hit[0]), "essay_id_comp": u["essay_id_comp"], "prompt": u["prompt_name"],
        "type": u["discourse_type"], "gold": u["discourse_effectiveness"], "holistic_score": int(u["holistic_essay_score"]),
        "essay_words": int(u["essay_word_count"]), "unit_words": int(u["unit_words"]),
        "text_excerpt": u["discourse_text"][:110].replace("\n", " ") + ("..." if len(u["discourse_text"]) > 110 else ""),
        "wk9-10 L0 pred / P(Ineff)": f"{c['week9_pred'][:4]} / {c['week9_p_ineff']:.3f}",
        "wk10 L1 pred / P(Ineff)": f"{c['level1_pred'][:4]} / {c['level1_p_ineff']:.3f}",
        "wk11 L1 P(Ineff)": lv["P_ineff_L1"], "PA": lv["P_ineff_PA"], "L1+-2": lv["P_ineff_L1w2"], "paragraph": lv["P_ineff_L1para"],
        "L2 source": lv["P_ineff_L2"], "L3 3ep": lv["P_ineff_L3"], "L3 7ep": lv["P_ineff_L3_7ep"],
        "levels_predicting_Ineffective": ", ".join(k for k, col in (("paragraph", "pred_L1para"), ("L2", "pred_L2"), ("L3 3ep", "pred_L3"), ("L3 7ep", "pred_L3_7ep")) if lv[col] == "Ineff") or "none",
        "information_needed (group reading)": READING[int(c["case_id"])][0],
        "observation (group reading)": READING[int(c["case_id"])][1],
    })
df = pd.DataFrame(rows)
save(df, "R8_ten_cases.csv")
print(df.drop(columns=["observation (group reading)"]).to_string(index=False))
