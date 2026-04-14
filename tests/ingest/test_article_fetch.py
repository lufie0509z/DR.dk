from __future__ import annotations

import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from dr_digest.ingest.article_fetch import enrich_feed_snapshot, parse_dr_article_html
from dr_digest.models import FeedSnapshot, NewsItem


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "dr_article.html"
SCRIPT_RE = re.compile(
    r'(<script id="__NEXT_DATA__" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)


class ArticleFetchTests(unittest.TestCase):
    def test_parse_dr_article_html_extracts_structured_fields(self) -> None:
        html_text = FIXTURE_PATH.read_text(encoding="utf-8")
        enrichment = parse_dr_article_html(html_text)

        self.assertEqual(enrichment.section, "Kort nyt")
        self.assertEqual(enrichment.section_path, ["Nyheder", "Kort nyt"])
        self.assertEqual(enrichment.authors, ["Sarah Yasin"])
        self.assertEqual(
            enrichment.summary,
            "Den italienske premierminister, Giorgia Meloni, giver sin fulde støtte til pave Leo.",
        )
        self.assertIn("Donald Trump", enrichment.body_text)
        self.assertEqual(
            enrichment.article_image_url,
            "https://asset.dr.dk/drdk/umbraco-images/c5ag1bzg/20260412-182857-6.jpg",
        )
        self.assertEqual(enrichment.published_at.isoformat(), "2026-04-14T12:44:00+00:00")

    def test_parse_dr_article_html_accepts_plain_json_script(self) -> None:
        html_text = FIXTURE_PATH.read_text(encoding="utf-8").replace(' id="__NEXT_DATA__"', "", 1)
        enrichment = parse_dr_article_html(html_text)

        self.assertEqual(enrichment.section, "Kort nyt")
        self.assertIn("Donald Trump", enrichment.body_text)

    def test_parse_dr_article_html_accepts_view_props_resource(self) -> None:
        original_html = FIXTURE_PATH.read_text(encoding="utf-8")
        match = SCRIPT_RE.search(original_html)
        payload = json.loads(match.group(2))
        resource = payload["props"]["pageProps"].pop("resource")
        payload["props"]["pageProps"]["viewProps"] = {"resource": resource}
        html_text = SCRIPT_RE.sub(
            lambda matched: f"{matched.group(1)}{json.dumps(payload)}{matched.group(3)}",
            original_html,
            count=1,
        )

        enrichment = parse_dr_article_html(html_text)

        self.assertEqual(enrichment.section_path, ["Nyheder", "Kort nyt"])

    @patch("dr_digest.ingest.article_fetch.fetch_text")
    def test_enrich_feed_snapshot_updates_items_and_returns_html(self, mock_fetch_text) -> None:
        html_text = FIXTURE_PATH.read_text(encoding="utf-8")
        mock_fetch_text.return_value = html_text
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

        article_html_by_guid = enrich_feed_snapshot(snapshot, timeout=10, article_limit=1)

        self.assertIn("urn:dr:umbraco:article:test-guid", article_html_by_guid)
        self.assertEqual(snapshot.items[0].section, "Kort nyt")
        self.assertIn("Donald Trump", snapshot.items[0].body_text)


if __name__ == "__main__":
    unittest.main()
