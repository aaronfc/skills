![aaronfc's skills logo](https://github.com/user-attachments/assets/1442050f-72fa-412d-90f3-17faf866f599)


# skills

My Claude Code workflow as it evolves, published so I can point at it.

Right now:

- **[`afk/`](afk/)** — autonomous issue implementation or research.
- **[`pr-authoring/create/`](pr-authoring/create/)** — create or update draft pull requests.
- **[`pr-authoring/screenshots/`](pr-authoring/screenshots/)** — add visual proof to pull requests.
- **[`sharpen-skill/`](sharpen-skill/)** — simplify skills with evaluation-backed checks.
- **`testing/`** — skills I am testing or experimenting with.

Install via [skills.sh](https://www.skills.sh):

```
npx skills@latest add aaronfc/skills
```

## Evaluations

Some skills ship with an `EVALUATIONS.yaml`. I'm using these to dogfood [unvibe](https://github.com/aaronfc/unvibe), a framework I built for writing evaluations for skills.

## Changelog

- **2026-09-17** — Promoted `afk`, both `pr-authoring` skills, and `sharpen-skill` to the root. Deprecated and removed `work-mode`; removed the vendored Matt Pocock skills.
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
