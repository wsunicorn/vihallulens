"""Remembering what the judge already said, so no sample is ever paid for twice.

Task T19 asks for this outright, and the free tier is why: a per-day allowance smaller than the
sample size makes a run that cannot resume simply impossible to finish. Every answer is appended
the moment it arrives, so a run killed by quota, by a dropped connection or by Ctrl-C keeps
everything it had already spent.

The key covers the model and the exact prompt. Reword the rubric and the old answers stop
matching, which is correct: they answered a different question, and silently reusing them would
be the quietest way to report a result that never happened.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def cache_key(model: str, prompt: str) -> str:
    """Stable id for one question put to one model."""
    digest = hashlib.sha256(f"{model}\x00{prompt}".encode())
    return digest.hexdigest()[:16]


class JudgeCache:
    """Append-only JSONL, read once into memory at startup."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.entries: dict[str, dict] = {}
        self.hits = 0
        self.writes = 0
        if self.path.exists():
            self._read()

    def _read(self) -> None:
        with self.path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    # A run killed mid-write leaves a truncated final line. Dropping it loses
                    # one sample; refusing to start loses the whole cache.
                    print(f"  bỏ qua dòng hỏng {number} trong {self.path}")
                    continue
                if "key" in record:
                    self.entries[record["key"]] = record

    def get(self, key: str) -> dict | None:
        record = self.entries.get(key)
        if record is not None:
            self.hits += 1
        return record

    def put(self, key: str, payload: dict) -> dict:
        record = {"key": key, **payload}
        self.entries[key] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.writes += 1
        return record

    def __len__(self) -> int:
        return len(self.entries)

    def __contains__(self, key: str) -> bool:
        return key in self.entries
