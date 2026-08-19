# CLAUDE.md — Ngữ cảnh dự án

> File này Claude Code đọc đầu tiên trong mọi phiên. Đọc hết trước khi viết dòng code nào.

## 1. Dự án là gì

Khóa luận tốt nghiệp ngành Khoa học dữ liệu, Trường Đại học Công nghiệp TP.HCM.

**Tên đề tài:** Nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt dựa trên tín hiệu chú ý nội tại.

**Ý tưởng một câu:** Khi một LLM đọc lại một câu trả lời cùng với ngữ cảnh đã truy xuất, phân bố trọng số chú ý của nó lên từng đoạn ngữ cảnh chứa tín hiệu đủ để phân biệt câu trả lời trung thực, ảo giác nội tại và ảo giác ngoại lai — mà không cần gọi LLM giám khảo nào.

**Đóng góp cốt lõi:** `chunk-aware lookback ratio` — tách tỷ lệ chú ý theo từng đoạn ngữ cảnh thay vì gộp toàn bộ ngữ cảnh thành một khối như Lookback Lens gốc.

**Nhóm:** Nguyễn Ngọc Lân (SV1, MSSV 22635801) và Nguyễn Tấn Minh (SV2, MSSV 22643511). GVHD: ThS. Trương Vĩnh Linh.

**Hạn:** tháng 12/2026. Bảo vệ hội đồng tuần 18 (30/11 – 06/12/2026).

## 2. Ràng buộc cứng

Những điều này KHÔNG được thương lượng khi viết code:

- **Phần cứng: GPU Tesla T4 16 GB hoặc P100 16 GB** trên Kaggle/Colab. Mọi thứ phải chạy vừa trong 16 GB.
- **Không có ngân sách API.** Chỉ dùng Gemini free tier ở quy mô rất nhỏ để dựng baseline LLM-giám-khảo. Không bao giờ viết code giả định có OpenAI/Anthropic API key.
- **Mọi thứ phải tái lập được** trên máy khác: seed cố định, config ghi ra file, không có magic number nằm trong code.
- **Ngôn ngữ:** code và docstring viết tiếng Anh; tài liệu, báo cáo, commit message viết tiếng Việt.
- **Hạn mức GPU Kaggle: 30 giờ mỗi tuần.** Task nặng phải chạy đầu tuần để còn thời gian sửa nếu hỏng. Luôn ước tính thời gian chạy trước khi bấm.
- **Khóa API để trong `.env`**, đọc bằng `python-dotenv`. `.env` phải nằm trong `.gitignore`. Không bao giờ ghi khóa vào code, config YAML, notebook hay commit.

## 3. Các quyết định đã chốt — không tự ý đổi

| Hạng mục | Quyết định |
|---|---|
| Python | 3.11 |
| Quản lý thư viện | `uv` + `pyproject.toml` |
| Bố cục | `src/` layout, tên gói `vihallulens` |
| Lint/format | `ruff` (thay cả black lẫn flake8) |
| Kiểm thử | `pytest`, chỉ test logic thuần, không test phần cần GPU |
| Cấu hình | YAML + `pydantic` để validate |
| Theo dõi thí nghiệm | Ghi file cục bộ `results/*.jsonl` + `results/*.csv`. **Không dùng W&B, không cần tài khoản.** |
| Git | `main` + nhánh riêng mỗi người, gộp qua Pull Request |
| Dữ liệu | Không commit vào Git. Để trong `data/` và gitignore, **trừ `data/raw/MANIFEST.md`**. |
| Mô hình đọc chính | `Qwen/Qwen2.5-7B-Instruct`, lượng tử hóa 4-bit NF4 |
| Bậc thang lùi | `Qwen/Qwen2.5-3B-Instruct` → `Qwen/Qwen2.5-1.5B-Instruct` |
| Mô hình ablation | `sail/Sailor2-8B-SFT` (mở rộng từ Qwen2.5, dùng chung code path) |
| Trích attention | `attn_implementation="eager"` + forward hook, cộng dồn trong hook |
| Chia chunk | Làm **cả hai** cách (theo câu và theo cửa sổ token) rồi so sánh — đây là một thí nghiệm riêng, không phải chọn sẵn |
| Chia tập | Theo ngữ cảnh (group split), seed 42, tỷ lệ 80/10/10 |

## 4. Bốn bộ dữ liệu và vai trò

| Bộ | Vai trò | File trong `data/raw/` | Ghi chú quan trọng |
|---|---|---|---|
| **ViHallu** | Bộ chính, xác định khung bài toán | `vihallu_train.csv` | Duy nhất có `response` do LLM sinh thật (GPT-4o). Chỉ tập train 7.000 mẫu có nhãn. File `vihallu_test_public.csv` không có nhãn, bỏ qua. |
| **ISE-DSC01** | Kiểm chứng `chunk-aware` | `isedsc01_train.json` | Ngữ cảnh dài 21–73 câu. Bằng chứng nguyên văn 23.785/23.786. **Nhãn NEI không có bằng chứng.** Hai file `isedsc01_test_public.json` và `isedsc01_test_private.json` thiếu `verdict`, bỏ qua. |
| **ViWikiFC** | Đối chứng ngoài + thí nghiệm ảo giác ngoại lai | `viwikifc_train.csv`, `viwikifc_dev.csv`, `viwikifc_test.csv` | Duy nhất có bằng chứng cho cả nhãn NEI (100% nguyên văn). Tập test có nhãn. |
| **ViFactCheck** | Dự phòng, thí nghiệm chuyển miền | `vifactcheck_train.parquet`, `vifactcheck_dev.parquet`, `vifactcheck_test.parquet` | Chỉ làm nếu tuần 14–15 còn thời gian. |

Tên file theo quy ước `{dataset}_{split}.{ext}`, để phẳng ngay trong `data/raw/`, không có thư mục con. Bảng ánh xạ từ tên gốc lúc tải về nằm ở `data/raw/MANIFEST.md` — file duy nhất trong `data/` được commit.

Chi tiết schema, đường dẫn đầy đủ và cách chuẩn hóa: xem `docs/DATA.md`.

## 5. Rủi ro số một

Bật `output_attentions` vô hiệu hóa FlashAttention và buộc materialize ma trận chú ý đầy đủ. Với ngữ cảnh 4.805 từ của ISE-DSC01, việc làm ngây thơ sẽ tràn 16 GB.

**Cách duy nhất được chấp nhận:** đăng ký forward hook trên từng lớp, tính đặc trưng lookback ngay trong hook, giải phóng tensor trước khi sang lớp tiếp theo. Không bao giờ giữ toàn bộ tuple attention của tất cả các lớp.

Nếu Task T05–T08 thất bại, dừng lại và báo cho người dùng. Không tự ý đổi hướng đề tài.

## 6. Quy trình làm việc bắt buộc

1. **Luôn đọc `TASKS.md` trước.** Làm đúng task tiếp theo chưa tick, theo thứ tự. Không nhảy cóc.
2. **Một task một PR.** Commit message tiếng Việt, mở đầu bằng mã task, ví dụ `T09: chuẩn hóa ViHallu về schema chung`.
3. **Trước khi tick hoàn thành**, phải chạy được lệnh nêu trong mục "Tiêu chí hoàn thành" của task và dán output vào PR.
4. **Nếu một task cần quyết định chưa có trong file này** — ví dụ chọn thư viện mới, đổi kiến trúc, thêm phụ thuộc nặng — **DỪNG LẠI và hỏi người dùng.** Không tự quyết.
5. **Không viết code cho task chưa tới.** Nếu thấy task sau cần thứ gì đó, ghi chú vào PR, đừng làm trước.
6. Sau mỗi task, cập nhật `TASKS.md`: đổi `[ ]` thành `[x]` và ghi ngày hoàn thành.

## 7. Những điều không được làm

- Không thêm phụ thuộc nặng (deepspeed, ray, vllm) mà không hỏi.
- Không tải mô hình lớn hơn 8B.
- Không viết code giả định có nhiều GPU.
- Không sửa dữ liệu gốc trong `data/raw/`. Chỉ đọc.
- Không hardcode đường dẫn tuyệt đối của máy cá nhân.
- Không commit file lớn hơn 10 MB.
- Không tự ý đổi seed hoặc tỷ lệ chia tập.
- Không đổi mẫu prompt đưa vào mô hình đọc sau khi đã chốt ở T07 (xem mục 9).
- Không commit khóa API, kể cả trong notebook đã chạy.

## 9. Mẫu prompt đưa vào mô hình đọc

Mẫu prompt quyết định vị trí token của ngữ cảnh, câu hỏi và phản hồi — tức quyết định toàn bộ việc tính chỉ số attention. **Đổi mẫu giữa chừng làm mọi đặc trưng đã trích trở nên vô giá trị.**

Quy tắc: ở Task T07, chốt đúng một mẫu, ghi nguyên văn vào mục này của `CLAUDE.md`, rồi không đổi nữa. Nếu buộc phải đổi, phải trích lại toàn bộ đặc trưng và ghi vào Nhật ký chặn trong `TASKS.md`.

```
MẪU PROMPT ĐÃ CHỐT: (điền ở T07)
```

## 10. Bố cục repo

```
.
├── CLAUDE.md              # file này
├── TASKS.md               # danh sách việc tuần tự — nguồn sự thật về tiến độ
├── README.md
├── pyproject.toml
├── configs/               # YAML cấu hình thí nghiệm
├── data/
│   ├── raw/               # dữ liệu gốc, chỉ đọc, gitignore trừ MANIFEST.md
│   │   ├── MANIFEST.md        # ánh xạ tên file gốc sang tên chuẩn (commit)
│   │   ├── vihallu_train.csv
│   │   ├── vihallu_test_public.csv
│   │   ├── isedsc01_train.json
│   │   ├── isedsc01_test_public.json
│   │   ├── isedsc01_test_private.json
│   │   ├── viwikifc_{train,dev,test}.csv
│   │   └── vifactcheck_{train,dev,test}.parquet
│   ├── interim/           # dữ liệu đã chuẩn hóa: {dataset}_{split}.parquet
│   └── processed/         # đặc trưng đã trích, gitignore
├── docs/
│   ├── SPEC.md            # đặc tả kỹ thuật
│   ├── DATA.md            # schema và chuẩn hóa dữ liệu
│   └── EXPERIMENTS.md     # kế hoạch thực nghiệm và bảng kết quả
├── notebooks/             # notebook chạy trên Kaggle, chỉ gọi hàm từ src
├── results/               # kết quả thí nghiệm dạng jsonl/csv
├── scripts/               # entry point CLI
├── src/vihallulens/
└── tests/
```
