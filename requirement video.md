# HƯỚNG DẪN & DÀN KHUNG CHUNG VIDEO BÁO CÁO (5 PHÚT)
## Course: Machine Learning Applications — Final Project Video Specification
**Đề tài:** Predicting the Effectiveness of Argumentative Discourse Units in Student Essays  
**Lớp / Nhóm:** CLC02 · Group 06  
**Thời lượng:** Khoảng **5 phút** (khuyến nghị 4:30 – 5:15, tương đương 650 – 720 từ tiếng Anh nói)  
**Định dạng nộp:** `Video/StudentID_Name.mp4` (1080p, âm thanh rõ, trình bày bằng tiếng Anh)  

---

## 1. YÊU CẦU CỐT LÕI TỪ GIẢNG VIÊN (`Requirements.md`)

Mỗi sinh viên nộp 1 video cá nhân riêng biệt đáp ứng 4 tiêu chí:
1. **Technical explanation:** Giới thiệu bài toán, phương pháp tiếp cận và vai trò đóng góp của bản thân.
2. **Evidence & demonstration:** Có thao tác demo thực tế trên màn hình (chạy code/terminal, mở notebook, hoặc chỉ ra file dự đoán) và giải thích một ví dụ dữ liệu cụ thể từ đầu vào đến kết quả.
3. **Data & charts:** Sử dụng bảng số liệu, biểu đồ hoặc ví dụ có chú thích để diễn giải kết quả.
4. **Error analysis & limitations:** Diễn giải ít nhất một trường hợp lỗi, hạn chế hoặc bài học rút ra.

---

## 2. DÀN KHUNG THUYẾT TRÌNH CHUNG (5 PHÚT)
*(Dàn khung dùng chung cho tất cả thành viên. Mỗi người chỉ cần đưa phần việc cụ thể của mình vào các vị trí đánh dấu `[...]`)*

```
[00:00 - 00:45] PHẦN 1: Giới thiệu bản thân & Bài toán nghiên cứu (45 giây)
[00:45 - 01:30] PHẦN 2: Phần việc cá nhân đảm nhiệm & Phương pháp tiếp cận (45 giây)
[01:30 - 02:45] PHẦN 3: Thao tác thực tế (Demo) & Lần vết 1 ví dụ cụ thể (75 giây)
[02:45 - 04:00] PHẦN 4: Phân tích kết quả thực nghiệm & Biểu đồ chính (75 giây)
[04:00 - 05:00] PHẦN 5: Phân tích trường hợp lỗi, Hạn chế & Kết luận (60 giây)
```

---

### CHI TIẾT TỪNG PHẦN:

### PHẦN 1: Giới thiệu bản thân & Bài toán (0:00 – 0:45)
- **Hình ảnh trình chiếu:** Slide tiêu đề (Họ tên, MSSV, Nhóm 06, Lớp CLC02, Tên đề tài) + Sơ đồ bài toán tổng thể (`fig01_user_decision_workflow.png`).
- **Nội dung nói:**
  - Giới thiệu bản thân: Tên, MSSV, nhóm.
  - Bối cảnh bài toán: Giáo viên dạy viết văn nghị luận tiếng Anh cần biết đoạn văn/luận điểm nào của học sinh bị yếu để sửa, thay vì chỉ nhận một con điểm tổng thể.
  - Dữ liệu nghiên cứu: Tập PERSUADE 2.0 (hơn 237.000 đơn vị luận điểm, 26.000 bài luận học sinh lớp 6–12 tại Mỹ, 15 đề viết).
  - Thách thức lớn nhất: Nhãn phân loại bị lệch rất nặng (`Ineffective` chỉ chiếm 4.5%, `Adequate` chiếm 80.5%, `Effective` chiếm 15.0%).

---

### PHẦN 2: Phần việc cá nhân & Phương pháp (0:45 – 1:30)
- **Hình ảnh trình chiếu:** Slide tóm tắt phân công cá nhân + Sơ đồ kiến trúc/pipeline tổng thể (`fig02_data_pipeline_split.png` hoặc `fig03_ml_pipeline.png`).
- **Nội dung nói:**
  - Nêu rõ phần việc cá nhân: `[Điền vai trò/nội dung cá nhân thực hiện: ví dụ xử lý dữ liệu & mô hình cổ điển / fine-tuning Transformer & ngữ cảnh / phân tích lỗi & kiểm soát đánh giá tập test]`.
  - Nguyên tắc dữ liệu của dự án: Chia tập 80/20 theo bài luận (`GroupShuffleSplit`, seed 42) để tránh rò rỉ thông tin giữa các đoạn trong cùng một bài.
  - Mục tiêu tối ưu: Đánh giá bằng Macro-F1 và F1 từng lớp để đảm bảo nhận diện tốt lớp thiểu số `Ineffective`.

---

### PHẦN 3: Thao tác thực tế & Lần vết ví dụ cụ thể (1:30 – 2:45)
- **Hình ảnh trình chiếu:** Quay màn hình thao tác thực tế (Mở VS Code / Jupyter Notebook hoặc chạy terminal lệnh tái lập).
- **Thao tác demo:**
  - *Cách 1 (Nhanh & trực quan):* Mở terminal, chạy lệnh `python MLA_Final/Code/reproduce_results.py` để hiển thị quá trình tính toán và kiểm chứng các bảng kết quả.
  - *Cách 2 (Chi tiết mô hình):* Mở một notebook đã chạy sẵn trong `MLA_Final/Code/notebooks/` để chỉ ra cấu hình mô hình và các cell xuất kết quả.
- **Lần vết 1 ví dụ dữ liệu:**
  - Chọn 1 câu luận điểm thực tế (ví dụ: *Claim: "Some kids will ask there parents to transfer school"* hoặc một câu thuộc phần việc của mình).
  - Giải thích cách dữ liệu đi từ văn bản gốc $\to$ đưa qua mô hình $\to$ cho ra nhãn dự đoán và xác suất xác thực.

---

### PHẦN 4: Kết quả thực nghiệm & Phân tích biểu đồ (2:45 – 4:00)
- **Hình ảnh trình chiếu:** Chiếu 1–2 biểu đồ chất lượng cao trong thư mục hình ảnh (`Results/figures/`) kết hợp với bảng số liệu tương ứng.
- **Nội dung nói:**
  - Trình bày kết quả cốt lõi liên quan đến phần việc của mình:
    - *Nếu nói về so sánh mô hình:* DeBERTa-v3 Level 1 đạt Macro-F1 **0.577** trên test, vượt trội so với Random Forest (**0.510**) và Majority (**0.297**).
    - *Nếu nói về vai trò ngữ cảnh:* Thêm 2 câu lân cận (Level 1) giúp tăng **+0.016 Macro-F1**, tăng mạnh nhất ở các loại luận điểm có tính liên kết logic (`Counterclaim`, `Rebuttal`).
    - *Nếu nói về đề bài mới:* Đánh giá trên đề chưa từng thấy (LOPO) bị hụt từ **0.025 đến 0.092 Macro-F1**, sụt mạnh nhất ở các đề đọc hiểu nguồn.
    - *Nếu nói về độ dài bài:* Độ dài bài tương quan mạnh với điểm (0.76). Trong cùng một mức điểm, bài càng dài thì tỷ lệ lỗi vẫn tăng (odds ratio 1.19).
  - Chỉ rõ số liệu trên biểu đồ và giải thích ý nghĩa thực tế.

---

### PHẦN 5: Phân tích lỗi, Hạn chế & Kết luận (4:00 – 5:00)
- **Hình ảnh trình chiếu:** Biểu đồ phân tích lỗi (`fig23`, `fig20` hoặc `fig24_rater_rater_vs_model_rater_agreement.png`).
- **Nội dung nói:**
  - Chỉ ra 1 điểm hạn chế hoặc 1 trường hợp mô hình đoán sai:
    - Ví dụ về tính chủ quan của người chấm: Độ đồng thuận giữa 2 người chấm độc lập chỉ đạt Cohen's $\kappa = 0.316$, cho thấy bản thân nhãn đã có độ nhiễu và tranh cãi.
    - Hoặc ví dụ về việc hạ ngưỡng phát hiện: Hạ ngưỡng $\theta = 0.10$ giúp tìm được 70% nhãn Ineffective nhưng phát sinh nhiều cảnh báo nhầm (false alarms).
  - Tuyên bố phạm vi ứng dụng: Công cụ này dùng để hỗ trợ giáo viên sắp xếp thứ tự đọc bài nhanh hơn, **tuyệt đối không dùng để chấm điểm tự động học sinh**.
  - Lời cảm ơn và kết thúc bài thuyết trình.

---

## 3. KHO TÀI NGUYÊN HÌNH ẢNH & SỐ LIỆU CHUNG (ASSET POOL)
*(Người làm video có thể tự do chọn các hình ảnh và bảng số liệu dưới đây để đưa vào bài nói)*

### A. Danh mục hình ảnh có sẵn (Độ phân giải 300 DPI tại `MLA_Final/Results/figures/`):
1. **Tổng quan & Luồng bài toán:**
   - `fig01_user_decision_workflow.png`: Luồng hỗ trợ giáo viên ra quyết định đọc và chữa bài.
   - `fig02_data_pipeline_split.png`: Luồng tiền xử lý, lọc dòng thiếu và phân chia tập 80/20 theo bài.
   - `fig03_ml_pipeline.png`: Kiến trúc mô hình Transformer và hàm mất mát class-weighted.
   - `fig26_test_governance.png`: Quy trình quản trị tập test độc lập (chấm 1 lần duy nhất với file khoá).
2. **Khảo sát dữ liệu & Biến nhiễu độ dài:**
   - `fig05_label_distribution_by_split.png`: Phân bố mất cân bằng nhãn trên các tập train/val/test.
   - `fig08_unit_length_by_label.png`: Phân bố số lượng từ của từng loại nhãn.
   - `fig09_essay_length_vs_holistic_score.png`: Tương quan chặt chẽ giữa độ dài bài và điểm tổng thể (Spearman 0.76).
   - `fig20_error_within_score_by_length.png`: Tỷ lệ lỗi trong cùng mức điểm phân theo 4 nhóm độ dài.
3. **Hiệu năng mô hình & Cắt bỏ ngữ cảnh:**
   - `fig12_per_class_results_val_test.png`: F1 từng lớp và Macro-F1 giữa các họ mô hình.
   - `fig13_confusion_matrices_test.png`: Ma trận nhầm lẫn 3x3 trên tập test chính thức.
   - `fig04_context_levels.png`: Thang biểu diễn các cấp độ ngữ cảnh (L0, L1, paragraph, source, full essay).
   - `fig14_L1_minus_L0_per_class.png`: Mức độ cải thiện của L1 so với L0 theo từng loại luận điểm.
   - `fig22_threshold_tradeoff.png`: Đánh đổi giữa độ bao phủ (Recall) và cảnh báo nhầm khi đổi ngưỡng $\theta$.
4. **Khái quát hóa trên đề mới & Phân tích lỗi:**
   - `fig16_prompt_coverage_indomain_vs_lopo.png`: Mức độ phủ 15 đề giữa in-domain và LOPO.
   - `fig17_lopo_vs_indomain_same_units.png`: So sánh hiệu năng LOPO và in-domain trên cùng các bài validation.
   - `fig23_ten_cases_by_context_level.png`: Kết quả dự đoán của các cấp ngữ cảnh trên 10 ca lỗi Ineffective.
   - `fig24_rater_rater_vs_model_rater_agreement.png`: So sánh độ đồng thuận $\kappa$ người–người (0.316) với $\kappa$ mô hình (0.372).

### B. Các bảng số liệu cốt lõi (Xem file CSV tại `MLA_Final/Results/tables/`):
- **Bảng 1 (So sánh mô hình trên tập Test):**
  - Majority Baseline: Macro-F1 = 0.297 | Accuracy = 80.5% | Ineffective F1 = 0.000
  - Random Forest (Feature Set B): Macro-F1 = 0.510 | Accuracy = 78.5% | Ineffective F1 = 0.202 (Recall 17.2%)
  - DeBERTa-v3 L0 (chỉ câu): Macro-F1 = 0.561 | Accuracy = 74.4% | Ineffective F1 = 0.339
  - DeBERTa-v3 L1 (kèm câu trước sau): Macro-F1 = **0.577** | Accuracy = 75.7% | Ineffective F1 = **0.368** (Recall 41.5%)
- **Bảng 2 (Độ chênh Level 1 − Level 0 trên cùng đơn vị):**
  - Test Macro-F1 delta: **+0.0159** [95% CI: +0.0115, +0.0205]
  - Test Ineffective F1 delta: **+0.0292**
  - Loại tăng mạnh nhất: Counterclaim (+0.037), Rebuttal (+0.028), Claim (+0.028)
- **Bảng 3 (Độ hụt khi sang đề mới - LOPO):**
  - A Cowboy Who Rode the Waves: sụt **−0.092** Macro-F1 (từ 0.476 xuống 0.384)
  - Distance learning: sụt **−0.048** Macro-F1 (từ 0.576 xuống 0.528)
  - Summer projects: sụt **−0.025** Macro-F1 (từ 0.508 xuống 0.483)

---

## 4. HƯỚNG DẪN THỰC HIỆN PHẦN DEMO THỰC TẾ TRONG VIDEO

Trong phần 3 (từ 1:30 đến 2:45), người thuyết trình cần quay trực tiếp màn hình máy tính. Có 2 cách thực hiện rất dễ:

### Cách 1: Chạy script kiểm chứng 1-lệnh trong Terminal (Khuyến nghị, nhanh nhất)
1. Mở Terminal (PowerShell / Command Prompt / VS Code Terminal).
2. Di chuyển vào thư mục: `cd MLA_Final/Code`
3. Chạy lệnh: `python reproduce_results.py`
4. Màn hình sẽ chạy và in ra toàn bộ Bảng 1, Bảng 2, Bảng 3 trong khoảng 5 giây. Người nói dùng chuột trỏ vào các hàng số liệu để diễn giải.

### Cách 2: Mở một Notebook đã chạy sẵn kết quả
- Mở một trong các Jupyter Notebook có sẵn trong `MLA_Final/Code/notebooks/`:
  - `01_deberta_prompt_aware_official_test.ipynb` (quá trình chấm test chính thức của DeBERTa).
  - `02_lopo_rerun_deberta_L0.ipynb` (đánh giá trên đề mới).
  - `03_random_forest_official_test.ipynb` (huấn luyện và đánh giá Random Forest).
- Cuộn đến đoạn code nạp dữ liệu và bảng ma trận nhầm lẫn / kết quả đánh giá để thuyết minh.

---

## 5. MẪU PROMPT CHUNG ĐỂ GIAO CHO AI KHÁC SINH SCRIPT CHI TIẾT

Khi bạn hoặc người khác muốn đưa tài liệu này vào một mô hình AI khác để tự động viết kịch bản chi tiết (lời thoại tiếng Anh từng câu + mô tả slide), hãy sử dụng mẫu prompt sau:

```text
PROMPT:
You are an expert academic presentation coach. Write a complete, timed 5-minute English spoken presentation script for an individual student presentation in an advanced Machine Learning course.

Student Name: [Điền tên sinh viên]
Student ID: [Điền mã sinh viên]
Group: Group 06, Class CLC02
Paper Title: Predicting the Effectiveness of Argumentative Discourse Units in Student Essays
My specific role/contribution: [Mô tả ngắn gọn vai trò hoặc phần việc của bạn]

Requirements:
1. Follow the exact 5-part timeline specified in "requirement video.md":
   - Part 1: Self-Introduction & Problem Context (0:00 - 0:45)
   - Part 2: Personal Ownership & Methodology (0:45 - 1:30)
   - Part 3: Live Demo & Example Walkthrough (1:30 - 2:45)
   - Part 4: Key Results & Visualizations (2:45 - 4:00)
   - Part 5: Error Analysis, Limitations & Conclusion (4:00 - 5:00)
2. Total word count: around 650 - 700 spoken English words.
3. For each part, include:
   - [Slide / Visual Cue]: specify which figure from the Asset Pool in "requirement video.md" to display.
   - [On-screen Action]: describe what to show on screen (slides or live terminal/notebook demo).
   - [Spoken Script]: the exact words to speak in natural, professional academic English.
4. Use the exact numbers from the Asset Pool (Macro-F1 0.577, L1 delta +0.016, class imbalance 4.5%, rater kappa 0.316).
```
