BỘ CÔNG THƯƠNG

**TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP TP. HỒ CHÍ MINH**

**KHOA CÔNG NGHỆ THÔNG TIN**

![Logo Trường Đại học Công nghiệp TP. Hồ Chí Minh](media/logo_iuh.png){width="2.51in" height="0.72in"}

**NGUYỄN NGỌC LÂN — MSSV 22635801**

**NGUYỄN TẤN MINH — MSSV 22643511**

> **NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG PHÁT HIỆN ẢO GIÁC CHO MÔ HÌNH NGÔN NGỮ LỚN TĂNG CƯỜNG TRUY XUẤT TIẾNG VIỆT DỰA TRÊN TÍN HIỆU CHÚ Ý NỘI TẠI**

**Ngành: Khoa học dữ liệu**

**Giảng viên hướng dẫn: ThS. Trương Vĩnh Linh**

THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026

<div style="page-break-after: always"></div>

BỘ CÔNG THƯƠNG

**TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP TP. HỒ CHÍ MINH**

**KHOA CÔNG NGHỆ THÔNG TIN**

![Logo Trường Đại học Công nghiệp TP. Hồ Chí Minh](media/logo_iuh.png){width="2.51in" height="0.72in"}

**NGUYỄN NGỌC LÂN — MSSV 22635801**

**NGUYỄN TẤN MINH — MSSV 22643511**

> **NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG PHÁT HIỆN ẢO GIÁC CHO MÔ HÌNH NGÔN NGỮ LỚN TĂNG CƯỜNG TRUY XUẤT TIẾNG VIỆT DỰA TRÊN TÍN HIỆU CHÚ Ý NỘI TẠI**

**Ngành: Khoa học dữ liệu**

**Giảng viên hướng dẫn: ThS. Trương Vĩnh Linh**

THÀNH PHỐ HỒ CHÍ MINH, THÁNG 12 NĂM 2026

<div style="page-break-after: always"></div>

**INDUSTRIAL UNIVERSITY OF HO CHI MINH CITY**

**FACULTY OF INFORMATION TECHNOLOGY**

![Logo Industrial University of Ho Chi Minh City](media/logo_iuh.png){width="2.51in" height="0.72in"}

**NGUYEN NGOC LAN — 22635801**

**NGUYEN TAN MINH — 22643511**

> **RESEARCH AND DEVELOPMENT OF A HALLUCINATION DETECTION SYSTEM FOR VIETNAMESE RETRIEVAL-AUGMENTED LARGE LANGUAGE MODELS BASED ON INTERNAL ATTENTION SIGNALS**

**Major: Data Science**

**Supervisor: MSc. Truong Vinh Linh**

HO CHI MINH CITY — DECEMBER 2026

<div style="page-break-after: always"></div>

# ABSTRACT {#abstract .unnumbered}

**Research and development of a hallucination detection system for Vietnamese retrieval-augmented large language models based on internal attention signals**

Retrieval-augmented generation (RAG) grounds a large language model (LLM) in retrieved passages, yet it still states things those passages do not support. Vietnamese detectors today either fine-tune a large encoder or call a judge LLM per answer. This thesis asks whether the attention maps of an open reading model, read from one forward pass, can detect such contextual hallucination.

We reproduce Lookback Lens, which measures per head how much of the response's attention goes to the context rather than to itself, and extend it into a chunk-aware lookback ratio: the same attention split over context chunks, its shape summarised by five statistics. Per-layer forward hooks keep a 4-bit Qwen2.5-7B-Instruct inside one 16 GB Tesla T4.

Across nineteen experiments on four Vietnamese corpora, a linear classifier over 756 lookback ratios (2,271 parameters) reaches a three-class macro-F1 of 0.745, matching a fine-tuned PhoBERT-large (0.749) and beating it on intrinsic hallucination. The strongest head points at the gold-evidence chunk in 87.8% of ISE-DSC01 samples, 14.3 times the random floor, and deleting that sentence moves all four pre-registered shape statistics as predicted, and the head beats context ablation (0.850 vs 0.733) at one-eleventh of the cost. The chunk-aware gain itself is not significant (0.757 against 0.745); three-class detectors do not transfer across corpora, while the binary decision does (0.78).

The detector ships as a Python library, a REST service with an attention view and a Docker image; future work covers span-level scoring.

**Keywords: hallucination detection, retrieval-augmented generation, attention analysis, Vietnamese natural language processing, model calibration.**

<div style="page-break-after: always"></div>

# TÓM TẮT {#tom-tat .unnumbered}

**Nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt dựa trên tín hiệu chú ý nội tại**

Sinh văn bản tăng cường truy xuất (RAG) giúp mô hình ngôn ngữ lớn bám vào ngữ cảnh truy xuất được, song mô hình vẫn phát biểu những điều ngữ cảnh không bảo chứng. Các bộ phát hiện cho tiếng Việt hiện nay hoặc tinh chỉnh trọn một bộ mã hóa lớn, hoặc gọi mô hình giám khảo cho từng câu trả lời. Khóa luận xét xem bản đồ chú ý của một mô hình đọc mã nguồn mở, lấy trong một lượt truyền xuôi, có đủ tín hiệu để phát hiện ảo giác theo ngữ cảnh hay không.

Khóa luận tái lập Lookback Lens — đo ở từng đầu chú ý phần chú ý mà phản hồi dành cho ngữ cảnh thay vì cho chính nó — rồi mở rộng thành chunk-aware lookback ratio: tách tỷ lệ ấy theo từng đoạn ngữ cảnh và mô tả hình dạng bằng năm đại lượng. Forward hook trên từng lớp giúp Qwen2.5-7B-Instruct 4 bit chạy vừa một card Tesla T4 16 GB.

Qua mười chín thí nghiệm trên bốn bộ dữ liệu tiếng Việt, bộ phân loại tuyến tính trên 756 tỷ lệ lookback (2.271 tham số) đạt macro-F1 ba lớp 0,745, ngang PhoBERT-large đã tinh chỉnh (0,749) và tốt hơn ở lớp ảo giác nội tại. Đầu chú ý mạnh nhất chỉ đúng đoạn chứa bằng chứng ở 87,8 % mẫu ISE-DSC01, gấp 14,3 lần mức ngẫu nhiên; khi xóa câu bằng chứng, cả bốn đại lượng hình dạng đổi đúng hướng đã xác định trước, và đúng hơn cắt bỏ ngữ cảnh (0,850 so với 0,733) dù rẻ hơn khoảng 11 lần. Phần cải thiện của chunk-aware không có ý nghĩa thống kê (0,757 so với 0,745); bộ phát hiện ba lớp không chuyển được sang bộ dữ liệu khác, còn quyết định nhị phân thì chuyển được (0,78).

Sản phẩm gồm thư viện Python, dịch vụ REST kèm giao diện quan sát chú ý và ảnh Docker; hướng phát triển là chấm điểm theo từng đoạn.

**Từ khóa: phát hiện ảo giác, sinh văn bản tăng cường truy xuất, phân tích chú ý, xử lý ngôn ngữ tự nhiên tiếng Việt, hiệu chỉnh xác suất.**

<div style="page-break-after: always"></div>

# LỜI CẢM ƠN {#loi-cam-on .unnumbered}

Trước hết, chúng em xin gửi lời cảm ơn chân thành đến ThS. Trương Vĩnh Linh, giảng viên hướng dẫn của đề tài. Thầy đã nhận hướng dẫn một đề tài có rủi ro kỹ thuật cao ngay từ tuần đầu và theo sát nhóm trong suốt quá trình thực hiện. Những góp ý của thầy qua các buổi báo cáo tiến độ đã giúp chúng em giữ nguyên tắc đo đạc trước khi kết luận, và trình bày kết quả đúng với mức độ chắc chắn mà số liệu cho phép.

Chúng em xin cảm ơn quý thầy cô Khoa Công nghệ Thông tin, Trường Đại học Công nghiệp Thành phố Hồ Chí Minh đã trang bị cho chúng em nền tảng về học máy, thống kê và kỹ thuật phần mềm — ba mảng kiến thức mà đề tài này đều cần đến.

Chúng em trân trọng cảm ơn các nhóm tác giả đã công khai dữ liệu và mã nguồn mà khóa luận sử dụng: nhóm ViHallu (UIT Data Science Challenge 2025), nhóm ISE-DSC01, nhóm ViWikiFC, nhóm ViFactCheck, nhóm SemViQA — cũng thuộc Trường Đại học Công nghiệp Thành phố Hồ Chí Minh — và nhóm Lookback Lens, công trình mà đề tài mở rộng trực tiếp.

Cuối cùng, chúng em cảm ơn gia đình đã luôn động viên trong suốt thời gian thực hiện khóa luận.

Mặc dù đã cố gắng, khóa luận không tránh khỏi thiếu sót. Chúng em rất mong nhận được ý kiến đóng góp của quý thầy cô.

> **Người thực hiện đề tài**
>
>  
>
>  
>
>  
>
> Nguyễn Ngọc Lân
>
>  
>
>  
>
> Nguyễn Tấn Minh

<div style="page-break-after: always"></div>

# NHẬN XÉT CỦA GIÁO VIÊN HƯỚNG DẪN {#nhan-xet-gvhd .unnumbered}

.................................................................................................

.................................................................................................

.................................................................................................

.................................................................................................

**TP. Hồ Chí Minh, ngày .... tháng .... năm .......**

CHỮ KÝ CỦA GIẢNG VIÊN

<div style="page-break-after: always"></div>

# NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 1 {#nhan-xet-pb1 .unnumbered}

.................................................................................................

.................................................................................................

.................................................................................................

.................................................................................................

**TP. Hồ Chí Minh, ngày .... tháng .... năm .......**

CHỮ KÝ CỦA GIẢNG VIÊN

<div style="page-break-after: always"></div>

# NHẬN XÉT CỦA GIÁO VIÊN PHẢN BIỆN 2 {#nhan-xet-pb2 .unnumbered}

.................................................................................................

.................................................................................................

.................................................................................................

.................................................................................................

**TP. Hồ Chí Minh, ngày .... tháng .... năm .......**

CHỮ KÝ CỦA GIẢNG VIÊN

<div style="page-break-after: always"></div>

# MỤC LỤC {#muc-luc .unnumbered}

@@GEN_TOC@@

<div style="page-break-after: always"></div>

# DANH MỤC HÌNH ẢNH {#danh-muc-hinh-anh .unnumbered}

@@GEN_LOF@@

<div style="page-break-after: always"></div>

# DANH MỤC BẢNG BIỂU {#danh-muc-bang-bieu .unnumbered}

@@GEN_LOT@@

<div style="page-break-after: always"></div>

# DANH MỤC CÁC THUẬT NGỮ VIẾT TẮT {#danh-muc-cac-thuat-ngu-viet-tat .unnumbered}

| Từ viết tắt | Từ đầy đủ | Nghĩa |
|---|---|---|
| **API** | Application Programming Interface | Giao diện lập trình ứng dụng |
| **AUROC** | Area Under the Receiver Operating Characteristic Curve | Diện tích dưới đường cong ROC |
| **BM25** | Best Matching 25 | Hàm xếp hạng truy xuất văn bản theo tần suất từ |
| **CH** | — | Câu hỏi nghiên cứu (CH1, CH2, CH3) |
| **CPU** | Central Processing Unit | Bộ xử lý trung tâm |
| **DSC** | Data Science Challenge | Cuộc thi Khoa học dữ liệu của Trường Đại học Công nghệ Thông tin, ĐHQG TP.HCM |
| **ECE** | Expected Calibration Error | Sai số hiệu chỉnh kỳ vọng |
| **GPU** | Graphics Processing Unit | Bộ xử lý đồ họa |
| **H** | — | Giả thuyết nghiên cứu (H1–H5) |
| **KTC** | — | Khoảng tin cậy |
| **LLM** | Large Language Model | Mô hình ngôn ngữ lớn |
| **MLP** | Multi-Layer Perceptron | Mạng truyền thẳng nhiều lớp bên trong mỗi lớp Transformer |
| **MRR** | Mean Reciprocal Rank | Nghịch đảo hạng trung bình |
| **NEI** | Not Enough Information | Nhãn "không đủ thông tin" trong các bộ kiểm chứng thông tin |
| **NF4** | 4-bit NormalFloat | Định dạng lượng tử hóa trọng số 4 bit |
| **NLI** | Natural Language Inference | Suy luận ngôn ngữ tự nhiên (kéo theo văn bản) |
| **RAG** | Retrieval-Augmented Generation | Sinh văn bản tăng cường truy xuất |
| **REST** | Representational State Transfer | Kiểu kiến trúc dịch vụ web |
| **SHA** | Secure Hash Algorithm | Họ hàm băm mật mã; đề tài dùng SHA-256 |
| **VRAM** | Video Random Access Memory | Bộ nhớ của card đồ họa |
| **YAML** | YAML Ain't Markup Language | Định dạng tệp cấu hình dạng văn bản |

<div style="page-break-after: always"></div>

# DANH MỤC KÝ HIỆU {#danh-muc-ky-hieu .unnumbered}

| Ký hiệu | Ý nghĩa |
|---|---|
| $L$, $H$ | Số lớp và số đầu chú ý mỗi lớp của mô hình đọc |
| $l$, $h$ | Chỉ số lớp và chỉ số đầu chú ý |
| $n$ | Độ dài chuỗi đầu vào, tính bằng token |
| $T$ | Số token của phản hồi cần chấm |
| $t$ | Chỉ số token phản hồi đang xét, đếm trong phạm vi phản hồi ($1 \le t \le T$) |
| $X$ | Tập token đứng trước phản hồi dùng làm mẫu số của tỷ lệ lookback |
| $C$, $C_k$ | Tập token ngữ cảnh truy xuất; tập token của đoạn thứ $k$ |
| $K$ | Số đoạn ngữ cảnh của một mẫu |
| $\alpha^{(l,h)}_{t,i}$ | Trọng số chú ý mà token phản hồi $t$ dành cho token $i$ tại lớp $l$, đầu $h$ |
| $\mathrm{LR}^{(l,h)}_{t}$ | Tỷ lệ lookback của token $t$ tại lớp $l$, đầu $h$ |
| $a_k$, $s_k$ | Mật độ chú ý của đoạn $k$; tỷ trọng chú ý của đoạn $k$ sau chuẩn hóa |
| $\mathrm{MAX}$, $\mathrm{ENT}$, $\mathrm{GINI}$, $\mathrm{GAP}$, $\mathrm{DRIFT}$ | Năm đặc trưng hình dạng của phân bố chú ý theo đoạn |
| $\mathcal{C}$ | Tập nhãn $\{\mathrm{no}, \mathrm{intrinsic}, \mathrm{extrinsic}\}$ |
| $\mathbf{z}$, $d$ | Véc-tơ đặc trưng đã chuẩn hóa của một mẫu và số chiều của nó |
| $P_c$, $R_c$, $\mathrm{F1}_{c}$ | Độ chính xác, độ bao phủ và F1 của lớp $c$ |
| $\kappa$ | Hệ số đồng thuận kappa của Cohen |
| $r_{\mathrm{rb}}$ | Hệ số tương quan hạng hai chuỗi (rank-biserial), dùng làm cỡ ảnh hưởng |
| $B$, $R$ | Số khoảng (bin) chia theo độ tự tin khi tính ECE; số lần lấy mẫu lại bootstrap |
| $\varepsilon$ | Ngưỡng số rất nhỏ ($10^{-12}$) dùng để tránh chia cho 0 |

<div style="page-break-after: always"></div>
