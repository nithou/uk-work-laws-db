#!/usr/bin/env python3
"""Convert legislation.gov.uk CLML XML (revised or made) to RAG-friendly Markdown, one file per Part/Schedule."""
import os, re, sys, json
from lxml import etree

NS = {"l": "http://www.legislation.gov.uk/namespaces/legislation",
      "ukm": "http://www.legislation.gov.uk/namespaces/metadata",
      "dc": "http://purl.org/dc/elements/1.1/", "dct": "http://purl.org/dc/terms/",
      "atom": "http://www.w3.org/2005/Atom"}
L = "{http://www.legislation.gov.uk/namespaces/legislation}"

def local(el):
    return etree.QName(el).localname if isinstance(el.tag, str) else ""

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def nummark(s):
    return re.sub(r"⟦(?:partly in force / prospective|still in force, to be replaced): ([^⟧]*)⟧", r"\1", s)

def slug(s, n=50):
    s = clean(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].strip("-")

SKIP_INLINE = {"CommentaryRef", "FootnoteRef"}
COMMENTS = {}
PARTIAL = re.compile(r"for specified purposes|prospective|not yet in force", re.I)

def inline(el):
    """Flatten inline content to text."""
    out = []
    if el.text:
        out.append(el.text)
    for c in el:
        name = local(c)
        if name in SKIP_INLINE:
            pass
        elif name in ("Emphasis",):
            out.append("*" + inline(c).strip() + "*")
        elif name in ("Strong",):
            out.append("**" + inline(c).strip() + "**")
        elif name == "Term":
            out.append(inline(c))
        elif name in ("Repeal",):
            t = inline(c).strip()
            if c.get("RetainText") == "true" and t:
                out.append(f"⟦still in force, to be replaced: {t}⟧")
            else:
                out.append(t if t else "…")
        elif name in ("Addition", "Substitution") and PARTIAL.search(COMMENTS.get(c.get("CommentaryRef"), ("", ""))[1] or ""):
            t = inline(c)
            out.append(f"⟦partly in force / prospective: {t.strip()}⟧" if t.strip() else t)
        else:
            out.append(inline(c))
        if c.tail:
            out.append(c.tail)
    return "".join(out)

class Ctx:
    def __init__(self, comments):
        self.comments = comments  # id -> (type, text)
        self.refs = []

def collect_refs(el, ctx):
    for r in el.iter(L + "CommentaryRef"):
        ref = r.get("Ref")
        if ref and ref not in ctx.refs:
            ctx.refs.append(ref)
    for a in ("CommentaryRef",):
        pass
    for x in el.iter():
        cr = x.get("CommentaryRef") if isinstance(x.tag, str) else None
        if cr and cr not in ctx.refs:
            ctx.refs.append(cr)

def table_md(tab):
    rows = []
    for tr in tab.iter("{http://www.w3.org/1999/xhtml}tr", L + "tr", "tr"):
        cells = [clean(inline(td)).replace("|", "/") for td in tr if local(td) in ("td", "th")]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)

BLOCK_P = {"P1": 0, "P2": 1, "P3": 2, "P4": 3, "P5": 4, "P6": 5}

def render_block(el, depth, out, quote=""):
    """Render block-level content under a provision."""
    for c in el:
        name = local(c)
        if not name:
            continue
        if name in ("P2", "P3", "P4", "P5", "P6"):
            num = nummark(clean(inline(c.find(L + "Pnumber")))) if c.find(L + "Pnumber") is not None else ""
            lvl = BLOCK_P[name] - 1
            mark = {"P2": f"({num})", "P3": f"({num})", "P4": f"({num})", "P5": f"({num})", "P6": f"({num})"}[name]
            sub = []
            render_block(c, depth + 1, sub, quote)
            body = "\n".join(sub).strip()
            ind = "  " * max(lvl, 0)
            if body:
                first, *rest = body.split("\n")
                out.append(f"{quote}{ind}{mark} {first.lstrip('> ').strip() if quote else first.strip()}")
                for r in rest:
                    out.append(r if r.startswith(quote) else f"{quote}{ind}  {r.strip()}")
            else:
                out.append(f"{quote}{ind}{mark}")
        elif name in ("Pnumber", "Title", "Number"):
            continue
        elif name == "Text":
            t = clean(inline(c))
            if t:
                out.append(quote + t)
        elif name in ("P1para", "P2para", "P3para", "P4para", "P5para", "P6para", "Para", "BlockText", "ListItem", "P", "Where"):
            render_block(c, depth, out, quote)
        elif name in ("UnorderedList", "OrderedList"):
            for i, li in enumerate([x for x in c if local(x) == "ListItem"], 1):
                sub = []
                render_block(li, depth + 1, sub, quote)
                t = " ".join(s.replace(quote, "", 1).strip() for s in sub if s.strip())
                out.append(f"{quote}- {t}" if name == "UnorderedList" else f"{quote}{i}. {t}")
        elif name == "Tabular":
            for tab in c.iter():
                if local(tab) == "table":
                    md = table_md(tab)
                    if md:
                        out.append("\n".join(quote + l for l in md.split("\n")))
                    break
        elif name == "BlockAmendment":
            sub = []
            render_block(c, depth, sub, quote + "> ")
            out.extend(sub)
        elif name in ("P1group", "P1"):
            # nested provisions inside block amendments
            title = c.find(L + "Title")
            if title is not None and clean(inline(title)):
                out.append(f"{quote}**{clean(inline(title))}**")
            if name == "P1group":
                render_block(c, depth, out, quote)
            else:
                num = c.find(L + "Pnumber")
                if num is not None:
                    out.append(f"{quote}**{clean(inline(num))}**")
                render_block(c, depth, out, quote)
        elif name in ("Pblock", "PsubBlock", "Part", "Chapter", "Schedule", "ScheduleBody"):
            title = c.find(L + "Title")
            numb = c.find(L + "Number")
            head = " ".join(x for x in [clean(inline(numb)) if numb is not None else "", clean(inline(title)) if title is not None else ""] if x)
            if head:
                out.append(f"{quote}**{head}**")
            render_block(c, depth, out, quote)
        elif name in ("Figure", "Image", "Formula"):
            out.append(quote + "[figure/formula — see legislation.gov.uk]")
        elif name in ("Commentaries", "Versions", "Resources", "Footnotes", "MarginNotes", "Reference"):
            continue
        else:
            render_block(c, depth, out, quote)

class Doc:
    def __init__(self, path, short, kind):
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()
        self.short = short
        self.kind = kind  # 'act' or 'si'
        md = self.root.find("ukm:Metadata", NS)
        self.title = clean(md.findtext("dc:title", namespaces=NS))
        self.uri = clean(md.findtext("dc:identifier", namespaces=NS))
        self.valid = clean(md.findtext("dct:valid", namespaces=NS)) or self.root.get("RestrictStartDate", "")
        self.modified = clean(md.findtext("dc:modified", namespaces=NS))
        self.comments = {}
        for cm in self.root.iter(L + "Commentary"):
            self.comments[cm.get("id")] = (cm.get("Type"), clean(inline_all(cm)))
        COMMENTS.clear(); COMMENTS.update(self.comments)
        self.unapplied = []
        for ue in md.iter("{%s}UnappliedEffect" % NS["ukm"]):
            self.unapplied.append({k: ue.get(k) for k in ("AffectedProvisions", "Type", "AffectingProvisions", "AffectingURI")} |
                                  {"affecting": clean("".join(ue.find("ukm:AffectingTitle", NS).itertext())) if ue.find("ukm:AffectingTitle", NS) is not None else "",
                                   "aprov": clean("".join(ue.find("ukm:AffectedProvisions", NS).itertext())) if ue.find("ukm:AffectedProvisions", NS) is not None else "",
                                   "gprov": clean("".join(ue.find("ukm:AffectingProvisions", NS).itertext())) if ue.find("ukm:AffectingProvisions", NS) is not None else "",
                                   "dates": " ".join(f"{d.get('Date','')} {d.get('Qualification','') or ''}".strip() for d in ue.iter("{%s}InForce" % NS["ukm"]))})

    def provision_label(self, in_schedule):
        if in_schedule:
            return "Paragraph"
        if self.kind == "act":
            return "Section"
        return "Rule" if "Rules" in self.title else ("Article" if "Order" in self.title else "Regulation")

    def render_provision(self, p1group_or_p1, crumbs, in_schedule):
        out = []
        ctx = Ctx(self.comments)
        collect_refs(p1group_or_p1, ctx)
        p1s = [p1group_or_p1] if local(p1group_or_p1) == "P1" else [x for x in p1group_or_p1 if local(x) == "P1"]
        title_el = p1group_or_p1.find(L + "Title") if local(p1group_or_p1) == "P1group" else None
        title = clean(inline(title_el)) if title_el is not None else ""
        if not p1s:
            # group without P1 (e.g. repealed) or text directly
            sub = []
            render_block(p1group_or_p1, 1, sub)
            body = "\n".join(sub).strip()
            if title or body:
                out.append(f"\n### {title or '(untitled)'}\n\n{body}\n")
            return out, ctx
        for p1 in p1s:
            num_el = p1.find(L + "Pnumber")
            num = nummark(clean(inline(num_el))) if num_el is not None else ""
            label = self.provision_label(in_schedule)
            uri = p1.get("DocumentURI", "")
            head = f"### {label} {num}" + (f" — {title.rstrip('.')}" if title else "")
            if "Prospective" in (p1group_or_p1.get("Status"), p1.get("Status")):
                head += " [PROSPECTIVE — not yet in force]"
            ext = p1group_or_p1.get("RestrictExtent") or p1.get("RestrictExtent") or ""
            sub = []
            render_block(p1, 1, sub)
            body = "\n".join(sub).strip()
            if not body or re.fullmatch(r"[.…\s]*", body):
                body = "*(Repealed or omitted — see annotations.)*"
            meta = []
            if uri:
                meta.append(f"[legislation.gov.uk]({uri})")
            if ext:
                meta.append(f"extent: {ext}")
            out.append(f"\n{head}\n{' · '.join(meta)}\n\n{body}\n")
        return out, ctx

    def annotations(self, ctx):
        lines = []
        for ref in ctx.refs:
            if ref in self.comments:
                typ, txt = self.comments[ref]
                if typ in ("F", "C", "I", "E", "X", "P") and txt:
                    lab = {"F": "Amendment", "C": "Modification", "I": "Commencement", "E": "Extent", "X": "Editorial", "P": "Subordinate legislation"}.get(typ, typ)
                    lines.append(f"- {lab}: {txt[:400]}")
        if lines:
            return "\n<details><summary>Annotations</summary>\n\n" + "\n".join(dict.fromkeys(lines)) + "\n\n</details>\n"
        return ""

    def walk(self, node, crumbs, in_schedule, out):
        for c in node:
            name = local(c)
            if name in ("Part", "Chapter", "Pblock", "PsubBlock", "ScheduleBody"):
                numb = c.find(L + "Number")
                title = c.find(L + "Title")
                head = " — ".join(x for x in [clean(inline(numb)) if numb is not None else "", clean(inline(title)) if title is not None else ""] if x)
                lvl = {"Part": 2, "Chapter": 2, "Pblock": 2, "PsubBlock": 2, "ScheduleBody": 2}[name]
                if head:
                    out.append(f"\n## {head}\n")
                self.walk(c, crumbs + ([head] if head else []), in_schedule, out)
            elif name in ("P1group", "P1"):
                parts, ctx = self.render_provision(c, crumbs, in_schedule)
                out.extend(parts)
                ann = self.annotations(ctx)
                if ann:
                    out.append(ann)
            elif name in ("Number", "Title", "Reference", "TitleBlock"):
                continue
            elif name in ("P", "Para", "Tabular"):
                sub = []
                render_block(etree.Element("wrap") if False else c, 1, sub) if name != "Tabular" else None
                if name == "Tabular":
                    for tab in c.iter():
                        if local(tab) == "table":
                            sub.append(table_md(tab)); break
                out.append("\n".join(sub))
            else:
                self.walk(c, crumbs, in_schedule, out)

    def units(self):
        """Yield (unit_title, element, in_schedule)."""
        body = self.root.find(".//l:Body", NS)
        if body is None:
            body = self.root.find(".//l:EUBody", NS)
        units = []
        if body is not None:
            parts = [c for c in body if local(c) in ("Part",)]
            if parts and self.kind == "act" or (parts and len(parts) > 1):
                loose = [c for c in body if local(c) not in ("Part",)]
                if loose:
                    units.append(("Preliminary provisions", loose, False))
                for p in body:
                    if local(p) == "Part":
                        n = clean(inline(p.find(L + "Number"))) if p.find(L + "Number") is not None else ""
                        t = clean(inline(p.find(L + "Title"))) if p.find(L + "Title") is not None else ""
                        units.append((f"{n} — {t}".strip(" —"), [p], False))
            else:
                units.append(("Main provisions", list(body), False))
        scheds = self.root.find(".//l:Schedules", NS)
        if scheds is not None:
            for s in scheds:
                if local(s) != "Schedule":
                    continue
                n = clean(inline(s.find(L + "Number"))) if s.find(L + "Number") is not None else "Schedule"
                t = ""
                tb = s.find(L + "TitleBlock")
                if tb is not None and tb.find(L + "Title") is not None:
                    t = clean(inline(tb.find(L + "Title")))
                units.append((f"{n} — {t}".strip(" —"), [s], True))
        return units

def inline_all(el):
    return " ".join(t for t in el.itertext())

def frontmatter(**kw):
    lines = ["---"]
    for k, v in kw.items():
        lines.append(f'{k}: "{str(v).replace(chr(34), chr(39))}"')
    return "\n".join(lines) + "\n---\n"

def convert(path, outdir, short, kind, max_units_merge=True, part_filter=None):
    d = Doc(path, short, kind)
    os.makedirs(outdir, exist_ok=True)
    units = d.units()
    if part_filter:
        units = [u for u in units if part_filter(u[0])]
    written = []
    # small instruments: one file
    total_size = os.path.getsize(path)
    single = total_size < 450_000 or len(units) <= 1
    chunks = []
    for title, els, in_sched in units:
        out = []
        for el in els:
            if local(el) in ("Part", "Schedule"):
                d.walk(el, [], in_sched, out)
            else:
                d.walk(_wrap(el), [], in_sched, out)
        text = "\n".join(out).strip()
        if text:
            chunks.append((title, text))
    head = lambda unit: frontmatter(source=d.title, unit=unit, uri=d.uri, valid_from=d.valid, retrieved="2026-11-03",
                                    licence="Open Government Licence v3.0 (Crown copyright)")
    note = (f"_Revised text as published on legislation.gov.uk (version valid from {d.valid}). "
            f"Check the annotations and the list of amendments not yet applied below: some changes made by later legislation "
            f"(notably the Employment Rights Act 2025) may not be reflected in the text yet._\n")
    if single:
        body = "\n\n".join(f"# {d.title} — {t}\n\n{x}" for t, x in chunks)
        fname = f"{short}.md"
        write(os.path.join(outdir, fname), head("whole instrument") + f"# {d.title}\n\n" + note + "\n" + body)
        written.append(fname)
    else:
        for i, (t, x) in enumerate(chunks, 1):
            fname = f"{short}_{i:02d}_{slug(t)}.md"
            write(os.path.join(outdir, fname), head(t) + f"# {d.title} — {t}\n\n" + note + "\n" + x)
            written.append(fname)
    # unapplied effects file
    if d.unapplied:
        lines = [frontmatter(source=d.title, unit="changes not yet applied", uri=d.uri),
                 f"# {d.title} — amendments not yet applied to the revised text\n",
                 "_List published by legislation.gov.uk of changes made by later legislation that are not yet incorporated in the revised text (often because they are not yet in force, or the editorial team has not yet processed them). Always check these before answering about the provisions listed._\n",
                 "| Provision affected | Type of effect | Made by | In force |", "|---|---|---|---|"]
        for u in d.unapplied:
            lines.append(f"| {u['aprov']} | {u.get('Type') or ''} | {u['affecting']} {u['gprov']} | {u['dates'] or 'not yet / see commencement'} |")
        fname = f"{short}_00_changes-not-yet-applied.md"
        write(os.path.join(outdir, fname), "\n".join(lines))
        written.append(fname)
    return d, written

def _wrap(el):
    w = etree.Element(L + "Wrap")
    w.append(_copy(el))
    return w

def _copy(el):
    import copy
    return copy.deepcopy(el)

def write(path, text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")

if __name__ == "__main__":
    path, outdir, short, kind = sys.argv[1:5]
    d, w = convert(path, outdir, short, kind)
    print(d.title, d.valid, len(w), "files")
