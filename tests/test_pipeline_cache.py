from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pytest

SINGLE_DISC_SCRIPTS = (
    Path(__file__).resolve().parents[1] / "mods" / "single-disc" / "scripts"
)
sys.path.insert(0, str(SINGLE_DISC_SCRIPTS))

from build_csrplus_staged import finalize as finalize_csrplus  # noqa: E402
from build_highwind_staged import finalize as finalize_highwind  # noqa: E402
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


@pytest.mark.parametrize(
    ("base", "filename", "finalize"),
    (
        ("csr-plus", "CSRPLUS_D1.bin", finalize_csrplus),
        ("highwind", "HIGHWIND_D1.bin", finalize_highwind),
    ),
)
def test_finalize_rejects_an_overwritten_working_baseline(
    tmp_path: Path,
    csr_root: Path,
    base: str,
    filename: str,
    finalize,
) -> None:
    run_dir = tmp_path / base
    working_dir = run_dir / "03-working"
    working_dir.mkdir(parents=True)
    baseline = working_dir / filename
    baseline.write_bytes(b"accidental Makou save")
    (working_dir / "stage-report.json").write_text(
        json.dumps({"outputSha256": hashlib.sha256(b"original").hexdigest()}),
        encoding="utf-8",
    )
    edited = tmp_path / f"{base}-edited.bin"
    edited.write_bytes(b"edited")
    args = argparse.Namespace(
        csr_root=csr_root,
        run_dir=run_dir,
        edited_image=edited,
    )

    with pytest.raises(SystemExit, match="--resume"):
        finalize(args)
