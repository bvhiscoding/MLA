"""Interpretable reference model: Logistic Regression on Feature Set B, fitted on the training split only,
evaluated on validation only (argmax, no threshold tuning). Added for the final report (15 Nov 2026).

Feature Set B is rebuilt exactly as in 01_Data_Pipeline_Classical_Baseline.py:
  word 1-2-gram TF-IDF (max 15,000 features, min_df 2, sublinear tf) + one-hot discourse type
  + 5 standardised structural features (unit characters, unit words, essay words, relative start position,
    unit/essay length ratio).  Every transformer is fitted on the training split only.
Outputs: tables/L1_lr_validation.csv, tables/L2_lr_top_features.csv, tables/L3_lr_case8_contributions.csv
"""
import os

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common import LABELS, P3, TRAIN_CSV, annotated_units, load_raw, save, summary

raw = load_raw(TRAIN_CSV, cols=["essay_id", "essay_id_comp", "competition_set", "discourse_id", "discourse_start",
                                "discourse_text", "discourse_type", "discourse_effectiveness", "holistic_essay_score",
                                "prompt_name", "task", "grade_level", "ell_status", "essay_word_count", "source_text", "full_text"])
u = annotated_units(raw)
val_idx = pd.read_csv(os.path.join(P3, "val_predictions_L1.csv"))["row_idx"].to_numpy()
is_val = np.zeros(len(u), bool); is_val[val_idx] = True
trn, val = u[~is_val], u.loc[val_idx]


def struct(df):
    t = df["discourse_text"].fillna("")
    full = df["full_text"].fillna("")
    char_len = t.str.len().to_numpy(float)
    wc = t.str.split().str.len().fillna(0).to_numpy(float)
    ewc = df["essay_word_count"].fillna(pd.Series(wc, index=df.index)).to_numpy(float)
    pos = np.clip(pd.to_numeric(df["discourse_start"], errors="coerce").fillna(0).to_numpy(float) / np.clip(full.str.len().to_numpy(float), 1, None), 0, 1)
    ratio = np.clip(wc / np.clip(ewc, 1, None), 0, 1)
    return np.c_[char_len, wc, ewc, pos, ratio]


SNAMES = ["unit characters", "unit words", "essay words", "relative start position", "unit/essay length ratio"]
tf = TfidfVectorizer(max_features=15000, min_df=2, ngram_range=(1, 2), sublinear_tf=True)
oh = OneHotEncoder(sparse_output=True, handle_unknown="ignore")
sc = StandardScaler()
Xtr = sp.hstack([tf.fit_transform(trn["discourse_text"]), oh.fit_transform(trn[["discourse_type"]]), sp.csr_matrix(sc.fit_transform(struct(trn)))], format="csr")
Xva = sp.hstack([tf.transform(val["discourse_text"]), oh.transform(val[["discourse_type"]]), sp.csr_matrix(sc.transform(struct(val)))], format="csr")
names = list(tf.get_feature_names_out()) + [f"type={c}" for c in oh.categories_[0]] + SNAMES

lr = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced", random_state=42)
lr.fit(Xtr, trn["label"].to_numpy())
assert list(lr.classes_) == [0, 1, 2]  # integer labels 0=Ineffective,1=Adequate,2=Effective -> no alphabetical trap
pred = lr.predict(Xva)
s = summary(val["label"].to_numpy(), pred)
save(pd.DataFrame([{"system": "Logistic Regression, Feature Set B (balanced, argmax; fit on train, scored on validation)",
                    **{k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()}}]), "L1_lr_validation.csv")
print({k: round(v, 4) for k, v in s.items() if isinstance(v, float)})

rows = []
for k, l in enumerate(LABELS):
    co = lr.coef_[k] - lr.coef_.mean(0)  # contrast against the average class
    top = np.argsort(co)[::-1][:12]
    rows += [{"class": l, "rank": r + 1, "feature": names[j], "weight_vs_mean": round(float(co[j]), 3)} for r, j in enumerate(top)]
save(pd.DataFrame(rows), "L2_lr_top_features.csv")
print(pd.DataFrame(rows).groupby("class")["feature"].apply(lambda s: ", ".join(s[:8])).to_string())

# trace case 8 (row_idx 108613): logit(Ineffective) - logit(Adequate) decomposed into feature contributions
pos = int(np.where(val_idx == 108613)[0][0])
x = Xva[pos].toarray().ravel()
p = lr.predict_proba(Xva[pos])[0]
diff = (lr.coef_[0] - lr.coef_[1]) * x
nz = np.argsort(np.abs(diff))[::-1]
rows = [{"feature": names[j], "value": round(float(x[j]), 3), "contribution_to_logit(Ineff)-logit(Adeq)": round(float(diff[j]), 3)} for j in nz[:12] if diff[j] != 0]
rows.append({"feature": "intercept difference", "value": None, "contribution_to_logit(Ineff)-logit(Adeq)": round(float(lr.intercept_[0] - lr.intercept_[1]), 3)})
rows.append({"feature": "TOTAL logit(Ineff)-logit(Adeq)", "value": None, "contribution_to_logit(Ineff)-logit(Adeq)": round(float(diff.sum() + lr.intercept_[0] - lr.intercept_[1]), 3)})
rows.append({"feature": f"P(Ineff/Adeq/Eff) = {p[0]:.3f}/{p[1]:.3f}/{p[2]:.3f}; prediction = {LABELS[int(np.argmax(p))]}", "value": None, "contribution_to_logit(Ineff)-logit(Adeq)": None})
save(pd.DataFrame(rows), "L3_lr_case8_contributions.csv")
print(pd.DataFrame(rows).to_string(index=False))
