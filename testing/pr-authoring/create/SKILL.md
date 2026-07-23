---
name: aa:create-pr
description: Create or update a GitHub pull request for the current branch. Use only when the user explicitly asks to create/open a PR, update/edit an existing PR, or invokes "/aa:create-pr". Do not use for code review, reviewing a pull request or diff, finding bugs, or leaving review comments. Follows the repository's PR template and writes a why-first body with reproducible testing steps and direct proof.
allowed-tools: Bash(*), Read, Glob, Grep
---
# Create or update a PR

Use this workflow only to create or update a PR. If the user only asks for code review, diff review,
bug finding, approval, or review comments, do not create or edit a PR.

1. Inspect the branch, diff, commits, linked issue, any existing PR body, and the repository's setup,
   run, and test instructions. Use the repo's PR template if present
   (`.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, or `docs/`); preserve its
   sections, but add distinct **Testing Steps** and **Proofs** sections when absent. Do not collapse
   reproducibility and collected evidence into one generic testing section.
2. Identify the changed behavior and its shortest representative user journey. When safe and
   feasible, run that journey plus the relevant automated checks before writing the PR. Record only
   evidence actually observed; never turn an assumption into a passing result.
3. Start with `Fixes #XXX` (or `Relates to #XXX`) when an issue is known from context or the branch
   name. Then write **Why** → **What** → **Testing Steps** → **Proofs**.
   - **Why**: explain the motivation and problem carefully — this is the part reviewers most need.
   - **What**: summarize the changes so the reviewer knows how to approach the diff.
   - **Testing Steps**: give the shortest independent path for a reviewer to exercise the actual
     change from a clean checkout. Include prerequisites or setup, exact copy-pasteable commands,
     prompts, or actions, and the expected observable result at each important point. Resolve exact
     syntax from repository docs or command help; do not write vague steps such as "create a task"
     when a concrete command exists. Prefer one primary happy path plus a cheap, important edge
     case. Automated test commands are not a substitute for this section. If direct exercise is not
     meaningful or feasible, say why and provide the closest reproducible verification instead of
     omitting the section. Include cleanup when the flow leaves persistent test data behind.
   - **Proofs**: put the strongest, most direct evidence first and match it to the change: compact
     before/after CLI or API output for behavioral changes; screenshots for UI; the same inputs plus
     pre/post scores and representative outputs for prompt changes; comparable benchmark results
     for performance; or an appropriate rendered/diff check for non-runtime work. When before/after
     is the clearest proof, run the same flow against the base and PR versions if safe; use an
     isolated worktree or existing artifacts rather than disturbing the user's working tree. Then
     list automated checks with their exact commands and concise outcomes. Do not paste redundant
     logs or enumerate irrelevant proof types; use `Not run (<reason>)` only for relevant evidence
     that could not be collected.
4. Keep the body optimized for reviewer time: make commands runnable, expected results scannable,
   and evidence sufficient to judge the acceptance criteria without reading the whole diff.
5. If the changes clearly affect the UI, also run `/aa:create-pr:screenshots` and place its
   before/after evidence under **Proofs**.
