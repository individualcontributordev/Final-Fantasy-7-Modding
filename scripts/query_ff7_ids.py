#!/usr/bin/env python3
"""Query FF7 field, movie, and music IDs.

Loads reference data from docs/reference/ and provides lookup utilities.

Usage:
  python3 scripts/query_ff7_ids.py field 637
  python3 scripts/query_ff7_ids.py movie 0x2f
  python3 scripts/query_ff7_ids.py music 82
  python3 scripts/query_ff7_ids.py field loslake1
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_field_mapping() -> dict[int, str]:
    """Load field ID -> name mapping."""
    mapping = {}
    path = ROOT / "docs/reference/field-id-mapping.txt"
    
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            field_id = int(parts[0])
            name = parts[1]
            mapping[field_id] = name
    
    return mapping


def load_movie_mapping() -> dict[int, tuple[str, str]]:
    """Load movie ID -> (filename, disc) mapping."""
    mapping = {}
    path = ROOT / "docs/reference/movie-id-mapping.txt"
    
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 3:
            movie_id = int(parts[0])
            filename = parts[1]
            disc = parts[2]
            mapping[movie_id] = (filename, disc)
    
    return mapping


def load_music_mapping() -> dict[int, tuple[str, str]]:
    """Load music ID -> (internal_name, full_title) mapping."""
    mapping = {}
    path = ROOT / "docs/reference/music-id-mapping.txt"
    
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Format: ID INTERNAL_NAME "FULL_TITLE"
        parts = line.split(maxsplit=2)
        if len(parts) >= 3:
            music_id = int(parts[0])
            internal = parts[1]
            full = parts[2].strip('"')
            mapping[music_id] = (internal, full)
    
    return mapping


def query_field(query: str):
    """Query field by ID or name."""
    fields = load_field_mapping()
    reverse = {v: k for k, v in fields.items()}
    
    # Try as ID first
    try:
        if query.startswith('0x'):
            field_id = int(query, 16)
        else:
            field_id = int(query)
        
        if field_id in fields:
            print(f"Field ID {field_id} (0x{field_id:03X}): {fields[field_id]}")
        else:
            print(f"Field ID {field_id} not found (valid range: 0-787)")
    except ValueError:
        # Try as name
        query_lower = query.lower()
        if query_lower in reverse:
            field_id = reverse[query_lower]
            print(f"Field '{query_lower}': ID {field_id} (0x{field_id:03X})")
        else:
            # Fuzzy search
            matches = [name for name in fields.values() if query_lower in name.lower()]
            if matches:
                print(f"Fields matching '{query}':")
                for name in matches[:10]:
                    field_id = reverse[name]
                    print(f"  {field_id:3d} (0x{field_id:03X}): {name}")
                if len(matches) > 10:
                    print(f"  ... and {len(matches) - 10} more")
            else:
                print(f"No fields found matching '{query}'")


def query_movie(query: str):
    """Query movie by ID."""
    movies = load_movie_mapping()
    
    try:
        if query.startswith('0x'):
            movie_id = int(query, 16)
        else:
            movie_id = int(query)
        
        if movie_id in movies:
            filename, disc = movies[movie_id]
            print(f"Movie ID {movie_id} (0x{movie_id:02X}): {filename}")
            print(f"  Disc: {disc}")
            print(f"  PMVIE opcode: f8{movie_id:02x}")
        else:
            print(f"Movie ID {movie_id} not found (valid range: 0-105)")
    except ValueError:
        print(f"Invalid movie ID: {query}")


def query_music(query: str):
    """Query music by ID."""
    music = load_music_mapping()
    
    try:
        if query.startswith('0x'):
            music_id = int(query, 16)
        else:
            music_id = int(query)
        
        if music_id in music:
            internal, full = music[music_id]
            print(f"Music ID {music_id} (0x{music_id:02X}): {internal}")
            print(f"  Title: \"{full}\"")
            print(f"  MUSIC opcode: f0{music_id:02x}")
        else:
            print(f"Music ID {music_id} not found (valid range: 0-99)")
    except ValueError:
        print(f"Invalid music ID: {query}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("type", choices=["field", "movie", "music"],
                    help="Type of ID to query")
    ap.add_argument("query", help="ID (decimal or hex with 0x prefix) or name")
    args = ap.parse_args()
    
    if args.type == "field":
        query_field(args.query)
    elif args.type == "movie":
        query_movie(args.query)
    elif args.type == "music":
        query_music(args.query)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
