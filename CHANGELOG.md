# Changelog

Updates are listed by date, newest first, without version numbers.

## 2026-09-17

- Promoted `afk/`, `pr-authoring/create/`, `pr-authoring/screenshots/`, and `sharpen-skill/` from `testing/` to the repository root, preserving their contents and updating plugin paths.
- Deprecated and removed `work-mode/` and its `work-init`, `work-prd`, and `work-done` skills from the repository and plugin. They remain available in git history.
- Removed the vendored Matt Pocock skills under `testing/mattpocock/` and their plugin registrations.
- Updated the README to reflect the promoted skills and retired workflow.

## 2026-07-30

- Added `aa:babysit-pr` for monitoring pull requests and triaging feedback.

## 2026-07-25

- Standardized skill evaluation filenames as `EVALUATIONS.yaml`.

## 2026-07-22

- Extended `aa:afk` to handle research issues alongside implementation work.

## 2026-07-17

- Added `aa:review-code` for dedicated code reviews.

## 2026-07-15

- Reorganized PR skills under `testing/pr-authoring/`, renaming them to `aa:create-pr` and `aa:create-pr:screenshots`.
- Added `aa:sharpen-skill` for simplifying skills with evaluation-backed checks.

## 2026-07-09

- Switched PR screenshot capture to Playwright.

## 2026-06-10

- Added Matt Pocock's `teach` skill to the experimental collection.

## 2026-05-26

- Added `aa:afk` for autonomous issue work.

## 2026-05-25

- Added PR authoring and screenshot skills, initially named `aa:review` and `aa:review:screenshot`, under `testing/review/`.
- Introduced skill evaluations using unvibe.

## 2026-05-14

- Initial repository release with the `work-mode/` PRD-driven workflow and Claude Code plugin registration.
- Added `testing/` as an experimental area, including a vendored collection of Matt Pocock's skills.
