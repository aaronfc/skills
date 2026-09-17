---
name: aa:create-pr:screenshots
description: Add visual proof to a pull request for UI changes. Use only while creating or updating a PR that needs screenshots, when aa:create-pr delegates UI evidence work, or when the user invokes "/aa:create-pr:screenshots". Do not use for code review, reviewing a pull request or diff, or general UI testing. Captures before/after screenshots with Playwright and links them into the PR body.
allowed-tools: Bash(gh *), Bash(git *), Bash(mv *), Bash(cp *), Bash(ls *), Bash(curl *), Bash(file *), Bash(*publish-pr-media.sh *), Read, SendUserFile, mcp__playwright__browser_navigate, mcp__playwright__browser_navigate_back, mcp__playwright__browser_resize, mcp__playwright__browser_snapshot, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_fill_form, mcp__playwright__browser_press_key, mcp__playwright__browser_hover, mcp__playwright__browser_select_option, mcp__playwright__browser_wait_for, mcp__playwright__browser_console_messages, mcp__playwright__browser_network_requests, mcp__playwright__browser_evaluate, mcp__playwright__browser_storage_state, mcp__playwright__browser_set_storage_state, mcp__playwright__browser_start_video, mcp__playwright__browser_stop_video
---
# PR screenshots

Capture with the **Playwright MCP** (`mcp__playwright__*`) — an isolated, headless browser that
never touches your real Chrome windows or sessions. Its `browser_take_screenshot` writes a real
PNG straight to disk, so there is **no download/GIF transport hack**: pass a `filename`, read the
absolute path the tool returns, done.

## Capture → local file

Per shot:
1. `browser_navigate` to the page. The isolated browser starts **logged-out**, so if the screen
   needs auth, sign in first (see below).
2. Drive it to the exact state (`browser_click` / `browser_type` / `browser_fill_form`, using
   `browser_snapshot` to get element refs; `browser_wait_for` to settle).
3. `browser_resize` to the target viewport (exact — Playwright honours the size).
4. `browser_take_screenshot` with an **absolute** `filename` in a working dir outside the repo
   (e.g. `filename:"/tmp/<shots>/<screen>-<viewport>-<state>.png"`). It writes the PNG there and
   **returns the path** — read it for the next steps. **Never commit binaries to the branch.**
   - Watch the save path: a bare *relative* `filename` (`"shot.png"`) resolves against the MCP
     server's cwd — usually the repo you launched in — so it can drop a stray PNG in the working
     tree. Omitting `filename` lands it in the MCP output dir (with an auto name); an **absolute**
     path is the reliable way to control location.

That's the whole capture loop. No overlays to disable, no frame timing, no `~/Downloads` hunt.

### Auth (isolated browser starts logged-out)

Reach authenticated states one of two ways:
- **Log in programmatically** with creds from the repo's dev docs / `CLAUDE.local.md` / env:
  `browser_navigate` to the login page → `browser_fill_form` → submit. (For this repo's Woo AI dev
  site: `https://aaronfc-wooai.jurassic.tube/wp-login.php`, `admin` / `aarontesting`.)
- **Reuse a saved session**: once logged in, `browser_storage_state` to save cookies/localStorage,
  then `browser_set_storage_state` at the start of later runs to skip the login.

For an **animated/behavioural** change (e.g. an animation-timing tweak), don't split into two
stills: `browser_start_video`, perform the real interaction, `browser_stop_video` (saves a video
to the output dir). Attach the video to the PR, or convert it to a GIF (`ffmpeg`) and host it on
the gist like the stills below.

### Before/after without rebuilding the state twice

Driving the app to the same state twice (once per branch) is the slow, flaky part — especially for
AI-agent flows whose tool availability is non-deterministic (a request that produces a card one
minute returns "I don't have that tool" the next). Avoid re-driving:

- **Reuse persisted client state across a bundle swap.** Build the app's assets on the **after**
  commit, drive the flow once, capture. Then build the **before** commit's assets into the *same*
  served location, hard-reload, and the persisted UI (chat history, cached view) re-renders through
  the *old* code — capture the before. Same operation, deterministic diff, one drive-through. Works
  whenever the branches differ only in front-end assets (no schema/state change) and the app
  persists the interaction.
- **Recover a lost conversation via the app's own history**, not by re-prompting. If an in-app chat
  resets to empty, open its history / past-chats panel and reopen the prior thread — the rendered
  result cards come back intact. Re-prompting risks a different (or tool-less) response.
- **Build assets reliably from the target dir.** `cd <dir> && <build>` can silently run in the
  wrong working directory, leaving the served bundle stale while the build "succeeds". Use the
  tool's explicit dir flag (e.g. `pnpm --dir <path> …`) and **verify the emitted bundle changed** —
  grep it for a token from your diff and check the asset version/hash flipped — before reloading. A
  matching `?ver=` hash on the page's `<script>` confirms the new code is actually served.
- **Restore the served state when done** — rebuild the after/PR bundle into the served location so
  the env isn't left on the before build.

## Viewports & naming

- Target **desktop 1354×896** and **mobile 390×844** via `browser_resize` → **4 shots per screen**
  (before/after × desktop/mobile). Playwright sets the viewport exactly, and can emulate any
  width — including narrow mobile — so keep before and after identical for a fair comparison.
- Some layouts are **width-dependent** (a docked sidebar becomes a floating panel when narrow). If
  the user wants a specific one (e.g. "test the docked sidebar"), that need **overrides the fixed
  viewport** — capture at the width that produces it and note the deviation.
- Name files `<screen>-<viewport>-<state>.png` (e.g. `login-mobile-after.png`).

## Host & link

The shots are real local files, so hosting is the only remaining step for PR embedding.

1. **Never commit binaries** to `main` or the branch. Publish them with
   `scripts/publish-pr-media.sh --description "<PR media description>" <media>...`. The script
   creates a per-PR **secret gist** from a text placeholder, pushes the binaries through git,
   verifies one upload, and prints revision-pinned raw URLs that survive PR force-pushes. A secret
   gist is *unlisted, not private*: its media is public by URL, so do not publish sensitive screens.
2. Link the revision-pinned **raw** URLs printed by the script. They render in both public and
   private-repository PRs because GitHub's image proxy can fetch them.
3. In the PR body, show side-by-side `Before | After` markdown tables, one pair per viewport,
   grouped per screen. Edit non-destructively: fetch the current body
   (`gh pr view <n> --json body --jq .body`), insert the screenshots section (e.g. before the
   trailing generated-by footer), and write it back with `gh pr edit <n> --body-file <file>` —
   don't clobber the existing description.

## Also useful to send the shots to the user

Independent of the PR, the captured PNGs are real local files, so `SendUserFile` can surface them
inline (e.g. for a quick before/after look, or as a fallback if the user prefers to drag them into
the PR themselves).
