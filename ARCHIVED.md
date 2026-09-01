# Archived from `main`

Notes, RE tooling, training data, and retired ship scripts are not on `main`.
The last commit that still contained that tree:

https://github.com/individualcontributordev/Final-Fantasy-7-Modding/tree/8bea169c2e0d6149d06d2803e39a97a2e231e7f1

Raw file:

`https://github.com/individualcontributordev/Final-Fantasy-7-Modding/blob/8bea169c2e0d6149d06d2803e39a97a2e231e7f1/<path>`

| Path | What it was |
|------|-------------|
| `docs/` | Curriculum, Ghidra guides, hardware-burn notes, runbooks |
| `data/` | Training JSONL and opcode dumps |
| `rag_index/` | Local RAG artifacts |
| `scripts/ghidra/` | Ghidra extract/analyze helpers |
| `scripts/` (most files) | One-off compares, training generators, RAM advisors |
| `scripts/init_external_repos.sh` | Cloned extra RE remotes into `./external/` (replaced by `scripts/init_workspace.sh`) |
| `mods/single-disc/scripts/ship_*.py`, `build_v0*.py` | Retired single-disc ship scripts |
| `mods/single-disc/patches/*.md` | Movie/field investigation notes |
| `mods/*/README.md`, `CHANGELOG.md` | Per-mod prose, now the root README |
| `tests/test_single_disc_stack.py`, `test_builder_contracts.py` | Contracts for retired packs |
| `workspace/discord-export/`, `workspace/field-script-compare-*` | Local notes |
| `train_ff7.py`, `run_ff7_agent.py`, `eval_greedy_test.py` | Local model training |

A separate historical dump also lives in `~/Final-Fantasy-7-RE-Archive` if that clone exists.
