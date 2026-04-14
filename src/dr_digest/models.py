from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class NewsItem:
    title: str
    link: str
    guid: str
    published_at: datetime | None = None
    image_url: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "title": self.title,
            "link": self.link,
            "guid": self.guid,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image_url": self.image_url,
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
