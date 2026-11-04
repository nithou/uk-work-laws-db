#!/usr/bin/env python3
import json, os, re, subprocess, time
from markdownify import markdownify as mdify

RAW = "/home/claude/uk/raw/govuk"
OUT = "/home/claude/uk-employment-law-bot/22-govuk-guidance"
SKIP_PATH = re.compile(r"(payroll-software|paye-online|running-payroll|pension|student-loan|tax-code|apprenticeship-levy|national-insurance-contribution|cis|childcare-vouchers|right-to-work-check|recruitment-agency|dbs|criminal-record|online-services|register-|business-rates|vat)")

def get(path):
    r = subprocess.run(["curl", "-sL", "-m", "60", "https://www.gov.uk/api/content" + path], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return None

def md(h):
    m = mdify(h or "", heading_style="ATX", bullets="-")
    m = re.sub(r"\]\(/", "](https://www.gov.uk/", m)
    return re.sub(r"\n{3,}", "\n\n", m).strip()

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:90]

def main():
    links = json.load(open(RAW + "/links.json"))
    os.makedirs(OUT, exist_ok=True)
    idx = []
    for path, (title, fmt, group) in sorted(links.items()):
        if fmt not in ("guide", "answer", "detailed_guide", "extra", "transaction", "simple_smart_answer"):
            continue
        if SKIP_PATH.search(path):
            continue
        d = get(path)
        time.sleep(0.3)
        if not d or "details" not in d:
            continue
        t = d.get("title", title)
        det = d["details"]
        parts = []
        if det.get("parts"):
            for p in det["parts"]:
                parts.append(f"## {p.get('title','')}\n\n" + md(p.get("body", "")))
        if det.get("body"):
            b = det["body"]
            if isinstance(b, list):
                b = " ".join(x.get("content", "") for x in b if isinstance(x, dict))
            parts.append(md(b))
        if det.get("introductory_paragraph"):
            parts.insert(0, md(det["introductory_paragraph"] if isinstance(det["introductory_paragraph"], str) else ""))
        if det.get("more_information"):
            parts.append(md(det["more_information"]))
        # publications: html attachments
        if fmt == "extra" and d.get("document_type") in ("guidance", "policy_paper", "statutory_guidance", "notice", "independent_report"):
            for a in det.get("attachments", []) or []:
                if a.get("attachment_type") == "html" and a.get("url"):
                    ap = a["url"].replace("https://www.gov.uk", "")
                    ad = get(ap)
                    if ad and ad.get("details", {}).get("body"):
                        parts.append(f"## {ad.get('title','')}\n\n" + md(ad["details"]["body"]))
        body = "\n\n".join(x for x in parts if x).strip()
        if len(body) < 300:
            continue
        updated = (d.get("public_updated_at") or "")[:10]
        url = "https://www.gov.uk" + path
        fm = f'---\nsource: "GOV.UK"\ntitle: "{t.replace(chr(34), chr(39))}"\nurl: "{url}"\nupdated: "{updated}"\nretrieved: "2026-11-03"\nlicence: "Open Government Licence v3.0"\n---\n'
        fn = slug(path.strip("/").replace("/", "-")) + ".md"
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            f.write(fm + f"# {t}\n\n_Source: GOV.UK — {url} — updated {updated}_\n\n" + body + "\n")
        idx.append((group, t, fn, updated))
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("# Index — GOV.UK employment guidance\n\n| Topic | Page | Updated |\n|---|---|---|\n" +
                "\n".join(f"| {g} | [{t}]({fn}) | {u} |" for g, t, fn, u in sorted(idx)) + "\n")
    print(len(idx))

main()
