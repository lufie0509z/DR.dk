from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from dr_digest.cli import main


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "dr_senestenyt.xml"


class CliTests(unittest.TestCase):
    def test_ingest_dr_command_saves_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            previous_raw_dir = os.environ.get("RAW_STORAGE_DIR")
            os.environ["RAW_STORAGE_DIR"] = temp_dir
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "ingest-dr",
                            "--feed-url",
                            FIXTURE_PATH.as_uri(),
                            "--max-items",
                            "2",
                        ]
                    )
                self.assertEqual(exit_code, 0)
                output = json.loads(stdout.getvalue())
                self.assertEqual(output["item_count"], 2)
                self.assertTrue(Path(output["feed_xml_path"]).exists())
                self.assertTrue(Path(output["items_json_path"]).exists())
            finally:
                if previous_raw_dir is None:
                    os.environ.pop("RAW_STORAGE_DIR", None)
                else:
                    os.environ["RAW_STORAGE_DIR"] = previous_raw_dir


if __name__ == "__main__":
    unittest.main()
