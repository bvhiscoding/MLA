# final_report — Group 06, CLC02: final project report package

Everything needed to read, check and rebuild the final report.

| Path | Content |
|---|---|
| `paper/PAPER.md` | Source of the 8-page main paper (edit directly) |
| `FINAL_REPORT.md` | Full report text, used as the Supplementary Report (assembled; do not edit directly) |
| `report_src/` | The report source, one file per chapter; edit these, then run `scripts/assemble_report.py` |
| `figures/` | All 26 figures (plus an unused timeline figure) (PNG, 300 dpi): data figures from `scripts/04_figures.py`, diagrams rendered from `diagrams/*.mmd` |
| `diagrams/` | Mermaid sources of the workflow, data pipeline, ML pipeline, context ladder and test-governance diagrams |
| `tables/` | Every table behind the report, recomputed from raw data and saved predictions (D* data checks, E* EDA, R* results, L* LR reference, `split_essays.csv` / `split_units.csv.gz` clean split files) |
| `evidence/data_checks_log.txt` | Log of the data verification checks C1–C7 (post-interview feedback item 1) |
| `evidence/results_log.txt` | Log of the recomputed results |
| `scripts/` | `01`–`07` analysis scripts, `assemble_report.py`, and the Word/PDF build script |
| `BUILD_SPEC.md` | Formatting specification for the Word and PDF versions |
| `output/` | `Group06_CLC02_Final_Paper.{docx,pdf}` (main paper, 8 pages of main text) and `Group06_CLC02_Final_Report.{docx,pdf}` (Supplementary Report, 86 pages) |
| `SUBMISSION_CHECKLIST.md` | Every item of the submission package with its file |
| `PHAN_CONG_VA_ON_TAP_GROUP06.md` | Role assignment checked against the records, answers to the post-interview feedback, study questions, and corrections to the earlier summary file (Vietnamese) |

Rebuild the numbers and figures (CPU, about 3 minutes, from the repository root, raw CSVs in `data/persuade_raw/`):

```
python final_report/scripts/01_data_checks_eda.py
python final_report/scripts/02_results_from_predictions.py
python final_report/scripts/03_ten_cases.py
python final_report/scripts/05_lr_interpretable_reference.py
python final_report/scripts/06_subgroup_ell.py
python final_report/scripts/07_export_split_ids.py
python final_report/scripts/04_figures.py
python final_report/scripts/assemble_report.py
python final_report/scripts/build_docx_pdf.py            # Supplementary Report (Word + PDF)
python final_report/scripts/build_docx_pdf.py --paper    # 8-page main paper (Word + PDF)
```

Before submission the group must fill in: member names and student IDs (title page, Appendix C), the "[to be completed]" cells of Appendix C, and the members' own rows of the AI-use table (Appendix D).
