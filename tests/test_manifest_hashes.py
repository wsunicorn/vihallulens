"""The raw data on this machine is byte-for-byte the data the experiments used.

data/raw/ is not in Git, so the hashes in section 5 of data/raw/MANIFEST.md are the only record
of which files every reported number came from. Files not downloaded yet are skipped.
"""

import hashlib
import re
from pathlib import Path

import pytest

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
ROW = re.compile(r"^\| `([^`]+)` \| [\d.]+ \| `([0-9a-f]{64})` \|$")


def manifest_hashes() -> dict[str, str]:
    text = (RAW / "MANIFEST.md").read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in map(ROW.match, text.splitlines()) if m}


def test_manifest_lists_every_dataset_file():
    names = manifest_hashes()
    assert len(names) == 13
    for used in ("vihallu_train.csv", "isedsc01_train.json", "viwikifc_train.csv"):
        assert used in names


@pytest.mark.parametrize("name", sorted(manifest_hashes()))
def test_raw_file_matches_manifest(name):
    path = RAW / name
    if not path.exists():
        pytest.skip(f"{name} chưa tải về")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest_hashes()[name]
