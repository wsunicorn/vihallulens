"""The classifier that sits on top of whatever features were extracted.

Section 2.4 of docs/SPEC.md fixes the default as multiclass logistic regression with balanced
class weights, and says the default must stay linear: the whole argument of this thesis is that
the signal is already present in the attention weights and needs only a cheap read-out. A
gradient-boosted model that beat it would leave open whether the gain came from the signal or
from the classifier, which is the one question the experiments must not blur.

The same class serves every experiment from E01 onward. Only the feature matrix changes.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np

DETECTOR_TYPES = ("logistic_regression", "linear_svc", "lightgbm")
CLASS_WEIGHTS = ("balanced", "none")

# Enough for lbfgs to converge on the small, well-conditioned feature matrices used here.
# Raised from the sklearn default of 100 because the surface features of E01 are on very
# different scales and the solver warns otherwise.
MAX_ITER = 2000


class LookbackDetector:
    """Fit, predict, and persist. Interface per section 2.4 of docs/SPEC.md."""

    def __init__(
        self,
        detector_type: str = "logistic_regression",
        class_weight: str = "balanced",
        seed: int = 42,
        standardize: bool = True,
    ) -> None:
        if detector_type not in DETECTOR_TYPES:
            raise ValueError(
                f"không biết loại {detector_type!r}; chọn một trong {list(DETECTOR_TYPES)}"
            )
        if class_weight not in CLASS_WEIGHTS:
            raise ValueError(
                f"không biết class_weight {class_weight!r}; chọn một trong {list(CLASS_WEIGHTS)}"
            )
        self.detector_type = detector_type
        self.class_weight = class_weight
        self.seed = seed
        # Response length is counted in words and lexical overlap lies in [0, 1], two scales
        # that differ by a factor of about forty. Without standardising, the regularisation
        # penalty falls almost entirely on the smaller-scale feature.
        self.standardize = standardize
        self._model = None
        self._scaler = None
        self.classes_: np.ndarray | None = None

    def _build(self):
        weight = None if self.class_weight == "none" else "balanced"
        if self.detector_type == "logistic_regression":
            from sklearn.linear_model import LogisticRegression

            return LogisticRegression(
                class_weight=weight, max_iter=MAX_ITER, random_state=self.seed
            )
        if self.detector_type == "linear_svc":
            from sklearn.svm import LinearSVC

            return LinearSVC(class_weight=weight, random_state=self.seed)
        from lightgbm import LGBMClassifier  # imported late: an optional comparison only

        return LGBMClassifier(class_weight=weight, random_state=self.seed, verbose=-1)

    def fit(self, X, y) -> LookbackDetector:
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        if len(X) != len(y):
            raise ValueError(f"X có {len(X)} dòng, y có {len(y)}")
        if len(np.unique(y)) < 2:
            raise ValueError("cần ít nhất hai lớp để huấn luyện")

        if self.standardize:
            from sklearn.preprocessing import StandardScaler

            self._scaler = StandardScaler().fit(X)
            X = self._scaler.transform(X)

        self._model = self._build().fit(X, y)
        self.classes_ = self._model.classes_
        return self

    def _prepare(self, X) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("chưa huấn luyện: gọi fit trước")
        X = np.asarray(X, dtype=np.float64)
        return self._scaler.transform(X) if self._scaler is not None else X

    def predict(self, X) -> np.ndarray:
        # _prepare first: attribute access on a None model would raise AttributeError from
        # somewhere inside sklearn instead of saying that fit was never called.
        prepared = self._prepare(X)
        return self._model.predict(prepared)

    def predict_proba(self, X) -> np.ndarray:
        """Class probabilities, in the order of ``classes_``.

        LinearSVC has no probabilities of its own — it returns distances from the decision
        boundary — so asking for them is refused rather than answered with a softmax over
        distances, which would look like a probability without being one.
        """
        model = self._model
        if model is None:
            raise RuntimeError("chưa huấn luyện: gọi fit trước")
        if not hasattr(model, "predict_proba"):
            raise NotImplementedError(
                f"{self.detector_type} không cho xác suất; dùng logistic_regression nếu cần ECE"
            )
        return model.predict_proba(self._prepare(X))

    @property
    def feature_weights(self) -> np.ndarray:
        """How hard the fitted model leans on each input feature.

        The largest absolute coefficient across the classes, one number per feature. Added at
        T20, where the reproduction has 756 inputs — one per layer-head pair — and one of the
        paper's findings is that a few heads carry most of the signal. Weight spread evenly over
        all of them is the shape of a reproduction that fitted noise, so it has to be visible.

        Public rather than reached for through ``_model`` because E13 asks the same question of
        a different reading model, and a private attribute would make that comparison a matter
        of remembering an implementation detail.
        """
        model = self._model
        if model is None:
            raise RuntimeError("chưa huấn luyện: gọi fit trước")
        if not hasattr(model, "coef_"):
            raise NotImplementedError(f"{self.detector_type} không phải mô hình tuyến tính")
        return np.abs(np.asarray(model.coef_)).max(axis=0)

    @property
    def n_params_trainable(self) -> int:
        """Number of fitted parameters, for the cost column of experiment E11.

        For a linear model this is the coefficient matrix plus the intercepts — a handful of
        numbers, which is the point being made against fine-tuning an encoder.
        """
        model = self._model
        if model is None:
            raise RuntimeError("chưa huấn luyện: gọi fit trước")
        if not hasattr(model, "coef_"):
            return 0
        return int(np.asarray(model.coef_).size + np.asarray(model.intercept_).size)

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            pickle.dump(self, handle)
        return path

    @staticmethod
    def load(path: Path | str) -> LookbackDetector:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"không thấy {path}")
        with path.open("rb") as handle:
            return pickle.load(handle)
