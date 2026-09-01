"""Reusable Highwind-specific stages for a collapsed, Makou-editable Disc 1.

Highwind and CSR+ share the same disc-safety stages:

* reserve enough FIELD.BIN space for Makou's normal gzip compressor;
* synchronize FIELD.BIN/WORLD.BIN lookup tables after DAT sizes change;
* inject SNOVA only after Makou editing;
* repair Mode2 Form1 EDC/ECC before producing a burn image;
* rebuild the published layer from its declared base and byte-compare it.

Only the source and field-collapse stages differ. Highwind starts from its
retired three-disc v0.2.0 layers, then restores the small set of field payloads
that the original collapsed release intentionally borrowed from CSR+.
"""
from __future__ import annotations

from pathlib import Path

from build_csrplus_staged import (
    SCENES,
    apply_layer,
    configure_sources,
    default_csr_root,
    fix_field_and_world_bins,
    git_json_at_ref,
    pristine,
    save_stage,
    sha256,
    write_json,
    write_new,
)
from psx_mode2_iso import extract_file, replace_file_within_sectors
from scan_all_field_collisions import list_field_dir

# This is the parent of the commit that collapsed Highwind to Disc 1 and
# deleted its Disc 2/3 layer files. Pinning the source avoids accidentally
# treating the already-collapsed output as a new multi-disc input.
HIGHWIND_SOURCE_REF = "e8f80fd1c4512d0c91a2f57134c1b92d2d3b46dd"
COLLAPSED_HIGHWIND_SOURCE_REF = "e21c84cdd96ee4523d295e44232962aeae10158d"
HIGHWIND_LAYER = "builder/highwind/layers/disc{disc}.layer.json"

# These are the only payloads Highwind intentionally inherited from CSR+.
# They are read from the pinned first collapsed Highwind release rather than
# today's CSR+ layer: BLIN70_4 and LOSLAKE1 have since diverged between the two
# bases, so following the live CSR+ layer would silently change Highwind.
SHARED_FIELD_PATHS = (
    "FIELD/BLACKBGB.DAT",
    *(path for scene in SCENES for path in scene["files"]),
)


def build_highwind_source_artifacts(csr: Path, output_dir: Path) -> dict:
    """Reconstruct three pre-collapse discs and the pinned shared-field source."""
    csr = csr.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    configure_sources(csr)
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")
    output_dir.mkdir(parents=True)

    input_dir = output_dir / "00-inputs"
    highwind_layers: dict[int, Path] = {}
    for disc in (1, 2, 3):
        layer = git_json_at_ref(
            csr,
            HIGHWIND_SOURCE_REF,
            HIGHWIND_LAYER.format(disc=disc),
        )
        layer_path = input_dir / "highwind-v0.2.0" / f"disc{disc}.layer.json"
        write_json(layer_path, layer)
        highwind_layers[disc] = layer_path

        image = bytearray(pristine(csr, disc).read_bytes())
        apply_layer(image, layer)
        write_new(
            output_dir / "01-highwind-multidisc" / f"FINALFANTASY7_D{disc}.bin",
            bytes(image),
        )

    collapsed_layer = git_json_at_ref(
        csr,
        COLLAPSED_HIGHWIND_SOURCE_REF,
        HIGHWIND_LAYER.format(disc=1),
    )
    collapsed_layer_path = (
        input_dir / "collapsed-highwind-v0.2.0" / "disc1.layer.json"
    )
    write_json(collapsed_layer_path, collapsed_layer)
    shared_image = bytearray(pristine(csr, 1).read_bytes())
    apply_layer(shared_image, collapsed_layer)
    shared_path = output_dir / "02-shared-fields-reference" / "FINALFANTASY7_D1.bin"
    write_new(shared_path, bytes(shared_image))

    report = {
        "stage": "highwind-sources",
        "highwindSourceCommit": HIGHWIND_SOURCE_REF,
        "highwindLayers": {
            str(disc): {
                "path": str(path),
                "sha256": sha256(path),
            }
            for disc, path in highwind_layers.items()
        },
        "highwindDiscs": str(output_dir / "01-highwind-multidisc"),
        "sharedFieldsSourceCommit": COLLAPSED_HIGHWIND_SOURCE_REF,
        "sharedFieldsLayer": {
            "path": str(collapsed_layer_path),
            "sha256": sha256(collapsed_layer_path),
        },
        "sharedFieldsImage": str(shared_path),
        "sharedFieldsImageSha256": sha256(shared_path),
        "sharedFields": list(SHARED_FIELD_PATHS),
    }
    write_json(output_dir / "stage-report.json", report)
    return report


def classify_highwind_merges(
    disc1: bytes,
    disc2: bytes,
    disc3: bytes,
) -> tuple[dict[str, int], list[dict]]:
    """Choose unambiguous later-disc fields and expose every ambiguous field.

    A field is automatically merged only when exactly one later disc differs
    from Disc 1. When both later discs differ, Disc 1 is retained. Even when
    Disc 2 and Disc 3 are byte-identical, selecting their version could replace
    an early-game script with a later-game state. This conservative rule
    matches the existing published Highwind collapse and records every skipped
    decision for later reverse-engineering.
    """
    images = {1: disc1, 2: disc2, 3: disc3}
    listings = {disc: list_field_dir(image) for disc, image in images.items()}
    all_names: set[str] = set()
    for listing in listings.values():
        all_names.update(listing)

    merges: dict[str, int] = {}
    collisions: list[dict] = []
    for name in sorted(all_names):
        present = [disc for disc in (1, 2, 3) if name in listings[disc]]
        if 1 not in present or len(present) < 2:
            continue

        path = f"FIELD/{name}.DAT"
        disc1_payload = extract_file(disc1, path)
        changed_later_discs = [
            disc
            for disc in present
            if disc != 1 and extract_file(images[disc], path) != disc1_payload
        ]
        if len(changed_later_discs) == 1:
            merges[name] = changed_later_discs[0]
            continue
        if len(changed_later_discs) < 2:
            continue

        disc2_payload = extract_file(disc2, path)
        disc3_payload = extract_file(disc3, path)
        disc2_equals_disc3 = disc2_payload == disc3_payload
        collisions.append(
            {
                "field": name,
                "laterDiscs": changed_later_discs,
                "disc2EqualsDisc3": disc2_equals_disc3,
                "decision": "keep-disc1",
                "reason": "Both later discs differ; preserve early-game behavior until reviewed.",
            }
        )
    return merges, collisions


def collapse_highwind_disc1(
    sources_dir: Path,
    output_dir: Path,
) -> tuple[Path, dict]:
    """Merge Highwind fields by ISO path and produce a table-consistent Disc 1."""
    sources_dir = sources_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    highwind_dir = sources_dir / "01-highwind-multidisc"
    shared_path = (
        sources_dir / "02-shared-fields-reference" / "FINALFANTASY7_D1.bin"
    )

    paths = {
        disc: highwind_dir / f"FINALFANTASY7_D{disc}.bin"
        for disc in (1, 2, 3)
    }
    for required in (*paths.values(), shared_path):
        if not required.is_file():
            raise SystemExit(f"Missing source artifact: {required}")
    if output_dir.exists():
        raise SystemExit(f"Output directory already exists: {output_dir}")

    highwind = {disc: paths[disc].read_bytes() for disc in (1, 2, 3)}
    image = bytearray(highwind[1])
    save_stage(output_dir, "01-highwind-disc1.bin", image)

    merges, collisions = classify_highwind_merges(
        highwind[1],
        highwind[2],
        highwind[3],
    )
    for field, source_disc in sorted(merges.items()):
        path = f"FIELD/{field}.DAT"
        payload = extract_file(highwind[source_disc], path)
        try:
            replace_file_within_sectors(image, path, payload)
        except ValueError as error:
            # Silently skipping a field would create a plausible-looking but
            # incomplete single-disc build. Stop and preserve the prior stage.
            raise SystemExit(
                f"Highwind {path} from Disc {source_disc} does not fit Disc 1: {error}"
            ) from error
    merged_path = save_stage(output_dir, "02-unambiguous-d2-d3-fields.bin", image)

    shared_image = shared_path.read_bytes()
    for path in SHARED_FIELD_PATHS:
        payload = extract_file(shared_image, path)
        replace_file_within_sectors(image, path, payload)
        if extract_file(image, path) != payload:
            raise SystemExit(f"Shared field injection did not round-trip: {path}")
    shared_fields_path = save_stage(output_dir, "03-shared-fields.bin", image)

    table_patches = fix_field_and_world_bins(image)
    final_path = save_stage(output_dir, "04-field-world-tables-fixed.bin", image)

    # This stage rebuilds the existing Highwind baseline before the user adds
    # new Makou edits. Compare every DAT payload—not raw sectors, whose
    # directory tables and EDC/ECC are intentionally normalized later.
    reference_fields = set(list_field_dir(shared_image))
    rebuilt_fields = set(list_field_dir(image))
    field_names = sorted(reference_fields | rebuilt_fields)
    mismatched_fields = []
    for field in field_names:
        path = f"FIELD/{field}.DAT"
        is_missing = field not in reference_fields or field not in rebuilt_fields
        if is_missing:
            mismatched_fields.append(field)
            continue

        reference_payload = extract_file(shared_image, path)
        rebuilt_payload = extract_file(image, path)
        if reference_payload != rebuilt_payload:
            mismatched_fields.append(field)
    if mismatched_fields:
        names = ", ".join(mismatched_fields)
        raise SystemExit(f"Rebuilt Highwind field payloads changed unexpectedly: {names}")

    report = {
        "stage": "highwind-collapse",
        "sourcesDir": str(sources_dir),
        "unambiguousMerges": len(merges),
        "mergeSources": merges,
        "reviewedPolicy": "keep Disc 1 whenever both later discs differ",
        "collisionsKeptFromDisc1": collisions,
        "sharedFieldSource": str(shared_path),
        "sharedFields": list(SHARED_FIELD_PATHS),
        "tableEntriesPatched": table_patches,
        "publishedFieldPayloadComparison": {
            "fieldsCompared": len(field_names),
            "differences": 0,
            "status": "pass",
        },
        "artifacts": {
            "afterHighwindMerge": str(merged_path),
            "afterSharedFields": str(shared_fields_path),
            "tableFixed": str(final_path),
        },
        "outputSha256": sha256(final_path),
    }
    write_json(output_dir / "stage-report.json", report)
    return final_path, report


def default_csr() -> Path:
    return default_csr_root()
