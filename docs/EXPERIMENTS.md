# EXPERIMENTS.md — Kế hoạch thực nghiệm

## 1. Ba câu hỏi nghiên cứu

- **CH1** — `chunk-aware lookback ratio` có hơn lookback gộp không, và phân bố chú ý có tập trung đúng vào đoạn chứa bằng chứng không?
- **CH2** — Hướng nội tại đứng ở đâu trên mặt phẳng đánh đổi độ chính xác và chi phí, so với bộ mã hóa và LLM giám khảo?
- **CH3** — Tín hiệu chú ý đóng góp thêm bao nhiêu so với đặc trưng bề mặt, và có khái quát hóa ra ngoài phân phối huấn luyện không?

## 2. Danh sách thí nghiệm

| Mã | Tên | Trả lời | Bộ dữ liệu | Phụ thuộc |
|---|---|---|---|---|
| E01 | Baseline tầm thường (độ dài + trùng lặp từ vựng) | CH3 | ViHallu | — |
| E02 | Tái lập Lookback Lens gốc (lookback gộp) | CH1 | ViHallu | — |
| E03 | Chunk-aware, chia theo câu | CH1 | ViHallu | E02 |
| E04 | Chunk-aware, chia theo cửa sổ token | CH1 | ViHallu | E02 |
| E05 | So sánh hai cách chia chunk, chọn cách tốt hơn | CH1 | ViHallu | E03, E04 |
| E06 | Định vị chú ý so với đoạn bằng chứng vàng | CH1 | ISE-DSC01 | E05 |
| E07 | Chunk-aware trên ngữ cảnh dài | CH1 | ISE-DSC01 | E05 |
| E08 | Thí nghiệm lớp ngoại lai (NEI có bằng chứng) | CH1 | ViWikiFC | E05 |
| E09 | Baseline bộ mã hóa (PhoBERT, XLM-R, InfoXLM) | CH2 | ViHallu | — |
| E10 | Baseline LLM giám khảo (Gemini free, mẫu nhỏ) | CH2 | ViHallu | — |
| E11 | Bảng đánh đổi độ chính xác và chi phí | CH2 | ViHallu | E05, E09, E10 |
| E12 | Ablation: nhóm đặc trưng nào đóng góp | CH3 | ViHallu | E05 |
| E13 | Ablation: mô hình đọc Qwen2.5-7B với Sailor2-8B | CH1, CH3 | ViHallu | E05 |
| E14 | Ablation: bậc thang kích thước 7B / 3B / 1.5B | CH2 | ViHallu | E05 |
| E15 | Đối chứng ngoài trên split gốc | CH2 | ViWikiFC | E05 |
| E16 | Chuyển giao ViHallu sang ISE-DSC01 và ngược lại | CH3 | cả hai | E05, E07 |
| E17 | Chuyển miền sang tin tức (chỉ nếu còn thời gian) | CH3 | ViFactCheck | E15 |

## 3. Chỉ số

**Chính:** macro-F1. **Phụ:** accuracy, F1 từng lớp, ECE (khi có xác suất).

**Vận hành, bắt buộc báo cáo với mọi phương pháp:**
- `ms_per_sample` — thời gian trung bình mỗi mẫu, đo bằng `time.perf_counter`, đã loại thời gian nạp mô hình
- `peak_vram_mb` — `torch.cuda.max_memory_allocated()` chia 1024²
- `n_params_trainable` — số tham số phải huấn luyện

Mọi con số phải kèm độ lệch chuẩn qua 5 seed cho phần huấn luyện bộ phân loại (rẻ). Phần trích đặc trưng chạy một lần vì tất định.

## 4. Chi tiết vài thí nghiệm quan trọng

### E01 — Baseline tầm thường

Đây là thí nghiệm **bắt buộc chạy sớm nhất**, vì nó định nghĩa sàn thật sự.

Đặc trưng chỉ gồm hai số: số từ của `response`, và tỷ lệ từ trong `response` cũng xuất hiện trong `context`. Bộ phân loại logistic. Trên ViHallu, nhóm đã đo trước hai chỉ số này biến thiên đơn điệu theo nhãn:

| Nhãn | Độ dài phản hồi | Tỷ lệ trùng lặp |
|---|---|---|
| no | 32,9 từ | 0,815 |
| intrinsic | 39,5 từ | 0,650 |
| extrinsic | 45,9 từ | 0,545 |

Nếu baseline này đạt macro-F1 cao, mọi phương pháp phức tạp hơn phải chứng minh vượt nó chứ không phải vượt PhoBERT 32,83%.

### E05 — Chọn cách chia chunk

Chạy E03 và E04 với cùng mọi thứ khác. Với `token_window` quét `window_size` thuộc `{64, 128, 256}` và `stride` bằng nửa cửa sổ. Báo cáo bảng đầy đủ, chọn cấu hình tốt nhất trên tập dev, và **giữ nguyên cấu hình đó cho mọi thí nghiệm sau**.

Ghi rõ trong báo cáo rằng nhóm đã thử cả hai họ chiến lược trước khi chốt — đây là một kết quả, không phải bước phụ.

### E06 — Định vị chú ý

Thí nghiệm quan trọng nhất cho CH1. Chỉ chạy trên các mẫu ISE-DSC01 có bằng chứng, tức nhãn SUPPORTED và REFUTED.

Với mỗi mẫu: chia ngữ cảnh thành chunk, xác định chunk chứa bằng chứng vàng, tính phân bố chú ý trên các chunk, rồi đo:

- `hit@1` — chunk được chú ý nhiều nhất có phải chunk bằng chứng không
- `hit@3`
- `MRR` của chunk bằng chứng
- So với sàn ngẫu nhiên `1/n_chunks`

Với nhãn NEI (không có bằng chứng), đo entropy phân bố và kiểm định giả thuyết entropy cao hơn đáng kể so với hai nhãn kia.

### E11 — Bảng đánh đổi

Bảng trung tâm của chương 7. Mỗi dòng một phương pháp, cột gồm macro-F1, ms/mẫu, VRAM đỉnh, số tham số huấn luyện, và có cần API ngoài không.

### E13 — Qwen2.5 với Sailor2

Cùng code, chỉ đổi `model_name`. Ngoài so sánh macro-F1, đo thêm **vị trí các đầu chú ý có ích nhất** (theo trọng số của bộ phân loại tuyến tính) và kiểm tra chúng có nằm ở cùng lớp/đầu giữa hai mô hình không. Đây là câu hỏi khoa học mới: huấn luyện chuyên sâu tiếng Việt có dịch chuyển vị trí các đầu sao chép không.

## 5. Bảng kết quả cần điền

Điền vào đây khi có số. Ô trống nghĩa là chưa chạy.

### Bảng 1 — Kết quả chính trên ViHallu (tập test tự chia theo ngữ cảnh)

| Phương pháp | macro-F1 | Acc | F1 no | F1 intr | F1 extr | ms/mẫu | VRAM MB |
|---|---|---|---|---|---|---|---|
| Baseline tầm thường (E01) | | | | | | | |
| PhoBERT tinh chỉnh (E09) | | | | | | | |
| XLM-R large tinh chỉnh (E09) | | | | | | | |
| InfoXLM large tinh chỉnh (E09) | | | | | | | |
| Gemini free giám khảo (E10) | | | | | | | |
| Lookback gộp (E02) | | | | | | | |
| **Chunk-aware (E05)** | | | | | | | |

### Bảng 2 — Định vị chú ý trên ISE-DSC01 (E06)

| Cấu hình | hit@1 | hit@3 | MRR | Sàn ngẫu nhiên |
|---|---|---|---|---|
| Chia theo câu | | | | |
| Cửa sổ 128 token | | | | |

### Bảng 3 — Chọn cách chia chunk (E05)

| Chiến lược | Tham số | macro-F1 dev |
|---|---|---|
| Câu | min_words=5 | |
| Cửa sổ | 64 / stride 32 | |
| Cửa sổ | 128 / stride 64 | |
| Cửa sổ | 256 / stride 128 | |

### Bảng 4 — Ablation nhóm đặc trưng (E12)

| Nhóm đặc trưng | macro-F1 | Chênh lệch |
|---|---|---|
| Chỉ bề mặt | | — |
| + lookback gộp | | |
| + chunk-aware | | |
| + ổn định | | |

### Bảng 5 — Mô hình đọc (E13, E14)

| Mô hình đọc | macro-F1 | ms/mẫu | VRAM MB |
|---|---|---|---|
| Qwen2.5-7B-Instruct | | | |
| Qwen2.5-3B-Instruct | | | |
| Qwen2.5-1.5B-Instruct | | | |
| Sailor2-8B-SFT | | | |

### Bảng 6 — Đối chứng ngoài trên ViWikiFC (E15)

| Phương pháp | Nguồn | Strict Acc | VC Acc | ER Acc | macro-F1 |
|---|---|---|---|---|---|
| InfoXLM large | Bài gốc ViWikiFC | — | — | — | 86,51 |
| BM25 + InfoXLM large | Bài gốc ViWikiFC | 67,00 | — | — | — |
| SemViQA | Bài SemViQA | 80,82 | 83,88 | 95,31 | — |
| **Phương pháp của nhóm** | | | | | |

### Bảng 7 — Khái quát hóa chéo bộ (E16)

| Huấn luyện trên | Đánh giá trên | macro-F1 | Sụt so với cùng bộ |
|---|---|---|---|
| ViHallu | ViHallu | | — |
| ViHallu | ISE-DSC01 | | |
| ISE-DSC01 | ISE-DSC01 | | — |
| ISE-DSC01 | ViHallu | | |

## 6. Các mốc so sánh đã công bố

Ghi lại để không phải tra lại:

- **ViHallu private test:** hệ thống tốt nhất 84,80 % macro-F1; baseline PhoBERT 32,83 %. Lưu ý nhóm không chấm được trên tập này vì không có nhãn — chỉ dùng để định vị, không đặt cạnh số của nhóm trong cùng một cột.
- **ViWikiFC test:** InfoXLM large 86,51 % macro-F1 (verdict prediction); pipeline BM25 + InfoXLM large 67,00 % strict accuracy; SemViQA 80,82 % strict accuracy và 95,31 % evidence retrieval accuracy; BM25 truy xuất top-1 đạt 88,30 % SUPPORTS / 86,93 % REFUTES / 56,67 % NEI.
- **ISE-DSC01 private test:** SemViQA 78,97 % strict accuracy, 82,54 % VC accuracy, 80,91 % ER accuracy.
- **ViFactCheck test:** Gemma 89,90 % macro-F1 với gold evidence, 85,94 % với full context; XLM-R large 88,02 % / 75,42 %; con người 84,93 %.

## 7. Nguyên tắc báo cáo

- Không so số của nhóm với con số leaderboard của bộ mà nhóm tự chia tập. Đặt ở hai bảng khác nhau, giải thích rõ.
- Mọi bảng phải ghi rõ tập nào, chia thế nào, seed bao nhiêu.
- Kết quả âm tính vẫn báo cáo. Nếu chunk-aware không hơn lookback gộp, đó là một kết quả có giá trị và phải phân tích tại sao.
