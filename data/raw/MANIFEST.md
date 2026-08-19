# MANIFEST — Dữ liệu gốc trong `data/raw/`

> Sinh ở Task T08B ngày 19/08/2026. Nhận diện từng bộ **theo tên cột**, không theo tên file,
> rồi đổi tên về quy ước `{dataset}_{split}.{ext}` mô tả ở mục 2 của `docs/DATA.md`.
>
> Thư mục này nằm trong `.gitignore` — chỉ file MANIFEST.md này được commit.
> Bản thân dữ liệu phải tải lại từ nguồn nêu ở `README.md`.

## 1. Bảng ánh xạ tên file

| Bộ | Tên file gốc | Tên file sau khi đổi | Định dạng | Số dòng | Dùng không |
|---|---|---|---|---|---|
| ViHallu | `ViHallu/vihallu-train.csv` | `vihallu_train.csv` | CSV | 7.000 | có |
| ViHallu | `ViHallu/vihallu-public-test.csv` | `vihallu_test_public.csv` | CSV | 1.000 | **không** — `predict_label` rỗng toàn bộ |
| ISE-DSC01 | `ISE-DSC01/ise-dsc01-train.json` | `isedsc01_train.json` | JSON | 36.369 | có |
| ISE-DSC01 | `ISE-DSC01/ise-dsc01-public-test-offcial.json` | `isedsc01_test_public.json` | JSON | 4.794 | **không** — thiếu `verdict` |
| ISE-DSC01 | `ISE-DSC01/ise-dsc01-private-test-offcial.json` | `isedsc01_test_private.json` | JSON | 5.396 | **không** — thiếu `verdict` |
| ViWikiFC | `ViWikiFC/viwikifc_train.csv` | `viwikifc_train.csv` | CSV | 16.738 | có |
| ViWikiFC | `ViWikiFC/viwikifc_dev.csv` | `viwikifc_dev.csv` | CSV | 2.090 | có |
| ViWikiFC | `ViWikiFC/viwikifc_test.csv` | `viwikifc_test.csv` | CSV | 2.091 | có |
| ViFactCheck | `ViFactCheck/train-00000-of-00001.parquet` | `vifactcheck_train.parquet` | Parquet | 5.062 | có |
| ViFactCheck | `ViFactCheck/dev-00000-of-00001.parquet` | `vifactcheck_dev.parquet` | Parquet | 723 | có |
| ViFactCheck | `ViFactCheck/test-00000-of-00001.parquet` | `vifactcheck_test.parquet` | Parquet | 1.447 | có |

Hai file kèm theo của ViFactCheck tải từ Hugging Face, không phải dữ liệu:

| Tên file gốc | Tên file sau khi đổi | Nội dung |
|---|---|---|
| `ViFactCheck/README.md` | `vifactcheck_dataset_card.md` | Dataset card của bộ trên Hugging Face |
| `ViFactCheck/gitattributes` | `vifactcheck_gitattributes.txt` | Cấu hình Git LFS của kho Hugging Face, không dùng đến |

Bốn thư mục con `ViHallu/`, `ISE-DSC01/`, `ViWikiFC/`, `ViFactCheck/` đã bị xóa sau khi dời file lên `data/raw/`.

## 2. Căn cứ nhận diện — tên cột thực tế

| Tên file sau khi đổi | Cột đọc được |
|---|---|
| `vihallu_train.csv` | `id, context, prompt, response, label` |
| `vihallu_test_public.csv` | `id, context, prompt, response, predict_label` |
| `isedsc01_train.json` | `context, claim, verdict, evidence, domain` |
| `isedsc01_test_public.json` | `context, claim` |
| `isedsc01_test_private.json` | `context, claim` |
| `viwikifc_{train,dev,test}.csv` | `pairID, evidence, gold_label, link, context, sentenceID, claim, annotator_labels, title` |
| `vifactcheck_{train,dev,test}.parquet` | `Unnamed: 0, index, Statement, Context, annotation_id, Topic, Author, Url, labels, Evidence` |

Ba file JSON của ISE-DSC01 là một `dict` duy nhất, khóa là chuỗi số thứ tự, mỗi value là một record.

## 3. Đối chiếu với bảng mục 4 của `docs/DATA.md`

| Chỉ tiêu | Kỳ vọng | Đọc được | Khớp |
|---|---|---|---|
| ViHallu — số mẫu có nhãn | 7.000 | 7.000 | ✅ |
| ViHallu — phân bố `no / intrinsic / extrinsic` | 2.245 / 2.448 / 2.307 | 2.245 / 2.448 / 2.307 | ✅ |
| ISE-DSC01 — số mẫu có nhãn | 36.369 | 36.369 | ✅ |
| ISE-DSC01 — phân bố `SUPPORTED / REFUTED / NEI` | 12.786 / 11.000 / 12.583 | 12.786 / 11.000 / 12.583 | ✅ |
| ViWikiFC — chia tập gốc | 16.738 / 2.090 / 2.091 | 16.738 / 2.090 / 2.091 | ✅ |
| ViWikiFC — phân bố train `Supports / Refutes / NEI` | 5.594 / 5.573 / 5.571 | 5.594 / 5.573 / 5.571 | ✅ |
| ViFactCheck — chia tập gốc | 5.062 / 723 / 1.447 | 5.062 / 723 / 1.447 | ✅ |
| ViFactCheck — phân bố train `0 / 1 / 2` | cân bằng | 1.751 / 1.658 / 1.653 | ✅ |

Không có file nào không nhận diện được, không thiếu bộ nào.

## 4. Lệnh kiểm tra lại

```bash
python - <<'PY'
from pathlib import Path
import json, pandas as pd
for f in sorted(Path("data/raw").iterdir()):
    if f.suffix == ".csv":
        df = pd.read_csv(f); print(f.name, len(df), list(df.columns))
    elif f.suffix == ".parquet":
        df = pd.read_parquet(f); print(f.name, len(df), list(df.columns))
    elif f.suffix == ".json":
        d = json.load(open(f, encoding="utf-8"))
        print(f.name, len(d), list(next(iter(d.values())).keys()))
PY
```
