---
name: aa:review-code
description: Pre-review generated or changed code before handoff, commit, or pull request through independent security, consistency, and simplicity passes. Use when Codex should inspect its own implementation, run a final code review, check a diff for evidence-backed issues before declaring work complete, or invoke "/aa:review-code".
---

# Review Code

Review only; do not edit unless asked. Read the request, repository instructions, status, full diff, relevant untracked files, and enough surrounding code to understand the change.

## Run independent passes

Spawn one subagent per lane. Run them concurrently when capacity permits; if slots are limited, schedule waves and do not finish until every lane completes. Give each the raw scope and repository access, not other reviewers' conclusions. Ask for findings only, with exact evidence and the smallest safe fix.

1. **Changed-line security** — Find concrete vulnerabilities in the changed code: broken trust or authorization, injection, unsafe parsing or file access, secret exposure, and similar implementation flaws.
2. **System security** — Identify new inputs, capabilities, or reachable paths introduced by the change. Trace them through validation, authorization, storage, rendering, logging, jobs, and integrations; include existing weaknesses only when this change exposes or worsens them.
3. **Consistency** — Compare neighboring code and equivalent features. Check domain language, API shape, error and lifecycle semantics, tests, and local idioms; ignore formatter or linter trivia.
4. **Simplicity** — Challenge abstractions, branches, fallbacks, options, comments, and defensive code not justified by requirements or reachable behavior. Prefer self-explanatory code and brief comments explaining only irreducible why. Optimize for maintainers' time without changing behavior.

When selectable, use the strongest available reasoning model for both security lanes, the least expensive capable model for consistency, and a strong general model for simplicity. Otherwise use the default. Add future concerns as separate lanes.

## Verify and report

Independently verify every candidate against the code and intended behavior. Keep only issues connected to the change by a demonstrable failure or security path; discard speculation, preferences, broad redesigns, and pre-existing problems the change does not expose. Deduplicate overlapping findings and prefer the narrowest proven correction.

Report findings only, ordered by severity. For each, give a P0–P3 priority, exact file and line, concise failure path, and smallest safe fix. If none survive verification, say `No findings.` Mention a validation gap only when it materially limits confidence.
