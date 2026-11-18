"""Recompute every main result directly from the saved per-unit predictions.

Answers post-interview feedback items 2 and 3 with tables that report per-class results next to Macro-F1,
compare Level 0 and Level 1 on the same units, and keep in-domain and leave-one-prompt-out results apart.

Outputs: final_report/tables/R*.csv, final_report/evidence/results_log.txt
Run (repo root, ~1 min):  python final_report/scripts/02_results_from_predictions.py
"""
import io
import os

import numpy as np
import pandas as pd

from common import (CTX, EVID, LABELS, LOPO, OUT, P3, QLABELS, TYPES, confusion, save, summary)

log = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=log)


units = pd.read_csv(os.path.join(EVID, "_units_slim.csv.gz"))
tv = units[units["split"] != "test"].set_index("row_idx")
te = units[units["split"] == "test"].set_index("row_idx")


def load_pred(path, ref=None):
    p = pd.read_csv(path)
    if "row_idx" not in p.columns:
        p["row_idx"] = ref
    if p["pred_label"].dtype == object:
        p["pred_label"] = p["pred_label"].map({l: i for i, l in enumerate(LABELS)})
    return p.set_index("row_idx")["pred_label"].astype(int)


vref = pd.read_csv(os.path.join(P3, "val_predictions_L1.csv"))["row_idx"].to_numpy()
rf_val = pd.read_csv(os.path.join(OUT, "strongest_baseline_predictions.csv"))
rf_val = pd.Series(rf_val["discourse_effectiveness_pred"].map({l: i for i, l in enumerate(LABELS)}).to_numpy(), index=vref)

VAL = {
    "Majority class (always Adequate)": pd.Series(1, index=vref),
    "Random Forest, Feature Set B (wk 9)": rf_val,
    "DeBERTa-v3 L0, unit only (wk 11)": load_pred(os.path.join(P3, "val_predictions_L0.csv")),
    "DeBERTa-v3 L1, +-1 unit (wk 11, locked)": load_pred(os.path.join(P3, "val_predictions_L1.csv")),
    "DeBERTa-v3 Prompt-Aware (wk 11)": load_pred(os.path.join(P3, "val_predictions_PA.csv")),
    "DeBERTa-v3 L1 +-2 units (supp.)": load_pred(os.path.join(CTX, "L1w2", "out_L1w2", "val_predictions_L1w2.csv")),
    "DeBERTa-v3 L1 paragraph (supp.)": load_pred(os.path.join(CTX, "L1para", "out_L1para", "val_predictions_L1para.csv")),
    "DeBERTa-v3 L2 source passage (supp.)": load_pred(os.path.join(CTX, "L2", "out_L2", "val_predictions_L2.csv")),
    "DeBERTa-v3 L3 whole essay, 3 ep (supp.)": load_pred(os.path.join(CTX, "L3", "out_L3", "val_predictions_L3.csv")),
    "DeBERTa-v3 L3 whole essay, 7 ep (supp.)": load_pred(os.path.join(CTX, "L3_7ep", "out_L3_7ep", "val_predictions_L3_7ep.csv")),
}
TEST = {
    "Majority class (always Adequate)": pd.Series(1, index=te.index),
    "Random Forest, Feature Set B": load_pred(os.path.join(OUT, "test_predictions_rf_feature_set_b.csv")),
    "DeBERTa-v3 L0, unit only": load_pred(os.path.join(P3, "test_predictions_L0.csv")),
    "DeBERTa-v3 L1, +-1 unit (locked)": load_pred(os.path.join(P3, "test_predictions_L1.csv")),
    "DeBERTa-v3 Prompt-Aware (exploratory)": load_pred(os.path.join(P3, "test_predictions_PA.csv")),
}


def table(models, ref, split):
    rows = []
    for name, pred in models.items():
        pred = pred.reindex(ref.index)
        s = summary(ref["label"].to_numpy(), pred.to_numpy())
        rows.append({"split": split, "system": name, **{k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()}})
    return pd.DataFrame(rows)


r1 = table(VAL, tv.loc[vref], "validation (29,102 units / 3,119 essays)")
r2 = table(TEST, te, "official test (93,677 units / 10,402 essays)")
save(r1, "R1_validation_per_class.csv")
save(r2, "R2_test_per_class.csv")
cols = ["system", "macro_f1", "accuracy", "balanced_accuracy", "qwk", "f1_Ineffective", "precision_Ineffective",
        "recall_Ineffective", "f1_Adequate", "f1_Effective", "recall_Effective"]
say("R1 validation\n" + r1[cols].to_string(index=False))
say("\nR2 official test\n" + r2[cols].to_string(index=False))

# confusion matrices
cms = []
for split, models, ref in (("validation", VAL, tv.loc[vref]), ("test", TEST, te)):
    for name, pred in models.items():
        m = confusion(ref["label"].to_numpy(), pred.reindex(ref.index).to_numpy())
        for i, g in enumerate(LABELS):
            cms.append({"split": split, "system": name, "gold": g, **{f"pred_{p}": int(m[i, j]) for j, p in enumerate(LABELS)}})
save(pd.DataFrame(cms), "R3_confusion_matrices.csv")


# ---------------------------------------------------------------- L0 vs L1 on the same units
def essay_counts(df, col):
    """per-essay 3x3 confusion counts -> array (n_essays, 9)"""
    code = df["label"].to_numpy() * 3 + df[col].to_numpy()
    e = pd.factorize(df["essay_id_comp"])[0]
    out = np.zeros((e.max() + 1, 9))
    np.add.at(out, (e, code), 1)
    return out


def f1_from_counts(c):
    m = c.reshape(-1, 3, 3)
    tp = np.stack([m[:, i, i] for i in range(3)], 1)
    prec = tp / np.maximum(m.sum(1), 1e-12)
    rec = tp / np.maximum(m.sum(2), 1e-12)
    f1 = np.where(prec + rec > 0, 2 * prec * rec / np.maximum(prec + rec, 1e-12), 0)
    return f1  # (B, 3)


def paired_boot(df, a, b, n=2000, seed=42):
    ca, cb = essay_counts(df, a), essay_counts(df, b)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(ca), (n, len(ca)))
    W = np.zeros((n, len(ca)))
    np.add.at(W, (np.repeat(np.arange(n), len(ca)), idx.ravel()), 1)
    fa, fb = f1_from_counts(W @ ca), f1_from_counts(W @ cb)
    pa, pb = f1_from_counts(ca.sum(0, keepdims=True))[0], f1_from_counts(cb.sum(0, keepdims=True))[0]
    res = {}
    for k, nm in enumerate(LABELS):
        d = fa[:, k] - fb[:, k]
        res[f"F1 {nm}"] = (pa[k] - pb[k], *np.percentile(d, [2.5, 97.5]))
    d = fa.mean(1) - fb.mean(1)
    res["Macro-F1"] = (pa.mean() - pb.mean(), *np.percentile(d, [2.5, 97.5]))
    return res


rows, trans = [], []
for split, ref, l0, l1 in (("validation", tv.loc[vref], VAL["DeBERTa-v3 L0, unit only (wk 11)"], VAL["DeBERTa-v3 L1, +-1 unit (wk 11, locked)"]),
                           ("test", te, TEST["DeBERTa-v3 L0, unit only"], TEST["DeBERTa-v3 L1, +-1 unit (locked)"])):
    d = ref.copy()
    d["L0"], d["L1"] = l0.reindex(d.index).to_numpy(), l1.reindex(d.index).to_numpy()
    for k, (pt, lo, hi) in paired_boot(d, "L1", "L0").items():
        rows.append({"split": split, "metric": k, "L1_minus_L0": round(pt, 4), "ci95_low": round(lo, 4), "ci95_high": round(hi, 4)})
    c0, c1 = d["L0"] == d["label"], d["L1"] == d["label"]
    trans.append({"split": split, "units": len(d), "same_prediction": int((d["L0"] == d["L1"]).sum()),
                  "prediction_changed": int((d["L0"] != d["L1"]).sum()),
                  "both_correct": int((c0 & c1).sum()), "L0_wrong_L1_correct": int((~c0 & c1).sum()),
                  "L0_correct_L1_wrong": int((c0 & ~c1).sum()), "both_wrong": int((~c0 & ~c1).sum()),
                  "gold_Ineff_fixed_by_L1": int(((d["label"] == 0) & ~c0 & c1).sum()),
                  "gold_Ineff_lost_by_L1": int(((d["label"] == 0) & c0 & ~c1).sum())})
    # transition matrix of predictions
    tm = pd.crosstab(d["L0"].map(dict(enumerate(LABELS))), d["L1"].map(dict(enumerate(LABELS))))
    tm.to_csv(os.path.join(os.path.dirname(EVID), "tables", f"R4c_L0_to_L1_prediction_transition_{split}.csv"))
    say(f"\nL0 -> L1 prediction transitions ({split}); rows L0, cols L1\n" + tm.to_string())
    # per discourse type
    for t in TYPES:
        s = d[d["discourse_type"] == t]
        s0, s1 = summary(s["label"].to_numpy(), s["L0"].to_numpy()), summary(s["label"].to_numpy(), s["L1"].to_numpy())
        trans.append  # noqa (kept for clarity)
        rows.append({"split": split, "metric": f"[{t}] Macro-F1 (n={len(s)}, Ineff n={int((s['label'] == 0).sum())})",
                     "L1_minus_L0": round(s1["macro_f1"] - s0["macro_f1"], 4), "ci95_low": None, "ci95_high": None,
                     "L0": round(s0["macro_f1"], 4), "L1": round(s1["macro_f1"], 4),
                     "L0_F1_Ineff": round(s0["f1_Ineffective"], 4), "L1_F1_Ineff": round(s1["f1_Ineffective"], 4)})
r4 = pd.DataFrame(rows)
r4b = pd.DataFrame(trans)
save(r4, "R4a_L1_vs_L0_same_units_deltas.csv")
save(r4b, "R4b_L1_vs_L0_paired_outcomes.csv")
say("\nR4a L1 - L0 on the same units (essay bootstrap, 2,000)\n" + r4.to_string(index=False))
say("\nR4b paired outcomes\n" + r4b.to_string(index=False))

# ---------------------------------------------------------------- LOPO vs in-domain, per class, same units
rows = []
l0v = VAL["DeBERTa-v3 L0, unit only (wk 11)"]
for f, pr in ((1, "A Cowboy Who Rode the Waves"), (2, "Summer projects"), (3, "Distance learning")):
    lp = load_pred(os.path.join(LOPO, f"predictions_fold{f}.csv"))
    allu = tv.loc[lp.index]
    s_all = summary(allu["label"].to_numpy(), lp.to_numpy())
    same = tv.loc[vref]
    same = same[same["prompt_name"] == pr]
    s_lopo = summary(same["label"].to_numpy(), lp.reindex(same.index).to_numpy())
    s_in = summary(same["label"].to_numpy(), l0v.reindex(same.index).to_numpy())
    for nm, s, units_desc in (("LOPO DeBERTa L0, all units of held-out prompt", s_all, f"{len(allu)} units / {allu['essay_id_comp'].nunique()} essays"),
                              ("LOPO DeBERTa L0, validation essays of that prompt", s_lopo, f"{len(same)} / {same['essay_id_comp'].nunique()}"),
                              ("In-domain DeBERTa L0 (wk 11), same validation essays", s_in, f"{len(same)} / {same['essay_id_comp'].nunique()}")):
        rows.append({"held_out_prompt": pr, "setting": nm, "units/essays": units_desc,
                     "gold %Ineff": round(100 * (allu if 'all' in nm else same)["label"].eq(0).mean(), 2),
                     **{k: round(s[k], 4) for k in ("macro_f1", "accuracy", "f1_Ineffective", "recall_Ineffective", "f1_Adequate", "f1_Effective")}})
r5 = pd.DataFrame(rows)
save(r5, "R5_lopo_vs_indomain_per_class.csv")
say("\nR5 LOPO vs in-domain (per class)\n" + r5.to_string(index=False))

# ---------------------------------------------------------------- per-type, L1 test
rows = []
lt = TEST["DeBERTa-v3 L1, +-1 unit (locked)"]
rft = TEST["Random Forest, Feature Set B"]
for t in TYPES:
    s = te[te["discourse_type"] == t]
    a, b = summary(s["label"].to_numpy(), lt.reindex(s.index).to_numpy()), summary(s["label"].to_numpy(), rft.reindex(s.index).to_numpy())
    rows.append({"discourse_type": t, "units": len(s), "gold Ineff": int(s["label"].eq(0).sum()),
                 "L1 Macro-F1": round(a["macro_f1"], 4), "L1 F1 Ineff": round(a["f1_Ineffective"], 4), "L1 F1 Adeq": round(a["f1_Adequate"], 4), "L1 F1 Eff": round(a["f1_Effective"], 4),
                 "RF Macro-F1": round(b["macro_f1"], 4), "RF F1 Ineff": round(b["f1_Ineffective"], 4)})
r6 = pd.DataFrame(rows)
save(r6, "R6_test_by_discourse_type.csv")
say("\nR6 test by type\n" + r6.to_string(index=False))

# ---------------------------------------------------------------- errors by length quartile (L1, val+test) incl. error composition
rows = []
for split, ref, pred in (("validation", tv.loc[vref], VAL["DeBERTa-v3 L1, +-1 unit (wk 11, locked)"]), ("test", te, lt)):
    d = ref.assign(p=pred.reindex(ref.index).to_numpy())
    for q in QLABELS:
        s = d[d["length_q"] == q]
        err = s[s["p"] != s["label"]]
        ae = err[(err["label"] != 0) & (err["p"] != 0)]
        rows.append({"split": split, "length_quartile": q, "units": len(s), "essays": s["essay_id_comp"].nunique(),
                     "error_rate_pct": round(100 * len(err) / len(s), 1),
                     "errors_Adequate_vs_Effective_pct": round(100 * len(ae) / len(err), 1),
                     "errors_involving_Ineffective_pct": round(100 * (len(err) - len(ae)) / len(err), 1),
                     "gold_Ineff_pct": round(100 * s["label"].eq(0).mean(), 2), "gold_Eff_pct": round(100 * s["label"].eq(2).mean(), 2),
                     **{f"F1 {l}": round(summary(s['label'].to_numpy(), s['p'].to_numpy())[f'f1_{l}'], 3) for l in LABELS},
                     "Macro-F1": round(summary(s['label'].to_numpy(), s['p'].to_numpy())['macro_f1'], 3)})
r7 = pd.DataFrame(rows)
save(r7, "R7_L1_errors_by_length_quartile.csv")
say("\nR7 L1 errors by length quartile\n" + r7.to_string(index=False))

with open(os.path.join(EVID, "results_log.txt"), "w", encoding="utf-8") as f:
    f.write(log.getvalue())
