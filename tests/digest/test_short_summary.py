from __future__ import annotations

import unittest
from datetime import datetime

from dr_digest.digest.short_summary import apply_short_summaries, build_short_summary
from dr_digest.models import (
    ArticleTranslations,
    FeedSnapshot,
    LocalizedNewsItem,
    NewsItem,
)


class ShortSummaryTests(unittest.TestCase):
    def test_build_short_summary_prefers_existing_summary(self) -> None:
        summary = build_short_summary(
            summary="This is the short summary. Another sentence.",
            body_text="Longer body text.",
            title="Title",
        )
        self.assertEqual(summary, "This is the short summary.")

    def test_build_short_summary_falls_back_to_body_then_title(self) -> None:
        body_summary = build_short_summary(
            summary="",
            body_text="First sentence from body. Second sentence from body.",
            title="Title",
        )
        title_summary = build_short_summary(
            summary="",
            body_text="",
            title="Fallback title",
        )
        self.assertEqual(body_summary, "First sentence from body.")
        self.assertEqual(title_summary, "DR reports: Fallback title.")

    def test_apply_short_summaries_updates_source_and_translations(self) -> None:
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 14, 13, 5),
            items=[
                NewsItem(
                    title="Original title",
                    link="https://www.dr.dk/nyheder/example",
                    guid="urn:example",
                    summary="Original summary. More detail.",
                    translations=ArticleTranslations(
                        en=LocalizedNewsItem(
                            title="Translated title",
                            summary="Translated summary. More detail.",
                        ),
                        zh=LocalizedNewsItem(
                            title="翻译标题",
                            summary="翻译摘要。更多细节。",
                        ),
                    ),
                )
            ],
        )

        count = apply_short_summaries(snapshot)

        self.assertEqual(count, 1)
        self.assertEqual(snapshot.items[0].short_summary, "Original summary.")
        self.assertEqual(snapshot.items[0].translations.en.short_summary, "Translated summary.")
        self.assertEqual(snapshot.items[0].translations.zh.short_summary, "翻译摘要。")


if __name__ == "__main__":
    unittest.main()
