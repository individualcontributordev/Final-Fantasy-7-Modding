#!/usr/bin/env python3
"""Parse the fixed world-map encounter choices used by build CLIs.

Vanilla means no mod layer. The shipped patches disable encounters, halve the
area threshold, or double it with saturation. Inputs may be names, 0/50/200
values, lists, or ``all``."""
from __future__ import annotations

import sys

RATES = (0, 50, 200)
DENSITIES = (
	("off", 0, "No Encs"),
	("half", 50, "Half Enc Rate"),
	("double", 200, "Double Enc Rate"),
)
RATE_BY_NAME = {name: rate for name, rate, _label in DENSITIES}
LABEL_BY_RATE = {rate: label for _name, rate, label in DENSITIES}


def rate_label(rate: int) -> str:
	return LABEL_BY_RATE.get(rate, f"{rate}%")


def parse_one_density(token: str) -> int:
	"""Map a shipped name or 0/50/200 token to the stub/pack-id integer."""
	value = token.strip().lower().removesuffix("%").strip()
	if value in RATE_BY_NAME:
		return RATE_BY_NAME[value]
	if value.isdigit() and int(value) in RATES:
		return int(value)
	raise SystemExit(
		f"Unknown density {token!r}. Use off, half, double, or 0, 50, 200."
	)


def parse_densities(spec: str) -> list[int]:
	"""Parse one token, a comma list, or all into unique shipped rates in request order."""
	value = spec.strip().lower()
	if value in {"all", "*"}:
		return list(RATES)
	rates: list[int] = []
	for part in value.replace(";", ",").split(","):
		if not part.strip():
			continue
		rate = parse_one_density(part)
		if rate not in rates:
			rates.append(rate)
	if not rates:
		raise SystemExit(f"No densities in {spec!r}")
	return rates


def prompt_densities(*, allow_all: bool = True, default: str = "half") -> list[int]:
	"""TTY-only selection of shipped rates; non-TTY callers must pass --density."""
	if not sys.stdin.isatty():
		raise SystemExit("Pass --density off|half|double|all")

	options = list(DENSITIES)
	for index, (_name, _rate, label) in enumerate(options, start=1):
		print(f"  [{index}] {label}")
	if allow_all:
		print(f"  [{len(options) + 1}] All")

	default_rates = parse_densities(default)
	while True:
		choice = input(f"Density [default {default}]: ").strip().lower()
		if not choice:
			return default_rates
		if allow_all and choice in {"all", "*", str(len(options) + 1)}:
			return list(RATES)
		if choice.isdigit() and 1 <= int(choice) <= len(options):
			return [options[int(choice) - 1][1]]
		try:
			return parse_densities(choice)
		except SystemExit as error:
			print(f"  {error}")
