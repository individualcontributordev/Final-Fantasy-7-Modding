# Task: fix .augment symlinks (Git Bash on Windows)

## Goal

Ensure this clone has **in-repo** agent files under `.agents/` and Auggie entrypoints under `.augment/` as **relative** symlinks (not plain text, not absolute paths outside the repo).

## Layout (already correct in git)

| Path | Role |
|------|------|
| `.agents/rules/`, `.agents/skills/` | Canonical copies — real files, edit only here |
| `.augment/rules` → `../.agents/rules` | Relative symlink for Auggie |
| `.augment/skills` → `../.agents/skills` | Relative symlink for Auggie |

Do **not** point at another machine path or home directory. Do **not** copy trees into `.augment/`.

## Success

From the **repo root** in Git Bash, you should see:

- `ls -la .augment` shows `rules -> ../.agents/rules` and `skills -> ../.agents/skills`
- `test -f .augment/rules/mac-human-workflow.mdc && echo rules_ok` prints `rules_ok`
- Modding: `test -f .augment/skills/record-findings/SKILL.md && echo skills_ok` prints `skills_ok`
- CSR (if fixing that clone): `test -f .augment/skills/ship-csr-plus-scene/SKILL.md && echo skills_ok`

## Steps (Git Bash — not cmd mklink)

### 1. Enable Git symlinks (once per machine)

    git config --global core.symlinks true

Windows may need **Developer Mode** (Settings → Privacy and security → For developers) or an elevated shell so Git can create symlinks.

### 2. Prefer Git restoring links

    cd "$(git rev-parse --show-toplevel)"
    git pull --ff-only
    rm -rf .augment/rules .augment/skills
    git checkout -- .augment
    ls -la .augment

### 3. If Git left plain text files or broken links — recreate with ln -s

    cd "$(git rev-parse --show-toplevel)"
    mkdir -p .augment
    cd .augment
    rm -rf rules skills
    ln -s ../.agents/rules rules
    ln -s ../.agents/skills skills
    ls -la
    test -f rules/mac-human-workflow.mdc && echo rules_ok
    test -d skills && ls skills && echo skills_ok

Repeat for **Final-Fantasy-7-CSR** and **individualcontributordev.github.io** if those clones are broken too (same commands, each repo root).

### 4. Do not use

- cmd `mklink` (use Git Bash `ln -s` instead)
- Absolute paths (`/d/projects/...`, `C:\...`)
- Copying rule/skill files into `.augment/`

Also documented in root **AGENTS.md** (Rules / skills layout).

## Evidence

Paste `ls -la .augment` and the `rules_ok` / `skills_ok` lines below, then commit this file and push. Say **check**.

    (paste here)
