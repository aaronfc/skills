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

1. Branch off the default branch. Before editing, explain the problem with one concrete user-facing example and identify coherent commit boundaries.
2. Implement one vertical slice at a time with test-driven development: red → green. Commit each completed piece with its relevant tests before starting the next. Use a short subject and a body explaining why the change is needed. Split by independently reviewable behavior, not file type or line count; explain material changes to the boundaries.
3. Before publishing, inspect the base-to-head diff and full commit messages. Run `python3 <skill-dir>/scripts/check_commits.py <base-ref>` to list actual subjects and detect missing bodies. Also judge whether each commit is coherent and its message explains why; the check cannot judge that. Correct your own commits before handoff without requesting supervision; do not rewrite others' commits or published history without authorization.
4. Open the PR with `/aa:create-pr` to draft and inspect the actual description (`Fixes #n`, why → what).
5. Report the issue and PR link, actual commit subjects, observed validation results, and unmet requirements. Do not substitute a self-reported checklist for evidence.

Explain behavior before platform internals. Start with a familiar example, define necessary unfamiliar terms, and distinguish platform conventions from choices made for this change. Keep explanations natural and technically accurate.

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
5. After all report comments succeed, remove `ready-for-agent`, add `needs-human` (if label exists) and leave the issue open. Only a human closes a research issue or makes it ready for another automatic pass.
6. Report which issue you researched and link the new comment.

Work the whole thing without checking in, unless the issue is ambiguous or you hit a real blocker — then stop and ask.
On these rare occasions add `needs-human` label (if label exists).
