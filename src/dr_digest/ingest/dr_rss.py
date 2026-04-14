from __future__ import annotations

import html
import subprocess
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

from ..models import FeedSnapshot, NewsItem

DEFAULT_USER_AGENT = "dr-digest/0.1"
MEDIA_NAMESPACE = {"media": "http://search.yahoo.com/mrss/"}


def fetch_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except urllib.error.URLError:
        return fetch_text_with_curl(url, timeout)


def fetch_text_with_curl(url: str, timeout: int) -> str:
    completed = subprocess.run(
        [
            "curl",
            "--fail",
            "--silent",
            "--show-error",
            "--location",
            "--max-time",
            str(timeout),
            url,
        ],
        capture_output=True,
        check=True,
    )
    return completed.stdout.decode("utf-8", errors="replace")


def clean_text(value: str | None) -> str:
    return html.unescape((value or "").strip())


def parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None


def parse_dr_rss(xml_text: str, *, source_url: str, fetched_at: datetime, max_items: int) -> FeedSnapshot:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("The DR RSS document did not contain a channel element.")

    channel_title = clean_text(channel.findtext("title"))
    channel_description = clean_text(channel.findtext("description"))
    items: list[NewsItem] = []

    for item in channel.findall("item")[:max_items]:
        media_content = item.find("media:content", MEDIA_NAMESPACE)
        items.append(
            NewsItem(
                title=clean_text(item.findtext("title")),
                link=clean_text(item.findtext("link")),
                guid=clean_text(item.findtext("guid")),
                published_at=parse_published_at(item.findtext("pubDate")),
                image_url=media_content.attrib.get("url") if media_content is not None else None,
            )
        )

    normalized_items = [item for item in items if item.title and item.link and item.guid]
    return FeedSnapshot(
        source_name="dr",
        source_url=source_url,
        channel_title=channel_title,
        channel_description=channel_description,
        fetched_at=fetched_at,
        items=normalized_items,
    )


def fetch_dr_feed_snapshot(
    *,
    feed_url: str,
    timeout: int,
    max_items: int,
    fetched_at: datetime,
) -> tuple[FeedSnapshot, str]:
    raw_xml = fetch_text(feed_url, timeout=timeout)
    snapshot = parse_dr_rss(
        raw_xml,
        source_url=feed_url,
        fetched_at=fetched_at,
        max_items=max_items,
    )
    return snapshot, raw_xml
