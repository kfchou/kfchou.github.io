---
layout: post
title: "interactive-review: an agent skill for editing prose in small passes"
categories: [AI Coding, Agent Skill, Claude Code, Writing]
excerpt: "interactive-review is an agent skill that turns a coding agent into an editor for a draft. You comment on the draft, the agent edits and answers, and the comments get resolved over several turns. It has a visual mode, where you review a rendered page in Lavish instead of reading comment markers in the markdown."
---

TL;DR - Claude Code users have no good way to review and edit markdown interactively with an agent, so I built one. `interactive-review` is an agent skill that makes the agent your editor, working a draft with you over many short turns instead of one rewrite. You can trade comments inline in the markdown file, or switch to **visual mode**: read a rendered page in Lavish [[1]], highlight a passage, comment on it, and see the agent's explanations in the margin. Install it with `npx skills add kfchou/kfchou.github.io --skill interactive-review`.

## Table of Contents <!-- omit from toc -->

- [Why a protocol for editing](#why-a-protocol-for-editing)
- [Bracket mode](#bracket-mode)
- [What the agent does as editor](#what-the-agent-does-as-editor)
- [Visual mode](#visual-mode)
- [How it compares to other tools](#how-it-compares-to-other-tools)
- [Installing it](#installing-it)
- [Limits](#limits)

## Why a protocol for editing

I work with markdown files a lot. Agents write good code, but the markdown they write is unpleasant to review in raw form: I end up reading syntax instead of the piece a reader will see. I wanted two things together, a rendered view of the document that is pleasant to read, and an interactive editing session with the agent on that same document.

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

The idea comes from the Claude desktop app, where you can highlight part of a response, comment on it, and have those comments go into your next message. I wanted the same thing for Claude Code users, in something lightweight that runs locally beside a terminal session.

Visual mode moves the conversation out of the file. The skill includes a small Node script, `scripts/serve.mjs`, which renders the markdown with markdown-it [[2]] to a reading page: a serif body, tables in a scrolling wrapper, and light and dark themes. The script keeps running beside the session, re-renders the page whenever the markdown or the agent's notes change, and saves edits I make on the page back to the file. The agent opens that page in Lavish [[1]], a local review surface for HTML pages in which you select text, comment on it, and send the comments back to the agent. The agent's notes are a JSON file of `{quote, note}` pairs; the page highlights each quoted passage and shows the note in the margin beside it.

![Visual mode in Lavish: a comment being written on a highlighted list item, with the agent's notes in the margin and its last reply in the Conversation panel](/assets/2026-10-22-interactive-review/visual-mode.png)

One turn in visual mode goes like this:

1. The agent starts `serve.mjs` in the background and opens the page with `lavish-axi <page>`.
2. It waits with `lavish-axi poll <page>`. I read the page, edit text directly or comment on passages, and send my comments.
3. The agent checks the file for edits I saved from the page, edits the markdown file itself, and rewrites the notes file to explain what it changed and what it wants from me. The page re-renders as the files change.
4. It waits again with `lavish-axi poll <page> --agent-reply "<handoff>"`, which shows its short summary in Lavish.

This repeats until I end the session from Lavish. The protocol is the same as bracket mode. My comments arrive as quoted selections instead of `<brackets>`, the agent's `<<replies>>` become margin notes, and a resolved thread drops its note. To answer a note, I highlight it and comment.

I can also edit the document on the page. With Lavish's Annotate switch turned off, clicking a paragraph, heading, list, or table swaps it for its markdown source. Enter adds a line and a blank line starts a new paragraph. When I click away, `serve.mjs` writes those lines into the file and the page re-renders, so typing `_unusual_` shows up in italics a moment later. The agent doesn't need to apply anything. At the start of its next turn it diffs the file against the version it last left and treats what changed as my decisions, adding a note only when an edit conflicts with something else in the draft. Editing and commenting are separate modes because Lavish doesn't open a comment box for a selection inside editable text.

Notes anchor by exact quote, so a note goes stale when the agent edits the passage it quotes. Stale notes are not dropped. The page lists them at the bottom under "Notes that no longer match the text", and the skill tells the agent to fix or delete them before handing back.

Bracket mode stays the default. When a session starts in bracket mode, the agent says in one line that visual mode is available, and it switches only when I ask ("review this visually", "open it in Lavish").

## How it compares to other tools

Other tools cover parts of this, and some are further along. Plannotator [[3]] is the closest. It is a local, browser-based review surface for Claude Code and several other agents, and its `/plannotator-annotate` command opens any markdown file. There you comment on exact text, mark passages for deletion, or edit the markdown, and Plannotator sends all of it back to the agent as structured feedback, with your edits as a diff.

Nimbalyst [[4]] is a desktop workspace that runs Claude Code and Codex. You step through the agent's proposed edits in a rendered WYSIWYG document and accept or reject each one. any-markdown [[5]], a VS Code extension, and VMark [[6]], a desktop editor, give you a WYSIWYG markdown editor that stays in step while an agent edits the same file. markupmarkdown [[7]] is a web app with threaded margin comments, where agents join through an MCP server, leave their own threads, and propose edits for you to accept. On a team, a pull request with Claude Code GitHub Actions [[8]] gives line-anchored comments that Claude answers with commits.

| Tool | Where you review | Agent's explanations anchored in the document | You edit the markdown file directly | Needs |
|------|------------------|-----------------------------------------------|-----------------------------------------------|-------|
| interactive-review | Rendered page in Lavish | Yes, margin notes | Yes, one block's source at a time | Node, lavish-axi |
| Plannotator | Browser review page | Not documented | No; edits go to the agent as a diff | Plannotator install |
| Nimbalyst | Desktop app, WYSIWYG | Not documented | Yes, and you accept or reject the agent's edits | Desktop app |
| any-markdown | VS Code, WYSIWYG | Not documented | Yes | VS Code or a compatible editor |
| VMark | Desktop app, WYSIWYG | Not documented | Yes | Desktop app |
| markupmarkdown | Web app | Yes, threads via MCP | Through its editor and a GitHub round-trip | Hosted app, or self-hosting with MongoDB |
| PR + GitHub Actions | GitHub diff | Yes, review comments | Through commits | GitHub, Actions, API key or subscription |

Most of what this skill adds is in how the agent edits. In the other tools the agent receives your comments or proposes edits for you to accept, and how it behaves as an editor is up to the agent. The skill gives it a protocol: read every open comment before changing anything, raise one issue per comment, make small edits without asking, and ask before restructuring. It also has the agent explain each change in a margin note beside the passage, which the same protocol does with `<<brackets>>` when no tooling is available. The visual mode is small: two Node scripts and Lavish in the browser, with no app, editor extension, account, or database, and the markdown file stays the only copy of the document.

The alternatives are better in several places. Plannotator is far more mature and has dedicated integrations for many agents. Nimbalyst and the WYSIWYG editors let you edit the rendered text itself, while this skill opens one block's markdown source at a time. markupmarkdown and pull requests handle more than one reviewer.

## Installing it

With the `skills` CLI [[9]]:

```sh
# for the current project
npx skills add kfchou/kfchou.github.io --skill interactive-review

# for your user, across projects
npx skills add kfchou/kfchou.github.io --skill interactive-review -g
```

The `--skill` flag is needed because the repository has other skills that only make sense for this blog. You can also copy the [`skills/interactive-review`][skill] folder into your agent's skills directory by hand (for Claude Code, `~/.claude/skills/interactive-review/`) Bracket mode has no other requirements. Visual mode needs Node.js 18 or later and `lavish-axi` (`npm install -g lavish-axi`). The scripts use only Node's standard library and a vendored copy of markdown-it, so there is nothing else to install.

## Limits

There is no view of what changed since my last review, so I rely on the agent's notes to say what moved.

The quote anchoring is plain text matching. A quote that appears twice highlights its first occurrence, and a quote copied with markdown syntax in it (`**bold**`, link brackets) won't match the rendered text. The agent is told to quote the text as it reads, but that rule is enforced only by the instructions.

Editing works on whole blocks of markdown source, so a list or a table opens as a whole. If the agent changes the file while I have a block open, my save is refused and the page asks me to reload rather than overwrite the agent's edit; I copy my text and redo it. The renderer is CommonMark with GitHub-style tables, so footnotes and other pandoc extensions show as plain text.

[skill]: https://github.com/kfchou/kfchou.github.io/tree/master/skills/interactive-review
[skillmd]: https://github.com/kfchou/kfchou.github.io/blob/master/skills/interactive-review/SKILL.md

## References

[1]: https://github.com/kunchenguid/lavish-axi "Lavish (lavish-axi)"
[2]: https://github.com/markdown-it/markdown-it "markdown-it"
[3]: https://github.com/backnotprop/plannotator "Plannotator"
[4]: https://github.com/nimbalyst/nimbalyst "Nimbalyst"
[5]: https://github.com/raggbal/any-markdown "any-markdown"
[6]: https://github.com/xiaolai/vmark "VMark"
[7]: https://www.metavert.io/markupmarkdown "markupmarkdown"
[8]: https://code.claude.com/docs/en/github-actions "Claude Code GitHub Actions"
[9]: https://www.npmjs.com/package/skills "skills CLI"

1. [Lavish (lavish-axi)](https://github.com/kunchenguid/lavish-axi)
2. [markdown-it](https://github.com/markdown-it/markdown-it)
3. [Plannotator](https://github.com/backnotprop/plannotator)
4. [Nimbalyst](https://github.com/nimbalyst/nimbalyst)
5. [any-markdown](https://github.com/raggbal/any-markdown)
6. [VMark](https://github.com/xiaolai/vmark)
7. [markupmarkdown](https://www.metavert.io/markupmarkdown)
8. [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
9. [skills CLI](https://www.npmjs.com/package/skills)
