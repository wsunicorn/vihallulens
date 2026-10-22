"""The Docker and Kaggle requirement files pin exactly the versions recorded in uv.lock."""

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TORCH_FAMILY = re.compile(r"^(torch|triton|nvidia-)")


def locked_versions() -> dict[str, set[str]]:
    """Every version uv.lock records per package (numpy is locked twice, per Python marker)."""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    versions: dict[str, set[str]] = {}
    for package in lock["package"]:
        if "version" in package:
            versions.setdefault(package["name"].lower(), set()).add(package["version"])
    return versions


def pins(path: Path) -> list[tuple[str, str]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split(";")[0].strip()
        if line and not line.startswith("#"):
            name, version = line.split("==")
            out.append((name.strip().lower(), version.strip()))
    return out


@pytest.mark.parametrize("filename", ["requirements-docker.txt", "requirements-kaggle.txt"])
def test_every_pin_matches_uv_lock(filename):
    locked = locked_versions()
    pinned = pins(ROOT / filename)
    assert pinned
    for name, version in pinned:
        assert version in locked.get(name, set()), f"{filename}: {name}=={version}"


def test_docker_requirements_leave_torch_to_the_base_image():
    pinned = dict(pins(ROOT / "requirements-docker.txt"))
    assert not [name for name in pinned if TORCH_FAMILY.match(name)]
    for needed in ("transformers", "bitsandbytes", "scikit-learn", "fastapi", "uvicorn"):
        assert needed in pinned, needed
