from __future__ import annotations

import unittest

from dr_digest.summarize.long_summary import build_detail_payload, render_detail_text


class LongSummaryTests(unittest.TestCase):
    def test_build_detail_payload_prefers_localized_content(self) -> None:
        entry = {
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

        payload = build_detail_payload(entry, language="en", fetched_at="2026-04-15T21:41:41+00:00")

        self.assertEqual(payload["title"], "English title")
        self.assertEqual(payload["summary"], "English summary")
        self.assertEqual(payload["body_text"], "English body text")

    def test_render_detail_text_contains_key_sections(self) -> None:
        text = render_detail_text(
            {
                "number": 3,
                "guid": "urn:example:3",
                "title": "English title",
                "summary": "English summary",
                "body_text": "English summary\n\nEnglish body text",
                "section": "Kort nyt",
                "published_at": "2026-04-15T12:00:00+00:00",
                "link": "https://www.dr.dk/nyheder/example-3",
            }
        )

        self.assertIn("Story 3: English title", text)
        self.assertIn("Section: Kort nyt", text)
        self.assertIn("Source: https://www.dr.dk/nyheder/example-3", text)
        self.assertEqual(text.count("English summary"), 1)


if __name__ == "__main__":
    unittest.main()
