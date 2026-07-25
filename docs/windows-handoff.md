# Windows checklist (human)

**Status:** active

Do **not** paste into the Mac chat. Push output via git, then say **check results** there.

```bash
git pull --ff-only
```

---

## Goal

Run encounter address byte search; save output for the Mac agent.

## Steps (Git Bash)

```bash
cd "$(git rev-parse --show-toplevel)"
python scripts/search_encounter_addrs.py workspace/iso-extract/FIELD.BIN.dec \
  > docs/windows-last-output.txt 2>&1
# if python fails, try: python3 … (same redirect)

git add docs/windows-last-output.txt
git commit -m "Windows output: search encounter addrs"
git push
```

## Then

In the Mac Cursor chat, type only: **check results**
