from __future__ import annotations

import json
from pathlib import Path

from ..models import FeedSnapshot, IngestArtifacts


def write_feed_snapshot(snapshot: FeedSnapshot, raw_xml: str, base_dir: Path) -> IngestArtifacts:
    stamp = snapshot.fetched_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    day_dir = base_dir / snapshot.source_name / snapshot.fetched_at.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    xml_path = day_dir / f"{stamp}.feed.xml"
    items_path = day_dir / f"{stamp}.items.json"

    xml_path.write_text(raw_xml, encoding="utf-8")
    items_path.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return IngestArtifacts(
        feed_xml_path=str(xml_path),
        items_json_path=str(items_path),
    )
