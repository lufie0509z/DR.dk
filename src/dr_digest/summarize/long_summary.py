from __future__ import annotations

from datetime import datetime


def _resolve_language_fields(entry: dict[str, object], language: str) -> tuple[str, str, str]:
    translations = entry.get("translations") or {}
    localized = translations.get(language) or {}

    if language in {"en", "zh"} and localized:
        return (
            str(localized.get("title") or entry.get("title") or ""),
            str(localized.get("summary") or entry.get("short_summary") or ""),
            str(localized.get("body_text") or entry.get("short_summary") or ""),
        )

    return (
        str(entry.get("title") or ""),
        str(entry.get("summary") or entry.get("short_summary") or ""),
        str(entry.get("body_text") or entry.get("short_summary") or ""),
    )


def build_detail_payload(
    entry: dict[str, object],
    *,
    language: str,
    fetched_at: str,
) -> dict[str, object]:
    display_title, display_summary, display_body_text = _resolve_language_fields(entry, language)
    return {
        "number": entry["number"],
        "guid": entry["guid"],
        "link": entry["link"],
        "display_language": language,
        "fetched_at": fetched_at,
        "title": display_title,
        "summary": display_summary,
        "body_text": display_body_text,
        "section": entry.get("section"),
        "published_at": entry.get("published_at"),
    }


def render_detail_text(detail_payload: dict[str, object]) -> str:
    header = f"Story {detail_payload['number']}: {detail_payload['title']}"
    lines = [header]

    section = str(detail_payload.get("section") or "").strip()
    if section:
        lines.append(f"Section: {section}")

    published_at = str(detail_payload.get("published_at") or "").strip()
    if published_at:
        lines.append(f"Published: {published_at}")

    lines.append("")

    summary = str(detail_payload.get("summary") or "").strip()
    if summary:
        lines.append(summary)
        lines.append("")

    body_text = str(detail_payload.get("body_text") or "").strip()
    if body_text:
        body_for_output = body_text
        if summary and body_text.startswith(summary):
            body_for_output = body_text[len(summary) :].lstrip()
        if body_for_output:
            lines.append(body_for_output)
            lines.append("")

    lines.append(f"Source: {detail_payload['link']}")
    return "\n".join(lines).strip()
