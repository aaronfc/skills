#!/usr/bin/env python3
"""Read-only pull-request event waiter backed by the authenticated gh CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any, Callable, NamedTuple
from urllib.parse import quote, unquote, urlparse


DEFAULT_INTERVAL = 60.0
DEFAULT_MAX_BACKOFF = 300.0
FEEDBACK_REVIEW_STATES = {"APPROVED", "COMMENTED", "CHANGES_REQUESTED"}
CONDITIONS = {"approved", "new-comment", "merged"}


class Target(NamedTuple):
    hostname: str
    owner: str
    repo: str
    number: int


class FetchError(RuntimeError):
    def __init__(self, message: str, *, transient: bool):
        super().__init__(message)
        self.transient = transient


def parse_target(
    value: str, current_repo: tuple[str, str, str] | None = None
) -> Target:
    """Resolve a full PR URL or a PR number plus current-repository identity."""
    value = value.strip()
    if value.isdigit():
        if current_repo is None:
            raise ValueError("a PR number requires an unambiguous current repository")
        hostname, owner, repo = current_repo
        return Target(hostname, owner, repo, int(value))

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("target must be a full pull-request URL or a PR number")
    match = re.search(r"/([^/]+)/([^/]+)/pull/(\d+)/?$", parsed.path)
    if not match:
        raise ValueError("URL must end in /OWNER/REPO/pull/NUMBER")
    owner, repo, number = match.groups()
    return Target(
        parsed.hostname,
        unquote(owner),
        unquote(repo),
        int(number),
    )


def _decode_json_stream(raw: str) -> Any:
    decoder = json.JSONDecoder()
    values = []
    position = 0
    while position < len(raw):
        while position < len(raw) and raw[position].isspace():
            position += 1
        if position >= len(raw):
            break
        value, position = decoder.raw_decode(raw, position)
        values.append(value)
    if not values:
        raise ValueError("GitHub returned an empty response")
    if len(values) == 1:
        return values[0]
    if all(isinstance(value, list) for value in values):
        return [item for value in values for item in value]
    return values


def _classify_failure(message: str) -> bool:
    lowered = message.lower()
    transient_markers = (
        "rate limit",
        "secondary rate",
        "temporarily unavailable",
        "temporary failure",
        "timed out",
        "timeout",
        "connection reset",
        "connection refused",
        "could not resolve host",
        "network is unreachable",
        "http 500",
        "http 502",
        "http 503",
        "http 504",
    )
    return any(marker in lowered for marker in transient_markers)


class GitHubClient:
    """Minimal GET-only wrapper around `gh api`."""

    def __init__(
        self,
        hostname: str,
        *,
        runner: Callable[..., Any] = subprocess.run,
    ) -> None:
        self.hostname = hostname
        self.runner = runner

    def get(self, endpoint: str, *, paginate: bool = False) -> Any:
        command = [
            "gh",
            "api",
            "--hostname",
            self.hostname,
            "--method",
            "GET",
            endpoint,
        ]
        if paginate:
            command.append("--paginate")
        try:
            result = self.runner(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as error:
            raise FetchError(f"could not run gh: {error}", transient=False) from error
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "unknown gh failure").strip()
            raise FetchError(
                f"GitHub API request failed: {detail}",
                transient=_classify_failure(detail),
            )
        try:
            return _decode_json_stream(result.stdout)
        except (ValueError, json.JSONDecodeError) as error:
            raise FetchError(
                f"GitHub returned invalid JSON: {error}", transient=True
            ) from error


def resolve_current_repo(
    runner: Callable[..., Any] = subprocess.run,
) -> tuple[str, str, str]:
    try:
        result = runner(
            ["gh", "repo", "view", "--json", "nameWithOwner,url"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise FetchError(f"could not run gh: {error}", transient=False) from error
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown gh failure").strip()
        raise FetchError(
            f"could not resolve current repository: {detail}",
            transient=_classify_failure(detail),
        )
    try:
        data = json.loads(result.stdout)
        owner, repo = data["nameWithOwner"].split("/", 1)
        hostname = urlparse(data["url"]).hostname
        if not hostname:
            raise ValueError("repository URL has no hostname")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise FetchError(
            f"could not parse current repository: {error}", transient=False
        ) from error
    return hostname, owner, repo


class SnapshotSource:
    def __init__(self, target: Target, client: GitHubClient | None = None) -> None:
        self.target = target
        self.client = client or GitHubClient(target.hostname)

    def __call__(self) -> dict[str, Any]:
        owner = quote(self.target.owner, safe="")
        repo = quote(self.target.repo, safe="")
        root = f"repos/{owner}/{repo}"
        number = self.target.number
        pr = self.client.get(f"{root}/pulls/{number}")
        conversation_comments = self.client.get(
            f"{root}/issues/{number}/comments?per_page=100", paginate=True
        )
        reviews = self.client.get(
            f"{root}/pulls/{number}/reviews?per_page=100", paginate=True
        )
        inline_comments = self.client.get(
            f"{root}/pulls/{number}/comments?per_page=100", paginate=True
        )
        if not isinstance(pr, dict) or not all(
            isinstance(items, list)
            for items in (conversation_comments, reviews, inline_comments)
        ):
            raise FetchError("GitHub returned an unexpected response shape", transient=True)
        return {
            "pr": pr,
            "conversation_comments": conversation_comments,
            "reviews": reviews,
            "inline_comments": inline_comments,
        }


def _is_bot(actor: Any) -> bool:
    if not isinstance(actor, dict):
        return False
    login = str(actor.get("login") or "")
    return str(actor.get("type") or "").lower() == "bot" or login.lower().endswith(
        "[bot]"
    )


def _short_text(value: Any, limit: int = 240) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _actor_login(value: Any) -> str | None:
    if isinstance(value, dict) and value.get("login"):
        return str(value["login"])
    return None


def _result(
    event: str,
    *,
    actor: str | None = None,
    timestamp: str | None = None,
    url: str | None = None,
    review_state: str | None = None,
    title: str = "",
    body: str = "",
) -> dict[str, Any]:
    return {
        "event": event,
        "actor": actor,
        "timestamp": timestamp,
        "url": url,
        "review_state": review_state,
        "title": title,
        "body": body,
    }


def _activities(
    snapshot: dict[str, Any], *, include_bots: bool
) -> list[dict[str, Any]]:
    title = _short_text(snapshot.get("pr", {}).get("title"))
    activities = []
    surfaces = (
        (
            "conversation-comment",
            "conversation_comments",
            "created_at",
            None,
        ),
        ("submitted-review", "reviews", "submitted_at", "state"),
        ("inline-comment", "inline_comments", "created_at", None),
    )
    for event, collection, timestamp_field, review_state_field in surfaces:
        for item in snapshot.get(collection, []):
            actor = item.get("user")
            if not include_bots and _is_bot(actor):
                continue
            review_state = (
                str(item.get(review_state_field) or "").upper()
                if review_state_field
                else None
            )
            if event == "submitted-review" and review_state not in FEEDBACK_REVIEW_STATES:
                continue
            activities.append(
                {
                    "key": f"{event}:{item.get('id')}",
                    "event": event,
                    "actor": _actor_login(actor),
                    "timestamp": item.get(timestamp_field),
                    "url": item.get("html_url") or snapshot.get("pr", {}).get("html_url"),
                    "review_state": review_state,
                    "title": title,
                    "body": _short_text(item.get("body")),
                }
            )
    activities.sort(
        key=lambda item: (
            item.get("timestamp") or "",
            item["event"],
            item["key"],
        )
    )
    return activities


def _terminal_event(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    pr = snapshot.get("pr", {})
    common = {
        "url": pr.get("html_url"),
        "title": _short_text(pr.get("title")),
    }
    if pr.get("merged_at"):
        return _result(
            "merged",
            actor=_actor_login(pr.get("merged_by")),
            timestamp=pr.get("merged_at"),
            **common,
        )
    if str(pr.get("state") or "").lower() == "closed":
        return _result("closed", timestamp=pr.get("closed_at"), **common)
    return None


def detect_event(
    baseline: dict[str, Any],
    current: dict[str, Any],
    conditions: set[str],
    *,
    include_bots: bool = False,
) -> dict[str, Any] | None:
    """Return the first matching new activity or terminal PR state."""
    terminal = _terminal_event(current)
    if terminal is not None:
        return terminal

    seen = {
        item["key"] for item in _activities(baseline, include_bots=include_bots)
    }
    for item in _activities(current, include_bots=include_bots):
        if item["key"] in seen:
            continue
        event = item["event"]
        is_approval = (
            event == "submitted-review" and item["review_state"] == "APPROVED"
        )
        if is_approval and "approved" in conditions:
            event = "approved"
        elif "new-comment" not in conditions:
            continue
        return _result(
            event,
            actor=item["actor"],
            timestamp=item["timestamp"],
            url=item["url"],
            review_state=item["review_state"],
            title=item["title"],
            body=item["body"],
        )
    return None


def _error_event(message: str) -> dict[str, Any]:
    return _result("error", body=_short_text(message, 500))


def _interrupted_event() -> dict[str, Any]:
    return _result("interrupted", body="Wait interrupted")


def _seconds(value: float) -> str:
    return f"{value:g}s"


def wait_for_event(
    source: Callable[[], dict[str, Any]],
    conditions: set[str],
    *,
    include_bots: bool = False,
    interval: float = DEFAULT_INTERVAL,
    max_backoff: float = DEFAULT_MAX_BACKOFF,
    sleep: Callable[[float], None] = time.sleep,
    warn: Callable[[str], None] = lambda message: print(
        f"warning: {message}", file=sys.stderr, flush=True
    ),
) -> dict[str, Any]:
    """Capture a baseline, then wait with bounded backoff until an event occurs."""
    try:
        delay = interval
        while True:
            try:
                baseline = source()
                break
            except FetchError as error:
                if not error.transient:
                    return _error_event(str(error))
                delay = min(max_backoff, delay * 2)
                warn(f"{error}; retrying in {_seconds(delay)}")
                sleep(delay)

        terminal = _terminal_event(baseline)
        if terminal is not None:
            return terminal

        delay = interval
        while True:
            sleep(delay)
            try:
                current = source()
            except FetchError as error:
                if not error.transient:
                    return _error_event(str(error))
                delay = min(max_backoff, delay * 2)
                warn(f"{error}; retrying in {_seconds(delay)}")
                continue

            delay = interval
            event = detect_event(
                baseline,
                current,
                conditions,
                include_bots=include_bots,
            )
            if event is not None:
                return event
    except KeyboardInterrupt:
        return _interrupted_event()


def _parse_conditions(values: list[str] | None) -> set[str]:
    requested = values or ["approved,new-comment"]
    conditions = {
        item.strip()
        for value in requested
        for item in value.split(",")
        if item.strip()
    }
    unknown = conditions - CONDITIONS
    if unknown:
        raise ValueError(
            "unknown wait condition(s): " + ", ".join(sorted(unknown))
        )
    if not conditions:
        raise ValueError("at least one wait condition is required")
    return conditions


def _positive_float(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def _human_result(event: dict[str, Any]) -> str:
    parts = [event["event"]]
    if event.get("actor"):
        parts.append(f"by @{event['actor']}")
    if event.get("review_state"):
        parts.append(f"({event['review_state']})")
    if event.get("body"):
        parts.append(f"— {event['body']}")
    if event.get("url"):
        parts.append(event["url"])
    return " ".join(parts)


def _exit_code(event: dict[str, Any], conditions: set[str]) -> int:
    name = event["event"]
    if name == "interrupted":
        return 130
    if name == "error":
        return 2
    if name == "closed":
        return 3
    if name == "merged" and "merged" not in conditions:
        return 3
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wait read-only for pull-request review events via gh.",
        epilog="Exit codes: 0 requested event, 2 error, 3 unrequested terminal state, 130 interrupted.",
    )
    parser.add_argument("target", help="full PR URL, or PR number in the current repo")
    parser.add_argument(
        "--until",
        action="append",
        metavar="CONDITION[,CONDITION...]",
        help="approved, new-comment, or merged (default: approved,new-comment)",
    )
    parser.add_argument(
        "--include-bots",
        action="store_true",
        help="include bot-authored activity (ignored by default)",
    )
    parser.add_argument(
        "--interval",
        type=_positive_float,
        default=DEFAULT_INTERVAL,
        metavar="SECONDS",
        help=f"poll interval (default: {DEFAULT_INTERVAL:g})",
    )
    parser.add_argument(
        "--max-backoff",
        type=_positive_float,
        default=DEFAULT_MAX_BACKOFF,
        metavar="SECONDS",
        help=f"maximum retry delay (default: {DEFAULT_MAX_BACKOFF:g})",
    )
    parser.add_argument(
        "--format",
        choices=("json", "human"),
        default="json",
        help="result format (default: json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        conditions = _parse_conditions(args.until)
        current_repo = resolve_current_repo() if args.target.strip().isdigit() else None
        target = parse_target(args.target, current_repo=current_repo)
        if args.max_backoff < args.interval:
            raise ValueError("--max-backoff must be at least --interval")
        event = wait_for_event(
            SnapshotSource(target),
            conditions,
            include_bots=args.include_bots,
            interval=args.interval,
            max_backoff=args.max_backoff,
        )
    except (FetchError, ValueError) as error:
        event = _error_event(str(error))

    if args.format == "human":
        print(_human_result(event), flush=True)
    else:
        print(json.dumps(event, sort_keys=True), flush=True)
    return _exit_code(event, conditions if "conditions" in locals() else set())


if __name__ == "__main__":
    raise SystemExit(main())
