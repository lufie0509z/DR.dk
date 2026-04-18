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
    dr_article_fetch_count: int
    dr_translation_count: int
    raw_storage_dir: Path
    digest_storage_dir: Path
    state_storage_dir: Path
    digest_language: str
    digest_batch_size: int
    argos_packages_dir: Path
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    telegram_poll_timeout: int

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[2]
        load_dotenv(project_root / ".env")
        raw_storage_dir = Path(os.getenv("RAW_STORAGE_DIR", "var/raw"))
        digest_storage_dir = Path(os.getenv("DIGEST_STORAGE_DIR", "var/digests"))
        state_storage_dir = Path(os.getenv("STATE_STORAGE_DIR", "var/state"))
        return cls(
            project_root=project_root,
            dr_feed_url=os.getenv("DR_FEED_URL", "https://www.dr.dk/nyheder/service/feeds/senestenyt"),
            http_timeout_seconds=int(os.getenv("HTTP_TIMEOUT_SECONDS", "20")),
            dr_max_items=int(os.getenv("DR_MAX_ITEMS", "25")),
            dr_article_fetch_count=int(os.getenv("DR_ARTICLE_FETCH_COUNT", "5")),
            dr_translation_count=int(os.getenv("DR_TRANSLATION_COUNT", "0")),
            raw_storage_dir=raw_storage_dir,
            digest_storage_dir=digest_storage_dir,
            state_storage_dir=state_storage_dir,
            digest_language=os.getenv("DIGEST_LANGUAGE", "en").strip().lower(),
            digest_batch_size=int(os.getenv("DIGEST_BATCH_SIZE", "10")),
            argos_packages_dir=Path(os.getenv("ARGOS_PACKAGES_DIR", "var/argos/packages")),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
            telegram_poll_timeout=int(os.getenv("TELEGRAM_POLL_TIMEOUT", "10")),
        )

    @property
    def resolved_raw_storage_dir(self) -> Path:
        if self.raw_storage_dir.is_absolute():
            return self.raw_storage_dir
        return self.project_root / self.raw_storage_dir

    @property
    def resolved_argos_packages_dir(self) -> Path:
        if self.argos_packages_dir.is_absolute():
            return self.argos_packages_dir
        return self.project_root / self.argos_packages_dir

    @property
    def resolved_digest_storage_dir(self) -> Path:
        if self.digest_storage_dir.is_absolute():
            return self.digest_storage_dir
        return self.project_root / self.digest_storage_dir

    @property
    def resolved_state_storage_dir(self) -> Path:
        if self.state_storage_dir.is_absolute():
            return self.state_storage_dir
        return self.project_root / self.state_storage_dir

    def with_overrides(
        self,
        *,
        dr_feed_url: str | None = None,
        dr_max_items: int | None = None,
        dr_article_fetch_count: int | None = None,
        dr_translation_count: int | None = None,
    ) -> "Settings":
        return replace(
            self,
            dr_feed_url=dr_feed_url or self.dr_feed_url,
            dr_max_items=dr_max_items if dr_max_items is not None else self.dr_max_items,
            dr_article_fetch_count=(
                dr_article_fetch_count
                if dr_article_fetch_count is not None
                else self.dr_article_fetch_count
            ),
            dr_translation_count=(
                dr_translation_count
                if dr_translation_count is not None
                else self.dr_translation_count
            ),
        )
