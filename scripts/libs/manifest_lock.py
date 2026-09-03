"""Exclusive lock around a JSON read-modify-write.

Parallel recuts all replace one add-on in ``builder/manifest.json``. Without a
lock, two processes can load the same file and the later write drops the other
pack. Pack JSON files are per-id and do not need this.

The lock is a sentinel file claimed with an exclusive create, not ``fcntl`` or
``msvcrt``: those are POSIX-only and Windows-only respectively, and the recut
scripts run on both.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# The guarded section is one small read-modify-write, so a sentinel still held
# after this long belongs to a crashed build rather than a slow one.
TIMEOUT_SECONDS = 120
POLL_SECONDS = 0.05


def _claim(lock_path: Path) -> None:
	"""Block until this process creates ``lock_path``, or give up."""
	deadline = time.monotonic() + TIMEOUT_SECONDS
	while True:
		try:
			fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
		except FileExistsError:
			if time.monotonic() >= deadline:
				raise SystemExit(
					f"Timed out waiting for {lock_path}\n"
					"If no build is running, delete that file and rerun."
				)
			time.sleep(POLL_SECONDS)
			continue
		# Recorded so a leftover sentinel names the build that died holding it.
		with os.fdopen(fd, "w", encoding="utf-8") as sentinel:
			sentinel.write(f"pid {os.getpid()}\n")
		return


@contextmanager
def locked_json(path: Path) -> Iterator[None]:
	"""Serialize read-modify-write access to ``path`` across processes."""
	lock_path = path.with_name(path.name + ".lock")
	lock_path.parent.mkdir(parents=True, exist_ok=True)
	_claim(lock_path)
	try:
		yield
	finally:
		lock_path.unlink(missing_ok=True)
