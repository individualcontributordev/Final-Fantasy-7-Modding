#!/usr/bin/env python3
"""Sanitize a Discord Chrome HAR into docs/history (gzipped archive + extracts)."""
from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs" / "history" / "archive"
EXTRACT = ROOT / "docs" / "history" / "extracts"
STRIP = {
    "authorization",
    "cookie",
    "set-cookie",
    "x-super-properties",
    "x-discord-locale",
    "x-discord-timezone",
    "x-debug-options",
    "x-fingerprint",
    "cf-ray",
    "cf-cache-status",
    "x-cloud-trace-context",
}


def strip_headers(headers):
    return [h for h in (headers or []) if str(h.get("name") or "").lower() not in STRIP]


def sanitize_har(har: dict) -> dict:
    log = har.get("log") or {}
    entries = []
    for e in log.get("entries") or []:
        e = json.loads(json.dumps(e))
        req, resp = e.get("request") or {}, e.get("response") or {}
        req["headers"] = strip_headers(req.get("headers"))
        resp["headers"] = strip_headers(resp.get("headers"))
        req.pop("cookies", None)
        resp.pop("cookies", None)
        e["request"], e["response"] = req, resp
        for k in ("_initiator", "_priority", "connection", "serverIPAddress"):
            e.pop(k, None)
        entries.append(e)
    return {
        "log": {
            "version": log.get("version", "1.2"),
            "creator": {"name": "sanitize_discord_har", "version": "1"},
            "comment": "Sanitized HAR for FF7 CSR/modding history archive.",
            "entries": entries,
        }
    }


def response_text(entry):
    content = (entry.get("response") or {}).get("content") or {}
    text = content.get("text")
    if not text:
        return None
    if content.get("encoding") == "base64":
        try:
            return base64.b64decode(text).decode("utf-8", errors="replace")
        except Exception:
            return None
    return text


def extract_messages(har: dict):
    by_id, channels = {}, set()
    for entry in (har.get("log") or {}).get("entries") or []:
        url = ((entry.get("request") or {}).get("url")) or ""
        if "/messages" not in url or "discord.com/api" not in url:
            continue
        m = re.search(r"/channels/(\d+)/messages", url)
        if m:
            channels.add(m.group(1))
        raw = response_text(entry)
        if not raw:
            continue
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            continue
        items = body if isinstance(body, list) else (
            body.get("messages") if isinstance(body, dict) else []
        )
        if not isinstance(items, list):
            continue
        for msg in items:
            if not isinstance(msg, dict) or not msg.get("id"):
                continue
            author = msg.get("author") or {}
            by_id[str(msg["id"])] = {
                "id": msg["id"],
                "timestamp": msg.get("timestamp"),
                "author": {
                    "username": author.get("username"),
                    "global_name": author.get("global_name"),
                },
                "content": msg.get("content") or "",
                "attachments": [
                    {"filename": a.get("filename"), "url": a.get("url")}
                    for a in (msg.get("attachments") or [])
                ],
            }
    msgs = sorted(by_id.values(), key=lambda m: m.get("timestamp") or "")
    return sorted(channels), msgs


def write_gz_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("har", type=Path)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    har_path = args.har.expanduser().resolve()
    if not har_path.is_file():
        print("missing", har_path, file=sys.stderr)
        return 1

    clean = sanitize_har(json.loads(har_path.read_text(encoding="utf-8", errors="replace")))
    channels, messages = extract_messages(clean)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    EXTRACT.mkdir(parents=True, exist_ok=True)

    gz_har = ARCHIVE / f"{args.slug}.sanitized.har.gz"
    with gzip.open(gz_har, "wt", encoding="utf-8") as f:
        f.write(json.dumps(clean, ensure_ascii=False, separators=(",", ":")))

    payload = {
        "title": args.title,
        "note": args.note,
        "slug": args.slug,
        "channelIds": channels,
        "messageCount": len(messages),
        "sourceArchive": str(gz_har.relative_to(ROOT)),
        "messages": messages,
    }
    write_gz_text(
        EXTRACT / f"{args.slug}-messages.json.gz",
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    lines = [f"# {args.title}", "", args.note, "", f"Messages: {len(messages)}", "", "---", ""]
    for msg in messages:
        a = msg.get("author") or {}
        name = a.get("global_name") or a.get("username") or "?"
        ts = (msg.get("timestamp") or "")[:19].replace("T", " ")
        lines += [f"### {ts} — {name}", "", msg.get("content") or "_(no text)_", ""]
    write_gz_text(EXTRACT / f"{args.slug}-messages.md.gz", "\n".join(lines) + "\n")

    man_path = ARCHIVE / "MANIFEST.json"
    man = json.loads(man_path.read_text()) if man_path.is_file() else {"archives": []}
    authors = Counter((m.get("author") or {}).get("username") or "?" for m in messages)
    t0 = (messages[0].get("timestamp") or "")[:10] if messages else ""
    t1 = (messages[-1].get("timestamp") or "")[:10] if messages else ""
    entry = {
        "slug": args.slug,
        "title": args.title,
        "note": args.note,
        "channelIds": channels,
        "messageCount": len(messages),
        "dateRange": [t0, t1],
        "archive": str(gz_har.relative_to(ROOT)),
        "messagesJson": f"docs/history/extracts/{args.slug}-messages.json.gz",
        "messagesMarkdown": f"docs/history/extracts/{args.slug}-messages.md.gz",
        "topAuthors": authors.most_common(12),
        "gzipBytes": gz_har.stat().st_size,
    }
    man["archives"] = [a for a in man.get("archives") or [] if a.get("slug") != args.slug]
    man["archives"].append(entry)
    man["archives"].sort(key=lambda a: (a.get("dateRange") or [""])[0])
    man_path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {gz_har.relative_to(ROOT)} ({len(messages)} messages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
