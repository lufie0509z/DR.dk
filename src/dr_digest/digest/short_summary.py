from __future__ import annotations

import re

from ..models import FeedSnapshot, LocalizedNewsItem, NewsItem

_WHITESPACE_RE = re.compile(r"\s+")
_FIRST_SENTENCE_RE = re.compile(r"^.*?[.!?。！？]")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return _WHITESPACE_RE.sub(" ", value).strip()


def clip_text(text: str, limit: int = 220) -> str:
    if len(text) <= limit:
        return text
    clipped = text[: limit - 3].rsplit(" ", 1)[0].strip()
    return (clipped or text[: limit - 3]).rstrip() + "..."


def first_sentence(text: str) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return ""
    match = _FIRST_SENTENCE_RE.match(normalized)
    if match:
        return clip_text(match.group(0).strip())
    return clip_text(normalized)


def fallback_short_summary(title: str) -> str:
    title = normalize_text(title)
    if not title:
        return ""
    return clip_text(f"DR reports: {title}.")


def build_short_summary(summary: str, body_text: str, title: str) -> str:
    summary_sentence = first_sentence(summary)
    if summary_sentence:
        return summary_sentence

    body_sentence = first_sentence(body_text)
    if body_sentence:
        return body_sentence

    return fallback_short_summary(title)


def apply_localized_short_summary(item: LocalizedNewsItem) -> None:
    item.short_summary = build_short_summary(
        summary=item.summary,
        body_text=item.body_text,
        title=item.title,
    )


def apply_item_short_summary(item: NewsItem) -> None:
    item.short_summary = build_short_summary(
        summary=item.summary,
        body_text=item.body_text,
        title=item.title,
    )
    if item.translations:
        if item.translations.en:
            apply_localized_short_summary(item.translations.en)
        if item.translations.zh:
            apply_localized_short_summary(item.translations.zh)


def apply_short_summaries(snapshot: FeedSnapshot) -> int:
    count = 0
    for item in snapshot.items:
        apply_item_short_summary(item)
        if item.short_summary:
            count += 1
    return count
