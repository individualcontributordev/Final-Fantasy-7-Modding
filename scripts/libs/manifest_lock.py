"""Exclusive lock around a JSON read-modify-write.

Parallel recuts all replace one add-on in ``builder/manifest.json``. Without a
lock, two processes can load the same file and the later write drops the other
pack. Pack JSON files are per-id and do not need this.
"""

from __future__ import annotations

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def locked_json(path: Path) -> Iterator[None]:
	"""Hold an exclusive flock on ``path.with_name(path.name + '.lock')``."""
	lock_path = path.with_name(path.name + ".lock")
	lock_path.parent.mkdir(parents=True, exist_ok=True)
	with lock_path.open("a", encoding="utf-8") as lock:
		fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
		try:
			yield
		finally:
			fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
