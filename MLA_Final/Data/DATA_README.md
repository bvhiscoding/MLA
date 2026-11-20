# DATA_README — PERSUADE 2.0 Dataset Documentation

**Course:** Machine Learning Applications (61FIT4MLA / 62FIT4MLA)  
**Class / Group:** CLC02 · Group 06  
**Project:** Predicting the Effectiveness of Argumentative Discourse Units in Student Essays  

---

## 1. Corpus Source, Version & License

- **Corpus Name:** PERSUADE 2.0 (Persuasive Essays for Rating, Selecting, and Understanding Argumentative Discourse)
- **Version:** 2.0 (Published 2024; builds on PERSUADE 1.0 with holistic essay scores and discourse element proficiency ratings)
- **Primary Reference:**
  Crossley, S. A., Tian, Y., Baffour, P., Franklin, A., Benner, M., & Boser, U. (2024). *A large-scale corpus for assessing written argumentation: PERSUADE 2.0*. Assessing Writing, 61, Article 100865. [https://doi.org/10.1016/j.asw.2024.100865](https://doi.org/10.1016/j.asw.2024.100865)
- **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
  Commercial redistribution is prohibited. Academic non-commercial research and evaluation are permitted under attribution.

---

## 2. Obtaining the Restricted Full Raw Data

In compliance with the CC BY-NC-SA 4.0 license and repository size restrictions, raw 1GB CSV files are not redistributed in git repositories. Authorized researchers and graders can download the official source datasets directly from the corpus release links:

- **Training Set CSV (~617 MB):**  
  [Google Drive Link](https://drive.google.com/file/d/13phHyDzIsb0MHyJr6q-B-qIa9P2tM135/view?usp=sharing)  
  *Filename:* `persuade_corpus_2.0_train.csv`  
  *SHA-256:* `5ea92d529aee5582f3efaf8fc34e4028608226079c67eb0a3f81eebf4277bbf4`

- **Official Test Set ZIP (~382 MB):**  
  [Google Drive Link](https://drive.google.com/file/d/1K1SIJiG-2zWgMlTzxQeYOcLwOsFaVel1/view?usp=sharing)  
  *Filename:* `persuade_corpus_2.0_test.csv.zip`  
  *Decryption Password:* `persuade_test`  
  *Extracted Filename:* `persuade_corpus_2.0_test.csv`  
  *SHA-256:* `f65c92582ea8693c66fec420bc2811a91722d46e4c274b7cb59489da3b27b469`

---

## 3. Data Cleaning, Filtering & Preparation Steps

The raw CSV files are preprocessed through the standard project pipeline (`MLA_Final/Code/scripts/common.py` and `01_Data_Pipeline_Classical_Baseline.py`):

1. **Filtering Non-Annotated Records:**  
   - Records with missing `discourse_effectiveness` or `discourse_text` are removed.
   - In the training set: 28,977 non-annotated rows dropped (28,973 unannotated spans + 4 missing labels).
   - In the test set: 18,440 non-annotated rows dropped.
   - Text is stripped of whitespace; empty text entries are removed.
   - Resulting dataset contains exactly **144,289** units (15,594 essays) in training and **93,677** units (10,402 essays) in test.

2. **Identifier Integrity Check:**  
   - Warning: Spreadsheet tools historically truncated/rounded numeric `discourse_id` into only 728 distinct values for 144,289 units.  
   - **Protocol:** `discourse_id` is never used as a merge key. All alignments strictly use sequential integer `row_idx` or uncorrupted string `essay_id_comp`.

3. **Data Splitting Protocol:**  
   - Partitioning is performed strictly at the **essay level** to avoid data leakage between units of the same essay.
   - Method: scikit-learn `GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)` grouped by `essay_id`.
   - Result:
     - Training Split: 115,187 units (12,475 essays)
     - Validation Split: 29,102 units (3,119 essays)
     - Official Test Split: 93,677 units (10,402 essays)

4. **Label Encoding:**  
   - `0` = `Ineffective` (4.5% overall test frequency — extreme minority)
   - `1` = `Adequate` (80.5% overall test frequency — dominant majority)
   - `2` = `Effective` (15.0% overall test frequency)

---

## 4. Included Approved Samples & Split Artifacts

To enable 100% offline reproducibility without downloading the restricted 1GB raw CSV files, this directory includes:

- `splits/split_essays.csv`: Mapping of every `essay_id_comp` to its partition (`train`, `val`, `test`).
- `splits/split_units.csv.gz`: Mapping of every unit `row_idx` to its partition.
- `samples/_units_slim.csv.gz`: Clean, approved unit metadata table (144,289 train/val + 93,677 test units). Includes `row_idx`, `essay_id_comp`, `prompt_name`, `task`, `discourse_type`, `label`, `unit_words`, `essay_word_count`, `holistic_essay_score`, `length_q`, and `ell_status` without distributing proprietary essay text.
- `rubrics/`: Official PERSUADE 2.0 evaluation guidelines and scoring rubrics:
  - `argumentation_effectiveness_rubric.pdf`
  - `sat_rubric_only_indy.pdf`
  - `sat_rubric_only_source_based.pdf`
