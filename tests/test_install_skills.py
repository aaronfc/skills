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


if __name__ == "__main__":
    unittest.main()
