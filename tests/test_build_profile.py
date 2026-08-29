from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = REPOSITORY_ROOT / "scripts" / "build_profile.py"


class ProfilePublisherTest(unittest.TestCase):
    def test_approved_record_generates_profile_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="durable-memory",
                title="让一次性对话成为长期记忆",
                published="2026-08-29",
                summary="我在尝试让人与 AI 的协作跨越会话和中断。",
                learning="真正有价值的不是保存所有对话，而是保存可复用的判断。",
                next_question="什么信息值得进入长期记忆？",
            )

            result = self._run_publisher(workspace)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (workspace / "README.md").read_text(encoding="utf-8"),
                "# AI 探索日志\n\n"
                "最近更新：2026-08-29\n\n"
                "## 我正在探索\n\n"
                "什么信息值得进入长期记忆？\n\n"
                "## 最近的探索\n\n"
                "### 2026-08-29 · 让一次性对话成为长期记忆\n\n"
                "我在尝试让人与 AI 的协作跨越会话和中断。\n\n"
                "**目前的认识：** 真正有价值的不是保存所有对话，而是保存可复用的判断。\n\n"
                "[阅读全文](explorations/durable-memory.md)\n",
            )
            self.assertEqual(
                (workspace / "explorations" / "README.md").read_text(
                    encoding="utf-8"
                ),
                "# 探索档案\n\n"
                "这里收录所有经过人工审核的探索记录。\n\n"
                "- **2026-08-29** [让一次性对话成为长期记忆](durable-memory.md)"
                " — 我在尝试让人与 AI 的协作跨越会话和中断。\n",
            )

    def test_local_path_is_rejected_without_changing_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="unsafe-note",
                title="不应公开的记录",
                published="2026-08-29",
                summary="素材来自 /Users/example/private-project。",
                learning="发布前必须检查隐私边界。",
                next_question="怎样阻止无意泄漏？",
            )
            (workspace / "README.md").write_text(
                "existing profile\n", encoding="utf-8"
            )
            (workspace / "explorations" / "README.md").write_text(
                "existing archive\n", encoding="utf-8"
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local-path", result.stderr)
            self.assertNotIn("/Users/example/private-project", result.stderr)
            self.assertEqual(
                (workspace / "README.md").read_text(encoding="utf-8"),
                "existing profile\n",
            )
            self.assertEqual(
                (workspace / "explorations" / "README.md").read_text(
                    encoding="utf-8"
                ),
                "existing archive\n",
            )

    def test_private_denylist_term_is_rejected_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="private-project",
                title="一次项目实验",
                published="2026-08-29",
                summary="这次实验来自 Project Nebula。",
                learning="公开结论不等于公开项目身份。",
                next_question="如何分享方法而不泄漏背景？",
            )

            result = self._run_publisher(
                workspace, private_terms="Project Nebula"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("private-term", result.stderr)
            self.assertNotIn("Project Nebula", result.stderr)
            self.assertFalse((workspace / "README.md").exists())
            self.assertFalse((workspace / "explorations" / "README.md").exists())

    def test_sensitive_template_is_rejected_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            template_path = workspace / "profile" / "README.template.md"
            sensitive_value = "/Users/example/private-template"
            template_path.write_text(
                template_path.read_text(encoding="utf-8")
                + f"\nInternal source: {sensitive_value}\n",
                encoding="utf-8",
            )
            self._write_record(
                workspace,
                slug="safe-note",
                title="安全记录",
                published="2026-08-29",
                summary="记录本身不含私密信息。",
                learning="所有公开输入都必须检查。",
                next_question="模板也安全吗？",
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("local-path", result.stderr)
            self.assertNotIn(sensitive_value, result.stderr)
            self.assertFalse((workspace / "README.md").exists())

    def test_duplicate_metadata_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="duplicate-metadata",
                title="重复元数据",
                published="2026-08-29",
                summary="重复字段不应被后一个值覆盖。",
                learning="元数据字段必须保持唯一。",
                next_question="怎样让输入保持明确？",
            )
            record_path = workspace / "explorations" / "duplicate-metadata.md"
            record_path.write_text(
                record_path.read_text(encoding="utf-8").replace(
                    "title: 重复元数据\n",
                    "title: 重复元数据\ntitle: 被覆盖的标题\n",
                ),
                encoding="utf-8",
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate metadata", result.stderr)
            self.assertFalse((workspace / "README.md").exists())

    def test_unsafe_record_filename_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="unsafe slug",
                title="不安全文件名",
                published="2026-08-29",
                summary="链接目标必须由安全的 slug 组成。",
                learning="文件名也是公开输出的一部分。",
                next_question="怎样约束稳定链接？",
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid record filename", result.stderr)
            self.assertFalse((workspace / "README.md").exists())

    def test_private_term_in_record_filename_is_rejected_without_echo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            sensitive_value = "nebula"
            self._write_record(
                workspace,
                slug=f"project-{sensitive_value}",
                title="匿名项目记录",
                published="2026-08-29",
                summary="正文已经完成匿名处理。",
                learning="公开文件名同样属于发布内容。",
                next_question="还有哪些隐蔽的公开表面？",
            )

            result = self._run_publisher(
                workspace, private_terms=sensitive_value
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("private-term", result.stderr)
            self.assertNotIn(sensitive_value, result.stderr)
            self.assertFalse((workspace / "README.md").exists())

    def test_common_sensitive_patterns_are_rejected(self) -> None:
        cases = (
            ("local-path", "/home/example/private-project"),
            ("local-path", r"C:\Users\example\private-project"),
            ("local-path", "~/private-project"),
            ("credential", "gh" + "p_1234567890abcdefghijklmnop"),
            ("credential", "sk-" + "proj-1234567890abcdefghijklmnop"),
            ("credential", "AK" + "IA1234567890ABCDEF"),
            (
                "credential",
                "ey" + "Jabcdefghijk.abcdefghijkl.abcdefghijkl",
            ),
            ("private-key", "-----BEGIN " + "OPENSSH PRIVATE KEY-----"),
            ("private-contact", "private@example.com"),
        )
        for category, sensitive_value in cases:
            with (
                self.subTest(category=category),
                tempfile.TemporaryDirectory() as temporary_directory,
            ):
                workspace = Path(temporary_directory)
                self._write_template(workspace)
                self._write_record(
                    workspace,
                    slug="unsafe-note",
                    title="不应公开的记录",
                    published="2026-08-29",
                    summary=f"不应出现的内容：{sensitive_value}",
                    learning="隐私检查必须阻止发布。",
                    next_question="如何保持安全？",
                )

                result = self._run_publisher(workspace)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(category, result.stderr)
                self.assertNotIn(sensitive_value, result.stderr)

    def test_invalid_record_contracts_are_rejected(self) -> None:
        cases = (
            ("missing metadata", "summary: 有效摘要。\n", "", "metadata fields"),
            (
                "invalid date",
                "date: 2026-08-29\n",
                "date: not-a-date\n",
                "invalid publication date",
            ),
            (
                "empty next question",
                "## 下一个问题\n\n后续问题。\n",
                "## 下一个问题\n",
                "required sections",
            ),
        )
        for name, old, new, expected_error in cases:
            with (
                self.subTest(name=name),
                tempfile.TemporaryDirectory() as temporary_directory,
            ):
                workspace = Path(temporary_directory)
                self._write_template(workspace)
                self._write_record(
                    workspace,
                    slug="invalid-record",
                    title="无效记录",
                    published="2026-08-29",
                    summary="有效摘要。",
                    learning="契约不完整时不应发布。",
                    next_question="后续问题。",
                )
                record_path = workspace / "explorations" / "invalid-record.md"
                record_path.write_text(
                    record_path.read_text(encoding="utf-8").replace(old, new),
                    encoding="utf-8",
                )

                result = self._run_publisher(workspace)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_error, result.stderr)
                self.assertFalse((workspace / "README.md").exists())

    def test_invalid_template_boundaries_are_rejected(self) -> None:
        for name, replacement in (
            ("missing", ""),
            ("duplicate", "{{CURRENT_QUESTION}}\n{{CURRENT_QUESTION}}"),
        ):
            with (
                self.subTest(name=name),
                tempfile.TemporaryDirectory() as temporary_directory,
            ):
                workspace = Path(temporary_directory)
                self._write_template(workspace)
                template_path = workspace / "profile" / "README.template.md"
                template_path.write_text(
                    template_path.read_text(encoding="utf-8").replace(
                        "{{CURRENT_QUESTION}}", replacement
                    ),
                    encoding="utf-8",
                )
                self._write_record(
                    workspace,
                    slug="valid-record",
                    title="有效记录",
                    published="2026-08-29",
                    summary="记录有效，但模板边界无效。",
                    learning="生成边界必须唯一。",
                    next_question="如何保持模板稳定？",
                )

                result = self._run_publisher(workspace)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("exactly once", result.stderr)
                self.assertFalse((workspace / "README.md").exists())

    def test_sensitive_value_composed_during_rendering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            template_path = workspace / "profile" / "README.template.md"
            template_path.write_text(
                template_path.read_text(encoding="utf-8").replace(
                    "{{CURRENT_QUESTION}}", "sk-{{CURRENT_QUESTION}}"
                ),
                encoding="utf-8",
            )
            self._write_record(
                workspace,
                slug="composed-secret",
                title="组合边界",
                published="2026-08-29",
                summary="各输入单独安全，组合输出仍需复查。",
                learning="最终输出也是隐私检查边界。",
                next_question="abcdefghijklmnopqrstuvwxyz",
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("credential", result.stderr)
            self.assertFalse((workspace / "README.md").exists())

    def test_duplicate_required_section_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="duplicate-section",
                title="重复章节",
                published="2026-08-29",
                summary="结构不明确的记录不应发布。",
                learning="每个语义章节必须唯一。",
                next_question="怎样保持结构清晰？",
            )
            record_path = workspace / "explorations" / "duplicate-section.md"
            record_path.write_text(
                record_path.read_text(encoding="utf-8")
                + "\n## 认识\n\n这个重复章节不应覆盖原内容。\n",
                encoding="utf-8",
            )

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("required sections", result.stderr)
            self.assertFalse((workspace / "README.md").exists())
            self.assertFalse((workspace / "explorations" / "README.md").exists())

    def test_output_preparation_failure_preserves_existing_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="valid-note",
                title="有效记录",
                published="2026-08-29",
                summary="内容有效，但输出目录暂时不可写。",
                learning="发布必须先准备完整输出。",
                next_question="怎样避免部分发布？",
            )
            profile_path = workspace / "README.md"
            profile_path.write_text("existing profile\n", encoding="utf-8")
            exploration_directory = workspace / "explorations"
            exploration_directory.chmod(0o555)
            try:
                result = self._run_publisher(workspace)
            finally:
                exploration_directory.chmod(0o755)

            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(str(workspace), result.stderr)
            self.assertEqual(
                profile_path.read_text(encoding="utf-8"), "existing profile\n"
            )
            self.assertFalse((exploration_directory / "README.md").exists())

    def test_second_output_replacement_failure_rolls_back_first_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            self._write_record(
                workspace,
                slug="valid-note",
                title="有效记录",
                published="2026-08-29",
                summary="内容有效，但第二个输出目标不可替换。",
                learning="发布失败时两个页面必须保持一致。",
                next_question="怎样验证跨文件回滚？",
            )
            profile_path = workspace / "README.md"
            profile_path.write_text("existing profile\n", encoding="utf-8")
            archive_path = workspace / "explorations" / "README.md"
            archive_path.mkdir()
            marker_path = archive_path / "marker.txt"
            marker_path.write_text("existing archive marker\n", encoding="utf-8")

            result = self._run_publisher(workspace)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                profile_path.read_text(encoding="utf-8"), "existing profile\n"
            )
            self.assertEqual(
                marker_path.read_text(encoding="utf-8"),
                "existing archive marker\n",
            )

    def test_records_are_ordered_limited_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            self._write_template(workspace)
            records = (
                ("beta", "同日第二篇", "2026-08-29", "问题 B"),
                ("alpha", "同日第一篇", "2026-08-29", "问题 A"),
                ("third", "第三篇", "2026-08-28", "问题 C"),
                ("oldest", "最早一篇", "2026-08-27", "问题 D"),
            )
            for slug, title, published, next_question in records:
                self._write_record(
                    workspace,
                    slug=slug,
                    title=title,
                    published=published,
                    summary=f"{title}摘要。",
                    learning=f"{title}认识。",
                    next_question=next_question,
                )
            sentinel = workspace / "unrelated.txt"
            sentinel.write_text("untouched\n", encoding="utf-8")

            first_result = self._run_publisher(workspace)
            first_profile = (workspace / "README.md").read_bytes()
            first_archive = (workspace / "explorations" / "README.md").read_bytes()
            second_result = self._run_publisher(workspace)

            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            profile = first_profile.decode("utf-8")
            archive = first_archive.decode("utf-8")
            self.assertIn("问题 A", profile)
            self.assertLess(profile.index("同日第一篇"), profile.index("同日第二篇"))
            self.assertLess(profile.index("同日第二篇"), profile.index("第三篇"))
            self.assertNotIn("最早一篇", profile)
            self.assertLess(archive.index("同日第一篇"), archive.index("同日第二篇"))
            self.assertIn("最早一篇", archive)
            self.assertEqual((workspace / "README.md").read_bytes(), first_profile)
            self.assertEqual(
                (workspace / "explorations" / "README.md").read_bytes(),
                first_archive,
            )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "untouched\n")

    def _run_publisher(
        self, workspace: Path, *, private_terms: str = ""
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        if private_terms:
            environment["PROFILE_PRIVATE_TERMS"] = private_terms
        return subprocess.run(
            [sys.executable, str(PUBLISHER), "--root", str(workspace)],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

    def _write_template(self, workspace: Path) -> None:
        template_directory = workspace / "profile"
        template_directory.mkdir(parents=True)
        (template_directory / "README.template.md").write_text(
            "# AI 探索日志\n\n"
            "最近更新：{{LATEST_DATE}}\n\n"
            "## 我正在探索\n\n"
            "{{CURRENT_QUESTION}}\n\n"
            "## 最近的探索\n\n"
            "{{RECENT_EXPLORATIONS}}\n",
            encoding="utf-8",
        )

    def _write_record(
        self,
        workspace: Path,
        *,
        slug: str,
        title: str,
        published: str,
        summary: str,
        learning: str,
        next_question: str,
    ) -> None:
        exploration_directory = workspace / "explorations"
        exploration_directory.mkdir(parents=True, exist_ok=True)
        (exploration_directory / f"{slug}.md").write_text(
            "---\n"
            f"title: {title}\n"
            f"date: {published}\n"
            f"summary: {summary}\n"
            "status: approved\n"
            "---\n\n"
            "## 问题\n\n如何让协作在中断后继续？\n\n"
            "## 实验\n\n把关键判断保存为可恢复的文档。\n\n"
            f"## 认识\n\n{learning}\n\n"
            f"## 下一个问题\n\n{next_question}\n",
            encoding="utf-8",
        )
