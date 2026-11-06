#!/usr/bin/env python3
"""Record a Makou Reactor edit of /FIELD/BLIN70_1.DAT as mods/masamune/field_edit.json.

usage: capture_edit.py <unedited disc.bin> <Makou-edited disc.bin>

Diffs the two scripts entity by entity (plus messages); the rebuild then applies that diff to any
base's script, so no porting is needed. Re-run it only when the field edit itself changes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from apply_masamune import EDIT, FIELD, capture_edit, extract_file, lzs


def main() -> None:
	if len(sys.argv) != 3:
		raise SystemExit(__doc__)
	base, edited = (lzs.decompress(extract_file(Path(p).read_bytes(), FIELD)) for p in sys.argv[1:])
	edit = capture_edit(base, edited)
	EDIT.write_text(json.dumps(edit, indent=1) + "\n", encoding="utf-8", newline="\n")
	print(f"wrote {EDIT}: {len(edit['entities'])} entities, {len(edit['messages_added'])} messages added")


if __name__ == "__main__":
	main()
