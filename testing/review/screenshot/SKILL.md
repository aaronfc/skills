---
name: aa:review:screenshot
description: Use when a PR touches the UI and needs visual proof, or the user says "/aa:review:screenshot". Captures before/after screenshots and links them into the PR body.
allowed-tools: Bash(gh *), Bash(git *), Read
---
# PR screenshots

1. Capture **4 shots per screen**: before/after × desktop/mobile. Fixed viewports — desktop 1354×896, mobile 390×844.
2. Name them `<screen>-<viewport>-<state>.<ext>`; use a GIF instead for behavioural/animated changes.
3. **Never commit binaries** to `main` or the branch. Host on a per-PR **secret gist**; link raw URLs pinned to the commit SHA.
4. In the PR body, show side-by-side `Before | After` markdown tables, one pair per viewport.
