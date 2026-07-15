---
name: aa:create-pr
description: Create or update a GitHub pull request for the current branch. Use only when the user explicitly asks to create/open a PR, update/edit an existing PR, or invokes "/aa:create-pr". Do not use for code review, reviewing a pull request or diff, finding bugs, or leaving review comments. Follows the repository's PR template and writes a why-first PR body.
allowed-tools: Bash(gh *), Bash(git *), Read, Glob, Grep
---
# Create or update a PR

Use this workflow only to create or update a PR. If the user only asks for code review, diff review,
bug finding, approval, or review comments, do not create or edit a PR.

1. Use the repo's PR template if present (`.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, or `docs/`). Otherwise: **Why** → **What** → references.
2. Add `Fixes #XXX` (or `Relates to #XXX`) when an issue is known from context/branch name.
3. **Why**: explain the motivation and problem carefully — this is the part reviewers most need.
4. **What**: summarize the changes so the reviewer knows how to approach the diff.
5. If the changes clearly affect the UI, also run `/aa:create-pr:screenshots`.
