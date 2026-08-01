#!/usr/bin/env python3
"""Merge Discord channel messages from a Chrome HAR into JSON + Markdown.

  python scripts/har_discord_messages.py path/to/discord.com.har
  python scripts/har_discord_messages.py path/to/discord.com.har -o workspace/discord-export

Does not need a Discord token. Prefer HARs saved with "Save all as HAR with content".
Never commit .har files (may contain cookies). Output defaults under workspace/.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path


def response_text(entry: dict) -> str | None:
    content = (entry.get("response") or {}).get("content") or {}
    text = content.get("text")
    if text is None or text == "":
        return None
    if content.get("encoding") == "base64":
        try:
            return base64.b64decode(text).decode("utf-8", errors="replace")
        except Exception:
            return None
    return text


def iter_messages(har: dict):
    for entry in (har.get("log") or {}).get("entries") or []:
        url = ((entry.get("request") or {}).get("url")) or ""
        if "/messages" not in url or "discord.com/api" not in url:
            continue
        m = re.search(r"/channels/(\d+)/messages", url)
        channel_id = m.group(1) if m else None
        raw = response_text(entry)
        if not raw:
            continue
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(body, dict) and isinstance(body.get("messages"), list):
            items = body["messages"]
        elif isinstance(body, list):
            items = body
        else:
            continue
        for msg in items:
            if isinstance(msg, dict) and msg.get("id"):
                yield channel_id, msg


def to_markdown(channel_ids: list[str], messages: list[dict]) -> str:
    ch = ", ".join(channel_ids) if channel_ids else "unknown"
    lines = [f"# Discord channel {ch}", "", f"Messages: {len(messages)} (from HAR)", ""]
    for msg in messages:
        author = msg.get("author") or {}
        name = author.get("global_name") or author.get("username") or "?"
        ts = msg.get("timestamp") or ""
        content = (msg.get("content") or "").replace("\r\n", "\n")
        lines.append(f"## {ts} — {name}")
        lines.append("")
        lines.append(content if content else "_(no text)_")
        for att in msg.get("attachments") or []:
            lines.append(f"- attachment: {att.get('filename')} {att.get('url', '')}")
        for emb in msg.get("embeds") or []:
            title = emb.get("title") or emb.get("description") or ""
            if title:
                lines.append(f"- embed: {str(title)[:200]}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("har", type=Path, help="Chrome HAR file")
    ap.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: workspace/discord-export)",
    )
    args = ap.parse_args()
    har_path = args.har.expanduser().resolve()
    if not har_path.is_file():
        print(f"Missing HAR: {har_path}", file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    out_dir = (args.out_dir or (root / "workspace" / "discord-export")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    har = json.loads(har_path.read_text(encoding="utf-8", errors="replace"))
    by_id: dict[str, dict] = {}
    channel_ids: set[str] = set()
    for channel_id, msg in iter_messages(har):
        if channel_id:
            channel_ids.add(channel_id)
        by_id[str(msg["id"])] = msg
    messages = sorted(by_id.values(), key=lambda m: m.get("timestamp") or "")
    channels = sorted(channel_ids)
    stem = channels[0] if len(channels) == 1 else "merged"
    payload = {
        "channelIds": channels,
        "messageCount": len(messages),
        "source": str(har_path.name),
        "messages": messages,
    }
    json_path = out_dir / f"channel-{stem}-messages.json"
    md_path = out_dir / f"channel-{stem}-messages.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(channels, messages), encoding="utf-8")
    print(f"channels: {channels or ['(none)']}")
    print(f"messages: {len(messages)}")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    if not messages:
        print("No messages found — export HAR with content and filter on messages.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
