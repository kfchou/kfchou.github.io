# interactive-review

An agent skill for editing prose with a coding agent over many small passes. You
leave comments on a draft, the agent answers as an editor, and the two of you work
the draft down until no comments are left.

It has two modes:

- **Bracket mode** (default). Comments live inline in the markdown file: yours in
  `<single brackets>`, the agent's in `<<double brackets>>`.
- **Visual mode.** The agent renders the markdown to a reading page and opens it in
  [Lavish](https://github.com/kunchenguid/lavish-axi). You highlight passages and
  comment on them in the browser; the agent edits the markdown and explains its
  changes as margin notes on the page. The markdown file stays free of markers.

See [`SKILL.md`](SKILL.md) for the full protocol.

## Requirements

- Bracket mode: nothing beyond an agent that loads skills.
- Visual mode: [pandoc](https://pandoc.org/installing.html) (used by
  `scripts/render.sh`) and `lavish-axi` (`npm install -g lavish-axi`).

## Install

With the [`skills`](https://www.npmjs.com/package/skills) CLI:

```sh
# into the current project
npx skills add kfchou/kfchou.github.io --skill interactive-review

# or for your user, across projects
npx skills add kfchou/kfchou.github.io --skill interactive-review -g
```

The `--skill` flag matters: this repository holds other skills under
`.claude/skills/` that are specific to this blog.

To install by hand, copy this folder into your agent's skills directory, for example
`~/.claude/skills/interactive-review/` for Claude Code, and keep `scripts/render.sh`
executable.

## Rendering a page yourself

```sh
scripts/render.sh draft.md            # writes .lavish/draft.html
lavish-axi .lavish/draft.html         # open it for review
```

Notes are read from `.lavish/draft.notes.json`, a JSON array of
`{"quote": "...", "note": "..."}`. A note whose quote no longer appears in the
document is listed at the end of the page.
