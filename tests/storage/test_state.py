from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dr_digest.storage.state import load_state, save_state, state_file_path


class StateStorageTests(unittest.TestCase):
    def test_save_and_load_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            save_state(base_dir, {"active_menu_json_path": "menu.json", "last_update_id": 12})
            payload = load_state(base_dir)

        self.assertEqual(payload["active_menu_json_path"], "menu.json")
        self.assertEqual(payload["last_update_id"], 12)

    def test_load_state_returns_empty_dict_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = load_state(Path(temp_dir))
        self.assertEqual(payload, {})


if __name__ == "__main__":
    unittest.main()
