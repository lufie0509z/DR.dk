from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from dr_digest.models import FeedSnapshot, NewsItem
from dr_digest.translate.argos_translate import (
    configure_packages_dir,
    ensure_language_pairs,
    translate_feed_snapshot,
    translate_item,
)


class FakeArgosTranslate:
    @staticmethod
    def translate(text: str, from_code: str, to_code: str) -> str:
        return f"{to_code}:{text}"


class FakeInstalledPackage:
    def __init__(self, from_code: str, to_code: str) -> None:
        self.from_code = from_code
        self.to_code = to_code


class FakeArgosPackage:
    def __init__(self) -> None:
        self.calls: list[object] = []

    def get_installed_packages(self, path=None):
        self.calls.append(path)
        return [FakeInstalledPackage("da", "en"), FakeInstalledPackage("en", "zh")]


class ArgosTranslateTests(unittest.TestCase):
    def test_configure_packages_dir_sets_env_and_creates_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir) / "argos" / "packages"
            result = configure_packages_dir(packages_dir)

            self.assertEqual(result, packages_dir)
            self.assertTrue(packages_dir.exists())

    def test_translate_item_builds_bilingual_translations(self) -> None:
        item = NewsItem(
            title="Overskrift",
            link="https://www.dr.dk/nyheder/example",
            guid="urn:example",
            section="Kort nyt",
            section_path=["Nyheder", "Kort nyt"],
            summary="Kort resume",
            body_text="Brødtekst",
        )

        translations = translate_item(item, FakeArgosTranslate())

        self.assertEqual(translations.en.title, "en:Overskrift")
        self.assertEqual(translations.zh.title, "zh:Overskrift")
        self.assertEqual(translations.en.section_path, ["en:Nyheder", "en:Kort nyt"])
        self.assertEqual(translations.zh.body_text, "zh:Brødtekst")

    def test_ensure_language_pairs_passes_iterable_path(self) -> None:
        fake_package = FakeArgosPackage()
        with tempfile.TemporaryDirectory() as temp_dir:
            packages_dir = Path(temp_dir) / "argos" / "packages"
            packages_dir.mkdir(parents=True, exist_ok=True)

            ensure_language_pairs(fake_package, packages_dir)

        self.assertEqual(fake_package.calls, [[packages_dir]])

    @patch("dr_digest.translate.argos_translate.ensure_language_pairs")
    @patch("dr_digest.translate.argos_translate.load_argos_modules")
    def test_translate_feed_snapshot_applies_translations(
        self,
        mock_load_argos_modules,
        mock_ensure_language_pairs,
    ) -> None:
        mock_load_argos_modules.return_value = (object(), FakeArgosTranslate())
        snapshot = FeedSnapshot(
            source_name="dr",
            source_url="https://www.dr.dk/nyheder/service/feeds/senestenyt",
            channel_title="Kort nyt | DR",
            channel_description="Nyheder fra sektionen Kort nyt",
            fetched_at=datetime(2026, 4, 14, 13, 5, tzinfo=timezone.utc),
            items=[
                NewsItem(
                    title="Overskrift",
                    link="https://www.dr.dk/nyheder/example",
                    guid="urn:example",
                )
            ],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            translated_count = translate_feed_snapshot(
                snapshot,
                packages_dir=Path(temp_dir) / "argos" / "packages",
                translation_limit=1,
            )

        self.assertEqual(translated_count, 1)
        self.assertEqual(snapshot.items[0].translations.en.title, "en:Overskrift")
        mock_ensure_language_pairs.assert_called_once()


if __name__ == "__main__":
    unittest.main()
