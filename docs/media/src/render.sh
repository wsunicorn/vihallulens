#!/usr/bin/env bash
# Rasterise one of the generated SVG figures with headless Chrome.
# Usage: ./render.sh <name-without-extension> <width> <height> [scale]
# Runs in Git Bash on Windows; CHROME_PATH overrides the default Chrome install.
set -euo pipefail

CHROME="${CHROME_PATH:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
MEDIA="$(cygpath -m "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)")"
WIN_MEDIA="$(cygpath -w "$MEDIA")"

name="$1"; w="$2"; h="$3"; scale="${4:-2}"

"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --default-background-color=ffffff \
  --force-device-scale-factor="$scale" \
  --window-size="$w,$h" \
  --screenshot="$WIN_MEDIA\\$name.png" \
  "file:///$MEDIA/$name.svg" 2>&1 | tail -1

python - "$MEDIA/$name.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1])
print(f"{sys.argv[1]} -> {im.size[0]}x{im.size[1]}")
PY
