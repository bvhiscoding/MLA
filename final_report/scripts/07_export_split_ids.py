"""Export clean train / validation / test assignments keyed by intact identifiers.

`outputs/split_assignments.csv` is keyed by `essay_id`, which the spreadsheet-altered CSV stores in rounded
scientific notation (e.g. 5.40889E+12). This script re-derives the same split from the saved predictions
(validation = row_idx values in val_predictions_L1.csv) and writes it keyed by `essay_id_comp` and `row_idx`.

Outputs
  final_report/tables/split_essays.csv       essay_id_comp, split, n_units, prompt_name
  final_report/tables/split_units.csv.gz     row_idx, essay_id_comp, discourse_type, split   (no text)
Run (repo root, ~30 s):  python final_report/scripts/07_export_split_ids.py
"""
import os

import numpy as np
import pandas as pd

from common import P3, TABLES, TEST_CSV, TRAIN_CSV, annotated_units, load_raw

COLS = ["essay_id", "essay_id_comp", "discourse_text", "discourse_type", "discourse_effectiveness",
        "prompt_name", "holistic_essay_score", "essay_word_count"]

tr = annotated_units(load_raw(TRAIN_CSV, cols=COLS))
te = annotated_units(load_raw(TEST_CSV, cols=COLS))
val_idx = pd.read_csv(os.path.join(P3, "val_predictions_L1.csv"))["row_idx"].to_numpy()
is_val = np.zeros(len(tr), bool)
is_val[val_idx] = True
tr["split"] = np.where(is_val, "validation", "train")
te["split"] = "test"

units = pd.concat([tr, te], ignore_index=True)[["split", "row_idx", "essay_id_comp", "discourse_type", "prompt_name"]]
essays = (units.groupby(["essay_id_comp", "split"], as_index=False)
          .agg(n_units=("row_idx", "size"), prompt_name=("prompt_name", "first")))

# ---- checks
counts = units.groupby("split").agg(units=("row_idx", "size"), essays=("essay_id_comp", "nunique"))
expected = {"train": (115187, 12475), "validation": (29102, 3119), "test": (93677, 10402)}
for s, (u, e) in expected.items():
    assert (counts.loc[s, "units"], counts.loc[s, "essays"]) == (u, e), (s, counts.loc[s].tolist())
assert essays["essay_id_comp"].is_unique, "an essay appears in more than one split"
for s in ("train", "validation"):
    assert units.loc[units["split"] == s, "prompt_name"].nunique() == 15, s
# row_idx is unique within each source file (train file: train+validation; test file: test)
assert units.loc[units["split"] != "test", "row_idx"].is_unique and units.loc[units["split"] == "test", "row_idx"].is_unique

essays.sort_values(["split", "essay_id_comp"]).to_csv(os.path.join(TABLES, "split_essays.csv"), index=False)
units[["row_idx", "essay_id_comp", "discourse_type", "split"]].to_csv(
    os.path.join(TABLES, "split_units.csv.gz"), index=False, compression="gzip")
print(counts.to_string())
print("Note: row_idx counts from 0 separately in the training file (train + validation) and in the test file.")
print("Wrote tables/split_essays.csv and tables/split_units.csv.gz; all checks passed.")
