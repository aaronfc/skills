#!/usr/bin/env python3
"""Unit tests for the deterministic aa:babysit-pr waiter."""

from __future__ import annotations

import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "wait-for-pr.py"
SPEC = importlib.util.spec_from_file_location("wait_for_pr", SCRIPT)
wait_for_pr = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(wait_for_pr)


def snapshot(**overrides):
    value = {
        "pr": {
            "state": "open",
            "merged_at": None,
            "closed_at": None,
            "html_url": "https://github.com/acme/widgets/pull/7",
            "title": "Make widgets safer",
            "merged_by": None,
        },
        "conversation_comments": [],
        "reviews": [],
        "inline_comments": [],
    }
    value.update(overrides)
    return value


def user(login="alice", kind="User"):
    return {"login": login, "type": kind}


class TargetParsingTests(unittest.TestCase):
    def test_parses_github_url(self):
        target = wait_for_pr.parse_target(
            "https://github.com/acme/widgets/pull/7?notification_referrer_id=1"
        )

        self.assertEqual(
            target,
            wait_for_pr.Target("github.com", "acme", "widgets", 7),
        )

    def test_parses_github_enterprise_url(self):
        target = wait_for_pr.parse_target(
            "https://git.corp.example/acme/widgets/pull/91/"
        )

        self.assertEqual(
            target,
            wait_for_pr.Target("git.corp.example", "acme", "widgets", 91),
        )

    def test_number_requires_and_uses_an_unambiguous_current_repo(self):
        target = wait_for_pr.parse_target(
            "12", current_repo=("git.corp.example", "acme", "widgets")
        )

        self.assertEqual(
            target,
            wait_for_pr.Target("git.corp.example", "acme", "widgets", 12),
        )
        with self.assertRaisesRegex(ValueError, "current repository"):
            wait_for_pr.parse_target("12")


class ChangeDetectionTests(unittest.TestCase):
    def test_existing_activity_is_only_the_baseline(self):
        existing = snapshot(
            conversation_comments=[
                {
                    "id": 1,
                    "user": user(),
                    "created_at": "2026-07-01T09:00:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-1",
                    "body": "existing conversation comment",
                }
            ],
            reviews=[
                {
                    "id": 2,
                    "user": user("bob"),
                    "state": "APPROVED",
                    "submitted_at": "2026-07-01T09:01:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#pullrequestreview-2",
                    "body": "existing review",
                }
            ],
            inline_comments=[
                {
                    "id": 3,
                    "user": user("carol"),
                    "created_at": "2026-07-01T09:02:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#discussion_r3",
                    "body": "existing inline comment",
                }
            ],
        )

        self.assertIsNone(
            wait_for_pr.detect_event(
                existing, existing, {"approved", "new-comment"}
            )
        )

    def test_new_approval_reports_stable_fields(self):
        baseline = snapshot()
        current = snapshot(
            reviews=[
                {
                    "id": 10,
                    "user": user("reviewer"),
                    "state": "APPROVED",
                    "submitted_at": "2026-07-01T10:00:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#pullrequestreview-10",
                    "body": "Looks good",
                }
            ]
        )

        self.assertEqual(
            wait_for_pr.detect_event(baseline, current, {"approved"}),
            {
                "event": "approved",
                "actor": "reviewer",
                "timestamp": "2026-07-01T10:00:00Z",
                "url": "https://github.com/acme/widgets/pull/7#pullrequestreview-10",
                "review_state": "APPROVED",
                "title": "Make widgets safer",
                "body": "Looks good",
            },
        )

    def test_new_conversation_comment(self):
        current = snapshot(
            conversation_comments=[
                {
                    "id": 11,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T10:01:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-11",
                    "body": "Could this handle empty input?",
                }
            ]
        )

        event = wait_for_pr.detect_event(snapshot(), current, {"new-comment"})

        self.assertEqual(event["event"], "conversation-comment")
        self.assertEqual(event["actor"], "reviewer")
        self.assertEqual(event["body"], "Could this handle empty input?")

    def test_submitted_review_states_are_feedback(self):
        for index, state in enumerate(("COMMENTED", "CHANGES_REQUESTED"), start=20):
            with self.subTest(state=state):
                current = snapshot(
                    reviews=[
                        {
                            "id": index,
                            "user": user("reviewer"),
                            "state": state,
                            "submitted_at": "2026-07-01T10:02:00Z",
                            "html_url": f"https://github.com/acme/widgets/pull/7#pullrequestreview-{index}",
                            "body": "Review body",
                        }
                    ]
                )

                event = wait_for_pr.detect_event(
                    snapshot(), current, {"new-comment"}
                )

                self.assertEqual(event["event"], "submitted-review")
                self.assertEqual(event["review_state"], state)

    def test_inline_review_comment_is_feedback(self):
        current = snapshot(
            inline_comments=[
                {
                    "id": 30,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T10:03:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#discussion_r30",
                    "body": "This branch is unreachable.",
                }
            ]
        )

        event = wait_for_pr.detect_event(snapshot(), current, {"new-comment"})

        self.assertEqual(event["event"], "inline-comment")

    def test_bots_are_ignored_unless_explicitly_included(self):
        current = snapshot(
            conversation_comments=[
                {
                    "id": 40,
                    "user": user("ci-helper[bot]", "Bot"),
                    "created_at": "2026-07-01T10:04:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-40",
                    "body": "Build passed.",
                }
            ]
        )

        self.assertIsNone(
            wait_for_pr.detect_event(snapshot(), current, {"new-comment"})
        )
        self.assertEqual(
            wait_for_pr.detect_event(
                snapshot(), current, {"new-comment"}, include_bots=True
            )["actor"],
            "ci-helper[bot]",
        )

    def test_merged_and_closed_are_terminal_without_being_requested(self):
        merged = snapshot(
            pr={
                **snapshot()["pr"],
                "state": "closed",
                "merged_at": "2026-07-01T11:00:00Z",
                "closed_at": "2026-07-01T11:00:00Z",
                "merged_by": user("maintainer"),
            }
        )
        closed = snapshot(
            pr={
                **snapshot()["pr"],
                "state": "closed",
                "closed_at": "2026-07-01T11:01:00Z",
            }
        )

        merged_event = wait_for_pr.detect_event(snapshot(), merged, {"approved"})
        closed_event = wait_for_pr.detect_event(snapshot(), closed, {"approved"})

        self.assertEqual(merged_event["event"], "merged")
        self.assertEqual(merged_event["actor"], "maintainer")
        self.assertEqual(closed_event["event"], "closed")


class PollingTests(unittest.TestCase):
    def test_healthy_unchanged_polls_emit_no_diagnostics(self):
        changed = snapshot(
            conversation_comments=[
                {
                    "id": 48,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T11:58:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-48",
                    "body": "Now there is an update",
                }
            ]
        )
        responses = iter([snapshot(), snapshot(), changed])
        sleeps = []
        diagnostics = []

        event = wait_for_pr.wait_for_event(
            lambda: next(responses),
            {"new-comment"},
            interval=1,
            sleep=sleeps.append,
            diagnose=diagnostics.append,
        )

        self.assertEqual(event["event"], "conversation-comment")
        self.assertEqual(sleeps, [1, 1])
        self.assertEqual(diagnostics, [])

    def test_transient_startup_failure_recovers_before_capturing_baseline(self):
        changed = snapshot(
            conversation_comments=[
                {
                    "id": 49,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T11:59:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-49",
                    "body": "After startup recovery",
                }
            ]
        )
        responses = iter(
            [
                wait_for_pr.FetchError(
                    "secure enclave is unavailable",
                    transient=True,
                    category="credential-unavailable",
                ),
                snapshot(),
                changed,
            ]
        )
        sleeps = []
        diagnostics = []

        def source():
            value = next(responses)
            if isinstance(value, Exception):
                raise value
            return value

        event = wait_for_pr.wait_for_event(
            source,
            {"new-comment"},
            interval=1,
            max_backoff=4,
            sleep=sleeps.append,
            diagnose=diagnostics.append,
        )

        self.assertEqual(event["event"], "conversation-comment")
        self.assertEqual(sleeps, [2, 1])
        self.assertEqual(
            [notice["phase"] for notice in diagnostics], ["baseline", "baseline"]
        )
        self.assertFalse(diagnostics[1]["baseline_preserved"])

    def test_transient_failure_backs_off_then_recovers(self):
        changed = snapshot(
            conversation_comments=[
                {
                    "id": 50,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T12:00:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-50",
                    "body": "One thought",
                }
            ]
        )
        responses = iter(
            [
                snapshot(),
                wait_for_pr.FetchError(
                    "temporary outage", transient=True, category="network"
                ),
                changed,
            ]
        )
        sleeps = []
        diagnostics = []

        def source():
            value = next(responses)
            if isinstance(value, Exception):
                raise value
            return value

        event = wait_for_pr.wait_for_event(
            source,
            {"new-comment"},
            interval=1,
            max_backoff=8,
            sleep=sleeps.append,
            diagnose=diagnostics.append,
        )

        self.assertEqual(event["event"], "conversation-comment")
        self.assertEqual(sleeps, [1, 2])
        self.assertEqual(
            [notice["status"] for notice in diagnostics],
            ["poll-retry", "poll-recovered"],
        )
        self.assertEqual(
            diagnostics[0],
            {
                "status": "poll-retry",
                "phase": "poll",
                "attempt": 1,
                "delay_seconds": 2,
                "max_backoff_seconds": 8,
                "error_class": "network",
                "error": "temporary outage",
                "guidance": "waiter is still running; resume this process instead of restarting it",
            },
        )
        self.assertEqual(diagnostics[1]["attempts"], 1)
        self.assertTrue(diagnostics[1]["baseline_preserved"])

    def test_repeated_failures_cap_backoff_and_reset_after_recovery(self):
        changed = snapshot(
            conversation_comments=[
                {
                    "id": 51,
                    "user": user("reviewer"),
                    "created_at": "2026-07-01T12:01:00Z",
                    "html_url": "https://github.com/acme/widgets/pull/7#issuecomment-51",
                    "body": "Connection is back",
                }
            ]
        )
        def offline():
            return wait_for_pr.FetchError(
                "network is unreachable", transient=True, category="network"
            )
        responses = iter(
            [
                snapshot(),
                offline(),
                offline(),
                offline(),
                snapshot(),
                offline(),
                changed,
            ]
        )
        sleeps = []
        diagnostics = []

        def source():
            value = next(responses)
            if isinstance(value, Exception):
                raise value
            return value

        event = wait_for_pr.wait_for_event(
            source,
            {"new-comment"},
            interval=1,
            max_backoff=4,
            sleep=sleeps.append,
            diagnose=diagnostics.append,
        )

        self.assertEqual(event["event"], "conversation-comment")
        self.assertEqual(sleeps, [1, 2, 4, 4, 1, 2])
        retries = [item for item in diagnostics if item["status"] == "poll-retry"]
        recoveries = [
            item for item in diagnostics if item["status"] == "poll-recovered"
        ]
        self.assertEqual([item["attempt"] for item in retries], [1, 2, 3, 1])
        self.assertEqual([item["delay_seconds"] for item in retries], [2, 4, 4, 2])
        self.assertEqual([item["attempts"] for item in recoveries], [3, 1])

    def test_authentication_failure_is_reported_without_retrying(self):
        calls = 0

        def source():
            nonlocal calls
            calls += 1
            raise wait_for_pr.FetchError("authentication required", transient=False)

        event = wait_for_pr.wait_for_event(
            source,
            {"approved"},
            interval=1,
            sleep=lambda _: self.fail("fatal errors must not sleep"),
        )

        self.assertEqual(event["event"], "error")
        self.assertIn("authentication required", event["body"])
        self.assertEqual(calls, 1)

    def test_interruption_returns_a_machine_readable_result(self):
        event = wait_for_pr.wait_for_event(
            lambda: snapshot(),
            {"approved"},
            interval=1,
            sleep=lambda _: (_ for _ in ()).throw(KeyboardInterrupt()),
        )

        self.assertEqual(event["event"], "interrupted")


class GitHubClientTests(unittest.TestCase):
    def test_uses_target_hostname_and_read_only_get_requests(self):
        commands = []

        def runner(command, **kwargs):
            commands.append((command, kwargs))
            return type("Result", (), {"returncode": 0, "stdout": "[]\n", "stderr": ""})()

        client = wait_for_pr.GitHubClient("git.corp.example", runner=runner)

        self.assertEqual(client.get("repos/acme/widgets/pulls/7/reviews"), [])
        self.assertEqual(
            commands[0][0],
            [
                "gh",
                "api",
                "--hostname",
                "git.corp.example",
                "--method",
                "GET",
                "repos/acme/widgets/pulls/7/reviews",
            ],
        )

    def test_missing_gh_is_a_stable_non_transient_error(self):
        def runner(command, **kwargs):
            raise FileNotFoundError("gh not found")

        client = wait_for_pr.GitHubClient("github.com", runner=runner)

        with self.assertRaises(wait_for_pr.FetchError) as raised:
            client.get("repos/acme/widgets/pulls/7")

        self.assertFalse(raised.exception.transient)
        self.assertIn("could not run gh", str(raised.exception))

    def test_locked_keychain_failure_is_retryable(self):
        def runner(command, **kwargs):
            return type(
                "Result",
                (),
                {
                    "returncode": 1,
                    "stdout": "",
                    "stderr": "failed to retrieve token: user interaction is not allowed (OSStatus error -25308)",
                },
            )()

        client = wait_for_pr.GitHubClient("github.com", runner=runner)

        with self.assertRaises(wait_for_pr.FetchError) as raised:
            client.get("repos/acme/widgets/pulls/7")

        self.assertTrue(raised.exception.transient)
        self.assertEqual(raised.exception.category, "credential-unavailable")


class FailureClassificationTests(unittest.TestCase):
    def test_classifies_recoverable_and_permanent_failures(self):
        cases = {
            "error connecting to api.github.com: network is unreachable": (
                True,
                "network",
            ),
            'Get "https://api.github.com": EOF': (True, "network"),
            "failed to retrieve token: secure enclave is unavailable": (
                True,
                "credential-unavailable",
            ),
            "failed to retrieve token: keyring is locked": (
                True,
                "credential-unavailable",
            ),
            "gh: API rate limit exceeded (HTTP 403)": (True, "rate-limit"),
            "gh: Service Unavailable (HTTP 503)": (True, "github"),
            "gh: Bad credentials (HTTP 401)": (False, "permanent"),
            "gh: Not Found (HTTP 404)": (False, "permanent"),
        }

        for message, expected in cases.items():
            with self.subTest(message=message):
                classification = wait_for_pr.classify_failure(message)
                self.assertEqual(
                    (classification.transient, classification.category), expected
                )


if __name__ == "__main__":
    unittest.main()
