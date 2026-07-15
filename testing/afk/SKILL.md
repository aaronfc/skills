---
name: aa:afk
description: Work a GitHub issue end-to-end on your own — use a supplied issue, or find a ready unblocked task, implement it, and open a PR. Use when the user wants you to work autonomously, "grab a ready issue", "work while I'm afk", or says "/aa:afk".
---

# AFK — work a ready issue on your own

1. If the invocation supplies an issue URL or number, use that issue directly; do not choose another. Otherwise, list open issues with `gh issue list --label ready-for-agent --state open`, skip those blocked by unfinished dependencies, and pick the smallest qualifying issue.
2. Branch off the default branch.
3. Implement one vertical slice at a time with test-driven development: red → green, until the acceptance criteria are met.
4. Open the PR with `/aa:create-pr` to draft the description (`Fixes #n`, why → what).
5. Report which issue you took and the PR link.

Work the whole thing without checking in, unless the issue is ambiguous or you hit a real blocker — then stop and ask.
