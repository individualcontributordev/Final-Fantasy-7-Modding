from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ff7mod
from libs.local_paths import expand_base_names


class ExpandUnmodifiedTests(unittest.TestCase):
    def test_unmodified_is_clean(self) -> None:
        self.assertEqual(expand_base_names(["unmodified"]), ["clean"])

    def test_all_still_uses_catalog_id_clean(self) -> None:
        self.assertEqual(
            expand_base_names(["all"]),
            ["csr", "csr-plus", "highwind", "clean"],
        )


class ScaffoldNewModTests(unittest.TestCase):
    def test_writes_unmodified_stub_and_copies_pristine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pristine = root / "workspace" / "pristine"
            pristine.mkdir(parents=True)
            (pristine / "FINALFANTASY7_D1.bin").write_bytes(b"DISC1")
            (pristine / "FINALFANTASY7_D2.bin").write_bytes(b"DISC2")

            written = ff7mod.scaffold(
                root=root,
                pack_id="diamond-weapon-speed",
                name="Diamond Weapon Speed",
                blurb="Walks to land faster.",
                hint="World-map Diamond Weapon only.",
                version="0.1.0",
                discs=[1, 2],
            )

            pack = json.loads(
                (root / "builder" / "diamond-weapon-speed" / "pack.json").read_text()
            )
            self.assertEqual(pack["id"], "diamond-weapon-speed")
            self.assertEqual(pack["compatibleBases"], ["clean"])
            self.assertNotIn("discs", pack)
            self.assertEqual(
                (root / "mods" / "diamond-weapon-speed" / "VERSION").read_text(),
                "0.1.0\n",
            )
            cache = root / "cache" / "diamond-weapon-speed"
            self.assertEqual((cache / "FINALFANTASY7_D1.bin").read_bytes(), b"DISC1")
            self.assertEqual((cache / "FINALFANTASY7_D2.bin").read_bytes(), b"DISC2")
            self.assertTrue((root / "mods" / "diamond-weapon-speed" / "scripts").is_dir())
            self.assertTrue(any(p.name.endswith(".bin") for p in written))

    def test_refuses_existing_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kwargs = dict(
                root=root,
                pack_id="example-mod",
                name="Example",
                blurb="Blurb",
                hint="Hint",
                version="0.1.0",
                discs=[1],
                copy_bins=False,
            )
            ff7mod.scaffold(**kwargs)
            with self.assertRaises(SystemExit):
                ff7mod.scaffold(**kwargs)

    def test_missing_pristine_explains_itself(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit) as raised:
                ff7mod.scaffold(
                    root=Path(tmp),
                    pack_id="example-mod",
                    name="Example",
                    blurb="Blurb",
                    hint="Hint",
                    version="0.1.0",
                    discs=[1],
                )
            self.assertIn("workspace/pristine", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
