"""Reading a normalised corpus back, per section 2.1 of docs/SPEC.md."""

import pandas as pd
import pytest

from vihallulens.data.loading import dataset_path, load_all_splits, load_dataset


def frame(split: str = "train", n: int = 2) -> pd.DataFrame:
    from vihallulens.data.schema import context_id, finalise

    records = [
        {
            "sample_id": f"vihallu_{split}_{index}",
            "dataset": "vihallu",
            "split": split,
            "context": f"Ngữ cảnh {index}.",
            "context_id": context_id(f"Ngữ cảnh {index}."),
            "question": "Câu hỏi?",
            "response": "Phản hồi.",
            "label": "no",
            "label_original": "no",
            "evidence": "",
            "evidence_start": -1,
            "evidence_end": -1,
            "response_is_generated": True,
            "meta": "{}",
        }
        for index in range(n)
    ]
    return finalise(pd.DataFrame.from_records(records))


def write(tmp_path, split: str = "train", **kwargs):
    frame(split, **kwargs).to_parquet(dataset_path("vihallu", split, tmp_path), index=False)
    return tmp_path


def test_a_written_split_reads_back(tmp_path):
    write(tmp_path)
    assert len(load_dataset("vihallu", "train", tmp_path)) == 2


def test_an_unknown_corpus_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="không biết bộ dữ liệu"):
        load_dataset("khong_ton_tai", "train", tmp_path)


def test_an_unknown_split_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="không biết tập"):
        load_dataset("vihallu", "validation", tmp_path)


def test_a_missing_file_says_which_command_to_run(tmp_path):
    with pytest.raises(FileNotFoundError, match="normalize_data.py"):
        load_dataset("vihallu", "train", tmp_path)


def test_a_file_holding_the_wrong_split_is_rejected(tmp_path):
    """Catches a file copied or renamed by hand, which would otherwise train on test data
    without anything looking wrong."""
    frame("dev").to_parquet(dataset_path("vihallu", "train", tmp_path), index=False)
    with pytest.raises(ValueError, match="không phải 'train'"):
        load_dataset("vihallu", "train", tmp_path)


def test_a_frame_breaking_the_schema_is_rejected_on_read(tmp_path):
    """Validation on read costs almost nothing beside the Parquet read, and catches a file
    written by an older version of the reader before it becomes a strange metric."""
    broken = frame().drop(columns=["label"])
    broken.to_parquet(dataset_path("vihallu", "train", tmp_path), index=False)
    with pytest.raises(ValueError, match="thiếu cột"):
        load_dataset("vihallu", "train", tmp_path)


def test_validation_can_be_switched_off(tmp_path):
    broken = frame().drop(columns=["label"])
    broken.to_parquet(dataset_path("vihallu", "train", tmp_path), index=False)
    assert len(load_dataset("vihallu", "train", tmp_path, check=False)) == 2


# -- all splits at once ------------------------------------------------------------------


def test_only_the_splits_that_exist_come_back(tmp_path):
    """ViHallu and ISE-DSC01 have a train file and nothing else until task T14 has run, and a
    caller that just wants all the data should not have to know that."""
    write(tmp_path, "train")
    assert sorted(load_all_splits("vihallu", tmp_path)) == ["train"]


def test_three_splits_come_back_when_all_three_exist(tmp_path):
    for split in ("train", "dev", "test"):
        write(tmp_path, split)
    assert sorted(load_all_splits("vihallu", tmp_path)) == ["dev", "test", "train"]


def test_a_corpus_with_no_files_at_all_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="không thấy file nào"):
        load_all_splits("vihallu", tmp_path)
