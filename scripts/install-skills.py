#!/usr/bin/env python3
"""Discover tracked skills in a local checkout and derive stable installed names."""

from __future__ import annotations

import dataclasses
import pathlib
import re
import subprocess


class DiscoveryError(RuntimeError):
    """Raised when tracked skills cannot be discovered or have name collisions."""


@dataclasses.dataclass(frozen=True)
class Skill:
    installed_name: str
    raw_name: str
    source_dir: pathlib.Path
    skill_file: pathlib.Path
    rel_skill_file: str


def parse_frontmatter_name(content: str) -> str | None:
    """Extract the top-level YAML frontmatter `name` field from SKILL.md text."""
    text = content.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    frontmatter_lines: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if stripped in {"---", "..."}:
            break
        frontmatter_lines.append(line)
    else:
        return None

    for line in frontmatter_lines:
        if not line or line[0].isspace():
            continue
        match = re.match(r"^name\s*:\s*(.*)$", line)
        if not match:
            continue
        raw = match.group(1).strip()
        if not raw:
            return None
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {'"', "'"}:
            return raw[1:-1].strip() or None
        raw = re.sub(r"\s+#.*$", "", raw).strip()
        return raw or None

    return None


def normalize_installed_name(raw_name: str) -> str:
    """Convert a skill name into a portable, directory-independent folder name."""
    normalized = re.sub(r"[^a-z0-9]+", "-", raw_name.strip().lower()).strip("-")
    if not normalized:
        raise DiscoveryError(
            f"Skill name {raw_name!r} does not produce a valid installed directory name."
        )
    return normalized


def discover_skills(repo_root: pathlib.Path) -> list[Skill]:
    """Discover tracked SKILL.md files under repo_root with unique installed names."""
    resolved_root = repo_root.resolve()
    result = subprocess.run(
        ["git", "-C", str(resolved_root), "ls-files", "-z"],
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise DiscoveryError(
            f"Failed to list tracked files in {resolved_root}: {stderr}"
        )

    entries = [
        entry.decode("utf-8", errors="surrogateescape")
        for entry in result.stdout.split(b"\0")
        if entry
    ]

    by_name: dict[str, list[Skill]] = {}
    for rel_path in sorted(entries):
        rel = pathlib.PurePosixPath(rel_path)
        if rel.name != "SKILL.md":
            continue
        skill_file = (resolved_root / rel_path).resolve()
        if not skill_file.is_file():
            continue
        source_dir = skill_file.parent
        if source_dir == resolved_root:
            raise DiscoveryError(
                f"Skill file {rel_path} cannot live directly at the repository root."
            )

        content = skill_file.read_text(encoding="utf-8")
        raw_name = parse_frontmatter_name(content) or source_dir.name
        installed_name = normalize_installed_name(raw_name)
        skill = Skill(
            installed_name=installed_name,
            raw_name=raw_name,
            source_dir=source_dir,
            skill_file=skill_file,
            rel_skill_file=rel_path,
        )
        by_name.setdefault(installed_name, []).append(skill)

    collisions = {
        name: group for name, group in sorted(by_name.items()) if len(group) > 1
    }
    if collisions:
        details = "; ".join(
            f"{name}: {', '.join(s.rel_skill_file for s in group)}"
            for name, group in collisions.items()
        )
        raise DiscoveryError(f"Duplicate installed skill names detected: {details}")

    return [by_name[name][0] for name in sorted(by_name)]
