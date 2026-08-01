# Task: export one Discord channel (Windows)

## Goal

Personal archive of a channel you can open, using DiscordChatExporter CLI.
Full guide: **[docs/discord-channel-export-windows.md](discord-channel-export-windows.md)**

## Do not

- Paste your token into chat, Discord, or git.
- Commit `.token` or export `out/` dumps.

## Success

1. CLI installed (`DiscordChatExporter.Cli.win-x64.zip` from release 2.47.3).
2. Token saved only as local `.token` next to the exe.
3. Channel exported to `out/` as **Json**.
4. Evidence: file name(s) + approx size (no token).

## Steps

1. Read `docs/discord-channel-export-windows.md`.
2. Download CLI → unzip under `%USERPROFILE%\tools\DiscordChatExporter.Cli\`.
3. Get user token (browser Network → filter `messages` → `authorization` header).
4. Save `.token`; get Channel ID (Developer Mode).
5. Run copy-paste below. Say **check** when done.

## Copy-paste (Git Bash)

    cd /c/Users/$USER/tools/DiscordChatExporter.Cli
    # first time only: place DiscordChatExporter.Cli.exe here from the zip
    # first time only: printf '%s' 'YOUR_TOKEN' > .token && chmod 600 .token

    mkdir -p out
    export DISCORD_TOKEN="$(tr -d '\r\n' < .token)"
    ./DiscordChatExporter.Cli.exe export \
      -c YOUR_CHANNEL_ID \
      -f Json \
      -o out/ \
      --include-threads All \
      --utc
    ls -la out/

## Copy-paste (PowerShell)

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

## Evidence

    (ls of out/ — file names + sizes only)
