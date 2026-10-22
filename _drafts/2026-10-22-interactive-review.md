---
layout: post
title: "interactive-review: an agent skill for editing prose in small passes"
categories: [AI Coding, Agent Skill, Claude Code, Writing]
excerpt: "interactive-review is an agent skill that turns a coding agent into an editor for a draft. You comment on the draft, the agent edits and answers, and the comments get resolved over several turns. It has a visual mode, where you review a rendered page in Lavish instead of reading comment markers in the markdown."
---

TL;DR - `interactive-review` is an agent skill for editing a piece of writing with a coding agent over many short turns instead of one rewrite. In the default **bracket mode**, you leave `<comments>` in the markdown file and the agent replies in `<<double brackets>>` beside them. In **visual mode**, the agent renders the markdown to a reading page and opens it in Lavish [[1]], you highlight passages and comment on them in the browser, and the agent's explanations show up as margin notes while the markdown file stays clean. The skill lives in this blog's repository under [`skills/interactive-review`][skill], and installs with `npx skills add kfchou/kfchou.github.io --skill interactive-review`.

## Table of Contents <!-- omit from toc -->

- [Why a protocol for editing](#why-a-protocol-for-editing)
- [Bracket mode](#bracket-mode)
- [What the agent does as editor](#what-the-agent-does-as-editor)
- [Visual mode](#visual-mode)
- [Installing it](#installing-it)
- [Limits](#limits)

## Why a protocol for editing

Asking an agent to "improve this draft" gets you a rewrite. The rewrite is smoother and less mine: the specific claims get softened, the voice drifts toward the model's, and the paragraph I liked is gone with no record of why. Going back and forth in chat keeps the draft intact, but the comments live in the conversation and the edits live in the file, and the two drift apart. After a few rounds I can't tell which of my comments were acted on, which were argued with, and which were dropped.

What I wanted was the way a writer works with a human editor: both people mark up one copy of the draft, each pass resolves some comments and raises a few sharper ones, and the draft converges because the comments run out. The skill writes that down as a protocol the agent follows.

The skill is for prose: posts, essays, READMEs, specs. It is not a code reviewer. It will edit a README or an error message as writing, but it doesn't judge the code around it.

## Bracket mode

All comments live in the document, and the number of brackets says who wrote them. Mine use single brackets; the agent's use double brackets. Here is one exchange from a draft about a research wiki whose analyses list their sources in a `sources:` field:

```markdown
Here's a lucky property of a research wiki: it grades itself. <expand — why lucky?>
<<Because the eval set already exists: every analysis's `sources:` field is a
labeled (query, gold-answer) pair. I've added a sentence below naming that. But it
only works if your wiki cites in a structured field. Want that as a caveat line or
folded in?>>
```

On its turn the agent reads every open comment before changing anything, because comments interact: a `<cut this>` in one paragraph can make another concern moot. For each of my comments it either makes the edit and deletes the comment, or leaves the comment in place with a `<<reply>>` when it disagrees or needs a decision. It then adds its own `<<comments>>`, deletes the ones I've answered, and hands back with a short chat message saying what changed and what it needs from me. The reasoning stays in the file, so I can open it cold and see where every thread stands. A finished draft has no comments left.

## What the agent does as editor

Carrying out my comments is the minimum. `SKILL.md` also gives the agent a checklist of problems to raise that I didn't ask about. The ones I rely on most:

- **Assumed reader knowledge**: a term or system I live inside and forget the reader doesn't.
- **Buried lead**: the best idea sitting in a subordinate clause three paragraphs in.
- **Restatement**: a paragraph whose later sentences repeat the first in different words.
- **Social-media cadence**: hook-and-reveal beats and punchy fragments in prose meant to be read straight through.
- **Unsupported claims**: a number or a causal claim with nothing behind it.

The agent gets autonomy for local edits only. It changes a word or tightens a paragraph without asking, but a section reframe, a move, or a cut is raised as a `<<STRUCTURAL: ...>>` comment and waits for my answer. The full list and rules are in [`SKILL.md`][skillmd].

## Visual mode

On a long draft, bracket mode's markers get in the way of reading. The file fills with comments, a table is hard to judge as raw pipe syntax, and I end up reviewing markdown source instead of the piece a reader will see.

Visual mode moves the conversation out of the file. The skill includes a small script, `scripts/render.sh`, which uses pandoc [[2]] to render the markdown to a reading page: a serif body, tables in a scrolling wrapper, and light and dark themes. The agent opens that page in Lavish [[1]], a local review surface for HTML pages in which you select text, comment on it, and send the comments back to the agent. The agent's notes are a JSON file of `{quote, note}` pairs; the page highlights each quoted passage and shows the note in the margin beside it.

![A rendered draft in visual mode, with highlighted passages and the agent's notes in the right margin](/assets/2026-10-22-interactive-review/visual-mode.png)

One turn in visual mode goes like this:

1. The agent renders the page and opens it with `lavish-axi <page>`.
2. It waits with `lavish-axi poll <page>`. I read the page, highlight passages, write comments, and send them.
3. The agent edits the markdown file, never the page, and rewrites the notes file to explain what it changed and what it wants from me.
4. It re-renders and waits again with `lavish-axi poll <page> --agent-reply "<handoff>"`, which shows its short summary in Lavish.

This repeats until I end the session from Lavish. The protocol is the same as bracket mode. My comments arrive as quoted selections instead of `<brackets>`, the agent's `<<replies>>` become margin notes, and a resolved thread drops its note. To answer a note, I highlight it and comment.

Notes anchor by exact quote, so a note goes stale when the agent edits the passage it quotes. Stale notes are not dropped. The page lists them at the bottom under "Notes that no longer match the text", and the skill tells the agent to fix or delete them before handing back.

Bracket mode stays the default. When a session starts in bracket mode, the agent says in one line that visual mode is available, and it switches only when I ask ("review this visually", "open it in Lavish").

## Installing it

With the `skills` CLI [[3]]:

```sh
# for the current project
npx skills add kfchou/kfchou.github.io --skill interactive-review

# for your user, across projects
npx skills add kfchou/kfchou.github.io --skill interactive-review -g
```

The `--skill` flag is needed because the repository has other skills that only make sense for this blog. You can also copy the [`skills/interactive-review`][skill] folder into your agent's skills directory by hand (for Claude Code, `~/.claude/skills/interactive-review/`) and keep `scripts/render.sh` executable. Bracket mode has no other requirements. Visual mode needs pandoc and `lavish-axi` (`npm install -g lavish-axi`).

## Limits

The page doesn't refresh while the agent edits the markdown; it changes only when the agent re-renders it at the end of a turn. There is also no view of what changed since my last review, so I rely on the agent's notes to say what moved.

The quote anchoring is plain text matching. A quote that appears twice highlights its first occurrence, and a quote copied with markdown syntax in it (`**bold**`, link brackets) won't match the rendered text. The agent is told to quote the text as it reads, but that rule is enforced only by the instructions.

[skill]: https://github.com/kfchou/kfchou.github.io/tree/master/skills/interactive-review
[skillmd]: https://github.com/kfchou/kfchou.github.io/blob/master/skills/interactive-review/SKILL.md

## References

[1]: https://github.com/kunchenguid/lavish-axi "Lavish (lavish-axi)"
[2]: https://pandoc.org/ "Pandoc"
[3]: https://www.npmjs.com/package/skills "skills CLI"

1. [Lavish (lavish-axi)](https://github.com/kunchenguid/lavish-axi)
2. [Pandoc](https://pandoc.org/)
3. [skills CLI](https://www.npmjs.com/package/skills)
