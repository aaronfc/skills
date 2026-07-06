---
name: aa:review:screenshot
description: Use when a PR touches the UI and needs visual proof, or the user says "/aa:review:screenshot". Captures before/after screenshots with the Chrome integration and links them into the PR body.
allowed-tools: Bash(gh *), Bash(git *), Bash(mv *), Bash(ls *), Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__resize_window, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__gif_creator, mcp__claude-in-chrome__find
---
# PR screenshots

## Capture → local file (the tricky part)

The Chrome integration screenshots live in a **sandbox**, not on your disk: `computer` screenshot `save_to_disk` and `upload_image` do **not** reach the local filesystem. The one path that lands a real file locally is a **browser download** via `gif_creator export {download:true}`, which writes to the user's real `~/Downloads`. So every shot is transported as a **GIF** — a single frame for static shots (256-colour, crisp enough for UI; verified), a real recording for animated ones.

Per shot:
1. `tabs_context_mcp` (createIfEmpty), `navigate` to the page in the user's **real logged-in browser** — that's why we use the integration and not a headless browser: it can reach authenticated app states.
2. Drive it to the exact state. Do each screen twice: **before** on the base branch, **after** on the PR branch — same URL, same data, same window size.
3. Record and export (overlays OFF, or the watermark/labels get burned in):
   - `gif_creator start_recording`
   - `computer` screenshot → `computer` wait 1s → `computer` screenshot  *(need ≥1 settled frame; a lone screenshot right after start yields "no frames")*
   - `gif_creator export` with `download:true`, `filename:"<screen>-<viewport>-<state>.gif"`, `options:{showClickIndicators:false, showDragPaths:false, showActionLabels:false, showProgressBar:false, showWatermark:false, quality:5}`
4. The file is now at `~/Downloads/<name>.gif`. `mv` it to a temp dir — **never into the repo**.

For an **animated/behavioural** change (e.g. an animation timing tweak): don't split into two stills — perform the real interaction (clicks/scrolls) between `start_recording` and `export` so the motion is captured.

## Viewports & naming

- Target **desktop 1354×896** and **mobile 390×844** via `resize_window` → **4 shots per screen** (before/after × desktop/mobile).
- The integration captures the *live* window, so `resize_window` is approximate — check the dimensions in the screenshot result and keep **before and after identical** (a fair comparison matters more than hitting the exact number). It **cannot** emulate device widths below ~500px, so for a real mobile view ask the user to switch Chrome into responsive/device mode (or narrow the window) before you capture.
- Name files `<screen>-<viewport>-<state>.gif` (e.g. `login-mobile-after.gif`).

## Host & link

1. **Never commit binaries** to `main` or the branch. Host on a per-PR **secret gist**: `gh gist create --secret <files…>`. This renders in the PR for **both public and private repos**, because the gist is publicly fetchable by GitHub's image proxy — which is also the caveat: a "secret" gist is *unlisted, not private*, so the screenshot is public-by-URL and lives outside the repo's access control. Fine for typical UI; reconsider for genuinely sensitive screens. (A committed-file `raw.githubusercontent.com` URL would be simpler but **won't render in private-repo PRs** — the proxy can't fetch private content — so gist it is.)
2. Link the **raw** URL — it's pinned to the gist revision SHA (`…/raw/<revisionsha>/<file>.gif`), so images keep working even after a PR force-push.
3. In the PR body (`gh pr edit --body`), show side-by-side `Before | After` markdown tables, one pair per viewport, grouped per screen.
