from __future__ import annotations

import json
from pathlib import Path


def state_file_path(base_dir: Path) -> Path:
    return base_dir / "telegram_state.json"


def load_state(base_dir: Path) -> dict[str, object]:
    path = state_file_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(base_dir: Path, payload: dict[str, object]) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    path = state_file_path(base_dir)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
