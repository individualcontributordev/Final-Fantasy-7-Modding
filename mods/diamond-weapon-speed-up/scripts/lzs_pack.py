"""FF7 LZS with the 4-byte length header, as used by WORLD/*.TXZ.

The compressor is a cost-optimal parse (9-bit literal, 17-bit reference), so a
patched bundle always ends up smaller than the original encoder's output and
fits its ISO slot."""

from __future__ import annotations

import functools

MAX_DIST = 4095
MAX_LEN = 18
MIN_LEN = 3
MAX_CANDIDATES = 200


def decompress(data: bytes) -> bytes:
	out = bytearray()
	end = 4 + int.from_bytes(data[:4], "little")
	i = 4
	while i < end:
		flags = data[i]
		i += 1
		for bit in range(8):
			if i >= end:
				break
			if flags >> bit & 1:
				out.append(data[i])
				i += 1
				continue
			b0, b1 = data[i], data[i + 1]
			i += 2
			offset = b0 | (b1 & 0xF0) << 4
			start = len(out) - ((len(out) - 18 - offset) & 0xFFF)
			length = MIN_LEN + (b1 & 0xF)
			if start >= 0 and start + length <= len(out):
				out += out[start : start + length]
				continue
			for k in range(length):  # overlapping copy or reach before the start
				out.append(out[start + k] if start + k >= 0 else 0)
	return bytes(out)


def _longest_matches(data: bytes) -> list[tuple[int, int] | None]:
	"""Per position: (length, distance) of the closest longest earlier match.

	Candidates are the last MAX_CANDIDATES positions sharing the 3-byte prefix,
	within MAX_DIST. Rather than compare each one, ask ``rfind`` for the closest
	occurrence of the next-longer prefix; ``last4`` answers the common length-4 case
	without a scan."""
	n = len(data)
	seen: dict[bytes, list[int]] = {}
	last4: dict[bytes, int] = {}
	best: list[tuple[int, int] | None] = [None] * n
	rfind = data.rfind
	for i in range(n - MIN_LEN + 1):
		positions = seen.setdefault(data[i : i + MIN_LEN], [])
		if positions and i - positions[-1] <= MAX_DIST:
			lo = max(i - MAX_DIST, positions[-min(len(positions), MAX_CANDIDATES)])
			p, length = positions[-1], MIN_LEN
			q = last4.get(data[i : i + 4], -1)
			if q >= lo:
				p, length = q, 4
				while length < MAX_LEN and i + length < n:
					q = rfind(data[i : i + length + 1], lo, i + length)
					if q < 0:
						break
					p, length = q, length + 1
			best[i] = (length, i - p)
		positions.append(i)
		if i + 4 <= n:
			last4[data[i : i + 4]] = i
	return best


def compress(data: bytes) -> bytes:
	return _compress(bytes(data))


@functools.lru_cache(maxsize=256)  # discs of one build repeat most files
def _compress(data: bytes) -> bytes:
	n = len(data)
	best = _longest_matches(data)
	cost = [1 << 60] * (n + 1)
	step: list[tuple[int, int] | None] = [None] * (n + 1)  # (start, distance or 0)
	cost[0] = 0
	for i in range(n):
		if cost[i] + 9 < cost[i + 1]:
			cost[i + 1], step[i + 1] = cost[i] + 9, (i, 0)
		if best[i]:
			length, dist = best[i]
			for k in range(MIN_LEN, length + 1):
				if cost[i] + 17 < cost[i + k]:
					cost[i + k], step[i + k] = cost[i] + 17, (i, dist)

	tokens: list[tuple[int, int, int]] = []  # (is_literal, a, b)
	i = n
	while i > 0:
		start, dist = step[i]
		if dist == 0:
			tokens.append((1, data[start], 0))
		else:
			tokens.append((0, (start - 18 - dist) & 0xFFF, i - start))
		i = start
	tokens.reverse()

	out = bytearray(4)
	for g in range(0, len(tokens), 8):
		group = tokens[g : g + 8]
		flags = sum(t[0] << j for j, t in enumerate(group))
		out.append(flags)
		for literal, a, b in group:
			if literal:
				out.append(a)
			else:
				out += bytes((a & 0xFF, (a >> 4) & 0xF0 | (b - MIN_LEN)))
	out[:4] = (len(out) - 4).to_bytes(4, "little")
	return bytes(out)
