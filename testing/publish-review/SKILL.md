---
name: aa:publish-review
description: Walk Aaron through posting existing PR findings when he asks to publish them or invokes /aa:publish-review. A request to review code alone does not start this flow.
---

# Publish review findings

1. Use the PR and findings from the conversation. Check the current head, diff and discussion with the local checkout and authenticated `gh`. Start with the highest-priority open finding unless Aaron picks another. Drop fixed findings. If a thread already covers the point, link it and move on.
2. Link the exact code. In one or two sentences, explain what someone would see and why it matters. Draft one comment in Aaron’s voice. Give a concrete observation and ask a short question or request a change. Distinguish what was tested from what the code suggests.
3. Stay on this finding until Aaron decides. Answer “why?” here. Show a new preview after wording suggestions. Agreement with the finding does not approve a post. Skip or defer when asked. If Aaron will post it himself, leave it to him.
4. If there is no suitable diff line, offer to save the item for one top-level PR comment. “Include it” saves the item. After all findings have a decision, show the full combined comment for edits and approval.
5. Post only on explicit approval, including “send it with these changes.” Recheck the head, target and discussion just before posting. If the claim, wording or placement must change, show the revised preview for approval. Confirm `gh api user` identifies Aaron on the PR host. Post the final approved text verbatim on the intended diff line or as the agreed combined comment.
6. Verify each post and return its permalink. If the result is unclear, look for Aaron’s exact comment at the intended location before retrying. If you cannot tell whether it posted, stop and report that. Finish with published links and any skipped or deferred items.
