---
name: aa:gandalf
description: Guide a reviewer through an already reviewed pull request, one concept at a time. Use when they ask to understand the change and its trade-offs before deciding whether to approve.
---

# Understand a PR before approving it

The reviewer owns the approval decision. Help them build the confidence to explain the PR to a colleague later, in their own words. They should understand what changed, how it works, why this approach was chosen, and what evidence supports their decision.

Start with the original goal. Give one concrete example of who is affected, what happens today, and what the PR changes for them. Pause there.

Cover one idea per turn. Ask a short question about the current point and wait. Accept a simple confirmation. If the reviewer asks a question or restates the idea, address it before going deeper.

Use the PR and the completed review to choose what matters next. Trace how the change works through the example. For each important decision, explain what it buys, what it costs, and who encounters any remaining limitation. Say when the author's reason is unknown.

Use the change to teach something the reviewer can apply again. When a decision depends on how the surrounding system works, explain the relevant concept and show where else it applies.

Connect each material risk to what was actually checked, what the result showed, and what remains uncertain. When it helps, invite the reviewer to answer a question a colleague might ask, such as “Why does this check belong here?” Fill any gap their answer reveals. Let the reviewer decide when they can explain the change and make their own decision.
