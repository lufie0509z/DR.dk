from __future__ import annotations

import unittest
from datetime import datetime

from dr_digest.digest.menu_builder import build_daily_digest
from dr_digest.models import (
    ArticleTranslations,
    FeedSnapshot,
    LocalizedNewsItem,
    NewsItem,
)


class MenuBuilderTests(unittest.TestCase):
    def test_build_daily_digest_uses_localized_display_language(self) -> None:
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 15, 7, 30),
            items=[
                NewsItem(
                    title="Dansk titel",
                    link="https://www.dr.dk/nyheder/example-1",
                    guid="urn:example:1",
                    short_summary="Dansk kort resume.",
                    translations=ArticleTranslations(
                        en=LocalizedNewsItem(
                            title="English title",
                            short_summary="English short summary.",
                        )
                    ),
                )
            ],
        )

        digest = build_daily_digest(snapshot, language="en", batch_size=10)

        self.assertEqual(digest["item_count"], 1)
        self.assertEqual(digest["entries"][0]["display_title"], "English title")
        self.assertEqual(digest["entries"][0]["display_short_summary"], "English short summary.")
        self.assertEqual(digest["batch_count"], 1)
        self.assertIn("1. English title", digest["batches"][0]["text"])

    def test_build_daily_digest_batches_entries(self) -> None:
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 15, 7, 30),
            items=[
                NewsItem(
                    title=f"Title {index}",
                    link=f"https://www.dr.dk/nyheder/example-{index}",
                    guid=f"urn:example:{index}",
                    short_summary=f"Short summary {index}.",
                )
                for index in range(1, 4)
            ],
        )

        digest = build_daily_digest(snapshot, language="en", batch_size=2)

        self.assertEqual(digest["batch_count"], 2)
        self.assertEqual(digest["batches"][0]["items"], [1, 2])
        self.assertEqual(digest["batches"][1]["items"], [3])


if __name__ == "__main__":
    unittest.main()
