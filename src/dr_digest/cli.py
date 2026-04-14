from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .config import Settings
from .ingest.dr_rss import fetch_dr_feed_snapshot
from .storage.files import write_feed_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DR digest utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest-dr", help="Fetch and persist the DR RSS feed.")
    ingest_parser.add_argument("--feed-url", help="Override the DR RSS feed URL.")
    ingest_parser.add_argument("--max-items", type=int, help="Limit the number of parsed items.")
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
    )
    snapshot, raw_xml = fetch_dr_feed_snapshot(
        feed_url=settings.dr_feed_url,
        timeout=settings.http_timeout_seconds,
        max_items=settings.dr_max_items,
        fetched_at=datetime.now(timezone.utc),
    )
    artifacts = write_feed_snapshot(
        snapshot=snapshot,
        raw_xml=raw_xml,
        base_dir=settings.resolved_raw_storage_dir,
    )

    result = {
        "source": snapshot.source_name,
        "feed_url": snapshot.source_url,
        "channel_title": snapshot.channel_title,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "item_count": len(snapshot.items),
        "feed_xml_path": artifacts.feed_xml_path,
        "items_json_path": artifacts.items_json_path,
        "headlines": [item.title for item in snapshot.items[:5]],
    }
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
