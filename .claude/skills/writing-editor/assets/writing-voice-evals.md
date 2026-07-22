# Writing-voice eval set

A labeled corpus of bad→good prose pairs for evaluating the [`writing-editor`](../../../agents/writing-editor.md)
agent (or any editor). Each case is one real defect caught while editing a draft, tied to
a specific calibration rule the agent is supposed to enforce.

The set exists so a change to the agent can be regression-tested: does the editor still
catch the LinkedIn frame, the announce-then-explain, the appeal to authority, and so on?

## Files

- `writing-voice-evals.jsonl` — one eval case per line.

## Schema

Each line is a JSON object:

| Field | Meaning |
|-------|---------|
| `id` | stable kebab-case slug |
| `category` | `voice` (register/rhetoric), `structure` (coherence/reference integrity), or `grammar` (proofing) |
| `pattern` | short human label for the defect |
| `rule` | the calibration rule it violates (maps to a rule in `writing-editor.md`) |
| `bad` | the offending text — the eval **input** |
| `good` | the fixed/reference text — the target direction. `<in angle brackets>` means the fix is a deletion or a judgment call, not a verbatim string |
| `note` | why it's bad / what the fix does |
| `source` | where it came from |

## How to use it

Two evaluation modes, depending on what you're testing:

1. **Detection** — feed `bad` to the editor and check it flags the defect named in
   `pattern` / `rule`. This is the cheaper, more robust check (no exact-string matching).
2. **Rewrite** — feed `bad` and check the editor's rewrite moves toward `good`. Because
   prose has many valid rewrites, judge with an LLM rubric ("does the rewrite remove the
   named defect without changing meaning or inventing facts?") rather than string equality.

The blog this came from surveys tracing/eval platforms (Langfuse, Braintrust) — any of
them can host the rewrite-mode judge if you want a real harness rather than a script.

## Coverage vs. the agent's rules

The `voice` cases map one-to-one onto the calibration rules in `writing-editor.md`:
density/precision, show-don't-show, plain-description-over-ranking, no-appeal-to-authority,
no-influencer-staccato, announce-then-explain, no-sales-pitch-framing, no-both-sidesing,
show-don't-tell. `structure` covers the dangling-connective / reference-integrity check.
`grammar` is plain proofing.

## Extending it

When a new defect surfaces in editing (the author points at a sentence and says "this is
bad writing"), add a case: capture the exact `bad` text, the `good` fix, and the `rule`.
The set should grow as the author's ear gets more specific — it's the empirical record
behind the agent's calibration.
