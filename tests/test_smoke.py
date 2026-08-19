"""Smoke test: the package imports and exposes a version string."""

import vihallulens


def test_package_imports_and_has_version():
    assert isinstance(vihallulens.__version__, str)
    assert vihallulens.__version__


def test_subpackages_import():
    """The six sub-packages of the four-layer architecture in docs/SPEC.md must be importable."""
    import importlib

    for name in ("data", "extract", "features", "detect", "evaluation", "serve"):
        assert importlib.import_module(f"vihallulens.{name}") is not None
