from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from libs.layer import apply_layer, build_layer
from repair_mode2_edc import SECTOR, generate_mode2_form1_edc_ecc, repair

import build_base_layer


def mode2_sector(*, form2: bool) -> bytearray:
    sector = bytearray(SECTOR)
    sector[0:12] = b"\x00" + (b"\xff" * 10) + b"\x00"
    sector[15] = 2
    if form2:
        sector[18] = 0x20
        sector[22] = 0x20
    return sector


class ApplyLayerTests(unittest.TestCase):
    def test_pads_to_modified_size_when_baseline_matches(self) -> None:
        base = bytearray(10 * SECTOR)
        target = 12 * SECTOR
        layer = {
            "format": "ic-layer-v1",
            "stats": {"originalBytes": len(base), "modifiedBytes": target},
            "records": [{"offset": 10 * SECTOR - 4, "hex": "deadbeef"}],
        }

        apply_layer(base, layer)

        self.assertEqual(len(base), target)
        self.assertEqual(base[10 * SECTOR - 4 : 10 * SECTOR], bytes.fromhex("deadbeef"))

    def test_aligns_records_to_a_sector(self) -> None:
        base = bytearray(8 * SECTOR)
        offset = 8 * SECTOR + 100
        layer = {
            "format": "ic-layer-v1",
            "stats": {"originalBytes": len(base), "modifiedBytes": offset + 3},
            "records": [{"offset": offset, "hex": "aabbcc"}],
        }

        apply_layer(base, layer)

        self.assertEqual(base[offset : offset + 3], bytes.fromhex("aabbcc"))
        self.assertEqual(len(base) % SECTOR, 0)

    def test_ignores_size_from_another_baseline(self) -> None:
        base = bytearray(5 * SECTOR)
        layer = {
            "format": "ic-layer-v1",
            "stats": {
                "originalBytes": 99 * SECTOR,
                "modifiedBytes": 200 * SECTOR,
            },
            "records": [{"offset": 10, "hex": "11"}],
        }

        apply_layer(base, layer)

        self.assertEqual(base[10], 0x11)
        self.assertEqual(len(base), 5 * SECTOR)

    def test_rejects_bad_format(self) -> None:
        with self.assertRaises(SystemExit):
            apply_layer(bytearray(SECTOR), {"format": "nope", "records": []})


class RepairTests(unittest.TestCase):
    def repair(self, pristine_data: bytes, image_data: bytes) -> bytes:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pristine = root / "pristine.bin"
            image = root / "image.bin"
            output = root / "output.bin"
            pristine.write_bytes(pristine_data)
            image.write_bytes(image_data)
            repair(pristine, image, output)
            return output.read_bytes()

    def test_changed_form2_payload_is_untouched(self) -> None:
        pristine_sector = mode2_sector(form2=True)
        image_sector = bytearray(pristine_sector)
        image_sector[2200:2204] = b"XA!!"

        repaired = self.repair(bytes(pristine_sector), bytes(image_sector))

        self.assertEqual(repaired, image_sector)

    def test_changed_form1_payload_with_pristine_footer_is_recomputed(self) -> None:
        pristine_sector = mode2_sector(form2=False)
        generate_mode2_form1_edc_ecc(pristine_sector)
        image_sector = bytearray(pristine_sector)
        image_sector[24:28] = b"EDIT"

        expected = bytearray(image_sector)
        generate_mode2_form1_edc_ecc(expected)
        repaired = self.repair(bytes(pristine_sector), bytes(image_sector))

        self.assertEqual(repaired, expected)

    def test_appended_form1_sector_gets_fresh_footer(self) -> None:
        pristine_sector = mode2_sector(form2=False)
        generate_mode2_form1_edc_ecc(pristine_sector)
        appended = mode2_sector(form2=False)
        appended[24:28] = b"DATA"

        expected = bytearray(appended)
        generate_mode2_form1_edc_ecc(expected)
        repaired = self.repair(bytes(pristine_sector), bytes(pristine_sector + appended))

        self.assertEqual(repaired[SECTOR:], expected)


class BuildAddonLayerTests(unittest.TestCase):
    def test_round_trip_against_parent_not_pristine(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            builder = root / "builder"
            pack_dir = builder / "fanfare-skip-on-csr-plus"
            pack_dir.mkdir(parents=True)
            (pack_dir / "pack.json").write_text(
                json.dumps(
                    {
                        "id": "fanfare-skip-on-csr-plus",
                        "name": "Fanfare Skip",
                        "kind": "mod",
                        "version": "0.1.6",
                        "compatibleBases": ["csr-plus"],
                        "discs": {"1": "./layers/disc1.layer.json"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            parent = bytearray(SECTOR)
            parent[100:104] = b"BASE"
            patched = bytearray(parent)
            patched[200:204] = b"MOD!"

            parent_path = root / "parent.bin"
            image_dir = root / "fanfare-skip-on-csr-plus"
            image_dir.mkdir()
            image_path = image_dir / "FINALFANTASY7_D1.bin"
            parent_path.write_bytes(parent)
            image_path.write_bytes(patched)

            layer = build_layer(
                parent_path,
                image_path,
                layer_id="test",
                description="test",
            )
            build_base_layer.verify(parent_path, layer, image_path)

            check = bytearray(parent)
            apply_layer(check, layer)
            self.assertEqual(check, patched)

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_base_layer.py"),
                    str(image_path),
                    "--version",
                    "0.1.7",
                    "--parent",
                    str(parent_path),
                    "--base-version",
                    "0.2.1",
                    "--builder-dir",
                    str(builder),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("OK -- layer apply matches patched image", result.stdout)
            published = json.loads(
                (pack_dir / "layers" / "disc1.layer.json").read_text(encoding="utf-8")
            )
            self.assertGreater(published["stats"]["records"], 0)
            manifest = json.loads((builder / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["addons"][0]["id"], "fanfare-skip-on-csr-plus")
            self.assertEqual(manifest["addons"][0]["version"], "0.1.7")
            # The builder hides a mod unless this names the current base build.
            self.assertEqual(manifest["addons"][0]["baseVersion"], "0.2.1")
            pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
            self.assertEqual(pack["baseVersion"], "0.2.1")

            # The builder keys its layer cache on this digest, so it has to be
            # the hash of the bytes actually published.
            expected = hashlib.sha256(
                (pack_dir / "layers" / "disc1.layer.json").read_bytes()
            ).hexdigest()
            self.assertEqual(pack["discDigests"]["1"], expected)
            self.assertEqual(manifest["addons"][0]["discDigests"]["1"], expected)


if __name__ == "__main__":
    unittest.main()
