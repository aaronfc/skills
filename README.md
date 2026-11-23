![aaronfc's skills logo](https://github.com/user-attachments/assets/1442050f-72fa-412d-90f3-17faf866f599)


# skills

My Claude Code workflow as it evolves, published so I can point at it.

Right now:

- **[`afk/`](afk/)** — autonomous issue implementation or research.
- **[`pr-authoring/create/`](pr-authoring/create/)** — create or update draft pull requests.
- **[`pr-authoring/screenshots/`](pr-authoring/screenshots/)** — add visual proof to pull requests.
- **[`sharpen-skill/`](sharpen-skill/)** — simplify skills with evaluation-backed checks.
- **`testing/`** — skills I am testing or experimenting with, including Matt Pocock's [`handoff`](testing/mattpocock/handoff/) for passing context to another agent.
  - [`/aa:publish-review`](testing/publish-review/SKILL.md) — discuss existing PR findings one at a time and approve each inline comment before posting. Findings without a suitable diff line can go into one top-level comment for final approval.

Install via [skills.sh](https://www.skills.sh):

```
npx skills@latest add aaronfc/skills
```

### Local symlink install

From a local checkout, run one command so edits take effect immediately through symlinks without `npx skills` or a background process:

```bash
./scripts/install-skills.py
```

By default, this discovers every tracked `SKILL.md` (including nested skills under `testing/`) and symlinks each skill into:

- Claude Code (`~/.claude/skills`)
- Codex (`~/.codex/skills`)
- Shared Agent Skills (`~/.agents/skills`)
- Antigravity (`~/.gemini/config/skills`)
- Gemini CLI (`~/.gemini/skills`)

Each installed folder name comes from the skill's `SKILL.md` frontmatter `name` (for example, `aa:babysit-pr` → `aa-babysit-pr`), independent of its directory path. Rerunning the command installs new skills, updates checkout-owned links after a skill moves out of `testing/`, and removes stale checkout-owned links when a skill is removed or renamed. Unrelated skills, existing copies, and conflicting symlinks are preserved untouched and reported (exiting non-zero) so you can decide whether to migrate them.

Use `--dry-run` to preview changes and conflicts, `--client claude,codex` to sync a subset of clients, or `--target <path>` to install into custom directories. Run the installer tests against temporary directories with:

```bash
python3 -m unittest discover -s tests
```

## Evaluations

Some skills ship with an `EVALUATIONS.yaml`. I'm using these to dogfood [unvibe](https://github.com/aaronfc/unvibe), a framework I built for writing evaluations for skills.

## Changelog

- **2026-11-20** — Added `aa:publish-review` with [unvibe evaluations](testing/publish-review/EVALUATIONS.yaml).
- **2026-09-17** — Promoted `afk`, both `pr-authoring` skills, and `sharpen-skill` to the root. Deprecated and removed `work-mode`; removed the vendored Matt Pocock skills except `handoff`, which was restored.
- **2026-07-30** — Added `aa:babysit-pr` for PR monitoring.
- **2026-07-25** — Standardized evaluation filenames as `EVALUATIONS.yaml`.
- **2026-07-22** — Extended `aa:afk` to research issues.
- **2026-07-17** — Added `aa:review-code`.
- **2026-07-15** — Reorganized PR skills under `pr-authoring` as `aa:create-pr` and `aa:create-pr:screenshots`; added `aa:sharpen-skill`.
- **2026-07-09** — Switched PR screenshot capture to Playwright.
- **2026-06-10** — Added Matt Pocock's `teach` skill.
- **2026-05-26** — Added `aa:afk` for autonomous issue work.
- **2026-05-25** — Added PR authoring and screenshot skills (originally `aa:review` and `aa:review:screenshot`), plus unvibe evaluations.
- **2026-05-14** — Initial release: `work-mode` PRD workflow, Claude Code plugin, and `testing/` with vendored Matt Pocock skills.
