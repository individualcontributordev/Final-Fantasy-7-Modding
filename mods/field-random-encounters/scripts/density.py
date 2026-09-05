#!/usr/bin/env python3
"""Define the shipped field-encounter choices used by build CLIs.

The rate integer is how often battles come compared with the unmodified game,
not a scale applied to any byte: 50 is about half as many, 200 about twice as
many. Unmodified is the builder's no-mod option, and its rate ramps between
battles off a step counter runners can route around; every stub here replaces
that ramp with a flat timer roll, so no selection is routable.

A flat roll cannot track the ramp exactly, so the thresholds are calibrated
while running, which is where players spend their time. Walking fields come out
somewhat busier than the label promises."""

from __future__ import annotations

import sys

# Pack id / stub files use these integers (field-encounter-50, not a free %).
RATES = (0, 50, 100, 200)

DENSITIES: tuple[dict, ...] = (
	{
		"name": "off",
		"rate": 0,
		"title": "No Encs",
		"hint": "No random field battles (FORCE path always clears Danger)",
	},
	{
		"name": "half",
		"rate": 50,
		"title": "Half Enc Rate",
		"hint": "About half the battles of the unmodified game",
	},
	{
		"name": "vanilla",
		"rate": 100,
		"title": "Vanilla Enc Rate",
		"hint": "About as many battles as the unmodified game, but unroutable",
	},
	{
		"name": "double",
		"rate": 200,
		"title": "Double Enc Rate",
		"hint": "About twice the battles of the unmodified game",
	},
)

_BY_NAME = {d["name"]: d["rate"] for d in DENSITIES}
_BY_RATE = {d["rate"]: d for d in DENSITIES}

# Derived so adding a density cannot leave stale text in prompts or errors.
_NAME_LIST = ", ".join(d["name"] for d in DENSITIES)
_NAME_SLASHES = "/".join(d["name"] for d in DENSITIES)
_RATE_LIST = " / ".join(str(r) for r in RATES)

RATE_HELP = (
	f"{_NAME_SLASHES} (or {_RATE_LIST}). "
	"Not a free-form % -- only these shipped stubs."
)


def rate_label(rate: int) -> str:
	d = _BY_RATE.get(rate)
	return d["title"] if d else f"{rate}%"


def parse_one_density(token: str) -> int:
	"""Parse one choice name or 0/50/100/200 -> rate int."""
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
			f"Unknown density {token!r}. Use {_NAME_LIST} "
			f"(or {_RATE_LIST}). Not a free-form %."
		)
	raise SystemExit(
		f"Unknown density {token!r}. Use {_NAME_LIST} (or {_RATE_LIST})."
	)


def parse_densities(spec: str) -> list[int]:
	"""Parse 'all', 'half', '0,100', etc. into unique rates in request order."""
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
	print("Field encounter density (shipped stubs -- pick a named rate, not a custom %):")
	print()
	for i, d in enumerate(DENSITIES, start=1):
		print(f"  [{i}] {d['title']:<16}  {d['hint']}")
	if allow_all:
		titles = " + ".join(d["title"] for d in DENSITIES)
		print(f"  [{len(DENSITIES) + 1}] {'All':<16}  Build {titles}")
	print()


def prompt_densities(*, allow_all: bool = True, default: str = "half") -> list[int]:
	"""Ask on a TTY. Returns one or more rates."""
	if not sys.stdin.isatty():
		raise SystemExit(
			"No density given and stdin is not a TTY.\n"
			f"Pass --density <name> ({RATE_HELP})"
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
	last_idx = all_idx if allow_all else len(DENSITIES)
	choices = f"1-{last_idx}"
	prompt = (
		f"Pick {choices}, a name ({_NAME_SLASHES}"
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
