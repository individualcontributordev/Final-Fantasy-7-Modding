from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_builder_config as verify
from libs.local_paths import remove_unlisted_disc_layers


class VerifyTargetTests(unittest.TestCase):
    def test_all_includes_clean(self) -> None:
        self.assertEqual(
            verify.expand_base_names(["all"]),
            ["csr", "csr-plus", "highwind", "clean"],
        )

    def test_repeated_bases_collapse(self) -> None:
        self.assertEqual(
            verify.expand_base_names(["all", "clean", "csr"]),
            ["csr", "csr-plus", "highwind", "clean"],
        )

    def test_unknown_base_fails(self) -> None:
        for name in ("csr+", "csr-family"):
            with self.subTest(name=name), self.assertRaises(SystemExit):
                verify.expand_base_names([name])

    def test_addons_follow_compatible_bases(self) -> None:
        manifest = {
            "addons": [
                {"id": "field-encounter-0", "compatibleBases": ["clean"]},
                {"id": "field-encounter-on-csr-0", "compatibleBases": ["csr"]},
                {"id": "field-encounter-on-highwind-0", "compatibleBases": ["highwind"]},
            ]
        }
        self.assertEqual(verify.addons_for_base(manifest, "clean"), ["field-encounter-0"])
        self.assertEqual(
            verify.addons_for_base(manifest, "csr"),
            ["field-encounter-on-csr-0"],
        )

    def test_clean_discs_are_all_three(self) -> None:
        self.assertEqual(verify.discs_for_base("clean", None), [1, 2, 3])

    def test_csr_plus_discs_come_from_csr_manifest(self) -> None:
        csr = {"bases": [{"id": "csr-plus", "discs": {"1": "./csr-plus/layers/disc1.layer.json"}}]}
        self.assertEqual(verify.discs_for_base("csr-plus", csr), [1])

    def test_rebuild_removes_layers_for_unsupported_discs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            layers = Path(tmp)
            disc1 = layers / "disc1.layer.json"
            disc2 = layers / "disc2.layer.json"
            notes = layers / "notes.txt"
            for path in (disc1, disc2, notes):
                path.write_text(path.name)

            removed = remove_unlisted_disc_layers(layers, [1])

            self.assertEqual(removed, [disc2])
            self.assertTrue(disc1.exists())
            self.assertTrue(notes.exists())
            self.assertFalse(disc2.exists())


if __name__ == "__main__":
    unittest.main()
