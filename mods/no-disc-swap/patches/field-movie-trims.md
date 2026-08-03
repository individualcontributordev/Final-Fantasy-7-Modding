# FIELD movie trims (Clean no-disc-swap)

Makou script edits (not engine MOVIE stubs).

## Confirmed / operator

| Map / DAT | Issue | Edit |
|-----------|-------|------|
| **fr_e** (#347) BLIN? | After Diamond Weapon — Set+Play blocked progress | Operator deleted Set+Play |
| **blin70_4** (#269) GameMoment >= 1572 | Set+Play needed trim | Operator deleted Set+Play |
| LOSLAKE3 (ioslake3) | ids 57/58 → ONTRAIN + OPENING.BIN; D2 wants loslake1+lslmv | Remove Set+Play; keep jump |
| Crawl sites (operator) | Missing movie slows field to crawl | Remove Set+Play found |
| Final descent BG movie (operator) | BG movie missing | Remove Set+Play |

## Full scan candidates

See field-movie-inventory-d1.md Tier 1 (non-stream D1 targets).

## Edit rule

Delete Set next movie + Play movie. Keep Wait / Execute / Jump / bits.
Rebuild pack layer after work-bin edits.
