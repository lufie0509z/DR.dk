from __future__ import annotations

import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from dr_digest.ingest.dr_rss import fetch_text, parse_dr_rss


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "dr_senestenyt.xml"


class ParseDrRssTests(unittest.TestCase):
    def test_parse_live_style_feed(self) -> None:
        xml_text = FIXTURE_PATH.read_text(encoding="utf-8")
        snapshot = parse_dr_rss(
            xml_text,
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            fetched_at=datetime(2026, 4, 14, 13, 0, tzinfo=timezone.utc),
            max_items=10,
        )

        self.assertEqual(snapshot.source_name, "dr")
        self.assertEqual(snapshot.channel_title, "Kort nyt | DR")
        self.assertEqual(snapshot.channel_description, "Nyheder fra sektionen Kort nyt")
        self.assertEqual(len(snapshot.items), 2)
        self.assertEqual(
            snapshot.items[0].title,
            "Udbrud af fugleinfluenza i fasanbesætning på Falster",
        )
        self.assertEqual(
            snapshot.items[1].image_url,
            "https://asset.dr.dk/imagescaler01/example.jpg&w=1200",
        )
        self.assertEqual(
            snapshot.items[0].published_at.isoformat(),
            "2026-04-14T12:48:00+00:00",
        )

    @patch("dr_digest.ingest.dr_rss.subprocess.run")
    @patch("dr_digest.ingest.dr_rss.urllib.request.urlopen")
    def test_fetch_text_falls_back_to_curl(self, mock_urlopen: MagicMock, mock_run: MagicMock) -> None:
        mock_urlopen.side_effect = urllib.error.URLError("network issue")
        mock_run.return_value = MagicMock(stdout=b"<rss />")

        xml_text = fetch_text("https://www.dr.dk/nyheder/service/feeds/senestenyt", timeout=10)

        self.assertEqual(xml_text, "<rss />")
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
