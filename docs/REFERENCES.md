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

## 4. Cập nhật 2025–2026 — đọc để định vị kết quả (thêm 26/09/2026)

Bốn công trình dưới đây **chưa có trong quyển báo cáo** (ReDeEP, LettuceDetect, RAGTruth ở mục 3
thì đã trích). Cách dùng từng công trình trong quyển ghi ở mục 8 của `docs/EXPERIMENTS.md`; đầu
việc đưa vào chương 2 là T42B.

| Công trình | Nói gì | Vì sao quan trọng với đề tài |
|---|---|---|
| **Hallucinated Span Detection with Multi-View Attention Features** (arXiv:2504.04335) | Đặc trưng chú ý theo từng token phản hồi — chú ý trung bình nhận vào, entropy chú ý vào và ra, cho mỗi (lớp, đầu) — đưa vào Transformer + CRF gán nhãn chuỗi. RAGTruth, Llama-3-8B-Instruct: F1 56,3 / 55,3 / 42,7 (QA / Data2Text / tóm tắt); LLM tinh chỉnh 59,7 / 50,4 / 41,6; **Lookback Lens 13,2 / 0,0 / 0,0** | Xác nhận độc lập rằng **gộp trung bình cả phản hồi là nút thắt**, không phải đặc trưng — cùng kết luận chương 7 của quyển tự đo ra. Cũng là bằng chứng hướng "hình dạng phân bố chú ý" (entropy) là một hướng nghiên cứu có thật, chỉ khác trục: họ đo trên trục token phản hồi, đề tài đo trên trục đoạn ngữ cảnh. Nền cho E18 |
| **ContextCite** (Cohen-Wang và cộng sự, NeurIPS 2024) | Quy trách nhiệm câu trả lời cho nguồn ngữ cảnh bằng cắt bỏ nguồn và mô hình thay thế tuyến tính; vượt các baseline dùng trọng số chú ý, gradient, độ tương đồng. Kết luận **trọng số chú ý thô thường không đáng tin để quy trách nhiệm** | Câu hội đồng dễ hỏi nhất về E06: "chú ý có phải lời giải thích không?". Đề tài đo *định vị trên bằng chứng vàng* chứ không đo *quy trách nhiệm*, nên hai kết luận không mâu thuẫn — nhưng phải nói rõ ranh giới đó. Nền cho E19 |
| **ARC-JSD** (arXiv:2505.16415, ICLR 2026) | Quy trách nhiệm bằng độ lệch Jensen–Shannon giữa phân phối đầu ra khi đủ ngữ cảnh và khi cắt bỏ từng đoạn; không tinh chỉnh, không gradient, không mô hình thay thế | Cùng thiết kế "cắt bỏ một đoạn rồi đo lại" với E08, dùng cho mục đích khác. Là phương pháp đối chứng trực tiếp cho E19 |
| **LUMINA** (arXiv:2509.21875, ICLR 2026) | Tách mức dùng ngữ cảnh ngoài (khoảng cách phân phối) và mức dùng tri thức nội tại (biến đổi token qua các lớp); hơn các phương pháp đo mức dùng ngữ cảnh trước đó tới +13 % AUROC trên HalluRAG | Đại diện mới nhất của hướng nội tại "ngữ cảnh đối lại tri thức tham số", cùng họ với ReDeEP. Đặt cạnh Lookback Lens ở bảng 2.1 của quyển để chương 2 không dừng ở 2024 |

Ghi chú khi trích: số của ba bài tiếng Anh đo **nhị phân hoặc mức đoạn trên RAGTruth, bằng F1 hoặc
AUROC**; đề tài đo **ba lớp mức phản hồi bằng macro-F1**. Theo quy tắc ở mục 7 của
`docs/EXPERIMENTS.md`, không đặt các số này cạnh số của nhóm trong cùng một cột.

