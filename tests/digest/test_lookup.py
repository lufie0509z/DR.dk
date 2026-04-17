from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dr_digest.digest.lookup import load_menu_payload, resolve_entry_by_number


class LookupTests(unittest.TestCase):
    def test_load_menu_payload_and_resolve_number(self) -> None:
        payload = {
            "source_name": "dr",
            "fetched_at": "2026-04-15T21:41:41+00:00",
            "display_language": "en",
            "entries": [
                {"number": 1, "guid": "urn:example:1", "title": "One"},
                {"number": 2, "guid": "urn:example:2", "title": "Two"},
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            menu_path = Path(temp_dir) / "menu.json"
            menu_path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_menu_payload(menu_path)
            entry = resolve_entry_by_number(loaded, 2)

        self.assertEqual(entry["guid"], "urn:example:2")

    def test_resolve_entry_by_number_raises_for_missing_item(self) -> None:
        with self.assertRaises(ValueError):
            resolve_entry_by_number({"entries": [{"number": 1}]}, 3)


if __name__ == "__main__":
    unittest.main()
