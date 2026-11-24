# ruff: noqa: E501 - the guides and practice items are prose shown to the annotators verbatim
"""Two annotation jobs for two people working apart: T13B and T34B.

**T13B, NEI round 2.** Round 1 (T13) asked four codes at once and had two flaws found on
24/11/2026. It had no code for the very case it set out to count — a claim that the context
neither settles nor supplements, NEI without any outside fact — and the test added to its guide
("neither refuted nor confirmed means extrinsic") is the definition of NEI, so it assumed the
answer. Round 2 asks two separate questions instead, gives both people a practice set with
answers first, and draws 100 new NEI samples and 30 new controls that round 1 did not use.

**T34B, the 100 wrong predictions.** Each row shows the response with the gold label and the
predicted label as two unnamed candidates in an order that differs per person, so neither can
favour "the label" over "the model".

Forms are single HTML files built from ``annotation_form.html``: open in Chrome, answer with
buttons or number keys, export a CSV into ``results/``.

Predictions, written before anyone annotates:
* T13B: five-code kappa above round 1's 0,505; between 50 and 75 of 100 NEI samples agreed as
  extrinsic in the strict sense (an outside fact); each person right on at least 85 % of controls;
* T34B: between 10 and 30 of 100 samples where both people prefer the predicted label.

Usage:
    python scripts/annotation_round2.py prepare          # writes data/annotation/*.html
    python scripts/annotation_round2.py practice results/1_luyen_tap_a_lan.csv --set a
    python scripts/annotation_round2.py report
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_nei_mapping import (  # noqa: E402
    CSV_ENCODING,
    SEED,
    agreement,
    describe_kappa,
    read_viwikifc,
)

ANNOTATORS = ("lan", "minh")
N_NEI, N_CONTROLS, N_PRACTICE = 100, 15, 8
PASS_MARK = 0.8
NEI = "Not_Enough_Information"
KEY_OF = {"Supports": "xac_nhan", "Refutes": "bac_bo"}
TEMPLATE = Path(__file__).with_name("annotation_form.html")
FORM_DIR, RESULTS = Path("data/annotation"), Path("results")

NEI_QUESTIONS = [
    {"key": "q1", "text": "1. Chỉ với ngữ cảnh này, phát biểu có kết luận được không?", "options": [
        {"value": "xac_nhan", "label": "Xác nhận được",
         "hint": "Ngữ cảnh nói đúng như vậy, hoặc suy ra hiển nhiên từ ngữ cảnh"},
        {"value": "bac_bo", "label": "Bác bỏ được",
         "hint": "Theo ngữ cảnh thì phát biểu chắc chắn sai"},
        {"value": "khong_du", "label": "Không đủ để kết luận",
         "hint": "Ngữ cảnh không cho biết phát biểu đúng hay sai"},
        {"value": "khong_chac", "label": "Tôi không quyết được"}]},
    {"key": "q2", "when": {"key": "q1", "value": "khong_du"},
     "text": "2. Phát biểu có nêu dữ kiện mà ngữ cảnh không nhắc tới không?", "options": [
         {"value": "co", "label": "Có dữ kiện ngoài ngữ cảnh",
          "hint": "Sự vật, sự kiện, con số, thời gian, đặc điểm mới"},
         {"value": "khong", "label": "Không, chỉ là suy diễn",
          "hint": "Mọi dữ kiện đều có trong ngữ cảnh; phần chưa rõ là quan hệ, nguyên nhân, "
                  "mức độ hay khái quát"}]},
]

NEI_GUIDE = """
<p>Chỉ dùng <b>ngữ cảnh</b>. Không dùng hiểu biết bên ngoài: một điều đúng ngoài đời nhưng ngữ cảnh
không nói thì vẫn là “không đủ để kết luận”.</p>
<p><b>Câu 1.</b> Trả lời theo thứ tự sau:</p>
<ol>
<li>Có phần nào của phát biểu <b>trái với ngữ cảnh</b>? → <b>Bác bỏ được</b> (kể cả khi các phần khác đúng
hoặc chưa rõ). Con số sai là bác bỏ nếu ngữ cảnh có nói về đúng con số đó và hai con số loại trừ nhau.</li>
<li>Mọi phần đều được ngữ cảnh nói tới và đúng? → <b>Xác nhận được</b>. Diễn đạt lại, rút gọn, hoặc viết gần
đúng (“48 tuần” thành “gần 50 tuần”) vẫn là xác nhận.</li>
<li>Còn lại → <b>Không đủ để kết luận</b>.</li>
</ol>
<p><b>Câu 2</b> chỉ hỏi khi không đủ. Nhìn vào <b>phần chưa kết luận được</b>: nó đưa vào một <b>dữ kiện</b> mới, hay
chỉ nối các dữ kiện đã có theo một cách ngữ cảnh không nói?</p>
<table>
<tr><th>Ngữ cảnh</th><th>Phát biểu</th><th>Câu 1</th><th>Câu 2</th></tr>
<tr><td rowspan="5">Hà Nội là thủ đô của Việt Nam. Năm 2019, Hà Nội đón 29 triệu lượt khách; Hồ Gươm nằm ở trung
tâm thành phố.</td><td>Thủ đô của Việt Nam là Hà Nội.</td><td>Xác nhận</td><td></td></tr>
<tr><td>Năm 2019, Hà Nội đón 15 triệu lượt khách.</td><td>Bác bỏ</td><td></td></tr>
<tr><td>Hà Nội là thủ đô và có 12 quận.</td><td>Không đủ</td><td>Có dữ kiện mới (12 quận)</td></tr>
<tr><td>Phần lớn khách đến Hà Nội năm 2019 để thăm Hồ Gươm.</td><td>Không đủ</td><td>Không, chỉ là suy
diễn (khách, Hồ Gươm đều có; quan hệ thì không)</td></tr>
<tr><td>Hồ Gươm nằm ở trung tâm Hải Phòng.</td><td>Bác bỏ</td><td></td></tr>
</table>
<p>Làm một mình, không trao đổi. Phân vân thì ghi một dòng ghi chú; chỉ chọn “không quyết được” khi thật sự
không chọn được.</p>
"""

# Practice items for the second question, which the corpus has no key for.
CRAFTED = {
    "a": [
        ("Chợ Bến Thành nằm ở trung tâm Thành phố Hồ Chí Minh, khánh thành năm 1914. Chợ có bốn cửa chính "
         "nhìn ra bốn hướng.", "Chợ Bến Thành khánh thành năm 1914 và có hơn 1.500 gian hàng.", "co",
         "ngữ cảnh không nói số gian hàng, đó là dữ kiện mới."),
        ("Sông Đà là phụ lưu lớn nhất của sông Hồng. Trên sông Đà có nhà máy thủy điện Hòa Bình và nhà máy "
         "thủy điện Sơn La.", "Nhà máy thủy điện Hòa Bình quan trọng hơn nhà máy thủy điện Sơn La.", "khong",
         "hai nhà máy đều có trong ngữ cảnh; chỉ phép so sánh là chưa kết luận được."),
        ("Lan học ở trường A từ năm 2018 đến năm 2021. Trong thời gian này, Lan đạt giải nhì môn Toán cấp "
         "tỉnh.", "Lan đạt giải nhì môn Toán cấp tỉnh nhờ học ở trường A.", "khong",
         "mọi dữ kiện đều có; quan hệ nguyên nhân thì ngữ cảnh không nói."),
        ("Vườn quốc gia Cúc Phương được thành lập năm 1962, là vườn quốc gia đầu tiên của Việt Nam.",
         "Vườn quốc gia Cúc Phương có loài voọc mông trắng sinh sống.", "co",
         "loài voọc mông trắng là dữ kiện mới."),
    ],
    "b": [
        ("Phố cổ Hội An được UNESCO công nhận là Di sản văn hóa thế giới năm 1999.",
         "Phố cổ Hội An đón bốn triệu lượt khách mỗi năm.", "co", "số lượt khách là dữ kiện mới."),
        ("Công ty X mở chi nhánh ở Đà Nẵng và Cần Thơ. Năm 2020, doanh thu của công ty tăng 12 %.",
         "Chi nhánh Đà Nẵng đóng góp vào mức tăng doanh thu nhiều hơn chi nhánh Cần Thơ.", "khong",
         "các dữ kiện đều có; chỉ phép so sánh là chưa kết luận được."),
        ("Cà phê Robusta được trồng nhiều ở Đắk Lắk. Đắk Lắk có đất đỏ bazan.",
         "Đất đỏ bazan là lý do chính khiến Đắk Lắk trồng nhiều cà phê Robusta.", "khong",
         "quan hệ nguyên nhân không có trong ngữ cảnh, nhưng không có dữ kiện mới."),
        ("Cầu Long Biên bắc qua sông Hồng, hoàn thành năm 1902.",
         "Cầu Long Biên do công ty Daydé và Pillé thi công.", "co", "đơn vị thi công là dữ kiện mới."),
    ],
}

LABEL_TEXT = {
    "no": ("Trung thực", "Mọi ý trong câu trả lời đều có căn cứ trong ngữ cảnh"),
    "intrinsic": ("Ảo giác nội tại", "Dựa vào nội dung có trong ngữ cảnh nhưng mâu thuẫn với ngữ cảnh"),
    "extrinsic": ("Ảo giác ngoại lai", "Có thông tin mà ngữ cảnh không nhắc tới"),
}
ERROR_GUIDE = """
<p>Mỗi câu trả lời có <b>hai nhãn ứng viên</b>. Một nhãn là nhãn của bộ dữ liệu, một nhãn do bộ phát hiện gán; phiếu
không cho biết nhãn nào là của ai, và thứ tự được xáo ngẫu nhiên. Chọn nhãn <b>phù hợp hơn</b> với ngữ cảnh.</p>
<ul>
<li><b>Trung thực</b>: mọi ý đều có căn cứ trong ngữ cảnh.</li>
<li><b>Nội tại</b>: nói về nội dung có trong ngữ cảnh nhưng mâu thuẫn với ngữ cảnh.</li>
<li><b>Ngoại lai</b>: bổ sung thông tin mà ngữ cảnh không nhắc tới.</li>
</ul>
<p>Câu hỏi của người dùng có thể bị bỏ dấu hoặc viết sai; chỉ đánh giá <b>câu trả lời</b> so với <b>ngữ cảnh</b>. Một câu
trả lời vừa mâu thuẫn vừa thêm thông tin thì chọn lỗi <b>nặng hơn</b> trong hai ứng viên và ghi chú. Chọn “cả hai
đều không đúng” khi nhãn thứ ba mới đúng, “không rõ” khi không kết luận được. Nên ghi một dòng lý do, vì ghi
chú sẽ dùng để phân loại lỗi. Làm một mình, không trao đổi.</p>
"""


# -- drawing -----------------------------------------------------------------------------


def draw_round2(frame: pd.DataFrame, used: set[str]) -> dict[str, pd.DataFrame]:
    """The main sheet and the two practice sets, none of them touching ``used`` or each other."""
    ordered = frame.sort_values("sample_id", kind="stable")
    ordered = ordered[~ordered["sample_id"].isin(used)].drop_duplicates("sample_id")
    out: dict[str, list] = {"main": [], "practice_a": [], "practice_b": []}
    out["main"].append(ordered[ordered["label_original"] == NEI].sample(
        n=N_NEI, random_state=SEED))
    for original in sorted(KEY_OF):
        pool = ordered[ordered["label_original"] == original]
        take = pool.sample(n=N_CONTROLS + 2 * N_PRACTICE, random_state=SEED)
        out["main"].append(take.iloc[:N_CONTROLS])
        out["practice_a"].append(take.iloc[N_CONTROLS : N_CONTROLS + N_PRACTICE])
        out["practice_b"].append(take.iloc[N_CONTROLS + N_PRACTICE :])
    return {name: pd.concat(parts).sort_values("sample_id", kind="stable")
            .sample(frac=1.0, random_state=SEED).reset_index(drop=True)
            for name, parts in out.items()}


def practice_rows(drawn: pd.DataFrame, which: str) -> list[dict]:
    rows = [{"sample_id": r.sample_id, "context": r.context, "claim": r.response,
             "key": {"q1": KEY_OF[r.label_original]},
             "explain": f"nhãn gốc của bộ dữ liệu là {r.label_original}."}
            for r in drawn.itertuples()]
    crafted = [{"sample_id": f"luyen_tap_{which}{i}", "context": context, "claim": claim,
                "key": {"q1": "khong_du", "q2": q2}, "explain": why}
               for i, (context, claim, q2, why) in enumerate(CRAFTED[which], start=1)]
    mixed = []  # spread the crafted ones through the set instead of leaving them at the end
    step = max(1, len(rows) // len(crafted))
    for i, row in enumerate(rows):
        mixed.append(row)
        if (i + 1) % step == 0 and crafted:
            mixed.append(crafted.pop(0))
    return mixed + crafted


def error_rows(frame: pd.DataFrame, who: str) -> list[dict]:
    rows = []
    for r in frame.itertuples():
        flip = hashlib.sha256(f"{who}:{r.sample_id}".encode()).digest()[0] % 2
        pair = [r.pred, r.label] if flip else [r.label, r.pred]
        options = [{"value": label, "label": LABEL_TEXT[label][0], "hint": LABEL_TEXT[label][1]}
                   for label in pair]
        options += [{"value": "khac", "label": "Cả hai đều không đúng"},
                    {"value": "khong_ro", "label": "Không rõ"}]
        rows.append({"sample_id": r.sample_id, "context": r.context, "question": r.question,
                     "claim": r.response, "options": {"chon": options}})
    return rows


def render(form: dict) -> str:
    # "</" is escaped so a response containing a closing tag cannot end the script block
    payload = json.dumps(form, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.read_text(encoding="utf-8").replace("/*DATA*/null", payload)


def command_prepare(args) -> int:
    used = set(pd.read_csv(RESULTS / "nei_mapping_audit_lan.csv", encoding=CSV_ENCODING)
               ["sample_id"])
    drawn = draw_round2(read_viwikifc(Path("data/interim")), used)
    errors = pd.read_csv(RESULTS / "error_analysis.csv", encoding=CSV_ENCODING).fillna("")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    base = {"questions": NEI_QUESTIONS, "guide": NEI_GUIDE, "claimTitle": "Phát biểu cần đánh giá"}
    for who in ANNOTATORS:
        forms = [
            {**base, "id": f"1_luyen_tap_a_{who}", "title": "Gán nhãn NEI, luyện tập A",
             "practice": True, "rows": practice_rows(drawn["practice_a"], "a")},
            {**base, "id": f"1_luyen_tap_b_{who}", "title": "Gán nhãn NEI, luyện tập B",
             "practice": True, "rows": practice_rows(drawn["practice_b"], "b")},
            {**base, "id": f"nei_round2_{who}", "title": "Gán nhãn NEI vòng 2",
             "rows": [{"sample_id": r.sample_id, "context": r.context, "claim": r.response}
                      for r in drawn["main"].itertuples()]},
            {"id": f"error_reading_{who}", "title": "Đọc 100 câu trả lời",
             "guide": ERROR_GUIDE, "claimTitle": "Câu trả lời cần đánh giá",
             "questions": [{"key": "chon", "options": [],
                            "text": "Nhãn nào phù hợp hơn với ngữ cảnh?"}],
             "rows": error_rows(errors, who)},
        ]
        for form in forms:
            path = out / f"{form['id']}.html"
            path.write_text(render(form), encoding="utf-8")
            print(f"  {path}  ({len(form['rows'])} câu)")
    return 0


# -- reading back ------------------------------------------------------------------------


def read_answers(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding=CSV_ENCODING, dtype=str).fillna("")
    return frame.drop_duplicates("sample_id").set_index("sample_id")


def code_of(q1: str, q2: str) -> str:
    """The five outcomes round 2 can tell apart."""
    if q1 == "khong_du":
        return {"co": "ngoai_lai", "khong": "suy_dien"}.get(q2, "")
    return {"xac_nhan": "khong", "bac_bo": "noi_tai", "khong_chac": "khong_chac"}.get(q1, "")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def command_practice(args) -> int:
    used = set(pd.read_csv(RESULTS / "nei_mapping_audit_lan.csv", encoding=CSV_ENCODING)
               ["sample_id"])
    drawn = draw_round2(read_viwikifc(Path("data/interim")), used)
    answers = read_answers(Path(args.path))
    rows = practice_rows(drawn[f"practice_{args.set}"], args.set)
    wrong = []
    for row in rows:
        got = answers.loc[row["sample_id"]] if row["sample_id"] in answers.index else {}
        if any(got.get(key, "") != value for key, value in row["key"].items()):
            wrong.append(row["sample_id"])
    score = 1 - len(wrong) / len(rows)
    print(f"{args.path}: đúng {len(rows) - len(wrong)}/{len(rows)} ({score:.0%}) — "
          f"{'ĐẠT, gán thật được' if score >= PASS_MARK else 'CHƯA ĐẠT, đọc lại hướng dẫn'}")
    print("  khác đáp án:", wrong or "không")
    return 0


def summarise_nei(codes: pd.DataFrame, originals: pd.Series) -> dict:
    """``codes`` has one column per annotator; ``originals`` the corpus label per row."""
    first, second = ANNOTATORS
    nei = codes[originals == NEI]
    out: dict = {"n_nei": len(nei), "kappa": agreement(nei[first], nei[second])}
    broad = nei.replace({"suy_dien": "khong_du", "ngoai_lai": "khong_du"})
    out["kappa_question1"] = agreement(broad[first], broad[second])
    out["crosstab"] = pd.crosstab(nei[first], nei[second]).to_dict("index")
    for name, table in (("strict", nei), ("broad", broad)):
        value = "ngoai_lai" if name == "strict" else "khong_du"
        both = int(((table[first] == value) & (table[second] == value)).sum())
        out[f"both_{name}"] = both
        out[f"both_{name}_ci"] = wilson(both, len(nei))
        out[f"each_{name}"] = {who: int((table[who] == value).sum()) for who in ANNOTATORS}
    controls = codes[originals != NEI]
    want = originals[originals != NEI].map({"Supports": "khong", "Refutes": "noi_tai"})
    out["controls"] = {who: {"right": int((controls[who] == want).sum()), "n": len(want),
                             "by_label": {str(k): int(v) for k, v in
                                          (controls[who] == want).groupby(
                                              originals[originals != NEI]).sum().items()}}
                       for who in ANNOTATORS}
    out["controls_both_extrinsic"] = int(
        ((controls[first] == "ngoai_lai") & (controls[second] == "ngoai_lai")).sum())
    return out


def summarise_errors(frame: pd.DataFrame) -> dict:
    """``frame``: label, pred and one ``chon_<who>`` column per annotator."""
    def side(row, who):
        choice = row[f"chon_{who}"]
        return ("nhan_goc" if choice == row["label"]
                else "du_doan" if choice == row["pred"] else choice)

    sides = pd.DataFrame({who: frame.apply(side, axis=1, who=who) for who in ANNOTATORS})
    first, second = ANNOTATORS
    both = {value: int(((sides[first] == value) & (sides[second] == value)).sum())
            for value in ("nhan_goc", "du_doan", "khac", "khong_ro")}
    return {"n": len(frame), "both": both, "disagree": len(frame) - sum(both.values()),
            "kappa": agreement(sides[first], sides[second]),
            "both_pred_ci": wilson(both["du_doan"], len(frame)),
            "each": {who: sides[who].value_counts().to_dict() for who in ANNOTATORS}}


def command_report(args) -> int:
    done = {}
    frame = read_viwikifc(Path("data/interim")).drop_duplicates("sample_id").set_index("sample_id")
    paths = {who: RESULTS / f"nei_round2_{who}.csv" for who in ANNOTATORS}
    if all(p.is_file() for p in paths.values()):
        answers = {who: read_answers(p) for who, p in paths.items()}
        ids = sorted(set(answers["lan"].index) & set(answers["minh"].index))
        codes = pd.DataFrame({who: [code_of(*answers[who].loc[i, ["q1", "q2"]]) for i in ids]
                              for who in ANNOTATORS}, index=ids)
        blank = {who: int((codes[who] == "").sum()) for who in ANNOTATORS}
        if any(blank.values()):
            raise SystemExit(f"còn câu chưa trả lời: {blank}")
        originals = frame.loc[ids, "label_original"]
        done["nei"] = summarise_nei(codes, originals)
        table = codes.assign(label_original=originals,
                             **{f"ghi_chu_{w}": answers[w].loc[ids, "ghi_chu"] for w in ANNOTATORS})
        table.to_csv(RESULTS / "nei_round2.csv", encoding=CSV_ENCODING, index_label="sample_id")
    paths = {who: RESULTS / f"error_reading_{who}.csv" for who in ANNOTATORS}
    if all(p.is_file() for p in paths.values()):
        errors = pd.read_csv(RESULTS / "error_analysis.csv", encoding=CSV_ENCODING).fillna("")
        for who, path in paths.items():
            errors[f"chon_{who}"] = errors["sample_id"].map(read_answers(path)["chon"]).fillna("")
            if (errors[f"chon_{who}"] == "").any():
                raise SystemExit(f"{path}: còn câu chưa trả lời")
        done["errors"] = summarise_errors(errors)
    if not done:
        raise SystemExit("chưa có tệp CSV nào của hai người trong results/")
    print(json.dumps(done, ensure_ascii=False, indent=2))
    if "nei" in done:
        kappa = done["nei"]["kappa"]["kappa"]
        print(f"kappa năm mã: {kappa:.3f} ({describe_kappa(kappa)}); vòng 1: 0,505")
    (RESULTS / "annotation_round2.json").write_text(
        json.dumps(done, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--out", default=str(FORM_DIR))
    prepare.set_defaults(func=command_prepare)
    practice = commands.add_parser("practice")
    practice.add_argument("path")
    practice.add_argument("--set", choices=("a", "b"), default="a")
    practice.set_defaults(func=command_practice)
    report = commands.add_parser("report")
    report.set_defaults(func=command_report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
