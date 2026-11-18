# Submission checklist — Group 06, CLC02

Each item required by the course's "Submission package" section, with the file that satisfies it.

| Required item | File(s) | Status |
|---|---|---|
| PDF report, research-paper structure, 6–8 main-text pages | `output/Group06_CLC02_Final_Paper.pdf` (main text: Abstract to Discussion = 8 pages) | Ready |
| Full report (supplementary) | `output/Group06_CLC02_Final_Report.pdf` (86 pages) | Ready |
| Word sources | `output/Group06_CLC02_Final_Paper.docx`, `output/Group06_CLC02_Final_Report.docx` | Ready |
| Executed notebooks / scripts | `../Week11_Person3_DeBERTa_OfficialTest/07_person3_prompt_aware_official_test.ipynb`, `../week11_lopo_rerun/11_lopo_rerun_L0_output.ipynb`, `../week11_context_levels/*_output.ipynb`, `../Person1/`, `../Person2Khoa/`, `scripts/01–07` | Ready |
| Reproduction instructions | `README.md`; Supplementary Report Appendix B; paper Appendix B | Ready |
| Permitted data link / version | Supplementary Report Section 3.1 and Appendix B.1 (repository link, SHA-256 of both CSV files) | Ready |
| Split IDs, configurations, seeds | `tables/split_essays.csv`, `tables/split_units.csv.gz` (from `scripts/07_export_split_ids.py`); seed 42; configuration in Supplementary Report Table 4.3 and `../Week11_Person3_DeBERTa_OfficialTest/outputs/week11_person3/run_metadata.json` | Ready |
| Predictions behind the main table | `../Week11_Person3_DeBERTa_OfficialTest/outputs/week11_person3/{val,test}_predictions_{L0,L1,PA}.csv`, `../outputs/test_predictions_rf_feature_set_b.csv`, `../outputs/strongest_baseline_predictions.csv`, `../week11_lopo_rerun/outputs/predictions_fold{1,2,3}.csv` | Ready |
| Error table | `tables/R8_ten_cases.csv`; Supplementary Report Tables 7.4–7.5; paper Appendix E | Ready |
| Experiment and run log | Supplementary Report Appendix A and Table 5.2; paper Appendix A | Ready |
| Individual contributions | Supplementary Report Appendix C; paper Appendix C; `PHAN_CONG_VA_ON_TAP_GROUP06.md` | Names to be filled in by the group |
| AI-use disclosure | Supplementary Report Appendix D; paper Appendix D | Each member completes their own entry |

Do not upload to a public repository: the PERSUADE CSV files (`../data/persuade_raw/`), the source articles (`../week11_context_levels/upload/source_texts.json`) and model checkpoints. They are excluded by `.gitignore`.

After filling in names or AI entries, rebuild from the repository root:

```
python final_report/scripts/assemble_report.py
python final_report/scripts/build_docx_pdf.py            # Supplementary Report
python final_report/scripts/build_docx_pdf.py --paper    # 8-page paper (source: final_report/paper/PAPER.md)
```
