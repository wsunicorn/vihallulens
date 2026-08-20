"""Normalise one raw corpus into the common schema and write it to ``data/interim/``.

Usage:
    python scripts/normalize_data.py --dataset vihallu
    python scripts/normalize_data.py --dataset vihallu --data-dir /kaggle/input/...

Output goes to ``data/interim/{dataset}_{split}.parquet``, one file per split, following
section 1 of docs/DATA.md. The directory is gitignored: the files are reproducible from
``data/raw`` by running this script, so there is no reason to carry them in the repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.data.paths import find_raw_dir  # noqa: E402

DEFAULT_OUTPUT_DIR = Path("data/interim")

# Which task implements which corpus. Naming the task in the error keeps the sequence of
# TASKS.md visible from the command line instead of only in the file.
PENDING = {
    "isedsc01": "T10",
    "viwikifc": "T11",
    "vifactcheck": "T12",
}


def normalize(name: str, raw_dir: Path):
    """Dispatch to the reader for one corpus."""
    if name == "vihallu":
        from vihallulens.data.vihallu import normalize_vihallu

        return normalize_vihallu(raw_dir)
    if name in PENDING:
        raise NotImplementedError(
            f"bộ {name} chưa chuẩn hóa được: đó là task {PENDING[name]} trong TASKS.md"
        )
    raise ValueError(f"không biết bộ dữ liệu {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Chuẩn hóa dữ liệu thô về schema chung.")
    parser.add_argument("--dataset", required=True, choices=["vihallu", *PENDING])
    parser.add_argument("--data-dir", type=Path, default=None, help="thư mục data/raw")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    raw_dir = find_raw_dir(args.data_dir)
    print()
    print("=" * 80)
    print(f"CHUẨN HÓA {args.dataset.upper()}")
    print("=" * 80)
    print(f"  nguồn                 : {raw_dir}")

    try:
        frame = normalize(args.dataset, raw_dir)
    except NotImplementedError as error:
        print(f"  {error}")
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for split, part in frame.groupby("split", sort=True):
        path = args.out_dir / f"{args.dataset}_{split}.parquet"
        part.reset_index(drop=True).to_parquet(path, index=False)
        written.append((path, len(part)))

    print(f"  số dòng               : {len(frame):,}")
    print(f"  ngữ cảnh duy nhất     : {frame['context_id'].nunique():,}")
    print()
    print("  phân bố nhãn:")
    for label, count in frame["label"].value_counts().sort_index().items():
        print(f"      {label:<12} {count:>7,}  ({count / len(frame) * 100:5.1f} %)")

    located = int((frame["evidence_start"] >= 0).sum())
    print(f"  có bằng chứng nguyên văn : {located:,}/{len(frame):,}")

    # meta carries whatever is specific to one corpus. Reporting the small categorical fields
    # here means a rule that silently stops firing — such as the noisy-prompt rule of section 7
    # of docs/DATA.md — shows up as a changed count instead of going unnoticed.
    meta = frame["meta"].map(json.loads)
    for key in sorted({name for payload in meta for name in payload}):
        values = meta.map(lambda payload, key=key: payload[key])
        if values.nunique() > 8 or values.map(type).eq(bool).all():
            continue
        print()
        print(f"  phân bố meta.{key}:")
        for value, count in values.value_counts().sort_index().items():
            print(f"      {str(value):<12} {count:>7,}  ({count / len(frame) * 100:5.1f} %)")

    print()
    print("  đã ghi:")
    for path, count in written:
        print(f"      {path}  ({count:,} dòng)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
