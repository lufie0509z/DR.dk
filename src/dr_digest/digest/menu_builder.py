from __future__ import annotations

from ..models import FeedSnapshot, NewsItem

DEFAULT_DIGEST_TITLE = "DR Daily Digest"


def resolve_display_text(item: NewsItem, language: str) -> tuple[str, str]:
    if language == "en" and item.translations and item.translations.en:
        return item.translations.en.title or item.title, item.translations.en.short_summary or item.short_summary
    if language == "zh" and item.translations and item.translations.zh:
        return item.translations.zh.title or item.title, item.translations.zh.short_summary or item.short_summary
    return item.title, item.short_summary


def build_digest_entries(snapshot: FeedSnapshot, language: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for number, item in enumerate(snapshot.items, start=1):
        display_title, display_short_summary = resolve_display_text(item, language)
        entries.append(
            {
                "number": number,
                "guid": item.guid,
                "link": item.link,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "section": item.section,
                "title": item.title,
                "short_summary": item.short_summary,
                "display_language": language,
                "display_title": display_title,
                "display_short_summary": display_short_summary,
                "translations": item.translations.to_dict() if item.translations else None,
            }
        )
    return entries


def chunk_entries(entries: list[dict[str, object]], batch_size: int) -> list[list[dict[str, object]]]:
    if batch_size <= 0:
        raise ValueError("Digest batch size must be greater than zero.")
    return [entries[index : index + batch_size] for index in range(0, len(entries), batch_size)]


def render_batch_text(
    entries: list[dict[str, object]],
    *,
    digest_date: str,
    batch_number: int,
    batch_count: int,
) -> str:
    header = f"{DEFAULT_DIGEST_TITLE} | {digest_date} | {batch_number}/{batch_count}"
    lines = [header, ""]
    for entry in entries:
        lines.append(f"{entry['number']}. {entry['display_title']}")
        short_summary = str(entry.get("display_short_summary") or "").strip()
        if short_summary:
            lines.append(f"   {short_summary}")
        lines.append("")
    return "\n".join(lines).strip()


def build_daily_digest(snapshot: FeedSnapshot, *, language: str, batch_size: int) -> dict[str, object]:
    entries = build_digest_entries(snapshot, language)
    batches = chunk_entries(entries, batch_size=batch_size)
    digest_date = snapshot.fetched_at.strftime("%Y-%m-%d")
    batch_payloads: list[dict[str, object]] = []

    for index, batch_entries in enumerate(batches, start=1):
        batch_payloads.append(
            {
                "batch_number": index,
                "batch_count": len(batches),
                "start_number": batch_entries[0]["number"] if batch_entries else None,
                "end_number": batch_entries[-1]["number"] if batch_entries else None,
                "items": [entry["number"] for entry in batch_entries],
                "text": render_batch_text(
                    batch_entries,
                    digest_date=digest_date,
                    batch_number=index,
                    batch_count=len(batches),
                ),
            }
        )

    return {
        "source_name": snapshot.source_name,
        "source_url": snapshot.source_url,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "display_language": language,
        "batch_size": batch_size,
        "item_count": len(entries),
        "batch_count": len(batch_payloads),
        "entries": entries,
        "batches": batch_payloads,
    }
