---
name: aa:create-pr
description: Create or update a GitHub PR only when explicitly requested or invoked with /aa:create-pr. Not for code review or review comments.
allowed-tools: Bash(*), Read, Glob, Grep
---
# Create or update a PR

Create new PRs with `gh pr create --draft`, even if repository guidance says otherwise. Never run `gh pr ready`; leave readiness to a human. Preserve existing PR review state. Return the PR URL.

Inspect the branch, diff, commits, linked issue, existing PR body, and repository setup/test instructions. Preserve repository PR template sections; add separate **Testing Steps** and **Proofs** if missing. Without a template, use **Why → What → Testing Steps → Proofs**. Include `Fixes #N` or `Relates to #N` for an issue identified from context or the branch; use `Fixes` only when resolved.

Write for a reviewer who has not seen the conversation. Omit runtime-testing statements for changes with no runtime effect.
- **Why:** State the problem and why it matters. Use a before/after example if clearer.
- **What:** Explain the final approach and where review needs attention. Group changes by purpose, not file or implementation step. Include internal details only to explain correctness, risk, or tradeoffs.
- **Testing Steps:** For trivial changes, give one inspection action and its expected result in one sentence. Otherwise, give the shortest path from a clean checkout to exercising the change: required setup, exact commands or actions, and expected results. Verify command syntax. Include a cheap, important edge case and cleanup when needed. Automated tests alone do not replace exercising changed behavior. If direct exercise is infeasible, explain why and give the closest reproducible check.
- **Proofs:** Lead with compact, observed evidence of the change, then exact automated-check commands and outcomes. Match evidence to the change: CLI/API output, UI screenshots, prompt outputs and scores on identical inputs, comparable benchmarks, or rendered/diff checks. For useful before/after comparisons, use the same flow on both versions when safe, preserving the working tree through isolated worktrees or existing artifacts. Summarize long artifacts and link them. Mark relevant unavailable evidence `Not run (<reason>)`.

Before writing, run the representative flow and relevant checks when safe and feasible. For UI changes, use `/aa:create-pr:screenshots` and put its before/after evidence under **Proofs**.

On every create or update, rewrite the title and whole body against the current diff and evidence. Remove stale claims, repetition, debugging history, and conversation details; retain abandoned approaches only to explain a current tradeoff. Keep only what helps understand, review, or verify the change. For trivial changes, use one sentence per section. Do not repeat results or explain why unrelated checks were unnecessary; template sections may point to the relevant evidence instead.

Use short sentences, plain English, and familiar technical terms. Explain necessary unfamiliar terms; avoid idioms and invented jargon. Never invent evidence or hide material risks, limitations, breaking changes, or failed/missing checks. Distinguish observed results from expectations and uncertainty.
