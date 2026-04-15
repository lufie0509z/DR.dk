from __future__ import annotations

import json
import re
from pathlib import Path

from ..models import FeedSnapshot, IngestArtifacts


def _article_stem(guid: str, index: int) -> str:
    suffix = guid.rsplit(":", 1)[-1] if guid else f"item-{index:02d}"
    suffix = re.sub(r"[^A-Za-z0-9._-]+", "-", suffix).strip("-")
    return f"{index:02d}-{suffix or f'item-{index:02d}'}"


def write_feed_snapshot(
    snapshot: FeedSnapshot,
    raw_xml: str,
    base_dir: Path,
    article_html_by_guid: dict[str, str] | None = None,
) -> IngestArtifacts:
    stamp = snapshot.fetched_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    day_dir = base_dir / snapshot.source_name / snapshot.fetched_at.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    xml_path = day_dir / f"{stamp}.feed.xml"
    items_path = day_dir / f"{stamp}.items.json"
    article_dir: Path | None = None

    if article_html_by_guid:
        article_dir = day_dir / f"{stamp}.articles"
        article_dir.mkdir(parents=True, exist_ok=True)
        for index, item in enumerate(snapshot.items, start=1):
            html_text = article_html_by_guid.get(item.guid)
            if not html_text:
                continue
            html_path = article_dir / f"{_article_stem(item.guid, index)}.article.html"
            html_path.write_text(html_text, encoding="utf-8")
            item.article_html_path = str(html_path)

    xml_path.write_text(raw_xml, encoding="utf-8")
    items_path.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return IngestArtifacts(
        feed_xml_path=str(xml_path),
        items_json_path=str(items_path),
        article_html_dir=str(article_dir) if article_dir else None,
        article_html_count=len(article_html_by_guid or {}),
    )


def write_short_digest(snapshot: FeedSnapshot, base_dir: Path) -> str:
    stamp = snapshot.fetched_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    day_dir = base_dir / snapshot.source_name / snapshot.fetched_at.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    digest_path = day_dir / f"{stamp}.short.json"
    payload = {
        "source_name": snapshot.source_name,
        "source_url": snapshot.source_url,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "item_count": len(snapshot.items),
        "items": [
            {
                "number": index,
                "guid": item.guid,
                "title": item.title,
                "link": item.link,
                "section": item.section,
                "short_summary": item.short_summary,
                "translations": (
                    {
                        "en": (
                            {
                                "title": item.translations.en.title,
                                "short_summary": item.translations.en.short_summary,
                            }
                            if item.translations and item.translations.en
                            else None
                        ),
                        "zh": (
                            {
                                "title": item.translations.zh.title,
                                "short_summary": item.translations.zh.short_summary,
                            }
                            if item.translations and item.translations.zh
                            else None
                        ),
                    }
                    if item.translations
                    else None
                ),
            }
            for index, item in enumerate(snapshot.items, start=1)
        ],
    }
    digest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return str(digest_path)
