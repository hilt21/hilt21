#!/usr/bin/env python3
"""Validate one final public proposal without changing its checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from build_profile import build_profile, parse_record


PUBLICATION_ID_PATTERN = re.compile(r"^pub_[0-9A-HJKMNP-TV-Z]{26}$")
ARTIFACT_PATH_PATTERN = re.compile(
    r"^explorations/[a-z0-9]+(?:-[a-z0-9]+)*\.md$"
)
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_FIELDS = {
    "schema_version",
    "publication_id",
    "artifact_path",
    "artifact_sha256",
}
GENERATED_SURFACES = {"README.md", "explorations/README.md"}
MAX_MANIFEST_BYTES = 4096
MAX_ARTIFACT_BYTES = 131072


def private_terms() -> tuple[str, ...]:
    return tuple(
        term.strip()
        for term in os.environ.get("PROFILE_PRIVATE_TERMS", "").splitlines()
        if term.strip()
    )


def run_git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError("git proposal boundary")
    return result.stdout.strip()


def load_manifest(root: Path, relative: str) -> dict[str, object]:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("manifest path")
    manifest_path = root / Path(*path.parts)
    if manifest_path.is_symlink() or manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("manifest file boundary")
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("manifest JSON") from error
    if not isinstance(value, dict) or set(value) != MANIFEST_FIELDS:
        raise ValueError("manifest fields")
    publication_id = value["publication_id"]
    if value["schema_version"] != 1:
        raise ValueError("manifest schema version")
    if not isinstance(publication_id, str) or not PUBLICATION_ID_PATTERN.fullmatch(
        publication_id
    ):
        raise ValueError("manifest publication identity")
    if relative != f"publication-manifests/{publication_id}.json":
        raise ValueError("manifest path")
    artifact_path = value["artifact_path"]
    if not isinstance(artifact_path, str) or not ARTIFACT_PATH_PATTERN.fullmatch(
        artifact_path
    ):
        raise ValueError("manifest artifact path")
    if artifact_path == "explorations/README.md":
        raise ValueError("manifest artifact path")
    digest = value["artifact_sha256"]
    if not isinstance(digest, str) or not DIGEST_PATTERN.fullmatch(digest):
        raise ValueError("manifest artifact digest")
    return value


def validate_git_boundary(
    root: Path,
    base: str,
    head: str,
    manifest_path: str,
    artifact_path: str,
    stage: str,
) -> None:
    if run_git(root, "rev-parse", "HEAD") != head:
        raise ValueError("final head checkout")
    run_git(root, "merge-base", "--is-ancestor", base, head)
    changed = {
        line
        for line in run_git(root, "diff", "--name-only", base, head, "--").splitlines()
        if line
    }
    required = {manifest_path, artifact_path}
    allowed = required | GENERATED_SURFACES
    if stage == "source" and changed != required:
        raise ValueError("source path scope")
    if stage == "final" and (
        not required.issubset(changed) or not changed.issubset(allowed)
    ):
        raise ValueError("proposal path scope")


def validate_artifact(root: Path, manifest: dict[str, object]) -> None:
    artifact_path = manifest["artifact_path"]
    expected_digest = manifest["artifact_sha256"]
    if not isinstance(artifact_path, str) or not isinstance(expected_digest, str):
        raise ValueError("manifest fields")
    artifact = root / artifact_path
    if artifact.is_symlink() or artifact.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact file boundary")
    actual_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if actual_digest != expected_digest:
        raise ValueError("artifact digest mismatch")
    parse_record(artifact, private_terms())


def validate_generated_surfaces(root: Path) -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        rendered = Path(temporary_directory)
        shutil.copytree(root / "profile", rendered / "profile")
        shutil.copytree(root / "explorations", rendered / "explorations")
        shutil.copy2(root / "README.md", rendered / "README.md")
        build_profile(rendered)
        for relative in sorted(GENERATED_SURFACES):
            if (root / relative).read_bytes() != (rendered / relative).read_bytes():
                raise ValueError("deterministic generated surfaces are stale")


def validate(
    root: Path,
    base: str,
    head: str,
    manifest_path: str,
    stage: str,
) -> None:
    manifest = load_manifest(root, manifest_path)
    artifact_path = manifest["artifact_path"]
    if not isinstance(artifact_path, str):
        raise ValueError("manifest fields")
    validate_git_boundary(root, base, head, manifest_path, artifact_path, stage)
    validate_artifact(root, manifest)
    if stage == "final":
        validate_generated_surfaces(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--stage", choices=("source", "final"), default="final")
    arguments = parser.parse_args()
    try:
        validate(
            arguments.root.resolve(),
            arguments.base,
            arguments.head,
            arguments.manifest,
            arguments.stage,
        )
    except ValueError as error:
        parser.exit(1, f"public proposal validation failed: {error}\n")
    except OSError:
        parser.exit(1, "public proposal validation failed: filesystem error\n")
    print("Public Proposal Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
