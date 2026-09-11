# vihallulens

Phát hiện ảo giác cho hệ thống RAG tiếng Việt bằng tín hiệu chú ý nội tại của LLM.

Khóa luận tốt nghiệp ngành Khoa học dữ liệu — Trường Đại học Công nghiệp TP.HCM, học kỳ 1 năm học 2026–2027.

## Ý tưởng

Khi một mô hình ngôn ngữ đọc lại một câu trả lời cùng với ngữ cảnh đã truy xuất, phân bố trọng số chú ý của nó lên từng đoạn ngữ cảnh mang thông tin về việc câu trả lời có bám vào bằng chứng hay không. Đề tài khai thác tín hiệu này để phân loại ba lớp: không ảo giác, ảo giác nội tại, ảo giác ngoại lai — chi phí gần bằng không vì tận dụng lại phép tính mô hình vốn đã thực hiện, và không cần gọi dịch vụ trả phí nào.

Đóng góp chính là **chunk-aware lookback ratio**: tách tỷ lệ chú ý theo từng đoạn ngữ cảnh thay vì gộp toàn bộ thành một khối như phương pháp Lookback Lens gốc.

## Chuẩn bị trước khi bắt đầu

Làm hết danh sách này trước khi chạy task đầu tiên. Ô nào chưa xong sẽ chặn task tương ứng ở cột bên phải.

### Tài khoản và khóa

| Việc | Chi tiết | Chặn task nào |
|---|---|---|
| Tài khoản Kaggle + **xác minh số điện thoại** | Không xác minh thì không bật được GPU và không bật được Internet trong notebook. Quota 30 giờ GPU mỗi tuần | T06 trở đi |
| Tài khoản Hugging Face + read token | Qwen2.5, PhoBERT, XLM-R, InfoXLM đều không khóa quyền truy cập nên không bắt buộc, nhưng có token thì đỡ bị giới hạn tốc độ tải | T06 |
| `GEMINI_API_KEY` từ aistudio.google.com | Chỉ dùng cho baseline LLM giám khảo, free tier, cần trước tuần 5 | T19 |
| Tài khoản Google | Dự phòng Colab khi Kaggle hết quota | — |
| Mời thành viên thứ hai vào repo GitHub với quyền write | Settings → Collaborators | T03 |

Khóa API để trong `.env` ở máy, và trong **Add-ons → Secrets** khi chạy trên Kaggle. Không bao giờ viết thẳng vào notebook hay YAML.

### Máy cá nhân

- Python 3.11
- `uv` — cài bằng `pip install uv` hoặc `winget install astral-sh.uv`
- Git, và một tài khoản GitHub đã đăng nhập `gh` hoặc đã cấu hình credential helper

### Dữ liệu trên Kaggle

Dữ liệu khoảng 248 MB và **không nằm trong repo**, nên notebook không clone kèm được. Đã tải sẵn lên Kaggle Dataset:

**`unicorn1209/vihallulens`** — kaggle.com/datasets/unicorn1209/vihallulens (version 1, 248,47 MB, 14 file để phẳng đúng tên chuẩn).

Chỉ cần attach dataset vào notebook, **không cần biết Kaggle gắn nó vào đâu**. Kaggle đã dùng cả `/kaggle/input/<slug>/` lẫn `/kaggle/input/datasets/<chủ>/<slug>/`, nên code tự dò thay vì đoán:

```python
from vihallulens.data.paths import find_raw_dir

print(find_raw_dir())   # tìm thư mục chứa vihallu_train.csv
```

Thứ tự ưu tiên: `--data-dir` truyền tay → biến môi trường `VIHALLULENS_DATA_DIR` → `data/raw` → các vị trí dưới `/kaggle/input`. Truyền `--data-dir` sai đường dẫn thì báo lỗi chứ không âm thầm dùng thư mục khác.

Nếu tải lại dataset ở bản mới, **giữ nguyên tên file** theo `data/raw/MANIFEST.md` — đổi tên là code gãy.

Repo là public nên notebook Kaggle clone bằng HTTPS không cần token, chỉ cần bật Internet trong phần cài đặt notebook.

Kết quả chạy ghi vào `/kaggle/working/`, tải về máy rồi commit từ máy. Không đẩy commit trực tiếp từ notebook.

## Bắt đầu

```bash
git clone https://github.com/wsunicorn/vihallulens.git
cd vihallulens
uv sync --extra dev      # tạo .venv đúng phiên bản trong uv.lock, kèm pytest/ruff/matplotlib
```

`uv.lock` khóa đúng phiên bản từng thư viện (kể cả `scikit-learn 1.9.x` mà bundle trong
`models/` cần), nên máy khác `uv sync` là được y hệt môi trường này. Chạy lệnh bằng
`uv run python ...` hoặc kích hoạt `.venv`.

Tải bốn bộ dữ liệu từ nguồn ở mục [Dữ liệu](#dữ-liệu), đặt vào `data/raw/` **đúng tên file dưới đây** rồi chuẩn hóa:

```
data/raw/
├── MANIFEST.md                     # có sẵn trong repo, ánh xạ tên file gốc sang tên chuẩn
├── vihallu_train.csv
├── vihallu_test_public.csv         # không có nhãn, không dùng
├── isedsc01_train.json
├── isedsc01_test_public.json       # thiếu verdict, không dùng
├── isedsc01_test_private.json      # thiếu verdict, không dùng
├── viwikifc_train.csv
├── viwikifc_dev.csv
├── viwikifc_test.csv
├── vifactcheck_train.parquet
├── vifactcheck_dev.parquet
└── vifactcheck_test.parquet
```

Rồi chuẩn hóa cả bốn bộ về schema chung trong `data/interim/`:

```bash
python scripts/normalize_data.py --dataset vihallu
python scripts/normalize_data.py --dataset isedsc01
python scripts/normalize_data.py --dataset viwikifc
python scripts/normalize_data.py --dataset vifactcheck
```

Chạy một thí nghiệm — trích đặc trưng trên GPU rồi chấm trên CPU:

```bash
python scripts/extract_features.py --config configs/e03_chunk_sentence_vihallu.yaml --split train
python scripts/extract_features.py --config configs/e03_chunk_sentence_vihallu.yaml --split dev
python scripts/extract_features.py --config configs/e03_chunk_sentence_vihallu.yaml --split test
python scripts/run_chunk_aware.py  --config configs/e03_chunk_sentence_vihallu.yaml \
    --save-bundle models/e03_chunk_aware.pkl
```

Bước thứ hai chọn cách gộp đầu chú ý trên tập dev, chấm tập test đúng một lần, ghi kết quả vào
`results/runs.jsonl`, và với `--save-bundle` thì lưu bộ phát hiện đã khớp **kèm công thức dựng
cột của nó** — đó là thứ thư viện và API nạp lên.

## Dùng thư viện

```python
from vihallulens import HallucinationDetector

detector = HallucinationDetector.from_pretrained("models/e03_chunk_aware.pkl")
result = detector.score(
    context="Hà Nội là thủ đô của Việt Nam. Thành phố nằm bên sông Hồng.",
    question="Hà Nội nằm ở đâu?",
    response="Hà Nội nằm bên sông Hồng.",
)
result.label               # 'no' | 'intrinsic' | 'extrinsic'
result.risk_score          # 1 − P(no): xác suất phản hồi có ảo giác, kiểu nào cũng tính
result.proba               # {'no': …, 'intrinsic': …, 'extrinsic': …}
result.chunk_attention     # mỗi đoạn ngữ cảnh: văn bản, vị trí ký tự, tỷ trọng chú ý nhận được
result.to_dict()           # đúng schema POST /score trong docs/SPEC.md
```

`from_pretrained` nạp bundle rồi nạp **đúng mô hình đọc mà bundle được khớp cùng** (tên mô hình,
lượng tử hóa, lớp bị bỏ, kiểu số đều nằm trong bundle), nên cần GPU — Qwen2.5-7B NF4 chiếm khoảng
8,3 GB. Mọi thứ khác chạy trên CPU. Bộ phát hiện mặc định `models/e03_chunk_aware.pkl` nặng 11,5 KB
và có 579 tham số.

Hai con số cần đọc đúng. `risk_score` là con số một hệ RAG nên hành động theo: Bảng 1 và Bảng 7
trong `docs/EXPERIMENTS.md` đo được bộ phát hiện tách "trung thực hay không" tốt hơn hẳn tách hai
loại ảo giác, và chỉ phán đoán nhị phân mới chuyển được giữa các bộ dữ liệu. `chunk_attention` là
tỷ trọng chú ý trung bình trên mọi lớp và đầu — chính đại lượng E06 đã đo hit@1 87,8 % so với đoạn
bằng chứng vàng — không phải thứ bộ phân loại đọc.

## Chạy dịch vụ REST

```bash
python scripts/serve.py --bundle models/e03_chunk_aware.pkl --port 8000
```

Trang quan sát ở `http://127.0.0.1:8000/` — dán ngữ cảnh, câu hỏi, câu trả lời, bấm Chấm: ngữ cảnh được tô màu theo tỷ trọng chú ý mỗi đoạn nhận được, kèm điểm rủi ro và xác suất ba lớp. HTML + JS thuần, không framework. Các route theo `docs/SPEC.md` §2.6, tài liệu tương tác ở `http://127.0.0.1:8000/docs`:

| Endpoint | Nhận | Trả |
|---|---|---|
| `POST /score` | `{context, response, question?, chunk_strategy?}` | `{label, proba, risk_score, chunk_attention, elapsed_ms, …}` |
| `POST /score/batch` | `{items: [...]}`, tối đa 64 | `{results: [...], elapsed_ms}` |
| `GET /health` | — | mô hình đã nạp chưa, tên mô hình, VRAM đang giữ, bộ sinh đã nạp chưa, số request đã chấm |
| `POST /demo/ask` | `{question, top_k?}` | tài liệu truy xuất, câu trả lời sinh ra, và điểm của nó (mục dưới) |
| `GET /demo/corpus` | — | 21 tài liệu của kho minh họa |
| `GET /` | — | trang quan sát |

Mô hình nạp **một lần lúc khởi động** (khoảng một phút với Qwen2.5-7B NF4 trên T4). `GET /health`
trả `loading` cho tới khi nạp xong, `ok` sau đó, `error` kèm lý do nếu nạp hỏng; hai route chấm
điểm trả **503** trong lúc chờ. `chunk_strategy` phải trùng cách chia đoạn bộ phát hiện được khớp
cùng — gửi cách khác bị từ chối **400** chứ không bị lặng lẽ bỏ qua, vì năm đặc trưng hình dạng
mô tả phân bố trên đúng các đoạn ấy.

## Hệ RAG minh họa

Dịch vụ kèm một hệ RAG tối giản trên **21 tài liệu ngắn về Việt Nam** (`serve/demo_corpus.jsonl`):
truy xuất BM25, sinh câu trả lời bằng **Qwen2.5-3B nạp ở `bfloat16`** (cùng chat template đã chốt
ở mục 8 `CLAUDE.md`, giải mã tham lam), rồi chấm câu trả lời ấy bằng bộ phát hiện. Vì sao không
dùng chính bản 7B `float16` đang nạp để sinh: lớp 27 của nó tràn số — bộ phát hiện né được bằng
cách không đọc lớp đó, nhưng LM head thì không né được, và logit NaN cho ra toàn `!`. Vì sao không
nạp thêm 7B `bfloat16`: hai bản 7B không nằm chung một card 16 GB (thử ngày 11/09, hết bộ nhớ lúc
nạp). 3B là cỡ lớn nhất của bậc thang còn vừa cạnh bộ đọc; nạp lười ở câu hỏi đầu tiên, đổi bằng
`scripts/serve.py --generator`. Trên trang quan sát là ô "Hỏi hệ
RAG"; qua API là `POST /demo/ask {question, top_k?}`; qua dòng lệnh:

```bash
python scripts/demo_rag.py --question "Đỉnh núi cao nhất Đông Dương là gì?" --out results/demo.json
```

Lập luận chi phí biên ở Bảng 8 `docs/EXPERIMENTS.md` ("lượt đọc hệ RAG dù sao cũng trả") vì thế
mang một điều khoản phần cứng: trên T4 ở `float16`, mô hình đọc không phải là bộ sinh, và bộ sinh
phải là một mô hình khác. Trên card lớn hơn có `bfloat16` gốc, một bản 7B duy nhất làm cả hai việc.

## Chạy bằng Docker

```bash
docker compose up --build
```

Một lệnh, lên dịch vụ ở `http://localhost:8000`. Cần Docker có GPU (NVIDIA Container Toolkit trên
Linux, Docker Desktop với WSL2 GPU trên Windows). Lần đầu tải trọng số Qwen2.5-7B (~15 GB) vào
volume `hf-cache`; các lần sau dùng lại. Trọng số **không nướng vào ảnh**. `GET /health` báo `ok`
khi mô hình đã nạp — `HEALTHCHECK` của ảnh cũng dựa vào đúng trạng thái đó, không phải chỉ cổng mở.

`HF_TOKEN` không bắt buộc; có thì đặt trong `.env` cạnh `docker-compose.yml`, compose tự đọc. Không
bao giờ viết khóa vào Dockerfile hay YAML.

## Chạy trên Kaggle

Notebook trong `notebooks/` chỉ làm ba việc: clone repo, cài đặt, gọi script. Không viết logic trong notebook.

```python
!git clone https://github.com/wsunicorn/vihallulens.git /kaggle/working/vihallulens
%cd /kaggle/working/vihallulens
!pip install -q --no-deps -e .                 # torch/transformers dùng bản Kaggle có sẵn
!pip install -q -U bitsandbytes rank-bm25 "scikit-learn>=1.9,<2"
!python scripts/extract_features.py --config configs/example.yaml --split test
```

`--no-deps` là cố ý: kéo cả cây phụ thuộc về sẽ cài lại torch mất hàng chục phút và có thể lệch
CUDA của Kaggle. Đổi lại phải tự cài những gói Kaggle không có sẵn — bài học T27 và T40.

Khóa API lấy từ Kaggle Secrets, không viết thẳng vào notebook:

```python
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
```

## Làm việc với Claude Code

Đầu mỗi phiên, mở Claude Code ở thư mục gốc repo rồi gõ đúng câu này:

```
Đọc CLAUDE.md và TASKS.md. Làm task chưa hoàn thành có số nhỏ nhất.
```

## Tài liệu

| File | Nội dung |
|---|---|
| `CLAUDE.md` | Ngữ cảnh dự án, ràng buộc, quyết định đã chốt, quy trình làm việc |
| `TASKS.md` | Danh sách việc tuần tự — nguồn sự thật về tiến độ |
| `docs/SPEC.md` | Đặc tả kỹ thuật: kiến trúc, module, API |
| `docs/DATA.md` | Schema chung, đường dẫn dữ liệu và cách chuẩn hóa bốn bộ |
| `data/raw/MANIFEST.md` | Ánh xạ tên file gốc sang tên chuẩn, kèm số dòng đã đối chiếu |
| `docs/EXPERIMENTS.md` | Kế hoạch thực nghiệm và bảng kết quả |
| `docs/REFERENCES.md` | Bài báo nền, công thức gốc Lookback Lens và các mốc so sánh |

## Dữ liệu

Bốn bộ tiếng Việt công khai. **Không commit vào repo** — `data/` nằm trong `.gitignore`, chỉ `data/raw/MANIFEST.md` được commit.

| Bộ | Vai trò | File trong `data/raw/` | Nguồn |
|---|---|---|---|
| ViHallu | Bộ chính | `vihallu_train.csv` | codabench.org/competitions/10153 |
| ISE-DSC01 | Kiểm chứng chunk-aware | `isedsc01_train.json` | codalab.lisn.upsaclay.fr/competitions/15497 |
| ViWikiFC | Đối chứng ngoài | `viwikifc_{train,dev,test}.csv` | huggingface.co/datasets/NghiemAbe/ViWikiFC |
| ViFactCheck | Dự phòng | `vifactcheck_{train,dev,test}.parquet` | huggingface.co/datasets/tranthaihoa/vifactcheck |

Tên file theo quy ước `{dataset}_{split}.{ext}`, để phẳng trong `data/raw/`. File tải về từ nguồn có tên khác — xem bảng ánh xạ ở `data/raw/MANIFEST.md` và mục 2 của `docs/DATA.md`.

## Nhóm

Nguyễn Ngọc Lân (22635801) · Nguyễn Tấn Minh (22643511)
GVHD: ThS. Trương Vĩnh Linh
