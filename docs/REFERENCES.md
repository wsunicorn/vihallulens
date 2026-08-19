# REFERENCES.md — Tài liệu nền

> Bản PDF nằm ở `reference_papers/` trên máy cá nhân. Thư mục đó **gitignore** vì là tài liệu bản quyền của bên thứ ba — mỗi người tự tải từ link arXiv bên dưới.

## 1. Bài nền phải đọc kỹ

### Lookback Lens (EMNLP 2024) — phương pháp mà đề tài mở rộng trực tiếp

Chuang, Y.-S., Qiu, L., Hsieh, C.-Y., Krishna, R., Kim, Y., Glass, J. *Lookback Lens: Detecting and Mitigating Contextual Hallucinations in Large Language Models Using Only Attention Maps.*
arXiv:2407.07071 · mã nguồn: github.com/voidism/Lookback-Lens · PDF cục bộ: `reference_papers/LookBackLens/2407.07071v2.pdf`

Công thức gốc, phải tái lập đúng ở T20 trước khi so sánh với chunk-aware:

```
                    A_t^{l,h}(context)
LR_t^{l,h} = ─────────────────────────────────────
             A_t^{l,h}(context) + A_t^{l,h}(new)

A_t^{l,h}(context) = (1/N)     · Σ_{i=1..N}       α_{l,h,i}      ← trung bình trên N token ngữ cảnh
A_t^{l,h}(new)     = (1/(t-1)) · Σ_{j=N+1..N+t-1} α_{l,h,j}      ← trung bình trên các token đã sinh
```

Bốn điểm dễ làm sai khi tái lập:

1. **Là trung bình theo token, không phải tổng khối lượng chú ý.** Chia cho `N` và `t-1`. Nếu lấy tổng, kết quả sẽ lệch mạnh vì ngữ cảnh dài hơn phần sinh rất nhiều.
2. Véc-tơ đặc trưng của một bước `t` là **nối toàn bộ `L × H`** giá trị `LR`, rồi **lấy trung bình các bước trong span** thành một véc-tơ duy nhất.
3. Bộ phân loại là `sklearn.linear_model.LogisticRegression` — đúng như quyết định đã chốt trong `CLAUDE.md`.
4. Bài gốc có hai cách lấy span: **predefined span** (khi có nhãn theo đoạn) và **sliding window kích thước 8 token**. Đề tài của nhóm có nhãn ở mức toàn phản hồi nên dùng nguyên phản hồi làm một span; ghi rõ khác biệt này trong báo cáo.

Cách nhóm hiện thực, chốt ở T07 sau khi đo: lưu **hai** biến thể tính từ cùng một ma trận. `lookback_total` lấy X là toàn bộ token trước phản hồi, đúng như công thức trên, và là bản E02 dùng. `lookback_context` chỉ đếm ngữ cảnh truy xuất, dễ diễn giải hơn và là nền của phần chunk-aware. Token phản hồi đầu tiên không được chấm vì mẫu số `t-1` bằng 0.

Khác biệt về bài toán phải nêu khi so sánh: bài gốc phân loại **nhị phân** (factual / hallucinated) và báo cáo **AUROC**; đề tài phân loại **ba lớp** và báo cáo **macro-F1**. Không đặt hai con số cạnh nhau.

Hai kết quả của bài gốc đáng đối chiếu: bộ phân loại tuyến tính trên lookback ratio ngang hoặc hơn bộ phân loại dùng toàn bộ hidden state; và bộ dò huấn luyện trên mô hình 7B dùng lại được cho 13B không cần huấn luyện lại — đây là gợi ý trực tiếp cho E13 và E14.

### ViHallu (DSC 2025) — bộ dữ liệu chính

Nguyen, A. T.-H. và cộng sự. *DSC2025 – ViHallu Challenge: Detecting Hallucination in Vietnamese LLMs.*
arXiv:2601.04711 · PDF cục bộ: `reference_papers/ViHallu/2601.04711v1.pdf` · giấy phép CC-BY-SA 4.0

Điểm cần nhớ: 10.000 bộ ba, ngữ cảnh lấy từ UIT-ViQuAD 2.0 (Wikipedia), độ dài 88–1.500 token. Phản hồi do GPT-4o sinh với decoding tất định. Nhãn gán **theo ngữ cảnh, không theo tri thức thế giới** — đúng khung bài toán của đề tài. 111 đội nộp bài, tốt nhất macro-F1 84,80 %, baseline bộ mã hóa 32,83 %. Ba loại prompt: factual, noisy, adversarial — xem mục 7 của `docs/DATA.md`.

## 2. Cơ sở so sánh trên tiếng Việt

| Công trình | Vai trò | Nguồn |
|---|---|---|
| **SemViQA** (Tran, D. X. và cộng sự, 2025) | SOTA trên cả ISE-DSC01 lẫn ViWikiFC. **Nhóm tác giả cùng Trường ĐH Công nghiệp TP.HCM** — có mã nguồn, thư viện PyPI và checkpoint công khai, và có thể hỏi trực tiếp qua GVHD nếu cần làm rõ cách chấm điểm. | arXiv:2503.00955 · github.com/DAVID-NGUYEN-S16/SemViQA · pypi.org/project/semviqa · huggingface.co/SemViQA |
| **ViWikiFC** (Le, H. T. và cộng sự, 2024) | Bộ đối chứng ngoài; bài gốc công bố số theo từng nhãn nên đối chiếu trực tiếp được. | arXiv:2405.07615 · huggingface.co/datasets/NghiemAbe/ViWikiFC |
| **ViFactCheck** (Tran, T.-H. và cộng sự, AAAI 2025) | Bộ chuyển miền tin tức, dự phòng. | arXiv:2412.15308 · github.com/QuangDiy/ViFactCheck |

Số liệu công bố dùng làm mốc so sánh: xem mục 6 của `docs/EXPERIMENTS.md`.

## 3. Công trình đọc để định vị, không tái lập

| Công trình | Vai trò |
|---|---|
| ReDeEP (ICLR 2025, arXiv:2410.11414) | Hướng nội tại thay thế, dùng để đối chiếu trong chương cơ sở lý thuyết |
| LettuceDetect (arXiv:2502.17125) | Đại diện hướng bộ mã hóa |
| RAGTruth (ACL 2024, arXiv:2401.00396) | Bộ ngữ liệu ảo giác tiếng Anh, tham chiếu về cách gán nhãn |
| RAGOps (arXiv:2506.03401) | Bối cảnh vận hành, dùng cho phần mở đầu |
| PhoBERT (Findings of EMNLP 2020) | Mô hình nền cho baseline tiếng Việt |
