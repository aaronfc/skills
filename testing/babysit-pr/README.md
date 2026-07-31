# aa:babysit-pr configuration

## Requirement for waits longer than five minutes

Codex limits empty background-terminal waits to five minutes by default. To let this skill block locally for one hour while the waiter runs, add this top-level setting to your user config:

```toml
background_terminal_max_timeout = 3600000
```

The user config is `$CODEX_HOME/config.toml`, or `~/.codex/config.toml` when `CODEX_HOME` is unset. Restart Codex and start a new session after changing it so the new limit is loaded.

The skill requests an empty one-hour `write_stdin` wait. Codex returns that call early when the waiter exits; otherwise the agent is invoked again only when the hour expires. Without this setting, the skill still works, but Codex clamps each wait to its five-minute default.

The waiter’s default `--interval 60` controls only how often its deterministic Python process checks GitHub. It does not require the agent or model to wake every 60 seconds.
