#!/usr/bin/env python3
"""Build the public profile README and exploration archive."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path


PLACEHOLDERS = (
    "{{LATEST_DATE}}",
    "{{CURRENT_QUESTION}}",
    "{{RECENT_EXPLORATIONS}}",
)
SECTION_NAMES = ("问题", "实验", "认识", "下一个问题")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRIVACY_PATTERNS = {
    "local-path": re.compile(
        r"(?:/(?:Users|home)/[^\s)]+|[A-Za-z]:\\Users\\[^\s)]+|~/[^\s)]+)"
    ),
    "credential": re.compile(
        r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
        r"sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|"
        r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})"
    ),
    "private-key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "private-contact": re.compile(
        r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+\b"
    ),
}


@dataclass(frozen=True)
class ExplorationRecord:
    slug: str
    title: str
    published: date
    summary: str
    sections: dict[str, str]


def validate_privacy(
    source_name: str, text: str, private_terms: tuple[str, ...]
) -> None:
    for category, pattern in PRIVACY_PATTERNS.items():
        if pattern.search(text):
            raise ValueError(f"{source_name}: privacy rule {category}")
    if any(term.casefold() in text.casefold() for term in private_terms):
        raise ValueError(f"{source_name}: privacy rule private-term")


def parse_record(path: Path, private_terms: tuple[str, ...]) -> ExplorationRecord:
    validate_privacy("record filename", path.name, private_terms)
    if not SLUG_PATTERN.fullmatch(path.stem):
        raise ValueError("invalid record filename")

    text = path.read_text(encoding="utf-8")
    validate_privacy(path.name, text, private_terms)

    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"{path.name}: invalid metadata block")

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"{path.name}: invalid metadata line")
        normalized_key = key.strip()
        if normalized_key in metadata:
            raise ValueError(f"{path.name}: duplicate metadata field")
        metadata[normalized_key] = value.strip()

    required_metadata = {"title", "date", "summary", "status"}
    if set(metadata) != required_metadata:
        raise ValueError(f"{path.name}: metadata fields must be title, date, summary, status")
    if metadata["status"] != "approved":
        raise ValueError(f"{path.name}: only approved records may be published")

    try:
        published = date.fromisoformat(metadata["date"])
    except ValueError as error:
        raise ValueError(f"{path.name}: invalid publication date") from error
    body = parts[2].strip()
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^## (.+)$", body, flags=re.MULTILINE))
    headings = tuple(match.group(1).strip() for match in matches)
    if headings != SECTION_NAMES:
        raise ValueError(f"{path.name}: required sections are 问题, 实验, 认识, 下一个问题")
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip()] = body[start:end].strip()

    if any(not sections[name] for name in SECTION_NAMES):
        raise ValueError(f"{path.name}: required sections are 问题, 实验, 认识, 下一个问题")

    return ExplorationRecord(
        slug=path.stem,
        title=metadata["title"],
        published=published,
        summary=metadata["summary"],
        sections=sections,
    )


def render_recent(records: list[ExplorationRecord]) -> str:
    blocks = []
    for record in records[:3]:
        blocks.append(
            f"### {record.published.isoformat()} · {record.title}\n\n"
            f"{record.summary}\n\n"
            f"**目前的认识：** {record.sections['认识']}\n\n"
            f"[阅读全文](explorations/{record.slug}.md)"
        )
    return "\n\n".join(blocks)


def render_archive(records: list[ExplorationRecord]) -> str:
    entries = "\n".join(
        f"- **{record.published.isoformat()}** [{record.title}]({record.slug}.md)"
        f" — {record.summary}"
        for record in records
    )
    return (
        "# 探索档案\n\n"
        "这里收录所有经过人工审核的探索记录。\n\n"
        f"{entries}\n"
    )


def replace_outputs(outputs: dict[Path, str]) -> None:
    staged_paths: list[tuple[Path, Path]] = []
    backup_paths: list[tuple[Path, Path]] = []
    replaced_destinations: list[Path] = []
    try:
        for destination, content in outputs.items():
            with tempfile.NamedTemporaryFile(
                "w",
                dir=destination.parent,
                encoding="utf-8",
                prefix=f".{destination.name}.",
                delete=False,
            ) as staged_file:
                staged_file.write(content)
                staged_paths.append((Path(staged_file.name), destination))

        for staged_path, destination in staged_paths:
            if destination.exists():
                with tempfile.NamedTemporaryFile(
                    "wb",
                    dir=destination.parent,
                    prefix=f".{destination.name}.backup.",
                    delete=False,
                ) as backup_file:
                    backup_path = Path(backup_file.name)
                    backup_paths.append((backup_path, destination))
                    backup_file.write(destination.read_bytes())
            staged_path.replace(destination)
            replaced_destinations.append(destination)
    except OSError:
        backups_by_destination = {
            destination: backup_path
            for backup_path, destination in backup_paths
        }
        for destination in reversed(replaced_destinations):
            backup_path = backups_by_destination.get(destination)
            if backup_path is None:
                destination.unlink(missing_ok=True)
            else:
                backup_path.replace(destination)
        raise
    finally:
        for staged_path, _ in staged_paths:
            staged_path.unlink(missing_ok=True)
        for backup_path, _ in backup_paths:
            backup_path.unlink(missing_ok=True)


def build_profile(root: Path) -> None:
    private_terms = tuple(
        term.strip()
        for term in os.environ.get("PROFILE_PRIVATE_TERMS", "").splitlines()
        if term.strip()
    )
    template = (root / "profile" / "README.template.md").read_text(
        encoding="utf-8"
    )
    validate_privacy("README.template.md", template, private_terms)
    for placeholder in PLACEHOLDERS:
        if template.count(placeholder) != 1:
            raise ValueError(f"template must contain {placeholder} exactly once")

    record_paths = sorted(
        path for path in (root / "explorations").glob("*.md") if path.name != "README.md"
    )
    records = sorted(
        (parse_record(path, private_terms) for path in record_paths),
        key=lambda record: (-record.published.toordinal(), record.slug),
    )
    if not records:
        raise ValueError("at least one approved exploration record is required")

    latest = records[0]
    readme = template
    replacements = {
        "{{LATEST_DATE}}": latest.published.isoformat(),
        "{{CURRENT_QUESTION}}": latest.sections["下一个问题"],
        "{{RECENT_EXPLORATIONS}}": render_recent(records),
    }
    for placeholder, value in replacements.items():
        readme = readme.replace(placeholder, value)
    archive = render_archive(records)
    validate_privacy("generated README", readme, private_terms)
    validate_privacy("generated archive", archive, private_terms)

    replace_outputs(
        {
            root / "README.md": readme,
            root / "explorations" / "README.md": archive,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()

    try:
        build_profile(arguments.root.resolve())
    except ValueError as error:
        parser.exit(1, f"profile generation failed: {error}\n")
    except OSError:
        parser.exit(1, "profile generation failed: filesystem error\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
