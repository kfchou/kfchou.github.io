---
name: references-formatter
description: Use when formatting citations in blog posts or documents - converts inline links to reference-style links with a References section at the end
---

# References Formatter Skill

This skill guides you through converting inline citations and links into reference-style link format, commonly used in markdown documents and professional blog posts.

## When to Use This Skill

Invoke this skill when:
- The user asks to "format citations" or "add references"
- You see inline citations like `[source](url)` or `(from [link](url))` that should be numbered
- The user wants to convert a document to use numbered citations like `[1]` or `[1,2]`

## Formatting Process

Follow these steps systematically:

### 1. Identify Citations

Scan the document for citation patterns:
- Inline source links: `([source](url))`
- Parenthetical citations: `(from [link](url))`
- Inline references: `as mentioned in [article](url)`
- Multiple links in a sentence that are clearly citations

**Do NOT convert:**
- Intentional navigation links (GitHub repos, project links)
- Links that are part of the narrative flow
- Links in code blocks or examples
- Ask the user if uncertain about a specific link

### 2. Convert to Numbered Citations

Replace citation links with numbered reference syntax using double brackets:

- Use the format `[[N]]` for each citation (NOT `[N]` or `[^N]`)
- First citation becomes `[[1]]`
- Second citation becomes `[[2]]`
- Multiple citations: `[[1]][[2]]` (adjacent double brackets)
- Keep the numbering sequential throughout the document
- Preserve any existing explicit inline references like `[docs]` or `[anthropic-sdk]` as-is

**Spacing and Punctuation Rules:**

- **Always add a space before the citation**: `word [[1]]` not `word[[1]]`
- **Periods and commas come AFTER citations, never before**: `fact [[1]].` not `fact. [[1]]`
- **Multiple citations**: `fact [[1]][[2]],` with space before first citation
- **Mid-sentence citations**: `This is true [[3]], and so is that.`

**Examples:**

```markdown
Before: "According to research ([source](https://example.com))"
After:  "According to research [[1]]"

Before: "This is documented in [the official guide](https://docs.example.com)"
After:  "This is documented in the official guide [[2]]"

Before: "Multiple studies show ([source1](url1), [source2](url2))"
After:  "Multiple studies show [[1]][[2]]"

Before: "New fact from [source3](url3), and another from [source4](url4)."
After:  "New fact [[3]], and another fact [[4]]."

Before: "Check out the [documentation hub][docs]"
After:  "Check out the [documentation hub][docs]"  (preserve explicit inline references)
```

### 3. Build/Update References Section

At the end of the document, create or update a `## References` section using reference-style link definitions AND a numbered list:

```markdown
## References

[1]: https://example.com/article "Descriptive Title - Author/Source"
[2]: https://example.com/article2 "Another Article Title - Publication"
[3]: https://example.com/article3 "Third Reference - Author"

1. [Descriptive Title - Author/Source](https://example.com/article)
2. [Another Article Title - Publication](https://example.com/article2)
3. [Third Reference - Author](https://example.com/article3)
```

**Reference Format Guidelines:**

- For each reference, include BOTH:
  1. The link definition at the top: `[N]: URL "Title - Source"`
  2. The numbered list item: `N. [Title - Source](URL)`
- Group all link definitions together at the top of the References section
- Then create the numbered list display below (separated by one blank line)
- Use descriptive titles that tell what the link is about
- Include author/source/publication name when available
- The link definition enables `[[N]]` to work as clickable links in the text
- The numbered list shows readers the full reference information in a clean format

### 4. Handle Further Reading (Optional)

If there are additional links that are supplementary but not directly cited:
- Create a separate `## Further Reading` section
- Place it after the References section
- Use descriptive markdown links without numbers

```markdown
## Further Reading

- [Topic Guide - Source Name](https://example.com)
- [Related Article - Publication](https://example.com/related)
```

## User Preferences to Ask About

Before starting, clarify:
1. Should intentional GitHub/repo links be preserved as-is?
2. Should all external links be converted, or only explicit citations?
3. Do they want a separate "Further Reading" section?

## Example Workflow

1. Read the entire document first
2. Identify all citation-style links
3. Ask user about any ambiguous links (e.g., "Should I preserve the GitHub repository links?")
4. Convert citations to numbers sequentially
5. Build the References section with proper formatting
6. Create Further Reading section if applicable
7. Verify all numbered citations have corresponding references

## Common Patterns to Recognize

**Pattern 1: Parenthetical source**

```markdown
Text here ([source](url))
→ Text here [^1]
```

**Pattern 2: Inline attribution**

```markdown
According to [research](url), we know that...
→ According to research [^1], we know that...
```

**Pattern 3: Multiple sources**

```markdown
Studies show ([source1](url1), [source2](url2))
→ Studies show [^1][^2]
```

**Pattern 4: Documentation reference**

```markdown
(from the [official docs](url))
→ (from the official docs [^1])
```

## Quality Checks

Before completing:
- [ ] All numbered citations have corresponding entries in References
- [ ] References are numbered sequentially (no gaps)
- [ ] Each reference has a descriptive title
- [ ] Intentional navigation links preserved if requested
- [ ] References section is at the end of the document
- [ ] One blank line between each reference entry

## Notes

- This is a formatting workflow - maintain context throughout the conversation
- Be prepared to iterate based on user feedback
- Some links may be ambiguous - always ask rather than assume
- Preserve the document's voice and flow while updating citations
