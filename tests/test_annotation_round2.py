"""Drawing, hiding and reading back the second annotation round."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import annotation_round2 as a  # noqa: E402


def corpus(n=200):
    labels = [a.NEI, "Supports", "Refutes"]
    return pd.DataFrame([{"sample_id": f"v_{label[:3]}_{i:03d}", "context": f"ngữ cảnh {i}",
                          "response": f"phát biểu {i}", "label_original": label}
                         for label in labels for i in range(n)])


def test_round2_avoids_round1_and_practice():
    used = {f"v_Not_{i:03d}" for i in range(50)}
    drawn = a.draw_round2(corpus(), used)
    ids = {name: set(frame["sample_id"]) for name, frame in drawn.items()}
    assert len(ids["main"]) == 130 and len(ids["practice_a"]) == len(ids["practice_b"]) == 16
    assert not ids["main"] & used
    assert not ids["main"] & ids["practice_a"]
    assert not ids["practice_a"] & ids["practice_b"]
    assert (drawn["main"]["label_original"] == a.NEI).sum() == 100


def test_drawing_does_not_depend_on_row_order():
    first = a.draw_round2(corpus(), set())["main"]["sample_id"].tolist()
    shuffled = corpus().sample(frac=1, random_state=9)
    assert a.draw_round2(shuffled, set())["main"]["sample_id"].tolist() == first


def test_practice_mixes_in_the_crafted_items():
    rows = a.practice_rows(a.draw_round2(corpus(), set())["practice_a"], "a")
    assert len(rows) == 20
    places = [i for i, r in enumerate(rows) if r["sample_id"].startswith("luyen_tap")]
    assert len(places) == 4 and places[0] < 10


def errors():
    return pd.DataFrame([{"sample_id": f"e{i}", "label": "no", "pred": "extrinsic", "context": "c",
                          "question": "q", "response": "r </script> x"} for i in range(40)])


def test_error_form_hides_which_label_is_gold():
    lan, minh = a.error_rows(errors(), "lan"), a.error_rows(errors(), "minh")
    first = [row["options"]["chon"][0]["value"] for row in lan]
    assert 5 < first.count("no") < 35
    assert first != [row["options"]["chon"][0]["value"] for row in minh]
    assert not {"label", "pred", "key"} & set(lan[0])


def test_rendered_form_cannot_be_broken_by_its_data():
    html = a.render({"id": "x", "rows": a.error_rows(errors(), "lan")})
    assert html.count("</script>") == 1 and "/*DATA*/null" not in html


@pytest.mark.parametrize(("q1", "q2", "code"), [
    ("khong_du", "co", "ngoai_lai"), ("khong_du", "khong", "suy_dien"),
    ("xac_nhan", "", "khong"), ("bac_bo", "", "noi_tai"), ("khong_chac", "", "khong_chac"),
    ("khong_du", "", ""), ("", "", "")])
def test_codes(q1, q2, code):
    assert a.code_of(q1, q2) == code


def test_nei_summary_counts_strict_and_broad():
    codes = pd.DataFrame({"lan": ["ngoai_lai", "suy_dien", "khong", "khong", "noi_tai"],
                          "minh": ["ngoai_lai", "ngoai_lai", "khong", "khong", "ngoai_lai"]})
    out = a.summarise_nei(codes, pd.Series([a.NEI, a.NEI, a.NEI, "Supports", "Refutes"]))
    assert out["n_nei"] == 3 and out["both_strict"] == 1 and out["both_broad"] == 2
    assert out["controls"]["lan"]["right"] == 2 and out["controls"]["minh"]["right"] == 1
    assert out["controls_both_extrinsic"] == 0


def test_error_summary_separates_label_noise_from_detector_errors():
    frame = pd.DataFrame({"label": ["no"] * 4, "pred": ["extrinsic"] * 4,
                          "chon_lan": ["no", "extrinsic", "extrinsic", "khac"],
                          "chon_minh": ["no", "extrinsic", "no", "khac"]})
    out = a.summarise_errors(frame)
    assert out["both"] == {"nhan_goc": 1, "du_doan": 1, "khac": 1, "khong_ro": 0}
    assert out["disagree"] == 1
