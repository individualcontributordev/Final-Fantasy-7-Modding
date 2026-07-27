#!/usr/bin/env python3
"""Deprecated alias — use scripts/compress_gzipps.py."""

from compress_gzipps import compress_field_bin, compress_gzipps, main

__all__ = ["compress_gzipps", "compress_field_bin", "main"]

if __name__ == "__main__":
	main()
