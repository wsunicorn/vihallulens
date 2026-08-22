"""Task T13: does ViWikiFC's NEI label really mean extrinsic hallucination?

Section 3 of docs/DATA.md maps NEI onto ``extrinsic`` and warns in the same breath that the
two are not equivalent. NEI means "the context does not settle this claim"; extrinsic
hallucination means "this claim brings in something the context never said". A claim can be
unsettled by a context that nevertheless contains every fact it mentions, and then the mapping
is wrong. Nobody knows how often that happens until somebody reads a sample by hand.

Two modes:

``--prepare``  draws the sample and writes one annotation sheet per person.
``--report``   reads the filled sheets, writes results/nei_mapping_audit.csv, and prints the
               agreement figures the task asks for.

The two people must not see each other's answers while working, so they get separate files
rather than two columns of one file.

Usage:
    python scripts/audit_nei_mapping.py --prepare
    python scripts/audit_nei_mapping.py --report
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

DEFAULT_INTERIM_DIR = Path("data/interim")
DEFAULT_RESULTS_DIR = Path("results")
AUDIT_NAME = "nei_mapping_audit"

# Fixed by section 3 of CLAUDE.md and never changed, so the same 100 samples come out on any
# machine and the audit can be repeated or checked by someone else.
SEED = 42

N_SAMPLES = 100
N_CONTROLS_PER_LABEL = 10

# Excel on Windows reads a plain UTF-8 CSV as mojibake. The BOM is what makes Vietnamese
# display correctly when the file is opened by double-clicking it, which is how it will be
# opened.
CSV_ENCODING = "utf-8-sig"

ANNOTATORS = ("lan", "minh")

# The four answers. They are the three target classes plus an escape hatch, rather than a
# yes/no on the mapping, because "this is not extrinsic" is not one answer but two very
# different ones: the claim may be faithful to the context, or it may contradict it. Only the
# first of those means the NEI label was simply too weak; the second means the mapping sent the
# sample to the wrong class entirely.
CHOICES = {
    "ngoai_lai": "Phát biểu nêu thông tin mà ngữ cảnh KHÔNG hề nhắc tới",
    "noi_tai": "Mọi thông tin đều có trong ngữ cảnh, nhưng phát biểu nói SAI hoặc mâu thuẫn",
    "khong": "Phát biểu bám sát ngữ cảnh: không thêm gì mới và cũng không mâu thuẫn",
    "khong_chac": "Không quyết được",
}

# What a control sample should get if the person actually read it.
CONTROL_ANSWER = {"Supports": "khong", "Refutes": "noi_tai"}

SHEET_COLUMNS = ("stt", "sample_id", "ngu_canh", "phat_bieu", "nhan_dinh", "ghi_chu")


def sheet_path(results_dir: Path, who: str) -> Path:
    return results_dir / f"{AUDIT_NAME}_{who}.csv"


# -- pure logic, tested in tests/test_nei_audit.py ---------------------------------------


def draw_sample(frame: pd.DataFrame) -> pd.DataFrame:
    """The 100 NEI samples plus the controls, shuffled together.

    Everything is drawn with the fixed seed and nothing depends on row order in the source, so
    running this on another machine produces the same sheet.
    """
    # Sorting by sample_id first is what makes the seed enough. pandas draws by position, so
    # without a fixed order the sample would follow whatever order the Parquet files happened
    # to be written in, and regenerating data/interim would silently change which 100 samples
    # the audit covers.
    ordered = frame.sort_values("sample_id", kind="stable")

    nei = ordered[ordered["label_original"] == "Not_Enough_Information"]
    if len(nei) < N_SAMPLES:
        raise ValueError(f"chỉ có {len(nei)} mẫu NEI, cần ít nhất {N_SAMPLES}")
    drawn = [nei.sample(n=N_SAMPLES, random_state=SEED).assign(vai_tro="nei")]

    for original in sorted(CONTROL_ANSWER):
        pool = ordered[ordered["label_original"] == original]
        if len(pool) < N_CONTROLS_PER_LABEL:
            raise ValueError(f"chỉ có {len(pool)} mẫu {original}, cần {N_CONTROLS_PER_LABEL}")
        drawn.append(
            pool.sample(n=N_CONTROLS_PER_LABEL, random_state=SEED).assign(vai_tro="doi_chung")
        )

    pooled = pd.concat(drawn, ignore_index=True).sort_values("sample_id", kind="stable")
    # Shuffling is the point of the controls: a sheet with the controls at the end would be
    # spotted immediately and read more carefully than the rest.
    return pooled.sample(frac=1.0, random_state=SEED).reset_index(drop=True)


def build_sheet(drawn: pd.DataFrame) -> pd.DataFrame:
    """The annotation sheet: what the person sees, and nothing else.

    The true label is deliberately absent — it is recovered at report time by looking the
    ``sample_id`` back up, so there is no answer key lying beside the questions.
    """
    return pd.DataFrame(
        {
            "stt": range(1, len(drawn) + 1),
            "sample_id": drawn["sample_id"].to_numpy(),
            "ngu_canh": drawn["context"].to_numpy(),
            "phat_bieu": drawn["response"].to_numpy(),
            "nhan_dinh": "",
            "ghi_chu": "",
        }
    )


def normalise_answer(value) -> str:
    """Tidy one filled-in cell. Blank stays blank so it can be counted as unfinished.

    Invisible characters have to go first. Copying a code out of a rendered document brings a
    zero-width space along often enough that it happened on the very first sheet: 34 answers
    arrived as ``"​ngoai_lai"``. ``str.strip()`` does not touch it, because Python strips
    whitespace and a zero-width space is a *format* character, not whitespace. Left alone every
    one of those answers would be rejected as an invalid code at report time, after the work was
    already done.
    """
    text = "".join(
        " " if char in "   " else char
        for char in str(value)
        if unicodedata.category(char) != "Cf"
    )
    text = text.strip().lower().replace(" ", "_").replace("-", "_")
    return text if text in CHOICES else ("" if text in ("", "nan", "none") else text)


def agreement(first: pd.Series, second: pd.Series) -> dict:
    """Raw agreement and Cohen's kappa between the two people.

    Raw agreement alone flatters this task: with one dominant answer two people who never read
    anything would still agree most of the time. Kappa measures how much of the agreement is
    beyond what their individual answer frequencies would produce by chance, which is the part
    that means something.
    """
    from sklearn.metrics import cohen_kappa_score

    raw = float((first == second).mean())
    labels = sorted(set(first) | set(second))
    kappa = float("nan") if len(labels) < 2 else float(cohen_kappa_score(first, second))
    return {"raw": raw, "kappa": kappa, "n": int(len(first))}


def describe_kappa(kappa: float) -> str:
    """Landis and Koch's bands, so the number is not reported bare in the thesis."""
    if kappa != kappa:
        return "không tính được (hai người dùng chung đúng một đáp án)"
    for threshold, wording in (
        (0.0, "tệ hơn ngẫu nhiên"),
        (0.20, "rất thấp"),
        (0.40, "thấp"),
        (0.60, "trung bình"),
        (0.80, "cao"),
    ):
        if kappa < threshold or (threshold == 0.0 and kappa < 0):
            return wording
    return "rất cao"


# -- prepare ------------------------------------------------------------------------------


def read_viwikifc(interim_dir: Path) -> pd.DataFrame:
    parts = []
    for split in ("train", "dev", "test"):
        path = interim_dir / f"viwikifc_{split}.parquet"
        if not path.is_file():
            raise FileNotFoundError(
                f"không thấy {path}. Chạy trước: python scripts/normalize_data.py "
                f"--dataset viwikifc"
            )
        parts.append(pd.read_parquet(path))
    return pd.concat(parts, ignore_index=True)


def write_guide(results_dir: Path, n_rows: int) -> Path:
    """The instructions. Written to a file rather than said once, because the two people work
    apart and the thesis has to quote the exact wording they were given."""
    path = results_dir / f"{AUDIT_NAME}_HUONGDAN.md"
    choices = "\n".join(f"| `{code}` | {text} |" for code, text in CHOICES.items())
    path.write_text(
        f"""# T13 — Hướng dẫn gán nhãn kiểm chứng ánh xạ NEI

## Việc cần làm

Mỗi người mở **đúng file của mình** trong `results/`:

- Lân: `{AUDIT_NAME}_lan.csv`
- Minh: `{AUDIT_NAME}_minh.csv`

Mỗi file có **{n_rows} dòng**. Điền cột `nhan_dinh` cho từng dòng. Cột `ghi_chu` không bắt
buộc, nhưng dòng nào thấy khó thì ghi lại một câu — phần đó vào mục thảo luận của báo cáo.

**Làm độc lập.** Không trao đổi, không xem file của nhau cho tới khi cả hai điền xong. Nếu
bàn nhau trong lúc làm thì hệ số đồng thuận đo được sẽ vô nghĩa.

## Câu hỏi phải trả lời

Đọc **ngữ cảnh**, rồi đọc **phát biểu**. Câu hỏi duy nhất:

> Phát biểu này có nêu thông tin nào **không có trong ngữ cảnh** không?

Điền một trong bốn mã sau vào cột `nhan_dinh`:

| Mã | Nghĩa |
|---|---|
{choices}

## Phân biệt bốn đáp án

Chỗ dễ nhầm nhất là giữa `ngoai_lai` và `noi_tai`. Cách phân biệt: hỏi xem **thông tin trong
phát biểu lấy từ đâu**.

- Nếu phát biểu nhắc tới một sự vật, con số, sự kiện mà **ngữ cảnh chưa từng nói đến** → thông
  tin đó đến từ bên ngoài → `ngoai_lai`.
- Nếu **mọi thứ trong phát biểu đều xuất hiện trong ngữ cảnh**, chỉ là bị nói ngược, bị gán
  sai cho nhau, hoặc sai con số → thông tin không đến từ bên ngoài, chỉ bị dùng sai →
  `noi_tai`.
- Nếu phát biểu chỉ diễn đạt lại điều ngữ cảnh đã nói, không thêm và không sai → `khong`.

Ví dụ. Ngữ cảnh:

> Hà Nội là thủ đô của Việt Nam. Thành phố Hồ Chí Minh là thành phố đông dân nhất cả nước.

| Phát biểu | Đáp án | Vì sao |
|---|---|---|
| Hà Nội là thủ đô của Việt Nam. | `khong` | Đúng như ngữ cảnh nói |
| TP.HCM là thủ đô của Việt Nam. | `noi_tai` | Hai vế đều có, chỉ bị **ghép sai** |
| Hà Nội có 8 triệu dân. | `ngoai_lai` | Ngữ cảnh không hề nói gì về **dân số** |

Nói gọn: `noi_tai` là **xáo trộn thứ đã có**, `ngoai_lai` là **mang thứ chưa có vào**.

## Phép thử khi phân vân

Ba gạch đầu dòng trên đủ cho phần lớn dòng. Gặp ca khó thì dùng phép thử này, sắc hơn:

> **Chỉ với ngữ cảnh này thôi, tôi có BÁC BỎ được phát biểu không?**

| Trả lời | Nghĩa | Mã |
|---|---|---|
| Bác bỏ được | Ngữ cảnh nói về đúng chuyện đó, và nói khác đi | `noi_tai` |
| Không bác bỏ được, cũng không xác nhận được | Ngữ cảnh im lặng về chuyện đó | `ngoai_lai` |
| Xác nhận được | Ngữ cảnh nói đúng như vậy | `khong` |

## Số liệu sai thì tính là gì?

Câu hỏi hay gặp nhất. Trả lời ngắn: **`noi_tai`**, nếu ngữ cảnh có nói về con số đó.

Chỗ dễ nhầm: một con số sai thì bản thân **giá trị mới** không xuất hiện trong ngữ cảnh, nghe
như "mang thứ chưa có vào". Nhưng phép thử **không phải** là "con số đó có trong ngữ cảnh
không" — mà là **ngữ cảnh có nói về thuộc tính đó của thực thể đó không**. Nếu có, thì mọi sai
lệch về nó là **mâu thuẫn**, không phải thông tin mới.

Ví dụ. Ngữ cảnh: *"Khoảng 65% bệnh nhân genotype 4 đáp ứng lâu dài với 48 tuần điều trị."*

| Phát biểu | Đáp án | Vì sao |
|---|---|---|
| 65% bệnh nhân genotype 4 đáp ứng với **72 tuần**. | `noi_tai` | Ngữ cảnh nói 48, bác bỏ được |
| **30%** bệnh nhân genotype 4 đáp ứng với 48 tuần. | `noi_tai` | Ngữ cảnh nói 65%, bác bỏ được |
| 65% bệnh nhân **genotype 5** đáp ứng với 48 tuần. | `ngoai_lai` | Không nói gì về genotype 5 |
| Genotype 4 tốn **12 triệu đồng** mỗi đợt. | `ngoai_lai` | Không nói gì về chi phí |

**Diễn đạt lỏng thì khác với nói sai.** "48 tuần" viết lại thành *"gần 50 tuần"* là **diễn đạt
lại** — 48 đúng là gần 50 — nên `khong`, không phải `noi_tai`. Chỉ tính là `noi_tai` khi giá
trị mới **loại trừ** giá trị trong ngữ cảnh: "72 tuần" thì không cách nào là 48.

Ranh giới này có chỗ mờ, nhất là khi phát biểu **đổi cả cách nói** chứ không chỉ đổi số — ví dụ
*"đáp ứng lâu dài"* thành *"thích nghi"*, hai khái niệm không hẳn trùng nhau. Gặp ca mờ thì
`khong_chac` kèm một dòng `ghi_chu` là câu trả lời trung thực nhất. **Chính những dòng đó là
phần đáng bàn nhất trong báo cáo** — chúng cho thấy ranh giới giữa ba lớp nhãn mờ tới đâu.

**Lưu ý quan trọng:** đừng đánh giá phát biểu **đúng hay sai ngoài đời**. Chỉ so với ngữ cảnh
được cho. Một phát biểu hoàn toàn đúng sự thật nhưng ngữ cảnh không nhắc tới thì vẫn là
`ngoai_lai`.

Không quyết được thì `khong_chac`. **Đừng đoán bừa** — một dòng `khong_chac` trung thực có ích
hơn nhiều so với một dòng đoán.

## Sau khi cả hai điền xong

Lưu file, giữ nguyên tên, giữ nguyên định dạng CSV (Excel: *Save As* → *CSV UTF-8*). Rồi chạy:

```
python scripts/audit_nei_mapping.py --report
```

Lệnh này sinh `results/{AUDIT_NAME}.csv` và in ra tỷ lệ khớp cùng hệ số đồng thuận Cohen kappa.

## Một điều chưa nói cho tới khi làm xong

Trong {n_rows} dòng có một số dòng **không phải** nhãn NEI. Đó là chủ ý: chúng dùng để kiểm tra
việc gán nhãn có thực sự được đọc kỹ hay không, và bước `--report` sẽ tách chúng ra khỏi thống
kê chính. Không cần tìm xem dòng nào là dòng nào — cứ đọc và gán như mọi dòng khác.
""",
        encoding="utf-8",
    )
    return path


def prepare(interim_dir: Path, results_dir: Path, force: bool) -> int:
    frame = read_viwikifc(interim_dir)
    drawn = draw_sample(frame)
    sheet = build_sheet(drawn)

    results_dir.mkdir(parents=True, exist_ok=True)
    for who in ANNOTATORS:
        path = sheet_path(results_dir, who)
        # Regenerating over a half-filled sheet would destroy someone's afternoon.
        if path.is_file() and not force:
            print(f"  {path} đã tồn tại, bỏ qua. Dùng --force nếu thật sự muốn ghi đè.")
            continue
        sheet.to_csv(path, index=False, encoding=CSV_ENCODING)
        print(f"  đã ghi {path}")

    guide = write_guide(results_dir, len(sheet))
    print(f"  đã ghi {guide}")

    counts = drawn["vai_tro"].value_counts().to_dict()
    print()
    print(f"  tổng số dòng          : {len(sheet)}")
    print(f"  mẫu NEI (kết quả T13) : {counts.get('nei', 0)}")
    print(f"  mẫu đối chứng         : {counts.get('doi_chung', 0)}")
    print(f"  seed                  : {SEED}")
    print()
    print("  Hai người điền file của mình, ĐỘC LẬP, rồi chạy:")
    print("      python scripts/audit_nei_mapping.py --report")
    return 0


# -- report -------------------------------------------------------------------------------


def report(interim_dir: Path, results_dir: Path) -> int:
    frame = read_viwikifc(interim_dir)
    truth = draw_sample(frame).set_index("sample_id")

    filled = {}
    for who in ANNOTATORS:
        path = sheet_path(results_dir, who)
        if not path.is_file():
            print(f"  không thấy {path}. Chạy --prepare trước.")
            return 1
        sheet = pd.read_csv(path, dtype=str, keep_default_na=False, encoding=CSV_ENCODING)
        # Excel is good at losing a column or renaming one on save, and the failure would
        # otherwise surface as a confusing KeyError several lines later.
        missing = [column for column in SHEET_COLUMNS if column not in sheet.columns]
        if missing:
            print(f"  {path} thiếu cột: {', '.join(missing)}. Lưu lại đúng định dạng "
                  f"CSV UTF-8 rồi chạy lại.")
            return 1
        sheet["nhan_dinh"] = sheet["nhan_dinh"].map(normalise_answer)
        filled[who] = sheet.set_index("sample_id")

    merged = pd.DataFrame(index=truth.index)
    merged["vai_tro"] = truth["vai_tro"]
    merged["label_original"] = truth["label_original"]
    merged["ngu_canh"] = truth["context"]
    merged["phat_bieu"] = truth["response"]
    for who in ANNOTATORS:
        merged[f"nhan_dinh_{who}"] = filled[who]["nhan_dinh"]
        merged[f"ghi_chu_{who}"] = filled[who]["ghi_chu"]

    print()
    print("=" * 80)
    print("T13 — KIỂM CHỨNG ÁNH XẠ NEI SANG NGOẠI LAI")
    print("=" * 80)

    blanks = {who: int((merged[f"nhan_dinh_{who}"] == "").sum()) for who in ANNOTATORS}
    unknown = {
        who: sorted(set(merged[f"nhan_dinh_{who}"]) - set(CHOICES) - {""})
        for who in ANNOTATORS
    }
    for who in ANNOTATORS:
        if blanks[who]:
            print(f"  {who}: còn {blanks[who]} dòng chưa điền.")
        if unknown[who]:
            print(f"  {who}: có mã không hợp lệ {unknown[who]}. Bốn mã hợp lệ: "
                  f"{', '.join(CHOICES)}")
    if any(blanks.values()) or any(unknown.values()):
        print("\n  Chưa đủ dữ liệu để tính. Điền nốt rồi chạy lại.")
        return 1

    # -- controls, before anything else. If these are wrong, nothing below is worth reading.
    controls = merged[merged["vai_tro"] == "doi_chung"]
    print()
    print("-" * 80)
    print(f"ĐỐI CHỨNG — {len(controls)} dòng không phải NEI, trộn lẫn vào")
    print("-" * 80)
    control_ok = {}
    for who in ANNOTATORS:
        wanted = controls["label_original"].map(CONTROL_ANSWER)
        hit = int((controls[f"nhan_dinh_{who}"] == wanted).sum())
        control_ok[who] = hit / len(controls)
        print(f"  {who:<6}: đúng {hit}/{len(controls)}  ({hit / len(controls) * 100:.0f} %)")
    if min(control_ok.values()) < 0.7:
        print()
        print("  CẢNH BÁO: có người dưới 70 % trên mẫu đối chứng. Những dòng NEI của người đó")
        print("  cũng đáng ngờ theo — cân nhắc gán lại trước khi đưa số vào báo cáo.")

    # -- the actual question
    audit = merged[merged["vai_tro"] == "nei"].copy()
    audit["khop"] = audit[f"nhan_dinh_{ANNOTATORS[0]}"] == audit[f"nhan_dinh_{ANNOTATORS[1]}"]

    print()
    print("-" * 80)
    print(f"ÁNH XẠ NEI -> NGOẠI LAI — {len(audit)} mẫu NEI")
    print("-" * 80)
    for who in ANNOTATORS:
        counts = audit[f"nhan_dinh_{who}"].value_counts()
        supports = int(counts.get("ngoai_lai", 0))
        print(f"  {who:<6}: {supports}/{len(audit)} cho là ngoại lai "
              f"({supports / len(audit) * 100:.0f} %)")
        for code in CHOICES:
            print(f"           {code:<12} {int(counts.get(code, 0)):>4}")

    both = audit[audit["khop"]]
    both_extrinsic = int((both[f"nhan_dinh_{ANNOTATORS[0]}"] == "ngoai_lai").sum())
    print()
    print(f"  Hai người cùng cho là ngoại lai: {both_extrinsic}/{len(audit)} "
          f"({both_extrinsic / len(audit) * 100:.0f} %)")
    print("  Đây là con số bảo thủ nhất, nên dùng nó khi viết báo cáo.")

    stats = agreement(audit[f"nhan_dinh_{ANNOTATORS[0]}"], audit[f"nhan_dinh_{ANNOTATORS[1]}"])
    print()
    print(f"  Tỷ lệ khớp thô        : {stats['raw'] * 100:.1f} %")
    print(f"  Cohen kappa           : {stats['kappa']:.3f}  ({describe_kappa(stats['kappa'])})")

    print()
    print("  Bảng chéo (hàng = Lân, cột = Minh):")
    crosstab = pd.crosstab(
        audit[f"nhan_dinh_{ANNOTATORS[0]}"], audit[f"nhan_dinh_{ANNOTATORS[1]}"]
    ).reindex(index=list(CHOICES), columns=list(CHOICES), fill_value=0)
    for line in crosstab.to_string().splitlines():
        print(f"      {line}")

    out = results_dir / f"{AUDIT_NAME}.csv"
    audit.reset_index().to_csv(out, index=False, encoding=CSV_ENCODING)
    print()
    print(f"  Đã ghi {out}  ({len(audit)} dòng)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="T13: kiểm chứng ánh xạ NEI sang ngoại lai.")
    parser.add_argument("--prepare", action="store_true", help="sinh phiếu gán nhãn")
    parser.add_argument("--report", action="store_true", help="tổng hợp phiếu đã điền")
    parser.add_argument("--force", action="store_true", help="ghi đè phiếu đã có")
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if bool(args.prepare) == bool(args.report):
        parser.error("chọn đúng một trong hai: --prepare hoặc --report")

    if args.prepare:
        print()
        print("=" * 80)
        print("T13 — SINH PHIẾU GÁN NHÃN")
        print("=" * 80)
        return prepare(args.interim_dir, args.results_dir, args.force)
    return report(args.interim_dir, args.results_dir)


if __name__ == "__main__":
    raise SystemExit(main())
