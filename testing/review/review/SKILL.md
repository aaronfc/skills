---
name: aa:review
description: Use when the user wants to write a PR description / review, "open a PR", "describe these changes", or says "/aa:review". Drafts a PR body following the repo's GitHub PR template, leading with the why.
allowed-tools: Bash(gh *), Bash(git *), Read, Glob, Grep
---
# PR review

1. Use the repo's PR template if present (`.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, or `docs/`). Otherwise: **Why** → **What** → references.
2. Add `Fixes #XXX` (or `Relates to #XXX`) when an issue is known from context/branch name.
3. **Why**: explain the motivation and problem carefully — this is the part reviewers most need.
4. **What**: summarize the changes so the reviewer knows how to approach the diff.
5. If the changes clearly affect the UI, also run `/aa:review:screenshot`.
