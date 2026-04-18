from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TELEGRAM_API_BASE = "https://api.telegram.org"


def build_api_url(bot_token: str, method_name: str) -> str:
    return f"{TELEGRAM_API_BASE}/bot{bot_token}/{method_name}"


def post_json(url: str, payload: dict[str, object], timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        return post_json_with_curl(url, payload, timeout)


def post_json_with_curl(url: str, payload: dict[str, object], timeout: int) -> dict:
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
            "-H",
            "Content-Type: application/json",
            "-d",
            json.dumps(payload),
        ],
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout.decode("utf-8"))


def send_message(bot_token: str, chat_id: str, text: str, *, timeout: int = 30) -> dict:
    response = post_json(
        build_api_url(bot_token, "sendMessage"),
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=timeout,
    )
    if not response.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {response}")
    return response["result"]


def send_text_batches(bot_token: str, chat_id: str, batch_dir: Path, *, timeout: int = 30) -> list[dict]:
    messages: list[dict] = []
    for batch_path in sorted(batch_dir.glob("*.txt")):
        text = batch_path.read_text(encoding="utf-8").strip()
        messages.append(send_message(bot_token, chat_id, text, timeout=timeout))
    return messages


def get_updates(
    bot_token: str,
    *,
    offset: int | None = None,
    timeout: int = 10,
    allowed_updates: list[str] | None = None,
) -> list[dict]:
    payload: dict[str, object] = {
        "timeout": timeout,
    }
    if offset is not None:
        payload["offset"] = offset
    if allowed_updates is not None:
        payload["allowed_updates"] = allowed_updates

    response = post_json(
        build_api_url(bot_token, "getUpdates"),
        payload,
        timeout=max(timeout + 5, 15),
    )
    if not response.get("ok"):
        raise RuntimeError(f"Telegram getUpdates failed: {response}")
    return list(response.get("result") or [])
