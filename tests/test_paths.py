"""Tests for locating the raw data directory on whichever machine the code runs."""

import pytest

from vihallulens.data import paths


def make_dataset(directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / paths.MARKER_FILE).write_text("id,context\n", encoding="utf-8")
    return directory


def test_explicit_directory_wins(tmp_path):
    wanted = make_dataset(tmp_path / "wanted")
    make_dataset(tmp_path / "other")
    assert paths.find_raw_dir(wanted) == wanted


def test_environment_variable_is_used(tmp_path, monkeypatch):
    wanted = make_dataset(tmp_path / "from_env")
    monkeypatch.setenv(paths.ENV_VAR, str(wanted))
    assert paths.find_raw_dir() == wanted


def test_local_default_is_found(tmp_path, monkeypatch):
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    make_dataset(tmp_path / "data" / "raw")
    assert paths.find_raw_dir() == paths.LOCAL_DEFAULT


@pytest.mark.parametrize("layout", ["vihallulens", "datasets/unicorn1209/vihallulens"])
def test_kaggle_mount_layouts_are_both_found(tmp_path, monkeypatch, layout):
    """Kaggle has used both mount shapes, so neither may be assumed."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "kaggle_input"
    wanted = make_dataset(root / layout)
    monkeypatch.setattr(paths, "KAGGLE_ROOT", root)

    assert paths.find_raw_dir() == wanted


def test_missing_data_raises_and_lists_what_was_tried(tmp_path, monkeypatch):
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match=paths.MARKER_FILE):
        paths.find_raw_dir()


def test_an_explicit_directory_without_the_marker_is_still_honoured(tmp_path, monkeypatch):
    """Pointing at a partial copy on purpose must work; guessing must not."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    partial = tmp_path / "partial"
    partial.mkdir()
    assert paths.find_raw_dir(partial) == partial


def test_a_wrong_explicit_directory_raises_instead_of_falling_back(tmp_path, monkeypatch):
    """Silently using another directory would run the experiment on data nobody asked for."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    make_dataset(tmp_path / "data" / "raw")
    with pytest.raises(FileNotFoundError, match="does not exist"):
        paths.find_raw_dir(tmp_path / "go-nham")
