"""apply_layer growth + 2352 alignment (no disc images)."""
from __future__ import annotations

import json

import pytest

SECTOR = 2352


def test_apply_layer_pads_to_modified_bytes_when_baseline_matches(apply_layer):
    base = bytearray(b"\x00" * (10 * SECTOR))
    # one record near end + stats saying image grew with trailing zeros omitted
    target = 12 * SECTOR  # aligned
    layer = {
        "format": "ic-layer-v1",
        "target": "disc-image",
        "stats": {"originalBytes": len(base), "modifiedBytes": target},
        "records": [
            {"offset": 10 * SECTOR - 4, "hex": "deadbeef"},
        ],
    }
    apply_layer(base, layer)
    assert len(base) == target
    assert len(base) % SECTOR == 0
    assert base[10 * SECTOR - 4 : 10 * SECTOR] == bytes.fromhex("deadbeef")


def test_apply_layer_sector_aligns_even_if_records_end_mid_sector(apply_layer):
    base = bytearray(b"\x00" * (8 * SECTOR))
    # grow by writing past end ending mid-sector; modifiedBytes slightly larger but
    # record max end unaligned — final image must still % 2352 == 0
    off = 8 * SECTOR + 100
    layer = {
        "format": "ic-layer-v1",
        "target": "disc-image",
        "stats": {
            "originalBytes": len(base),
            # intentional: modifiedBytes == max record end (unaligned)
            "modifiedBytes": off + 3,
        },
        "records": [{"offset": off, "hex": "aabbcc"}],
    }
    apply_layer(base, layer)
    assert base[off : off + 3] == bytes.fromhex("aabbcc")
    assert len(base) % SECTOR == 0
    assert len(base) >= off + 3


def test_apply_layer_skips_modifiedbytes_when_baseline_mismatch(apply_layer):
    # Cross-baseline: layer built on different size must not inflate from stats alone
    base = bytearray(b"\x00" * (5 * SECTOR))
    layer = {
        "format": "ic-layer-v1",
        "target": "disc-image",
        "stats": {"originalBytes": 99 * SECTOR, "modifiedBytes": 200 * SECTOR},
        "records": [{"offset": 10, "hex": "11"}],
    }
    apply_layer(base, layer)
    assert base[10] == 0x11
    # no stats growth; only tiny extend if records required it (they didn't past len)
    assert len(base) == 5 * SECTOR


def test_apply_layer_rejects_bad_format(apply_layer):
    img = bytearray(b"\x00" * SECTOR)
    with pytest.raises(SystemExit):
        apply_layer(img, {"format": "nope", "records": []})
