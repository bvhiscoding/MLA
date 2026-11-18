"""All data figures of the final report (PNG, 300 dpi, Times New Roman).

Inputs: final_report/tables/*.csv (from scripts 01-03), outputs/*.csv (original experiment outputs),
        VAN_DAP_4_TIEU_CHI/trace_mau_that/outputs/rf_what_if_case8.csv (case-8 trace).
Run (repo root):  python final_report/scripts/04_figures.py
"""
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from common import EVID, FIGS, LABELS, OUT, QLABELS, ROOT, TABLES, TYPES, summary

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10, "figure.dpi": 110,
    "savefig.dpi": 300, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#555555", "axes.linewidth": 0.8, "grid.color": "#dddddd", "grid.linewidth": 0.6,
    "axes.axisbelow": True, "mathtext.fontset": "stix",
})
# Fixed class colours (validated categorical slots 2,1,3 of the reference palette; all-pairs CVD-safe)
CC = {"Ineffective": "#eb6834", "Adequate": "#2a78d6", "Effective": "#1baf7a"}
INK, MUTED, HILITE = "#222222", "#8a8a8a", "#2a78d6"
T = lambda n: pd.read_csv(os.path.join(TABLES, n))
O = lambda n: pd.read_csv(os.path.join(OUT, n))


def save(fig, name):
    fig.savefig(os.path.join(FIGS, name), facecolor="white")
    plt.close(fig)
    print("saved", name)


def stacked_h(ax, df, labelcol, title=None, annotate_min=4.0, nfmt=None):
    left = np.zeros(len(df))
    y = np.arange(len(df))
    for l in LABELS:
        v = df[f"% {l}"].to_numpy()
        ax.barh(y, v, left=left, color=CC[l], edgecolor="white", linewidth=1.2, height=0.72, label=l)
        for yi, (lv, vv) in enumerate(zip(left, v)):
            if vv >= annotate_min:
                ax.text(lv + vv / 2, yi, f"{vv:.1f}", ha="center", va="center", fontsize=8.5,
                        color="white" if l != "Effective" else INK)
        left += v
    ax.set_yticks(y)
    ax.set_yticklabels(df[labelcol] if nfmt is None else [nfmt(r) for _, r in df.iterrows()])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of units (%)")
    ax.invert_yaxis()
    if title:
        ax.set_title(title, loc="left")
    ax.grid(axis="x")


units = pd.read_csv(os.path.join(EVID, "_units_slim.csv.gz"))

# ---------------------------------------------------------------- F05 label distribution by split
e1 = T("E1_split_label_distribution.csv")
fig, ax = plt.subplots(figsize=(7.2, 2.6))
stacked_h(ax, e1, "split", nfmt=lambda r: f"{r['split']}  (n={int(r['units']):,})", annotate_min=3)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.32), frameon=False)
save(fig, "fig05_label_distribution_by_split.png")

# ---------------------------------------------------------------- F06 type x label
e2 = T("E2_type_label_mix_trainval.csv").sort_values("% Ineffective", ascending=False)
fig, ax = plt.subplots(figsize=(7.2, 3.4))
stacked_h(ax, e2, "discourse_type", nfmt=lambda r: f"{r['discourse_type']}  (n={int(r['units']):,})", annotate_min=3)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
save(fig, "fig06_label_mix_by_discourse_type.png")

# ---------------------------------------------------------------- F07 prompt x label
e3 = T("E3_prompt_label_mix_trainval.csv").sort_values("% Ineffective", ascending=False)
fig, ax = plt.subplots(figsize=(7.4, 5.6))
stacked_h(ax, e3, "prompt_name",
          nfmt=lambda r: f"{r['prompt_name']}{' *' if r['task'] == 'Text dependent' else ''}  (n={int(r['units']):,})", annotate_min=4)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.09), frameon=False)
ax.text(0, -0.2, "* source-based (text-dependent) prompt; all others are independent prompts. Train + validation units.",
        transform=ax.transAxes, fontsize=9, color="#444444")
save(fig, "fig07_label_mix_by_prompt.png")

# ---------------------------------------------------------------- F08 unit length by label
fig, ax = plt.subplots(figsize=(6.4, 3.4))
data = [units.loc[units["label"] == i, "unit_words"].clip(lower=1) for i in range(3)]
bp = ax.boxplot(data, vert=False, widths=0.55, patch_artist=True, showfliers=False,
                medianprops=dict(color=INK, linewidth=1.4))
for patch, l in zip(bp["boxes"], LABELS):
    patch.set_facecolor(CC[l]); patch.set_alpha(0.85); patch.set_edgecolor("white")
ax.set_xscale("log")
ax.set_xticks([5, 10, 20, 50, 100, 200, 400]); ax.set_xticklabels([5, 10, 20, 50, 100, 200, 400])
ax.set_yticks([1, 2, 3]); ax.set_yticklabels([f"{l}\n(median {int(np.median(d))} words)" for l, d in zip(LABELS, data)])
ax.set_xlabel("Words in the discourse unit (log scale; whiskers 1.5 IQR, outliers hidden)")
ax.grid(axis="x")
save(fig, "fig08_unit_length_by_label.png")

# ---------------------------------------------------------------- F09 essay length vs holistic score
ess = units.drop_duplicates("essay_id_comp")
from scipy.stats import spearmanr
rho = spearmanr(ess["essay_word_count"], ess["holistic_essay_score"])[0]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
d = [ess.loc[ess["holistic_essay_score"] == s, "essay_word_count"] for s in range(1, 7)]
bp = ax.boxplot(d, widths=0.55, patch_artist=True, showfliers=False, medianprops=dict(color=INK, linewidth=1.4))
for p in bp["boxes"]:
    p.set_facecolor("#cfdcf0"); p.set_edgecolor("#4a6fa5")
for q in (315, 422, 566):
    ax.axhline(q, color=MUTED, linestyle="--", linewidth=0.8)
    ax.text(6.62, q, f"{q}", va="center", fontsize=8.5, color="#555555")
ax.set_xticklabels([f"{s}\n(n={len(x):,})" for s, x in zip(range(1, 7), d)])
ax.set_xlabel("Holistic essay score (1-6), essays in all splits")
ax.set_ylabel("Essay length (words)")
ax.set_title(f"Spearman rho = {rho:.2f} between essay length and holistic score (n = {len(ess):,} essays)", loc="left", fontsize=11)
ax.text(1.02, 0.02, "dashed: length-\nquartile cut points", transform=ax.transAxes, fontsize=8.5, color="#555555")
ax.grid(axis="y")
save(fig, "fig09_essay_length_vs_holistic_score.png")

# ---------------------------------------------------------------- F10 label mix by score and by length quartile
a, b = T("E6a_label_mix_by_holistic_score.csv"), T("E6b_label_mix_by_length_quartile.csv")
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"wspace": 0.55})
a["lab"] = a.apply(lambda r: f"Score {int(r['holistic_essay_score'])} (n={int(r['units']):,})", axis=1)
stacked_h(axs[0], a, "lab", title="(a) by holistic score", annotate_min=5)
b["lab"] = b.apply(lambda r: f"{r['length_q']}\nmean score {r['mean holistic score (per essay)']:.2f}", axis=1)
stacked_h(axs[1], b, "lab", title="(b) by essay-length quartile", annotate_min=5)
axs[0].legend(ncol=3, loc="upper center", bbox_to_anchor=(1.25, -0.2), frameon=False)
save(fig, "fig10_label_mix_by_score_and_length.png")

# ---------------------------------------------------------------- F11 within-score class mix by length
c = T("E6c_label_mix_score_x_length.csv")
fig, axs = plt.subplots(1, 4, figsize=(10, 2.9), sharey=False)
for ax, s in zip(axs, (2, 3, 4, 5)):
    x = c[c["holistic_essay_score"] == s]
    qi = [QLABELS.index(q) for q in x["length_q"]]
    ax.plot(qi, x["% Ineffective"], "-o", color=CC["Ineffective"], markersize=5, linewidth=1.8, label="% Ineffective")
    ax.plot(qi, x["% Effective"], "-s", color=CC["Effective"], markersize=5, linewidth=1.8, label="% Effective")
    ax.set_xticks(range(4)); ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4"])
    ax.set_title(f"Holistic score {s}", fontsize=11)
    ax.set_ylim(0, max(45, x[["% Ineffective", "% Effective"]].max().max() + 5)); ax.grid(axis="y")
axs[0].set_ylabel("Share of units (%)")
axs[0].legend(loc="upper left", frameon=False, fontsize=9)
fig.text(0.5, -0.04, "Essay-length quartile (cells with at least 200 units; train + validation)", ha="center")
save(fig, "fig11_label_mix_within_score_by_length.png")

# ---------------------------------------------------------------- F12 per-class results, validation and test
r1, r2 = T("R1_validation_per_class.csv"), T("R2_test_per_class.csv")
short = {"Majority class (always Adequate)": "Majority", "Random Forest, Feature Set B (wk 9)": "RF (FS-B)",
         "Random Forest, Feature Set B": "RF (FS-B)", "DeBERTa-v3 L0, unit only (wk 11)": "DeBERTa\nL0",
         "DeBERTa-v3 L0, unit only": "DeBERTa\nL0", "DeBERTa-v3 L1, +-1 unit (wk 11, locked)": "DeBERTa\nL1 (locked)",
         "DeBERTa-v3 L1, +-1 unit (locked)": "DeBERTa\nL1 (locked)", "DeBERTa-v3 Prompt-Aware (wk 11)": "Prompt-\nAware",
         "DeBERTa-v3 Prompt-Aware (exploratory)": "Prompt-\nAware"}
fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.0), sharey=True)
for ax, r, ttl in ((axs[0], r1, "(a) Validation, 29,102 units"), (axs[1], r2, "(b) Official test, 93,677 units (one pass)")):
    r = r[r["system"].isin(short)].reset_index(drop=True)
    x = np.arange(len(r)); w = 0.25
    for k, l in enumerate(LABELS):
        ax.bar(x + (k - 1) * w, r[f"f1_{l}"], w * 0.92, color=CC[l], label=f"F1 {l}")
    ax.scatter(x, r["macro_f1"], marker="D", s=34, color=INK, zorder=5, label="Macro-F1")
    for xi, m in zip(x, r["macro_f1"]):
        ax.text(xi, 1.05, f"{m:.3f}", ha="center", fontsize=9, color=INK)
    ax.set_xticks(x); ax.set_xticklabels([short[s] for s in r["system"]], fontsize=9.5)
    ax.set_title(ttl, loc="left", pad=16); ax.set_ylim(0, 1.1); ax.set_yticks(np.arange(0, 1.01, 0.2)); ax.grid(axis="y")
    ax.text(-0.45, 1.05, "Macro-F1:", ha="right", fontsize=9, color=INK)
axs[0].set_ylabel("F1 score")
axs[0].legend(ncol=4, loc="upper center", bbox_to_anchor=(1.05, -0.2), frameon=False)
save(fig, "fig12_per_class_results_val_test.png")

# ---------------------------------------------------------------- F13 confusion matrices on test
cm = T("R3_confusion_matrices.csv")
sel = ["Random Forest, Feature Set B", "DeBERTa-v3 L0, unit only", "DeBERTa-v3 L1, +-1 unit (locked)"]
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.3))
for ax, s in zip(axs, sel):
    m = cm[(cm["split"] == "test") & (cm["system"] == s)][[f"pred_{l}" for l in LABELS]].to_numpy()
    rn = m / m.sum(1, keepdims=True)
    ax.imshow(rn, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{m[i, j]:,}\n{rn[i, j]:.0%}", ha="center", va="center", fontsize=8.5,
                    color="white" if rn[i, j] > 0.55 else INK)
    ax.set_xticks(range(3)); ax.set_xticklabels(["Ineff", "Adeq", "Eff"])
    ax.set_yticks(range(3)); ax.set_yticklabels(["Ineff", "Adeq", "Eff"])
    ax.set_xlabel("Predicted"); ax.set_title(short[s].replace("\n", " "), fontsize=11)
    for sp in ax.spines.values():
        sp.set_visible(False)
axs[0].set_ylabel("Gold label")
save(fig, "fig13_confusion_matrices_test.png")

# ---------------------------------------------------------------- F14 L1 - L0 per class, same units
r4 = T("R4a_L1_vs_L0_same_units_deltas.csv")
r4 = r4[r4["ci95_low"].notna()]
fig, ax = plt.subplots(figsize=(6.6, 3.2))
metrics = ["Macro-F1", "F1 Ineffective", "F1 Adequate", "F1 Effective"]
for k, (split, col, off) in enumerate((("validation", "#7f7f7f", -0.13), ("test", HILITE, 0.13))):
    s = r4[r4["split"] == split].set_index("metric").loc[metrics]
    y = np.arange(len(metrics)) + off
    ax.errorbar(s["L1_minus_L0"], y, xerr=[s["L1_minus_L0"] - s["ci95_low"], s["ci95_high"] - s["L1_minus_L0"]],
                fmt="o", color=col, ecolor=col, capsize=3, markersize=6, linewidth=1.5,
                label=f"{split} ({'29,102' if split == 'validation' else '93,677'} units)")
ax.axvline(0, color=INK, linewidth=0.9)
ax.set_yticks(range(len(metrics))); ax.set_yticklabels(metrics); ax.invert_yaxis()
ax.set_xlabel("Level 1 minus Level 0 (95% essay-bootstrap CI, 2,000 resamples)")
ax.legend(frameon=False, loc="lower right"); ax.grid(axis="x")
save(fig, "fig14_L1_minus_L0_per_class.png")

# ---------------------------------------------------------------- F15 official-test paired comparisons
bt = pd.read_csv(os.path.join(ROOT, "Week11_Person3_DeBERTa_OfficialTest", "outputs", "official_test_deberta_bootstrap.csv"))
rf = O("official_test_bootstrap_deberta_vs_rf.csv")
print(bt.columns.tolist())
rows = []
for _, r in bt.iterrows():
    vals = [v for v in r.values]
    rows.append(vals)
print(bt.to_string())
comp = []
for _, r in rf.iterrows():
    comp.append((r["So sánh"].replace("−", "-"), r["delta_macro_f1"], r["ci95_low"], r["ci95_high"]))
name_col = bt.columns[0]
dcol = [c for c in bt.columns if "delta" in c.lower() or "Δ" in c][0]
lcol = [c for c in bt.columns if "low" in c.lower()][0]
hcol = [c for c in bt.columns if "high" in c.lower()][0]
for _, r in bt.iterrows():
    comp.append((str(r[name_col]).replace("−", "-"), r[dcol], r[lcol], r[hcol]))
comp = pd.DataFrame(comp, columns=["c", "d", "lo", "hi"]).drop_duplicates("c")
order = ["L0 - RF", "L1 - RF", "PA - RF", "L1 - L0", "PA - L0", "PA - L1"]
comp["key"] = comp["c"].str.extract(r"(PA|L1|L0)\s*-\s*(RF|L0|L1)").agg(" - ".join, axis=1)
comp = comp.set_index("key").reindex([o for o in order if o in set(comp["key"])])
fig, ax = plt.subplots(figsize=(6.6, 3.0))
y = np.arange(len(comp))
cols = [HILITE if lo > 0 else MUTED for lo in comp["lo"]]
for yi, (d_, lo, hi, cc) in enumerate(zip(comp["d"], comp["lo"], comp["hi"], cols)):
    ax.plot([lo, hi], [yi, yi], color=cc, linewidth=2)
    ax.plot(d_, yi, "o", color=cc, markersize=7)
    ax.text(hi + 0.002, yi, f"{d_:+.4f} [{lo:+.4f}, {hi:+.4f}]", va="center", fontsize=8.8)
ax.axvline(0, color=INK, linewidth=0.9)
ax.set_yticks(y); ax.set_yticklabels(comp.index); ax.invert_yaxis()
ax.set_xlim(-0.01, 0.115)
ax.set_xlabel("Difference in Macro-F1 on the official test (95% paired essay-bootstrap CI)")
ax.grid(axis="x")
save(fig, "fig15_official_test_paired_bootstrap.png")

# ---------------------------------------------------------------- F16 LOPO / in-domain coverage map
lc = O("lopo_classical_results.csv")
lc = lc[lc["level"] == "overall"].copy()
lc["held_out_prompt"] = lc["held_out_prompt"].str.strip('"')
svm = O("lopo_svm_baseline_results.csv").set_index("held_out_prompt")["macro_f1"]
dl = O("lopo_deberta_rerun_results.csv").set_index("held_out_prompt")["macro_f1"]
prompts = lc.sort_values("macro_f1")["held_out_prompt"].tolist()
cols_ = ["RF (FS-B)\nin-domain", "DeBERTa L0/L1/PA\nin-domain", "RF (FS-B)\nLOPO", "Linear SVM\nLOPO", "DeBERTa L0\nLOPO (rerun)"]
M = np.full((len(prompts), len(cols_)), np.nan)
txt = [["" for _ in cols_] for _ in prompts]
for i, p in enumerate(prompts):
    M[i, 0] = M[i, 1] = 0.0
    txt[i][0] = txt[i][1] = "val + test"
    M[i, 2] = lc.set_index("held_out_prompt").loc[p, "macro_f1"]; txt[i][2] = f"{M[i, 2]:.3f}"
    if p in svm.index:
        M[i, 3] = svm[p]; txt[i][3] = f"{svm[p]:.3f}"
    if p in dl.index:
        M[i, 4] = dl[p]; txt[i][4] = f"{dl[p]:.3f}"
fig, ax = plt.subplots(figsize=(8.4, 6.0))
for i in range(len(prompts)):
    for j in range(len(cols_)):
        if j < 2:
            fc = "#e6eef9"
        elif np.isnan(M[i, j]):
            fc = "#f4f4f4"
        else:
            fc = plt.cm.Oranges(0.25 + 0.6 * (0.55 - M[i, j]) / 0.25)
        ax.add_patch(plt.Rectangle((j, i), 0.96, 0.92, color=fc))
        ax.text(j + 0.48, i + 0.46, txt[i][j] if txt[i][j] else "not run", ha="center", va="center",
                fontsize=8.6, color=INK if txt[i][j] else "#9a9a9a")
ax.set_xlim(0, len(cols_)); ax.set_ylim(len(prompts), 0)
ax.set_xticks(np.arange(len(cols_)) + 0.48); ax.set_xticklabels(cols_, fontsize=9)
ax.xaxis.tick_top()
ax.set_yticks(np.arange(len(prompts)) + 0.46); ax.set_yticklabels(prompts, fontsize=9.5)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.tick_params(length=0)
ax.axvline(2, color=INK, linewidth=1.2)
ax.text(1, len(prompts) + 0.7, "In-domain: prompt seen in training\n(scores reported over all prompts, not per prompt)", ha="center", va="top", fontsize=9)
ax.text(3.5, len(prompts) + 0.7, "Leave-one-prompt-out: Macro-F1 on all units of the held-out prompt\n(darker = lower)", ha="center", va="top", fontsize=9)
save(fig, "fig16_prompt_coverage_indomain_vs_lopo.png")

# ---------------------------------------------------------------- F17 LOPO vs in-domain on same units
g = O("lopo_deberta_rerun_gap_same_units.csv")
fig, ax = plt.subplots(figsize=(6.8, 2.8))
for i, r in g.iterrows():
    ax.plot([r["lopo_macro_f1_same_units"], r["indomain_w11_macro_f1"]], [i, i], color=MUTED, linewidth=2, zorder=1)
    ax.scatter(r["indomain_w11_macro_f1"], i, color=HILITE, s=55, zorder=2, label="In-domain DeBERTa L0" if i == 0 else None)
    ax.scatter(r["lopo_macro_f1_same_units"], i, color=CC["Ineffective"], s=55, zorder=2, label="LOPO DeBERTa L0 (prompt unseen)" if i == 0 else None)
    ax.text(0.595, i, f"gap {r['gap_lopo_minus_w11']:+.3f} {r['gap_w11_ci95']}", va="center", fontsize=9)
ax.set_yticks(range(len(g)))
ax.set_yticklabels([f"{p}\n({n:,} units / {e} essays)" for p, n, e in zip(g["held_out_prompt"], g["n_units_same_set"], g["n_essays"])], fontsize=9.5)
ax.invert_yaxis(); ax.set_xlim(0.36, 0.75)
ax.set_xlabel("Macro-F1 on the same validation essays of the held-out prompt")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.3), ncol=2); ax.grid(axis="x")
save(fig, "fig17_lopo_vs_indomain_same_units.png")

# ---------------------------------------------------------------- F18 RF LOPO 15 prompts
lc2 = lc.sort_values("macro_f1")
fig, ax = plt.subplots(figsize=(7.0, 4.6))
chosen = {"A Cowboy Who Rode the Waves", "Summer projects", "Distance learning"}
ax.barh(range(len(lc2)), lc2["macro_f1"], color=[HILITE if p in chosen else "#b9c7da" for p in lc2["held_out_prompt"]], height=0.7)
for i, v in enumerate(lc2["macro_f1"]):
    ax.text(v + 0.004, i, f"{v:.3f}", va="center", fontsize=8.5)
ax.set_yticks(range(len(lc2))); ax.set_yticklabels(lc2["held_out_prompt"], fontsize=9.5)
ax.axvline(lc2["macro_f1"].mean(), color=INK, linestyle="--", linewidth=0.9)
ax.text(lc2["macro_f1"].mean() + 0.003, len(lc2) - 0.4, f"mean {lc2['macro_f1'].mean():.3f}", fontsize=9)
ax.set_xlabel("Random Forest (Feature Set B) Macro-F1 on the held-out prompt")
ax.set_xlim(0.3, 0.56); ax.grid(axis="x")
ax.legend(handles=[Patch(color=HILITE, label="selected for DeBERTa LOPO (hardest, median, easiest)")], frameon=False, loc="lower right", fontsize=9)
save(fig, "fig18_rf_lopo_15_prompts.png")

# ---------------------------------------------------------------- F19 context ladder
cl = O("context_levels_validation_summary.csv")
pb = O("context_levels_posthoc_bias_ensemble.csv").set_index("system")
names = {"L0": "L0 unit only", "PA": "Prompt-Aware", "L1w2": "L1 +-2 units", "L1para": "Paragraph",
         "L2": "L2 source passage", "L3": "L3 whole essay, 3 ep", "L3_7ep": "L3 whole essay, 7 ep"}
order = ["L0", "PA", "L1w2", "L1para", "L2", "L3", "L3_7ep"]


def parse_ci(s):
    a = re.findall(r"[-+]?\d*\.\d+", s)
    return float(a[0]), float(a[1])


fig, axs = plt.subplots(1, 2, figsize=(10.2, 3.6), sharey=True)
for ax, (ttl, src) in zip(axs, (("(a) argmax decision (as trained)", "argmax"), ("(b) after the same cross-fitted class-offset correction", "bias"))):
    for i, k in enumerate(order):
        if src == "argmax":
            r = cl.set_index("model").loc[k]; d_ = r["delta_vs_L1"]; lo, hi = parse_ci(r["ci95_vs_L1"])
        else:
            r = pb.loc[k]; d_ = r["delta_vs_L1_bias"]; lo, hi = parse_ci(r["ci95_vs_L1_bias"])
        cc = HILITE if lo > 0 else (CC["Ineffective"] if hi < 0 else MUTED)
        ax.plot([lo, hi], [i, i], color=cc, linewidth=2); ax.plot(d_, i, "o", color=cc, markersize=6)
        ax.text(0.047, i, f"{d_:+.4f}", va="center", fontsize=8.8)
    ax.axvline(0, color=INK, linewidth=0.9); ax.set_xlim(-0.03, 0.058)
    ax.set_title(ttl, loc="left", fontsize=11); ax.grid(axis="x")
    ax.set_xlabel("Macro-F1 difference vs. L1 (95% essay-bootstrap CI)")
axs[0].set_yticks(range(len(order))); axs[0].set_yticklabels([names[k] for k in order]); axs[0].invert_yaxis()
fig.text(0.01, -0.05, "Validation only (29,102 units), trained after the official test pass; none of these models was scored on the test. "
         "Blue: CI above 0; orange: CI below 0; grey: CI contains 0.", fontsize=9)
save(fig, "fig19_context_ladder_validation.png")

# ---------------------------------------------------------------- F20 within-score error by length
h = O("holistic_score_x_length_quartile_error_rates.csv")
h = h[h["model"].str.startswith("DeBERTa L1 (tu") & h["model"].str.contains("11")]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.5), sharey=True)
scol = {2: "#9b9b9b", 3: HILITE, 4: CC["Ineffective"], 5: CC["Effective"]}
for ax, split, ttl in ((axs[0], "validation", "(a) Validation (decisions made here)"), (axs[1], "official_test", "(b) Official test (descriptive only)")):
    for s in (2, 3, 4, 5):
        x = h[(h["split"] == split) & (h["holistic_essay_score"] == s) & (h["n_units"] >= 200)]
        if x.empty:
            continue
        qi = np.array([QLABELS.index(q) for q in x["length_quartile"]]) + (s - 3.5) * 0.06
        ax.errorbar(qi, x["error_rate_pct"], yerr=[x["error_rate_pct"] - x["ci95_low_pct"], x["ci95_high_pct"] - x["error_rate_pct"]],
                    fmt="-o", color=scol[s], capsize=2.5, markersize=4.5, linewidth=1.6, label=f"holistic score {s}")
    ax.set_xticks(range(4)); ax.set_xticklabels(QLABELS, fontsize=9)
    ax.set_title(ttl, loc="left", fontsize=11); ax.grid(axis="y")
axs[0].set_ylabel("Error rate of DeBERTa L1 (%)")
axs[0].legend(frameon=False, fontsize=9, ncol=2, loc="upper left")
fig.text(0.01, -0.06, "Cells with at least 200 units; 95% CI from 1,000 essay-level bootstrap resamples. Quartile cut points fixed on validation.", fontsize=9)
save(fig, "fig20_error_within_score_by_length.png")

# ---------------------------------------------------------------- F21 error composition and per-class F1 by length
r7 = T("R7_L1_errors_by_length_quartile.csv")
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4))
v = r7[r7["split"] == "validation"]
x = np.arange(4)
ax = axs[0]
ae = v["error_rate_pct"] * v["errors_Adequate_vs_Effective_pct"] / 100
ie = v["error_rate_pct"] - ae
ax.bar(x, ie, color=CC["Ineffective"], width=0.6, label="errors involving Ineffective", edgecolor="white")
ax.bar(x, ae, bottom=ie, color=HILITE, width=0.6, label="Adequate <-> Effective confusions", edgecolor="white")
for xi, t_, a_ in zip(x, v["error_rate_pct"], v["errors_Adequate_vs_Effective_pct"]):
    ax.text(xi, t_ + 0.6, f"{t_:.1f}%\n({a_:.0f}% A<->E)", ha="center", fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels(QLABELS, fontsize=9); ax.set_ylim(0, 38)
ax.set_ylabel("Error rate (%)"); ax.set_title("(a) L1 error rate and its composition (validation)", loc="left", fontsize=11)
ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y")
ax = axs[1]
for l, mk in zip(LABELS, ("o", "s", "^")):
    ax.plot(x, v[f"F1 {l}"], "-" + mk, color=CC[l], linewidth=1.8, markersize=5, label=f"F1 {l}")
ax.plot(x, v["Macro-F1"], "--D", color=INK, linewidth=1.4, markersize=4.5, label="Macro-F1")
ax.set_xticks(x); ax.set_xticklabels(QLABELS, fontsize=9); ax.set_ylim(0, 1)
ax.set_title("(b) per-class F1 of L1 by length quartile (validation)", loc="left", fontsize=11)
ax.legend(frameon=False, fontsize=9, ncol=2, loc="lower left"); ax.grid(axis="y")
save(fig, "fig21_error_composition_by_length.png")

# ---------------------------------------------------------------- F22 threshold trade-off
th = O("ineffective_threshold_tuning_table.csv")
th = th[th["model"].str.contains("11")].copy()
th["theta"] = th["rule"].str.extract(r">=\s*([\d.]+)").astype(float)
arg = th[th["rule"] == "argmax"].iloc[0]
th = th.dropna(subset=["theta"]).sort_values("theta")
fig, ax = plt.subplots(figsize=(6.8, 3.6))
ax.plot(th["theta"], th["ineff_recall_pct"] / 100, "-o", color=CC["Ineffective"], markersize=4, label="Recall (Ineffective)")
ax.plot(th["theta"], th["ineff_precision_pct"] / 100, "-s", color=HILITE, markersize=4, label="Precision (Ineffective)")
ax.plot(th["theta"], th["macro_f1"], "-D", color=INK, markersize=4, label="Macro-F1")
for yv, cc in ((arg["ineff_recall_pct"] / 100, CC["Ineffective"]), (arg["ineff_precision_pct"] / 100, HILITE), (arg["macro_f1"], INK)):
    ax.axhline(yv, color=cc, linestyle=":", linewidth=0.9)
ax.text(0.505, arg["macro_f1"] + 0.012, "dotted: argmax rule", fontsize=8.5, ha="right")
ax.set_xlabel("Decision threshold on P(Ineffective)"); ax.set_ylabel("Value (validation)")
ax.set_ylim(0, 0.85); ax.grid(axis="y"); ax.legend(frameon=False, fontsize=9, loc="upper right")
save(fig, "fig22_threshold_tradeoff.png")

# ---------------------------------------------------------------- F23 ten cases across context levels
tc = T("R8_ten_cases.csv")
lv = [("wk11 L1 P(Ineff)", "L1"), ("PA", "Prompt-\nAware"), ("L1+-2", "L1 +-2"), ("paragraph", "Para-\ngraph"),
      ("L2 source", "L2\nsource"), ("L3 3ep", "L3\n3 ep"), ("L3 7ep", "L3\n7 ep")]
fig, ax = plt.subplots(figsize=(8.4, 4.0))
Z = tc[[a for a, _ in lv]].to_numpy()
im = ax.imshow(Z, cmap="Oranges", vmin=0, vmax=1, aspect="auto")
for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
        ax.text(j, i, f"{Z[i, j]:.2f}" + (" *" if Z[i, j] >= 0.5 else ""), ha="center", va="center", fontsize=8.5,
                color="white" if Z[i, j] > 0.6 else INK)
ax.set_xticks(range(len(lv))); ax.set_xticklabels([b for _, b in lv], fontsize=9)
ax.set_yticks(range(len(tc))); ax.set_yticklabels([f"Case {c}: {t}" for c, t in zip(tc["case"], tc["type"])], fontsize=9)
cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("P(Ineffective)")
ax.set_title("P(Ineffective) for the ten gold-Ineffective failure cases (* = predicted Ineffective)", loc="left", fontsize=11)
save(fig, "fig23_ten_cases_by_context_level.png")

# ---------------------------------------------------------------- F24 rater-rater vs model-rater agreement
crossley = {"Lead": 0.378, "Position": 0.274, "Claim": 0.165, "Counterclaim": 0.188, "Rebuttal": 0.256, "Evidence": 0.432, "Concluding Statement": 0.370}
p = pd.read_csv(os.path.join(ROOT, "Week11_Person3_DeBERTa_OfficialTest", "outputs", "week11_person3", "test_predictions_L1.csv"))
mk = {t: summary(s["true_label"].to_numpy(), s["pred_label"].to_numpy())["kappa"] for t, s in p.groupby("discourse_type")}
fig, axs = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
y = np.arange(len(TYPES))
axs[0].barh(y, [crossley[t] for t in TYPES], color="#9aa9bd", height=0.6)
axs[1].barh(y, [mk[t] for t in TYPES], color=HILITE, height=0.6)
for ax, vals in ((axs[0], [crossley[t] for t in TYPES]), (axs[1], [mk[t] for t in TYPES])):
    for yi, v_ in zip(y, vals):
        ax.text(v_ + 0.008, yi, f"{v_:.3f}", va="center", fontsize=8.8)
    ax.set_xlim(0, 0.55); ax.grid(axis="x")
axs[0].set_yticks(y); axs[0].set_yticklabels(TYPES); axs[0].invert_yaxis()
axs[0].set_title("(a) Rater vs. rater, before adjudication\n(Crossley et al., 2024, Table 1; all essays)", loc="left", fontsize=10.5)
axs[1].set_title("(b) DeBERTa L1 vs. adjudicated label\n(unweighted Cohen's kappa, official test)", loc="left", fontsize=10.5)
axs[0].set_xlabel("Cohen's kappa (as reported)"); axs[1].set_xlabel("Cohen's kappa")
fig.text(0.01, -0.14, "The two panels answer different questions and are not on a common scale: (a) measures how far two trained raters agree with each other "
         "on overlapping segments;\n(b) measures how far the model reproduces the final adjudicated label. A higher value in (b) does not mean the model is 'better than a rater'.", fontsize=8.8)
save(fig, "fig24_rater_rater_vs_model_rater_agreement.png")

# ---------------------------------------------------------------- F25 project timeline by week
tl = [("Wk 6", "Midterm proposal: problem, user, data, 2 model families, evaluation plan", 0),
      ("Wk 7-8", "Classical baselines (LR, SVM), BERT + DeBERTa ensemble on a 14,303-unit dev split", 1),
      ("Wk 9", "Fixed split 115,187 / 29,102; LR 6.13% defect diagnosed; RF FS-B; single DeBERTa; 10 cases", 2),
      ("Wk 10", "Length-confound table; L0 vs L1 context ablation; RF LOPO (15 prompts); DeBERTa LOPO (3)", 3),
      ("Wk 11a", "Protocol locked; L0/L1/PA retrained; official test scored once (RF, L0, L1, PA)", 4),
      ("Wk 11b", "31-item audit; corrected length table and RF test; LOPO rerun; context ladder L1+-2..L3", 5),
      ("Post-int.", "Feedback of 03 Nov: raw-data checks, same-unit L0/L1 and LOPO tables, per-class results", 6)]
fig, ax = plt.subplots(figsize=(10, 3.6))
for i, (wk, txt_, k) in enumerate(tl):
    ax.add_patch(plt.Rectangle((0, -i - 0.4), 1.15, 0.8, color="#1f3864" if k in (4,) else "#4a6fa5"))
    ax.text(0.575, -i, wk, ha="center", va="center", color="white", fontsize=10)
    ax.text(1.3, -i, txt_, va="center", fontsize=10)
ax.set_xlim(0, 10); ax.set_ylim(-len(tl) + 0.4, 0.6); ax.axis("off")
save(fig, "fig25_project_timeline.png")

# ---------------------------------------------------------------- F27 RF what-if (case 8)
wf = pd.read_csv(os.path.join(ROOT, "VAN_DAP_4_TIEU_CHI", "trace_mau_that", "outputs", "rf_what_if_case8.csv"))
en = ["0. original unit", "1. spelling: there -> their", "2. add a reason to the sentence", "3. type Claim -> Evidence",
      "4. longer essay (169 -> 520 words)", "5. move unit to essay start"]
fig, ax = plt.subplots(figsize=(6.8, 3.0))
vals = wf["P(Ineffective)"].to_numpy()
ax.barh(range(len(vals)), vals, color=[MUTED] + [CC["Ineffective"] if v > vals[0] else HILITE for v in vals[1:]], height=0.6)
for i, v_ in enumerate(vals):
    ax.text(v_ + 0.005, i, f"{v_:.3f}" + ("" if i == 0 else f"  ({v_ - vals[0]:+.3f})"), va="center", fontsize=9)
ax.set_yticks(range(len(vals))); ax.set_yticklabels(en, fontsize=9.5); ax.invert_yaxis()
ax.set_xlim(0, 0.5); ax.set_xlabel("Random Forest P(Ineffective) for case 8 (row_idx 108613); prediction stays Adequate")
ax.grid(axis="x")
save(fig, "fig27_rf_what_if_case8.png")
print("done")
