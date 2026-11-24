---
name: aa:my-words
description: Draft existing PR findings or replies to reviewer feedback in the user's voice. Use when asked to phrase or publish PR feedback, or when invoked with /aa:my-words. A request to review code or fix an issue alone does not start this flow.
---

# Put PR feedback in my words

Use the PR, findings, and decisions from the conversation. Check the current head, diff, and discussion with the local checkout and authenticated `gh` on the PR host. Take one item at a time in the user's chosen order.

- **New finding.** Start with the highest-priority open finding by default. Drop fixed findings. If a thread already covers the point, link it and move on. Link the exact code and explain the consequence. Draft a concrete observation and a short question or request. Distinguish what was tested from what the code suggests.
- **Reply to feedback.** Read the original thread and draft a direct reply there. Explain the agreed decision briefly. For a pushed fix, verify and link the commit that addresses the point. Describe any pending work accurately. If the decision is unclear, ask the user before drafting.

Use the user's voice. Stay on the item until they decide. Answer questions, preview edits, and skip or defer when asked. Agreement with a finding or approval of a fix does not approve a post. If the user will post it themselves, leave it to them.

For a new finding without a suitable diff line, offer to save it for one top-level PR comment. “Include it” saves the item. After all findings have a decision, show the full combined comment for edits and approval.

Post only on explicit approval, including “send it with these changes.” Recheck the head, target, and discussion just before posting. If the claim, wording, or placement must change, show the revised preview for approval. Confirm `gh api user` identifies the user on the PR host. Post the approved text verbatim on the intended diff line, in the original thread, or as the agreed top-level comment.

Verify each post and return its permalink. If the result is unclear, look for the user's exact comment at the intended location before retrying. If you cannot tell whether it posted, stop and report that. Finish with published links and any skipped or deferred items.
