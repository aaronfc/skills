from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "install-skills.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("install_skills", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load installer module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def init_repo(root: pathlib.Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    git("init", "-q")
    git("config", "user.name", "Test User")
    git("config", "user.email", "test@example.com")


def add_skill(
    root: pathlib.Path,
    rel_dir: str,
    content: str,
    *,
    track: bool = True,
) -> pathlib.Path:
    skill_dir = root / rel_dir
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")
    if track:
        subprocess.run(
            ["git", "-C", str(root), "add", str(skill_file.relative_to(root))],
            check=True,
            capture_output=True,
            text=True,
        )
    return skill_dir


class DiscoverSkillsTest(unittest.TestCase):
    def test_discovers_tracked_skills_nested_and_ignores_untracked_or_deleted(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            afk_dir = add_skill(repo, "afk", "---\nname: aa:afk\ndescription: x\n---\n")
            create_dir = add_skill(
                repo,
                "pr-authoring/create",
                '---\nname: "aa:create-pr"\ndescription: x\n---\n',
            )
            handoff_dir = add_skill(
                repo,
                "testing/mattpocock/handoff",
                "---\nname: handoff  # comment\ndescription: x\n---\n",
            )
            fallback_dir = add_skill(
                repo,
                "testing/My_Skill",
                "---\ndescription: no name field\n---\n",
            )
            # Untracked skill and backup file should be ignored.
            add_skill(
                repo,
                "testing/untracked-draft",
                "---\nname: aa:draft\ndescription: x\n---\n",
                track=False,
            )
            (afk_dir / "SKILL.md.orig").write_text("backup", encoding="utf-8")
            # Tracked skill deleted on disk before git rm should also be ignored.
            deleted_dir = add_skill(
                repo,
                "testing/removed-local",
                "---\nname: aa:removed\ndescription: x\n---\n",
            )
            (deleted_dir / "SKILL.md").unlink()

            discovered = installer.discover_skills(repo)

            self.assertEqual(
                {s.installed_name: s.source_dir for s in discovered},
                {
                    "aa-afk": afk_dir.resolve(),
                    "aa-create-pr": create_dir.resolve(),
                    "handoff": handoff_dir.resolve(),
                    "my-skill": fallback_dir.resolve(),
                },
            )

    def test_installed_name_stays_stable_when_skill_moves_out_of_testing(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            before_dir = add_skill(
                repo,
                "testing/babysit-pr",
                "---\nname: aa:babysit-pr\ndescription: x\n---\n",
            )
            before = installer.discover_skills(repo)
            self.assertEqual([s.installed_name for s in before], ["aa-babysit-pr"])
            self.assertEqual(before[0].source_dir, before_dir.resolve())

            after_dir = repo / "babysit-pr"
            subprocess.run(
                ["git", "-C", str(repo), "mv", "testing/babysit-pr", "babysit-pr"],
                check=True,
                capture_output=True,
                text=True,
            )
            after = installer.discover_skills(repo)
            self.assertEqual([s.installed_name for s in after], ["aa-babysit-pr"])
            self.assertEqual(after[0].source_dir, after_dir.resolve())

    def test_rejects_duplicate_installed_names(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            add_skill(repo, "alpha", "---\nname: aa:shared\ndescription: x\n---\n")
            add_skill(
                repo,
                "testing/beta",
                "---\nname: aa-shared\ndescription: x\n---\n",
            )

            with self.assertRaises(installer.DiscoveryError) as ctx:
                installer.discover_skills(repo)

            message = str(ctx.exception)
            self.assertIn("aa-shared", message)
            self.assertIn("alpha/SKILL.md", message)
            self.assertIn("testing/beta/SKILL.md", message)

    def test_rejects_skill_at_repository_root(self):
        installer = load_installer()
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp) / "repo"
            repo.mkdir()
            init_repo(repo)

            root_skill = repo / "SKILL.md"
            root_skill.write_text("---\nname: root\ndescription: x\n---\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(repo), "add", "SKILL.md"],
                check=True,
                capture_output=True,
                text=True,
            )

            with self.assertRaises(installer.DiscoveryError):
                installer.discover_skills(repo)

    def test_discovers_all_skills_in_this_repository(self):
        installer = load_installer()
        discovered = installer.discover_skills(REPO_ROOT)
        self.assertEqual(
            [s.installed_name for s in discovered],
            [
                "aa-afk",
                "aa-babysit-pr",
                "aa-create-pr",
                "aa-create-pr-screenshots",
                "aa-publish-review",
                "aa-review-code",
                "aa-sharpen-skill",
                "handoff",
            ],
        )


class InstallSkillsCLITest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            text=True,
            capture_output=True,
        )

    def test_installs_to_all_default_clients_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            home = base / "home"
            repo.mkdir()
            home.mkdir()
            init_repo(repo)

            afk_dir = add_skill(repo, "afk", "---\nname: aa:afk\ndescription: v1\n---\n")
            nested_dir = add_skill(
                repo,
                "testing/babysit-pr",
                "---\nname: aa:babysit-pr\ndescription: v1\n---\n",
            )

            first = self.run_cli("--repo", str(repo), "--home", str(home))
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            expected_dirs = {
                "claude": home / ".claude" / "skills",
                "codex": home / ".codex" / "skills",
                "agents": home / ".agents" / "skills",
                "antigravity": home / ".gemini" / "config" / "skills",
                "gemini": home / ".gemini" / "skills",
            }
            for client, target_dir in expected_dirs.items():
                afk_link = target_dir / "aa-afk"
                babysit_link = target_dir / "aa-babysit-pr"
                self.assertTrue(afk_link.is_symlink(), f"{client} missing aa-afk link")
                self.assertTrue(
                    babysit_link.is_symlink(), f"{client} missing aa-babysit-pr link"
                )
                self.assertEqual(afk_link.resolve(), afk_dir.resolve())
                self.assertEqual(babysit_link.resolve(), nested_dir.resolve())

            # Edits in the checkout take effect immediately through the symlinks.
            (afk_dir / "SKILL.md").write_text(
                "---\nname: aa:afk\ndescription: edited\n---\n", encoding="utf-8"
            )
            for target_dir in expected_dirs.values():
                self.assertIn(
                    "description: edited",
                    (target_dir / "aa-afk" / "SKILL.md").read_text(encoding="utf-8"),
                )

            # Repeated runs are idempotent.
            second = self.run_cli("--repo", str(repo), "--home", str(home))
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("0 installed, 0 updated, 0 removed, 2 unchanged", second.stdout)

    def test_updates_links_after_move_out_of_testing_with_one_entry_per_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            claude_dir = base / "claude-skills"
            codex_dir = base / "codex-skills"
            repo.mkdir()
            init_repo(repo)

            add_skill(
                repo,
                "testing/babysit-pr",
                "---\nname: aa:babysit-pr\ndescription: x\n---\n",
            )
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "Add babysit-pr"],
                check=True,
                capture_output=True,
                text=True,
            )

            first = self.run_cli(
                "--repo",
                str(repo),
                "--target",
                f"claude={claude_dir}",
                "--target",
                f"codex={codex_dir}",
            )
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

            subprocess.run(
                ["git", "-C", str(repo), "mv", "testing/babysit-pr", "babysit-pr"],
                check=True,
                capture_output=True,
                text=True,
            )

            second = self.run_cli(
                "--repo",
                str(repo),
                "--target",
                f"claude={claude_dir}",
                "--target",
                f"codex={codex_dir}",
            )
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("1 updated", second.stdout)

            for target_dir in (claude_dir, codex_dir):
                entries = sorted(p.name for p in target_dir.iterdir())
                self.assertEqual(entries, ["aa-babysit-pr"])
                self.assertEqual(
                    (target_dir / "aa-babysit-pr").resolve(),
                    (repo / "babysit-pr").resolve(),
                )

    def test_installs_new_skills_prunes_stale_repo_links_and_preserves_unrelated(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            other_repo = base / "other-repo"
            target_dir = base / "skills-target"
            repo.mkdir()
            other_repo.mkdir()
            target_dir.mkdir()
            init_repo(repo)

            # Unrelated entries in target_dir that must never be touched.
            system_dir = target_dir / ".system"
            system_dir.mkdir()
            (system_dir / "marker.txt").write_text("keep", encoding="utf-8")

            other_skill = other_repo / "foreign"
            other_skill.mkdir()
            foreign_link = target_dir / "foreign-skill"
            foreign_link.symlink_to(other_skill)

            broken_foreign = target_dir / "broken-foreign"
            broken_foreign.symlink_to(other_repo / "missing")

            add_skill(repo, "afk", "---\nname: aa:afk\ndescription: x\n---\n")
            add_skill(
                repo,
                "testing/old-skill",
                "---\nname: aa:old-skill\ndescription: x\n---\n",
            )
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "Initial skills"],
                check=True,
                capture_output=True,
                text=True,
            )

            first = self.run_cli("--repo", str(repo), "--target", f"custom={target_dir}")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertTrue((target_dir / "aa-old-skill").is_symlink())

            # Remove testing/old-skill, rename aa:afk -> aa:afk-v2, and add a new skill.
            subprocess.run(
                ["git", "-C", str(repo), "rm", "-rq", "testing/old-skill"],
                check=True,
                capture_output=True,
                text=True,
            )
            (repo / "afk" / "SKILL.md").write_text(
                "---\nname: aa:afk-v2\ndescription: renamed\n---\n", encoding="utf-8"
            )
            add_skill(
                repo,
                "testing/brand-new",
                "---\nname: aa:brand-new\ndescription: x\n---\n",
            )

            second = self.run_cli("--repo", str(repo), "--target", f"custom={target_dir}")
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("2 installed, 0 updated, 2 removed", second.stdout)

            # Stale repo-owned links were removed; new ones installed.
            self.assertFalse((target_dir / "aa-old-skill").exists())
            self.assertFalse((target_dir / "aa-old-skill").is_symlink())
            self.assertFalse((target_dir / "aa-afk").is_symlink())
            self.assertEqual(
                (target_dir / "aa-afk-v2").resolve(), (repo / "afk").resolve()
            )
            self.assertEqual(
                (target_dir / "aa-brand-new").resolve(),
                (repo / "testing" / "brand-new").resolve(),
            )

            # Unrelated skills and foreign links remain completely intact.
            self.assertTrue((system_dir / "marker.txt").is_file())
            self.assertTrue(foreign_link.is_symlink())
            self.assertEqual(foreign_link.resolve(), other_skill.resolve())
            self.assertTrue(broken_foreign.is_symlink())

    def test_preserves_and_reports_copies_files_and_conflicting_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            other_repo = base / "other-repo"
            home = base / "home"
            repo.mkdir()
            other_repo.mkdir()
            home.mkdir()
            init_repo(repo)

            add_skill(repo, "afk", "---\nname: aa:afk\ndescription: x\n---\n")
            add_skill(
                repo,
                "sharpen-skill",
                "---\nname: aa:sharpen-skill\ndescription: x\n---\n",
            )
            add_skill(
                repo,
                "testing/publish-review",
                "---\nname: aa:publish-review\ndescription: x\n---\n",
            )

            agents_dir = home / ".agents" / "skills"
            claude_dir = home / ".claude" / "skills"
            agents_dir.mkdir(parents=True)
            claude_dir.mkdir(parents=True)

            # Existing directory copy in ~/.agents/skills.
            copy_dir = agents_dir / "aa-sharpen-skill"
            copy_dir.mkdir()
            (copy_dir / "SKILL.md").write_text("local copy", encoding="utf-8")

            # Existing repo symlink in ~/.agents/skills/aa-afk, chained from ~/.claude/skills/aa-afk.
            (agents_dir / "aa-afk").symlink_to((repo / "afk").resolve())
            (claude_dir / "aa-afk").symlink_to(pathlib.Path("../../.agents/skills/aa-afk"))

            # Existing foreign symlink to another checkout in ~/.claude/skills.
            other_sharpen = other_repo / "sharpen-skill"
            other_sharpen.mkdir()
            (claude_dir / "aa-sharpen-skill").symlink_to(other_sharpen)

            # Existing regular file in ~/.agents/skills/aa-publish-review.
            (agents_dir / "aa-publish-review").write_text("not a dir", encoding="utf-8")

            result = self.run_cli(
                "--repo",
                str(repo),
                "--home",
                str(home),
                "--client",
                "agents",
                "--client",
                "claude",
            )
            # Conflicts cause a non-zero exit while non-conflicting skills still install.
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

            # Non-conflicting skill in claude was still installed.
            self.assertTrue((claude_dir / "aa-publish-review").is_symlink())
            self.assertEqual(
                (claude_dir / "aa-publish-review").resolve(),
                (repo / "testing" / "publish-review").resolve(),
            )
            # Existing repo-owned symlink in agents stayed unchanged.
            self.assertEqual((agents_dir / "aa-afk").resolve(), (repo / "afk").resolve())

            # Conflicting copy, file, foreign link, and indirect chained link were all preserved.
            self.assertTrue(copy_dir.is_dir() and not copy_dir.is_symlink())
            self.assertEqual(
                (copy_dir / "SKILL.md").read_text(encoding="utf-8"), "local copy"
            )
            self.assertEqual(
                (agents_dir / "aa-publish-review").read_text(encoding="utf-8"),
                "not a dir",
            )
            self.assertEqual(
                pathlib.Path(
                    subprocess.check_output(
                        ["readlink", str(claude_dir / "aa-afk")], text=True
                    ).strip()
                ),
                pathlib.Path("../../.agents/skills/aa-afk"),
            )
            self.assertEqual(
                (claude_dir / "aa-sharpen-skill").resolve(), other_sharpen.resolve()
            )

            # Every conflict is reported in output.
            self.assertIn("conflict", result.stdout.lower())
            self.assertIn("aa-sharpen-skill", result.stdout)
            self.assertIn("aa-publish-review", result.stdout)
            self.assertIn("aa-afk", result.stdout)

    def test_source_collision_fails_before_touching_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            target_dir = base / "target"
            repo.mkdir()
            init_repo(repo)

            add_skill(repo, "one", "---\nname: aa:dup\ndescription: x\n---\n")
            add_skill(repo, "testing/two", "---\nname: aa-dup\ndescription: x\n---\n")

            result = self.run_cli("--repo", str(repo), "--target", f"test={target_dir}")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("aa-dup", result.stderr)
            self.assertFalse(target_dir.exists())

    def test_dry_run_reports_changes_without_modifying_filesystem(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            target_dir = base / "missing-target"
            repo.mkdir()
            init_repo(repo)

            add_skill(repo, "afk", "---\nname: aa:afk\ndescription: x\n---\n")

            result = self.run_cli(
                "--repo", str(repo), "--target", f"test={target_dir}", "--dry-run"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("dry-run", result.stdout.lower())
            self.assertIn("aa-afk", result.stdout)
            self.assertFalse(target_dir.exists())

    def test_supports_comma_separated_clients_and_rejects_conflicting_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            repo = base / "repo"
            home = base / "home"
            repo.mkdir()
            home.mkdir()
            init_repo(repo)
            add_skill(repo, "afk", "---\nname: aa:afk\ndescription: x\n---\n")

            selected = self.run_cli(
                "--repo", str(repo), "--home", str(home), "--client", "antigravity,gemini"
            )
            self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
            self.assertTrue((home / ".gemini" / "config" / "skills" / "aa-afk").is_symlink())
            self.assertTrue((home / ".gemini" / "skills" / "aa-afk").is_symlink())
            self.assertFalse((home / ".claude").exists())
            self.assertFalse((home / ".codex").exists())
            self.assertFalse((home / ".agents").exists())

            invalid = self.run_cli(
                "--repo",
                str(repo),
                "--client",
                "claude",
                "--target",
                str(base / "custom"),
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("Cannot combine --target with --client", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
