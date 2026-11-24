![aaronfc's skills logo](https://github.com/user-attachments/assets/1442050f-72fa-412d-90f3-17faf866f599)


# skills

My Claude Code workflow as it evolves, published so I can point at it.

Right now:

- **[`afk/`](afk/)** — autonomous issue implementation or research.
- **[`pr-authoring/create/`](pr-authoring/create/)** — create or update draft pull requests.
- **[`pr-authoring/screenshots/`](pr-authoring/screenshots/)** — add visual proof to pull requests.
- **[`sharpen-skill/`](sharpen-skill/)** — simplify skills with evaluation-backed checks.
- **`testing/`** — skills I am testing or experimenting with, including Matt Pocock's [`handoff`](testing/mattpocock/handoff/) for passing context to another agent.
  - [`/aa:review-pr`](testing/review-pr/SKILL.md) — review changes and rank findings by priority.
  - [`/aa:publish-review`](testing/publish-review/SKILL.md) — discuss existing review findings and approve each comment before posting.
  - [`/aa:my-words`](testing/my-words/SKILL.md) — draft findings and replies to PR feedback in your voice. Approve each message before posting.
  - [`/aa:gandalf`](testing/gandalf/SKILL.md) — talk through a reviewed PR before deciding whether to approve.

Install via [skills.sh](https://www.skills.sh):

```
npx skills@latest add aaronfc/skills
```

### Local symlink install

From a local checkout, run one command so edits take effect immediately through symlinks without `npx skills` or a background process:

```bash
./scripts/install-skills.py
```

By default, this discovers every tracked `SKILL.md` (including nested skills under `testing/`) and symlinks each skill into three non-overlapping global skill directories:

- Shared Agent Skills (`~/.agents/skills`) — used by Codex and other Agent Skills tools
- Claude Code (`~/.claude/skills`)
- Antigravity (`~/.gemini/config/skills`) — shared by Antigravity App, CLI (`agy`), and IDE

Each installed folder name comes from the skill's `SKILL.md` frontmatter `name` (for example, `aa:babysit-pr` → `aa-babysit-pr`), independent of its directory path. Rerunning the command installs new skills, updates checkout-owned links after a skill moves out of `testing/`, and removes stale checkout-owned links when a skill is removed or renamed. Unrelated skills, existing copies, and conflicting symlinks are preserved untouched and reported (exiting non-zero) so you can decide whether to migrate them.

Use `--dry-run` to preview changes and conflicts, `--client agents,claude` to sync a subset of clients, or `--target <path>` to install into custom directories. Run the installer tests against temporary directories with:

```bash
python3 -m unittest discover -s tests
```

## Evaluations

Some skills ship with an `EVALUATIONS.yaml`. I'm using these to dogfood [unvibe](https://github.com/aaronfc/unvibe), a framework I built for writing evaluations for skills.

## Changelog

- **2026-11-24** — Renamed `review-code` to `review-pr` and `walk-pr` to `gandalf`. Added `my-words` alongside `publish-review` to try drafting findings and review-thread replies with one skill.

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
