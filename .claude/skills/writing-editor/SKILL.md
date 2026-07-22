---
name: writing-editor
description: Use when editing or reviewing a blog draft for this site (posts in _posts/ and _drafts/) to sharpen prose for the author's voice — strips AI-slop tells, enforces density/precision over rhetorical polish, verifies citations and structure. Pairs with the writing-editor subagent for dispatched reviews.
---

# Writing Editor

Editing calibration for this blog. The author's core preference is **counter-intuitive**:
rhetorical polish reads as slop. Improve a draft by making it more precise, concrete, and
useful — never by making it flow more smoothly. Never trade a specific for a cadence.

The authoritative, long-form calibration (exemplars, worked before/after examples, the full
rule set) lives in `references/calibration.md` — the single source of truth. For a full pass,
read it directly, or dispatch the `writing-editor` subagent (which reads the same file in its
own context). Use the checklist below for quick inline edits.

## Calibration checklist

- **Density over polish.** Exact paths/versions/numbers; link primary sources. A rougher,
  exact sentence beats a smooth one that gestures.
- **Show the artifact, don't describe it.** Replace "computes token breakdowns" with the real
  table/output.
- **Opinions must be the author's.** Keep genuine takes; strip only the impersonating frames
  ("What's really important is…", "It's not X, it's Y"). When unsure, flag — don't delete.
- **Plain functional description**, not rhetorical ranking ("the fullest example") or
  sales-pitch framing ("The pitch is…").
- **No appeal to authority.** Cite facts, not a named person's reaction/approval. Keep the
  `[[n]]` citation; drop the name-drop and the borrowed-enthusiasm quote.
- **No influencer/TED-talk staccato.** Don't stack short declaratives for drumbeat; fold into
  flowing prose. Replace colon-cliff list lead-ins ("What it emits:") with a real sentence.
- **No announce-then-explain.** Don't label a point with an abstract noun before stating it
  ("The catch is content depth…"). Make the concrete subject the actor; give the reason with
  because/so.
- **Show, don't tell.** Don't describe that an argument exists ("makes an explicit argument
  for why it's two"); make it.
- **No both-sidesing / filler.** Cut false-balance closers, filler adverbs ("surprisingly"),
  and underdeveloped asides (named-without-link).
- **Named surface tells.** Also catch: superficial `-ing` analysis ("highlighting,"
  "underscoring"), synonym cycling (rotating "agent/assistant/tool" for one referent),
  faux-insight setups ("what nobody tells you"), colon reveals ("The best part: …"), importance
  puffery ("marks a pivotal moment"), weasel attribution ("studies show"), and fake-profound
  kickers (delete them, don't improve them). Full definitions and before/after fixes are in the
  agent prompt.
- **Coherence.** Every "also/too/as well/likewise" needs a real prior antecedent in the
  body. Uncounted ordinals ("a fifth X") need an explicit prior count — name the
  relationship instead. And check **section placement**: each paragraph must belong
  under its header (a tool outside all four families does not go under "Family 4").

## Eval set

`assets/writing-voice-evals.jsonl` is a labeled corpus of bad→good pairs — one real defect
per case, tagged by the rule it violates. Use it to regression-test the agent: feed each
`bad` and check the editor flags the right pattern (detection mode) or moves toward `good`
(rewrite mode, judged with an LLM rubric). Schema and usage in
`assets/writing-voice-evals.md`.

**Extend it.** When the author points at a sentence as "bad writing," add a case: the exact
`bad` text, the `good` fix, and the `rule`. The set is the empirical record behind this
calibration and should grow over time.
