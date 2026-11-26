import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

cli = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/my-words"))
NOW = 1800000000
PR = "https://github.example/owner/repo/pull/12"


class Workflow(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store = Path(tmp.name) / "state"
        self.body = self.store.with_name("body")
        self.body.write_text("First draft\n")
        self.calls = []
        self.login = "aaronfc"
        self.head = "abc"
        self.activity = {}
        self.failure = None
        for obj, name, value in [(subprocess, "run", self.github),
                                 (cli["time"], "time", lambda: NOW),
                                 (cli["os"], "umask", lambda mask: None)]:
            mock = patch.object(obj, name, value)
            mock.start()
            self.addCleanup(mock.stop)

    def github(self, cmd, input, **kwargs):
        prefix = "repos/owner/repo/"
        self.assertEqual(cmd[:4], ["gh", "api", "--hostname", "github.example"])
        path = cmd[4].removeprefix(prefix).split("?")[0]
        self.calls.append(path)
        if input is not None:
            self.payload = json.loads(input)
            self.comment = dict(body=self.payload["body"], user={"login": self.login},
                                html_url=PR + "#comment", created_at=cli["utc"](NOW))
            if "path" in self.payload:
                self.comment.update(path=self.payload["path"], side=self.payload["side"],
                                    original_commit_id=self.head, original_line=self.payload["line"])
            if path.endswith("/replies"):
                self.comment["in_reply_to_id"] = int(path.split("/")[-2])
            if self.failure:
                return subprocess.CompletedProcess(cmd, 1, "", self.failure)
            result = self.comment
        elif "--paginate" in cmd:
            result = [[], self.activity.get(path, [])]
        elif path == "user":
            result = {"login": self.login}
        else:
            self.assertEqual(path, "pulls/12")
            result = {"head": {"sha": self.head}, "state": "open"}
        return subprocess.CompletedProcess(cmd, 0, json.dumps(result), "")

    def invoke(self, *args):
        out = io.StringIO()
        with patch.object(sys, "argv", ["my-words", "--store", str(self.store), *args]):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                cli["main"]()
        return json.loads(out.getvalue())

    def draft(self, *target, head_age=0, discussion_age=0):
        return self.invoke("draft", "--pr", PR, "--login", "aaronfc", "--head", "abc",
                           "--head-checked", str(NOW - head_age),
                           "--discussion-checked", str(NOW - discussion_age),
                           "--body-file", str(self.body), *target)["id"]

    def edit(self, key):
        return self.invoke("draft", "--replaces", key, "--body-file", str(self.body))["id"]

    def test_discard_current_revision(self):
        first = self.draft("--top-level")
        current = self.edit(first)
        with self.assertRaisesRegex(ValueError, "superseded"):
            self.invoke("discard", first)
        for _ in range(2):
            self.assertEqual(self.invoke("discard", current), {"id": current, "status": "discarded"})
        with self.assertRaisesRegex(ValueError, "discarded"):
            self.invoke("send", current)
        with self.assertRaisesRegex(ValueError, "current revision"):
            self.edit(current)
        self.assertEqual(self.calls, [])

    def test_edit_and_immediate_publish(self):
        first = self.draft("--inline", "some file", "LEFT", "9")
        self.body.write_bytes(b"Use `x`.\r\n")
        edited = self.edit(first)
        with self.assertRaisesRegex(ValueError, "superseded"):
            self.invoke("send", first)
        sent = self.invoke("send", edited)
        with self.assertRaisesRegex(ValueError, "sent"):
            self.invoke("discard", edited)
        self.assertEqual(sent, self.invoke("send", edited))
        self.assertEqual(self.calls, ["user", "pulls/12/comments"])
        self.assertEqual(self.payload, dict(path="some file", line=9, side="LEFT",
                                            commit_id="abc", body="Use `x`.\r\n"))

    def test_stale_head_survives_edit(self):
        key = self.edit(self.draft("--top-level", head_age=301))
        self.head = "def"
        with self.assertRaisesRegex(ValueError, "head def"):
            self.invoke("send", key)
        self.assertEqual(self.calls, ["pulls/12"])

    def test_stale_discussion_survives_edit(self):
        key = self.edit(self.draft("--reply", "8", discussion_age=301))
        self.activity["pulls/12/reviews"] = [dict(submitted_at=cli["utc"](NOW), html_url="/review")]
        with self.assertRaisesRegex(ValueError, "/review"):
            self.invoke("send", key)
        self.assertEqual(self.calls, ["issues/12/comments", "pulls/12/comments", "pulls/12/reviews"])

    def test_stale_unchanged_and_wrong_account(self):
        key = self.draft("--top-level", head_age=301, discussion_age=301)
        self.login = "other"
        with self.assertRaisesRegex(ValueError, "account"):
            self.invoke("send", key)
        self.assertFalse(hasattr(self, "payload"))
        self.login = "aaronfc"
        self.assertEqual(self.invoke("send", key)["url"], PR + "#comment")
        self.assertEqual(self.calls[-1], "issues/12/comments")

    def test_ambiguous_reply_recovers_only_at_original_thread(self):
        key = self.draft("--reply", "8")
        self.failure = "connection reset"
        with self.assertRaisesRegex(ValueError, "Cannot confirm"):
            self.invoke("send", key)
        with self.assertRaisesRegex(ValueError, "pending"):
            self.invoke("discard", key)
        self.activity["pulls/12/comments"] = [dict(self.comment, in_reply_to_id=9), self.comment]
        self.assertEqual(self.invoke("send", key)["url"], PR + "#comment")
        self.assertEqual(self.calls.count("pulls/12/comments/8/replies"), 1)

    def test_rejected_post_can_be_revised(self):
        key = self.draft("--inline", "file", "RIGHT", "3")
        self.failure = "gh: Validation Failed (HTTP 422)"
        with self.assertRaisesRegex(ValueError, "422"):
            self.invoke("send", key)
        self.assertTrue(self.edit(key))
