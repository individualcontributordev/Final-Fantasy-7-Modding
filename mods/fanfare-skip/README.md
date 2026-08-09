# Fanfare Skip

After the last enemy dies, skip the victory ceremony path (same idea as Midgar
train battles).

Optional builder mod. Default patches **BATTLE/BATTLE.X only** (not field scripts,
not FAN2.SND).

- Rewards still apply (exp / AP / gil / items)
- Loot and level-up screens still show
- Works on random battles and bosses
- Does **not** replace FAN2.SND (quiet FAN2 freezes battle audio — fixed in 0.1.5)

Build:

```bash
python mods/fanfare-skip/scripts/build_on_base.py --against clean --discs 1
python mods/fanfare-skip/scripts/build_on_base.py --against all --discs 1,2,3
```
