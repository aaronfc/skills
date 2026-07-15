---
name: aa:sharpen-skill
description: Use to simplify a skill to its essential ideas — "sharpen this skill", "make this SKILL.md shorter/simpler", or "/aa:sharpen-skill [path]". Iteratively reduces a SKILL.md to the bare minimum, guarded by an unvibe eval, extracting deterministic parts into scripts.
allowed-tools: Bash, Read, Edit, Write
---
# Sharpen a skill

Target dir = the path argument, else the current directory. Run this skill's `scripts/sharpen.sh` for every mechanical step.

1. **Start**: `sharpen.sh start <dir>` — backs up `SKILL.md` → `SKILL.md.orig`, resolves an installed unvibe, and reports eval state.
2. **Missing unvibe**: recommend the eval safety net and get explicit human approval before either installing it with `uv tool install git+https://github.com/aaronfc/unvibe.git` or using it without a global install via `UNVIBE_BIN='uvx --from git+https://github.com/aaronfc/unvibe.git unvibe' sharpen.sh …`. Never install or invoke `uvx` without that approval. If declined, offer judgment-only reduction (no safety net) or stop.
3. **Eval**: a pre-existing `EVALUATION.yaml` is a **frozen contract** — never weaken it. Otherwise `sharpen.sh create <dir>`, then prune the scaffold to 2–4 rubric-heavy scenarios capturing only the skill's core behaviors.
4. **Reduce in batches**: cut prose, merge steps, drop hedging — keeping every core idea. Conservatively move genuinely deterministic, exact-command sequences into `<dir>/scripts/` and reference them. Then `sharpen.sh verify <dir>` (run it in the background).
5. **On red**: fix or revert that batch. A flexible (generated) eval may shed brittle assertions, but surface any rubric you weaken or remove.
6. **Repeat** until the next cut would break the eval or drop a core idea. Aim ~10 lines, ~25 ceiling — justify going over.
7. **Finish**: keep the final `EVALUATION.yaml`. Run `sharpen.sh diff <dir>` and summarize what was cut, scripts extracted, and any rubric changes. Leave `SKILL.md.orig` for the user to delete.
