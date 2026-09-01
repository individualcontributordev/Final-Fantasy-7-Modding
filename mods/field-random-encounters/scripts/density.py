#!/usr/bin/env python3
"""Define the shipped field-encounter density choices used by build CLIs.

Parsers accept names, their fixed 0/25/50/75 values, lists, or ``all`` and
return ordered unique rates; the prompt is available only on a TTY. These
integers identify tracked MIPS stubs and stable pack ids, not arbitrary
percentages, so unsupported rates are rejected before any file is patched."""

from __future__ import annotations

import sys

# Pack id / stub files use these integers (field-encounter-25, not a free %).
RATES = (0, 25, 50, 75)

DENSITIES: tuple[dict, ...] = (
	{
		"name": "off",
		"rate": 0,
		"title": "Off (0%)",
		"hint": "No random field battles (FORCE path always clears Danger)",
	},
	{
		"name": "light",
		"rate": 25,
		"title": "Light (25%)",
		"hint": "Fewer battles — sparse; often feels like a step-routed run",
	},
	{
		"name": "standard",
		"rate": 50,
		"title": "Standard (50%)",
		"hint": "Moderate — busier than Light; flat chance every check",
	},
	{
		"name": "dense",
		"rate": 75,
		"title": "Dense (75%)",
		"hint": "More battles — busy on purpose",
	},
)

_BY_NAME = {d["name"]: d["rate"] for d in DENSITIES}
_BY_RATE = {d["rate"]: d for d in DENSITIES}

RATE_HELP = (
	"off / light / standard / dense (or 0 / 25 / 50 / 75). "
	"Not a free-form % — only these shipped stubs."
)


def rate_label(rate: int) -> str:
	d = _BY_RATE.get(rate)
	return d["title"] if d else f"{rate}%"


def parse_one_density(token: str) -> int:
	"""Parse one density name or 25/50/75 → rate int."""
	raw = token.strip().lower()
	if not raw:
		raise SystemExit("Empty density value")
	if raw in _BY_NAME:
		return _BY_NAME[raw]
	if raw.endswith("%"):
		raw = raw[:-1].strip()
	if raw.isdigit():
		rate = int(raw)
		if rate in RATES:
			return rate
		raise SystemExit(
			f"Unknown density {token!r}. Use light, standard, dense "
			f"(or {', '.join(str(r) for r in RATES)}). Not a free-form %."
		)
	raise SystemExit(
		f"Unknown density {token!r}. Use light, standard, dense "
		f"(or {', '.join(str(r) for r in RATES)})."
	)


def parse_densities(spec: str) -> list[int]:
	"""Parse 'all', 'light', '25,75', 'light,dense', etc. → unique rates in order."""
	raw = spec.strip().lower()
	if raw in {"all", "*"}:
		return list(RATES)
	rates: list[int] = []
	for part in raw.replace(";", ",").split(","):
		part = part.strip()
		if not part:
			continue
		rate = parse_one_density(part)
		if rate not in rates:
			rates.append(rate)
	if not rates:
		raise SystemExit(f"No densities in {spec!r}")
	return rates


def print_density_menu(*, allow_all: bool) -> None:
	print()
	print("Field encounter density (shipped stubs — pick a preset, not a custom %):")
	print()
	for i, d in enumerate(DENSITIES, start=1):
		print(f"  [{i}] {d['title']:<16}  {d['hint']}")
	if allow_all:
		print(f"  [{len(DENSITIES) + 1}] All               Build Off + Light + Standard + Dense")
	print()


def prompt_densities(*, allow_all: bool = True, default: str = "standard") -> list[int]:
	"""Ask on a TTY. Returns one or more rates."""
	if not sys.stdin.isatty():
		raise SystemExit(
			"No density given and stdin is not a TTY.\n"
			f"Pass --density <preset> ({RATE_HELP})"
			+ (" or --density all" if allow_all else "")
			+ "."
		)

	print_density_menu(allow_all=allow_all)
	default_key = default.strip().lower()
	if allow_all and default_key in {"all", "*"}:
		default_rates = list(RATES)
		default_label = "All"
	else:
		default_rates = [parse_one_density(default_key)]
		default_label = _BY_RATE[default_rates[0]]["title"]
	all_idx = len(DENSITIES) + 1 if allow_all else None
	choices = "1-4" if allow_all else "1-3"
	prompt = (
		f"Pick {choices}, a name (light/standard/dense"
		+ ("/all" if allow_all else "")
		+ f"), or Enter for {default_label}: "
	)

	while True:
		choice = input(prompt).strip().lower()
		if not choice:
			return default_rates
		if allow_all and choice in {"all", "*", str(all_idx)}:
			return list(RATES)
		if choice.isdigit():
			n = int(choice)
			if 1 <= n <= len(DENSITIES):
				return [DENSITIES[n - 1]["rate"]]
			if allow_all and n == all_idx:
				return list(RATES)
			print(f"  Enter {choices}.")
			continue
		try:
			if allow_all and choice in {"all", "*"}:
				return list(RATES)
			return [parse_one_density(choice)]
		except SystemExit as exc:
			print(f"  {exc}")
