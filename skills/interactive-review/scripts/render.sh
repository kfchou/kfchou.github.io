#!/usr/bin/env bash
# Render a markdown document to an HTML reading page for review in Lavish.
#
# Usage: render.sh <document.md> [notes.json] [out.html]
#
#   out.html    defaults to .lavish/<document-name>.html in the current directory
#   notes.json  defaults to <out without .html>.notes.json, beside the page;
#               a missing or empty file means "no notes"
#
# Notes are a JSON array of {"quote": "...", "note": "..."}. Each quote is exact
# text from the rendered document (whitespace may differ). The page highlights the
# quote and shows the note in the margin; a note whose quote no longer matches is
# listed at the end of the page instead of being dropped.
#
# Prints the path of the rendered page. Requires pandoc.
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 3 ]; then
  echo "usage: $(basename "$0") <document.md> [notes.json] [out.html]" >&2
  exit 2
fi
src=$1
[ -f "$src" ] || { echo "render.sh: no such file: $src" >&2; exit 1; }
command -v pandoc >/dev/null || { echo "render.sh: pandoc is required" >&2; exit 1; }

name=$(basename "$src"); name=${name%.*}
out=${3:-.lavish/$name.html}
notes=${2:-${out%.html}.notes.json}
mkdir -p "$(dirname "$out")"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# Page shell. Pandoc fills $...$ variables and escapes metadata values, so the
# document title and source path never pass through the shell into the HTML.
cat > "$tmp/page.html" <<'TEMPLATE'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$if(title)$$pagetitle$$else$$review-name$$endif$</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f2328;--muted:#656d76;--rule:#e4e0d8;--note:#fff6d6;--noteb:#e8c547;--mark:#fdeeb0;--warn:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--fg:#e6e6e6;--muted:#9aa1a9;--rule:#2c3036;--note:#2b2717;--noteb:#a8892a;--mark:#4a3f12;--warn:#f97066}}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 Charter,"Iowan Old Style",Georgia,serif}
main{max-width:46rem;margin:0 auto;padding:3rem 1rem 6rem}
.src{font:13px ui-monospace,monospace;color:var(--muted);overflow-wrap:anywhere}
h1{font-size:2rem;line-height:1.25;margin:.4rem 0 2rem}
h2{margin-top:2.6rem;padding-top:.6rem;border-top:1px solid var(--rule)}
img{max-width:100%}
pre{overflow-x:auto;background:var(--rule);padding:.8rem 1rem;border-radius:4px}
code{font:.88em ui-monospace,monospace;background:var(--rule);padding:.05em .3em;border-radius:3px}
pre code{background:none;padding:0}
blockquote{margin:1rem 0;padding-left:1rem;border-left:3px solid var(--rule);color:var(--muted)}
.tw{overflow-x:auto}
table{border-collapse:collapse;font:14px/1.45 system-ui,sans-serif;width:100%}
th,td{border:1px solid var(--rule);padding:.45rem .6rem;vertical-align:top;text-align:left}
th{background:var(--rule)}
mark.agent{background:var(--mark);color:inherit;border-radius:2px}
aside.agent-note{font:14px/1.5 system-ui,sans-serif;background:var(--note);border-left:3px solid var(--noteb);padding:.6rem .8rem;margin:.6rem 0 1.2rem;border-radius:4px}
.anno{position:relative}
.warn{font:14px/1.5 system-ui,sans-serif;color:var(--warn)}
#unanchored blockquote{font-style:italic}
@media (min-width:70rem){
  main{margin-left:max(0px,calc((100% - 67rem)/2))}
  .margin{position:absolute;top:0;left:calc(100% + 2rem);width:18rem}
  .margin aside.agent-note{margin:0 0 .6rem}
}
</style>
</head>
<body>
<main>
<div class="src">$review-source$</div>
$if(title)$
<h1>$title$</h1>
$endif$
$body$
</main>
$for(include-after)$
$include-after$
$endfor$
</body>
</html>
TEMPLATE

# Notes ride in a JSON data block. Escaping "<" as < keeps note text from
# closing the <script> element; inside JSON strings it decodes back to "<".
{
  printf '<script type="application/json" id="agent-notes">'
  if [ -s "$notes" ]; then sed 's/</\\u003c/g' "$notes"; else printf '[]'; fi
  printf '</script>\n'
  cat <<'SCRIPT'
<script>
(() => {
  const main = document.querySelector('main');

  // Wide tables scroll sideways instead of widening the page.
  for (const t of main.querySelectorAll('table')) {
    const w = document.createElement('div');
    w.className = 'tw';
    t.replaceWith(w);
    w.append(t);
  }

  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  };

  let notes = [];
  try {
    const raw = document.getElementById('agent-notes').textContent.trim();
    notes = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(notes)) throw new Error('expected a JSON array');
  } catch (e) {
    main.prepend(el('p', 'warn', 'Notes file could not be read (' + e.message + '); showing the document without notes.'));
    notes = [];
  }

  // Index the document's visible text with whitespace collapsed, remembering
  // which text node and offset each character came from.
  function indexText() {
    const chars = [];
    let text = '';
    const walk = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: n => n.parentElement.closest('.margin, #unanchored, .src, .warn')
        ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT,
    });
    for (let n; (n = walk.nextNode());) {
      for (let i = 0; i < n.data.length; i++) {
        const space = /\s/.test(n.data[i]);
        if (space && text.endsWith(' ')) continue;
        text += space ? ' ' : n.data[i];
        chars.push([n, i]);
      }
    }
    return { text, chars };
  }

  // Highlight the first occurrence of quote; return the first <mark> or null.
  function highlight(quote) {
    const q = quote.replace(/\s+/g, ' ').trim();
    if (!q) return null;
    const { text, chars } = indexText();
    const at = text.indexOf(q);
    if (at < 0) return null;
    const spans = new Map();
    for (const [node, i] of chars.slice(at, at + q.length)) {
      const s = spans.get(node);
      if (s) s[1] = i + 1; else spans.set(node, [i, i + 1]);
    }
    let first = null;
    for (const [node, [start, end]] of spans) {
      const r = document.createRange();
      r.setStart(node, start);
      r.setEnd(node, end);
      const m = el('mark', 'agent');
      r.surroundContents(m);
      first = first || m;
    }
    return first;
  }

  // The margin column belongs to the top-level block that holds the mark.
  function marginFor(mark) {
    let block = mark;
    while (block.parentElement !== main) block = block.parentElement;
    if (block.classList.contains('anno')) return block.querySelector('.margin');
    const anno = el('div', 'anno');
    const margin = el('div', 'margin');
    block.replaceWith(anno);
    anno.append(block, margin);
    anchors.set(margin, mark);
    return margin;
  }

  const anchors = new Map();
  const unanchored = [];
  for (const n of notes) {
    const quote = n && typeof n.quote === 'string' ? n.quote : '';
    const note = n && typeof n.note === 'string' ? n.note : JSON.stringify(n);
    const mark = quote ? highlight(quote) : null;
    if (mark) marginFor(mark).append(el('aside', 'agent-note', note));
    else unanchored.push([quote, note]);
  }

  if (unanchored.length) {
    const s = el('section');
    s.id = 'unanchored';
    s.append(el('h2', '', 'Notes that no longer match the text'),
      el('p', 'warn', 'The quoted passage was not found in the current document, usually because it was edited after the note was written.'));
    for (const [quote, note] of unanchored) {
      s.append(el('blockquote', '', quote || '(no quote)'), el('aside', 'agent-note', note));
    }
    main.append(s);
  }

  // On wide screens each margin column starts level with its first highlight,
  // pushed down when it would overlap the column above it.
  const wide = matchMedia('(min-width:70rem)');
  function stack() {
    let bottom = -Infinity;
    for (const [m, mark] of anchors) {
      m.style.top = '';
      if (!wide.matches) continue;
      const base = m.parentElement.getBoundingClientRect().top;
      const top = Math.max(mark.getBoundingClientRect().top, bottom + 12);
      m.style.top = (top - base) + 'px';
      bottom = m.getBoundingClientRect().bottom;
    }
  }
  stack();
  addEventListener('resize', stack);
  document.fonts && document.fonts.ready.then(stack);
})();
</script>
SCRIPT
} > "$tmp/after.html"

# -smart keeps straight quotes and dashes, so the rendered text matches the
# markdown source and notes can quote either one.
# --quiet drops pandoc's "nonempty <title>" warning; the template supplies one.
pandoc --quiet -f markdown-smart -t html5 --standalone --template "$tmp/page.html" \
  --include-after-body "$tmp/after.html" \
  -M "review-source=$src" -M "review-name=$name" \
  -o "$out" "$src"

echo "$out"
