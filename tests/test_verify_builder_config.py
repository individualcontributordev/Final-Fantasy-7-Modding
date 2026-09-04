from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import verify_builder_config as verify
from libs import local_paths
from libs.local_paths import ensure_parent_image, remove_unlisted_disc_layers


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


class ParentCacheStampTests(unittest.TestCase):
    """A cached parent BIN is only trusted while it names the live base version.

    Without the stamp an old cache stands in for the current base, which shows
    up as a bogus "layer mismatch" during verify and, worse, as mod layers
    diffed against a disc CSR no longer publishes.
    """

    STALE = b"cache built against an older csr-plus"

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        patched = mock.patch.object(local_paths, "CACHE_DIR", tmp / "cache")
        patched.start()
        self.addCleanup(patched.stop)

        self.pristine = tmp / "pristine_d1.bin"
        self.pristine.write_bytes(b"pristine disc bytes")

        self.csr = tmp / "csr"
        layer = self.csr / "builder" / "csr-plus" / "layers" / "disc1.layer.json"
        layer.parent.mkdir(parents=True)
        layer.write_text(
            json.dumps(
                {
                    "format": "ic-layer-v1",
                    "records": [{"offset": 0, "hex": "70415443484544"}],
                }
            )
        )
        (self.csr / "builder" / "manifest.json").write_text(
            json.dumps(
                {
                    "bases": [
                        {
                            "id": "csr-plus",
                            "discs": {"1": "./csr-plus/layers/disc1.layer.json"},
                        }
                    ]
                }
            )
        )
        (self.csr / "builder" / "csr-plus" / "VERSION").write_text("0.2.6\n")

        self.cached = local_paths.cache_bin_path("csr-plus", 1)
        self.cached.parent.mkdir(parents=True)
        self.cached.write_bytes(self.STALE)

    def load(self) -> bytes:
        data, _path = ensure_parent_image(
            base_id="csr-plus", disc=1, pristine=self.pristine, csr=self.csr
        )
        return data

    def test_unstamped_cache_is_rebuilt(self) -> None:
        self.assertNotEqual(self.load(), self.STALE)
        stamp = local_paths.cache_stamp_path("csr-plus", 1)
        self.assertEqual(stamp.read_text().strip(), "0.2.6")

    def test_cache_from_an_older_version_is_rebuilt(self) -> None:
        local_paths.cache_stamp_path("csr-plus", 1).write_text("0.2.4\n")
        self.assertNotEqual(self.load(), self.STALE)

    def test_cache_matching_the_live_version_is_reused(self) -> None:
        local_paths.cache_stamp_path("csr-plus", 1).write_text("0.2.6\n")
        self.assertEqual(self.load(), self.STALE)


if __name__ == "__main__":
    unittest.main()
