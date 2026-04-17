from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dr_digest.cli import main


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "dr_senestenyt.xml"


class CliTests(unittest.TestCase):
    def test_ingest_dr_command_saves_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            previous_raw_dir = os.environ.get("RAW_STORAGE_DIR")
            previous_digest_dir = os.environ.get("DIGEST_STORAGE_DIR")
            os.environ["RAW_STORAGE_DIR"] = temp_dir
            os.environ["DIGEST_STORAGE_DIR"] = str(Path(temp_dir) / "digests")
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
                self.assertEqual(output["short_summary_count"], 2)
                self.assertTrue(Path(output["feed_xml_path"]).exists())
                self.assertTrue(Path(output["items_json_path"]).exists())
                self.assertTrue(Path(output["short_digest_path"]).exists())
                self.assertTrue(Path(output["menu_json_path"]).exists())
                self.assertTrue(Path(output["menu_batch_dir"]).exists())
                self.assertEqual(output["menu_batch_count"], 1)
            finally:
                if previous_raw_dir is None:
                    os.environ.pop("RAW_STORAGE_DIR", None)
                else:
                    os.environ["RAW_STORAGE_DIR"] = previous_raw_dir

                if previous_digest_dir is None:
                    os.environ.pop("DIGEST_STORAGE_DIR", None)
                else:
                    os.environ["DIGEST_STORAGE_DIR"] = previous_digest_dir

    @patch("dr_digest.cli.translate_feed_snapshot")
    def test_ingest_dr_command_reports_translation_count(self, mock_translate_feed_snapshot) -> None:
        mock_translate_feed_snapshot.return_value = 2
        with tempfile.TemporaryDirectory() as temp_dir:
            previous_raw_dir = os.environ.get("RAW_STORAGE_DIR")
            previous_digest_dir = os.environ.get("DIGEST_STORAGE_DIR")
            previous_argos_dir = os.environ.get("ARGOS_PACKAGES_DIR")
            os.environ["RAW_STORAGE_DIR"] = temp_dir
            os.environ["DIGEST_STORAGE_DIR"] = str(Path(temp_dir) / "digests")
            os.environ["ARGOS_PACKAGES_DIR"] = str(Path(temp_dir) / "argos" / "packages")
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
                            "--translate",
                            "--translation-limit",
                            "2",
                        ]
                    )
                self.assertEqual(exit_code, 0)
                output = json.loads(stdout.getvalue())
                self.assertEqual(output["translated_item_count"], 2)
            finally:
                if previous_raw_dir is None:
                    os.environ.pop("RAW_STORAGE_DIR", None)
                else:
                    os.environ["RAW_STORAGE_DIR"] = previous_raw_dir

                if previous_digest_dir is None:
                    os.environ.pop("DIGEST_STORAGE_DIR", None)
                else:
                    os.environ["DIGEST_STORAGE_DIR"] = previous_digest_dir

                if previous_argos_dir is None:
                    os.environ.pop("ARGOS_PACKAGES_DIR", None)
                else:
                    os.environ["ARGOS_PACKAGES_DIR"] = previous_argos_dir

    def test_detail_command_writes_detail_artifacts(self) -> None:
        menu_payload = {
            "source_name": "dr",
            "fetched_at": "2026-04-15T21:41:41+00:00",
            "display_language": "en",
            "entries": [
                {
                    "number": 3,
                    "guid": "urn:example:3",
                    "link": "https://www.dr.dk/nyheder/example-3",
                    "title": "Dansk titel",
                    "summary": "Dansk resume",
                    "body_text": "Dansk brødtekst",
                    "section": "Kort nyt",
                    "published_at": "2026-04-15T12:00:00+00:00",
                    "translations": {
                        "en": {
                            "title": "English title",
                            "summary": "English summary",
                            "body_text": "English body text",
                        }
                    },
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            previous_digest_dir = os.environ.get("DIGEST_STORAGE_DIR")
            os.environ["DIGEST_STORAGE_DIR"] = str(Path(temp_dir) / "digests")
            menu_path = Path(temp_dir) / "menu.json"
            menu_path.write_text(json.dumps(menu_payload), encoding="utf-8")
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "detail",
                            "--menu-json",
                            str(menu_path),
                            "--number",
                            "3",
                            "--language",
                            "en",
                        ]
                    )
                self.assertEqual(exit_code, 0)
                output = json.loads(stdout.getvalue())
                self.assertTrue(Path(output["detail_json_path"]).exists())
                self.assertTrue(Path(output["detail_text_path"]).exists())
            finally:
                if previous_digest_dir is None:
                    os.environ.pop("DIGEST_STORAGE_DIR", None)
                else:
                    os.environ["DIGEST_STORAGE_DIR"] = previous_digest_dir


if __name__ == "__main__":
    unittest.main()
