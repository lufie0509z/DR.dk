from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dr_digest.publish.telegram import build_api_url, send_text_batches


class TelegramPublishTests(unittest.TestCase):
    def test_build_api_url(self) -> None:
        url = build_api_url("token123", "sendMessage")
        self.assertEqual(url, "https://api.telegram.org/bottoken123/sendMessage")

    @patch("dr_digest.publish.telegram.send_message")
    def test_send_text_batches_reads_files_in_order(self, mock_send_message) -> None:
        mock_send_message.side_effect = [{"message_id": 1}, {"message_id": 2}]
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_dir = Path(temp_dir)
            (batch_dir / "02.txt").write_text("Second", encoding="utf-8")
            (batch_dir / "01.txt").write_text("First", encoding="utf-8")

            messages = send_text_batches("token", "chat-id", batch_dir)

        self.assertEqual(len(messages), 2)
        self.assertEqual(mock_send_message.call_args_list[0].args[2], "First")
        self.assertEqual(mock_send_message.call_args_list[1].args[2], "Second")


if __name__ == "__main__":
    unittest.main()
