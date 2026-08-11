"""Minimal MODE2/2352 ISO9660 helpers for FF7 FIELD.BIN extract / pad-inject.

Emulators usually tolerate stale sector EDC/ECC (same as ff7tk). We only rewrite
Form 1 user data (2048 bytes per sector) and pad shorter replacements with zeros.
"""

from __future__ import annotations

from dataclasses import dataclass

SECTOR = 2352
USER = 2048
USER_OFF = 24  # sync(12) + header(4) + subheader(8)


@dataclass(frozen=True)
class IsoFile:
    path: str
    lba: int
    size: int


def _user(img: memoryview | bytes | bytearray, lba: int) -> bytes:
    off = lba * SECTOR + USER_OFF
    if off + USER > len(img):
        raise ValueError(f"LBA {lba} past end of image")
    return bytes(img[off : off + USER])


def _write_user(img: bytearray, lba: int, data: bytes) -> None:
    if len(data) != USER:
        raise ValueError(f"sector user data must be {USER} bytes")
    off = lba * SECTOR + USER_OFF
    if off + USER > len(img):
        raise ValueError(f"LBA {lba} past end of image")
    img[off : off + USER] = data


def _u32_le(b: bytes, i: int) -> int:
    return b[i] | (b[i + 1] << 8) | (b[i + 2] << 16) | (b[i + 3] << 24)


def _iso_name(raw: bytes) -> str:
    # "FIELD.BIN;1" or "FIELD" directory
    name = raw.split(b";", 1)[0].decode("ascii", errors="replace").strip()
    return name.upper()


def _parse_dir_records(blob: bytes) -> list[tuple[str, int, int, bool]]:
    """Return (name, lba, size, is_dir) for records in a directory extent."""
    out: list[tuple[str, int, int, bool]] = []
    i = 0
    while i < len(blob):
        length = blob[i]
        if length == 0:
            # move to next sector boundary inside this extent blob
            nxt = ((i // USER) + 1) * USER
            if nxt <= i:
                break
            i = nxt
            continue
        if i + length > len(blob):
            break
        rec = blob[i : i + length]
        flags = rec[25]
        name_len = rec[32]
        if name_len == 1 and rec[33] in (0x00, 0x01):
            i += length
            continue
        name = _iso_name(rec[33 : 33 + name_len])
        lba = _u32_le(rec, 2)
        size = _u32_le(rec, 10)
        is_dir = bool(flags & 0x02)
        out.append((name, lba, size, is_dir))
        i += length
    return out


def _read_extent(img: memoryview | bytes | bytearray, lba: int, size: int) -> bytes:
    remaining = size
    sector = lba
    chunks: list[bytes] = []
    while remaining > 0:
        user = _user(img, sector)
        take = min(USER, remaining)
        chunks.append(user[:take])
        remaining -= take
        sector += 1
    return b"".join(chunks)


def _list_dir(img: memoryview | bytes | bytearray, lba: int, size: int):
    return _parse_dir_records(_read_extent(img, lba, size))


def find_file(img: bytes | bytearray, path: str) -> IsoFile:
    """Locate a file by ISO path like FIELD/FIELD.BIN (case-insensitive)."""
    parts = [p for p in path.replace("\\", "/").upper().split("/") if p]
    if not parts:
        raise ValueError("empty path")

    if len(img) % SECTOR != 0:
        raise ValueError(f"image size {len(img)} is not a multiple of {SECTOR}")

    pvd = _user(img, 16)
    if pvd[0] != 1 or pvd[1:6] != b"CD001":
        raise ValueError("Primary Volume Descriptor not found at LBA 16")

    root = pvd[156 : 156 + 34]
    dir_lba = _u32_le(root, 2)
    dir_size = _u32_le(root, 10)

    for idx, part in enumerate(parts):
        entries = _list_dir(img, dir_lba, dir_size)
        match = next((e for e in entries if e[0] == part), None)
        if match is None:
            names = ", ".join(e[0] for e in entries[:20])
            raise FileNotFoundError(
                f"missing {part!r} under {'/'.join(parts[:idx]) or '[root]'} "
                f"(saw: {names}{'…' if len(entries) > 20 else ''})"
            )
        name, lba, size, is_dir = match
        is_last = idx == len(parts) - 1
        if is_last:
            if is_dir:
                raise IsADirectoryError(path)
            return IsoFile(path="/".join(parts), lba=lba, size=size)
        if not is_dir:
            raise NotADirectoryError("/".join(parts[: idx + 1]))
        dir_lba, dir_size = lba, size

    raise FileNotFoundError(path)


def extract_file(img: bytes | bytearray, path: str) -> bytes:
    meta = find_file(img, path)
    return _read_extent(img, meta.lba, meta.size)


def replace_file_padded(img: bytearray, path: str, new_data: bytes) -> IsoFile:
    """Replace file contents in-place. Shorter files are zero-padded to the ISO size.

    Refuses to write a longer file (would need a full ISO rebuild).
    """
    meta = find_file(img, path)
    if len(new_data) > meta.size:
        raise ValueError(
            f"{path}: new file is {len(new_data)} bytes but ISO slot is {meta.size} "
            "(longer inject not supported — pad/rebuild required)"
        )
    payload = new_data + (b"\x00" * (meta.size - len(new_data)))

    remaining = meta.size
    sector = meta.lba
    offset = 0
    while remaining > 0:
        take = min(USER, remaining)
        chunk = payload[offset : offset + take]
        if take < USER:
            # last partial sector: preserve tail of existing user data after file end
            user = bytearray(_user(img, sector))
            user[:take] = chunk
            _write_user(img, sector, bytes(user))
        else:
            _write_user(img, sector, chunk)
        offset += take
        remaining -= take
        sector += 1
    return meta


def _patch_dirent_size_only(img: bytearray, path: str, new_size: int) -> None:
    """Update ISO9660 dirent size (LE+BE) keeping LBA. File must already exist."""
    import struct

    parts = [p for p in path.replace("\\", "/").upper().split("/") if p]
    pvd = _user(img, 16)
    root = pvd[156 : 156 + 34]
    dir_lba = _u32_le(root, 2)
    dir_size = _u32_le(root, 10)
    target = parts[-1]
    parent_parts = parts[:-1]

    for part in parent_parts:
        entries = _list_dir(img, dir_lba, dir_size)
        match = next((e for e in entries if e[0] == part), None)
        if match is None or not match[3]:
            raise FileNotFoundError(path)
        dir_lba, dir_size = match[1], match[2]

    # load dir extent
    remaining = dir_size
    sector = dir_lba
    data = bytearray()
    secs: list[int] = []
    while remaining > 0:
        take = min(USER, remaining)
        secs.append(sector)
        data.extend(_user(img, sector)[:take])
        remaining -= take
        sector += 1

    # find record for target
    i = 0
    found_pos = None
    while i < len(data):
        length = data[i]
        if length == 0:
            nxt = ((i // USER) + 1) * USER
            if nxt <= i:
                break
            i = nxt
            continue
        if i + length > len(data):
            break
        rec = data[i : i + length]
        name_len = rec[32]
        if name_len == 1 and rec[33] in (0x00, 0x01):
            i += length
            continue
        name = _iso_name(bytes(rec[33 : 33 + name_len]))
        if name == target:
            found_pos = i
            break
        i += length
    if found_pos is None:
        raise FileNotFoundError(path)

    struct.pack_into("<I", data, found_pos + 10, new_size)
    struct.pack_into(">I", data, found_pos + 14, new_size)

    off = 0
    rem = dir_size
    for s in secs:
        take = min(USER, rem)
        chunk = bytes(data[off : off + take])
        if take < USER:
            user = bytearray(_user(img, s))
            user[:take] = chunk
            _write_user(img, s, bytes(user))
        else:
            _write_user(img, s, chunk)
        off += take
        rem -= take


def replace_file_within_sectors(img: bytearray, path: str, new_data: bytes) -> IsoFile:
    """Replace file; size may change if it still fits the same 2048-byte sector count.

    Used for CSR+ FIELD maps a few bytes larger/smaller than the baseline slot
    but within the same sector allocation (common after Makou edits).
    """
    meta = find_file(img, path)
    old_sec = (meta.size + USER - 1) // USER
    new_sec = (len(new_data) + USER - 1) // USER
    if new_sec > old_sec:
        raise ValueError(
            f"{path}: new file needs {new_sec} sectors but slot has {old_sec} "
            f"({len(new_data)} bytes > capacity {old_sec * USER})"
        )
    # Always set ISO size to payload length when sector count allows.
    if len(new_data) != meta.size:
        _patch_dirent_size_only(img, path, len(new_data))
        meta = find_file(img, path)
        if meta.size != len(new_data):
            raise RuntimeError(f"{path}: size patch failed got {meta.size}")

    # Write full sector allocation (payload + zero pad to end of last sector).
    cap = old_sec * USER
    payload = new_data + (b"\x00" * (cap - len(new_data)))
    remaining = cap
    sector = meta.lba
    offset = 0
    while remaining > 0:
        take = min(USER, remaining)
        chunk = payload[offset : offset + take]
        _write_user(img, sector, chunk if take == USER else chunk + b"\x00" * (USER - take))
        offset += take
        remaining -= take
        sector += 1
    return find_file(img, path)
