from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ArticleEnrichment:
    section: str | None = None
    section_path: list[str] = field(default_factory=list)
    summary: str = ""
    body_text: str = ""
    authors: list[str] = field(default_factory=list)
    article_image_url: str | None = None
    published_at: datetime | None = None


@dataclass(slots=True)
class LocalizedNewsItem:
    title: str = ""
    section: str = ""
    section_path: list[str] = field(default_factory=list)
    summary: str = ""
    body_text: str = ""
    short_summary: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "section": self.section,
            "section_path": self.section_path,
            "summary": self.summary,
            "body_text": self.body_text,
            "short_summary": self.short_summary,
        }


@dataclass(slots=True)
class ArticleTranslations:
    en: LocalizedNewsItem | None = None
    zh: LocalizedNewsItem | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "en": self.en.to_dict() if self.en else None,
            "zh": self.zh.to_dict() if self.zh else None,
        }


@dataclass(slots=True)
class NewsItem:
    title: str
    link: str
    guid: str
    published_at: datetime | None = None
    image_url: str | None = None
    section: str | None = None
    section_path: list[str] = field(default_factory=list)
    summary: str = ""
    body_text: str = ""
    short_summary: str = ""
    authors: list[str] = field(default_factory=list)
    article_image_url: str | None = None
    article_html_path: str | None = None
    translations: ArticleTranslations | None = None

    def apply_enrichment(self, enrichment: ArticleEnrichment) -> None:
        self.section = enrichment.section
        self.section_path = enrichment.section_path
        self.summary = enrichment.summary
        self.body_text = enrichment.body_text
        self.authors = enrichment.authors
        self.article_image_url = enrichment.article_image_url
        if enrichment.published_at is not None:
            self.published_at = enrichment.published_at

    def apply_translations(self, translations: ArticleTranslations) -> None:
        self.translations = translations

    def to_dict(self) -> dict[str, str | None]:
        return {
            "title": self.title,
            "link": self.link,
            "guid": self.guid,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image_url": self.image_url,
            "section": self.section,
            "section_path": self.section_path,
            "summary": self.summary,
            "body_text": self.body_text,
            "short_summary": self.short_summary,
            "authors": self.authors,
            "article_image_url": self.article_image_url,
            "article_html_path": self.article_html_path,
            "translations": self.translations.to_dict() if self.translations else None,
        }


@dataclass(slots=True)
class FeedSnapshot:
    source_name: str
    source_url: str
    channel_title: str
    channel_description: str
    fetched_at: datetime
    items: list[NewsItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "channel_title": self.channel_title,
            "channel_description": self.channel_description,
            "fetched_at": self.fetched_at.isoformat(),
            "item_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(slots=True)
class IngestArtifacts:
    feed_xml_path: str
    items_json_path: str
    article_html_dir: str | None = None
    article_html_count: int = 0
    short_digest_path: str | None = None
    menu_json_path: str | None = None
    menu_batch_dir: str | None = None
    menu_batch_count: int = 0
    detail_json_path: str | None = None
    detail_text_path: str | None = None
