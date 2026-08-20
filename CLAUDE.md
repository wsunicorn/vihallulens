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

- **Phần cứng: GPU Tesla T4 16 GB** trên Kaggle/Colab. Mọi thứ phải chạy vừa trong 16 GB. P100 cũng 16 GB nhưng là kiến trúc Pascal (compute capability 6.0) trong khi `bitsandbytes` NF4 khuyến nghị 7.5 trở lên — **chạy thử một lượt rồi mới coi P100 là phương án dự phòng**, đừng mặc định nó tương đương T4.
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
| Kiểu số khi tính | `float16`, **bỏ lớp 27** của Qwen2.5-7B. Đo ở T07: lớp 27 tràn số ở 20/20 mẫu, 27 lớp còn lại khớp `float32` với sai lệch trung bình 0,07 % thang đo và lỗi không tăng dần về cuối. `float32` sạch nhưng chậm 3,6 lần |
| Mẫu số lookback | Lưu **cả hai**: `lookback_total` tính cả token khung như bài gốc (dùng cho E02), `lookback_context` chỉ tính ngữ cảnh (dùng cho phần chunk-aware) |
| Chia chunk | Làm **cả hai** cách (theo câu và theo cửa sổ token) rồi so sánh — đây là một thí nghiệm riêng, không phải chọn sẵn |
| Chia tập | Theo ngữ cảnh (group split), seed 42, tỷ lệ 80/10/10 |

## 4. Bốn bộ dữ liệu và vai trò

| Bộ | Vai trò | File trong `data/raw/` | Ghi chú quan trọng |
|---|---|---|---|
| **ViHallu** | Bộ chính, xác định khung bài toán | `vihallu_train.csv` | Duy nhất có `response` do LLM sinh thật (GPT-4o). Chỉ tập train 7.000 mẫu có nhãn. File `vihallu_test_public.csv` không có nhãn, bỏ qua. |
| **ISE-DSC01** | Kiểm chứng `chunk-aware` | `isedsc01_train.json` | Ngữ cảnh dài 21–73 câu. Bằng chứng nguyên văn 23.783/23.784 (số cũ 23.785/23.786 đếm nhầm hai mẫu có bằng chứng chỉ là dòng trống, sửa ở T10). **Nhãn NEI không có bằng chứng.** Hai file `isedsc01_test_public.json` và `isedsc01_test_private.json` thiếu `verdict`, bỏ qua. |
| **ViWikiFC** | Đối chứng ngoài + thí nghiệm ảo giác ngoại lai | `viwikifc_train.csv`, `viwikifc_dev.csv`, `viwikifc_test.csv` | Duy nhất có bằng chứng cho cả nhãn NEI (100% nguyên văn). Tập test có nhãn. |
| **ViFactCheck** | Dự phòng, thí nghiệm chuyển miền | `vifactcheck_train.parquet`, `vifactcheck_dev.parquet`, `vifactcheck_test.parquet` | Chỉ làm nếu tuần 14–15 còn thời gian. |

Tên file theo quy ước `{dataset}_{split}.{ext}`, để phẳng ngay trong `data/raw/`, không có thư mục con. Bảng ánh xạ từ tên gốc lúc tải về nằm ở `data/raw/MANIFEST.md` — file duy nhất trong `data/` được commit.

Chi tiết schema, đường dẫn đầy đủ và cách chuẩn hóa: xem `docs/DATA.md`. Bài báo nền và công thức gốc phải tái lập: xem `docs/REFERENCES.md`.

## 5. Rủi ro số một

Bật `output_attentions` vô hiệu hóa FlashAttention và buộc materialize ma trận chú ý đầy đủ. Với ngữ cảnh 4.805 từ của ISE-DSC01, việc làm ngây thơ sẽ tràn 16 GB.

**Cách duy nhất được chấp nhận:** đăng ký forward hook trên từng lớp, tính đặc trưng lookback ngay trong hook, giải phóng tensor trước khi sang lớp tiếp theo. Không bao giờ giữ toàn bộ tuple attention của tất cả các lớp.

### Ngân sách bộ nhớ — đây là phép tính, không phải phỏng đoán

Qwen2.5-7B-Instruct có 28 lớp và 28 đầu chú ý. Ma trận chú ý một lớp ở fp16 chiếm `n_heads × seq_len² × 2` byte:

| Độ dài chuỗi | Một lớp | Giữ cả 28 lớp cùng lúc |
|---|---|---|
| 2.048 token | 0,23 GB | 6,6 GB |
| 4.096 token | 0,94 GB | 26 GB — tràn |
| 8.192 token | 3,76 GB | 105 GB — tràn |

Cột phải là hậu quả của `output_attentions=True` dùng ngây thơ. Cột giữa là mức mà thiết kế hook giữ lại. Cộng trọng số 4-bit khoảng 5–6 GB, đỉnh thực tế ở 4.096 token ước chừng 8–9 GB (có thêm bản sao tạm khi softmax, KV cache và activation) — vẫn nằm trong 16 GB.

Kết luận: **T07 kiểm tra hook có cài đúng không, không phải kiểm tra bài toán có khả thi về mặt vật lý không.** Phần vật lý đã tính xong.

**Bộ nhớ bậc hai, thời gian tuyến tính — đừng lẫn hai thứ.** Bảng trên nói về bộ nhớ và vẫn đúng. Thời gian thì khác: đo ở T08 trên T4, chi phí là **khoảng 1,05 ms mỗi token prompt**, gần như hằng số từ 371 tới 2.492 token (mũ đo được `k ≈ 1,00`). Lý do là ở dải này các phép nhân ma trận của MLP và việc giải nén trọng số NF4 vẫn chi phối, ma trận chú ý chưa đủ lớn để lấn. Hệ quả thực dụng: muốn tiết kiệm **bộ nhớ** thì cắt độ dài, muốn tiết kiệm **thời gian** thì giảm số mẫu.

**Đo ms/mẫu thì mỗi cấu hình một phiên GPU riêng.** Ở T08, hai lượt chạy nối nhau trong cùng phiên cho thấy ba mức độ dài có khối lượng tính toán *y hệt nhau* vẫn chậm đi 10–15 % ở lượt sau — nhiều khả năng do T4 tản nhiệt thụ động bị hạ xung sau vài phút chạy liên tục. Vì vậy mọi so sánh chi phí giữa các mô hình (E13 Sailor2, E14 bậc thang 3B/1.5B) phải chạy mỗi cấu hình một phiên riêng hoặc đo xen kẽ, nếu không phần hạ xung sẽ bị tính nhầm thành khác biệt giữa các mô hình.

### Ba điều dễ hiểu sai về thiết kế hook

1. **Hook không giảm được đỉnh bộ nhớ của chính lớp đó.** Attention eager đã tạo đủ ma trận `(q_len × k_len)` bên trong module *trước khi* hook chạy. Hook chỉ quyết định giữ lại bao nhiêu. Muốn hạ dưới mức 0,94 GB một lớp thì phải **thay hàm tính attention** để chỉ tính các hàng truy vấn ứng với token phản hồi — đó là đổi kiến trúc, phải hỏi trước theo mục 6.
2. **Hook có thể trả về giá trị mới để thay output.** Đây là cách chặn `all_self_attns` tích lũy: tính đặc trưng xong thì trả về `(attn_output, None)`.
3. **Việc `output` của hook có chứa `attn_weights` hay không phụ thuộc phiên bản `transformers`.** Có phiên bản chỉ trả về khi bật `output_attentions=True`, có phiên bản luôn trả về. Phải kiểm tra thực tế ở T07 rồi **ghim đúng phiên bản** trong `pyproject.toml`, kèm một test khẳng định `attn_weights is not None`.

### Nếu T07 không qua

Dừng lại và **hỏi người dùng**, không tự đổi hướng đề tài. Trước khi bàn tới phương án thay thế phải đi hết các nấc lùi dưới đây theo thứ tự:

| Nấc | Cách làm | Hiệu quả |
|---|---|---|
| 1 | Hạ `max_context_tokens` từ 4.096 xuống 2.048 | **Chỉ mua được bộ nhớ, không mua được thời gian.** Đo ở T08 bằng hai lượt chạy thật: VRAM đỉnh 8.428 → 6.305 MB (giảm 25 %), nhưng dự báo giờ GPU lại *tăng* 10,32 → 11,58 giờ. Lý do ở mục ngay trên bảng này. Về mất mát dữ liệu thì nấc này rẻ: đo ở T05, chỉ cắt thêm 1,09 % mẫu ISE-DSC01 và 2,81 % ViFactCheck — xem mục 4B `docs/DATA.md` |
| 2 | Chỉ trích một phần lớp, ví dụ 8 trong 28 | Giảm gần tuyến tính; Lookback Lens cho thấy ít đầu mang phần lớn tín hiệu |
| 3 | Thay hàm attention để chỉ tính hàng truy vấn của token phản hồi | Hiệu quả lớn nhất nhưng là đổi kiến trúc — phải hỏi |
| 4 | Lùi Qwen2.5-3B rồi 1.5B | Cùng họ, chỉ đổi `model_name` trong YAML |
| 5 | Xử lý ngữ cảnh theo cửa sổ trượt | Đổi mẫu số của lookback ratio — phải trích lại toàn bộ đặc trưng |
| 6 | Đổi sang P100 hoặc Colab khi Kaggle hết quota | Xem cảnh báo về P100 ở mục 2 |

Đi hết sáu nấc mà vẫn không lấy được attention thì mới bàn tới hướng thay thế đã nêu trong đề xuất đề tài.

## 6. Quy trình làm việc bắt buộc

1. **Luôn đọc `TASKS.md` trước.** Làm đúng task tiếp theo chưa tick, theo thứ tự. Không nhảy cóc.
2. **Một task một PR.** Commit message tiếng Việt, mở đầu bằng mã task, ví dụ `T09: chuẩn hóa ViHallu về schema chung`.
3. **Trước khi tick hoàn thành**, phải chạy được lệnh nêu trong mục "Tiêu chí hoàn thành" của task và dán output vào PR.
4. **Nếu một task cần quyết định chưa có trong file này** — ví dụ chọn thư viện mới, đổi kiến trúc, thêm phụ thuộc nặng — **DỪNG LẠI và hỏi người dùng.** Không tự quyết.
5. **Không viết code cho task chưa tới.** Nếu thấy task sau cần thứ gì đó, ghi chú vào PR, đừng làm trước.
6. Sau mỗi task, cập nhật `TASKS.md`: đổi `[ ]` thành `[x]`, ghi ngày hoàn thành, **và viết phần diễn giải ngay dưới task đó** — task này để làm gì, đã làm gì, kết quả số ra sao, học được gì. `TASKS.md` vừa là nguồn sự thật về tiến độ vừa là sổ tay giải thích, nên viết sao cho người chưa biết gì đọc cũng hiểu: thuật ngữ xuất hiện lần đầu thì giải thích ngay tại chỗ.

## 7. Những điều không được làm

- Không thêm phụ thuộc nặng (deepspeed, ray, vllm) mà không hỏi.
- Không tải mô hình lớn hơn 8B.
- Không viết code giả định có nhiều GPU.
- Không sửa dữ liệu gốc trong `data/raw/`. Chỉ đọc.
- Không hardcode đường dẫn tuyệt đối của máy cá nhân.
- Không commit file lớn hơn 10 MB.
- Không tự ý đổi seed hoặc tỷ lệ chia tập.
- Không đổi mẫu prompt đưa vào mô hình đọc sau khi đã chốt ở T07 (xem mục 8).
- Không commit khóa API, kể cả trong notebook đã chạy.

## 8. Mẫu prompt đưa vào mô hình đọc

Mẫu prompt quyết định vị trí token của ngữ cảnh, câu hỏi và phản hồi — tức quyết định toàn bộ việc tính chỉ số attention. **Đổi mẫu giữa chừng làm mọi đặc trưng đã trích trở nên vô giá trị.**

Quy tắc: ở Task T07, chốt đúng một mẫu, ghi nguyên văn vào mục này của `CLAUDE.md`, rồi không đổi nữa. Nếu buộc phải đổi, phải trích lại toàn bộ đặc trưng và ghi vào Nhật ký chặn trong `TASKS.md`.

**Đã chốt ngày 19/08/2026 ở T07.** Dùng chat template chính thức của mô hình qua `tokenizer.apply_chat_template`, ngữ cảnh và câu hỏi ở lượt `user`, phản hồi cần chấm ở lượt `assistant`. Hiện thực nằm ở `src/vihallulens/extract/prompt.py` — file đó là nguồn sự thật, mục này là bản ghi để đọc nhanh.

```
<|im_start|>system
Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.<|im_end|>
<|im_start|>user
Ngữ cảnh:
{context}

Câu hỏi: {question}<|im_end|>
<|im_start|>assistant
{response}<|im_end|>
```

Bốn quy tắc đi kèm, cũng không được đổi:

1. **Không có câu hỏi thì bỏ hẳn khối câu hỏi.** Ba bộ kiểm chứng thông tin không có câu hỏi; in ra dòng `Câu hỏi:` rỗng sẽ thêm token vô nghĩa và dịch chuyển mọi vị trí.
2. **Vùng ngữ cảnh là đúng chuỗi `{context}`**, không gồm dòng tiêu đề `Ngữ cảnh:`. Chunk chia trên chuỗi này.
3. **Vùng phản hồi là đúng chuỗi `{response}`**, không gồm token `<|im_start|>assistant`.
4. **Token khung được xử lý theo hai cách, lưu song song.** `lookback_total` tính chúng vào mẫu số đúng như bài Lookback Lens gốc, nơi X là toàn bộ chuỗi đầu vào — đây là bản E02 phải dùng để gọi là tái lập. `lookback_context` loại chúng ra, chỉ đếm ngữ cảnh truy xuất, dễ diễn giải hơn và là nền của phần chunk-aware. Chi phí thêm gần bằng không vì cả hai tính từ cùng một ma trận.
5. **Token phản hồi đầu tiên không được chấm.** Nó chưa có token nào đứng trước để so, nên tỷ lệ của nó luôn bằng 1 bất kể mô hình làm gì — và ở `float16` có khi thành 0 do underflow. Cả hai đều vô nghĩa. Trục token của mọi mảng đặc trưng vì thế có độ dài `n_response_tokens - 1`.

Vị trí hai vùng được tìm bằng cách **dò chuỗi trong prompt đã render** rồi ánh xạ sang token qua `return_offsets_mapping`, chứ không đếm ký tự khung. Nhờ vậy nếu chat template của mô hình khác (Sailor2 ở E13) có khác đôi chút thì vị trí vẫn đúng, không lệch âm thầm.

## 9. Bố cục repo

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
│   ├── EXPERIMENTS.md     # kế hoạch thực nghiệm và bảng kết quả
│   └── REFERENCES.md      # bài báo nền, công thức gốc Lookback Lens
├── notebooks/             # notebook chạy trên Kaggle, chỉ gọi hàm từ src
├── results/               # kết quả thí nghiệm dạng jsonl/csv
├── scripts/               # entry point CLI
├── src/vihallulens/
└── tests/
```
