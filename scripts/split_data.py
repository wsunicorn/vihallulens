"""Task T14: split the two corpora that need it, and report the leakage in all four.

ViHallu and ISE-DSC01 ship only a training set, so section 5 of docs/DATA.md splits them
80/10/10 by ``context_id`` with seed 42. ViWikiFC and ViFactCheck keep their original split so
their numbers stay comparable with published ones — which means keeping their leakage too, and
that is exactly why it has to be measured and written down.

Running this twice is safe: the split files are read back and recombined before splitting, and
the split is deterministic, so the second run reproduces the first.

Usage:
    python scripts/split_data.py
    python scripts/split_data.py --report-only
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.loading import (  # noqa: E402
    DEFAULT_INTERIM_DIR,
    dataset_path,
    load_all_splits,
)
from vihallulens.data.schema import context_id  # noqa: E402
from vihallulens.data.splits import (  # noqa: E402
    DEFAULT_RATIOS,
    SPLIT_NAMES,
    group_split,
    leakage_between,
)

DEFAULT_REPORT = Path("results/leakage_report.md")

# The two corpora with no original split. Section 5 of docs/DATA.md.
TO_SPLIT = ("vihallu", "isedsc01")
# The two that keep theirs, leakage and all, so published numbers stay comparable.
KEEP_ORIGINAL = ("viwikifc", "vifactcheck")

# The unlabelled public test files. They are never used for anything — no labels, no verdict —
# but section 6 of docs/DATA.md reports how much of their context was already in train, because
# it is the evidence that the competition splits leak and that ours had to be built differently.
PUBLIC_TEST = {
    "vihallu": ("vihallu_train.csv", "vihallu_test_public.csv"),
    "isedsc01": ("isedsc01_train.json", "isedsc01_test_public.json"),
}


def read_whole(name: str, interim_dir: Path) -> pd.DataFrame:
    """Every row of a corpus, whatever splits it is currently sitting in.

    Recombining is what makes this script idempotent. Splitting an already-split corpus would
    otherwise carve 80 % out of the 80 %, quietly shrinking the training set on every run.
    """
    parts = load_all_splits(name, interim_dir)
    frame = pd.concat(parts.values(), ignore_index=True)
    if frame["sample_id"].duplicated().any():
        count = int(frame["sample_id"].duplicated().sum())
        raise ValueError(
            f"{name}: {count} sample_id trùng khi gộp các tập lại. Có file cũ lẫn file mới "
            f"trong {interim_dir}; chạy lại python scripts/normalize_data.py --dataset {name}"
        )
    return frame


def split_one(name: str, interim_dir: Path) -> dict[str, pd.DataFrame]:
    """Group-split one corpus and write the three files back."""
    whole = read_whole(name, interim_dir)
    splits = group_split(
        whole, ratios=DEFAULT_RATIOS, seed=REQUIRED_SPLIT_SEED, group_col="context_id"
    )
    for split, part in splits.items():
        part.to_parquet(dataset_path(name, split, interim_dir), index=False)
    return splits


def raw_context_ids(raw_dir: Path, filename: str) -> set[str]:
    """Context ids straight from a raw file, used only for the public-test comparison."""
    path = raw_dir / filename
    if not path.is_file():
        return set()
    if filename.endswith(".csv"):
        texts = pd.read_csv(path, dtype=str, keep_default_na=False)["context"]
    else:
        import json

        with path.open(encoding="utf-8") as handle:
            texts = [str(record.get("context", "")) for record in json.load(handle).values()]
    return {context_id(str(text)) for text in texts}


def leakage_rows(splits: dict[str, pd.DataFrame]) -> list[dict]:
    """Leakage of every later split against everything that came before it.

    Comparing dev and test against the union of what precedes them, rather than against train
    alone, is the honest version: a context that reached test through dev is just as leaked.
    """
    rows = []
    order = [name for name in SPLIT_NAMES if name in splits]
    for index, name in enumerate(order[1:], start=1):
        earlier = pd.concat([splits[before] for before in order[:index]], ignore_index=True)
        rows.append({"split": name, "against": " + ".join(order[:index]),
                     **leakage_between(earlier, splits[name])})
    return rows


def format_report(
    measured: dict[str, dict], public: dict[str, tuple[int, int]], interim_dir: Path
) -> str:
    """The Markdown report. Written to a file because section 6 of docs/DATA.md is a claim the
    thesis makes, and a claim needs something regenerable standing behind it."""
    stamp = datetime.now(UTC).strftime("%d/%m/%Y")
    lines = [
        "# Báo cáo rò rỉ ngữ cảnh",
        "",
        f"Sinh tự động bởi `scripts/split_data.py` ngày {stamp}. Đừng sửa tay — chạy lại lệnh.",
        "",
        "## Rò rỉ là gì và vì sao phải đo",
        "",
        "Hai mẫu dùng chung một ngữ cảnh thì không độc lập với nhau: mô hình đã thấy một mẫu",
        "lúc huấn luyện thì cũng đã thấy gần hết phần vật liệu của mẫu kia. Nếu chúng nằm ở",
        "hai tập khác nhau, điểm trên tập test đo **trí nhớ** nhiều ngang đo **khả năng khái",
        "quát hóa**, và con số báo cáo sẽ đẹp hơn sự thật.",
        "",
        "Vì vậy đơn vị chia tập là `context_id` chứ không phải dòng — mục 5 `docs/DATA.md`.",
        "Bảng dưới đếm hai kiểu: theo **ngữ cảnh** cho biết bao nhiêu vật liệu bị dùng lại,",
        "theo **dòng** cho biết bao nhiêu phần điểm số thật sự dựa lên đó. Con số theo dòng",
        "thường lớn hơn và mới là con số đáng lo.",
        "",
        "## Tập do nhóm tự chia — ViHallu và ISE-DSC01",
        "",
        f"Chia 80/10/10 theo `context_id`, seed {REQUIRED_SPLIT_SEED}, bằng `group_split`.",
        "Hàm này raise nếu có bất kỳ ngữ cảnh nào lọt vào hai tập, nên **rò rỉ ở đây bằng 0",
        "theo thiết kế**; bảng dưới là bằng chứng chứ không phải kỳ vọng.",
        "",
        "| Bộ | Tập | Dòng | Tỷ lệ | Ngữ cảnh | Rò rỉ ngữ cảnh | Rò rỉ dòng |",
        "|---|---|---|---|---|---|---|",
    ]

    for name in [item for item in TO_SPLIT if item in measured]:
        info = measured[name]
        total = sum(len(part) for part in info["splits"].values())
        for split in SPLIT_NAMES:
            part = info["splits"][split]
            row = next((item for item in info["leakage"] if item["split"] == split), None)
            leak_g = "—" if row is None else f"{row['shared_groups']}/{row['n_groups']}"
            leak_r = "—" if row is None else f"{row['shared_rows']}/{row['n_rows']}"
            lines.append(
                f"| {name} | {split} | {len(part):,} | {len(part) / total * 100:.1f} % | "
                f"{part['context_id'].nunique():,} | {leak_g} | {leak_r} |"
            )

    lines += [
        "",
        "### Phân bố nhãn sau khi chia",
        "",
        "Chia theo nhóm ngữ cảnh thì **không** ép được cân bằng nhãn cùng lúc — hai ràng buộc",
        "đó xung khắc nhau. Bảng này để thấy việc chia có làm lệch nhãn hay không.",
        "",
        "| Bộ | Tập | no | intrinsic | extrinsic |",
        "|---|---|---|---|---|",
    ]
    for name in [item for item in TO_SPLIT if item in measured]:
        for split in SPLIT_NAMES:
            counts = measured[name]["splits"][split]["label"].value_counts()
            total = int(counts.sum())
            cells = " | ".join(
                f"{int(counts.get(label, 0)):,} ({counts.get(label, 0) / total * 100:.1f} %)"
                for label in ("no", "intrinsic", "extrinsic")
            )
            lines.append(f"| {name} | {split} | {cells} |")

    lines += [
        "",
        "## Tập giữ nguyên split gốc — ViWikiFC và ViFactCheck",
        "",
        "Hai bộ này **giữ split gốc** để so được với số đã công bố, nên nhóm phải nhận luôn",
        "phần rò rỉ có sẵn trong đó. Không sửa được, chỉ báo cáo được.",
        "",
        "| Bộ | Tập | Dòng | Ngữ cảnh | Rò rỉ ngữ cảnh | Rò rỉ dòng |",
        "|---|---|---|---|---|---|",
    ]
    for name in [item for item in KEEP_ORIGINAL if item in measured]:
        info = measured[name]
        for row in info["leakage"]:
            part = info["splits"][row["split"]]
            lines.append(
                f"| {name} | {row['split']} | {len(part):,} | {part['context_id'].nunique():,} | "
                f"{row['shared_groups']}/{row['n_groups']} ({row['group_rate'] * 100:.1f} %) | "
                f"{row['shared_rows']}/{row['n_rows']} ({row['row_rate'] * 100:.1f} %) |"
            )

    lines += [
        "",
        "**Hệ quả bắt buộc ghi vào báo cáo:** không dùng ViWikiFC và ViFactCheck để kết luận",
        "về khả năng khái quát hóa. Tập test của ViWikiFC dùng lại **toàn bộ** ngữ cảnh của",
        "train, nên điểm trên đó không nói gì về dữ liệu chưa từng thấy. Chúng vẫn dùng được",
        "làm đối chứng ngoài phân phối huấn luyện của ViHallu, và để so với số đã công bố.",
        "",
        "## File public test — không dùng, nhưng là lý do phải tự chia",
        "",
        "ViHallu và ISE-DSC01 có file public test nhưng **không có nhãn dùng được**, nên nhóm",
        "không dùng chúng. Vẫn đo phần rò rỉ của chúng, vì đây là bằng chứng cho thấy split do",
        "ban tổ chức phát hành cũng rò rỉ — tức việc nhóm tự chia không phải là làm khó mình.",
        "",
        "| Bộ | Ngữ cảnh test public có trong train |",
        "|---|---|",
    ]
    for name, (shared, total) in public.items():
        rate = f" ({shared / total * 100:.1f} %)" if total else ""
        lines.append(f"| {name} | {shared:,}/{total:,}{rate} |")

    lines += [
        "",
        "## Cách tái lập",
        "",
        "```",
        "python scripts/normalize_data.py --all",
        "python scripts/split_data.py",
        "```",
        "",
        f"Dữ liệu đọc từ `{Path(interim_dir).as_posix()}`. Chạy lại cho ra đúng kết quả này: nhóm",
        f"ngữ cảnh được sắp theo `context_id` trước khi xáo, nên seed {REQUIRED_SPLIT_SEED} là đủ.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="T14: chia tập và báo cáo rò rỉ.")
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--raw-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--report-only", action="store_true", help="không chia lại, chỉ đo")
    parser.add_argument(
        "--only",
        nargs="+",
        choices=[*TO_SPLIT, *KEEP_ORIGINAL],
        help="chỉ xử lý những bộ này; mặc định làm cả bốn. Dùng khi chỉ cần một bộ, "
             "ví dụ E09 chỉ cần vihallu",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from vihallulens.data.paths import find_raw_dir

    print()
    print("=" * 80)
    print("T14 — CHIA TẬP VÀ BÁO CÁO RÒ RỈ")
    print("=" * 80)

    wanted = set(args.only) if args.only else {*TO_SPLIT, *KEEP_ORIGINAL}
    to_split = [name for name in TO_SPLIT if name in wanted]
    keep_original = [name for name in KEEP_ORIGINAL if name in wanted]
    if args.only:
        print(f"  chỉ xử lý           : {', '.join(sorted(wanted))}")

    measured: dict[str, dict] = {}
    for name in to_split:
        if args.report_only:
            splits = load_all_splits(name, args.interim_dir)
        else:
            splits = split_one(name, args.interim_dir)
        measured[name] = {"splits": splits, "leakage": leakage_rows(splits)}
        total = sum(len(part) for part in splits.values())
        sizes = " / ".join(f"{len(splits[s]):,}" for s in SPLIT_NAMES if s in splits)
        shares = " / ".join(
            f"{len(splits[s]) / total * 100:.1f}%" for s in SPLIT_NAMES if s in splits
        )
        print(f"  {name:<12}: {sizes}  ({shares})  tổng {total:,}")

    for name in keep_original:
        splits = load_all_splits(name, args.interim_dir)
        measured[name] = {"splits": splits, "leakage": leakage_rows(splits)}

    print()
    print("-" * 80)
    print("RÒ RỈ NGỮ CẢNH")
    print("-" * 80)
    print(f"  {'Bộ':<12} {'Tập':<6} {'ngữ cảnh':>16} {'dòng':>18}")
    for name, info in measured.items():
        for row in info["leakage"]:
            groups = f"{row['shared_groups']}/{row['n_groups']} ({row['group_rate'] * 100:.1f}%)"
            rows_ = f"{row['shared_rows']}/{row['n_rows']} ({row['row_rate'] * 100:.1f}%)"
            print(f"  {name:<12} {row['split']:<6} {groups:>16} {rows_:>18}")

    raw_dir = find_raw_dir(args.raw_dir)
    public = {}
    for name, (train_file, test_file) in PUBLIC_TEST.items():
        if name not in measured:
            continue
        train_ids = raw_context_ids(raw_dir, train_file)
        test_ids = raw_context_ids(raw_dir, test_file)
        public[name] = (len(test_ids & train_ids), len(test_ids))

    print()
    print("  File public test (không dùng, chỉ để đối chiếu mục 6 docs/DATA.md):")
    for name, (shared, total) in public.items():
        print(f"    {name:<12} {shared:,}/{total:,}")

    # A partial run must not overwrite the report covering all four corpora: mục 6
    # docs/DATA.md points at that file by name, and half of it is worse than none of it.
    report = args.report
    if args.only:
        report = report.with_name(f"{report.stem}_{'_'.join(sorted(wanted))}{report.suffix}")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(format_report(measured, public, args.interim_dir), encoding="utf-8")
    print()
    print(f"  Đã ghi {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
