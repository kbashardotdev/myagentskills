#!/usr/bin/env python3
"""Check a fix report page. Usage: python3 check.py <page.html>
Prints one line per check. Exit 0: all pass. Exit 1: a check failed.
The page is data: the script does not run or follow it."""
import base64, re, sys
from html.parser import HTMLParser

PARTS = ["What was wrong", "How it was fixed", "Test evidence", "Lifecycle"]
MAX_VISIBLE, MAX_CARD, MAX_IMG_KB, PX = 600, 120, 300, 7
words = lambda t: sum(1 for w in t.split() if re.search(r"\w", w))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.visible, self.cards, self.done, self.h2 = [], [], [], [], []
        self.imgs, self.attrs_text, self.labels, self.vb, self.lab = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        a = {k: v or "" for k, v in attrs}
        self.attrs_text += [a[k] for k in ("alt", "aria-label", "title") if k in a]
        if tag == "img":
            self.imgs.append(a.get("src", ""))
        if tag in ("img", "meta", "br", "hr", "link", "source", "input"):
            return
        self.stack.append(tag)
        if tag == "details":
            self.cards.append([])
        if tag == "svg":
            p = re.split(r"[\s,]+", a.get("viewbox", "").strip())
            self.vb.append(float(p[2]) if len(p) == 4 and re.match(r"[\d.]+$", p[2]) else None)
        if tag == "text" and self.vb:
            self.lab = [float(a.get("x", "0") or 0), a.get("text-anchor", "start"), self.vb[-1], ""]

    def handle_endtag(self, tag):
        while tag in self.stack:
            top = self.stack.pop()
            if top == "details" and self.cards:
                self.done.append(words(" ".join(self.cards.pop())))
            if top == "svg" and self.vb:
                self.vb.pop()
            if top == "text" and self.lab:
                self.labels.append(self.lab)
                self.lab = None
            if top == tag:
                break

    def handle_data(self, data):
        d = data
        if "style" in self.stack or "script" in self.stack:
            return
        self.attrs_text.append(d)
        if self.lab is not None:
            self.lab[3] += d
        if "h2" in self.stack or "summary" in self.stack:
            self.h2.append(d)
        if "svg" in self.stack or "pre" in self.stack:
            return
        (self.cards[-1] if self.cards else self.visible).append(d)


def main(path):
    html = open(path, encoding="utf-8").read()
    p = Page()
    p.feed(html)
    rows = []
    rows.append(("no {{MARK}} left", not re.search(r"\{\{[A-Z_]+[:}]", html), ""))
    heads = " ".join(p.h2)
    missing = [x for x in PARTS if x not in heads]  # Lifecycle: an h2 section or a closed card
    rows.append(("parts in place", not missing, ", ".join(missing)))
    v = words(" ".join(p.visible))
    rows.append((f"visible words <= {MAX_VISIBLE}", v <= MAX_VISIBLE, str(v)))
    big = [n for n in p.done if n > MAX_CARD]
    rows.append((f"each card <= {MAX_CARD} words", not big, str(p.done)))
    codes = sorted({c for t in p.attrs_text for c in re.findall(r"\b[A-Z][0-9]{1,2}\b", t)})
    rows.append(("no codes such as B1", not codes, ", ".join(codes)))
    sizes, ext = [], []
    for s in p.imgs:
        m = re.match(r"data:image/[\w+]+;base64,(.*)", s, re.S)
        if m:
            sizes.append(len(base64.b64decode(m.group(1))) // 1024)
        else:
            ext.append(s[:40])
    rows.append(("images are data URIs", not ext, ", ".join(ext)))
    rows.append((f"each image <= {MAX_IMG_KB} KB", all(k <= MAX_IMG_KB for k in sizes), f"{sizes} KB"))
    css = " ".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    rows.append(("both dark-mode blocks", "prefers-color-scheme: dark" in css and ':root[data-theme="dark"]' in css, ""))
    over = []
    for x, anchor, width, text in p.labels:
        w = len(" ".join(text.split())) * PX
        left = {"middle": x - w / 2, "end": x - w}.get(anchor, x)
        if width and (left < -0.5 or left + w > width + 0.5):
            over.append(text.strip()[:30])
    rows.append(("SVG labels fit (7 px per char)", not over, "; ".join(over)))
    for name, ok, info in rows:
        print(f"{'ok  ' if ok else 'FAIL'}  {name}  {info}")
    return 0 if all(r[1] for r in rows) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
