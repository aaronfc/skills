---
name: update-vocabulary
description: Refresh a project's shared vocabulary, terminology, glossary, and domain-language docs after a work session. Use when the user asks to update vocabulary, terminology, glossary, CONTEXT.md, domain language, naming conventions, or to capture newly clarified distinctions so future humans and coding agents communicate more efficiently.
---

# Update Vocabulary

Keep the project's language sharp after a session. The goal is not to document
everything discussed; it is to capture terms and distinctions that will prevent
future confusion, improve issue/PR writing, or make agent work more reliable.

## Workflow

### 1. Locate The Vocabulary Surface

Read the repo's agent/domain instructions before editing:

- `AGENTS.md` or `CLAUDE.md`
- `docs/agents/domain.md`, if present
- `CONTEXT.md` or `CONTEXT-MAP.md`
- relevant ADRs or decision logs only when the terminology encodes a durable
  architectural choice

If the repo has not been configured with `setup-matt-pocock-skills`, infer the
best local convention from existing docs. Do not run a full setup unless the
user asks for it.

### 2. Extract Candidate Vocabulary

Review the recent conversation and any referenced issue, PR, or docs. Look for:

- new repo-specific nouns, roles, states, artifacts, or workflow names
- terms that were overloaded or caused confusion
- distinctions that need stable names
- terms to prefer or avoid in durable writing
- aliases that should point to one canonical term

Skip generic software terms unless the repo gives them a special meaning.
Skip ephemeral implementation details that are unlikely to matter after the
current change.

### 3. Decide Where Each Change Belongs

Use the narrowest durable home:

- `CONTEXT.md`: canonical domain terms, actor vocabulary, workflow nouns,
  artifact names, and preferred/avoided terms.
- `docs/agents/domain.md`: instructions for skills or coding agents about how
  to consume and apply the vocabulary.
- `docs/decisions.md` or `docs/adr/`: why a term exists when it reflects a
  durable design decision or rejected alternative.
- `docs/gotchas.md`: terminology traps that repeatedly lead to wrong code,
  wrong assumptions, or wrong review behavior.
- Nearby feature docs: local wording fixes when a concept is already explained
  there and the canonical glossary only needs a pointer.

Do not duplicate full definitions across many files. Put the canonical
definition in one place and make other docs point to it.

### 4. Edit Conservatively

For each accepted term, prefer a short definition with boundaries:

- what the term means in this repo
- what it does not mean, if confusion is likely
- which term to use instead of common ambiguous aliases

When renaming or clarifying an existing term, update nearby references that
would otherwise contradict the glossary. Avoid broad churn in unrelated docs.

### 5. Verify

Run text checks before finishing:

- `rg` for the old/confusing term and the new canonical term
- `git diff --check` for whitespace issues
- any repo-specific doc lint or validation command if one exists and is cheap

If the repo expects commits for completed work, commit the scoped vocabulary
change using the repo's commit convention. Leave unrelated dirty files alone.

## Final Response

Report:

- the canonical terms added or changed
- the files updated
- any intentionally unresolved naming questions
- validation performed
