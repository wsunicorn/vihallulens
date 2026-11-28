# TÀI LIỆU THAM KHẢO {#tai-lieu-tham-khao .unnumbered}

@@GEN_REFS@@

<div style="page-break-after: always"></div>

# PHỤ LỤC {#phu-luc .unnumbered}

## Phụ lục A — Cấu trúc mã nguồn và kiểm thử

Mã nguồn của hệ thống được tổ chức theo bố cục `src/` với gói `vihallulens`; bộ kiểm thử kiểm tra các điều kiện luôn phải đúng của phép tính, như các ví dụ ở mục [[sec:c3-chia-tap]], [[sec:c4-dac-trung]] và [[sec:c4-hook]]. Lượt chạy kiểm thử trên máy cá nhân ngày 25/11/2026 cho kết quả 860 ca đạt, 0 ca thất bại, 0 ca bỏ qua, trong 22,8 giây; các ca kiểm thử chạy trên CPU, không cần GPU. [[fig:terminal]] cho thấy cây thư mục, lượt chạy kiểm thử và trạng thái của dịch vụ; [[tab:duong-dan]] liệt kê vị trí các thành phần chính.

*[[tab:duong-dan]] Vị trí các thành phần của mã nguồn và dữ liệu*

| Thành phần | Vị trí |
|---|---|
| Mã nguồn thư viện | `src/vihallulens/` (47 tệp, 6.163 dòng) |
| Kiểm thử | `tests/` (50 tệp, 8.197 dòng, 860 ca) |
| Chương trình dòng lệnh | `scripts/` (38 tệp) |
| Cấu hình thí nghiệm | `configs/` (24 tệp YAML: 23 cấu hình thí nghiệm, 1 tệp mẫu; kèm danh sách 300 mẫu của E19) |
| Notebook chạy GPU | `notebooks/` (21 tệp) |
| Kết quả | `results/`, giải thích từng tệp ở `results/README.md` |
| Bundle bộ phát hiện | `models/e03_chunk_aware.pkl` (11,5 KB) kèm tệp mô tả `.json` |
| Tài liệu dự án | `docs/SPEC.md`, `docs/DATA.md`, `docs/EXPERIMENTS.md`, `docs/REFERENCES.md` |
| Mã sinh hình vẽ của báo cáo | `docs/media/src/` |

![Cấu trúc mã nguồn, lượt chạy kiểm thử và trạng thái dịch vụ](media/hinh_terminal_ma_nguon.png)

*[[fig:terminal]] Cấu trúc mã nguồn, lượt chạy kiểm thử và trạng thái dịch vụ*

Dữ liệu thô không được đưa vào kho Git; bảng ánh xạ từ tên tệp gốc sang tên chuẩn nằm ở `data/raw/MANIFEST.md`.

## Phụ lục B — Tài liệu giao diện lập trình và đóng gói

Dịch vụ REST tự sinh tài liệu OpenAPI tại đường dẫn `/docs` ([[fig:openapi]]). Trang chủ của hệ thống giới thiệu đề tài và ba cách sử dụng bộ phát hiện: thư viện Python, dịch vụ REST và ảnh Docker.

![Tài liệu OpenAPI tự sinh của dịch vụ REST](media/anh_tai_lieu_rest_api.png)

*[[fig:openapi]] Tài liệu OpenAPI tự sinh của dịch vụ REST*

Toàn bộ dịch vụ chạy được bằng một lệnh:

```
docker compose up --build
```

Ảnh Docker có kích thước 10,5 GB. Trọng số của mô hình đọc (khoảng 15 GB) không nằm trong ảnh mà được tải vào một vùng lưu trữ riêng (volume) ở lần chạy đầu, để việc sửa mã nguồn không buộc dựng lại 15 GB dữ liệu. Nếu máy không có GPU NVIDIA, lệnh trên báo lỗi sau khoảng sáu giây thay vì tải trọng số rồi mới thất bại.

## Phụ lục C — Tái lập kết quả

Phụ lục này gồm hai phần: các lệnh dựng lại kết quả từ dữ liệu gốc, và mức tái lập thực tế của từng loại kết quả: trùng từng chữ số, chỉ trùng trong một sai số nhỏ, hay không lặp lại được, và vì sao.

Các lệnh, theo đúng thứ tự (bước trích đặc trưng cần GPU, các bước khác chạy trên CPU; cách dựng lại quyển ở `docs/report/README.md`):

```
uv sync                                    # môi trường
python scripts/normalize_data.py --all     # chuẩn hóa dữ liệu
python scripts/split_data.py               # chia tập
CFG=configs/e03_chunk_sentence_vihallu.yaml
python scripts/extract_features.py --config $CFG
python scripts/run_chunk_aware.py --config $CFG
python scripts/build_tradeoff.py           # bảng chi phí
python scripts/run_paired_tests.py         # kiểm định ghép cặp
python scripts/serve.py --bundle models/e03_chunk_aware.pkl --port 8000
```

**Môi trường đã chạy.** Phần trích đặc trưng, tinh chỉnh bộ mã hóa và đo chi phí chạy trên Kaggle (Tesla T4, Python 3.12.13, PyTorch 2.10.0, transformers 5.0.0–5.16.1, bitsandbytes 0.50.1–0.50.2); phần huấn luyện bộ phân loại, đánh giá và dịch vụ chạy trên máy cá nhân (Python 3.11.9, PyTorch 2.14.0, transformers 5.17.0). Trên Kaggle, phiên bản thay đổi giữa các notebook, nên mỗi notebook in ra phiên bản đã dùng ở ô đầu.

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

**Những gì được cố định.** [[tab:co-dinh]] liệt kê các thành phần được giữ cố định để một lượt chạy lại đọc đúng dữ liệu, đúng cấu hình và đúng mã nguồn như lượt đã báo cáo.

*[[tab:co-dinh]] Các thành phần được cố định để tái lập*

| Thành phần | Cách cố định |
|---|---|
| Chia tập | Theo ngữ cảnh, tỷ lệ 80/10/10, seed 42. Thứ tự các nhóm lấy từ giá trị băm SHA-256 của cặp (seed, mã ngữ cảnh), nên không phụ thuộc thứ tự đọc tệp (mục [[sec:c3-chia-tap]]). |
| Cấu hình | 23 tệp YAML cấu hình thí nghiệm (cùng một tệp mẫu) trong `configs/`, được pydantic kiểm tra khi nạp. Mỗi tệp đặc trưng và mỗi bản ghi kết quả mang mã băm của cấu hình đã sinh ra nó. |
| Mã nguồn | Mỗi bản ghi trong `results/runs.jsonl` mang mã commit Git của lượt chạy. Ô đầu của mỗi notebook Kaggle in mã commit và phiên bản thư viện; notebook được lưu nguyên đầu ra. |
| Mẫu prompt | Cố định từ ngày 19/08/2026 (mục [[sec:c4-prompt]]), không đổi trong suốt các thí nghiệm. |
| Mô hình đọc | Qwen2.5-7B-Instruct, kho Hugging Face ở mã commit `a09a3545`; kiểu số float16 bỏ lớp 27, riêng Qwen2.5-1.5B dùng bfloat16 ([[tab:kieu-so]]). |
| Bộ phân loại | Hồi quy logistic của scikit-learn với `random_state=42`; cách gộp đầu chú ý chọn trên tập dev, tập test chỉ dùng để báo cáo. |
| LLM giám khảo | Mỗi phản hồi của Gemini được lưu vào `results/judge_cache.jsonl` theo khóa SHA-256 của (mô hình, prompt); khi đánh giá lại, kết quả được đọc từ bộ nhớ đệm này thay vì gọi lại API. Lượt chạy lại tiêu chí rút gọn tháng 11 lưu riêng ở `results/judge_cache_v1_rerun.jsonl`. |
| Dữ liệu gốc | Không sửa tệp nào trong `data/raw/`; mã băm SHA-256 của các tệp đã dùng ở [[tab:ma-bam]]. |

**Mức tái lập của từng loại kết quả.** [[tab:muc-tai-lap]] phân loại các kết quả theo mức lặp lại được khi chạy lại.

*[[tab:muc-tai-lap]] Mức tái lập của từng loại kết quả*

| Loại kết quả | Mức tái lập | Ghi chú |
|---|---|---|
| Chuẩn hóa, chia tập, thống kê dữ liệu, phân tích rò rỉ | Trùng từng chữ số | Phép tính không có yếu tố ngẫu nhiên, có ca kiểm thử kiểm tra kết quả. |
| Dự đoán của bộ phát hiện đã đóng gói | Trùng từng dự đoán | Nạp lại `models/e03_chunk_aware.pkl` và đánh giá 700 mẫu test: trùng 700/700 với lúc thí nghiệm. |
| Huấn luyện lại bộ phân loại từ tệp đặc trưng | Trùng trong cùng một môi trường | Giữa Kaggle và máy cá nhân, điểm trên tập dev lệch tối đa 0,0075 ở cấu hình phụ, do bộ tối ưu lbfgs hội tụ khác nhau theo phiên bản thư viện số; cấu hình được chọn cho 0,7768 ở cả hai. Vì vậy mọi bảng so sánh được tính trên cùng một máy. |
| Trích đặc trưng chú ý | Trùng trên cùng loại GPU; trong sai số số học nếu khác phần cứng | Tính ở float16 trên GPU nên không bảo đảm trùng từng bit giữa các phần cứng và phiên bản. Trên cùng Tesla T4 của Kaggle thì trùng: lượt trích lại ViHallu ngày 23/10/2026 cho thí nghiệm gộp đặc trưng theo từng câu (E18) trùng hoàn toàn với lượt trích của bộ phát hiện chunk-aware (E03) ngày 30/08/2026 ở cả 7.000 mẫu (giá trị lưu ở 6 chữ số thập phân), và đánh giá lại cho đúng macro-F1 0,7567. Tệp đặc trưng không đưa lên kho mã vì dung lượng; chạy lại phải trích lại trên GPU, gần một giờ T4 cho riêng ViHallu. |
| Tinh chỉnh PhoBERT, XLM-R | Dao động theo seed và theo lượt | Ba seed mỗi mô hình, độ lệch chuẩn 0,011 (PhoBERT) và 0,017 (XLM-R), ghi trong `results/runs.jsonl`. Cố định seed chưa đủ: cùng seed 42, XLM-R hội tụ ở lượt ngày 27/08 nhưng không hội tụ ở lượt ngày 28/08. |
| LLM giám khảo Gemini | Từ bộ nhớ đệm | Gọi lại API cho kết quả khác vì mô hình phía nhà cung cấp thay đổi theo thời gian: chạy lại tiêu chí rút gọn trên cùng 300 mẫu vào tháng 11/2026 cho macro-F1 0,708 thay vì 0,664 (+0,045 [+0,010; +0,081]). Số trong báo cáo tái lập được từ bộ nhớ đệm. |
| Thời gian và bộ nhớ GPU | Gắn với phần cứng | Đo trên Tesla T4, mỗi cấu hình một phiên riêng hoặc đo xen kẽ, vì hai lượt nối nhau trong cùng phiên đã chậm đi 10–15 % do giảm xung nhịp. |

## Phụ lục D — Nguồn số liệu

Mọi con số trong Chương 6 và Chương 7 đều có bản ghi đọc được bằng máy trong thư mục `results/` ([[tab:nguon-so-lieu]]). Phần diễn giải chi tiết của từng thí nghiệm nằm ở `docs/EXPERIMENTS.md`.

*[[tab:nguon-so-lieu]] Nguồn số liệu của các bảng kết quả*

| Bảng trong báo cáo | Tệp nguồn và khóa bản ghi |
|---|---|
| [[tab:ket-qua-chinh]] | `results/runs.jsonl`, khóa `e01_*`, `e02_*`, `e03_*`, `e09_*`, `e10_*` |
| [[tab:dinh-vi]] | `results/runs.jsonl`, khóa `e06_localization_isedsc01`, `e08_extrinsic_viwikifc` |
| [[tab:chia-doan]] | `results/runs.jsonl`, khóa `e04_*`, `e05_*` |
| [[tab:ngu-canh-dai]] | `results/runs.jsonl`, khóa `e07_*` |
| [[tab:can-thiep]] | `results/runs.jsonl`, khóa `e08_extrinsic_viwikifc` |
| [[tab:ablation]], [[tab:chong-lan]] | `results/runs.jsonl`, khóa `e12_ablation_*` |
| [[tab:mo-hinh-doc]], [[tab:ece-tham-so]] | `results/runs.jsonl`, khóa `e13_*`, `e14_*`, `e07_*`, `e15_*` |
| [[tab:ghep-cap]] | `results/paired_tests.json`, tính từ dự đoán đã lưu trong `results/runs.jsonl` |
| [[tab:ece-cung-co]] | `results/calibration.json` |
| [[tab:viwikifc]] | `results/runs.jsonl`, khóa `e15_*` |
| [[fig:ban-do-dau]], [[fig:thay-doi]], [[fig:do-tin-cay]] | `results/figures/*.json`, dựng lại bằng `scripts/build_figure_data.py` |
| [[tab:cheo-bo]] | `results/runs.jsonl`, khóa `e16_*` |
| Mục [[sec:c6-vifactcheck]] | `results/runs.jsonl`, khóa `e17_*` |
| [[tab:theo-cau]] | `results/runs.jsonl`, khóa `e18_sentence_*`; nhánh `whole` là bản ghi `e03_chunk_aware` |
| [[fig:cat-bo]] | `results/runs.jsonl`, khóa `e19_attribution_viwikifc`; điểm cắt bỏ từng mẫu ở `results/e19_attribution.jsonl` |
| [[tab:chi-phi]] | `results/tradeoff.csv`, `results/feasibility.jsonl` |
| [[tab:tu-kiem-tra]] | `results/e11_self_check.jsonl`, `results/e11_self_check.json` |
| [[tab:nhan-cau-truc]], [[fig:ma-tran-nham-lan]] | `results/error_analysis.json`, `results/error_analysis.csv` |
| [[tab:ro-ri]], [[tab:ket-qua-chia]] | `results/leakage_report.md` |
| [[tab:kiem-nei]], [[tab:bang-cheo-nei]] | `results/nei_mapping_audit*.csv` |

## Phụ lục E — Bảng tham khảo bổ sung

Các bảng dưới đây được nhắc tới ở Chương 3, Chương 4, Chương 6 và Chương 7. Bốn bảng cuối là số liệu đầy đủ của [[fig:dong-gop]], [[fig:cheo-bo]], [[fig:ghep-cap]] và của phân tích ở mục [[sec:c7-hieu-chinh]].

*[[tab:schema]] Lược đồ chung dùng cho cả bốn bộ dữ liệu*

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `sample_id` | Chuỗi | Khóa chính, duy nhất trên toàn bộ dữ liệu |
| `context_id` | Chuỗi | Định danh ngữ cảnh, băm SHA-256 từ nội dung ngữ cảnh; là đơn vị chia tập |
| `context` | Chuỗi | Ngữ cảnh truy xuất |
| `question` | Chuỗi hoặc rỗng | Câu hỏi; rỗng với ba bộ kiểm chứng thông tin |
| `response` | Chuỗi | Phản hồi (hoặc phát biểu) cần kiểm tra |
| `label` | Ba lớp | `no` / `intrinsic` / `extrinsic` |
| `evidence`, `evidence_start` | Chuỗi, số nguyên | Câu bằng chứng nguyên văn và vị trí ký tự của nó trong ngữ cảnh, nếu bộ dữ liệu có |
| `meta` | Từ điển khóa – giá trị | Thông tin riêng từng bộ, ví dụ loại prompt của ViHallu |

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

*[[tab:ablation]] Macro-F1 khi thêm lần lượt các nhóm đặc trưng (trong ngoặc là chênh lệch so với bước liền trước)*

| Bộ dữ liệu | Cách gộp đầu | Chỉ bề mặt | + Lookback gộp | + Chunk-aware | + DRIFT (nhóm stability) |
|---|---|---|---|---|---|
| ViHallu | Chọn riêng ở từng bước | 0,6562 | 0,7653 (+0,1091) | 0,7388 (−0,0266) | 0,7746 (+0,0358) |
| ViHallu | Cố định 32 đầu | 0,6562 | 0,7759 (+0,1197) | 0,7688 (−0,0071) | 0,7746 (+0,0057) |
| ISE-DSC01 | Chọn riêng ở từng bước | 0,4767 | 0,7837 (+0,3070) | 0,7839 (+0,0002) | 0,7918 (+0,0079) |
| ISE-DSC01 | Cố định 32 đầu | 0,4767 | 0,6554 (+0,1787) | 0,6950 (+0,0396) | 0,7024 (+0,0074) |

*[[tab:cheo-bo]] Đánh giá chéo bộ dữ liệu giữa ViHallu và ISE-DSC01*

| Huấn luyện trên | Đánh giá trên | Nhóm đặc trưng | macro-F1 chéo bộ [KTC 95 %] | Khi huấn luyện trên chính bộ đích | Mức giảm | Nhị phân chéo bộ | ECE chéo bộ |
|---|---|---|---|---|---|---|---|
| ViHallu | ISE-DSC01 | Lookback gộp | 0,4301 [0,4146–0,4456] | 0,7851 | −0,3550 | 0,6309 | 0,372 |
| ViHallu | ISE-DSC01 | Chunk-aware | 0,3584 [0,3450–0,3719] | 0,7919 | −0,4334 | 0,6640 | 0,354 |
| ISE-DSC01 | ViHallu | Lookback gộp | 0,5540 [0,5179–0,5913] | 0,7451 | −0,1911 | 0,7838 | 0,291 |
| ISE-DSC01 | ViHallu | Chunk-aware | 0,5521 [0,5160–0,5897] | 0,7567 | −0,2047 | 0,7756 | 0,297 |

*[[tab:ghep-cap]] Hiệu macro-F1 giữa chunk-aware và lookback gộp trong tám cấu hình*

| Cấu hình | Số mẫu test | Hiệu macro-F1 | KTC 95 % ghép cặp | *p* bootstrap | *p* sau Holm |
|---|---|---|---|---|---|
| ViHallu, Qwen2.5-7B | 700 | +0,0116 | [−0,0233; +0,0453] | 0,52 | 1,00 |
| ViHallu, Qwen2.5-3B | 700 | −0,0128 | [−0,0442; +0,0186] | 0,43 | 1,00 |
| ViHallu, Qwen2.5-1.5B | 700 | +0,0114 | [−0,0056; +0,0286] | 0,20 | 0,99 |
| ViHallu, Sailor2-8B | 697 | −0,0258 | [−0,0570; +0,0053] | 0,11 | 0,67 |
| ISE-DSC01, 29.077 mẫu huấn luyện | 3.646 | +0,0068 | [−0,0010; +0,0144] | 0,09 | 0,67 |
| ISE-DSC01, 5.600 mẫu huấn luyện | 3.646 | +0,0050 | [−0,0045; +0,0145] | 0,30 | 1,00 |
| ViWikiFC | 2.091 | −0,0012 | [−0,0132; +0,0106] | 0,85 | 1,00 |
| ViFactCheck | 1.447 | +0,0226 | [−0,0029; +0,0478] | 0,08 | 0,67 |

*[[tab:ece-tham-so]] ECE và số tham số phải huấn luyện của lookback gộp và chunk-aware trong bảy cấu hình (bên có ECE thấp hơn in đậm)*

| Cấu hình | Tham số, lookback | Tham số, chunk-aware | ECE, lookback | ECE, chunk-aware |
|---|---|---|---|---|
| ViHallu, Qwen2.5-7B | 2.271 | **579** | 0,109 | **0,044** |
| ISE-DSC01, 29.077 mẫu | **2.271** | 2.751 | **0,026** | 0,033 |
| ISE-DSC01, 5.600 mẫu | **2.271** | 2.511 | **0,146** | 0,152 |
| ViWikiFC, Qwen2.5-7B | **2.271** | 2.751 | **0,050** | 0,062 |
| ViHallu, Sailor2-8B | **195** | 1.155 | **0,048** | 0,071 |
| ViHallu, Qwen2.5-3B | **195** | 1.851 | **0,061** | 0,089 |
| ViHallu, Qwen2.5-1.5B | **1.011** | 1.131 | **0,050** | 0,061 |

## Phụ lục F — Sử dụng công cụ AI trong quá trình thực hiện

Phụ lục này trình bày cách nhóm sử dụng công cụ AI trong quá trình nghiên cứu và phát triển phần mềm của khóa luận: dùng vào việc gì, theo quy trình nào, với những ràng buộc nào, và rút ra kinh nghiệm gì. Mục đích là để người đọc thấy rõ ranh giới giữa phần do nhóm quyết định và phần công cụ hỗ trợ, đồng thời có thể lặp lại cách làm. Mức tái lập của các kết quả thực nghiệm được trình bày riêng ở Phụ lục C.

**Hai vai trò khác nhau của mô hình ngôn ngữ lớn.** Trong khóa luận, mô hình ngôn ngữ lớn xuất hiện ở hai vai trò cần tách bạch. Thứ nhất, chúng là đối tượng nghiên cứu: Qwen2.5 là mô hình đọc mà đặc trưng chú ý được trích ra (Chương 4), còn Gemini là phương pháp so sánh dùng LLM giám khảo ở Chương 6; vai trò này thuộc về phương pháp và đã được mô tả ở các chương chính. Thứ hai, nhóm dùng một trợ lý lập trình dựa trên mô hình ngôn ngữ lớn, tích hợp trong trình soạn thảo mã, như một công cụ hỗ trợ kỹ thuật. Phụ lục này chỉ nói về vai trò thứ hai.

**Phân định vai trò.** Công cụ AI chỉ giữ vai trò hỗ trợ thực thi. Mọi quyết định về đề tài, thiết kế thực nghiệm, cách đánh giá và kết luận do nhóm đưa ra; công cụ thực hiện các phần việc kỹ thuật theo yêu cầu cụ thể của nhóm và chịu sự kiểm duyệt của nhóm ở từng bước ([[tab:phan-dinh-ai]]).

*[[tab:phan-dinh-ai]] Phân định vai trò giữa nhóm và công cụ AI*

| Hạng mục | Nhóm thực hiện và quyết định | Công cụ AI hỗ trợ |
|---|---|---|
| Đề tài, câu hỏi và giả thuyết | Chọn đề tài và ý tưởng chunk-aware; đặt ba câu hỏi nghiên cứu, năm giả thuyết; ghi hướng dự đoán trước khi chạy thí nghiệm can thiệp | Không tham gia |
| Thiết kế thực nghiệm | Chọn bộ dữ liệu, cách chia tập, các phương pháp so sánh, ràng buộc phần cứng và ngân sách GPU; duyệt từng thí nghiệm trước khi chạy; đặt các phép đối chứng | Trả lời câu hỏi kỹ thuật và nêu phương án khi được hỏi |
| Mã nguồn và kiểm thử | Đặt yêu cầu và tiêu chí hoàn thành cho từng việc; đọc lại, chạy và duyệt từng pull request trước khi gộp | Viết mã và kiểm thử theo yêu cầu |
| Chạy thực nghiệm | Chạy notebook trên Kaggle, theo dõi hạn mức GPU, lưu notebook và nhật ký làm minh chứng, đối chiếu kết quả | Dựng notebook; đọc nhật ký lỗi để chỉ ra nguyên nhân |
| Kiểm chứng nhãn | Hai thành viên gán nhãn độc lập 100 mẫu NEI (mục [[sec:c3-anh-xa]]) | Không tham gia gán nhãn |
| Phân tích và kết luận | Diễn giải kết quả, quyết định trình bày cả kết quả bất lợi, rút ra kết luận | Tổng hợp số liệu từ tệp kết quả khi được yêu cầu |

**Quy trình làm việc.** Để công cụ không tự ý quyết định thay nhóm và để mọi bước kiểm tra được, nhóm tổ chức công việc theo sáu nguyên tắc:

- **Bộ quy tắc dự án viết thành văn bản.** Tệp `CONVENTIONS.md` (khoảng 200 dòng) ghi ràng buộc cứng về phần cứng và ngân sách, các quyết định đã chốt và những điều bị cấm. Công cụ đọc tệp này ở đầu mỗi phiên, nên quy tắc không phụ thuộc vào trí nhớ của một cuộc hội thoại.
- **Danh sách việc tuần tự.** Tệp `TASKS.md` chia công việc thành 50 mã việc trong 10 giai đoạn (58 việc nếu tính cả các việc bổ sung), mỗi việc có tiêu chí hoàn thành là một lệnh chạy được. Các việc được thực hiện tuần tự, không làm trước việc chưa đến lượt.
- **Mỗi việc một pull request.** Từ 19/08 đến 22/10/2026, kho mã có 135 pull request; nhóm đọc và gộp từng pull request. Ngày 22/10/2026 kho mã được tạo lại với đúng lịch sử commit của nhánh chính; 135 pull request gốc vẫn giữ trong kho lưu trữ `vihallulens-luu-tru`, và danh sách đầy đủ kèm ngày thực tế nằm ở `docs/LICH_SU_PR.md`.
- **Chỉ đánh dấu hoàn thành khi có bằng chứng.** Một việc chỉ được đánh dấu xong khi lệnh trong tiêu chí chạy được và đầu ra được dán vào pull request; với việc cần GPU, notebook Kaggle đã chạy được lưu nguyên đầu ra trong thư mục `notebooks/`.
- **Dừng lại và hỏi.** Mọi quyết định chưa có trong bộ quy tắc (thêm thư viện, đổi kiến trúc, đổi hướng khi một bước kiểm tra thất bại), công cụ phải dừng lại để nhóm quyết định.
- **Ghi nhật ký diễn giải.** Sau mỗi việc, mục đích, kết quả số và điều rút ra được ghi lại trong `TASKS.md` và `docs/EXPERIMENTS.md`; đây cũng là nguồn số liệu ở Phụ lục D.

**Các ràng buộc đặt cho công cụ.** Dưới đây là một số quy tắc trích nguyên văn từ `CONVENTIONS.md`. Đây là phần quan trọng nhất của quy trình, vì các quy tắc này áp dụng cho mọi phiên làm việc chứ không chỉ cho một yêu cầu.

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

**Một số yêu cầu tiêu biểu.** [[tab:yeu-cau-ai]] trích một số yêu cầu nhóm đưa ra trong quá trình làm (rút gọn, giữ nguyên ý), kèm mục đích của từng yêu cầu. Điểm chung là nhóm luôn yêu cầu kiểm tra trước khi sử dụng tài nguyên tính toán và giữ quyền quyết định ở những bước then chốt của nghiên cứu.

*[[tab:yeu-cau-ai]] Một số yêu cầu tiêu biểu nhóm đưa cho công cụ*

| Ngày | Yêu cầu (trích) | Mục đích |
|---|---|---|
| 19/08 | “Câu ‘dừng và báo’ trong TASKS.md nghĩa là dừng để hỏi ý kiến, không phải dừng để đổi đề tài.” | Giữ quyền quyết định hướng đề tài ở nhóm trước bước kiểm tra khả thi T07 |
| 19/08 | “Các file dữ liệu trên Kaggle đều có định dạng như này, hãy xem code lại coi có chỗ nào sai không trước khi tôi chạy.” | Rà soát mã trước khi sử dụng hạn mức GPU |
| 20/08 | “Có cần so sánh chạy hai phiên khác nhau phần ô 6 và 7 không?” | Dẫn tới quy tắc đo chi phí mỗi cấu hình một phiên riêng, sau khi phát hiện giảm xung nhịp làm chậm 10–15 % |
| 27/08 | “Kiểm tra lại lần nữa coi đúng chưa và cho tôi biết 5 seed có cần thiết không.” | Cân nhắc độ tin cậy với chi phí GPU trước khi quyết định |
| 30/08 | “… phép đối chứng để tách nốt câu hỏi ‘câu thắng vì ngữ nghĩa hay vì không chồng lấn’.” | Đặt câu hỏi dẫn tới phép đối chứng cửa sổ không chồng lấn ở mục [[sec:c6-chia-doan]] |
| 11/09 | “Dựa vào log lúc nãy chạy là thành công rồi hả, sao đã tick vào ô 40?” | Phát hiện lỗi đánh dấu hoàn thành khi chưa đối chiếu minh chứng |
| 11/09 | “Kiểm tra lại toàn bộ repo xem các file có sai sót và không khớp nhau ở chỗ nào không.” | Rà soát chéo toàn bộ kho mã trước giai đoạn tổng hợp kết quả |

**Kinh nghiệm rút ra.** Bốn điều nhóm thấy quan trọng nhất khi dùng công cụ AI trong một dự án nghiên cứu:

- **Công cụ có thể đưa ra kết quả sai với độ tự tin cao, nên mọi con số phải đối chiếu với tệp kết quả.** Nhóm đã phát hiện ba lỗi nhờ đối chiếu. Số mẫu ISE-DSC01 có bằng chứng nguyên văn bị đếm thành 23.785 thay vì 23.783, do hai mẫu có bằng chứng chỉ là dòng trống. Hàm xếp hạng BM25 dùng phép sắp xếp không ổn định khiến 17 trên 1.836 cặp ngữ cảnh khác nhau giữa hai máy; lỗi này đã được sửa bằng phép sắp xếp có quy tắc xử lý giá trị bằng nhau. Một việc từng bị đánh dấu hoàn thành trước khi nhật ký chạy được kiểm tra.
- **Quy tắc được văn bản hóa có hiệu lực lâu dài hơn chỉ dẫn trong hội thoại.** Khi một phiên làm việc dài bị tóm tắt lại, những chỉ dẫn chỉ nằm trong hội thoại có thể bị bỏ sót; quy tắc trong `CONVENTIONS.md` thì được đọc lại mỗi phiên. Vì vậy mỗi quyết định quan trọng đều được ghi vào tệp này ngay khi chốt.
- **Việc sử dụng GPU phải được ước tính và chạy lại được từng phần.** Nhóm yêu cầu mọi notebook ước tính thời gian trước khi chạy và ghi kết quả từng mẫu ngay khi tính xong, để một phiên Kaggle bị gián đoạn không làm mất phần đã chạy.
- **Công cụ không thay thế được phán đoán khoa học.** Những quyết định định hình kết quả, như đặt phép đối chứng nào, ghi hướng dự đoán trước khi chạy, trình bày đầy đủ kết quả bất lợi của phần chunk-aware, đều do nhóm đưa ra.

**Tính tái lập của quy trình.** Bộ quy tắc `CONVENTIONS.md`, danh sách việc `TASKS.md`, lịch sử 135 pull request (`docs/LICH_SU_PR.md`), các notebook đã chạy và nhật ký `results/runs.jsonl` đều nằm trong kho mã nguồn. Người đọc có thể kiểm tra từng bước đã làm, và có thể lặp lại cách làm này với một công cụ hỗ trợ khác.

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
| 3 | 17/08/2026 | 23/08/2026 | 19/08/2026 | Dựng khung mã nguồn, cấu hình và bộ ghi kết quả; nạp Qwen2.5-7B 4 bit trên Kaggle T4; chốt mẫu prompt và trích chú ý bằng forward hook, vượt qua bước kiểm tra khả thi kỹ thuật; chuẩn hóa bốn bộ dữ liệu, kiểm chứng thủ công phép ánh xạ nhãn NEI, chia tập theo ngữ cảnh, báo cáo rò rỉ, chia đoạn và xây dựng kho truy xuất ViWikiFC. |  |
| 4 | 24/08/2026 | 30/08/2026 | 28/08/2026 | Các phương pháp so sánh: đặc trưng bề mặt (E01), tinh chỉnh PhoBERT, XLM-R, InfoXLM (E09), Gemini giám khảo (E10); tái lập Lookback Lens (E02); chunk-aware chia theo câu (E03); thử các cửa sổ token và cấu hình đối chứng, chọn cách chia theo câu (E04, E05). |  |
| 5 | 31/08/2026 | 06/09/2026 | 06/09/2026 | Định vị chú ý trên ISE-DSC01 (E06); chunk-aware trên ngữ cảnh dài (E07); thí nghiệm loại bỏ câu bằng chứng (E08); phân tích đóng góp của từng nhóm đặc trưng (E12); bắt đầu đổi mô hình đọc sang Sailor2-8B (E13). |  |
| 6 | 07/09/2026 | 13/09/2026 | 11/09/2026 | Hoàn thành thí nghiệm Sailor2-8B (E13); mô hình đọc nhỏ hơn 3B và 1.5B (E14); so sánh độ chính xác và chi phí (E11); so sánh với kết quả đã công bố trên ViWikiFC (E15); đánh giá chéo bộ dữ liệu (E16); phân tích sai sót; thư viện Python, dịch vụ REST, Docker, giao diện quan sát và hệ RAG minh họa chạy trên T4. |  |
| 7 | 14/09/2026 | 20/09/2026 | 20/09/2026 | Dựng bộ slide trình bày với GVHD; trang giới thiệu hệ thống; rà soát toàn bộ kho mã, sửa các điểm trong tài liệu chưa khớp với mã nguồn. |  |
| 8 | 21/09/2026 | 27/09/2026 |  | Viết bản thảo đầy đủ tám chương của quyển; tự đánh giá mức hoàn thành ba câu hỏi nghiên cứu, đề xuất ba thí nghiệm bổ sung. |  |
| 9 | 28/09/2026 | 04/10/2026 | 02/10/2026 | Gửi báo cáo giữa kỳ cho GVHD; sửa định dạng quyển theo mẫu của Khoa. |  |
| 10 | 05/10/2026 | 11/10/2026 |  | Tiếp thu ý kiến GVHD ngày 05/10: in một mặt, giữ bố cục tám chương, thêm phần sử dụng công cụ AI và tái lập; dựng lại quyển v3. |  |
| 11 | 12/10/2026 | 18/10/2026 | 16/10/2026 | Rà soát định dạng, mục lục và chú thích; quyển v4, 130 trang; bộ slide Hội đồng rút gọn; gửi GVHD quyển v4 và slide. |  |
| 12 | 19/10/2026 | 25/10/2026 |  | Cố định phiên bản mô hình và thư viện, thêm mã băm dữ liệu gốc; bộ slide Hội đồng 23 trang; ba thí nghiệm bổ sung: chuyển sang miền tin tức trên ViFactCheck (E17), gộp đặc trưng theo từng câu phản hồi (E18), so sánh định vị bằng chú ý với cắt bỏ ngữ cảnh (E19); đưa nguồn dựng quyển vào kho mã; cập nhật quyển với kết quả mới. |  |
| 13 | 26/10/2026 | 01/11/2026 |  | Làm bộ slide trình bày trước Hội đồng; hoàn thiện quyển báo cáo. |  |
| 14 | 02/11/2026 | 08/11/2026 |  | Tiếp tục làm bộ slide và hoàn thiện quyển báo cáo. |  |
| 15 | 09/11/2026 | 15/11/2026 |  | Hoàn thiện bộ slide Hội đồng (31 slide); rà dùng từ, bố cục và định dạng quyển theo mẫu báo cáo. |  |
| 16 | 16/11/2026 | 22/11/2026 |  | Đọc lại và chỉnh sửa luận văn. |  |
| 17 | 23/11/2026 | 29/11/2026 |  | Đo chi phí tự kiểm tra với Qwen2.5-3B; đối chiếu kiểu số của Sailor2-8B; kiểm định ghép cặp giữa các phương pháp; so sánh hiệu chỉnh xác suất ở cùng số tham số; bổ sung phép kiểm tra tiêu chí đánh giá của LLM giám khảo; vẽ lại bảy biểu đồ kết quả; rà diễn đạt và rút gọn quyển. |  |

*Ghi chú: cột "Tóm tắt công việc đã thực hiện" ghi theo công việc thực tế, đối chiếu với ngày hoàn thành trong `TASKS.md`, lịch sử pull request (`docs/LICH_SU_PR.md`) và thời điểm ghi kết quả trong `results/runs.jsonl`. Cột "Ngày báo cáo GVHD" ghi ngày gửi thư báo cáo; từ tháng 10, theo ý kiến GVHD, nhóm chỉ báo cáo khi có kết quả mới.*
