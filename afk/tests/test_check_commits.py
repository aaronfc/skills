import pathlib
import subprocess
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'check_commits.py'


class CheckCommitsTest(unittest.TestCase):
    def test_only_branch_commits_require_bodies(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(
                    ['git', '-C', directory, *args], text=True
                ).strip()

            git('init', '-q')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.com')
            git('commit', '--allow-empty', '-qm', 'Existing base without body')
            base = git('rev-parse', 'HEAD')
            git('commit', '--allow-empty', '-qm', 'Validate addresses',
                '-m', 'Reject malformed addresses before saving subscriptions.')

            def check():
                return subprocess.run(
                    ['python3', str(SCRIPT), base], cwd=directory,
                    text=True, capture_output=True,
                )

            passed = check()
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn('Validate addresses', passed.stdout)
            git('commit', '--allow-empty', '-qm', 'Add unsubscribe link')
            failed = check()
            self.assertEqual(failed.returncode, 1, failed.stderr)
            self.assertIn('Add unsubscribe link', failed.stdout)
            self.assertIn('missing body', failed.stdout)
            git('commit', '--amend', '--allow-empty', '-qm', 'Add unsubscribe link',
                '-m', 'Let subscribers stop future emails from each message.')
            fixed = check()
            self.assertEqual(fixed.returncode, 0, fixed.stderr)

    def test_invalid_base_fails(self):
        result = subprocess.run(
            ['python3', str(SCRIPT), 'refs/heads/nonexistent-issue3-base'],
            text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
