# Discord channel export (Windows)

One-time personal archive of a channel **you can already open**.
Uses [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) CLI.
User-token automation is against Discord TOS — use only for your own archive; risk is yours.

**Never** commit tokens, put them in chat, or push export dumps to git.

## 1. Download CLI

Release: https://github.com/Tyrrrz/DiscordChatExporter/releases/tag/2.47.3

- Most PCs: **`DiscordChatExporter.Cli.win-x64.zip`**
- ARM Windows: **`DiscordChatExporter.Cli.win-arm64.zip`**

Unzip to a folder you control, e.g.:

```text
%USERPROFILE%\tools\DiscordChatExporter.Cli\
```

You should see `DiscordChatExporter.Cli.exe` in that folder.

## 2. Get your user token (browser)

1. Open **https://discord.com/app** in **Chrome or Edge** (not the Discord desktop app).
2. Log in; open any channel.
3. Press **F12** (or Ctrl+Shift+I) → **Network** tab.
4. Press **Ctrl+R** to reload; click a few channels.
5. Filter box: `messages`
6. Click a request whose name starts with **messages**.
7. **Headers** → **Request Headers** → **authorization**
8. Copy the **full** value (long string).

Save only on disk (PowerShell):

```powershell
# Run in the Cli folder
cd $env:USERPROFILE\tools\DiscordChatExporter.Cli
# Paste token when prompted (not echoed to scrollback if you use Read-Host -AsSecureString variants;
# simplest one-liner — clear terminal history after):
$token = Read-Host "Paste Discord token"
Set-Content -Path .\.token -Value $token -NoNewline
icacls .\.token /inheritance:r | Out-Null
# Optional: restrict to your user only
icacls .\.token /grant:r "$env:USERNAME:(R)"
```

Or Notepad: save one line as `.token` next to the exe, no extra spaces/newlines if possible.

## 3. Channel ID

1. Discord → **User Settings** → **Advanced** → **Developer Mode** ON.
2. Right-click the target channel → **Copy Channel ID**.

## 4. Export (Git Bash or PowerShell)

### Git Bash

```bash
cd /c/Users/$USER/tools/DiscordChatExporter.Cli
mkdir -p out
export DISCORD_TOKEN="$(tr -d '\r\n' < .token)"
./DiscordChatExporter.Cli.exe export \
  -c YOUR_CHANNEL_ID \
  -f Json \
  -o out/ \
  --include-threads All \
  --utc
ls -la out/
```

### PowerShell

```powershell
cd $env:USERPROFILE\tools\DiscordChatExporter.Cli
New-Item -ItemType Directory -Force -Path .\out | Out-Null
$env:DISCORD_TOKEN = (Get-Content -Raw .\.token).Trim()
.\DiscordChatExporter.Cli.exe export `
  -c YOUR_CHANNEL_ID `
  -f Json `
  -o .\out\ `
  --include-threads All `
  --utc
Get-ChildItem .\out
```

Replace `YOUR_CHANNEL_ID` with the real ID. JSON appears under `out\`.

Optional readable HTML: `-f HtmlDark` instead of `-f Json`.

## 5. After export

1. Confirm `out\` has `.json` (and no errors in the console).
2. **Do not** `git add` `.token` or `out\`.
3. Say **check** in the Mac chat and point at the folder path if you synced it,
   or paste only a short status (message count / file name) under Evidence in
   `docs/windows-last-task.md` if that task is active.

## Bot token?

Only if a **bot is in that server** with View Channel + Read Message History.
If you do not own the server and no admin invited a bot, use the **user** token steps above.

## Alternative: Chrome HAR (no token file)

If you already scrolled the channel with DevTools Network open:

1. Filter messages then right-click list -> Save all as HAR with content.
2. Do not commit the .har (gitignores *.har).
3. On a machine with this repo:

    cd "$(git rev-parse --show-toplevel)"
    python scripts/har_discord_messages.py path/to/discord.com.har

Writes workspace/discord-export/channel-<id>-messages.json and .md

