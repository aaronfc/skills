# Work mode

A tiny PRD-driven workflow for keeping a non-trivial piece of work coherent across many sessions. Artifacts live in a gitignored `_work/` directory at the repo root — close to the code they describe, but out of commits.

```
        ┌───────────────┐
        │   work-init   │   ← start a task: investigate, clarify, write a PRD
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │  implementing │── side-track? ──►  ┌───────────────┐
        └───────┬───────┘                    │   work-prd    │
                │                            │ capture a new │
                │                            │ PRD without   │
                │                            │ switching     │
                │                            └───────────────┘
                ▼
        ┌───────────────┐
        │   work-done   │   ← archive the PRD, promote durable lessons
        └───────────────┘                    into README.md / docs/
```

## What it does

- **`work-init`** — Enters structured mode. Investigates, asks clarifying questions, then writes a timestamped PRD + notes file under the project's `_work/` directory. Manages a feature branch across affected repos. Loads `~/_work/lessons.md` at session start so corrections stick across projects.
- **`work-prd`** — Mid-session capture. When the current work surfaces *another* PRD-worthy thread, drops a lightweight PRD into the same `_work/` without switching focus.
- **`work-done`** — Archives the active PRD into `_work/_archive/`, checks for unpushed commits, and runs a two-pass *promote-then-cross-check* over the affected repo's `README.md` / `docs/` so durable knowledge doesn't die with the PRD.

## Where work files live

PRDs, notes, and phase plans live in a **project-local `_work/`** directory at the repo root — gitignored, so they stay out of commits and PRs. Recommended setup: add `_work/` to your global gitignore so every repo excludes it automatically:

```
echo '_work/' >> ~/.gitignore
git config --global core.excludesfile ~/.gitignore
```

The skills create `_work/_archive/` on first invocation. No script install required.

The one global file is `~/_work/lessons.md` — a cross-project corrections log that `work-init` reads at session start. Created on first user-correction.

## Conventions the skills assume

- **PRD filename:** `YYYY-MM-DD-HH-MM-<slug>.prd.md` (chronological, sortable).
- **One notes file per PRD:** `<same-stem>.notes.md` — every implementation decision gets logged with a timestamp.
- **Phase files** for multi-phase PRDs: `<same-stem>.phaseX.md`.
- **Branch prefix:** `add/` for new features, `fix/` for bugs, `update/` for refactors / improvements.
- **No time estimates.** Ever.
- **Phase vs. new PRD:** if a step was always part of the original task → phase. If it *emerged from doing the work* → new PRD via `work-prd`. Keeps the parent PRD able to reach "done".

## Related

See `../context-engineering/` for the complementary loop that keeps the project's own context (CLAUDE.md, docs/, ADRs) sharp — `work-done`'s promotion pass is the natural feeder into it.
