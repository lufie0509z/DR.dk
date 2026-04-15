from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .config import Settings
from .digest import apply_short_summaries
from .ingest import enrich_feed_snapshot
from .ingest.dr_rss import fetch_dr_feed_snapshot
from .storage.files import write_feed_snapshot, write_short_digest
from .translate import translate_feed_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DR digest utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest-dr", help="Fetch and persist the DR RSS feed.")
    ingest_parser.add_argument("--feed-url", help="Override the DR RSS feed URL.")
    ingest_parser.add_argument("--max-items", type=int, help="Limit the number of parsed items.")
    ingest_parser.add_argument(
        "--enrich-articles",
        action="store_true",
        help="Fetch article pages and enrich items with section, summary, and body text.",
    )
    ingest_parser.add_argument(
        "--article-limit",
        type=int,
        help="Limit how many article pages are fetched for enrichment.",
    )
    ingest_parser.add_argument(
        "--translate",
        action="store_true",
        help="Translate items to English and Chinese with Argos Translate.",
    )
    ingest_parser.add_argument(
        "--translation-limit",
        type=int,
        help="Limit how many items are translated.",
    )
    ingest_parser.add_argument(
        "--print-items",
        action="store_true",
        help="Print the normalized items JSON after saving.",
    )
    return parser


def run_ingest_dr(args: argparse.Namespace) -> int:
    settings = Settings.from_env().with_overrides(
        dr_feed_url=args.feed_url,
        dr_max_items=args.max_items,
        dr_article_fetch_count=args.article_limit,
        dr_translation_count=args.translation_limit,
    )
    snapshot, raw_xml = fetch_dr_feed_snapshot(
        feed_url=settings.dr_feed_url,
        timeout=settings.http_timeout_seconds,
        max_items=settings.dr_max_items,
        fetched_at=datetime.now(timezone.utc),
    )
    translated_item_count = 0
    article_html_by_guid: dict[str, str] | None = None
    if args.enrich_articles:
        article_html_by_guid = enrich_feed_snapshot(
            snapshot,
            timeout=settings.http_timeout_seconds,
            article_limit=settings.dr_article_fetch_count,
        )
    if args.translate:
        translated_item_count = translate_feed_snapshot(
            snapshot,
            packages_dir=settings.resolved_argos_packages_dir,
            translation_limit=settings.dr_translation_count,
        )
    short_summary_count = apply_short_summaries(snapshot)
    artifacts = write_feed_snapshot(
        snapshot=snapshot,
        raw_xml=raw_xml,
        base_dir=settings.resolved_raw_storage_dir,
        article_html_by_guid=article_html_by_guid,
    )
    short_digest_path = write_short_digest(
        snapshot=snapshot,
        base_dir=settings.resolved_digest_storage_dir,
    )
    artifacts.short_digest_path = short_digest_path

    result = {
        "source": snapshot.source_name,
        "feed_url": snapshot.source_url,
        "channel_title": snapshot.channel_title,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "item_count": len(snapshot.items),
        "enriched_item_count": sum(1 for item in snapshot.items if item.body_text),
        "translated_item_count": translated_item_count,
        "short_summary_count": short_summary_count,
        "feed_xml_path": artifacts.feed_xml_path,
        "items_json_path": artifacts.items_json_path,
        "short_digest_path": artifacts.short_digest_path,
        "headlines": [item.title for item in snapshot.items[:5]],
    }
    if artifacts.article_html_dir:
        result["article_html_dir"] = artifacts.article_html_dir
        result["article_html_count"] = artifacts.article_html_count
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.print_items:
        print()
        print(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "ingest-dr":
        return run_ingest_dr(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2
