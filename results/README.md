# Đọc kết quả thí nghiệm

Thư mục này giữ kết quả của mười chín thí nghiệm (E01–E19). Các tệp được viết cho máy đọc; trang này
cho biết mỗi tệp trả lời câu hỏi nào, mỗi trường nghĩa là gì và hình nào trong quyển vẽ từ tệp đó.
Diễn giải đầy đủ của từng thí nghiệm ở [docs/EXPERIMENTS.md](../docs/EXPERIMENTS.md); bảng nào của
quyển lấy số từ tệp nào nằm ở Phụ lục D.

## Muốn biết điều gì thì mở tệp nào

| Câu hỏi | Xem hình, bảng trong quyển | Tệp số liệu |
|---|---|---|
| Phương pháp nào tốt hơn trên ViHallu? | Hình 6.1, Bảng 6.1 | `runs.jsonl` |
| Chú ý có chỉ đúng đoạn bằng chứng không, ở đầu nào? | Hình 6.2, Bảng 6.2 | `figures/head_hit1.json` |
| Bỏ câu bằng chứng thì chú ý đổi thế nào? | Hình 6.4, Bảng 6.5 | `figures/e08_changes.json` |
| Mỗi nhóm đặc trưng đóng góp bao nhiêu? | Hình 6.5 | `runs.jsonl`, khóa `e12_*` |
| Huấn luyện ở bộ này, dùng ở bộ kia được không? | Hình 6.6 | `runs.jsonl`, khóa `e16_*` |
| Đắt hay rẻ, so với độ chính xác? | Hình 6.7, Bảng 6.9 và 6.10 | `tradeoff.csv`, `e11_self_check.json` |
| Bộ phát hiện sai ở đâu? | Hình 6.8 | `error_analysis.json`, `error_analysis.csv` |
| Chú ý so với cắt bỏ ngữ cảnh? | Hình 6.9 | `runs.jsonl`, khóa `e19_*`; `e19_attribution.jsonl` |
| Chunk-aware có hơn lookback gộp không? | Hình 7.1 | `paired_tests.json` |
| Xác suất của bộ phát hiện có đáng tin không? | Hình 7.2, Bảng 7.2 | `figures/reliability.json`, `calibration.json` |

## Cách đọc nhanh các đại lượng

| Đại lượng | Nghĩa | Đọc thế nào |
|---|---|---|
| `macro_f1` | Trung bình F1 của ba lớp, mỗi lớp tính ngang nhau | 0,33 là đoán ngẫu nhiên, 1 là hoàn hảo |
| `binary_macro_f1` | Như trên, nhưng chỉ hỏi có ảo giác hay không | 0,50 là đoán ngẫu nhiên |
| `*_lo`, `*_hi` | Hai đầu khoảng tin cậy 95 % (bootstrap) | Khoảng càng hẹp, con số càng chắc |
| `delta`, `lo`, `hi` (tệp ghép cặp) | Hiệu giữa hai phương pháp trên cùng các mẫu, và khoảng tin cậy của hiệu | Khoảng chứa 0: chưa phân biệt được hai phương pháp |
| `p_holm` | Giá trị *p* sau khi hiệu chỉnh cho nhiều phép so sánh | Dưới 0,05 mới gọi là có ý nghĩa thống kê |
| `ece` | Độ lệch giữa độ tự tin và tỷ lệ đúng thực tế | 0 là khớp hoàn toàn, càng thấp càng tốt |
| `hit@1` | Tỷ lệ mẫu mà đầu chú ý xếp đoạn chứa bằng chứng lên đầu | So với `hit@1_floor` (mức ngẫu nhiên) |
| `effect` | Cỡ ảnh hưởng rank-biserial | Từ 0,43 trở lên là lớn (Chương 3) |
| `ms_per_sample` | Thời gian xử lý một mẫu, tính bằng mili giây | `null`: lượt chạy không đo thời gian |
| `n_params_trainable` | Số tham số phải huấn luyện | Mô hình đọc giữ nguyên nên không tính |

Ba nhãn: `no` là trung thực, `intrinsic` là ảo giác nội tại (mâu thuẫn với ngữ cảnh), `extrinsic` là
ảo giác ngoại lai (ngữ cảnh không chứa thông tin).

## Từng tệp

### `runs.jsonl`: nhật ký mọi lượt đánh giá

Mỗi dòng là một lượt chạy: `run_name` (mã thí nghiệm và cấu hình), `config` và `config_hash` (cấu hình
đầy đủ), `git_commit`, `timestamp`, `metrics` (các chỉ số) và `extra` (thông tin riêng của thí
nghiệm: `y_pred` là dự đoán từng mẫu test, `head_aggregation_chosen` là cách gộp đầu được chọn trên
dev, `weight_share_per_block` là phần trọng số của từng nhóm đặc trưng…). Một `run_name` có thể xuất
hiện nhiều lần; dòng cuối là lượt đang dùng.

| Khóa | Thí nghiệm |
|---|---|
| `e01_*` | Đặc trưng bề mặt |
| `e02_*`, `e03_*` | Lookback gộp, chunk-aware chia theo câu |
| `e04_*`, `e05_*` | Chia đoạn theo cửa sổ token, cấu hình đối chứng |
| `e06_*`, `e08_*` | Định vị bằng chứng, loại bỏ câu bằng chứng |
| `e07_*` | Ngữ cảnh dài trên ISE-DSC01 |
| `e09_*`, `e10_*` | Tinh chỉnh bộ mã hóa, LLM giám khảo |
| `e12_*` | Đóng góp của từng nhóm đặc trưng |
| `e13_*`, `e14_*` | Sailor2-8B, Qwen2.5-3B và 1.5B |
| `e15_*`, `e16_*`, `e17_*` | ViWikiFC, đánh giá chéo bộ, ViFactCheck |
| `e18_*`, `e19_*` | Gộp theo câu phản hồi, so sánh với cắt bỏ ngữ cảnh |

E11 tổng hợp từ các lượt trên nên không có khóa riêng ở đây; kết quả của E11 nằm ở `tradeoff.csv` và
`e11_self_check.json`.

### `paired_tests.json`: so sánh ghép cặp

`h2` gồm tám cấu hình so chunk-aware (`a`) với lookback gộp (`b`); `others` gồm các so sánh còn lại.
Mỗi mục có macro-F1 của hai bên, hiệu `delta` kèm khoảng `[lo; hi]`, `p_bootstrap`, `p_holm` (chỉ ở
`h2`) và `mcnemar` (số mẫu chỉ bên *a* đúng, chỉ bên *b* đúng, giá trị *p*).

### `calibration.json`: hiệu chỉnh xác suất

Tám cấu hình, mỗi cấu hình bốn bộ phân loại (`lookback_small`, `lookback_full`, `chunk_small`,
`chunk_full`): số tham số, ECE trước và sau temperature scaling (`ece`, `ece_scaled`), hệ số
`temperature` (trên 1 là đang quá tự tin). `differences` là hiệu ECE ghép cặp giữa các bộ.

### `tradeoff.csv`, `e11_self_check.json`, `e11_self_check.jsonl`: chi phí

`tradeoff.csv` có một dòng cho mỗi phương pháp: macro-F1, `ms_moi_mau`, `vram_mb`,
`tham_so_huan_luyen`, `loai_chi_phi`. `e11_self_check.json` là kịch bản tự kiểm tra với Qwen2.5-3B:
A là sinh câu trả lời, B là sinh với chú ý eager, C là đọc chú ý khi sinh, R là đọc lại một lượt;
`contrast` cho phần thời gian phát sinh. Tệp `.jsonl` giữ từng mẫu.

### `error_analysis.csv`, `error_analysis.json`, `error_analysis.png`: phân tích sai sót

Tệp `.csv` có một dòng cho mỗi mẫu sai được chọn: `label` là nhãn gốc, `pred` là dự đoán, `cap_nham`
là cặp nhầm, các cột `co_*` là nhãn mô tả lỗi (1 là có), `confidence` là xác suất của lớp được dự
đoán, `margin` là khoảng cách giữa hai lớp cao nhất. Tệp `.json` là các con số tổng hợp.

### `e19_attribution.jsonl`: điểm cắt bỏ từng đoạn

Mỗi dòng là một mẫu: `gold_chunk` là chỉ số đoạn bằng chứng, `scores` là điểm của từng đoạn khi bị
cắt bỏ; đoạn có điểm cao nhất là đoạn mà phương pháp cắt bỏ chỉ ra.

### `judge_cache.jsonl`, `judge_cache_v1_rerun.jsonl`: câu trả lời của LLM giám khảo

Mỗi dòng là một lượt hỏi Gemini: `verdict` là nhãn bằng mã tiếng Việt, `reason` là lý do mô hình đưa
ra, `confidence` là độ tin cậy do mô hình tự báo. Bộ nhớ đệm giúp không phải gọi lại API. Tệp thứ hai giữ
lượt chạy lại tiêu chí rút gọn tháng 11/2026 (`e10_gemini_judge_v1_rerun`): cùng mô hình, cùng prompt nên
khóa trùng với lượt tháng 08, phải để ở tệp riêng.

### `feasibility.jsonl`: thời gian và bộ nhớ trên Tesla T4

Các lượt đo thời gian, bộ nhớ của ba cỡ Qwen2.5, kèm thông tin GPU trong lúc đo (`gpu_telemetry`).

### `figures/`: số liệu rút gọn để vẽ hình

Dựng lại bằng `python scripts/build_figure_data.py` (cần dữ liệu trong `data/processed/`), rồi vẽ
bằng `python docs/media/src/result_charts.py`. Script dừng nếu số tính lại khác số đã công bố.

| Tệp | Nội dung |
|---|---|
| `head_hit1.json` | Bảng 27 lớp × 28 đầu, mỗi ô là hit@1 của đầu đó, trên hai bộ dữ liệu; `spearman` là tương quan hạng giữa hai bảng |
| `e08_changes.json` | Tần suất mức thay đổi của từng đặc trưng trên 1.836 cặp; `aligned` là tỷ lệ cặp đúng hướng dự đoán |
| `reliability.json` | Từng nhóm độ tự tin: số mẫu, độ tự tin trung bình, tỷ lệ đúng, trước và sau hiệu chỉnh |

### Các tệp còn lại

| Tệp | Nội dung |
|---|---|
| `leakage_report.md` | Kiểm tra rò rỉ ngữ cảnh và kích thước các tập |
| `nei_mapping_audit*.csv`, `nei_mapping_audit_HUONGDAN.md` | Gán nhãn thủ công nhãn NEI và bản hướng dẫn |
| `t30b/`, `t30c/` | Đối chiếu kiểu số của Sailor2-8B và Qwen2.5-7B |
| `t40/` | Kiểm thử thư viện, dịch vụ REST và hệ RAG minh họa trên Kaggle |
