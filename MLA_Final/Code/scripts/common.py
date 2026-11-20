"""Shared paths, loaders and metric helpers for the final-report scripts.

Every number used in FINAL_REPORT.md is produced either by these scripts (from the raw
PERSUADE 2.0 CSVs and the saved prediction files) or read from the outputs/ CSVs that the
original experiment scripts wrote. Nothing is typed in by hand.

Run from the repository root:  python final_report/scripts/01_data_checks_eda.py
"""
import os
import sys

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", ".."))

if os.path.exists(os.path.join(PKG_ROOT, "Results", "tables")):
    # MLA_Final self-contained root
    ROOT = PKG_ROOT
    TABLES = os.path.join(PKG_ROOT, "Results", "tables")
    FIGS = os.path.join(PKG_ROOT, "Results", "figures")
    EVID = os.path.join(PKG_ROOT, "Data", "samples")
    P3 = os.path.join(PKG_ROOT, "Results", "predictions")
    OUT = os.path.join(PKG_ROOT, "Results", "predictions")
    CTX = os.path.join(PKG_ROOT, "Results", "predictions")
    LOPO = os.path.join(PKG_ROOT, "Results", "predictions")
    TRAIN_CSV = os.path.join(PKG_ROOT, "Data", "persuade_corpus_2.0_train.csv")
    TEST_CSV = os.path.join(PKG_ROOT, "Data", "persuade_corpus_2.0_test.csv")
    if not os.path.exists(TRAIN_CSV):
        TRAIN_CSV = os.path.abspath(os.path.join(PKG_ROOT, "..", "data", "persuade_raw", "persuade_corpus_2.0_train.csv"))
        TEST_CSV = os.path.abspath(os.path.join(PKG_ROOT, "..", "data", "persuade_raw", "persuade_corpus_2.0_test.csv"))
else:
    ROOT = PKG_ROOT
    FR = os.path.join(ROOT, "final_report")
    TABLES = os.path.join(FR, "tables")
    FIGS = os.path.join(FR, "figures")
    EVID = os.path.join(FR, "evidence")
    TRAIN_CSV = os.path.join(ROOT, "data", "persuade_raw", "persuade_corpus_2.0_train.csv")
    TEST_CSV = os.path.join(ROOT, "data", "persuade_raw", "persuade_corpus_2.0_test.csv")
    P3 = os.path.join(ROOT, "Week11_Person3_DeBERTa_OfficialTest", "outputs", "week11_person3")
    OUT = os.path.join(ROOT, "outputs")
    CTX = os.path.join(ROOT, "week11_context_levels", "results")
    LOPO = os.path.join(ROOT, "week11_lopo_rerun", "outputs")

for d in (TABLES, FIGS, EVID):
    os.makedirs(d, exist_ok=True)

LABELS = ["Ineffective", "Adequate", "Effective"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
TYPES = ["Lead", "Position", "Claim", "Counterclaim", "Rebuttal", "Evidence", "Concluding Statement"]
QEDGES = [-np.inf, 315, 422, 566, np.inf]
QLABELS = ["Q1 (<=315)", "Q2 (316-422)", "Q3 (423-566)", "Q4 (>=567)"]

SOURCE_BASED = {  # PERSUADE 2.0: seven source-based (text-dependent) prompts
    "A Cowboy Who Rode the Waves", "Car-free cities", "Does the electoral college work?",
    "Exploring Venus", "Facial action coding system", "The Face on Mars", "Driverless cars",
}

RAW_COLS = ["essay_id", "essay_id_comp", "competition_set", "discourse_id", "discourse_start",
            "discourse_text", "discourse_type", "discourse_effectiveness", "holistic_essay_score",
            "prompt_name", "task", "grade_level", "ell_status", "essay_word_count", "source_text"]


def load_raw(path, cols=RAW_COLS):
    """Read the raw CSV as strings (no numeric coercion of IDs)."""
    df = pd.read_csv(path, usecols=cols, dtype=str, low_memory=False, keep_default_na=True)
    df["raw_record"] = np.arange(len(df))  # 0-based record number in the raw file
    return df


def annotated_units(raw):
    """Exactly the filtering rule of notebook 07 / all week-11 scripts:
    dropna(effectiveness, text) -> strip -> drop empty -> reset_index.  The new index is row_idx."""
    df = raw.dropna(subset=["discourse_effectiveness", "discourse_text"]).copy()
    df["discourse_text"] = df["discourse_text"].astype(str).str.strip()
    # the raw CSV stores one prompt as '"A Cowboy Who Rode the Waves"' (with quotes); prediction files drop them
    df["prompt_name"] = df["prompt_name"].str.strip().str.strip('"')
    df = df[df["discourse_text"].str.len() > 0].reset_index(drop=True)
    df["row_idx"] = np.arange(len(df))
    df["label"] = df["discourse_effectiveness"].map(LABEL2ID)
    df["holistic_essay_score"] = pd.to_numeric(df["holistic_essay_score"], errors="coerce")
    df["essay_word_count"] = pd.to_numeric(df["essay_word_count"], errors="coerce")
    df["unit_words"] = df["discourse_text"].str.split().str.len()
    df["length_q"] = pd.cut(df["essay_word_count"], QEDGES, labels=QLABELS)
    return df


# ---------------------------------------------------------------- metrics
def confusion(y, p, k=3):
    m = np.zeros((k, k), dtype=int)
    np.add.at(m, (np.asarray(y, int), np.asarray(p, int)), 1)
    return m


def per_class(y, p):
    m = confusion(y, p)
    out = {}
    for i, l in enumerate(LABELS):
        tp = m[i, i]
        prec = tp / m[:, i].sum() if m[:, i].sum() else 0.0
        rec = tp / m[i, :].sum() if m[i, :].sum() else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[l] = (prec, rec, f1, int(m[i, :].sum()))
    return out, m


def kappa(y, p, weights=None, k=3):
    m = confusion(y, p, k).astype(float)
    n = m.sum()
    i = np.arange(k)
    if weights == "quadratic":
        w = (i[:, None] - i[None, :]) ** 2 / (k - 1) ** 2
    else:
        w = (i[:, None] != i[None, :]).astype(float)
    exp = np.outer(m.sum(1), m.sum(0)) / n
    return 1 - (w * m).sum() / (w * exp).sum()


def summary(y, p):
    pc, m = per_class(y, p)
    f1s = [pc[l][2] for l in LABELS]
    recs = [pc[l][1] for l in LABELS]
    return {
        "n_units": int(len(y)),
        "macro_f1": float(np.mean(f1s)),
        "accuracy": float((np.asarray(y) == np.asarray(p)).mean()),
        "balanced_accuracy": float(np.mean(recs)),
        "kappa": float(kappa(y, p)),
        "qwk": float(kappa(y, p, "quadratic")),
        **{f"{c}_{l}": v for l in LABELS for c, v in zip(("precision", "recall", "f1", "support"), pc[l])},
    }


def macro_f1(y, p):
    pc, _ = per_class(y, p)
    return float(np.mean([pc[l][2] for l in LABELS]))


def essay_bootstrap_delta(df, col_a, col_b, n=2000, seed=42):
    """Paired essay-level bootstrap of Macro-F1(a) - Macro-F1(b); df needs essay_id_comp, label, col_a, col_b."""
    rng = np.random.default_rng(seed)
    groups = df.groupby("essay_id_comp").indices
    keys = list(groups)
    y = df["label"].to_numpy()
    a = df[col_a].to_numpy()
    b = df[col_b].to_numpy()
    deltas = []
    for _ in range(n):
        pick = rng.integers(0, len(keys), len(keys))
        idx = np.concatenate([groups[keys[j]] for j in pick])
        deltas.append(macro_f1(y[idx], a[idx]) - macro_f1(y[idx], b[idx]))
    d = np.array(deltas)
    return float(macro_f1(y, a) - macro_f1(y, b)), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def save(df, name):
    path = os.path.join(TABLES, name)
    df.to_csv(path, index=False, encoding="utf-8")
    return path
