---
name: aa:my-words
description: Walk through existing PR review findings one at a time. Discuss, revise, skip, or defer each finding and publish approved comments in the user's voice. Also use for replies to existing review threads.
---

# Put PR feedback in my words

Start with the findings, reviewed commit, diff lines, and discussion already available from the review. Fill evidence gaps for the current item with the local checkout or authenticated `gh` on the PR host. If you learn about a push or new feedback, assess it before proceeding.

Take the user's chosen item, otherwise the highest-priority open finding. Drop fixed findings. If a thread covers the point, link it and move on. Show the exact code link and a draft in the user's voice with a concrete consequence and short request. Distinguish a test result from a code trace. For a reply, use the original thread and agreed decision. Verify and link any pushed fix.

Use the bundled [my-words CLI](scripts/my-words) from the same working directory throughout the conversation, or pass the same absolute `--store` path before the command. In the examples, `my-words` stands for the path to that executable. Save the text before showing its preview.

```sh
my-words draft --pr https://github.com/owner/repo/pull/42 --login aaronfc \
  --head "$reviewed_sha" --inline src/order.py RIGHT 219 \
  --head-checked "$head_check_time" --discussion-checked "$discussion_check_time" \
  --body-file "$body_file"
my-words draft --replaces "$draft_id" --body-file "$edited_body_file"
my-words send "$approved_revision_id"
```

Use the expected account for this host. Supply actual Unix timestamps for when the remote head and discussion were checked. Omit unknown times. Use `--reply ROOT_COMMENT_ID` for a thread. If a finding has no suitable diff line, offer to include it in a combined `--top-level` comment. “Include it” saves the item for the combined preview after all findings have a decision.

Discuss, skip, or defer without sending. For wording edits, replace the current revision locally and show its full text. Check evidence for a changed claim. “Send it” approves the latest preview. “Send it with these changes” also approves the specified edit. Agreement with a finding or fix does not authorize posting.

On approval, call `send` with the saved revision. It reuses each check for five minutes, checks the posting account and returns the verified permalink. If it reports changed evidence, assess that change. Use `draft --replaces` with the updated evidence and actual check time. Proceed under the existing approval only if the text, claim and destination still hold. Otherwise show the revised preview for approval.

If publication is uncertain, another `send` of the same ID only looks up the attempted post. Report unresolved attempts. Finish with posted links and skipped or deferred items. If the user takes over posting, leave it to them.
