from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = REPOSITORY_ROOT / "scripts" / "build_profile.py"
VALIDATOR = REPOSITORY_ROOT / "scripts" / "validate_public_proposal.py"
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "update-profile.yml"
PUBLICATION_ID = "pub_01K6AV5DX1C2D3E4F5G6H7J8KN"


class PublicProposalValidationTest(unittest.TestCase):
    def test_exact_publication_and_generated_surfaces_pass(self) -> None:
        with self._proposal() as proposal:
            result = self._validate(proposal)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "Public Proposal Validation passed.\n")

    def test_unexpected_path_is_rejected(self) -> None:
        with self._proposal(extra_path="notes/unapproved.md") as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("path scope", result.stderr)

    def test_artifact_digest_mismatch_is_rejected(self) -> None:
        with self._proposal(manifest_digest="0" * 64) as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("artifact digest", result.stderr)

    def test_privacy_hazard_is_rejected_without_echo(self) -> None:
        sensitive = "/Users/example/private-memory"
        with self._proposal(summary=f"素材来自 {sensitive}。", generate=False) as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("privacy rule local-path", result.stderr)
            self.assertNotIn(sensitive, result.stderr)

    def test_stale_generated_surface_is_rejected(self) -> None:
        with self._proposal(stale_surface=True) as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("deterministic generated surfaces", result.stderr)

    def test_manifest_contract_is_strict(self) -> None:
        with self._proposal(extra_manifest_field=True) as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest fields", result.stderr)

    def test_publication_artifact_requires_reviewed_english_metadata(self) -> None:
        with self._proposal(include_english=False) as proposal:
            result = self._validate(proposal)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reviewed English metadata", result.stderr)

    def test_source_stage_accepts_only_manifest_and_artifact(self) -> None:
        with self._proposal(generate=False) as proposal:
            result = self._validate(proposal, stage="source")

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_stage_rejects_pre_modified_generated_surfaces(self) -> None:
        with self._proposal() as proposal:
            result = self._validate(proposal, stage="source")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source path scope", result.stderr)

    def test_workflow_uses_trusted_dispatch_and_bounded_permissions(self) -> None:
        source = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("repository_dispatch:", source)
        self.assertIn("types: [prepare-publication]", source)
        self.assertNotIn("branches:\n      - main", source)
        self.assertIn("permissions: {}", source)
        self.assertEqual(source.count("contents: write"), 1)
        self.assertIn("contents: read", source)
        self.assertIn("statuses: write", source)
        self.assertIn("path: trusted", source)
        self.assertIn("path: proposal", source)

    def _validate(
        self, proposal: "Proposal", *, stage: str = "final"
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--root",
                str(proposal.root),
                "--base",
                proposal.base,
                "--head",
                proposal.head,
                "--manifest",
                proposal.manifest,
                "--stage",
                stage,
            ],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

    def _proposal(self, **options: object) -> "ProposalContext":
        return ProposalContext(**options)


class Proposal:
    def __init__(self, root: Path, base: str, head: str, manifest: str) -> None:
        self.root = root
        self.base = base
        self.head = head
        self.manifest = manifest


class ProposalContext:
    def __init__(
        self,
        *,
        extra_path: str | None = None,
        manifest_digest: str | None = None,
        summary: str = "这次实验把一次探索变成可恢复、可审查的知识。",
        generate: bool = True,
        stale_surface: bool = False,
        extra_manifest_field: bool = False,
        include_english: bool = True,
    ) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        for relative in ("README.md", "profile", "explorations"):
            source = REPOSITORY_ROOT / relative
            destination = self.root / relative
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        self._git("init", "-q")
        self._git("config", "user.name", "Fixture")
        self._git("config", "user.email", "fixture@example.invalid")
        self._git("add", ".")
        self._git("commit", "-q", "-m", "base")
        self.base = self._git("rev-parse", "HEAD").stdout.strip()

        artifact = self.root / "explorations" / "seed-memory-system.md"
        english_metadata = ""
        if include_english:
            english_metadata = (
                "title_en: Turning Codex Explorations into Durable Memory\n"
                "abstract_en: This exploration tests a private source of truth for AI-era learning. Human review remains the boundary for knowledge admission and public disclosure.\n"
            )
        artifact.write_text(
            "---\n"
            "title: 把 Codex 探索沉淀为可恢复的记忆\n"
            f"{english_metadata}"
            "date: 2026-08-31\n"
            f"summary: {summary}\n"
            "status: approved\n"
            "---\n\n"
            "## 问题\n\n怎样让 AI 协作跨越会话？\n\n"
            "## 实验\n\n以私密仓库保存证据、判断和决策。\n\n"
            "## 认识\n\n自动化负责提议，人负责知识准入和披露。\n\n"
            "## 下一个问题\n\n怎样持续提炼新的探索？\n",
            encoding="utf-8",
        )
        digest = manifest_digest or hashlib.sha256(artifact.read_bytes()).hexdigest()
        manifest_directory = self.root / "publication-manifests"
        manifest_directory.mkdir()
        manifest = {
            "schema_version": 1,
            "publication_id": PUBLICATION_ID,
            "artifact_path": "explorations/seed-memory-system.md",
            "artifact_sha256": digest,
        }
        if extra_manifest_field:
            manifest["unexpected"] = True
        self.manifest = f"publication-manifests/{PUBLICATION_ID}.json"
        (self.root / self.manifest).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if extra_path:
            path = self.root / extra_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not approved\n", encoding="utf-8")
        if generate:
            result = subprocess.run(
                [sys.executable, str(PUBLISHER), "--root", str(self.root)],
                capture_output=True,
                check=False,
                text=True,
            )
            if result.returncode != 0:
                raise AssertionError(result.stderr)
        if stale_surface:
            (self.root / "README.md").write_text("stale\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-q", "-m", "proposal")
        self.head = self._git("rev-parse", "HEAD").stdout.strip()

    def __enter__(self) -> Proposal:
        return Proposal(self.root, self.base, self.head, self.manifest)

    def __exit__(self, *args: object) -> None:
        self.temporary_directory.cleanup()

    def _git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            capture_output=True,
            check=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
