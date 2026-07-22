---
name: aa:babysit-pr
description: Wait read-only for pull-request approval, new human feedback, merge, closure, or access errors. Use when the user asks to babysit, watch, monitor, or wait on a GitHub pull request or invokes "/aa:babysit-pr".
---

# Babysit a pull request

1. Resolve the target and stopping conditions. Prefer a full PR URL; a number is valid only when the current repository is unambiguous. Supported conditions are `approved`, `new-comment`, and `merged`; default to `approved,new-comment` when the user does not specify one.
2. From this skill directory, start exactly one foreground waiter. For example:

   ```bash
   scripts/wait-for-pr.py "$PR_URL" --until approved,new-comment
   ```

   The script captures the baseline, ignores existing activity, polls through the authenticated `gh` CLI, and emits one JSON result. It is read-only. Bots are ignored unless the user explicitly wants `--include-bots`; keep the conservative 60-second interval unless they request another interval.
3. Let the process keep running. When the execution tool yields a session or cell ID, resume that same process with its wait mechanism in intervals of at most 60 seconds. Do not launch another waiter: restarting would establish a new baseline.
4. Report the exact event, actor, review state, short body/title, and direct URL from the result. Exit `0` is a requested event; `2` is an access/authentication error; `3` is an unrequested merge or closure; `130` is interruption.
5. Say what needs attention. Changes requested, inline feedback, or a concrete human request are actionable; approval and merge are informational. For a general comment, inspect its body and state whether it requests work. Closure or an error needs human attention. Do not take follow-up action unless the invocation explicitly authorized it.

For a new review round, start the waiter only after the revision is pushed so that the new process records a fresh baseline. To wait for merge while still waking on feedback, use `--until merged,new-comment`; closure always stops the waiter.

When the user explicitly requests tmux handoff, run one waiter in a named detached session, redirect its JSON result to a user-visible file, and report the session name and result path. Do not use tmux otherwise.
