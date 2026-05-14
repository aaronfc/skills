---
name: work-prd
description: This skill should be used when the user wants to "capture a PRD", "save this as a PRD", "create a quick PRD", "note this for later", or identifies something during work that deserves its own PRD without switching focus. Triggers on phrases like "capture it", "save as prd", "new prd from this".
allowed-tools: Bash(mkdir *), Bash(date *), Write(_work/**), Read, Glob
---
# Quick PRD Capture

You've identified something during our current work that deserves its own PRD, but you don't want to switch focus right now.

**When to use this vs. adding a phase to an existing PRD:** if the new work *was always part of the original task* (always-known step), make it a phase. If it *emerged from learning/using the system* and the original PRD can reach its own "done" without it, capture it as a new PRD here. Phases that emerge from project evolution turn the parent PRD into a never-ending journal.

**I will create a lightweight PRD that captures:**
- The essence of the problem/opportunity
- Key context from our current conversation
- Reference to the originating PRD/project (if applicable)
- Enough detail to jump back in quickly later

## Current Project

- Work directory: !`mkdir -p _work/_archive && echo "_work"`

PRDs and notes live in the project-local `_work/` directory at the repo root (gitignored).

## My Process

1. **Analyze current context** - I'll review our recent conversation to understand:
   - What issue/opportunity was identified
   - What project/PRD we're currently working on (the origin)
   - Key technical details and complexities discussed
   - Any proposed solutions or approaches mentioned

2. **Create timestamped PRD** - I'll create `_work/YYYY-MM-DD-HH-MM-[descriptive-name].prd.md` with:
   ```markdown
   # [Descriptive Title]

   **Status**: Captured - Needs Discussion
   **Created**: YYYY-MM-DD
   **Origin**: [Link to originating PRD if applicable]
   **Branch**: prefix/descriptive-name (infer `add/` for features, `fix/` for bugs, `update/` for improvements)
   **Affected Repos**: (none yet)

   ---

   ## Context

   [Brief description of how this was identified and why it matters]

   ## Problem/Opportunity

   [Core issue or opportunity captured]

   ## Key Points from Discovery

   [Bullet points of important details, complexities, considerations]

   ## Potential Approaches

   [Any approaches discussed, even if incomplete]

   ## Questions to Resolve

   [Open questions that need answers]

   ## References

   - Origin PRD: `_work/[originating-prd].prd.md`
   - Related files/code mentioned
   - External links if any
   ```

3. **Create minimal notes file** - `_work/YYYY-MM-DD-HH-MM-[descriptive-name].notes.md`

4. **Confirm and continue** - Show you what was captured, then we continue with our current work

---

## Instructions

Please tell me:
1. **What to capture** - Brief description of the issue/opportunity (or say "from our discussion" and I'll infer)
2. **Suggested name** - A short descriptive name for the PRD (optional - I can suggest one)

Or just say **"capture it"** and I'll analyze our recent conversation to create the PRD automatically.
