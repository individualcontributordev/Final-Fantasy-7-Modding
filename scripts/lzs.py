"""FF7 LZS decompress (Okumura / ff7tk LZS::decompressAllWithHeader)."""

from __future__ import annotations

import struct


def decompress_all(data: bytes) -> bytes:
	"""Decompress raw LZS payload (no 4-byte size header)."""
	out = bytearray()
	text_buf = bytearray(4096)
	cur = 4078
	i = 0
	n = len(data)
	first_byte = 0

	while i < n:
		first_byte >>= 1
		if (first_byte & 256) == 0:
			if i >= n:
				break
			first_byte = data[i] | 0xFF00
			i += 1
		if i >= n:
			break
		if first_byte & 1:
			b = data[i]
			i += 1
			text_buf[cur] = b
			out.append(b)
			cur = (cur + 1) & 4095
		else:
			if i + 1 >= n:
				break
			b1 = data[i]
			b2 = data[i + 1]
			i += 2
			offset = b1 | ((b2 & 0xF0) << 4)
			end = (b2 & 0x0F) + 2 + offset
			for pos in range(offset, end + 1):
				b = text_buf[pos & 4095]
				text_buf[cur] = b
				out.append(b)
				cur = (cur + 1) & 4095

	return bytes(out)


def decompress_all_with_header(data: bytes) -> bytes:
	"""PSX FIELD/*.DAT style: u32le compressed size, then LZS bytes."""
	if len(data) < 4:
		raise ValueError("LZS header truncated")
	(lzs_size,) = struct.unpack_from("<I", data, 0)
	if lzs_size <= 0 or 4 + lzs_size > len(data):
		raise ValueError(f"bad LZS size {lzs_size} for file of {len(data)}")
	return decompress_all(data[4 : 4 + lzs_size])



def compress_all(data: bytes) -> bytes:
	"""FF7 LZS compress matching decompress_all (ring 4096, cur starts 4078)."""
	from collections import defaultdict

	n_ring, f_max = 4096, 18
	text_buf = bytearray(n_ring)
	cur = 4078
	chains: dict[int, list[int]] = defaultdict(list)
	ring_at: list[int] = []
	out = bytearray()
	i = 0
	n = len(data)

	def key_at(p: int):
		if p + 2 >= n:
			return None
		return (data[p] << 16) | (data[p + 1] << 8) | data[p + 2]

	def index_start(p: int) -> None:
		k = key_at(p)
		if k is None:
			return
		chains[k].append(p)
		if len(chains[k]) > 512:
			chains[k] = chains[k][-256:]

	while i < n:
		fpos = len(out)
		out.append(0)
		flags = 0
		for bit in range(8):
			if i >= n:
				break
			best_len, best_data_pos = 0, -1
			k = key_at(i)
			if k is not None and i > 0:
				for src in chains.get(k, [])[-256:]:
					if src >= i or i - src > n_ring:
						continue
					ml = 0
					while ml < f_max and i + ml < n and data[src + ml] == data[i + ml]:
						ml += 1
					if ml > best_len:
						best_len, best_data_pos = ml, src
			if best_len >= 3 and best_data_pos >= 0:
				length = min(best_len, 18)
				best_off = ring_at[best_data_pos]
				b1 = best_off & 0xFF
				b2 = ((best_off >> 4) & 0xF0) | ((length - 3) & 0x0F)
				out.append(b1)
				out.append(b2)
				for j in range(length):
					b = data[i + j]
					ring_at.append(cur)
					text_buf[cur] = b
					cur = (cur + 1) & 4095
					index_start(len(ring_at) - 3)
				i += length
			else:
				flags |= 1 << bit
				b = data[i]
				out.append(b)
				ring_at.append(cur)
				text_buf[cur] = b
				cur = (cur + 1) & 4095
				index_start(len(ring_at) - 3)
				i += 1
		out[fpos] = flags
	return bytes(out)


def compress_all_with_header(data: bytes) -> bytes:
	"""u32le compressed size + LZS payload (FIELD/*.DAT style)."""
	body = compress_all(data)
	return struct.pack("<I", len(body)) + body
