# Victory Skip (train-style)

After the last enemy dies, leave the fight without the victory song and win poses — same idea as the Midgar train battles.

Optional builder mod. Does not change fields; it patches BATTLE/BATTLE.X so every battle treats the official no-victory-music battle-mode bit as on.

Rewards (exp / AP / gil / items) still apply. Reward pop-up screens are unchanged.

Build:

    python mods/victory-skip/scripts/build_on_base.py --against clean --discs 1
    python mods/victory-skip/scripts/build_on_base.py --against all --discs 1,2,3
