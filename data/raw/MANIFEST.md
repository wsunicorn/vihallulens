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

## 5. Mã băm SHA-256

> Bổ sung ngày 22/10/2026. Tính trên đúng các tệp đã dùng cho mọi thí nghiệm. Ai tải lại dữ liệu
> từ nguồn (hoặc từ Kaggle Dataset `unicorn1209/vihallulens`) thì so mã băm để chắc mình có cùng
> dữ liệu; lệch một byte là lệch số liệu. `tests/test_manifest_hashes.py` tự kiểm bảng này với các
> tệp đang có trong `data/raw/` (tệp nào chưa tải thì bỏ qua).

| Tệp | Kích thước (byte) | SHA-256 |
|---|---:|---|
| `isedsc01_test_private.json` | 21.082.906 | `31c95112b72cef4b744ebdad3d3a55e791b663ba2099708dd4fef4d453cd85c7` |
| `isedsc01_test_public.json` | 19.287.569 | `0d46e2dcf7b082df61efebd00edcda1376065208494955ddca93daede28300ef` |
| `isedsc01_train.json` | 154.804.483 | `76605fc30a4192a1e1d5d961ec32572de727230f3dc5b5d633a499b009b82dd3` |
| `vifactcheck_dataset_card.md` | 3.453 | `1ae40d96a9cac33617ca3695d37299e28edf5fd1a9990d3be7977357b965f0c7` |
| `vifactcheck_dev.parquet` | 1.225.466 | `16b6d8b244ec07be1a6d80fcb389486c2f26e5c10cdc66f6cab72bd159920454` |
| `vifactcheck_gitattributes.txt` | 2.307 | `f4e703ea6e44bbebe53aceed2a89c11e40b88b7ae130c480c89860ab805ffc8f` |
| `vifactcheck_test.parquet` | 2.484.723 | `d797eb5a3797f12c052d4c8dbdda0b9cf7174f3dfce91050f95354b044816214` |
| `vifactcheck_train.parquet` | 8.071.153 | `ff054bc61afb59e3c9aa1dd402f0eb44700a30866c75ee6c66e117517bd510e8` |
| `vihallu_test_public.csv` | 1.529.146 | `e63def805fbc5ef004aedd73c8d00c0083f46ddeecc7079f6605fcdd7f3fdca6` |
| `vihallu_train.csv` | 10.728.910 | `52a9d8605688f77d5e2d4504c81765e8183f83e1d0ceab8957aeab67381c9bce` |
| `viwikifc_dev.csv` | 2.924.939 | `d0d45cfde4844c6b6f89dc61700416d0f3f1f9b6edba871c23f9f2cb88cf83fc` |
| `viwikifc_test.csv` | 2.950.356 | `ff6016f9c04ac6aee6333583876bcf5f88ba455141767f548213f1868726c84c` |
| `viwikifc_train.csv` | 23.370.947 | `477adcca59920d40f5cb6580a7cbdd6828e22839f0bb52abed7212c0edf4af5d` |

Kiểm tay: `sha256sum data/raw/*` trên Linux, `Get-FileHash data/raw/* -Algorithm SHA256` trên Windows.
