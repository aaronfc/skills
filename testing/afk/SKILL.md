---
name: aa:afk
description: Work a GitHub issue end-to-end on your own — use a supplied issue or find a ready unblocked task, then either implement it and open a PR or research it and post evidence-backed findings. Use when the user wants you to work autonomously, "grab a ready issue", "work while I'm afk", or says "/aa:afk".
---

# AFK — work a ready issue on your own

## Choose and understand the issue

1. If the invocation supplies an issue URL or number, use that issue directly; do not choose another. Otherwise, list open issues with `gh issue list --label ready-for-agent --state open`, skip those blocked by unfinished dependencies, and pick the smallest qualifying issue.
2. Before choosing or acting, read the title, body, and complete chronological comment history for each candidate you inspect. Use `gh issue view <issue> --comments`; paginate comments with `gh api` if needed. Treat newer human comments as requirements or refinements, including requests for another pass.
3. Classify the chosen issue after reading the whole thread:
   - Use **research** when the issue explicitly asks for research or clearly asks only to investigate, explore, compare, or recommend.
   - Otherwise use **implementation**. Stop and ask only when the intended deliverable is genuinely ambiguous or another real blocker exists.

## Implementation

1. Branch off the default branch.
2. Implement one vertical slice at a time with test-driven development: red → green, until the acceptance criteria are met.
3. Open the PR with `/aa:create-pr` to draft the description (`Fixes #n`, why → what).
4. Report which issue you took and the PR link.

## Research

1. Research until the issue's questions and acceptance criteria, as refined by all comments, are answered. Do not create a branch, repository files, commits, or a PR. Disposable experiments and files are allowed outside the repository; leave the worktree exactly as found.
2. Support every research claim with inspectable proof:
   - Cite repository evidence with paths, relevant excerpts, and line references where useful.
   - Cite authoritative external sources with links.
   - For experiments, include enough code, commands, inputs, environment details, and observed output to inspect or reproduce the result.
   - If local code or files helped prove something, include their relevant contents and results in the report; a local path alone is not evidence.
   - Never present an inference or recommendation as an observed fact.
3. Write a self-contained Markdown report that clearly separates observed facts and their evidence from inferences, recommendations, and uncertainty. Prefer **Conclusion**, **Findings and evidence**, **Recommendation or next steps**, and **Open questions or uncertainty**, but adapt, rename, or omit sections when another structure preserves that separation more clearly.
4. Append the report as a new issue comment; never replace a previous research comment. `gh issue comment` cannot upload attachments: keep details in one or more comments and link existing sources when useful.
5. After all report comments succeed, remove `ready-for-agent`, add `ready-for-human` (create the label first if missing, following repository conventions), and leave the issue open. Only a human closes a research issue or makes it ready for another automatic pass.
6. Report which issue you researched and link the new comment.

Work the whole thing without checking in, unless the issue is ambiguous or you hit a real blocker — then stop and ask.
