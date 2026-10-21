#!/usr/bin/env python3
"""Layout-preserving PDF -> plain text extractor with bold/italic tagging.

Usage:  python extract_layout.py input.pdf output.txt [--style markdown|html] [--cols 110]

* Works on PDFs with live (selectable) text. Uses PyMuPDF (pip install pymupdf).
* Each text span is placed on a fixed-width character grid using its x-coordinate, so
  indentation, line wraps, column alignment and table cells keep their visual position.
* Vertical gaps larger than a normal line are kept as blank lines (paragraph breaks).
* Emphasis is detected from font flags AND font names (e.g. 'Helvetica-BoldOblique'):
    markdown style: **bold**  *italic*  ***bold italic***
    html style:     <b>bold</b>  <i>italic</i>  <b><i>bold italic</i></b>
* Pages are separated with a marker line:  ===== Page N / M =====
"""
import sys, argparse, re
import pymupdf

def emphasis(span):
    name = span["font"].lower()
    bold = bool(span["flags"] & 16) or bool(re.search(r"bold|black|heavy|semibold", name))
    italic = bool(span["flags"] & 2) or bool(re.search(r"italic|oblique", name))
    return bold, italic

def wrap(text, bold, italic, style):
    core = text.strip()
    if not core or not (bold or italic):
        return text
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    if style == "html":
        if bold: core = f"<b>{core}</b>"
        if italic: core = f"<i>{core}</i>" if not bold else f"<b><i>{core[3:-4]}</i></b>"
    else:
        mark = "***" if bold and italic else "**" if bold else "*"
        core = f"{mark}{core}{mark}"
    return lead + core + trail

def merge_spans(spans):
    """Join neighbouring spans that share the same emphasis so tags are not fragmented."""
    out = []
    for s in spans:
        if out and out[-1]["emph"] == s["emph"] and s["x0"] - out[-1]["x1"] < s["size"] * 0.6:
            gap = " " if s["x0"] - out[-1]["x1"] > s["size"] * 0.15 and not out[-1]["text"].endswith(" ") else ""
            out[-1]["text"] += gap + s["text"]; out[-1]["x1"] = s["x1"]
        else:
            out.append(dict(s))
    return out

def page_lines(page):
    rows = []
    d = page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)
    for block in d["blocks"]:
        for line in block.get("lines", []):
            for sp in line["spans"]:
                if not sp["text"].strip():
                    continue
                x0, y0, x1, y1 = sp["bbox"]
                rows.append({"x0": x0, "x1": x1, "y": (y0 + y1) / 2, "h": y1 - y0, "size": sp["size"],
                             "text": sp["text"], "emph": emphasis(sp)})
    rows.sort(key=lambda r: (round(r["y"], 0), r["x0"]))
    lines, cur = [], []
    for r in rows:  # group spans whose vertical centres are within 40% of the text height
        if cur and abs(r["y"] - cur[0]["y"]) > 0.4 * max(r["h"], cur[0]["h"]):
            lines.append(cur); cur = []
        cur.append(r)
    if cur: lines.append(cur)
    return lines

def render_page(page, style, cols):
    lines = page_lines(page)
    if not lines:
        return ""
    x_min = min(s["x0"] for l in lines for s in l)
    x_max = max(s["x1"] for l in lines for s in l)
    cw = max((x_max - x_min) / cols, 1e-3)          # points per character column
    body = sorted(s["size"] for l in lines for s in l)[len([1 for l in lines for s in l]) // 2]
    out, prev_y = [], None
    for l in lines:
        y = sum(s["y"] for s in l) / len(l)
        if prev_y is not None and y - prev_y > body * 1.9:   # paragraph gap -> blank line
            out.append("")
        prev_y = y
        text, col, prev = "", 0, None     # col = printed width so far (tags included, so cells start on the grid)
        for sp in merge_spans(sorted(l, key=lambda s: s["x0"])):
            target = int(round((sp["x0"] - x_min) / cw))
            if prev is not None and sp["x0"] - prev["x1"] < sp["size"] * 1.2:
                # inline continuation: normal word spacing, not grid spacing
                need = sp["x0"] - prev["x1"] > sp["size"] * 0.12 and not text.endswith(" ") and not sp["text"].startswith(" ")
                pad = 1 if need else 0
            else:
                # column jump (table cell, indent, tab stop): snap to the character grid
                piece = wrap(sp["text"], *sp["emph"], style)
                open_len = len(piece) - len(piece.lstrip("*<>bi/")) if piece.lstrip()[:1] in "*<" else 0
                pad = max(target - col - open_len, 1 if prev is not None else 0)  # visible text lands on the grid
            text += " " * pad
            piece = wrap(sp["text"], *sp["emph"], style)
            col += pad + len(piece)
            text += piece
            prev = sp
        out.append(text.rstrip())
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf"); ap.add_argument("out")
    ap.add_argument("--style", choices=["markdown", "html"], default="markdown")
    ap.add_argument("--cols", type=int, default=110, help="character width of the text grid")
    a = ap.parse_args()
    doc = pymupdf.open(a.pdf)
    parts = []
    legend = "**bold**  *italic*  ***bold italic***" if a.style == "markdown" else "<b>bold</b>  <i>italic</i>"
    parts.append(f"[Extracted from {a.pdf} | emphasis convention: {legend}]")
    for i, page in enumerate(doc, 1):
        parts.append(f"\n===== Page {i} / {doc.page_count} =====\n")
        parts.append(render_page(page, a.style, a.cols))
    open(a.out, "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print(f"wrote {a.out}: {doc.page_count} pages")

if __name__ == "__main__":
    main()
