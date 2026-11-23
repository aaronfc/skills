#!/usr/bin/env python3
"""Install tracked skills from a local checkout into agent skill directories via symlinks."""

from __future__ import annotations

import argparse
import dataclasses
import os
import pathlib
import re
import subprocess
import sys


DEFAULT_CLIENT_PATHS: dict[str, tuple[str, ...]] = {
    "agents": (".agents", "skills"),
    "claude": (".claude", "skills"),
    "antigravity": (".gemini", "config", "skills"),
}


class DiscoveryError(RuntimeError):
    """Raised when tracked skills cannot be discovered or have name collisions."""


class InstallError(RuntimeError):
    """Raised when target configuration or installation fails."""


@dataclasses.dataclass(frozen=True)
class Skill:
    installed_name: str
    raw_name: str
    source_dir: pathlib.Path
    skill_file: pathlib.Path
    rel_skill_file: str


@dataclasses.dataclass(frozen=True)
class TargetSpec:
    name: str
    directory: pathlib.Path


@dataclasses.dataclass(frozen=True)
class Conflict:
    installed_name: str
    dest: pathlib.Path
    reason: str
    wanted: pathlib.Path


@dataclasses.dataclass
class TargetReport:
    target: TargetSpec
    installed: list[tuple[str, pathlib.Path]] = dataclasses.field(default_factory=list)
    updated: list[tuple[str, str, pathlib.Path]] = dataclasses.field(default_factory=list)
    removed: list[tuple[str, str]] = dataclasses.field(default_factory=list)
    unchanged: list[str] = dataclasses.field(default_factory=list)
    conflicts: list[Conflict] = dataclasses.field(default_factory=list)


def parse_frontmatter_name(content: str) -> str | None:
    """Extract the top-level YAML frontmatter `name` field from SKILL.md text."""
    text = content.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    frontmatter_lines: list[str] = []
    for line in lines[1:]:
        if line.rstrip() in {"---", "..."}:
            break
        frontmatter_lines.append(line)
    else:
        return None

    for index, line in enumerate(frontmatter_lines):
        if not line or line[0].isspace():
            continue
        match = re.match(r"^name\s*:\s*(.*)$", line)
        if not match:
            continue
        raw = match.group(1).strip()
        if not raw:
            return None
        if re.fullmatch(r"[>|](?:[+-]?[1-9]?|[1-9][+-]?)(?:\s+#.*)?", raw):
            # Folding and line breaks both become separators in installed names.
            parts = []
            for part in frontmatter_lines[index + 1:]:
                if part and not part[0].isspace():
                    break
                parts.append(part.strip())
            return " ".join(parts).strip() or None
        quoted = re.fullmatch(r"""('(?:[^']|'')*'|"(?:[^"\\]|\\.)*")(?:\s+#.*)?""", raw)
        if quoted:
            value = quoted[1][1:-1]
            if quoted[1].startswith("'"):
                value = value.replace("''", "'")
            return value.strip() or None
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


def resolve_repo_root(path: pathlib.Path) -> pathlib.Path:
    """Resolve the git top-level directory for path."""
    resolved = path.resolve()
    result = subprocess.run(
        ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise DiscoveryError(f"{resolved} is not inside a git checkout: {stderr}")
    return pathlib.Path(result.stdout.strip()).resolve()


def discover_skills(repo_root: pathlib.Path) -> list[Skill]:
    """Discover tracked SKILL.md files under repo_root with unique installed names."""
    resolved_root = resolve_repo_root(repo_root)
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
        skill_file = resolved_root / rel_path
        source_dir = skill_file.parent.resolve()
        if not (
            source_dir.is_relative_to(resolved_root)
            and skill_file.resolve().is_relative_to(resolved_root)
        ):
            raise DiscoveryError(f"Skill file {rel_path} points outside the checkout.")
        if not skill_file.is_file():
            continue
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


def direct_link_target(link: pathlib.Path) -> pathlib.Path | None:
    """Resolve a symlink's direct target path without following the target itself."""
    try:
        raw = pathlib.Path(os.readlink(link))
        joined = raw if raw.is_absolute() else (link.parent.resolve() / raw)
        normalized = pathlib.Path(os.path.normpath(str(joined)))
        if normalized == normalized.parent:
            return normalized
        return normalized.parent.resolve() / normalized.name
    except OSError:
        return None


def is_owned_by_repo(link: pathlib.Path, resolved_repo: pathlib.Path) -> bool:
    """Return True when link directly points to an entry inside resolved_repo."""
    target = direct_link_target(link)
    return (
        target is not None
        and target != resolved_repo
        and target.is_relative_to(resolved_repo)
    )


def sync_target(
    target: TargetSpec,
    skills: list[Skill],
    repo_root: pathlib.Path,
    *,
    dry_run: bool = False,
) -> TargetReport:
    """Sync symlinks for skills in a single target directory."""
    resolved_repo = repo_root.resolve()
    target_dir = target.directory
    report = TargetReport(target=target)

    if os.path.lexists(target_dir) and not target_dir.is_dir():
        raise InstallError(
            f"Target path {target_dir} ({target.name}) exists and is not a directory."
        )

    dir_existed = target_dir.is_dir()
    if not dir_existed and not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    desired = {skill.installed_name: skill for skill in skills}

    for skill in skills:
        dest = target_dir / skill.installed_name
        if not dir_existed or not os.path.lexists(dest):
            if not dry_run:
                dest.symlink_to(skill.source_dir)
            report.installed.append((skill.installed_name, skill.source_dir))
            continue

        if dest.is_symlink():
            current_target = direct_link_target(dest)
            if current_target == skill.source_dir:
                report.unchanged.append(skill.installed_name)
                continue
            if is_owned_by_repo(dest, resolved_repo):
                old_raw = os.readlink(dest)
                if not dry_run:
                    dest.unlink()
                    dest.symlink_to(skill.source_dir)
                report.updated.append((skill.installed_name, old_raw, skill.source_dir))
                continue
            raw_target = os.readlink(dest)
            report.conflicts.append(
                Conflict(
                    installed_name=skill.installed_name,
                    dest=dest,
                    reason=f"existing symlink -> {raw_target}",
                    wanted=skill.source_dir,
                )
            )
            continue

        entry_kind = "existing directory" if dest.is_dir() else "existing file"
        report.conflicts.append(
            Conflict(
                installed_name=skill.installed_name,
                dest=dest,
                reason=entry_kind,
                wanted=skill.source_dir,
            )
        )

    if dir_existed:
        for entry in sorted(target_dir.iterdir(), key=lambda p: p.name):
            if entry.name in desired:
                continue
            if entry.is_symlink() and is_owned_by_repo(entry, resolved_repo):
                old_raw = os.readlink(entry)
                if not dry_run:
                    entry.unlink()
                report.removed.append((entry.name, old_raw))

    return report


def parse_clients(raw_clients: list[str] | None) -> list[str]:
    """Parse repeatable/comma-separated --client names."""
    if not raw_clients:
        return list(DEFAULT_CLIENT_PATHS)
    selected: list[str] = []
    for item in raw_clients:
        for name in item.split(","):
            client = name.strip().lower()
            if not client:
                continue
            if client not in DEFAULT_CLIENT_PATHS:
                valid = ", ".join(DEFAULT_CLIENT_PATHS)
                raise InstallError(f"Unknown client {client!r}. Choose from: {valid}.")
            if client not in selected:
                selected.append(client)
    if not selected:
        raise InstallError("At least one client must be specified.")
    return selected


def parse_targets(
    raw_targets: list[str] | None,
    raw_clients: list[str] | None,
    home: pathlib.Path,
) -> list[TargetSpec]:
    """Resolve install targets from --target or default --client directories."""
    if raw_targets and raw_clients:
        raise InstallError("Cannot combine --target with --client.")

    if raw_targets:
        specs: list[TargetSpec] = []
        for item in raw_targets:
            if "=" in item:
                name, path_str = item.split("=", 1)
                name = name.strip()
                path_str = path_str.strip()
            else:
                name = item.strip()
                path_str = item.strip()
            if not path_str:
                raise InstallError(f"Invalid --target specification: {item!r}.")
            specs.append(
                TargetSpec(
                    name=name or path_str,
                    directory=pathlib.Path(path_str).expanduser(),
                )
            )
        return specs

    clients = parse_clients(raw_clients)
    return [
        TargetSpec(name=client, directory=home.joinpath(*DEFAULT_CLIENT_PATHS[client]))
        for client in clients
    ]


def format_report(reports: list[TargetReport], *, dry_run: bool = False) -> str:
    """Format a human-readable summary of install actions and conflicts."""
    prefix = "[dry-run] " if dry_run else ""
    lines: list[str] = []
    total_conflicts = 0

    for report in reports:
        conflict_count = len(report.conflicts)
        total_conflicts += conflict_count
        conflict_word = "conflict" if conflict_count == 1 else "conflicts"
        lines.append(
            f"{prefix}{report.target.name} ({report.target.directory}): "
            f"{len(report.installed)} installed, "
            f"{len(report.updated)} updated, "
            f"{len(report.removed)} removed, "
            f"{len(report.unchanged)} unchanged, "
            f"{conflict_count} {conflict_word}"
        )
        for name, source_dir in report.installed:
            lines.append(f"  + {name} -> {source_dir}")
        for name, old_target, source_dir in report.updated:
            lines.append(f"  ~ {name}: {old_target} -> {source_dir}")
        for name, old_target in report.removed:
            lines.append(f"  - {name} (was -> {old_target})")
        for conflict in report.conflicts:
            lines.append(
                f"  ! conflict: {conflict.dest} ({conflict.reason}; "
                f"wanted -> {conflict.wanted})"
            )

    if total_conflicts:
        lines.append(
            f"Preserved {total_conflicts} conflicting "
            f"{'entry' if total_conflicts == 1 else 'entries'}. "
            "Remove or move any entry you want to migrate, then rerun this command."
        )

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    default_clients = ", ".join(DEFAULT_CLIENT_PATHS)
    parser = argparse.ArgumentParser(
        description=(
            "Symlink tracked skills from this checkout into local agent skill "
            f"directories ({default_clients})."
        )
    )
    parser.add_argument(
        "--repo",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent.parent,
        help="Path to the skills git checkout (defaults to this repository).",
    )
    parser.add_argument(
        "--home",
        type=pathlib.Path,
        default=pathlib.Path.home(),
        help="Base home directory for default client paths (defaults to ~).",
    )
    parser.add_argument(
        "--client",
        action="append",
        help=(
            "Client(s) to sync; repeatable or comma-separated "
            f"({default_clients}). Defaults to all."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        help=(
            "Custom install directory (NAME=PATH or PATH); repeatable. "
            "Installs only to these directories instead of default clients."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned symlink changes and conflicts without modifying disk.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        repo_root = resolve_repo_root(args.repo)
        targets = parse_targets(args.target, args.client, args.home.expanduser())
        for target in targets:
            if os.path.lexists(target.directory) and not target.directory.is_dir():
                raise InstallError(
                    f"Target path {target.directory} ({target.name}) exists and is not a directory."
                )
        skills = discover_skills(repo_root)
        reports = [
            sync_target(target, skills, repo_root, dry_run=args.dry_run)
            for target in targets
        ]
    except (DiscoveryError, InstallError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(format_report(reports, dry_run=args.dry_run))
    has_conflicts = any(report.conflicts for report in reports)
    return 1 if has_conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
