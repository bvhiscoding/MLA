# PHÂN CÔNG VÀ ÔN TẬP — GROUP 06 (CLC02), BẢN ĐỐI CHIẾU HỒ SƠ

**Ngày:** 18/11/2026
**Thay thế:** file "Tổng hợp toàn diện dự án MLA: giải đáp tuần 11, format báo cáo & phân công 3 thành viên". Các chỗ sai của file đó được liệt kê ở Phụ lục.

**Nguyên tắc soạn**
- Mọi con số lấy từ báo cáo cuối kỳ (`final_report/output/Group06_CLC02_Final_Report.pdf`, gọi tắt là *bản luận*; `Group06_CLC02_Final_Paper.pdf`, gọi tắt là *bản 8 trang*) hoặc từ `final_report/tables/*.csv` và `outputs/*.csv`.
- Phân công lấy theo file phân công từng tuần (`HUONG_DAN_PHAN_CONG_TUAN_9.md`, `WEEK10_PLAN_AND_ASSIGNMENTS.md`, `WEEK11_PLAN_AND_ASSIGNMENTS.md`), hồ sơ cá nhân `KNOWLEDGE_BASE/19–21` và nhật ký rà soát `RA_SOAT_TUAN11_SO_VOI_NHAN_XET_TUAN10.md`.
- Chỗ nào không có ghi chép thì để **[tự điền]**. Không dựng lại lịch sử không được ghi lại, vì rubric cấm việc này.
- "Người 1/2/3" là **vai** theo file phân công. Người giữ vai có thể đổi giữa các tuần; mỗi người tự ghi tên vào tuần mình làm.

---

## PHẦN 1. TRẢ LỜI 3 CÂU NHẬN XÉT SAU INTERVIEW (03/11/2026)

### Câu 1 — Đơn vị chú giải, nhãn, kiểm tra ghép ID và nạp nhãn

- **Đơn vị quan sát:** một đoạn luận điểm đã được người chấm tách và gán 1 trong 7 loại (Lead, Position, Claim, Counterclaim, Rebuttal, Evidence, Concluding Statement). Các dòng không có nhãn hiệu quả bị bỏ:
  - file train: 28.977 dòng (28.973 dòng loại "Unannotated" và 4 dòng thiếu nhãn);
  - file test: 18.440 dòng.

  Còn lại 144.289 đơn vị trong file train và 93.677 đơn vị trong file test. Bản luận mục 3.4, Bảng 3.2.
- **Nhãn:** định nghĩa theo rubric của PERSUADE (Bảng 3.1 bản luận):
  - Effective: đơn vị làm tốt chức năng của nó;
  - Adequate: làm đủ;
  - Ineffective: không làm được.

  Nhãn mang tính **quan hệ**: Claim được chấm so với Position, Rebuttal so với Counterclaim, Evidence so với Claim mà nó đỡ, Position so với đề. Mã hoá cố định: Ineffective = 0, Adequate = 1, Effective = 2.
- **Kiểm tra ghép ID và nạp nhãn** (bản luận mục 3.5, Bảng 3.4–3.5; log `final_report/evidence/data_checks_log.txt`). 7 kiểm tra C1–C7, đều đạt:
  1. Mã băm SHA-256 của hai file CSV khớp mã ghi lúc train và trong file khoá test.
  2. Lọc dữ liệu tái tạo đúng số đơn vị.
  3. Bộ nhãn và bộ loại đúng.
  4. `discourse_id` chỉ còn 728 giá trị cho 144.289 đơn vị (bị Excel làm tròn), nên **không bao giờ dùng để ghép**. Mọi phép ghép dùng `row_idx` hoặc `essay_id_comp`.
  5. 17 file dự đoán khớp dữ liệu gốc từng dòng về bài, loại và nhãn: 0 dòng lệch.
  6. Không bài nào nằm ở hai tập.
  7. 6 bản ghi thật được lần vết "nhãn chữ trong CSV → số đã nạp → nhãn trong file dự đoán", trong đó có ca 8 (`row_idx` 108613).

### Câu 2 — L1 thêm gì so với L0; tách in-domain và LOPO

- **L1 thêm gì:** đơn vị đứng ngay trước và ngay sau trong cùng bài.
  - Nhờ vậy mô hình thấy được claim có evidence liền sau không, counterclaim có rebuttal liền sau không.
  - L1 không thấy những gì nằm xa hơn: rebuttal ở đoạn khác, nội dung bài đọc nguồn.
  - Bản luận mục 4.3.3.
- **So trên cùng đơn vị, cùng split, cùng ngân sách huấn luyện** (bản luận Bảng 6.2–6.4; bản 8 trang Bảng 2):

  | L1 − L0 | Validation (29.102 đơn vị) | Test (93.677 đơn vị) |
  |---|---|---|
  | Macro-F1 | +0,0087 [+0,0015; +0,0161] | +0,0159 [+0,0115; +0,0205] |
  | F1 Ineffective | +0,0091 [−0,0097; +0,0278] | +0,0292 [+0,0185; +0,0408] |
  | F1 Adequate | +0,0108 [+0,0074; +0,0145] | +0,0098 [+0,0080; +0,0117] |
  | F1 Effective | +0,0061 [−0,0017; +0,0136] | +0,0087 [+0,0040; +0,0135] |

  - Lần train đầu tiên cho L1 − L0 = +0,0022 trên validation, nên mức cải thiện ngang với dao động giữa hai lần train.
  - Lợi nhiều nhất ở Counterclaim, Rebuttal và Claim.
  - Trong 10 ca lỗi: không ca nào đổi nhãn ở L1. P(Ineffective) tăng ở 8/10 ca, tính trên lần train L1 đầu tiên.
- **Mô hình nào phủ đề nào** (bản luận Hình 6.5):

  | Mô hình | Kiểu đánh giá | Số đề |
  |---|---|---|
  | RF, DeBERTa L0/L1/PA | In-domain (thấy cả 15 đề khi train) | Đánh giá chung trên cả 15 đề, không tách từng đề |
  | RF | LOPO | Cả 15 đề |
  | Linear SVM, DeBERTa L0 | LOPO | 3 đề: Cowboy, Summer projects, Distance learning |

- **LOPO so với in-domain trên cùng các bài validation của đề bị giấu** (bản luận Bảng 6.7; DeBERTa LOPO train cố định 3 epoch, không chọn epoch trên đề bị giấu):

  | Đề bị giấu | Số đơn vị / bài | LOPO | In-domain | Chênh [CI 95%] |
  |---|---|---:|---:|---|
  | A Cowboy Who Rode the Waves | 1.030 / 134 | 0,384 | 0,476 | −0,092 [−0,132; −0,049] |
  | Summer projects | 2.074 / 177 | 0,483 | 0,508 | −0,025 [−0,052; +0,011] |
  | Distance learning | 3.533 / 283 | 0,528 | 0,576 | −0,048 [−0,078; −0,019] |

### Câu 3 — Kết quả theo lớp; độ dài bài so với điểm và tỷ lệ lớp; κ

- **Theo lớp trên test** (bản luận Bảng 6.5). Linear SVM **không có** số QWK và recall Ineffective.

  | Hệ thống | Macro-F1 | F1 Ineff (recall) | F1 Adeq | F1 Eff | Accuracy | QWK |
  |---|---:|---|---:|---:|---:|---:|
  | Majority (luôn Adequate) | 0,297 | 0 (0%) | 0,892 | 0 | 80,5% | 0 |
  | RF, Feature Set B | 0,510 | 0,202 (17,2%) | 0,870 | 0,457 | 78,5% | 0,350 |
  | DeBERTa L0 | 0,561 | 0,339 (37,2%) | 0,831 | 0,514 | 74,4% | 0,422 |
  | DeBERTa L1 (khoá) | 0,577 | 0,368 (41,5%) | 0,841 | 0,523 | 75,7% | 0,442 |
  | DeBERTa Prompt-Aware (thăm dò) | 0,581 | 0,379 (44,2%) | 0,838 | 0,526 | 75,4% | 0,446 |
  | Linear SVM (bổ sung) | 0,482 | 0,204 | 0,844 | 0,398 | 74,4% | — |

- **Kiểm tra độ dài bài trước khi quy lỗi cho thiếu ngữ cảnh** (bản luận mục 3.7.4 rồi 7.2):
  - Độ dài bài và điểm holistic tương quan mạnh: Spearman 0,76 trên 25.996 bài. Tỷ lệ lớp cũng đổi theo độ dài (Cramér's V: điểm 0,386; độ dài 0,221).
  - Lỗi của L1 tăng từ 22,0% (Q1) lên 30,5% (Q4) trên validation, và ở Q4 92% lỗi là nhầm Adequate↔Effective. Nhưng **Macro-F1 gần như không đổi (0,53–0,55)**: tỷ lệ lỗi tăng chủ yếu vì tỷ lệ lớp thay đổi.
  - Trong cùng một mức điểm, lỗi **vẫn** tăng theo độ dài:
    - điểm 3: 19,3% → 28,2% trên validation; 17,6% → 29,2% trên test;
    - OR mỗi bậc độ dài là 1,19 [1,14; 1,25] khi kiểm soát điểm;
    - OR là 1,17 [1,11; 1,23] khi kiểm soát thêm nhãn gold và loại đơn vị.
  - Kết luận: giữ cả hai giả thuyết. Giả thuyết A là **độ dài/độ phức tạp**, không phải "mất ngữ cảnh". Chưa xác định được cơ chế.
- **κ mô hình–nhãn và κ người–người** (bản luận mục 8.3, Hình 8.1):
  - κ người–người = 0,316. Đo **độ tin cậy của nhãn**: hai người chấm độc lập. Crossley và cộng sự tính trên các đoạn mà cả hai cùng tách (chồng nhau ≥ 50%), trước khi phân xử, có trọng số.
  - κ mô hình–nhãn = 0,372 (L1 trên test, không trọng số). Đo mức mô hình **tái tạo nhãn đã phân xử** mà nó được train để bắt chước.
  - Hai số khác nhau về đối tượng so sánh, về nhãn, về đơn vị, về cách tính và về dữ liệu, nên **không so trực tiếp**. 0,372 > 0,316 không có nghĩa là mô hình giỏi hơn người chấm. κ người thấp cho biết một phần "lỗi mô hình" là bất đồng trong chính nhãn.

---

## PHẦN 2. FORMAT VÀ GÓI NỘP — TRẠNG THÁI

| Yêu cầu của rubric | Đường dẫn | Trạng thái |
|---|---|---|
| PDF đọc được, cấu trúc bài báo, 6–8 trang nội dung chính | `final_report/output/Group06_CLC02_Final_Paper.pdf`: nội dung chính 8 trang (Abstract → hết Discussion) | Xong |
| Bản đầy đủ làm tài liệu bổ sung | `final_report/output/Group06_CLC02_Final_Report.pdf` (86 trang) | Xong |
| Xuất từ Word, không từ HTML; Times New Roman 13; A4 dọc; không in đậm trong thân bài | `final_report/scripts/build_docx_pdf.py` (`--paper` cho bản 8 trang) | Xong, kiểm tra tự động đạt |
| Notebook/script đã chạy | `Week11_Person3_DeBERTa_OfficialTest/`, `week11_lopo_rerun/`, `week11_context_levels/`, `Person1/`, `Person2Khoa/`, `final_report/scripts/` | Xong |
| Hướng dẫn tái lập | Bản luận Phụ lục B; `final_report/README.md` | Xong |
| Dữ liệu: nguồn và phiên bản | Bản luận mục 3.1 và Phụ lục B.1 (link, SHA-256) | Xong |
| File chia tập và seed | `final_report/tables/split_essays.csv`, `split_units.csv.gz` (khoá `essay_id_comp`/`row_idx`); seed 42 | Xong |
| Dự đoán đằng sau bảng chính | `Week11_Person3_…/outputs/week11_person3/*predictions*.csv`, `outputs/test_predictions_rf_feature_set_b.csv`, `week11_lopo_rerun/outputs/` | Xong |
| Bảng ca lỗi | `final_report/tables/R8_ten_cases.csv`; bản luận Bảng 7.4–7.5 | Xong |
| Nhật ký thí nghiệm | Bản luận Phụ lục A, Bảng 5.2 | Xong |
| Đóng góp cá nhân | Bản luận Phụ lục C; bản 8 trang Phụ lục C | **Nhóm điền tên** |
| Khai báo dùng AI | Bản luận Phụ lục D; bản 8 trang Phụ lục D | **Mỗi người điền phần mình** |
| Không đưa dữ liệu hạn chế lên repo công khai | CSV gốc, văn bản nguồn, checkpoint đã nằm trong `.gitignore` | Xong |

---

## PHẦN 3. PHÂN CÔNG THEO VAI VÀ TUẦN (THEO HỒ SƠ)

| Tuần | Người 1 — dữ liệu, mô hình cổ điển, độ dài | Người 2 — DeBERTa, ngữ cảnh, ngưỡng, SVM | Người 3 — phân tích lỗi, LOPO, quản lý test |
|---|---|---|---|
| Tên | [tuần 9: ……] / [tuần 10–11: ……] | [……] | [tuần 9: ……] / [tuần 10–11: ……] |
| Trước tuần 9 | Người sau này giữ vai 1 ở tuần 9: tìm 3 bài báo R01–R03, chọn dữ liệu, pipeline thử `discourse_effectiveness_pipeline.py`, ensemble BERT + DeBERTa (`Ensemble_BERT_DeBERTa_A003/`) | [tự điền] | [tự điền] |
| 9 | `01_Data_Pipeline_Classical_Baseline.py`: pipeline, chia `GroupShuffleSplit` theo `essay_id` (seed 42; 115.187 / 29.102), Feature Set A/B, LR/RF/SVM/LightGBM, tái hiện lỗi LR 6,13% | `02_DeBERTa_Single_Evaluation.py`: DeBERTa đơn so với RF trên cùng validation (+0,054 [0,043; 0,065]), hiệu chỉnh xác suất, bỏ ensemble | `03_Error_Analysis_and_Reporting.py`: 10 ca Ineffective, lỗi theo loại và theo đề, kiểm tra ELL, đối chiếu tài liệu |
| 10 | `04_Length_Confound_and_LOPO.py`: bảng nhãn × đề × 4 nhóm độ dài; RF LOPO 15 đề | `05_Context_Ablation_DeBERTa.py`: L0 với L1 trên cùng đơn vị; kiểm tra lại 10 ca | `06_LOPO_DeBERTa.py`: DeBERTa LOPO 3 đề; báo cáo tuần 10 |
| 11 | `Person1/`: bảng điểm holistic × độ dài; RF trên test (bản đầu) | `Person2Khoa/`: quét ngưỡng và ca 8 (bản đầu); Linear SVM trên test; SVM LOPO **3 đề** | `Week11_Person3_DeBERTa_OfficialTest/`: train L0/L1/PA, chấm test một lần, file khoá, bootstrap |
| 11, rà soát 31/10 | — | — | Rà soát 31 mục (`RA_SOAT…md`, có dùng AI). Sửa: ghép theo `row_idx` thay cho `discourse_id`; dựng lại bảng độ dài × điểm; dựng lại RF Feature Set B (validation 0,5261 rồi test 0,5098); viết lại script ngưỡng; kiểm tra đoạn 36; LOPO trên cùng đơn vị (`script_lopo_same_units_gap.py`) |
| Sau 31/10 | — | — | Chạy lại LOPO (`week11_lopo_rerun/`); thang ngữ cảnh L1 ±2 / cả đoạn / L2 / L3 (`week11_context_levels/`) |
| Báo cáo cuối | [tự điền] | [tự điền] | [tự điền] (`final_report/`) |

**Nói thật về phần bị sửa**
- **Người 1, tuần 11:**
  - Bảng độ dài × điểm bản đầu ghép theo `discourse_id`, nên ra kết quả "phẳng 26%".
  - Script RF test bản đầu không phải Feature Set B (100 cây, depth 30, TF-IDF 10k, train cả validation; test 0,4834).
  - Cả hai được phát hiện và sửa trong đợt rà soát 31/10.
- **Người 2, tuần 11:**
  - Bản đầu ghi "recall 76,51% ở θ = 0,10, cứu được ca 8". Số đúng là 73,04%, và chỉ đúng với mô hình L1 train lần đầu.
  - Với mô hình L1 đã khoá, ca 8 có P = 0,058 nên **không** đổi nhãn ở θ = 0,10.
  - SVM chấm test được train trên cả validation; cùng cấu hình train trên 115.187 đơn vị cho validation 0,4845.
- Nếu chính bạn đã tự chạy lại script sửa, ghi **ngày chạy** vào đây: [tự điền].

---

## PHẦN 4. CÂU HỎI ÔN CHO TỪNG VAI

*Interview đã diễn ra ngày 03/11. Phần này để ôn và để trả lời nếu thầy hỏi lại khi chấm báo cáo.*

| Vai | Câu hỏi | Ý chính, đúng số |
|---|---|---|
| Người 1 | Vì sao lỗi tăng theo độ dài không có nghĩa là bài dài khó hơn với mô hình? | Bài dài là bài của học sinh giỏi hơn (Spearman 0,76). Tỷ lệ lớp lệch sang Adequate/Effective; ở Q4 92% lỗi là nhầm A↔E; Macro-F1 gần như không đổi. Nhưng trong cùng điểm lỗi vẫn tăng (OR 1,19; 1,17), nên chưa loại được giả thuyết độ dài/độ phức tạp |
| Người 1 | Vì sao không ghép theo `discourse_id`? | Excel làm tròn ID, 144.289 đơn vị chỉ còn 728 giá trị, ghép vào sẽ gán nhầm bài. Ghép theo `row_idx`/`essay_id_comp` và kiểm tra nhãn khớp từng dòng (C4–C5) |
| Người 1 | RF trên test có đúng mô hình đã chọn trên validation không? | Có: Feature Set B (TF-IDF 15k + one-hot loại + 5 đặc trưng chuẩn hoá; 200 cây, depth 35), chỉ chấm test sau khi tái tạo validation 0,5261; test 0,5098 |
| Người 2 | L1 thêm gì so với L0, và tăng bao nhiêu? | Thêm đơn vị trước và sau. Trên test +0,016 Macro-F1, +0,029 F1 Ineffective, cùng đơn vị. Ngang dao động giữa hai lần train (lần đầu +0,002) |
| Người 2 | Hạ ngưỡng Ineffective có làm mô hình tốt hơn không? | Không. θ = 0,10 với L1 đã khoá: recall 45% → 70%, Macro-F1 0,581 → 0,535, khoảng 8 báo nhầm cho mỗi ca bắt thêm. Ngưỡng là lựa chọn của giáo viên. Ca 8 không đổi nhãn với mô hình đã khoá |
| Người 2 | Vì sao 10 ca không đổi nhãn ở L1? | Phần lớn cần thông tin ngoài 2 câu lân cận: toàn bài (ca 1, 6), đề hoặc nguồn (5, 7, 9); một số yếu ngay trong câu (2, 3, 4, 10). Chỉ cả đoạn, nguồn hoặc cả bài mới làm đổi ca 2; L3 3 epoch làm đổi ca 1 và 5 |
| Người 3 | Vì sao không so κ mô hình 0,372 với κ người 0,316? | Hai đại lượng khác nhau (xem Câu 3). κ người đo độ tin cậy của nhãn, κ mô hình đo mức tái tạo nhãn đã phân xử |
| Người 3 | Tập test đã được dùng thế nào? | Một lần, cấu hình khoá trước, file khoá ghi mã băm; RF chỉ chấm sau cổng tái tạo validation. Mọi lựa chọn làm trên validation; các thí nghiệm sau đó chỉ chạy trên validation |
| Người 3 | LOPO khác in-domain ở đâu, đề nào giảm nhiều nhất? | LOPO không thấy đề khi train. Trên cùng đơn vị: Cowboy −0,092, Distance −0,048 (đều có ý nghĩa), Summer −0,025 (CI chứa 0). Liên hệ với đề dựa trên bài đọc chỉ là diễn giải, vì mới có 3 đề |

---

## PHỤ LỤC. ĐÍNH CHÍNH FILE TỔNG HỢP GỐC

| Chỗ trong file gốc | Ghi sai | Đúng | Nguồn kiểm chứng |
|---|---|---|---|
| Câu 2, bảng LOPO | Cowboy −0,117 [−0,171; −0,057], LOPO 0,3584; Summer −0,047, LOPO 0,4605; Distance −0,005, "chuyển giao hoàn hảo" | −0,092 [−0,132; −0,049]; −0,025 [−0,052; +0,011]; −0,048 [−0,078; −0,019]. Số cũ thuộc lần chạy chọn epoch trên chính đề bị giấu | `outputs/lopo_deberta_rerun_gap_same_units.csv` |
| Câu 2, mô hình nào phủ đề nào | Không nêu RF 15 đề / SVM 3 đề | RF LOPO 15 đề; SVM và DeBERTa LOPO 3 đề | `outputs/lopo_classical_results.csv`, `lopo_svm_baseline_results.csv` |
| Câu 3, bảng test | Linear SVM QWK 0,401 | Không có QWK cho SVM | `outputs/official_test_svm_actual_result.csv` |
| Câu 3, κ | κ mô hình trên test 0,374 | 0,372 (0,374 là validation) | `final_report/tables/R2_test_per_class.csv` |
| Câu 1, định nghĩa nhãn | "nghệ thuật tu từ tốt", "gắn kết với toàn bài" | Định nghĩa theo rubric PERSUADE, mang tính quan hệ | `data/persuade_raw/argumentation_effectiveness_rubric.pdf` |
| Câu 1, kiểm chứng | Chỉ 2 ví dụ | 7 kiểm tra C1–C7, 6 bản ghi lần vết | `final_report/evidence/data_checks_log.txt` |
| Câu 3, kết luận | "Giả thuyết A (độ dài/mất ngữ cảnh)"; thiếu ý Macro-F1 không đổi | Giả thuyết A là độ dài/độ phức tạp; Macro-F1 0,53–0,55 ở mọi nhóm độ dài | `final_report/tables/R7_L1_errors_by_length_quartile.csv` |
| Phần 2, độ dài | Chưa xử lý | Bản 8 trang + bản luận bổ sung | `final_report/output/` |
| Phần 3, Người 1 | Chia theo `essay_id_comp`; "phát hiện và khắc phục lỗi Excel"; Feature Set B "10k TF-IDF" | Chia theo `essay_id`; lỗi Excel phát hiện trong rà soát 31/10; Feature Set B dùng TF-IDF 15k | `01_Data_Pipeline_Classical_Baseline.py`, `RA_SOAT…md` B1 |
| Phần 3, Người 2 | SVM LOPO "toàn bộ 15 đề"; sở hữu `03_Error_Analysis…`; tự mở nguồn kiểm tra đoạn 36; "θ = 0,10 cứu ca 5, 8" | SVM LOPO 3 đề; `03_…` là của Người 3; đoạn 36 kiểm tra trong rà soát; ca 8 không đổi nhãn với mô hình đã khoá | Phân công tuần 9, `RA_SOAT…md`, `outputs/threshold_case_flips.csv` |
| Phần 3, Người 3 | Sở hữu `02_DeBERTa…`, `05_Context_Ablation…`; Cowboy −0,117 | Hai file đó là của Người 2; Cowboy −0,092 | Phân công tuần 9 và 10 |
| Phần 3 | `BAO_CAO_VAN_DAP_NGUOI_1_CONFOUND_RF_SVM.md` | File không có trong repo | — |
| Toàn file | Dùng "chứng minh" nhiều lần | Viết đúng mức ("cho thấy", "phù hợp với"), như thầy đã nhắc | — |
