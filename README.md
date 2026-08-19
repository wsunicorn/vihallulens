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
uv pip install -e .
```

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

Chạy một thí nghiệm:

```bash
python scripts/extract_features.py --config configs/example.yaml
python scripts/train_detector.py   --config configs/example.yaml
python scripts/evaluate.py         --config configs/example.yaml
```

## Chạy trên Kaggle

Notebook trong `notebooks/` chỉ làm ba việc: clone repo, cài đặt, gọi script. Không viết logic trong notebook.

```python
!git clone https://github.com/wsunicorn/vihallulens.git /kaggle/working/vihallulens
%cd /kaggle/working/vihallulens
!pip install -e . -q
!python scripts/extract_features.py --config configs/example.yaml
```

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
