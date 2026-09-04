from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_builder_config as verify


class VerifyTargetTests(unittest.TestCase):
    def test_all_includes_clean(self) -> None:
        self.assertEqual(
            verify.expand_base_names(["all"]),
            ["csr", "csr-plus", "highwind", "clean"],
        )

    def test_csr_family_skips_clean(self) -> None:
        self.assertEqual(
            verify.expand_base_names(["csr-family"]),
            ["csr", "csr-plus", "highwind"],
        )

    def test_repeated_bases_collapse(self) -> None:
        self.assertEqual(
            verify.expand_base_names(["all", "clean", "csr"]),
            ["csr", "csr-plus", "highwind", "clean"],
        )

    def test_unknown_base_fails(self) -> None:
        with self.assertRaises(SystemExit):
            verify.expand_base_names(["csr+"])

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


if __name__ == "__main__":
    unittest.main()
