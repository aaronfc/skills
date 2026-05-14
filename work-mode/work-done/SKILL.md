---
name: work-done
description: This skill should be used when the user wants to "archive a PRD", "mark work as done", "complete a task", "finish this PRD", or is done working on a feature. Triggers on phrases like "done", "archive this", "mark as complete", "finished".
allowed-tools: Bash(git *), Bash(mkdir *), Bash(mv *), Bash(ls *), Read, Glob, Edit(_work/**), Task
---
# Archive Completed PRD

You're marking a PRD as complete. I will move it and its related files to the archive.

## Current Project

- Work directory: !`mkdir -p _work/_archive && echo "_work"`

PRDs live in the project-local `_work/` directory at the repo root (gitignored).

## My Process

1. **Identify the PRD** - I'll list active PRDs:
   ```
   ls -t _work/*.prd.md 2>/dev/null
   ```

2. **Confirm which PRD to archive** - You tell me which one (or I'll assume the one we've been working on)

3. **Move related files** - I'll move to `_work/_archive/`:
   - The PRD file: `[name].prd.md`
   - The notes file: `[name].notes.md`
   - Any phase files: `[name].phase*.md`
   - Any continue files: `[name].continue.md`

4. **Update PRD status** - Before moving, I'll update the PRD status to "Completed" with completion date

5. **Confirm completion** - Show you what was archived

6. **Check for unpushed changes** - If the PRD has `Affected Repos`, check each repo for unpushed commits:
   - Run `git -C <path> log @{u}.. --oneline 2>/dev/null` for each affected repo
   - If there are unpushed commits, inform the user (do NOT push — just report)

7. **Unload durable knowledge into project docs** - Two-pass process before archiving:

   **Pass 1: Promote (active)**
   Read the PRD + notes.md. Identify durable items the project should remember after this PRD archives:
   - New architectural shape or pipeline changes
   - Non-obvious gotchas surfaced during work
   - Design decisions worth keeping (the "why")
   - New entry points or commands users will run

   For each item, propose a specific edit to the affected repo's `README.md` or `docs/*.md`. Apply after user confirmation. If `docs/` doesn't exist and there are 2+ durable items, propose creating it (e.g., `docs/architecture.md`, `docs/gotchas.md`, `docs/decisions.md`).

   **Pass 2: Cross-check (reactive)**
   Use Task tool with subagent_type='Explore' to scan `CLAUDE.md`, `CLAUDE.local.md`, `README.md`, `docs/*.md` for now-stale content the completed work made wrong (renamed entry points, removed features, replaced patterns). Update what's wrong; leave the rest.

   Skip this step entirely only if the PRD was a tiny isolated change that produced no durable lessons.

## Files to Archive

For a PRD named `2025-01-15-10-30-feature-name.prd.md`, I'll move:
- `_work/2025-01-15-10-30-feature-name.prd.md` → `_work/_archive/`
- `_work/2025-01-15-10-30-feature-name.notes.md` → `_work/_archive/`
- `_work/2025-01-15-10-30-feature-name.phase*.md` → `_work/_archive/` (if any)
- `_work/2025-01-15-10-30-feature-name.continue.md` → `_work/_archive/` (if any)

---

## Instructions

Tell me which PRD to archive:
- **By name**: "archive [prd-name]"
- **Current**: "archive current" (I'll identify from our conversation)
- **List first**: "show active" (I'll list active PRDs, then you choose)

Or just say **"done"** and I'll archive the PRD we've been working on.
