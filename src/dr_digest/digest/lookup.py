from __future__ import annotations

import json
from pathlib import Path


def load_menu_payload(menu_json_path: Path) -> dict[str, object]:
    return json.loads(menu_json_path.read_text(encoding="utf-8"))


def resolve_entry_by_number(menu_payload: dict[str, object], number: int) -> dict[str, object]:
    for entry in menu_payload.get("entries", []):
        if int(entry["number"]) == number:
            return entry
    raise ValueError(f"Digest item number {number} was not found in the menu.")
