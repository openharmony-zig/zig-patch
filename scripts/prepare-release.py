#!/usr/bin/env python3
"""Prepare the same release asset formats as the project's 0.16.0 release."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import lzma
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 4 * 1024 * 1024


def digest_stream(stream):
    digest = hashlib.sha256()
    while chunk := stream.read(CHUNK_SIZE):
        digest.update(chunk)
    return digest.hexdigest()


def digest_file(path):
    with path.open("rb") as stream:
        return digest_stream(stream)


def prepare_product(product, source, stage, manifest):
    kind, target = product
    package = f"zig-{target['zig_target']}-{target['cpu']}"
    archive = source / f"{package}.tar.xz"
    checksum = archive.with_name(archive.name + ".sha256")
    declared = checksum.read_text().split()
    digest = digest_file(archive)
    if declared != [digest, archive.name]:
        raise ValueError(f"archive checksum mismatch: {archive.name}")

    metadata = {}
    compiler_found = False
    with tarfile.open(archive, "r|xz") as payload:
        for member in payload:
            if member.name != package and not member.name.startswith(package + "/"):
                raise ValueError(f"unexpected archive root: {archive.name}")
            if member.name == f"{package}/{target['executable']}":
                compiler_found = member.isfile() and member.size > 0
            if member.name in (
                f"{package}/OHOS-MANIFEST.json",
                f"{package}/BUILD-INFO.txt",
            ):
                stream = payload.extractfile(member)
                if stream is None:
                    raise ValueError(f"missing package metadata: {member.name}")
                metadata[member.name.rsplit("/", 1)[-1]] = stream.read().decode()
    if not compiler_found:
        raise ValueError(f"compiler missing from {archive.name}")
    if json.loads(metadata["OHOS-MANIFEST.json"]) != manifest:
        raise ValueError(f"package manifest differs from source: {archive.name}")
    info = dict(line.split("=", 1) for line in metadata["BUILD-INFO.txt"].splitlines())
    expected_info = {
        "zig_version": manifest["zig"]["version"],
        "package_kind": kind,
        "package_name": package,
        "target": target["zig_target"],
        "cpu": target["cpu"],
        "bootstrap_base": manifest["zig"]["bootstrap_base_commit"],
    }
    if info != expected_info:
        raise ValueError(f"package build metadata mismatch: {archive.name}")

    shutil.copy2(archive, stage / archive.name)
    if digest_file(stage / archive.name) != digest:
        raise ValueError(f"copy checksum mismatch: {archive.name}")
    (stage / checksum.name).write_text(f"{digest}  {archive.name}\n")
    assets = [
        {"name": archive.name, "sha256": digest, "size": archive.stat().st_size},
        {
            "name": checksum.name,
            "sha256": digest_file(stage / checksum.name),
            "size": (stage / checksum.name).stat().st_size,
        },
    ]
    if kind == "host":
        gzip_path = stage / f"{package}.tar.gz"
        tar_digest = hashlib.sha256()
        with lzma.open(archive, "rb") as original, gzip_path.open("wb") as output:
            with gzip.GzipFile(filename="", mode="wb", fileobj=output, compresslevel=6, mtime=0) as packed:
                while chunk := original.read(CHUNK_SIZE):
                    tar_digest.update(chunk)
                    packed.write(chunk)
        with gzip.open(gzip_path, "rb") as unpacked:
            if digest_stream(unpacked) != tar_digest.hexdigest():
                raise ValueError(f"gzip/xz payload mismatch: {gzip_path.name}")
        assets.append(
            {
                "name": gzip_path.name,
                "sha256": digest_file(gzip_path),
                "size": gzip_path.stat().st_size,
                "tar_payload_sha256": tar_digest.hexdigest(),
                "same_payload_as": archive.name,
            }
        )
    return assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "zig-bootstrap/dist")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--only", choices=("all", "host", "native"), default="all")
    parser.add_argument("--targets", default="all", help="comma-separated manifest names")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "zig-bootstrap/ohos/manifest.json").read_text())
    version = manifest["zig"]["version"]
    base = manifest["zig"]["bootstrap_base_commit"]
    head = subprocess.check_output(
        ["git", "-C", str(ROOT / "zig-bootstrap"), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != base:
        raise ValueError(f"bootstrap base mismatch: expected {base}, got {head}")
    selection = None if args.targets == "all" else set(args.targets.split(","))
    products = []
    available_names = set()
    for kind, key in (("host", "host_targets"), ("native", "native_zig_targets")):
        if args.only not in ("all", kind):
            continue
        for target in manifest[key]:
            available_names.add(target["name"])
            if selection is None or target["name"] in selection:
                products.append((kind, target))
    if not products or (selection is not None and selection - available_names):
        raise ValueError("target selection does not match the requested manifest set")
    output = (args.output_dir or ROOT / "dist/releases" / version).resolve()
    output.mkdir(parents=True, exist_ok=True)
    assets_dir = output / "assets"
    expected_names = set()
    for kind, target in products:
        package = f"zig-{target['zig_target']}-{target['cpu']}"
        expected_names.update((f"{package}.tar.xz", f"{package}.tar.xz.sha256"))
        if kind == "host":
            expected_names.add(f"{package}.tar.gz")
    if assets_dir.exists() and {p.name for p in assets_dir.iterdir()} - expected_names:
        raise ValueError("output assets contain another target selection; choose a new output directory")

    with tempfile.TemporaryDirectory(prefix=".assets-", dir=output) as temporary:
        stage = Path(temporary)
        assets = []
        with ThreadPoolExecutor(max_workers=2) as workers:
            results = workers.map(
                lambda product: prepare_product(product, args.source_dir.resolve(), stage, manifest),
                products,
            )
            for product, result in zip(products, results):
                assets.extend(result)
                print(f"PASS {product[1]['name']}: package metadata, checksums and compression", flush=True)
        if {asset["name"] for asset in assets} != expected_names:
            raise ValueError("prepared assets do not match the requested platform matrix")
        assets_dir.mkdir(exist_ok=True)
        for path in stage.iterdir():
            path.replace(assets_dir / path.name)
    assets.sort(key=lambda asset: asset["name"])
    report = {
        "zig_version": version,
        "bootstrap_base": base,
        "reference_release": "https://github.com/openharmony-zig/zig-patch/releases/tag/0.16.0",
        "asset_count": len(assets),
        "assets": assets,
    }
    (output / "release-assets.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "SHA256SUMS").write_text(
        "".join(f"{asset['sha256']}  assets/{asset['name']}\n" for asset in assets)
    )
    print(f"Prepared {len(assets)} release assets: {assets_dir}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Release preparation failed: {error}") from error
