from __future__ import annotations

import json
import re
from datetime import datetime

from ..models import ArticleEnrichment, FeedSnapshot
from .dr_rss import clean_text, fetch_text

_META_DESCRIPTION_RE = re.compile(
    r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\'](.*?)["\']',
    re.IGNORECASE | re.DOTALL,
)
_NEXT_DATA_RE = re.compile(
    r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
_SCRIPT_RE = re.compile(r"<script(?:\s[^>]*)?>(.*?)</script>", re.IGNORECASE | re.DOTALL)
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str | None) -> str:
    return _WHITESPACE_RE.sub(" ", clean_text(value)).strip()


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def extract_meta_description(html_text: str) -> str:
    match = _META_DESCRIPTION_RE.search(html_text)
    if not match:
        return ""
    return normalize_text(match.group(1))


def extract_next_data_payload(html_text: str) -> dict:
    match = _NEXT_DATA_RE.search(html_text)
    if not match:
        for script_body in _SCRIPT_RE.findall(html_text):
            candidate = script_body.strip()
            if not candidate.startswith("{"):
                continue
            if '"pageProps"' not in candidate or '"resource"' not in candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        raise ValueError("The DR article page did not include a structured page payload.")
    return json.loads(match.group(1))


def extract_resource(payload: dict) -> dict:
    page_props = payload.get("props", {}).get("pageProps", {})
    resource = page_props.get("resource")
    if isinstance(resource, dict):
        return resource
    view_props = page_props.get("viewProps") or {}
    resource = view_props.get("resource")
    if isinstance(resource, dict):
        return resource
    raise ValueError("The DR page payload did not include a resource object.")


def flatten_inline_text(node: object) -> str:
    if isinstance(node, dict):
        node_type = node.get("type")
        if node_type == "Text":
            return node.get("text", "")
        if "body" in node:
            return "".join(flatten_inline_text(part) for part in node.get("body", []))
        return ""
    if isinstance(node, list):
        return "".join(flatten_inline_text(part) for part in node)
    return ""


def extract_body_text(resource: dict) -> str:
    paragraphs: list[str] = []
    for component in resource.get("body", []):
        text = normalize_text(flatten_inline_text(component))
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def extract_section_path(resource: dict) -> list[str]:
    site = resource.get("site") or {}
    path = [normalize_text(parent.get("title")) for parent in site.get("parentSites", []) if parent.get("title")]
    site_title = normalize_text(site.get("title"))
    if site_title:
        path.append(site_title)
    return path


def extract_authors(resource: dict) -> list[str]:
    authors: list[str] = []
    for contribution in resource.get("contributions", []):
        agent = contribution.get("agent") or {}
        author_name = normalize_text(agent.get("name"))
        if author_name:
            authors.append(author_name)
    return authors


def extract_article_image_url(resource: dict) -> str | None:
    head = resource.get("head") or []
    for component in head:
        if component.get("type") != "ImageComponent":
            continue
        default_image = ((component.get("image") or {}).get("default") or {})
        for key in ("managedUrl", "url"):
            image_url = default_image.get(key)
            if image_url:
                return image_url

    teaser_image = ((resource.get("teaserImage") or {}).get("default") or {})
    for key in ("managedUrl", "url"):
        image_url = teaser_image.get(key)
        if image_url:
            return image_url
    return None


def parse_dr_article_html(html_text: str) -> ArticleEnrichment:
    payload = extract_next_data_payload(html_text)
    resource = extract_resource(payload)

    body_text = extract_body_text(resource)
    summary = normalize_text(resource.get("summary")) or extract_meta_description(html_text)
    if not summary and body_text:
        summary = body_text.split("\n\n", 1)[0]

    section_path = extract_section_path(resource)
    section = section_path[-1] if section_path else None

    return ArticleEnrichment(
        section=section,
        section_path=section_path,
        summary=summary,
        body_text=body_text,
        authors=extract_authors(resource),
        article_image_url=extract_article_image_url(resource),
        published_at=parse_iso_datetime(resource.get("startDate")),
    )


def enrich_feed_snapshot(
    snapshot: FeedSnapshot,
    *,
    timeout: int,
    article_limit: int,
) -> dict[str, str]:
    article_html_by_guid: dict[str, str] = {}
    for item in snapshot.items[: max(0, article_limit)]:
        try:
            html_text = fetch_text(item.link, timeout=timeout)
            enrichment = parse_dr_article_html(html_text)
        except Exception:
            continue
        item.apply_enrichment(enrichment)
        article_html_by_guid[item.guid] = html_text
    return article_html_by_guid
