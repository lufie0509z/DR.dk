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

    @patch("dr_digest.cli.send_text_batches")
    def test_telegram_send_digest_updates_state(self, mock_send_text_batches) -> None:
        mock_send_text_batches.return_value = [{"message_id": 1}, {"message_id": 2}]
        menu_payload = {
            "source_name": "dr",
            "fetched_at": "2026-04-15T21:41:41+00:00",
            "display_language": "en",
            "entries": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            previous_state_dir = os.environ.get("STATE_STORAGE_DIR")
            previous_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            previous_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            os.environ["STATE_STORAGE_DIR"] = str(Path(temp_dir) / "state")
            os.environ["TELEGRAM_BOT_TOKEN"] = "test-bot-token"
            os.environ["TELEGRAM_CHAT_ID"] = "1234"
            menu_path = Path(temp_dir) / "2026-04-15T21-41-41Z.menu.json"
            batch_dir = Path(temp_dir) / "2026-04-15T21-41-41Z.menu"
            batch_dir.mkdir(parents=True, exist_ok=True)
            (batch_dir / "01.txt").write_text("Batch 1", encoding="utf-8")
            menu_path.write_text(json.dumps(menu_payload), encoding="utf-8")
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["telegram-send-digest", "--menu-json", str(menu_path)])
                self.assertEqual(exit_code, 0)
                output = json.loads(stdout.getvalue())
                self.assertEqual(output["sent_message_count"], 2)
                self.assertTrue(Path(output["state_path"]).exists())
            finally:
                if previous_state_dir is None:
                    os.environ.pop("STATE_STORAGE_DIR", None)
                else:
                    os.environ["STATE_STORAGE_DIR"] = previous_state_dir

                if previous_bot_token is None:
                    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                else:
                    os.environ["TELEGRAM_BOT_TOKEN"] = previous_bot_token

                if previous_chat_id is None:
                    os.environ.pop("TELEGRAM_CHAT_ID", None)
                else:
                    os.environ["TELEGRAM_CHAT_ID"] = previous_chat_id

    @patch("dr_digest.cli.send_message")
    def test_telegram_send_detail_sends_rendered_detail(self, mock_send_message) -> None:
        mock_send_message.return_value = {"message_id": 10}
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
            previous_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            previous_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            os.environ["DIGEST_STORAGE_DIR"] = str(Path(temp_dir) / "digests")
            os.environ["TELEGRAM_BOT_TOKEN"] = "test-bot-token"
            os.environ["TELEGRAM_CHAT_ID"] = "1234"
            menu_path = Path(temp_dir) / "menu.json"
            menu_path.write_text(json.dumps(menu_payload), encoding="utf-8")
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "telegram-send-detail",
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
                self.assertEqual(output["message_id"], 10)
                self.assertTrue(Path(output["detail_json_path"]).exists())
                self.assertTrue(Path(output["detail_text_path"]).exists())
            finally:
                if previous_digest_dir is None:
                    os.environ.pop("DIGEST_STORAGE_DIR", None)
                else:
                    os.environ["DIGEST_STORAGE_DIR"] = previous_digest_dir

                if previous_bot_token is None:
                    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                else:
                    os.environ["TELEGRAM_BOT_TOKEN"] = previous_bot_token

                if previous_chat_id is None:
                    os.environ.pop("TELEGRAM_CHAT_ID", None)
                else:
                    os.environ["TELEGRAM_CHAT_ID"] = previous_chat_id

    @patch("dr_digest.cli.send_message")
    @patch("dr_digest.cli.get_updates")
    def test_telegram_poll_once_handles_numeric_reply(self, mock_get_updates, mock_send_message) -> None:
        mock_get_updates.return_value = [
            {
                "update_id": 101,
                "message": {
                    "chat": {"id": 1234},
                    "text": "3",
                },
            }
        ]
        mock_send_message.return_value = {"message_id": 11}
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
            previous_state_dir = os.environ.get("STATE_STORAGE_DIR")
            previous_digest_dir = os.environ.get("DIGEST_STORAGE_DIR")
            previous_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            os.environ["STATE_STORAGE_DIR"] = str(Path(temp_dir) / "state")
            os.environ["DIGEST_STORAGE_DIR"] = str(Path(temp_dir) / "digests")
            os.environ["TELEGRAM_BOT_TOKEN"] = "test-bot-token"
            menu_path = Path(temp_dir) / "menu.json"
            menu_path.write_text(json.dumps(menu_payload), encoding="utf-8")
            state_dir = Path(temp_dir) / "state"
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "telegram_state.json").write_text(
                json.dumps(
                    {
                        "active_menu_json_path": str(menu_path),
                        "active_chat_id": "1234",
                    }
                ),
                encoding="utf-8",
            )
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = main(["telegram-poll-once", "--language", "en"])
                self.assertEqual(exit_code, 0)
                output = json.loads(stdout.getvalue())
                self.assertEqual(output["handled_numbers"], [3])
                self.assertTrue(Path(output["state_path"]).exists())
            finally:
                if previous_state_dir is None:
                    os.environ.pop("STATE_STORAGE_DIR", None)
                else:
                    os.environ["STATE_STORAGE_DIR"] = previous_state_dir

                if previous_digest_dir is None:
                    os.environ.pop("DIGEST_STORAGE_DIR", None)
                else:
                    os.environ["DIGEST_STORAGE_DIR"] = previous_digest_dir

                if previous_bot_token is None:
                    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                else:
                    os.environ["TELEGRAM_BOT_TOKEN"] = previous_bot_token


if __name__ == "__main__":
    unittest.main()
