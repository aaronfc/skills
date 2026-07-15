---
name: aa:afk
description: Pick up a ready GitHub issue and work it end-to-end on your own — find an unblocked task, implement it, and open a PR. Use when the user wants you to work autonomously, "grab a ready issue", "work while I'm afk", or says "/aa:afk".
---

# AFK — work a ready issue on your own

1. List open issues: `gh issue list --label ready-for-agent --state open`.
2. Pick one whose dependencies are all met by analyzing its content and related issues. Skip anything blocked by unfinished work.
3. When several issues qualify, take the smallest.
4. Branch off the default branch.
5. Implement the slice with `/tdd` — one vertical slice at a time, red → green, until the acceptance criteria are met.
6. Open the PR with `/aa:create-pr` to draft the description (why → what, `Closes #N`).
7. Report which issue you took and the PR link.

Work the whole thing without checking in, unless the issue is ambiguous or you hit a real blocker — then stop and ask.
