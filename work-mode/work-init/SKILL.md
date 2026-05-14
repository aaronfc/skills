---
name: work-init
description: This skill should be used when the user asks to "start work mode", "init work", "begin structured work", "start a new task", "work on something", or wants to enter a structured PRD-based workflow. Triggers on phrases like "let's work on", "start working", "new feature", "new task".
allowed-tools: Bash(git *), Bash(mkdir *), Bash(ls *), Bash(find *), AskUserQuestion, Read(~/_work/lessons.md), Edit(_work/**), Write(_work/**)
---
# Structured Project Workflow

I want you to work in structured mode.

## Work Directory

All work files (PRDs, notes, phase plans) live in a **project-local `_work/` directory** at the repo root. It should be gitignored — see **Git Behavior** below.

## Current Status

- Work directory: !`mkdir -p _work/_archive && echo "_work"`
- Existing most recent PRDs:
!`find _work -maxdepth 1 -name "*.prd.md" 2>/dev/null`
- Current git branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "(not a git repo)"`
- Uncommitted changes: !`git status --short 2>/dev/null`
- Lessons learned: !`cat ~/_work/lessons.md 2>/dev/null || echo "(no lessons file yet)"`

## What to work on?

Choose the appropriate path based on how the skill was invoked:

### Path A: User provided context with the command
If the user included a task description, ticket reference, conversation link, or any context alongside the `/work-init` command (e.g., `/work-init let's work on ticket LIN-1234 and check slack thread XYZ`), **skip the task selector entirely**. Use the provided context as the starting point and proceed directly to the Investigation & Clarification phase.

### Path B: Invoked mid-conversation (retroactive initialization)
If this is NOT the beginning of the conversation — there are prior messages with substantial context about work already being discussed or done — the user wants to **retroactively enter structured mode**. Do NOT ask what to work on. Instead:
1. Synthesize what has been discussed and decided so far from the conversation history
2. Proceed directly to PRD Creation, capturing the current state of the work
3. Create the notes file with any decisions already made during the conversation
4. Continue in structured mode going forward

### Path C: Fresh start with no context
Use AskUserQuestion tool to present a selector with:
   - Each recent PRD as an option (use filename as label, "Continue working on this PRD" as description)
   - The user can also select "Other" or directly provide a new task description

Example AskUserQuestion usage:
```
questions: [{
  question: "What would you like to work on?",
  header: "Task",
  options: [
    { label: "feature-name.prd.md", description: "Continue working on this PRD" },
    { label: "another-prd.prd.md", description: "Continue working on this PRD" },
    // ... more PRDs from ls output
  ],
  multiSelect: false
}]
```

After the user selects:
- If they selected an existing PRD:
  1. Read the PRD and its notes file
  2. **Branch checkout**: If the PRD has `Branch` and `Affected Repos`, handle checkout for each affected repo (see **Branch Management** section)
  3. Ask how to proceed
- If they selected "Other": Ask for task description, references, and context

## My Process

### Investigation & Clarification
You will:
- **Read durable project context first.** If the affected repo has `README.md`, `docs/`, or `CLAUDE.md`, read those before exploring code. They describe the system as it currently is; the new PRD should reference them, not duplicate them.
- Investigate the codebase and gather relevant information
- Ask clarifying questions about unclear aspects
- **Challenge my assumptions** - If something seems wrong or unclear, you  must push back
- Explore the problem space thoroughly before jumping to solutions

**Important**: You will question and correct me when needed. I am ok with being wrong and value learning from my own errors.

### PRD Creation
After our discussion rounds, you will:
- Ask for confirmation on your own understanding
- Create a PRD document at `_work/YYYY-MM-DD-HH-MM-[feature-name].prd.md` (timestamp prefix)
- Include problem definition, solution approach, and implementation phases if task or feature is long enough
- Always include a `**Branch**` field in the PRD header — infer the branch name from the feature slug with an appropriate prefix (see **Branch Management**)
- Include `**Affected Repos**: (none yet)` — populated automatically during implementation
- **Never include time estimations** - No estimates of how long tasks will take
- Create `_work/YYYY-MM-DD-HH-MM-[feature-name].notes.md` with this template:
  ```
  # [Feature Name] - Decision Log

  This file tracks important decisions, learnings, and changes made during the implementation of this feature.

  ## Format
  Each entry should include:
  - Date and time (YYYY-MM-DD HH:MM)
  - Decision or change description
  - Rationale
  - Related files/phases affected
  ```
- **Ask me to review the PRD** before proceeding with implementation
- During review: You will apply any changes I request immediately to the PRD (we're in definition phase - don't log these in notes.md)
- You will make counter-intuitive aspects explicit in the PRD
- Keep it as a living document (updated as we learn)

### Implementation Planning
When we are ready to proceed, I will tell you to either:
- Work on the entire PRD (if small)
- Focus work on a specific phase
- Ask you to elaborate on a phase with more defailed implementaiton steps

For complex PRDs with multiple phases, you will create `_work/YYYY-MM-DD-HH-MM-[feature-name].phaseX.md` with step-by-step implementation details, then **ask you me to review it** before jumping to implementation.

**Phase vs. new PRD.** Before creating a `phaseX.md`, ask: was this step *always part of the original task* (legitimate phase), or did *using/learning from the work change what's needed* (new PRD)? If the latter — invoke `/work-prd` for the new track instead. The original PRD should still be able to reach a "done." Phases that emerge from project evolution turn the PRD into a never-ending journal.

### Implementation Practices

These apply throughout implementation — not just at the end.

**Verify as you go**: After completing each meaningful unit of work (a function, a component, a phase), verify it works before moving on. Run tests, check for lint/type errors, or do a quick manual check. Don't accumulate unverified changes — catch problems early when the context is fresh.

**Demand elegance**: For non-trivial changes, pause before presenting your work and ask yourself: "Is there a more elegant way?" If a solution feels hacky or overly complex, step back and reconsider. Skip this for simple, obvious fixes — don't over-engineer.

**Fix problems autonomously**: When you encounter errors, failing tests, or unexpected behavior during implementation — just fix them. Investigate logs, read stack traces, find root causes. Don't ask for hand-holding on problems you can solve yourself. Zero context switching required from the user.

### Progress & Decision Tracking
Throughout the work:
- **All reviews** (PRD or phaseX files) may result in updates
- During PRD definition phase: you will apply your changes immediately to the PRD
- During phaseX definition or implementation: Updates may affect the PRD or phaseX files
- **Important**: You must log any change during PRD implementation or phaseX review/implementation in the corresponding `.notes.md` with timestamp (YYYY-MM-DD HH:MM)
- You must track decisions, rationale, and affected files in notes

## Branch Management

### Branch Naming
When creating a PRD, always generate a branch name from the feature slug (lowercase, hyphenated) with a prefix:
- `add/` — new features or capabilities
- `fix/` — bug fixes
- `update/` — improvements, refactoring, changes to existing features

Example: PRD slug `image-upload-unified-experience` for a new feature → `add/image-upload-unified-experience`

### On PRD Selection (resuming work)
When the user selects an existing PRD that has `Branch` and `Affected Repos`:
1. For each affected repo, check current branch and working tree using `git -C <repo-path>`
2. If a repo has **uncommitted changes** on a different branch: ask the user what to do (stash, commit first, or abort) — **never discard changes**
3. If a repo is on a different branch with a **clean working tree**: checkout the PRD branch
4. Report branch status of all affected repos before proceeding

If the PRD has a branch but `Affected Repos` is empty or `(none yet)`, skip branch operations — no repos have been touched yet.

### During Implementation (lazy branch creation)
Before making code changes in any repository (including submodules and related repos referenced in `CLAUDE.local.md`):
1. Check if the current branch in that repo matches the PRD's `Branch`
2. If NOT on the PRD branch:
   - Check for uncommitted changes — if dirty, ask the user what to do
   - If the branch exists locally: `git -C <path> checkout <branch>`
   - If the branch doesn't exist: `git -C <path> checkout -b <branch>`
   - Add the repo's absolute path to the PRD's `**Affected Repos**` list
3. Only create/checkout branches when actual code changes are about to happen — never preemptively branch repos that may not need changes

### Affected Repos Tracking
The PRD's `**Affected Repos**` field tracks which repositories have the PRD branch checked out. Initially `(none yet)`. Update it as a bullet list of absolute paths whenever you create or checkout the branch in a new repository.

## File Structure
- `_work/YYYY-MM-DD-HH-MM-[feature-name].prd.md` - PRD for each feature/task (timestamp prefix)
- `_work/YYYY-MM-DD-HH-MM-[feature-name].phaseX.md` - Detailed phase implementation plans
- `_work/YYYY-MM-DD-HH-MM-[feature-name].notes.md` - **One notes file per PRD/feature**
- `_work/_archive/` - Completed PRDs and their notes (moved via `work-done` skill)

## Git Behavior for `_work/`

The `_work/` directory is intended to be **gitignored**. Recommended: add `_work/` to your global gitignore (`~/.gitignore`) so it's excluded from every repo automatically.

When committing:
- **If `_work/` files do NOT appear in `git status`**: they're intentionally excluded — don't try to add them.
- **If `_work/` files DO appear in `git status`**: the project has an explicit unignore for them — follow normal commit practices.

**Rule**: only commit what `git status` shows. Never attempt to add `_work/` files git isn't tracking.

## Lessons

A global lessons file at `~/_work/lessons.md` captures patterns learned from user corrections across all projects.

**Reading**: The file is loaded automatically in the Current Status section at session start. Review it and apply any relevant lessons to your work.

**Writing**: After **any correction** from the user during implementation, append a lesson to `~/_work/lessons.md` with this format:

```
### YYYY-MM-DD — <short description>
<What went wrong and the correct approach. Be specific enough to prevent the same mistake.>
```

Only capture patterns that generalize — things that would apply to future work, not one-off details specific to the current feature. If the file doesn't exist yet, create it with a `# Lessons Learned` header.

## Key Principles
- **Always create a PRD** when in this mode, even for the smallest tasks
- **Challenge assumptions** - Question anything that seems off
- **Document decisions** - Track important choices in notes.md. Keeping track of the why is paramount. When in doubt, ask me and I will help clarifying the why.
- **Keep PRD current** - Update as source of truth when needed
- **One feature per conversation** - Each conversation focuses on a single feature/task PRD
- **No time estimations** - Never include time estimates in PRDs or phase documents
- **Timestamp prefix** - All PRD files use `YYYY-MM-DD-HH-MM-` prefix for chronological ordering

## Related Skills
- **work-prd** - Quickly capture a new PRD from current context without switching focus
- **work-done** - Archive the current PRD when complete (moves to `_work/_archive/`)

## Context Continuity
When resuming work:
- Reference existing PRD and related documents
- Check notes.md for previous decisions and stopping points
- Handle branch checkout for affected repos (see **Branch Management**)
- Update phase files as implementation progresses

---

Let's start working. Greet me with some sfw dad joke.
