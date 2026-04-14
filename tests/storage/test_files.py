from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dr_digest.models import FeedSnapshot, NewsItem
from dr_digest.storage.files import write_feed_snapshot


class WriteFeedSnapshotTests(unittest.TestCase):
    def test_writes_raw_xml_and_items_json(self) -> None:
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 14, 13, 5, tzinfo=timezone.utc),
            items=[
                NewsItem(
                    title="Headline",
                    link="https://www.dr.dk/nyheder/example",
                    guid="urn:example",
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = write_feed_snapshot(snapshot, "<rss />", Path(temp_dir))
            self.assertTrue(Path(artifacts.feed_xml_path).exists())
            self.assertTrue(Path(artifacts.items_json_path).exists())

            payload = json.loads(Path(artifacts.items_json_path).read_text(encoding="utf-8"))
            self.assertEqual(payload["source_name"], "dr")
            self.assertEqual(payload["item_count"], 1)
            self.assertEqual(payload["items"][0]["title"], "Headline")
            self.assertIsNone(payload["items"][0]["article_html_path"])

    def test_writes_article_html_when_enrichment_is_present(self) -> None:
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 14, 13, 5, tzinfo=timezone.utc),
            items=[
                NewsItem(
                    title="Headline",
                    link="https://www.dr.dk/nyheder/example",
                    guid="urn:dr:umbraco:article:test-guid",
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = write_feed_snapshot(
                snapshot,
                "<rss />",
                Path(temp_dir),
                article_html_by_guid={"urn:dr:umbraco:article:test-guid": "<html>article</html>"},
            )
            self.assertEqual(artifacts.article_html_count, 1)
            self.assertIsNotNone(artifacts.article_html_dir)
            self.assertTrue(Path(snapshot.items[0].article_html_path).exists())


if __name__ == "__main__":
    unittest.main()
