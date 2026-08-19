"""Report what is actually installed and where the data is, before anything expensive runs.

Every failure so far on Kaggle has been "the code you think you are running is not the code
that ran". This script answers that question in one place: which checkout, which package
file, which library versions, which data directory.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Run against the checkout rather than whatever happens to be installed. An editable install
# works through a .pth file that Python reads only at start-up, so inside a Kaggle kernel it
# can be missing entirely; the checkout is the thing we actually want to test.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def version_of(name: str) -> str:
    try:
        module = __import__(name)
    except ImportError:
        return "chưa cài"
    return getattr(module, "__version__", "không rõ")


def git_commit(repo: Path) -> str:
    try:
        done = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "không rõ"
    return done.stdout.strip()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    repo = Path(__file__).resolve().parents[1]

    print()
    print("=" * 80)
    print("MÔI TRƯỜNG")
    print("=" * 80)
    print(f"  repo             : {repo}")
    print(f"  commit           : {git_commit(repo)}")
    print(f"  python           : {sys.version.split()[0]}")
    print(f"  torch            : {version_of('torch')}")
    print(f"  transformers     : {version_of('transformers')}")
    print(f"  bitsandbytes     : {version_of('bitsandbytes')}")
    print(f"  accelerate       : {version_of('accelerate')}")

    import vihallulens
    from vihallulens.data.paths import find_raw_dir

    print(f"  vihallulens      : {vihallulens.__version__} tại {vihallulens.__file__}")

    try:
        data_dir = find_raw_dir()
    except FileNotFoundError as error:
        print(f"\n  DỮ LIỆU: KHÔNG TÌM THẤY\n  {error}")
        return 1

    files = sorted(path.name for path in data_dir.iterdir())
    print(f"  dữ liệu          : {data_dir}  ({len(files)} file)")
    for name in files:
        print(f"      {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
