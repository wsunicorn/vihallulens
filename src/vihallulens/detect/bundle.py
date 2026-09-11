"""A fitted detector together with everything needed to apply it to a new sample.

``LookbackDetector`` on its own is a scaler and a logistic regression over some number of
columns. It does not know what those columns *are*: which feature groups, which layers, which
heads survived the ``topk`` selection on dev, whether the ``basic`` block was kept whole. Every
experiment script knew those things while it ran and then threw them away — the T35 error
analysis had to refit E03 from scratch to get a model to inspect, because none had been saved
in a usable form.

This bundle is the usable form. It carries the detector and the recipe for its input columns,
so ``vector(record)`` builds the exact matrix row the detector was fitted on, from one record,
at request time. The recipe is validated against the record — a shard extracted from a different
reading model has the same vector length and different column meanings, and E13/E14 showed how
far apart those can be — so a mismatch raises rather than returning a number.
"""

from __future__ import annotations

import json
import pickle
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from vihallulens.detect.detector import LookbackDetector
from vihallulens.evaluation.metrics import LABELS
from vihallulens.features.assemble import build_matrix, matrix_names

BUNDLE_VERSION = 1


@dataclass
class DetectorBundle:
    """Everything between a shard record and a label."""

    detector: LookbackDetector
    groups: list[str]
    mode: str
    keep: list[int] | None
    layer_indices: list[int]
    n_heads: int
    run_name: str
    config: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)
    version: int = BUNDLE_VERSION

    # -- the input recipe ----------------------------------------------------------------

    @property
    def n_layers(self) -> int:
        return len(self.layer_indices)

    @property
    def feature_names(self) -> list[str]:
        return matrix_names(self.groups, self.layer_indices, self.n_heads, self.mode,
                            None if self.keep is None else np.asarray(self.keep))

    @property
    def n_features(self) -> int:
        return len(self.feature_names)

    def check_record(self, record: dict) -> None:
        """Refuse a record whose columns would not mean what the detector thinks they mean."""
        got = list(record.get("layer_indices", []))
        if got != list(self.layer_indices):
            raise ValueError(
                f"bản ghi trích trên lưới lớp {got}, bộ phát hiện khớp trên {self.layer_indices} "
                f"— cùng chỉ số cột mà khác nghĩa, không chấm được"
            )
        width = len(record["lookback_total"])
        expected = self.n_layers * self.n_heads
        if width != expected:
            raise ValueError(
                f"bản ghi có {width} giá trị lookback_total, bộ phát hiện chờ "
                f"{self.n_layers} lớp × {self.n_heads} đầu = {expected}"
            )

    def vector(self, records) -> np.ndarray:
        """The detector's input for one or more records, columns in fitted order."""
        rows = [records] if isinstance(records, dict) else list(records)
        for record in rows:
            self.check_record(record)
        keep = None if self.keep is None else np.asarray(self.keep)
        return build_matrix(rows, self.groups, self.n_layers, self.n_heads, self.mode, keep)

    # -- scoring ---------------------------------------------------------------------------

    def predict_record(self, record: dict) -> tuple[str, dict[str, float]]:
        """Label and per-class probabilities for one record, in reporting order."""
        matrix = self.vector(record)
        label = str(self.detector.predict(matrix)[0])
        proba = self.detector.predict_proba(matrix)[0]
        pairs = zip(self.detector.classes_, proba, strict=True)
        by_class = {str(cls): float(p) for cls, p in pairs}
        return label, {name: by_class.get(name, 0.0) for name in LABELS}

    # -- persistence -----------------------------------------------------------------------

    def save(self, path: Path | str) -> Path:
        """One pickle. A JSON sidecar next to it says what is inside without unpickling."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(self, handle)
        sidecar = {k: v for k, v in asdict(self).items() if k != "detector"}
        sidecar["n_features"] = self.n_features
        sidecar["n_params_trainable"] = int(self.detector.n_params_trainable)
        path.with_suffix(".json").write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @staticmethod
    def load(path: Path | str) -> DetectorBundle:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"không thấy {path}")
        with path.open("rb") as handle:
            bundle = pickle.load(handle)
        if not isinstance(bundle, DetectorBundle):
            raise TypeError(f"{path} không phải DetectorBundle mà là {type(bundle).__name__}")
        return bundle

    def describe(self) -> str:
        keep = "tất cả" if self.keep is None else f"{len(self.keep)} đầu"
        return (f"{self.run_name}: {', '.join(self.groups)} · {self.mode} ({keep}) · "
                f"lưới {self.n_layers} × {self.n_heads} · {self.n_features} cột · "
                f"{self.detector.n_params_trainable:,} tham số")
