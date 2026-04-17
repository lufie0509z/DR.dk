from __future__ import annotations

import os
from pathlib import Path

from ..models import ArticleTranslations, FeedSnapshot, LocalizedNewsItem, NewsItem

SOURCE_LANGUAGE = "da"
ENGLISH_LANGUAGE = "en"
CHINESE_LANGUAGE = "zh"
REQUIRED_LANGUAGE_PAIRS = [
    (SOURCE_LANGUAGE, ENGLISH_LANGUAGE),
    (ENGLISH_LANGUAGE, CHINESE_LANGUAGE),
]


def configure_packages_dir(packages_dir: Path) -> Path:
    packages_dir.mkdir(parents=True, exist_ok=True)
    os.environ["ARGOS_PACKAGES_DIR"] = str(packages_dir)
    return packages_dir


def load_argos_modules() -> tuple[object, object]:
    try:
        import argostranslate.package as argos_package
        import argostranslate.translate as argos_translate
    except ImportError as exc:
        raise RuntimeError(
            "argostranslate is not installed. Run `python3 -m pip install -e .` "
            "or install project dependencies first."
        ) from exc
    return argos_package, argos_translate


def ensure_language_pairs(argos_package: object, packages_dir: Path) -> None:
    installed_pairs = {
        (pkg.from_code, pkg.to_code)
        for pkg in argos_package.get_installed_packages(path=[packages_dir])
    }
    missing_pairs = [pair for pair in REQUIRED_LANGUAGE_PAIRS if pair not in installed_pairs]
    if not missing_pairs:
        return

    argos_package.update_package_index()
    for from_code, to_code in missing_pairs:
        installed = argos_package.install_package_for_language_pair(from_code, to_code)
        if not installed:
            raise RuntimeError(
                f"Could not install the Argos Translate model for {from_code} -> {to_code}."
            )


def translate_text(argos_translate: object, text: str, *, to_code: str) -> str:
    if not text:
        return ""
    return argos_translate.translate(text, SOURCE_LANGUAGE, to_code)


def translate_item(item: NewsItem, argos_translate: object) -> ArticleTranslations:
    return ArticleTranslations(
        en=LocalizedNewsItem(
            title=translate_text(argos_translate, item.title, to_code=ENGLISH_LANGUAGE),
            section=translate_text(argos_translate, item.section or "", to_code=ENGLISH_LANGUAGE),
            section_path=[
                translate_text(argos_translate, part, to_code=ENGLISH_LANGUAGE)
                for part in item.section_path
            ],
            summary=translate_text(argos_translate, item.summary, to_code=ENGLISH_LANGUAGE),
            body_text=translate_text(argos_translate, item.body_text, to_code=ENGLISH_LANGUAGE),
        ),
        zh=LocalizedNewsItem(
            title=translate_text(argos_translate, item.title, to_code=CHINESE_LANGUAGE),
            section=translate_text(argos_translate, item.section or "", to_code=CHINESE_LANGUAGE),
            section_path=[
                translate_text(argos_translate, part, to_code=CHINESE_LANGUAGE)
                for part in item.section_path
            ],
            summary=translate_text(argos_translate, item.summary, to_code=CHINESE_LANGUAGE),
            body_text=translate_text(argos_translate, item.body_text, to_code=CHINESE_LANGUAGE),
        ),
    )


def translate_feed_snapshot(
    snapshot: FeedSnapshot,
    *,
    packages_dir: Path,
    translation_limit: int,
) -> int:
    configured_packages_dir = configure_packages_dir(packages_dir)
    argos_package, argos_translate = load_argos_modules()
    ensure_language_pairs(argos_package, configured_packages_dir)

    effective_limit = len(snapshot.items) if translation_limit <= 0 else min(translation_limit, len(snapshot.items))

    translated_count = 0
    for item in snapshot.items[:effective_limit]:
        try:
            translations = translate_item(item, argos_translate)
        except Exception:
            continue
        item.apply_translations(translations)
        translated_count += 1
    return translated_count
