from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SINGLE_DISC_SCRIPTS = (
    Path(__file__).resolve().parents[1] / "mods" / "single-disc" / "scripts"
)
sys.path.insert(0, str(SINGLE_DISC_SCRIPTS))

from pipeline_cache import archive_path, cached_artifacts, cached_output  # noqa: E402


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cached_output_rejects_an_edited_file(tmp_path: Path) -> None:
    output = tmp_path / "working.bin"
    output.write_bytes(b"unchanged checkpoint")
    report = tmp_path / "stage-report.json"
    report.write_text(
        json.dumps({"outputSha256": file_sha256(output)}),
        encoding="utf-8",
    )

    valid, _, _ = cached_output(
        report_path=report,
        output_path=output,
        sha256_file=file_sha256,
    )
    assert valid

    output.write_bytes(b"accidental Makou save")
    valid, _, reason = cached_output(
        report_path=report,
        output_path=output,
        sha256_file=file_sha256,
    )
    assert not valid
    assert "output hash changed" in reason


def test_cached_artifacts_checks_every_declared_output(tmp_path: Path) -> None:
    first = tmp_path / "disc1.bin"
    second = tmp_path / "disc2.bin"
    first.write_bytes(b"disc one")
    second.write_bytes(b"disc two")
    report = tmp_path / "stage-report.json"
    report.write_text(
        json.dumps(
            {
                "cacheArtifacts": {
                    first.name: file_sha256(first),
                    second.name: file_sha256(second),
                }
            }
        ),
        encoding="utf-8",
    )

    valid, _, _ = cached_artifacts(
        report_path=report,
        stage_dir=tmp_path,
        sha256_file=file_sha256,
    )
    assert valid

    second.write_bytes(b"changed")
    valid, _, reason = cached_artifacts(
        report_path=report,
        stage_dir=tmp_path,
        sha256_file=file_sha256,
    )
    assert not valid
    assert second.name in reason


def test_archive_path_preserves_existing_work(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    working = run_dir / "03-working"
    working.mkdir(parents=True)
    (working / "edited.bin").write_bytes(b"user edits")

    archived = archive_path(working, run_dir)

    assert archived is not None
    assert not working.exists()
    assert (archived / "edited.bin").read_bytes() == b"user edits"
