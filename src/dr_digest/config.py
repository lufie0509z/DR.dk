from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(slots=True)
class Settings:
    project_root: Path
    dr_feed_url: str
    http_timeout_seconds: int
    dr_max_items: int
    raw_storage_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[2]
        load_dotenv(project_root / ".env")
        raw_storage_dir = Path(os.getenv("RAW_STORAGE_DIR", "var/raw"))
        return cls(
            project_root=project_root,
            dr_feed_url=os.getenv("DR_FEED_URL", "https://www.dr.dk/nyheder/service/feeds/senestenyt"),
            http_timeout_seconds=int(os.getenv("HTTP_TIMEOUT_SECONDS", "20")),
            dr_max_items=int(os.getenv("DR_MAX_ITEMS", "25")),
            raw_storage_dir=raw_storage_dir,
        )

    @property
    def resolved_raw_storage_dir(self) -> Path:
        if self.raw_storage_dir.is_absolute():
            return self.raw_storage_dir
        return self.project_root / self.raw_storage_dir

    def with_overrides(
        self,
        *,
        dr_feed_url: str | None = None,
        dr_max_items: int | None = None,
    ) -> "Settings":
        return replace(
            self,
            dr_feed_url=dr_feed_url or self.dr_feed_url,
            dr_max_items=dr_max_items if dr_max_items is not None else self.dr_max_items,
        )
