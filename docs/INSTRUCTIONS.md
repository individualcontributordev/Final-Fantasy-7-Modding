# Your turn: builder burn + console playtest (endings shipped)

## What we published

Three separate mods (not one blob):

| Mod | When the site adds it |
|-----|------------------------|
| **Single-disc** | You turn it on |
| **CSR speedrun movies** | Auto only on **CSR alone** + Single-disc (not if CSR+ scenes are on) |
| **Ending credits** (7 hidden parts) | Auto with Single-disc on **CSR** (alone **or** CSR+). Also marked for Highwind later |

Verify locally already **PASS** for CSR + Single-disc + speedrun movies + all 7 ending parts.

## Build a disc on the site

1. Open https://individualcontributor.dev/builder/  
2. Base: **CSR** (try CSR alone first; later CSR+ if you want).  
3. Turn on **Single-disc**.  
4. Do not hunt for movies/endings in the list — they auto-add when hidden rules match.  
5. Download the Disc 1 image, burn, play on console.

Expected size class stays a full one-disc image (~731 MiB range after movies/endings).

## What to check on console

1. Game boots, New Game / load OK.  
2. A mid-game path you care about (optional).  
3. **Lake cutscene** if you reach it — picture + sound.  
4. **Ending / credits** after the final fight — should run; some credit **names** may look noisy mid-roll (known).  

## Reply with

Boot OK/fail, anything broken, credits OK/messy/fail.  

If the site did not pull new packs yet, wait for GitHub Pages after this push, or hard-refresh the builder.
