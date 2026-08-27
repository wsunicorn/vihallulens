"""What actually arrived when a checkpoint was loaded.

``transformers`` prints a load report saying which weights were missing, unexpected or
re-initialised. Task T18 silences it with ``logging.set_verbosity_error()``, because the
tokenizer repeats a truncation warning once per batch and buries everything worth reading —
which also buries the one message that would announce a silently half-loaded model.

So the check moves here, where it is explicit and testable instead of being a log line nobody
reads. It cost real time at T18: with the report suppressed, "the body was never loaded" stayed
a live theory for InfoXLM-large long after it should have been ruled out in one line.
"""

from __future__ import annotations

# Weights the classification head brings with it. These are supposed to be missing from a
# checkpoint trained on some other task — that is what fine-tuning is for.
HEAD_PREFIXES = ("classifier.", "score.", "lm_head.", "pooler.")


def body_gaps(loading_info) -> dict[str, list[str]]:
    """Split a transformers loading report into the harmless part and the alarming part.

    Missing head weights are expected. Missing *body* weights are not: they mean part of the
    pretrained network was replaced by a random draw, and the model will train far worse than
    its name suggests while giving no other sign.
    """
    def names(key):
        # transformers returns a set on some versions and a list on others.
        return sorted(loading_info.get(key) or [])

    missing = names("missing_keys")
    return {
        "body_missing": [k for k in missing if not k.startswith(HEAD_PREFIXES)],
        "head_missing": [k for k in missing if k.startswith(HEAD_PREFIXES)],
        "unexpected": names("unexpected_keys"),
        "mismatched": [str(k) for k in names("mismatched_keys")],
        "errors": [str(k) for k in names("error_msgs")],
    }


def describe(loading_info) -> tuple[bool, str]:
    """One line about the load, and whether it is safe to train on.

    Returns ``(ok, message)``. ``ok`` is False only when the pretrained body is incomplete or
    the loader reported an outright error — the two cases where continuing would waste a GPU
    session on a model that is not the one being claimed.
    """
    gaps = body_gaps(loading_info)
    if gaps["errors"]:
        return False, f"lỗi khi nạp: {gaps['errors'][:2]}"
    if gaps["mismatched"]:
        return False, f"lệch kích thước {len(gaps['mismatched'])} tensor: {gaps['mismatched'][:2]}"
    if gaps["body_missing"]:
        return False, (
            f"{len(gaps['body_missing'])} trọng số của THÂN mô hình không có trong checkpoint "
            f"nên bị khởi tạo ngẫu nhiên, ví dụ {gaps['body_missing'][:3]} — "
            f"mô hình này không phải mô hình đã tiền huấn luyện"
        )
    return True, (
        f"thân nạp đủ; đầu phân loại mới khởi tạo {len(gaps['head_missing'])} trọng số, "
        f"bỏ qua {len(gaps['unexpected'])} trọng số của tác vụ cũ"
    )
