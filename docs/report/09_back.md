# TÀI LIỆU THAM KHẢO {#tai-lieu-tham-khao .unnumbered}

@@GEN_REFS@@

<div style="page-break-after: always"></div>

# PHỤ LỤC {#phu-luc .unnumbered}

## Phụ lục A — Cấu trúc mã nguồn và kiểm thử

Mã nguồn của hệ thống được tổ chức theo bố cục `src/` với gói `vihallulens`; bộ kiểm thử khóa các bất biến quan trọng của phép tính, như các ví dụ ở mục [[sec:c3-chia-tap]], [[sec:c4-dac-trung]] và [[sec:c4-hook]]. Lượt chạy kiểm thử trên máy cá nhân ngày 18/09/2026 cho kết quả 688 ca đạt, 0 ca thất bại. Sáu tệp kiểm thử cần PyTorch với CUDA hoặc bộ tách từ tiếng Việt `pyvi` được chạy cùng các notebook trên Kaggle. [[fig:terminal]] cho thấy cây thư mục, lượt chạy kiểm thử và trạng thái của dịch vụ; [[tab:duong-dan]] liệt kê vị trí các thành phần chính.

![Cấu trúc mã nguồn, lượt chạy kiểm thử và trạng thái dịch vụ](media/hinh_terminal_ma_nguon.png)

*[[fig:terminal]] Cấu trúc mã nguồn, lượt chạy kiểm thử và trạng thái dịch vụ*

*[[tab:duong-dan]] Vị trí các thành phần của mã nguồn và dữ liệu*

| Thành phần | Vị trí |
|---|---|
| Mã nguồn thư viện | `src/vihallulens/` (43 tệp, 5.573 dòng) |
| Kiểm thử | `tests/` (40 tệp, 7.373 dòng, 688 ca) |
| Điểm vào dòng lệnh | `scripts/` (32 tệp) |
| Cấu hình thí nghiệm | `configs/` (21 tệp YAML: 20 cấu hình thí nghiệm, 1 tệp mẫu) |
| Notebook chạy GPU | `notebooks/` (15 tệp) |
| Kết quả thô | `results/runs.jsonl`, `results/tradeoff.csv`, `results/error_analysis.json` |
| Bundle bộ phát hiện | `models/e03_chunk_aware.pkl` (11,5 KB) kèm tệp mô tả `.json` |
| Tài liệu dự án | `docs/SPEC.md`, `docs/DATA.md`, `docs/EXPERIMENTS.md`, `docs/REFERENCES.md` |
| Mã sinh hình vẽ của báo cáo | `docs/media/src/` |

Dữ liệu thô không được đưa vào kho Git; bảng ánh xạ từ tên tệp gốc sang tên chuẩn nằm ở `data/raw/MANIFEST.md`.

## Phụ lục B — Tài liệu giao diện lập trình và đóng gói

Dịch vụ REST tự sinh tài liệu OpenAPI tại đường dẫn `/docs` ([[fig:openapi]]). Trang chủ của hệ thống trình bày ba cách sử dụng bộ phát hiện — thư viện Python, dịch vụ REST và ảnh Docker ([[fig:ba-cach-dung]]).

![Tài liệu OpenAPI tự sinh của dịch vụ REST](media/anh_tai_lieu_rest_api.png)

*[[fig:openapi]] Tài liệu OpenAPI tự sinh của dịch vụ REST*

![Ba cách sử dụng bộ phát hiện](media/anh_ba_cach_dung.png)

*[[fig:ba-cach-dung]] Ba cách sử dụng bộ phát hiện: thư viện, dịch vụ REST và Docker*

Toàn bộ dịch vụ chạy được bằng một lệnh:

```
docker compose up --build
```

Ảnh Docker có kích thước 10,5 GB. Trọng số của mô hình đọc (khoảng 15 GB) không nằm trong ảnh mà được tải vào một volume riêng ở lần chạy đầu, để việc sửa mã nguồn không buộc dựng lại 15 GB dữ liệu. Nếu máy không có GPU NVIDIA, lệnh trên báo lỗi sau khoảng sáu giây thay vì tải trọng số rồi mới thất bại.

## Phụ lục C — Trang giới thiệu hệ thống

Ngoài giao diện quan sát và hệ RAG minh họa, hệ thống có một trang giới thiệu trình bày đề tài cho người đọc chưa có kiến thức nền ([[fig:trang-chu]]). Trang gồm một khối tương tác so sánh cách tính của Lookback Lens gốc — gộp cả ngữ cảnh thành một con số — với cách tính chunk-aware — mỗi đoạn một tỷ trọng, kèm các đại lượng hình dạng cập nhật theo thanh trượt ([[fig:khoi-tuong-tac]]); khối này ghi rõ trên giao diện rằng số liệu chỉ mang tính minh họa.

![Trang giới thiệu của hệ thống](media/anh_trang_chu_hero.png)

*[[fig:trang-chu]] Trang giới thiệu của hệ thống ViHalluLens*

![Khối tương tác so sánh lookback gộp và chunk-aware](media/anh_trang_chu_chunk_aware.png)

*[[fig:khoi-tuong-tac]] Khối tương tác so sánh lookback gộp và chunk-aware*

## Phụ lục D — Tái lập kết quả

Phụ lục này gồm hai phần: các lệnh dựng lại kết quả từ dữ liệu gốc, và mức tái lập thực tế của từng loại kết quả — thứ gì lặp lại được trùng từng chữ số, thứ gì chỉ lặp lại được trong một sai số nhỏ, thứ gì không lặp lại được và vì sao.

Chuẩn bị môi trường:

```
uv sync
```

Chuẩn hóa dữ liệu và chia tập (chạy đúng thứ tự):

```
python scripts/normalize_data.py --all
python scripts/split_data.py
```

Trích đặc trưng cho một thí nghiệm (cần GPU):

```
python scripts/extract_features.py --config configs/e03_chunk_sentence_vihallu.yaml
```

Khớp và chấm bộ phát hiện (chạy trên CPU):

```
python scripts/run_chunk_aware.py --config configs/e03_chunk_sentence_vihallu.yaml
```

Dựng bảng đánh đổi và phân tích sai sót:

```
python scripts/build_tradeoff.py
python scripts/error_analysis.py --config configs/e03_chunk_sentence_vihallu.yaml \
    --reference-run e03_chunk_aware
```

Chạy dịch vụ và hệ RAG minh họa:

```
python scripts/serve.py --bundle models/e03_chunk_aware.pkl --port 8000
```

Sinh lại hình vẽ và dựng lại báo cáo (bước cuối cần Microsoft Word):

```
python docs/media/src/charts.py
python docs/media/src/method_figs.py
python docs/media/src/concept_figs.py
python docs/media/src/fig_tong_quat_he_thong.py
python docs/media/src/fig_terminal.py
python docs/tools/resolve.py
python docs/tools/build_docx.py
```

**Những gì được cố định.** [[tab:co-dinh]] liệt kê các thành phần được giữ cố định để một lượt chạy lại đọc đúng dữ liệu, đúng cấu hình và đúng mã nguồn như lượt đã báo cáo.

*[[tab:co-dinh]] Các thành phần được cố định để tái lập*

| Thành phần | Cách cố định |
|---|---|
| Chia tập | Theo ngữ cảnh, tỷ lệ 80/10/10, seed 42. Thứ tự các nhóm lấy từ giá trị băm SHA-256 của cặp (seed, mã ngữ cảnh), nên không phụ thuộc thứ tự đọc tệp (mục [[sec:c3-chia-tap]]). |
| Cấu hình | 20 tệp YAML cấu hình thí nghiệm trong `configs/`, được pydantic kiểm tra khi nạp. Mỗi tệp đặc trưng và mỗi bản ghi kết quả mang mã băm của cấu hình đã sinh ra nó. |
| Mã nguồn | Mỗi bản ghi trong `results/runs.jsonl` mang mã commit Git của lượt chạy. Ô đầu của mỗi notebook Kaggle in mã commit và phiên bản thư viện; notebook được lưu nguyên đầu ra. |
| Mẫu prompt | Chốt ngày 19/08/2026 (mục [[sec:c4-prompt]]), không đổi trong suốt các thí nghiệm. |
| Mô hình đọc | Qwen2.5-7B-Instruct, kho Hugging Face ở mã commit `a09a3545`; kiểu số float16 bỏ lớp 27, riêng Qwen2.5-1.5B dùng bfloat16 ([[tab:kieu-so]]). |
| Bộ phân loại | Hồi quy logistic của scikit-learn với `random_state=42`; cách gộp đầu chú ý chọn trên tập kiểm định, tập kiểm tra chỉ chấm một lần. |
| LLM giám khảo | Mỗi phản hồi của Gemini được lưu vào `results/judge_cache.jsonl` theo khóa SHA-256 của (mô hình, prompt); chấm lại đọc từ bộ nhớ đệm này thay vì gọi lại API. |
| Dữ liệu gốc | Không sửa tệp nào trong `data/raw/`; mã băm SHA-256 của các tệp đã dùng ở [[tab:ma-bam]]. |

**Môi trường đã chạy.** Các lượt chạy diễn ra trên hai môi trường. Phiên bản thư viện thực tế đọc từ đầu ra của các notebook và từ tệp khóa `uv.lock` ([[tab:moi-truong]]).

*[[tab:moi-truong]] Phiên bản môi trường đã dùng cho các lượt chạy*

| Môi trường | Python | PyTorch | transformers | Dùng cho |
|---|---|---|---|---|
| Kaggle, Tesla T4 | 3.12.13 | 2.10.0 | 5.0.0 – 5.16.1 | Trích đặc trưng, tinh chỉnh bộ mã hóa, đo thời gian và bộ nhớ |
| Máy cá nhân | 3.11.9 | 2.14.0 | 5.17.0 | Khớp bộ phân loại, chấm điểm, kiểm thử, dịch vụ |

Trên Kaggle, thư viện được cài bản mới nhất ở thời điểm chạy nên phiên bản thay đổi giữa các notebook; vì vậy mỗi notebook in ra phiên bản đã dùng ngay ở ô đầu. bitsandbytes là 0.50.1 ở T07–T08 và 0.50.2 từ T20 trở đi.

**Mức tái lập của từng loại kết quả.** [[tab:muc-tai-lap]] phân loại các kết quả theo mức lặp lại được khi chạy lại.

*[[tab:muc-tai-lap]] Mức tái lập của từng loại kết quả*

| Loại kết quả | Mức tái lập | Ghi chú |
|---|---|---|
| Chuẩn hóa, chia tập, thống kê dữ liệu, phân tích rò rỉ | Trùng từng chữ số | Tính toán thuần, có kiểm thử khóa kết quả. |
| Dự đoán của bộ phát hiện đã đóng gói | Trùng từng dự đoán | Nạp lại `models/e03_chunk_aware.pkl` và chấm 700 mẫu kiểm tra: trùng 700/700 với lúc thí nghiệm. |
| Khớp lại bộ phân loại từ tệp đặc trưng | Trùng trong cùng một môi trường | Giữa Kaggle và máy cá nhân, điểm trên tập kiểm định lệch tối đa 0,0075 ở cấu hình phụ, do bộ tối ưu lbfgs hội tụ khác nhau theo phiên bản thư viện số; cấu hình được chọn cho 0,7768 ở cả hai. Vì vậy mọi bảng so sánh được chấm trên cùng một máy. |
| Trích đặc trưng chú ý | Trong sai số số học | Tính ở float16 trên GPU nên không trùng từng bit giữa các phần cứng và phiên bản. Tệp đặc trưng không đưa lên kho mã vì dung lượng; chạy lại phải trích lại trên GPU, gần một giờ T4 cho riêng ViHallu. |
| Tinh chỉnh PhoBERT, XLM-R | Dao động theo seed và theo lượt | Ba seed mỗi mô hình, độ lệch chuẩn 0,011 (PhoBERT) và 0,017 (XLM-R), ghi trong `results/runs.jsonl`. Cố định seed chưa đủ: cùng seed 42, XLM-R học được ở lượt ngày 27/08 nhưng không học được ở lượt ngày 28/08. |
| LLM giám khảo Gemini | Từ bộ nhớ đệm | Gọi lại API có thể cho kết quả khác vì mô hình phía nhà cung cấp thay đổi theo thời gian; số trong báo cáo tái lập được từ `results/judge_cache.jsonl`. |
| Thời gian và bộ nhớ GPU | Gắn với phần cứng | Đo trên Tesla T4, mỗi cấu hình một phiên riêng hoặc đo xen kẽ, vì hai lượt nối nhau trong cùng phiên đã chậm đi 10–15 % do hạ xung. |

**Kiểm tra dữ liệu gốc.** Dữ liệu không nằm trong kho mã và phải tải lại từ nguồn công bố của từng bộ (mục [[sec:c3-bon-bo]]). [[tab:ma-bam]] ghi mã băm SHA-256 của đúng các tệp đã dùng, để người chạy lại kiểm tra mình có cùng dữ liệu hay không (lệnh `sha256sum` trên Linux, `Get-FileHash` trên Windows).

*[[tab:ma-bam]] Mã băm SHA-256 của các tệp dữ liệu gốc đã dùng*

| Tệp | SHA-256 |
|---|---|
| `vihallu_train.csv` | `52a9d8605688f77d5e2d4504c81765e8183f83e1d0ceab8957aeab67381c9bce` |
| `isedsc01_train.json` | `76605fc30a4192a1e1d5d961ec32572de727230f3dc5b5d633a499b009b82dd3` |
| `viwikifc_train.csv` | `477adcca59920d40f5cb6580a7cbdd6828e22839f0bb52abed7212c0edf4af5d` |
| `viwikifc_dev.csv` | `d0d45cfde4844c6b6f89dc61700416d0f3f1f9b6edba871c23f9f2cb88cf83fc` |
| `viwikifc_test.csv` | `ff6016f9c04ac6aee6333583876bcf5f88ba455141767f548213f1868726c84c` |
| `vifactcheck_train.parquet` | `ff054bc61afb59e3c9aa1dd402f0eb44700a30866c75ee6c66e117517bd510e8` |
| `vifactcheck_dev.parquet` | `16b6d8b244ec07be1a6d80fcb389486c2f26e5c10cdc66f6cab72bd159920454` |
| `vifactcheck_test.parquet` | `d797eb5a3797f12c052d4c8dbdda0b9cf7174f3dfce91050f95354b044816214` |

## Phụ lục E — Nguồn số liệu

Mọi con số trong Chương 6 và Chương 7 đều có bản ghi đọc được bằng máy trong thư mục `results/` ([[tab:nguon-so-lieu]]). Phần diễn giải chi tiết của từng thí nghiệm nằm ở `docs/EXPERIMENTS.md`.

*[[tab:nguon-so-lieu]] Nguồn số liệu của các bảng kết quả*

| Bảng trong báo cáo | Tệp nguồn và khóa bản ghi |
|---|---|
| [[tab:ket-qua-chinh]] | `results/runs.jsonl`, khóa `e01_*`, `e02_*`, `e03_*`, `e09_*`, `e10_*` |
| [[tab:e02-e03]] | `results/runs.jsonl`, khóa `e02_*`, `e03_*` |
| [[tab:dinh-vi]], [[tab:lap-lai]] | `results/runs.jsonl`, khóa `e06_localization_isedsc01`, `e08_extrinsic_viwikifc` |
| [[tab:chia-doan]] | `results/runs.jsonl`, khóa `e04_*`, `e05_*` |
| [[tab:ngu-canh-dai]] | `results/runs.jsonl`, khóa `e07_*` |
| [[tab:can-thiep]] | `results/runs.jsonl`, khóa `e08_extrinsic_viwikifc` |
| [[tab:ablation]], [[tab:chong-lan]] | `results/runs.jsonl`, khóa `e12_ablation_*` |
| [[tab:mo-hinh-doc]], [[tab:ece-tham-so]] | `results/runs.jsonl`, khóa `e13_*`, `e14_*`, `e07_*`, `e15_*` |
| [[tab:viwikifc]] | `results/runs.jsonl`, khóa `e15_*` |
| [[tab:cheo-bo]] | `results/runs.jsonl`, khóa `e16_*` |
| [[tab:chi-phi]] | `results/tradeoff.csv`, `results/feasibility.jsonl` |
| [[tab:nhan-cau-truc]], [[tab:loai-prompt]], [[fig:ma-tran-nham-lan]] | `results/error_analysis.json`, `results/error_analysis.csv` |
| [[tab:ro-ri]], [[tab:ket-qua-chia]] | `results/leakage_report.md` |
| [[tab:kiem-nei]], [[tab:bang-cheo-nei]] | `results/nei_mapping_audit*.csv` |

## Phụ lục F — Bảng tham khảo bổ sung

Các bảng dưới đây được nhắc tới ở Chương 3 và Chương 4.

*[[tab:schema]] Lược đồ chung dùng cho cả bốn bộ dữ liệu*

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `sample_id` | chuỗi | Khóa chính, duy nhất trên toàn bộ dữ liệu |
| `context_id` | chuỗi | Định danh ngữ cảnh, băm SHA-256 từ nội dung ngữ cảnh; là đơn vị chia tập |
| `context` | chuỗi | Ngữ cảnh truy xuất |
| `question` | chuỗi hoặc rỗng | Câu hỏi; rỗng với ba bộ kiểm chứng thông tin |
| `response` | chuỗi | Phản hồi (hoặc phát biểu) cần chấm |
| `label` | ba lớp | `no` / `intrinsic` / `extrinsic` |
| `evidence`, `evidence_start` | chuỗi, số nguyên | Câu bằng chứng nguyên văn và vị trí ký tự của nó trong ngữ cảnh, nếu bộ dữ liệu có |
| `meta` | từ điển | Thông tin riêng từng bộ, ví dụ loại prompt của ViHallu |

*[[tab:do-dai-token]] Độ dài quy ra token và số mẫu vượt ngưỡng cắt*

| Bộ | Token/từ | Ngữ cảnh p50 | Ngữ cảnh dài nhất | Đầu vào p50 | Đầu vào p99 | Đầu vào dài nhất | Vượt 2.048 | Vượt 4.096 |
|---|---|---|---|---|---|---|---|---|
| ViHallu | 1,35 | 218 | 2.347 | 308 | 635 | 2.474 | 3 (0,04 %) | 0 |
| ISE-DSC01 | 1,33 | 768 | 6.543 | 796 | 2.072 | 6.622 | 396 (1,09 %) | 6 (0,02 %) |
| ViWikiFC | 1,36 | 183 | 805 | 214 | 590 | 950 | 0 | 0 |
| ViFactCheck | 1,33 | 823 | 4.696 | 870 | 2.738 | 4.782 | 142 (2,81 %) | 8 (0,16 %) |

"Đầu vào" gồm ngữ cảnh, câu hỏi và phản hồi, chưa kể các token khung của mẫu prompt; hai cột cuối đếm số mẫu có đầu vào vượt ngưỡng. Số liệu của ViWikiFC và ViFactCheck tính trên tập huấn luyện.

*[[tab:bang-cheo-nei]] Bảng chéo nhãn của hai người gán trên 100 mẫu NEI (hàng: người thứ nhất, cột: người thứ hai)*

| | `ngoai_lai` | `noi_tai` | `khong` | `khong_chac` |
|---|---|---|---|---|
| **`ngoai_lai`** | 67 | 4 | 0 | 0 |
| **`noi_tai`** | 4 | 3 | 0 | 0 |
| **`khong`** | 6 | 6 | 9 | 1 |
| **`khong_chac`** | 0 | 0 | 0 | 0 |

## Phụ lục G — Sử dụng công cụ AI trong quá trình thực hiện

Phụ lục này trình bày cách nhóm sử dụng công cụ AI trong quá trình nghiên cứu và phát triển phần mềm của khóa luận: dùng vào việc gì, theo quy trình nào, với những ràng buộc nào, và rút ra kinh nghiệm gì. Mục đích là để người đọc thấy rõ ranh giới giữa phần do nhóm quyết định và phần công cụ hỗ trợ, đồng thời có thể lặp lại cách làm. Mức tái lập của các kết quả thực nghiệm được trình bày riêng ở Phụ lục D.

**Hai vai trò khác nhau của mô hình ngôn ngữ lớn.** Trong khóa luận, mô hình ngôn ngữ lớn xuất hiện ở hai vai trò cần tách bạch. Thứ nhất, chúng là đối tượng nghiên cứu: Qwen2.5 là mô hình đọc mà đặc trưng chú ý được trích ra (Chương 4), còn Gemini là mốc LLM giám khảo được so sánh ở Chương 6; vai trò này thuộc về phương pháp và đã được mô tả ở các chương chính. Thứ hai, nhóm dùng trợ lý lập trình Claude Code (Anthropic), chạy trong trình soạn thảo VS Code, như một công cụ hỗ trợ kỹ thuật. Phụ lục này chỉ nói về vai trò thứ hai.

**Phân định vai trò.** Công cụ AI chỉ giữ vai trò hỗ trợ thực thi. Mọi quyết định về đề tài, thiết kế thực nghiệm, cách đánh giá và kết luận do nhóm đưa ra; công cụ thực hiện các phần việc kỹ thuật theo yêu cầu cụ thể của nhóm và chịu sự kiểm duyệt của nhóm ở từng bước ([[tab:phan-dinh-ai]]).

*[[tab:phan-dinh-ai]] Phân định vai trò giữa nhóm và công cụ AI*

| Hạng mục | Nhóm thực hiện và quyết định | Công cụ AI hỗ trợ |
|---|---|---|
| Đề tài, câu hỏi và giả thuyết | Chọn đề tài và ý tưởng chunk-aware; đặt ba câu hỏi nghiên cứu, năm giả thuyết; ghi hướng dự đoán trước khi chạy thí nghiệm can thiệp | Không tham gia |
| Thiết kế thực nghiệm | Chọn bộ dữ liệu, cách chia tập, các mốc so sánh, ràng buộc phần cứng và ngân sách GPU; duyệt từng thí nghiệm trước khi chạy; đặt các phép đối chứng | Trả lời câu hỏi kỹ thuật và nêu phương án khi được hỏi |
| Mã nguồn và kiểm thử | Đặt yêu cầu và tiêu chí hoàn thành cho từng việc; đọc lại, chạy và duyệt từng pull request trước khi gộp | Viết mã và kiểm thử theo yêu cầu |
| Chạy thực nghiệm | Chạy notebook trên Kaggle, theo dõi hạn mức GPU, lưu notebook và nhật ký làm minh chứng, đối chiếu kết quả | Dựng notebook; đọc nhật ký lỗi để chỉ ra nguyên nhân |
| Kiểm chứng nhãn | Hai thành viên gán nhãn độc lập 100 mẫu NEI (mục [[sec:c3-anh-xa]]) | Không tham gia gán nhãn |
| Phân tích và kết luận | Diễn giải kết quả, quyết định trình bày cả kết quả bất lợi, rút ra kết luận | Tổng hợp số liệu từ tệp kết quả khi được yêu cầu |

**Quy trình làm việc.** Để công cụ không tự ý quyết định thay nhóm và để mọi bước kiểm tra được, nhóm tổ chức công việc theo sáu nguyên tắc:

1. **Bộ quy tắc dự án viết thành văn bản.** Tệp `CLAUDE.md` (khoảng 200 dòng) ghi ràng buộc cứng về phần cứng và ngân sách, các quyết định đã chốt và những điều bị cấm. Công cụ đọc tệp này ở đầu mỗi phiên, nên quy tắc không phụ thuộc vào trí nhớ của một cuộc hội thoại.
2. **Danh sách việc tuần tự.** Tệp `TASKS.md` chia công việc thành 52 việc trong 10 giai đoạn, mỗi việc có tiêu chí hoàn thành là một lệnh chạy được. Việc làm đúng thứ tự, không làm trước việc chưa tới.
3. **Mỗi việc một pull request.** Từ 19/08 đến 02/10/2026, kho mã có 127 pull request; nhóm đọc và gộp từng pull request.
4. **Chỉ đánh dấu hoàn thành khi có bằng chứng.** Một việc chỉ được đánh dấu xong khi lệnh trong tiêu chí chạy được và đầu ra được dán vào pull request; với việc cần GPU, notebook Kaggle đã chạy được lưu nguyên đầu ra trong thư mục `notebooks/`.
5. **Dừng lại và hỏi.** Mọi quyết định chưa có trong bộ quy tắc — thêm thư viện, đổi kiến trúc, đổi hướng khi một bước kiểm tra thất bại — công cụ phải dừng lại để nhóm quyết định.
6. **Ghi nhật ký diễn giải.** Sau mỗi việc, mục đích, kết quả số và điều rút ra được ghi lại trong `TASKS.md` và `docs/EXPERIMENTS.md`; đây cũng là nguồn số liệu ở Phụ lục E.

**Các ràng buộc đặt cho công cụ.** Dưới đây là một số quy tắc trích nguyên văn từ `CLAUDE.md`. Đây là dạng câu lệnh chuyên biệt quan trọng nhất của quy trình: chúng được áp dụng cho mọi phiên làm việc chứ không chỉ cho một yêu cầu.

```
Phần cứng: GPU Tesla T4 16 GB trên Kaggle/Colab. Mọi thứ phải
chạy vừa trong 16 GB.
Mọi thứ phải tái lập được trên máy khác: seed cố định, config
ghi ra file, không có magic number nằm trong code.
Không đổi mẫu prompt đưa vào mô hình đọc sau khi đã chốt ở T07.
Không sửa dữ liệu gốc trong data/raw/. Chỉ đọc.
Trước khi tick hoàn thành, phải chạy được lệnh nêu trong mục
"Tiêu chí hoàn thành" của task và dán output vào PR.
Nếu một task cần quyết định chưa có trong file này — ví dụ chọn
thư viện mới, đổi kiến trúc, thêm phụ thuộc nặng — DỪNG LẠI và
hỏi người dùng. Không tự quyết.
```

**Một số yêu cầu tiêu biểu.** [[tab:yeu-cau-ai]] trích một số yêu cầu nhóm đưa ra trong quá trình làm (rút gọn, giữ nguyên ý), kèm mục đích của từng yêu cầu. Điểm chung là nhóm luôn yêu cầu kiểm tra trước khi tốn tài nguyên và giữ quyền quyết định ở những điểm rẽ của nghiên cứu.

*[[tab:yeu-cau-ai]] Một số yêu cầu tiêu biểu nhóm đưa cho công cụ*

| Ngày | Yêu cầu (trích) | Mục đích |
|---|---|---|
| 19/08 | “Câu ‘dừng và báo’ trong TASKS.md nghĩa là dừng để hỏi ý kiến, không phải dừng để đổi đề tài.” | Giữ quyền quyết định hướng đề tài ở nhóm trước bước kiểm tra khả thi T07 |
| 19/08 | “Các file dữ liệu trên Kaggle đều có định dạng như này, hãy xem code lại coi có chỗ nào sai không trước khi tôi chạy.” | Rà mã trước khi tiêu tốn hạn mức GPU |
| 20/08 | “Có cần so sánh chạy hai phiên khác nhau phần ô 6 và 7 không?” | Dẫn tới quy tắc đo chi phí mỗi cấu hình một phiên riêng, sau khi phát hiện hạ xung làm chậm 10–15 % |
| 27/08 | “Kiểm tra lại lần nữa coi đúng chưa và cho tôi biết 5 seed có cần thiết không.” | Cân nhắc độ tin cậy với chi phí GPU trước khi quyết định |
| 30/08 | “… phép đối chứng để tách nốt câu hỏi ‘câu thắng vì ngữ nghĩa hay vì không chồng lấn’.” | Đặt câu hỏi dẫn tới phép đối chứng cửa sổ không chồng lấn ở mục [[sec:c6-chia-doan]] |
| 11/09 | “Dựa vào log lúc nãy chạy là thành công rồi hả, sao đã tick vào ô 40?” | Bắt lỗi đánh dấu hoàn thành khi chưa đối chiếu minh chứng |
| 11/09 | “Kiểm tra lại toàn bộ repo xem các file có sai sót và không khớp nhau ở chỗ nào không.” | Rà soát chéo toàn bộ kho mã trước giai đoạn tổng hợp kết quả |

**Kinh nghiệm rút ra.** Bốn điều nhóm thấy quan trọng nhất khi dùng công cụ AI trong một dự án nghiên cứu:

1. **Công cụ có thể sai một cách tự tin, nên mọi con số phải đối chiếu với tệp kết quả.** Các lỗi nhóm đã phát hiện nhờ đối chiếu: số mẫu ISE-DSC01 có bằng chứng nguyên văn bị đếm thành 23.785 thay vì 23.783, do hai mẫu có bằng chứng chỉ là dòng trống; hàm xếp hạng BM25 dùng phép sắp xếp không ổn định khiến 17 trên 1.836 cặp ngữ cảnh khác nhau giữa hai máy, đã sửa bằng phép sắp xếp có quy tắc phân định hòa; một việc từng bị đánh dấu hoàn thành trước khi nhật ký chạy được kiểm tra.
2. **Quy tắc viết thành văn bản bền hơn lời dặn trong hội thoại.** Khi một phiên làm việc dài bị tóm tắt lại, những lời dặn chỉ nằm trong hội thoại có thể bị bỏ sót; quy tắc trong `CLAUDE.md` thì được đọc lại mỗi phiên. Vì vậy mỗi quyết định quan trọng đều được ghi vào tệp này ngay khi chốt.
3. **Việc tốn GPU phải được ước tính và chạy lại được từng phần.** Nhóm yêu cầu mọi notebook ước tính thời gian trước khi chạy và ghi kết quả từng mẫu ngay khi tính xong, để một phiên Kaggle bị đứt không làm mất phần đã chạy.
4. **Công cụ không thay được phán đoán khoa học.** Những quyết định định hình kết quả — đặt phép đối chứng nào, ghi hướng dự đoán trước khi chạy, trình bày thẳng kết quả bất lợi của phần chunk-aware — đều do nhóm đưa ra.

**Tính tái lập của quy trình.** Bộ quy tắc `CLAUDE.md`, danh sách việc `TASKS.md`, lịch sử 127 pull request, các notebook đã chạy và nhật ký `results/runs.jsonl` đều nằm trong kho mã nguồn. Người đọc có thể kiểm tra từng bước đã làm, và có thể lặp lại cách làm này với một công cụ hỗ trợ khác.

<div style="page-break-after: always"></div>

# NHẬT KÍ LÀM VIỆC {#nhat-ki-lam-viec .unnumbered}

**Đề tài: Nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt dựa trên tín hiệu chú ý nội tại**

**Giảng viên hướng dẫn: ThS. Trương Vĩnh Linh**

**Sinh viên thực hiện: Nguyễn Ngọc Lân (22635801) — Nguyễn Tấn Minh (22643511)**

**Ngày bắt đầu: 03/08/2026**

| Tuần | Từ ngày | Đến ngày | Ngày báo cáo GVHD | Tóm tắt công việc đã thực hiện | Nhận xét của GVHD |
|---|---|---|---|---|---|
| 1 | 03/08/2026 | 09/08/2026 |  | Khảo sát tài liệu về phát hiện ảo giác trong RAG; xác định hướng đề tài. |  |
| 2 | 10/08/2026 | 16/08/2026 |  | Thu thập bốn bộ dữ liệu tiếng Việt; kiểm tra cấu trúc và chất lượng nhãn; viết đề xuất đề tài. |  |
| 3 | 17/08/2026 | 23/08/2026 |  | Dựng khung mã nguồn và môi trường; kiểm chứng khả thi trích trọng số chú ý trên GPU T4 (mốc quyết định). |  |
| 4 | 24/08/2026 | 30/08/2026 |  | Chuẩn hóa bốn bộ dữ liệu về lược đồ chung; chia tập theo ngữ cảnh; báo cáo rò rỉ ngữ cảnh. |  |
| 5 | 31/08/2026 | 06/09/2026 |  | Dựng các mốc so sánh: đặc trưng bề mặt, bộ mã hóa, LLM giám khảo; tái lập Lookback Lens. |  |
| 6 | 07/09/2026 | 13/09/2026 |  | Hiện thực đặc trưng chunk-aware lookback ratio; thí nghiệm hai cách chia đoạn. |  |
| 7 | 14/09/2026 | 20/09/2026 |  | Thí nghiệm định vị chú ý trên ISE-DSC01; thí nghiệm lớp ảo giác ngoại lai trên ViWikiFC. |  |
| 8 | 21/09/2026 | 27/09/2026 |  | Tổng hợp kết quả sơ bộ; viết báo cáo giữa kỳ. |  |
| 9 | 28/09/2026 | 04/10/2026 |  | Trình bày báo cáo giữa kỳ cho GVHD; tiếp thu góp ý và điều chỉnh kế hoạch. |  |
| 10 | 05/10/2026 | 11/10/2026 |  | Ablation nhóm đặc trưng, mô hình đọc và bậc thang kích thước. |  |
| 11 | 12/10/2026 | 18/10/2026 |  | Bảng đánh đổi chi phí; đối chứng ngoài trên ViWikiFC; khái quát hóa chéo bộ; phân tích sai sót. |  |
| 12 | 19/10/2026 | 25/10/2026 |  | Đóng gói thư viện Python, dịch vụ REST và Docker. |  |
| 13 | 26/10/2026 | 01/11/2026 |  | Giao diện quan sát phân bố chú ý; hệ RAG minh họa. |  |
| 14 | 02/11/2026 | 08/11/2026 |  | Thí nghiệm chuyển miền nếu còn thời gian; viết chương 1 đến chương 4. |  |
| 15 | 09/11/2026 | 15/11/2026 |  | Viết chương 5 đến chương 8; rà soát định dạng theo mẫu của Khoa. |  |

*Ghi chú: cột "Tóm tắt công việc đã thực hiện" được điền theo kế hoạch dự kiến; nhóm cập nhật theo công việc thực tế trước khi gửi giảng viên hướng dẫn.*
