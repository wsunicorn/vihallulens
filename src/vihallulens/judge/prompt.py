"""What the LLM judge is asked, and how its answer is read back.

The rubric is copied from ``results/nei_mapping_audit_HUONGDAN.md`` — the sheet the two
students annotated by hand at T13 — rather than written fresh. Handing the judge a different
definition of the three classes than the humans used would make the comparison a comparison of
instructions, and a reviewer would be right to say so.

Two deliberate departures from that sheet, both recorded because they matter when reading the
score:

1. The humans could answer ``khong_chac``. The judge cannot: a baseline has to produce a label
   for every sample or its macro-F1 is not comparable with the other rows of Bảng 1.
2. The judge states a reason *before* its verdict. The schema fixes that order, so the model
   works through the evidence before committing rather than justifying a label it already
   emitted.
"""

from __future__ import annotations

from vihallulens.evaluation.metrics import LABELS

# The judge answers in the vocabulary of the annotation sheet, not in the corpus's English
# labels, so that the wording it sees is the wording the humans saw.
VERDICT_TO_LABEL = {
    "khong": "no",
    "noi_tai": "intrinsic",
    "ngoai_lai": "extrinsic",
}
VERDICTS = tuple(VERDICT_TO_LABEL)

assert set(VERDICT_TO_LABEL.values()) == set(LABELS)

SYSTEM = """Bạn là giám khảo kiểm tra xem một câu trả lời có trung thực với ngữ cảnh được cung \
cấp hay không. Chỉ dựa vào ngữ cảnh, tuyệt đối không dùng kiến thức bên ngoài: một thông tin \
đúng ngoài đời nhưng không có trong ngữ cảnh vẫn bị tính là ngoại lai."""

# Wording follows the annotation sheet of T13 as closely as prose allows.
RUBRIC = """Đọc ngữ cảnh, rồi đọc câu trả lời. Câu hỏi duy nhất: câu trả lời có nêu thông tin \
nào không có trong ngữ cảnh không?

Chọn đúng một trong ba mã:

- `ngoai_lai`: câu trả lời nhắc tới sự vật, con số hoặc sự kiện mà ngữ cảnh KHÔNG hề nói đến.
  Thông tin đó đến từ bên ngoài.
- `noi_tai`: MỌI thông tin trong câu trả lời đều xuất hiện trong ngữ cảnh, nhưng bị nói ngược,
  bị gán sai cho nhau, hoặc sai con số. Thông tin không đến từ bên ngoài, chỉ bị dùng sai.
- `khong`: câu trả lời bám sát ngữ cảnh, không thêm gì mới và cũng không mâu thuẫn.

Chỗ dễ nhầm nhất là giữa `ngoai_lai` và `noi_tai`. Cách phân biệt: hỏi xem thông tin trong câu \
trả lời lấy từ đâu. Có trong ngữ cảnh mà dùng sai thì là `noi_tai`; không có trong ngữ cảnh thì \
là `ngoai_lai`.

Ví dụ. Ngữ cảnh: "Hà Nội là thủ đô của Việt Nam. Thành phố Hồ Chí Minh là thành phố đông dân \
nhất cả nước."

- "Hà Nội là thủ đô của Việt Nam." → `khong`, đúng như ngữ cảnh nói.
- "TP.HCM là thủ đô của Việt Nam." → `noi_tai`, hai vế đều có, chỉ bị ghép sai.
- "Hà Nội có 8 triệu dân." → `ngoai_lai`, ngữ cảnh không nói gì về dân số Hà Nội.

Phải chọn một mã, không được bỏ trống và không được trả lời là không chắc."""

# propertyOrdering makes the model write ``ly_do`` first. Gemini generates the fields in the
# order given, so this is what turns the reason into reasoning rather than into an excuse.
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "ly_do": {"type": "string"},
        "nhan_dinh": {"type": "string", "enum": list(VERDICTS)},
        "do_tin_cay": {"type": "number"},
    },
    "required": ["ly_do", "nhan_dinh", "do_tin_cay"],
    "propertyOrdering": ["ly_do", "nhan_dinh", "do_tin_cay"],
}


def build_prompt(context: str, response: str, question: str = "") -> str:
    """Assemble one judging prompt.

    The material shown mirrors what the encoder baseline of E09 is given — context, question,
    response and nothing else — so that Bảng 1 compares methods rather than compares who was
    shown more. The question block disappears entirely when there is none, following rule 1 of
    section 8 of CLAUDE.md.
    """
    parts = [RUBRIC, "", "Ngữ cảnh:", str(context).strip()]
    if str(question).strip():
        parts += ["", f"Câu hỏi: {str(question).strip()}"]
    parts += ["", "Câu trả lời cần chấm:", str(response).strip()]
    return "\n".join(parts)


def to_label(verdict: str) -> str:
    """Map an annotation-sheet code to the corpus label."""
    key = str(verdict).strip().lower()
    if key not in VERDICT_TO_LABEL:
        raise ValueError(f"mã lạ: {verdict!r}; chỉ chấp nhận {list(VERDICTS)}")
    return VERDICT_TO_LABEL[key]


def clamp_confidence(value) -> float:
    """Pull a self-reported confidence into [0, 1].

    Models return 0,85 and 85 with equal cheer, and occasionally something unparseable. This is
    only ever used for a calibration figure that is reported separately from the softmax-based
    ECE of the other rows, never mixed into the same column — the two are not the same quantity.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number > 1.0:
        number = number / 100.0
    return min(1.0, max(0.0, number))
