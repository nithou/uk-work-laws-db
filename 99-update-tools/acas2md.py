#!/usr/bin/env python3
import os, re, sys, glob
from lxml import html as LH, etree
from markdownify import markdownify as mdify

SRC = "/home/claude/uk/raw/acas/html"
OUT = "/home/claude/uk-employment-law-bot"
SKIP = re.compile(r"(consultation|acas-response|acas-council-response|acas-updates|acas-seeks|introducing-the-new|consulting-on|statement-of-voluntary|annual-report|corporate|board-|-strategy|freedom-of|our-|acas-statement|news|press|blog|case-stud(y|ies)-|survey|webinar|e-learning|training|podcast|events)")

def clean_md(m):
    m = re.sub(r"\n{3,}", "\n\n", m)
    m = re.sub(r"(?m)^\s*Please tell us why the information did not help.*$", "", m)
    m = re.sub(r"\]\(/", "](https://www.acas.org.uk/", m)
    return m.strip()

def convert(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    d = LH.fromstring(raw)
    h1 = d.xpath("//h1")
    title = re.sub(r"\s+", " ", h1[0].text_content()).strip() if h1 else os.path.basename(path)
    nodes = d.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," article__content ")]') or d.xpath("//main")
    if not nodes:
        return None
    node = nodes[0]
    for bad in node.xpath('.//form|.//script|.//style|.//nav|.//*[contains(@class,"feedback")]|.//*[contains(@class,"share")]|.//*[contains(@class,"webform")]|.//button'):
        bad.getparent().remove(bad)
    md = clean_md(mdify(etree.tostring(node, encoding="unicode"), heading_style="ATX", bullets="-"))
    upd = re.search(r"(?i)(?:last updated|updated|published)\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})", raw)
    return title, md, (upd.group(1) if upd else "")

def main():
    n = 0
    idx = {"20-acas-codes-of-practice": [], "21-acas-advice": []}
    for p in sorted(glob.glob(SRC + "/*.html")):
        slugname = os.path.basename(p)[:-5]
        if "draft-revision" in slugname or re.search(r"user-interface|content-pattern|terms-of-reference|business-plan|training|video-transcript|style-guide|office-addresses|modern-slavery|participant-charter|statistics", slugname):
            continue
        rawt = open(p, encoding="utf-8", errors="replace").read()
        m = re.search(r"page-node-type-([\w-]+)", rawt)
        ntype = m.group(1) if m else "?"
        if ntype not in ("secondary-page", "details-page", "code-of-practice", "page", "flexible-landing-page"):
            continue
        r = convert(p)
        if not r:
            continue
        title, md, upd = r
        if len(md) < 500:
            continue
        url = "https://www.acas.org.uk/" + slugname.replace("__", "/")
        is_code = slugname.startswith("acas-code-of-practice") or slugname == "codes-of-practice"
        folder = "20-acas-codes-of-practice" if is_code else "21-acas-advice"
        fm = f'---\nsource: "Acas"\ntitle: "{title.replace(chr(34), chr(39))}"\nurl: "{url}"\nupdated: "{upd}"\nretrieved: "2026-11-03"\nlicence: "Open Government Licence v3.0 (Crown copyright)"\n---\n'
        text = fm + f"# {title}\n\n_Source: Acas — {url}" + (f" — updated {upd}" if upd else "") + "_\n\n" + md
        os.makedirs(os.path.join(OUT, folder), exist_ok=True)
        with open(os.path.join(OUT, folder, slugname[:110] + ".md"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        idx[folder].append((title, slugname[:110] + ".md"))
        n += 1
    for folder, items in idx.items():
        with open(os.path.join(OUT, folder, "INDEX.md"), "w", encoding="utf-8") as f:
            f.write(f"# Index — {folder}\n\n" + "\n".join(f"- [{t}]({fn})" for t, fn in items) + "\n")
    print(n, {k: len(v) for k, v in idx.items()})

main()
