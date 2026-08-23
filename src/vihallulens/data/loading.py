"""Reading a normalised corpus back off disk.

Signature follows section 2.1 of docs/SPEC.md. Everything downstream of task T14 goes through
here rather than touching ``data/interim`` directly, so the layout of that directory stays one
module's business.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from vihallulens.data.schema import DATASETS, SPLITS, validate

DEFAULT_INTERIM_DIR = Path("data/interim")


def dataset_path(name: str, split: str, interim_dir: Path | str = DEFAULT_INTERIM_DIR) -> Path:
    return Path(interim_dir) / f"{name}_{split}.parquet"


def load_dataset(
    name: str,
    split: str,
    interim_dir: Path | str = DEFAULT_INTERIM_DIR,
    check: bool = True,
) -> pd.DataFrame:
    """One split of one corpus, in the common schema of section 1 of docs/DATA.md.

    ``check`` re-runs the schema validation on read. It costs almost nothing next to the
    Parquet read itself and catches a file that was edited, truncated or written by an older
    version of the reader, which is otherwise the kind of thing that surfaces as a strange
    metric three steps later.
    """
    if name not in DATASETS:
        raise ValueError(f"không biết bộ dữ liệu {name!r}; chọn một trong {list(DATASETS)}")
    if split not in SPLITS:
        raise ValueError(f"không biết tập {split!r}; chọn một trong {list(SPLITS)}")

    path = dataset_path(name, split, interim_dir)
    if not path.is_file():
        raise FileNotFoundError(
            f"không thấy {path}. Chạy trước:\n"
            f"    python scripts/normalize_data.py --dataset {name}\n"
            f"    python scripts/split_data.py"
        )

    frame = pd.read_parquet(path)
    if check:
        validate(frame)
        wrong = sorted(set(frame["split"]) - {split})
        if wrong:
            raise ValueError(f"{path} chứa dòng của tập {wrong}, không phải {split!r}")
    return frame


def load_all_splits(
    name: str, interim_dir: Path | str = DEFAULT_INTERIM_DIR, check: bool = True
) -> dict[str, pd.DataFrame]:
    """Every split of one corpus that exists on disk, keyed by split name.

    Missing splits are skipped rather than raising: ViHallu and ISE-DSC01 have only a train
    file until task T14 has run over them, and callers that merely want "all the data" should
    not have to know that.
    """
    found = {}
    for split in SPLITS:
        path = dataset_path(name, split, interim_dir)
        if path.is_file():
            found[split] = load_dataset(name, split, interim_dir, check=check)
    if not found:
        raise FileNotFoundError(
            f"không thấy file nào cho bộ {name} trong {interim_dir}. Chạy trước: "
            f"python scripts/normalize_data.py --dataset {name}"
        )
    return found
