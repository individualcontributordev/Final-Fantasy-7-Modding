# History archive

Long-form story: **[HISTORY.md](HISTORY.md)**

| Path | Contents |
|------|----------|
| `archive/*.sanitized.har.gz` | Browser HARs with cookies/auth stripped |
| `archive/MANIFEST.json` | Index of archives and extracts |
| `extracts/*-messages.json.gz` | Slim message JSON |
| `extracts/*-messages.md.gz` | Readable chat logs |
| `extracts/all-messages-merged.json.gz` | Both archives, time-sorted |

## Add a new capture

1. Save Chrome HAR **with content** (do not commit the raw file).
2. Run:

```text
python scripts/sanitize_discord_har.py path/to/capture.har
  --slug YYYY-MM-description
  --title "Short title"
  --note "One-line context"
```

3. Update HISTORY.md / SUGGESTIONS.md if the story or backlog changed.

**Never commit raw unsanitized HARs.**
