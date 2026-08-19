# SPEC.md — Đặc tả kỹ thuật

## 1. Tổng quan kiến trúc

Bốn tầng, mỗi tầng là một gói con độc lập, tầng trên chỉ gọi tầng dưới:

```
Tầng 4  serve/       Dịch vụ REST API + giao diện quan sát
Tầng 3  detect/      Bộ phân loại + hiệu chỉnh + ngưỡng quyết định
Tầng 2  features/    Tính chunk-aware lookback ratio và đặc trưng dẫn xuất
Tầng 1  extract/     Nạp mô hình, chạy teacher forcing, trích trọng số chú ý
```

Hai gói ngang hàng phục vụ cả bốn tầng:

```
data/        Nạp và chuẩn hóa bốn bộ dữ liệu
evaluation/  Chỉ số, chia tập, ghi kết quả
```

## 2. Đặc tả từng module

### 2.1. `vihallulens.data`

```python
load_dataset(name: str, split: str) -> pd.DataFrame
```
Trả về DataFrame theo schema chuẩn trong `docs/DATA.md`. `name` thuộc `{"vihallu", "isedsc01", "viwikifc", "vifactcheck"}`.

```python
group_split(df, ratios=(0.8, 0.1, 0.1), seed=42, group_col="context_id") -> dict[str, pd.DataFrame]
```
Chia theo nhóm ngữ cảnh. Bắt buộc kiểm tra không có `context_id` nào xuất hiện ở hai tập; nếu có thì raise.

```python
chunk_context(context: str, strategy: str, **kw) -> list[Chunk]
```
`strategy` thuộc `{"sentence", "token_window"}`. `Chunk` là dataclass gồm `text, char_start, char_end, token_start, token_end, index`.

- `sentence`: tách câu bằng regex tiếng Việt, gộp các câu ngắn hơn 5 từ vào câu trước.
- `token_window`: cửa sổ cố định `window_size` token, chồng lấn `stride`.

```python
locate_evidence_chunk(chunks: list[Chunk], evidence: str) -> int | None
```
Trả về chỉ số chunk chứa câu bằng chứng, hoặc `None` nếu không tìm thấy. Dùng cho ISE-DSC01 và ViWikiFC.

### 2.2. `vihallulens.extract`

```python
class AttentionExtractor:
    def __init__(self, model_name: str, quantization: str = "nf4",
                 max_context_tokens: int = 4096, device: str = "cuda")
    def extract(self, context: str, question: str, response: str,
                chunks: list[Chunk]) -> AttentionFeatures
```

Yêu cầu hiện thực bắt buộc:

- Nạp mô hình với `attn_implementation="eager"` và `torch_dtype=torch.float16`.
- Lượng tử hóa 4-bit NF4 qua `bitsandbytes`, `bnb_4bit_compute_dtype=torch.float16`.
- **Không dùng `output_attentions=True` ở mức `model(...)`.** Thay vào đó đăng ký `forward_hook` trên từng `self_attn` module.
- Trong hook: nhận `attn_weights` shape `(batch, n_heads, q_len, k_len)`, tính ngay các tổng cần thiết theo từng chunk, ghi vào bộ tích lũy, rồi `del` tensor.
- Ghép prompt theo mẫu: ngữ cảnh, câu hỏi, rồi phản hồi. Ghi lại `response_token_start` để biết vùng token nào là phần cần chấm.
- Chạy một lượt forward duy nhất với toàn bộ chuỗi (teacher forcing), không sinh token mới.
- Nếu tổng token vượt `max_context_tokens`, cắt bớt ngữ cảnh từ giữa và ghi cờ `truncated=True` vào metadata.

`AttentionFeatures` là dataclass:

```python
@dataclass
class AttentionFeatures:
    lookback_per_chunk: np.ndarray   # (n_layers, n_heads, n_response_tokens, n_chunks)
    lookback_total: np.ndarray       # (n_layers, n_heads, n_response_tokens)
    self_attention: np.ndarray       # (n_layers, n_heads, n_response_tokens)
    # Mọi giá trị chuẩn hóa theo trung bình trên mỗi token nguồn, không phải tổng
    # khối lượng chú ý — giữ đúng định nghĩa gốc của Lookback Lens.
    n_chunks: int
    truncated: bool
    peak_vram_mb: float
    elapsed_ms: float
```

Lưu ra đĩa dạng `.npz` nén, `float16`. Một file cho mỗi mẫu, tên `{dataset}_{sample_id}.npz`.

### 2.3. `vihallulens.features`

Từ `AttentionFeatures` sinh véc-tơ đặc trưng cho bộ phân loại:

| Nhóm | Đặc trưng | Mô tả |
|---|---|---|
| Cơ bản | `lookback_mean`, `lookback_std` | Tỷ lệ chú ý vào ngữ cảnh, gộp toàn bộ — tái lập Lookback Lens gốc. Tỷ lệ tính theo **trung bình chú ý trên mỗi token**, xem công thức ở mục 1 của `docs/REFERENCES.md` |
| Chunk-aware | `chunk_entropy` | Entropy của phân bố chú ý trên các chunk. Thấp = tập trung. |
| Chunk-aware | `chunk_max_share` | Tỷ trọng chunk được chú ý nhiều nhất |
| Chunk-aware | `chunk_gini` | Hệ số Gini của phân bố |
| Chunk-aware | `top1_top2_gap` | Khoảng cách giữa chunk nhất và chunk nhì |
| Ổn định | `chunk_drift` | Độ lệch trung bình của phân bố chunk giữa các bước sinh liên tiếp |
| Định vị | `evidence_chunk_rank` | Thứ hạng của chunk chứa bằng chứng vàng (chỉ có khi có nhãn bằng chứng) |
| Bề mặt | `response_len`, `lexical_overlap` | Dùng cho baseline tầm thường, xem `docs/EXPERIMENTS.md` |

Mọi đặc trưng tính riêng cho từng cặp (lớp, đầu), sau đó có ba chế độ gộp: `all` giữ nguyên, `mean_over_heads`, `topk_heads` chọn k đầu tốt nhất theo validation.

```python
build_feature_matrix(features: list[AttentionFeatures], config: FeatureConfig) -> np.ndarray
```

### 2.4. `vihallulens.detect`

```python
class LookbackDetector:
    def fit(self, X, y) -> None
    def predict(self, X) -> np.ndarray
    def predict_proba(self, X) -> np.ndarray
    def save(self, path) / load(path)
```

Mặc định `LogisticRegression` đa lớp, `class_weight="balanced"`. Cho phép cấu hình đổi sang `LinearSVC` hoặc `LightGBM` để so sánh, nhưng mặc định phải là tuyến tính vì đó là luận điểm về chi phí thấp.

Kèm module hiệu chỉnh xác suất (`sklearn.calibration.CalibratedClassifierCV`) và hàm chọn ngưỡng theo chi phí sai lệch.

### 2.5. `vihallulens.evaluation`

```python
compute_metrics(y_true, y_pred, y_proba=None) -> dict
```
Trả về `macro_f1`, `accuracy`, `f1_no`, `f1_intrinsic`, `f1_extrinsic`, và khi có `y_proba` thì thêm `ece` (expected calibration error).

```python
log_result(run_name: str, config: dict, metrics: dict, extra: dict) -> None
```
Ghi một dòng JSON vào `results/runs.jsonl`, gồm `timestamp`, `git_commit`, `config_hash`, `config`, `metrics`, `extra`. `extra` bắt buộc chứa `ms_per_sample` và `peak_vram_mb`.

```python
export_table(filter: dict, columns: list[str]) -> pd.DataFrame
```
Sinh bảng kết quả để dán vào báo cáo.

### 2.6. `vihallulens.serve`

FastAPI, ba endpoint:

- `POST /score` — nhận `{context, question, response, chunk_strategy}`, trả `{label, proba, chunk_attention, risk_score, elapsed_ms}`
- `POST /score/batch` — nhận danh sách, trả danh sách
- `GET /health` — trả trạng thái mô hình đã nạp và VRAM đang dùng

Giao diện quan sát: một trang HTML tĩnh, hiển thị ngữ cảnh với các chunk được tô màu theo tỷ trọng chú ý, kèm điểm rủi ro. Không dùng framework frontend nặng — HTML + JS thuần là đủ.

## 3. Cấu hình

Mọi thí nghiệm khai báo bằng một file YAML trong `configs/`. Ví dụ cấu trúc:

```yaml
run_name: e03_chunk_aware_sentence_vihallu
dataset:
  name: vihallu
  split_seed: 42
chunking:
  strategy: sentence
  min_words: 5
extractor:
  model_name: Qwen/Qwen2.5-7B-Instruct
  quantization: nf4
  max_context_tokens: 4096
features:
  groups: [basic, chunk_aware, stability]
  head_aggregation: topk_heads
  topk: 32
detector:
  type: logistic_regression
  class_weight: balanced
```

Validate bằng pydantic. Hash của config ghi kèm kết quả để tái lập.

## 4. Điểm vào CLI

```
scripts/normalize_data.py   --dataset vihallu
scripts/extract_features.py --config configs/xxx.yaml
scripts/train_detector.py   --config configs/xxx.yaml
scripts/evaluate.py         --config configs/xxx.yaml
scripts/probe_vram.py       --model Qwen/Qwen2.5-7B-Instruct --seq-len 4096
```

Mỗi script phải chạy được độc lập trên Kaggle bằng `!python scripts/xxx.py --config ...` sau khi `git clone` và `uv pip install -e .`.

## 5. Kiểm thử

Chỉ test phần không cần GPU:

- `chunk_context` với đầu vào tiếng Việt có dấu, câu ngắn, câu chứa số thập phân
- `locate_evidence_chunk` với bằng chứng nằm vắt qua ranh giới chunk
- `group_split` phải raise khi có rò rỉ nhóm
- Các hàm tính entropy, Gini, drift với đầu vào đã biết đáp án
- Validate schema config

Phần cần GPU chỉ có một smoke test chạy tay, ghi lại trong `results/`.
