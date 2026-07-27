#!/usr/bin/env python3
"""Deprecated alias — use scripts/decompress_gzipps.py."""

from decompress_gzipps import decompress_field_bin, decompress_gzipps, main

__all__ = ["decompress_gzipps", "decompress_field_bin", "main"]

if __name__ == "__main__":
	main()
