"""Pre-defined subgroup check (ELL status) for the locked L1 model, validation and official test.
ELL status is never a model input; it is used only to describe performance. Output: tables/R9_ell_subgroups.csv"""
import os
import pandas as pd
from common import EVID, P3, save, summary

u = pd.read_csv(os.path.join(EVID, "_units_slim.csv.gz"))
u["ell"] = u["ell_status"].fillna("missing").str.strip().replace({"": "missing"})
rows = []
for split, f in (("validation", "val_predictions_L1.csv"), ("test", "test_predictions_L1.csv")):
    p = pd.read_csv(os.path.join(P3, f))
    d = p.merge(u[u["split"] == ("test" if split == "test" else "validation")][["row_idx", "ell"]], on="row_idx")
    for g, s in d.groupby("ell"):
        m = summary(s["true_label"].to_numpy(), s["pred_label"].to_numpy())
        rows.append({"split": split, "ell_status": g, "units": len(s), "essays": s["essay_id_comp"].nunique(),
                     "gold %Ineff": round(100 * (s["true_label"] == 0).mean(), 2), "gold %Eff": round(100 * (s["true_label"] == 2).mean(), 2),
                     **{k: round(m[k], 4) for k in ("macro_f1", "accuracy", "f1_Ineffective", "recall_Ineffective", "precision_Ineffective", "f1_Adequate", "f1_Effective")}})
df = pd.DataFrame(rows)
save(df, "R9_ell_subgroups.csv")
print(df.to_string(index=False))
