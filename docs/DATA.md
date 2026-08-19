# DATA.md — Schema chung và cách chuẩn hóa

## 1. Schema chuẩn

Cả bốn bộ chuẩn hóa về đúng các cột sau, lưu Parquet tại `data/interim/{dataset}_{split}.parquet`.

| Cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `sample_id` | str | có | Định danh duy nhất, dạng `{dataset}_{split}_{index}` |
| `dataset` | str | có | Một trong `vihallu`, `isedsc01`, `viwikifc`, `vifactcheck` |
| `split` | str | có | `train`, `dev`, `test` |
| `context` | str | có | Đoạn văn bản làm bằng chứng nguồn |
| `context_id` | str | có | Hash của `context`, dùng để chia tập theo nhóm |
| `question` | str | không | Câu hỏi. Rỗng với ba bộ kiểm chứng thông tin. |
| `response` | str | có | Văn bản cần chấm. Với ViHallu là phản hồi LLM, ba bộ còn lại là claim. |
| `label` | str | có | `no`, `intrinsic`, `extrinsic` — xem mục 3 |
| `label_original` | str | có | Nhãn gốc chưa ánh xạ, giữ để truy vết |
| `evidence` | str | không | Câu bằng chứng vàng. Rỗng nếu bộ không có. |
| `evidence_start` | int | không | Vị trí ký tự bắt đầu của bằng chứng trong `context`, `-1` nếu không xác định |
| `evidence_end` | int | không | Vị trí ký tự kết thúc, `-1` nếu không xác định |
| `response_is_generated` | bool | có | `True` chỉ với ViHallu |
| `meta` | str (JSON) | có | Các trường riêng của từng bộ |

## 2. Nguồn và cách đọc

Dữ liệu gốc nằm trong `data/raw/`, **để phẳng, không có thư mục con**, đặt tên theo quy ước `{dataset}_{split}.{ext}`. Task T08B đã đổi tên xong ngày 19/08/2026; bảng ánh xạ tên cũ sang tên mới nằm ở `data/raw/MANIFEST.md`.

Đây là danh sách đường dẫn cố định mà code được phép giả định. Thiếu file nào thì raise, không đoán tên khác:

| Bộ | Tập | Đường dẫn | Số dòng | Dùng không |
|---|---|---|---|---|
| ViHallu | train | `data/raw/vihallu_train.csv` | 7.000 | có |
| ViHallu | public test | `data/raw/vihallu_test_public.csv` | 1.000 | **không** — `predict_label` rỗng toàn bộ |
| ISE-DSC01 | train | `data/raw/isedsc01_train.json` | 36.369 | có |
| ISE-DSC01 | public test | `data/raw/isedsc01_test_public.json` | 4.794 | **không** — thiếu `verdict` |
| ISE-DSC01 | private test | `data/raw/isedsc01_test_private.json` | 5.396 | **không** — thiếu `verdict` |
| ViWikiFC | train | `data/raw/viwikifc_train.csv` | 16.738 | có |
| ViWikiFC | dev | `data/raw/viwikifc_dev.csv` | 2.090 | có |
| ViWikiFC | test | `data/raw/viwikifc_test.csv` | 2.091 | có |
| ViFactCheck | train | `data/raw/vifactcheck_train.parquet` | 5.062 | có |
| ViFactCheck | dev | `data/raw/vifactcheck_dev.parquet` | 723 | có |
| ViFactCheck | test | `data/raw/vifactcheck_test.parquet` | 1.447 | có |

Kèm theo hai file mô tả tải từ Hugging Face, không phải dữ liệu: `data/raw/vifactcheck_dataset_card.md` và `data/raw/vifactcheck_gitattributes.txt`.

Cột thực tế của từng file — dùng làm dấu hiệu nhận diện nếu sau này phải nhận lại dữ liệu từ nguồn:

| Bộ | Định dạng | Cột đọc được | Ghi chú |
|---|---|---|---|
| ViHallu | CSV | `id, context, prompt, response, label` | File public test thay `label` bằng `predict_label` rỗng |
| ISE-DSC01 | JSON | `context, claim, verdict, evidence, domain` | JSON là một dict, khóa là số thứ tự dạng chuỗi, mỗi value là một record. Hai file test chỉ có `context, claim` |
| ViWikiFC | CSV | `pairID, evidence, gold_label, link, context, sentenceID, claim, annotator_labels, title` | Dùng cả ba tập |
| ViFactCheck | Parquet | `Unnamed: 0, index, Statement, Context, annotation_id, Topic, Author, Url, labels, Evidence` | Dùng cả ba tập. Bỏ cột `Unnamed: 0` khi đọc |

## 3. Ánh xạ nhãn

| Bộ | Nhãn gốc | Nhãn chuẩn |
|---|---|---|
| ViHallu | `no` | `no` |
| ViHallu | `intrinsic` | `intrinsic` |
| ViHallu | `extrinsic` | `extrinsic` |
| ISE-DSC01 | `SUPPORTED` | `no` |
| ISE-DSC01 | `REFUTED` | `intrinsic` |
| ISE-DSC01 | `NEI` | `extrinsic` |
| ViWikiFC | `Supports` | `no` |
| ViWikiFC | `Refutes` | `intrinsic` |
| ViWikiFC | `Not_Enough_Information` | `extrinsic` |
| ViFactCheck | `0` | `no` |
| ViFactCheck | `1` | `intrinsic` |
| ViFactCheck | `2` | `extrinsic` |

**Cảnh báo phải ghi vào báo cáo:** ánh xạ NEI sang `extrinsic` là gần đúng, không phải tương đương định nghĩa. NEI nghĩa là "không đủ thông tin để kết luận", còn ảo giác ngoại lai nghĩa là "chứa thông tin không có trong ngữ cảnh". Hai khái niệm giao nhau lớn nhưng không trùng. Task T13 yêu cầu kiểm tra thủ công 100 mẫu để báo cáo tỷ lệ khớp.

## 4. Số liệu kiểm tra đã xác nhận

Dùng làm giá trị kỳ vọng trong test tự động. Nếu số liệu sau khi chuẩn hóa lệch khỏi bảng này, dừng lại và báo.

| Chỉ tiêu | ViHallu | ISE-DSC01 | ViWikiFC | ViFactCheck |
|---|---|---|---|---|
| Số mẫu có nhãn | 7.000 | 36.369 | 20.919 | 7.232 |
| Chia tập gốc | chỉ train | chỉ train | 16.738 / 2.090 / 2.091 | 5.062 / 723 / 1.447 |
| Phân bố nhãn (train) | 2.245 / 2.448 / 2.307 | 12.786 / 11.000 / 12.583 | 5.594 / 5.573 / 5.571 | cân bằng |
| Số ngữ cảnh gốc | 3.865 | 4.793 | 1.479 | 1.035 |
| Độ dài ngữ cảnh trung bình | 179,7 từ | 637 từ | 153 từ | 693 từ |
| Số câu mỗi ngữ cảnh (trung vị) | 5 | 19 | 4 | 17 |
| Ngữ cảnh dài nhất | 1.537 từ | 4.805 từ | 600 từ | 3.602 từ |
| Bằng chứng nguyên văn | không có trường | 23.785/23.786 | 100 % cả ba nhãn | 59,2 % |

Thứ tự phân bố nhãn theo `no / intrinsic / extrinsic`.

**Chênh lệch phải ghi vào phần hạn chế của báo cáo:** tập train ISE-DSC01 nhóm tải về có **36.369** mẫu, trong khi bài SemViQA (arXiv:2503.00955) ghi **37.967** mẫu — thiếu 1.598 mẫu. Nhóm không truy được nguyên nhân (có thể do bản phát hành khác nhau của ban tổ chức). Quy tắc xử lý: **báo cáo theo số thực tế 36.369**, nêu rõ chênh lệch này ở chương đánh giá, và **không so trực tiếp** số của nhóm với số SemViQA công bố trên ISE-DSC01 mà không kèm ghi chú.

## 4B. Độ dài tính bằng token — đo ở T05 ngày 19/08/2026

Bảng mục 4 đếm bằng **từ**, còn ngân sách bộ nhớ ở mục 5 của `CLAUDE.md` tính bằng **token**. Đây là số quy đổi thật, đo bằng `python scripts/probe_vram.py` với tokenizer của `Qwen/Qwen2.5-7B-Instruct` trên toàn bộ dữ liệu có nhãn.

Ngữ cảnh, tính trên từng mẫu:

| Bộ | Mẫu | Ngữ cảnh duy nhất | token/từ | p50 | p90 | p99 | Dài nhất |
|---|---|---|---|---|---|---|---|
| ViHallu | 7.000 | 3.865 | 1,35 | 218 | 358 | 549 | 2.347 |
| ISE-DSC01 | 36.369 | 4.793 | 1,33 | 768 | 1.456 | 2.049 | 6.543 |
| ViWikiFC | 16.738 | 1.479 | 1,36 | 183 | 388 | 536 | 805 |
| ViFactCheck | 5.062 | 1.035 | 1,33 | 823 | 1.519 | 2.687 | 4.696 |

Ngữ cảnh + câu hỏi + phản hồi, và số mẫu bị cắt theo `max_context_tokens` (chưa kể phần khung của mẫu prompt, sẽ chốt ở T07):

| Bộ | p50 | p99 | Dài nhất | Vượt 2.048 | Vượt 4.096 |
|---|---|---|---|---|---|
| ViHallu | 308 | 635 | 2.474 | 3 (0,04 %) | 0 (0,00 %) |
| ISE-DSC01 | 796 | 2.072 | 6.622 | 396 (1,09 %) | 6 (0,02 %) |
| ViWikiFC | 214 | 590 | 950 | 0 (0,00 %) | 0 (0,00 %) |
| ViFactCheck | 870 | 2.738 | 4.782 | 142 (2,81 %) | 8 (0,16 %) |

Ba kết luận dùng cho T07 và về sau:

1. **Tokenizer của Qwen2.5 nén tiếng Việt tốt hơn dự đoán:** khoảng **1,33–1,36 token mỗi từ**, không phải 2 như ước lượng ban đầu. Ngữ cảnh 4.805 từ dài nhất của ISE-DSC01 chỉ ra 6.543 token.
2. **`max_context_tokens = 4096` gần như không cắt gì:** tổng cộng 14 mẫu trên cả bốn bộ. Con số này không đủ để ảnh hưởng kết quả, nhưng vẫn phải đặt cờ `truncated=True` và đếm lại khi trích đặc trưng.
3. **Nấc lùi 1 rẻ hơn tưởng:** hạ xuống 2.048 token chỉ cắt thêm 1,09 % mẫu ISE-DSC01 và 2,81 % ViFactCheck. Nếu T07 chật bộ nhớ thì đây là nấc đầu tiên nên dùng, gần như không mất mát.

## 5. Chia tập

- **ViHallu và ISE-DSC01:** chỉ có tập train nên tự chia 80/10/10 theo `context_id`, seed 42.
- **ViWikiFC và ViFactCheck:** giữ nguyên split gốc để so sánh được với số công bố. Không chia lại.

Hàm `group_split` phải kiểm tra và raise nếu phát hiện `context_id` xuất hiện ở nhiều tập.

## 6. Rò rỉ ngữ cảnh trong split gốc

Đây là phát hiện của nhóm, phải giữ lại và báo cáo:

| Bộ | Ngữ cảnh test có trong train |
|---|---|
| ViWikiFC | 845/845 (100 %) |
| ViFactCheck | 753/758 (99,3 %) |
| ISE-DSC01 (public test) | 1.004/1.319 |
| ViHallu (public test) | 713/919 |

Với ViWikiFC và ViFactCheck, nhóm chấp nhận rò rỉ vì phải giữ split gốc để đối chứng — nhưng **không dùng hai bộ này để kết luận về khả năng khái quát hóa**. Task T14 sinh báo cáo rò rỉ tự động.

## 7. Xử lý riêng từng bộ

**ViHallu.** `prompt` map sang `question`. `response_is_generated = True`. Không có trường bằng chứng nên `evidence` rỗng và `evidence_start = -1`.

Bài báo ViHallu (arXiv:2601.04711) nói rõ mỗi ngữ cảnh được sinh **ba loại prompt**, phân bố cân bằng:

| Loại | Cách tạo | Vì sao quan trọng với đề tài |
|---|---|---|
| `factual` | Câu hỏi trực tiếp, đúng ngữ pháp, rút từ nội dung ngữ cảnh | Mức nền |
| `noisy` | Nhiễu có kiểm soát: **bỏ dấu tiếng Việt**, hoán vị ký tự, xóa token, đảo trật tự từ | **Bỏ dấu làm tokenizer cắt ra chuỗi token hoàn toàn khác** → thay đổi số token và vị trí token của câu hỏi, tức thay đổi trực tiếp mẫu số của lookback ratio. Không tách riêng thì hiệu ứng này lẫn vào tín hiệu ảo giác |
| `adversarial` | LLM sinh prompt chứa tiền giả định sai, tiền đề giả, bẫy logic, đảo ngược quan hệ kéo theo | Loại khó nhất, nhiều khả năng là nguồn chính của nhãn `intrinsic` |

Bộ dữ liệu không có cột ghi loại prompt nên phải suy ra và ghi vào `meta.prompt_type`:

- `noisy` — nhận diện được tin cậy: prompt **không chứa ký tự có dấu tiếng Việt** trong khi ngữ cảnh có. Dùng dải Unicode tiếng Việt để kiểm tra, không dùng danh sách từ.
- `factual` và `adversarial` — không tách được bằng luật đơn giản. Ghi `unknown`, **không đoán bừa**.

Ghi thêm `meta.prompt_has_diacritics` (bool) để phân tích sau này kiểm chứng được.

**ISE-DSC01.** `claim` map sang `response`, `question` rỗng. `verdict` map theo bảng mục 3. Với nhãn NEI, `evidence` rỗng — đây là hạn chế đã biết. Tìm `evidence_start` bằng `context.find(evidence)`; nếu không thấy thì đặt `-1` và đếm vào báo cáo. Ghi `meta.domain`.

**ViWikiFC.** `claim` map sang `response`, `question` rỗng. Bằng chứng có ở cả ba nhãn, `context.find` phải thành công 100% — nếu không thì có lỗi encoding, dừng lại kiểm tra. Ghi `meta.title`, `meta.link`, `meta.sentenceID`.

**ViFactCheck.** `Statement` map sang `response`, `Context` sang `context`, `Evidence` sang `evidence`. Chỉ 59,2% bằng chứng nằm nguyên văn nên `evidence_start = -1` khá thường xuyên; điều này bình thường, không phải lỗi. Ghi `meta.topic`, `meta.author`.

## 8. Kho truy xuất ViWikiFC

ViWikiFC có đặc điểm riêng: toàn bộ chỉ 3.814 câu bằng chứng duy nhất từ 73 bài Wikipedia. Task T16 xây một chỉ mục BM25 trên toàn bộ 3.814 câu này để dựng ngữ cảnh nhiều đoạn thật sự — lấy top-k câu thay vì dùng `context` ngắn có sẵn. Đây là cách duy nhất chạy được thí nghiệm chunk-aware trên bộ này.

Lưu chỉ mục tại `data/interim/viwikifc_evidence_corpus.parquet` với cột `evidence_id, text, title, link`.
