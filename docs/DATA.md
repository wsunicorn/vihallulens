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

**Cảnh báo phải ghi vào báo cáo:** ánh xạ NEI sang `extrinsic` là gần đúng, không phải tương đương định nghĩa. NEI nghĩa là "không đủ thông tin để kết luận", còn ảo giác ngoại lai nghĩa là "chứa thông tin không có trong ngữ cảnh". Hai khái niệm giao nhau lớn nhưng không trùng.

**Đã đo ở T13 ngày 20/08/2026 trên 100 mẫu NEI của ViWikiFC, hai người gán độc lập:**

| Chỉ số | Giá trị |
|---|---|
| Hai người **cùng** cho là ngoại lai | **67/100** |
| Lân cho là ngoại lai | 71/100 |
| Minh cho là ngoại lai | 77/100 |
| Tỷ lệ khớp thô | 79,0 % |
| Cohen kappa | **0,505** (trung bình theo thang Landis–Koch) |
| Dương tính giả trên mẫu đối chứng (cả hai) | 1/20 = 5 % |

**Con số phải dùng khi viết báo cáo là 67 %**, tức **khoảng một phần ba nhãn NEI không phải ảo giác ngoại lai**. Đây là con số bảo thủ vì đòi cả hai người cùng đồng ý, và tỷ lệ dương tính giả đo trên 20 mẫu đối chứng chỉ 5 % nên phần sai sót còn sót lại là nhỏ.

Phân rã 33 mẫu còn lại theo cách hiểu của Lân: 22 mẫu `khong` (phát biểu bám sát ngữ cảnh, chỉ là ngữ cảnh không đủ để xác nhận) và 7 mẫu `noi_tai` (phát biểu mâu thuẫn với ngữ cảnh, tức lẽ ra phải là nội tại chứ không phải ngoại lai). Nhóm thứ hai đáng lo hơn: ánh xạ không chỉ *yếu* mà đẩy mẫu sang **sai hẳn lớp**.

**Ranh giới nội tại–ngoại lai là chỗ khó nhất, và khó với cả người:** 8/100 mẫu có một người gán `noi_tai` còn người kia gán `ngoai_lai`. Trên 20 mẫu đối chứng, cả hai đều gặp khó đúng ở đó — nhãn `Refutes` (đáp án đúng là `noi_tai`) chỉ đạt 7/10 và 5/10, trong khi nhãn `Supports` (đáp án `khong`) đạt 9/10 và 7/10.

Cách dùng kết quả này: khi báo cáo số liệu trên ViWikiFC, **không được nói lớp `extrinsic` của bộ này là ảo giác ngoại lai thuần túy**. Phải ghi rõ nó là nhãn NEI ánh xạ sang, với khoảng một phần ba không khớp định nghĩa. Chi tiết cách gán và số liệu đầy đủ nằm ở phần T13 của `TASKS.md`; dữ liệu thô ở `results/nei_mapping_audit.csv`.

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
| Bằng chứng nguyên văn | không có trường | **23.783/23.784** (sửa ở T10, xem dưới) | **20.918/20.919** = 99,995 % (sửa ở T11, xem dưới) | 59,2 % (xác nhận ở T12, biết lý do — xem dưới) |

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

**Đã hiện thực ở T14**, `src/vihallulens/data/splits.py`. Kết quả chia thật:

| Bộ | train | dev | test |
|---|---|---|---|
| ViHallu | 5.598 (80,0 %) | 702 (10,0 %) | 700 (10,0 %) |
| ISE-DSC01 | 29.082 (80,0 %) | 3.653 (10,0 %) | 3.634 (10,0 %) |

Tỷ lệ chỉ **xấp xỉ** 80/10/10 vì chia cả nhóm chứ không chia dòng — một ngữ cảnh phải rơi trọn vào một tập. Sai lệch nhỏ vì nhóm nhỏ: nhóm lớn nhất của ViHallu có 5 dòng, của ISE-DSC01 có 33 dòng, đều dưới 0,1 % cỡ bộ.

Phân bố nhãn sau khi chia lệch không quá 2 điểm phần trăm so với toàn bộ, dù **không hề ép cân bằng nhãn** — chia theo nhóm ngữ cảnh và ép cân bằng nhãn là hai ràng buộc xung khắc, không thỏa mãn đồng thời được. Bảng đầy đủ ở `results/leakage_report.md`.

Chạy hai lệnh này, theo thứ tự:

```
python scripts/normalize_data.py --all
python scripts/split_data.py
```

Chạy lại lệnh thứ hai nhiều lần vẫn ra đúng kết quả cũ: nó gộp các tập lại trước rồi mới chia, nên không cắt 80 % của 80 %. Chạy lại lệnh thứ nhất sau khi đã chia thì nó tự xóa file dev và test cũ, nên không để hai bản của cùng một dòng nằm trong hai file.

## 6. Rò rỉ ngữ cảnh trong split gốc

Đây là phát hiện của nhóm, phải giữ lại và báo cáo:

| Bộ | Ngữ cảnh test có trong train |
|---|---|
| ViWikiFC | 845/845 (100 %) |
| ViFactCheck | 753/758 (99,3 %) |
| ISE-DSC01 (public test) | 1.004/1.319 |
| ViHallu (public test) | 713/919 |

**Đo lại tự động ở T14 ngày 23/08/2026, cả bốn con số khớp chính xác.** Báo cáo đầy đủ sinh tự động ở `results/leakage_report.md`; chạy lại bằng `python scripts/split_data.py`. Bảng dưới bổ sung hai thứ bảng trên không có: tập dev, và **tỷ lệ theo dòng** — con số đáng lo hơn tỷ lệ theo ngữ cảnh, vì nó cho biết bao nhiêu phần điểm số thật sự dựa lên vật liệu đã thấy.

| Bộ | Tập | Rò rỉ theo ngữ cảnh | Rò rỉ theo dòng |
|---|---|---|---|
| ViWikiFC | dev | 836/838 (99,8 %) | 2.088/2.090 (99,9 %) |
| ViWikiFC | test | 845/845 (100 %) | 2.091/2.091 (100 %) |
| ViFactCheck | dev | 495/496 (99,8 %) | 721/723 (99,7 %) |
| ViFactCheck | test | 753/758 (99,3 %) | 1.433/1.447 (99,0 %) |
| **ViHallu** (nhóm tự chia) | dev, test | **0** | **0** |
| **ISE-DSC01** (nhóm tự chia) | dev, test | **0** | **0** |

Hai bộ nhóm tự chia có rò rỉ bằng 0 **theo thiết kế**: `group_split` raise nếu có bất kỳ `context_id` nào lọt vào hai tập, nên con số 0 là bằng chứng chứ không phải kỳ vọng.

File public test của ViHallu và ISE-DSC01 rò rỉ 77,6 % và 76,1 % — nhóm không dùng chúng vì thiếu nhãn, nhưng con số này là bằng chứng rằng split do ban tổ chức phát hành **cũng** rò rỉ, tức việc nhóm tự chia không phải là tự làm khó mình.

Với ViWikiFC và ViFactCheck, nhóm chấp nhận rò rỉ vì phải giữ split gốc để đối chứng — nhưng **không dùng hai bộ này để kết luận về khả năng khái quát hóa**. Task T14 sinh báo cáo rò rỉ tự động.

**Đo lại độc lập ở T11 bằng `context_id`, khớp đúng bảng trên:** ViWikiFC test có 845/845 ngữ cảnh nằm trong train, tức 2.091/2.091 dòng, **100 % rò rỉ**. Tập dev thêm một số chưa từng ghi: 836/838 ngữ cảnh, tức 2.088/2.090 dòng, **99,9 %**. Cả ba tập cộng lại chỉ có 1.481 ngữ cảnh duy nhất, trong khi riêng train đã 1.479 — nghĩa là dev và test gần như **không mang theo ngữ cảnh nào mới**. Việc con số này tái lập đúng bằng một đường tính hoàn toàn khác cũng là một phép thử cho `context_id`.

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

**Đo thật ở T09 ngày 20/08/2026: luật này bắt được 245 mẫu, tức 3,5 %.** Con số này **thấp hơn nhiều** so với tỷ lệ một phần ba mà bài báo ngụ ý cho nhóm `noisy`, và đó là chuyện bình thường chứ không phải lỗi: bỏ dấu chỉ là **một trong bốn** phép nhiễu mà bài báo liệt kê. Một prompt bị hoán vị ký tự hoặc xóa token nhưng vẫn còn dấu thì luật này không bắt được, và nó bị xếp vào `unknown`.

Nói cách khác, `prompt_type = noisy` là một nhóm **độ chính xác cao, độ phủ thấp**. Hệ quả phải nhớ khi làm T35: so sánh không phải là "nhóm noisy với nhóm không noisy" mà là **"nhóm bị bỏ dấu với tất cả phần còn lại"**, trong đó phần còn lại vẫn lẫn những mẫu noisy kiểu khác. Phải viết đúng như vậy trong báo cáo, đừng gọi tắt thành "noisy".

Ba mẫu bắt được, để thấy luật hoạt động đúng:

```
De tai duoc su dung nhieu nhat trong cac luan van tien si A Rap Xe Ut la gi?
Coo bao nhieu nguooi dan Bac Trieu Tien ti nan o mien Nam sau cuoc cai cach ruong ddats?
Truoc khi duoc Ton Trung Son cai to thanh Trung Quoc Quoc dan Dang thi Dang nay da tung...
```

Chú ý mẫu thứ hai: ngoài bỏ dấu còn có nhân đôi ký tự (`Coo`, `nguooi`, `ddats`), tức một mẫu có thể dính nhiều phép nhiễu cùng lúc. Phân bố nhãn trong 245 mẫu này là 68 `no` / 79 `intrinsic` / 98 `extrinsic`, lệch về `extrinsic` hơn tổng thể một chút nhưng cỡ mẫu quá nhỏ để kết luận gì.

**ISE-DSC01.** `claim` map sang `response`, `question` rỗng. `verdict` map theo bảng mục 3. Với nhãn NEI, `evidence` là **`null` trong JSON** chứ không phải chuỗi rỗng — đây là hạn chế đã biết. Tìm `evidence_start` bằng `context.find(evidence)`; nếu không thấy thì đặt `-1` và đếm vào báo cáo. Ghi `meta.domain` và `meta.evidence_given`.

**Sửa số ở T10 ngày 20/08/2026: đúng là 23.783/23.784, không phải 23.785/23.786.** Con số cũ đếm cả **hai mẫu có `evidence` chỉ gồm hai ký tự xuống dòng**, tức một dòng trống. Khoảng trắng là giá trị rỗng duy nhất mà `context.find` vẫn **tìm thấy**: nó trả về vị trí của một dòng trống nào đó trong ngữ cảnh, và mẫu đó mang một `evidence_start` trỏ vào chỗ không có gì trong khi trông vẫn hợp lệ. Đúng hai mẫu, đúng hai đơn vị chênh lệch.

Vì sao phải sửa chứ không mặc kệ hai dòng trên ba vạn: E06 đo hit@1, hit@3 và MRR bằng cách so đoạn được chú ý nhiều nhất với **đoạn chứa bằng chứng vàng**. Một `evidence_start` trỏ vào dòng trống sẽ được E06 coi là đáp án đúng cần trúng. Hai mẫu không đủ làm lệch kết quả, nhưng chi phí sửa bằng không và đây là loại lỗi âm thầm khó truy về sau. Hàm `find_evidence` trong `src/vihallulens/data/schema.py` vì thế coi bằng chứng chỉ gồm khoảng trắng là **không có bằng chứng**.

Ngoài ra còn **đúng một mẫu trượt thật**: bằng chứng ghi `...ông Thiệu nói..` với hai dấu chấm, còn ngữ cảnh chỉ có một dấu chấm rồi xuống dòng. Đây là lỗi của bộ dữ liệu gốc, xử lý theo đúng quy tắc trên: `evidence_start = -1`, đếm vào báo cáo, không dùng khớp gần đúng.

Tổng kết ba loại "không có offset" của bộ này, phải phân biệt được với nhau:

| Loại | Số mẫu | Ý nghĩa |
|---|---|---|
| `evidence` là `null` | 12.583 | Toàn bộ nhãn NEI. Bộ dữ liệu không cung cấp bằng chứng |
| `evidence` chỉ gồm khoảng trắng | 2 | Rác trong dữ liệu gốc, coi như không có |
| Có bằng chứng nhưng không tìm thấy nguyên văn | 1 | Lỗi dữ liệu gốc: dấu chấm thừa |
| **Tìm thấy nguyên văn** | **23.783** | Dùng được cho E06 |

Cột `meta.evidence_given` phân biệt loại một với ba loại kia: `false` nghĩa là bộ dữ liệu không có bằng chứng cho dòng đó, `true` mà `evidence_start = -1` nghĩa là có ghi nhưng không định vị được.

**ViWikiFC.** `claim` map sang `response`, `question` rỗng. Bằng chứng có ở cả ba nhãn, `context.find` phải thành công gần như 100% — nếu tụt nhiều thì có lỗi encoding, dừng lại kiểm tra. Ghi `meta.title`, `meta.link`, `meta.sentence_id`, `meta.evidence_given`.

**Sửa số ở T11 ngày 20/08/2026: 20.918/20.919, tức 99,995 %, không phải tròn 100 %.** Đúng **một** dòng của tập train trượt. Nguyên nhân **không phải encoding**: bằng chứng ghi `...thế kỷ 20 thì NhậtaimBản đã trở thành...`, còn ngữ cảnh ghi `...thế kỷ 20 thì Nhật Bản đã trở thành...` — ba chữ `aim` chèn đè lên dấu cách. Đã kiểm cả NFC lẫn NFD lẫn cắt khoảng trắng, đều không khớp; 20.918 dòng còn lại khớp chính xác, nên encoding của bộ này lành lặn. Đây là lỗi của bộ dữ liệu công bố, xử lý bằng `evidence_start = -1` và đếm vào báo cáo, **không khớp gần đúng**.

Vì sao vẫn giữ phép kiểm tra dù biết nó không bao giờ đạt tròn 100 %: mục đích của nó là bắt **lỗi encoding hàng loạt**, thứ sẽ làm hỏng hàng nghìn dòng trong im lặng trong khi mọi con số khác vẫn đúng. Nên hàm `check_evidence` raise khi số trượt **nhiều hơn** một, chứ không phải khi khác một — ít hơn thì chỉ có thể nghĩa là bộ dữ liệu đã được sửa, và từ chối chạy trên bộ đã sửa thì vô lý.

**Tính chất riêng của bộ này, đo lại ở T11 và xác nhận:** nhãn NEI có bằng chứng tìm thấy **100 % ở cả ba tập** (5.571/5.571 train, 730/730 dev, 677/677 test). Đây là thứ không bộ nào khác có, và là toàn bộ nền tảng của E08.

**Cảnh báo: `pairID` trông như khóa chính nhưng không phải.** Tập train có 16.738 dòng nhưng chỉ 15.903 `pairID` duy nhất: 321 nhóm gồm 835 dòng dùng chung một `pairID`, mỗi nhóm 2–7 dòng. Đo ở T11, các dòng trong cùng nhóm **luôn cùng `evidence` và cùng `gold_label` nhưng khác `claim` 100 %** — tức `pairID` định danh cặp (bằng chứng, nhãn), không định danh mẫu. Code nào dùng nó làm khóa sẽ âm thầm gộp các dòng đó lại. Trong schema chung nó nằm ở `meta.source_id`, còn khóa thật là `sample_id`.

Phân bố nhãn ba tập, đo ở T11 (bảng mục 4 trước đây chỉ có tập train):

| Tập | no | intrinsic | extrinsic | Tổng |
|---|---|---|---|---|
| train | 5.594 | 5.573 | 5.571 | 16.738 |
| dev | 666 | 694 | 730 | 2.090 |
| test | 708 | 706 | 677 | 2.091 |

**ViFactCheck.** `Statement` map sang `response`, `Context` sang `context`, `Evidence` sang `evidence`. Chỉ 59,2% bằng chứng nằm nguyên văn nên `evidence_start = -1` khá thường xuyên; điều này bình thường, không phải lỗi. Ghi `meta.topic`, `meta.author`, `meta.url`, `meta.evidence_given`. Bỏ cột `Unnamed: 0` — nó chỉ là số thứ tự dòng 0..n-1 được lưu kèm.

**T12 ngày 20/08/2026 tìm ra vì sao chỉ 59 %: bằng chứng của bộ này là nhiều câu KHÔNG LIỀN NHAU ghép lại.** Đo trên 2.064 mẫu trượt của tập train:

| Quan sát | Số mẫu |
|---|---|
| 30 ký tự **đầu** của bằng chứng có trong ngữ cảnh | 1.874 |
| Cả 30 ký tự **đầu lẫn 30 ký tự cuối** đều có | 1.741 |
| Không thấy đầu cũng không thấy đuôi | 20 |

Ví dụ điển hình — bằng chứng ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình ILA tiếp nhận và hỗ trợ ...
```

còn ngữ cảnh ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình. Chẳng những được miễn học phí ...
```

Người gán nhãn lấy câu A, **bỏ dấu chấm cuối câu**, rồi nối thẳng câu C ở chỗ khác vào. Cả hai mảnh đều có thật trong ngữ cảnh, chỉ có chuỗi ghép là không.

Đã kiểm và loại trừ hai giả thuyết dễ nghĩ tới: gộp khoảng trắng cứu được **0/2.064**, chuẩn hóa NFC cứu được **0/2.064**. Nên đây không phải chuyện định dạng.

**Hệ quả về mặt thiết kế:** schema chung chỉ có **một** cặp `(evidence_start, evidence_end)`, tức một đoạn liền mạch. Bằng chứng nhiều mảnh rời **về nguyên tắc không biểu diễn được** bằng cấu trúc đó. Con số 59,2 % vì thế không phải "tỷ lệ khớp" mà là **tỷ lệ bằng chứng chỉ có một mảnh**. Ai định làm thí nghiệm định vị bằng chứng trên bộ này (E17) phải mở rộng schema thành danh sách đoạn trước, hoặc chấp nhận chỉ dùng 59 % kia.

**Cảnh báo giống ViWikiFC: `annotation_id` không phải khóa chính.** Tập train có 5.062 dòng nhưng chỉ **1.250** `annotation_id` duy nhất. Nó nằm ở `meta.source_id`; khóa thật là `sample_id`.

**Cột `Topic` không nhất quán hoa thường.** 52 giá trị khác nhau, trong đó có cả `Thể thao` lẫn `THỂ THAO`, cả `Văn hoá` lẫn `Văn hóa` lẫn `VĂN HÓA` lẫn `VĂN HOÁ`. Schema **giữ nguyên văn** để còn truy ngược về nguồn; ai cắt kết quả theo chủ đề phải tự gộp hoa thường và thống nhất `hoá`/`hóa` trước, nếu không sẽ đếm một chủ đề thành bốn.

Phân bố nhãn ba tập, đo ở T12:

| Tập | no | intrinsic | extrinsic | Tổng | Bằng chứng nguyên văn |
|---|---|---|---|---|---|
| train | 1.751 | 1.658 | 1.653 | 5.062 | 2.998 (59,2 %) |
| dev | 256 | 244 | 223 | 723 | 430 (59,5 %) |
| test | 508 | 468 | 471 | 1.447 | 868 (60,0 %) |

## 8. Kho truy xuất ViWikiFC

ViWikiFC có đặc điểm riêng: toàn bộ chỉ 3.814 câu bằng chứng duy nhất từ 73 bài Wikipedia. Task T16 xây một chỉ mục BM25 trên toàn bộ 3.814 câu này để dựng ngữ cảnh nhiều đoạn thật sự — lấy top-k câu thay vì dùng `context` ngắn có sẵn. Đây là cách duy nhất chạy được thí nghiệm chunk-aware trên bộ này.

Lưu chỉ mục tại `data/interim/viwikifc_evidence_corpus.parquet` với cột `evidence_id, text, title, link`.
