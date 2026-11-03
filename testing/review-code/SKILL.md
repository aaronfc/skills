---
name: aa:review-code
description: Review changed code through a main-agent correctness review and independent security, consistency, and simplicity passes. Use only when the user explicitly invokes "/aa:review-code". Do not trigger automatically for implementation, handoff, commit, pull request, or general code-review tasks.
---

# Review Code

If the user did not explicitly invoke `/aa:review-code`, do not apply this skill; continue the user's task normally.

Review only; do not edit unless explicitly asked. Read the request, repository instructions, status, full diff, relevant untracked files, and enough surrounding code to understand the change.

## Main-agent correctness review

The main agent owns correctness and local verification. Establish the main purpose and required behavior from the request, linked issue or PR context, and relevant code and tests. Trace the changed behavior end to end to determine whether it fulfills that purpose. Look for missing requirements, incorrect results, regressions, and relevant failure or boundary cases. Treat tests and the implementation as evidence, not as the definition of intent; state material gaps or conflicts in that intent instead of inventing requirements.

Do this review yourself while subagents run their focused lanes; their findings do not replace your own understanding or checks. Use the strongest available reasoning model for the main review when selectable.

## Run independent passes

Spawn one subagent per lane. Run them concurrently when possible. Do not finish until every lane completes. Give each the raw scope and repository access, not other reviewers' conclusions. Ask for findings only, with exact evidence and the smallest safe fix.

1. **Changed-line security** — Find concrete vulnerabilities in the changed code: broken trust or authorization, injection, unsafe parsing or file access, secret exposure, and similar implementation flaws.
2. **System security** — Identify new inputs, capabilities, or reachable paths introduced by the change. Trace them through validation, authorization, storage, rendering, logging, jobs, and integrations; include existing weaknesses only when this change exposes or worsens them.
3. **Consistency** — Compare neighboring code and equivalent features. Check domain language, API shape, error and lifecycle semantics, tests, and local idioms; ignore formatter or linter trivia.
4. **Simplicity** — Challenge abstractions, branches, fallbacks, options, comments, and defensive code not justified by requirements or reachable behavior. Prefer self-explanatory code and brief comments explaining only irreducible why. Optimize for future maintainers' time without changing behavior.

When selectable, use the strongest available reasoning model for both security lanes, the least expensive capable model for consistency, and a strong general model for simplicity. Otherwise use the default.

## Verify and report

The main agent must use the project's existing local dev environment when available. Run relevant tests and directly exercise the changed behavior against the intended outcome, including meaningful failure and boundary cases. Passing existing tests alone is not enough: check requirements they do not cover. Follow repository setup instructions and keep checks proportional to the change. If some checks are blocked, run those still available and report the exact blocker and unverified behavior. Stop any services you start.

The main agent must independently verify every candidate from its own review and the subagent lanes against the code and intended behavior. Reproduce reported failures locally when possible; otherwise trace the concrete failure path and state any material verification limit. Keep only issues connected to the change by a demonstrable failure or security path; discard speculation, preferences, broad redesigns, and pre-existing problems the change does not expose. Deduplicate overlapping findings and prefer the narrowest proven correction.

Take into account existing comments from other reviewers (human or ai assistants). Separate already reported things from new findings from our own.

Report findings ordered by severity, followed by a brief verification summary with checks run, results, and material gaps. For each finding, give a P0–P3 priority, exact file and line, concise failure path, and smallest safe fix. If none survive verification, say `No findings.` Use Simplified Technical English (ASD-STE100) in your report.
