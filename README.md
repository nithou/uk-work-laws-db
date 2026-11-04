# UK Employment Law Knowledge Base

A curated, plain-Markdown corpus of **Great Britain** employment law (England, Wales, Scotland), built for LLM assistants that advise **workers and workplace representatives** — not employers. The point is a bot that can cite "section 111(2) ERA 1996" and be right, instead of paraphrasing whatever a search engine surfaced.

**Snapshot:** 3 November 2026 · 1,015 files · ~12 MB · 10 Acts + SSCBA 1992 (SSP/SMP extracts) + 22 statutory instruments · 1,686 statutory sections. Detailed inventory: [`00-README.md`](00-README.md).

> Not legal advice. This is source material for a bot; a human makes the call.

## Why a corpus and not a web search

- **Stable, citable text.** Full revised text from legislation.gov.uk, one heading per section, so chunking is deterministic and every chunk maps back to a section number.
- **Dates in the YAML header** (`valid_from`, `retrieved`, `uri`) let the bot say which version it is quoting.
- **Prospective changes are marked, never silently applied.** Look for `⟦still in force, to be replaced: …⟧`, `⟦partly in force / prospective: …⟧`, `[PROSPECTIVE — not yet in force]`, and one `_00_changes-not-yet-applied.md` per Act. The Employment Rights Act 2025 is being phased in until 2027 and beyond: a bot that ignores the phase-in answers confidently and wrongly.
- **The hierarchy is written down** (legislation > statutory Code > official guidance > written synthesis) in [`02-METHOD.md`](02-METHOD.md), so the bot has a tie-break rule instead of vibes.

## Contents

| Folder | Files | Content | Nature |
|---|---|---|---|
| `01-SYSTEM-PROMPT.md` | 1 | Bot instructions | Written |
| `02-METHOD.md` | 1 | Source hierarchy, employment status, Scotland, reasoning method | Written |
| `10-acts/` | 168 | Revised full text: ERA 1996, **ERA 2025**, EqA 2010, TULRCA 1992, ETA 1996, NMWA 1998, ERelsA 1999, HSWA 1974, PHA 1997, EA 2002, SSCBA 1992 (Parts XI–XII) | Official |
| `11-regulations-and-rules/` | 54 | 22 SIs: Working Time, TUPE, NMW, **ET Procedure Rules 2024**, early conciliation, family leave, flexible working, part-time/fixed-term/agency, ICE, SSP, safety reps, **Increase of Limits Order 2026**, ERA 2025 commencement regs | Official |
| `20-acas-codes-of-practice/` | 11 | The five statutory Acas Codes | Official |
| `21-acas-advice/` | 620 | Acas advice pages (dismissal, redundancy, discrimination, pay, leave, early conciliation…) | Official guidance |
| `22-govuk-guidance/` | 136 | GOV.UK guides (rights at work, pay, time off, tribunals, unions) | Official guidance |
| `40-guides/` | 11 | Worker-side guides: unfair/constructive dismissal, redundancy, discrimination, whistleblowing, pay & holiday, sickness, family leave, TUPE & contract changes, settlement, time limits, calculations | Written |
| `50-tribunal/` | 2 | Early conciliation, ET1, case management, hearing, remedies, appeals | Written |
| `60-representatives/` | 1 | Union reps, employee reps, H&S reps, ICE, collective consultation, recognition, industrial action | Written |
| `70-case-law/` | 1 | Leading cases by topic | Written |
| `80-templates/` | 1 | Grievance, appeal, flexible working, SAR, without prejudice, rep letters | Written |
| `90-key-figures-and-era-2025-tracker.md` | 1 | 2026/27 rates and limits; ERA 2025 implementation tracker | Written |
| `99-update-tools/` | 6 | Scripts that regenerate folders 10, 11, 20, 21, 22 | Tooling |

## File format

Every official-text file opens with a YAML header and uses one heading per unit of law:

```yaml
---
source: "Employment Rights Act 1996"
unit: "Part X — Unfair dismissal"
uri: "http://www.legislation.gov.uk/ukpga/1996/18"
valid_from: "2026-10-30"
retrieved: "2026-11-03"
licence: "Open Government Licence v3.0 (Crown copyright)"
---
```

then `## Chapter …`, `### Section 94 — The right`, with a legislation.gov.uk deep link per section and extent markers (`E+W+S`). Chunk on `###`; keep the YAML as retrievable metadata so the bot can filter by Act, part and version date.

## Using it with a bot

1. Paste [`01-SYSTEM-PROMPT.md`](01-SYSTEM-PROMPT.md) as the system prompt and [`02-METHOD.md`](02-METHOD.md) as method reference.
2. Index the corpus (folder 10/11 first, then 20, then the rest). Chunk at heading level; never split a subsection from its section heading.
3. Require section-level citations and let `90-key-figures-and-era-2025-tracker.md` arbitrate rates.
4. Pair it with a live MCP server for anything time-sensitive — see below.

## MCP servers

The corpus is a fixed snapshot. Legal text is not. Two remote MCP servers close the gap at answer time, and both are public and unauthenticated:

| Server | Endpoint | What it adds |
|---|---|---|
| `openlaw` — `openlaw-mcp` 0.2.0 | `https://openlawmcp.legalaispace.com/v1/mcp` | legislation.gov.uk lookups **as of a date**, Find Case Law search/fetch, citator, OSCOLA formatting, plus ECHR (HUDOC), EU (Cellar), FCA Handbook, ICO, HMRC manuals |
| `lex` — `Lex API` 3.2.0 | `https://lex.lab.i.ai.gov.uk/mcp` | Semantic search over legislation.gov.uk (Acts and SIs), full text, amendment trails, explanatory notes |

Both speak Streamable HTTP (JSON-RPC 2.0, protocol 2025-06-18) and need no key. `openlaw` self-limits at 600 requests/minute.

### Tools worth wiring into the bot

**openlaw**
- `lookup_statute` — in-force provision, with `as_of` (YYYY-MM-DD) for "what did the law say on the dismissal date"
- `legislation_toc` — table of contents of an Act or SI
- `search_caselaw`, `fetch_judgment`, `grep_judgment` — Find Case Law (E&W courts and tribunals from 2001)
- `citator_lite` — judgments citing a neutral citation
- `parse_citation`, `format_oscola` — citation hygiene
- Cross-border: `fetch_eurlex` (CELEX), `fetch_hudoc` (ECtHR), `search_fca_handbook`, `search_ico_guidance`, `fetch_hmrc_manual`

**lex**
- `search_for_legislation_sections` — text search inside sections (the precise one)
- `search_for_legislation_acts`, `lookup_legislation` (e.g. `ukpga/2018/12`)
- `get_legislation_sections`, `get_legislation_full_text`
- `search_amendments`, `search_explanatory_note`, `get_explanatory_note_by_section`
- `health_check_healthcheck_get`

### Division of labour

| Question | Answer from |
|---|---|
| "What does section 111 ERA 1996 say?" | corpus — fast, no rate limit, already chunked |
| "Was it still in force on 3 February 2026?" | `openlaw.lookup_statute` with `as_of` |
| "What changed since 30 October 2026?" | `lex.search_amendments` + the Act's `_00-changes-not-yet-applied.md` |
| "Is there a judgment on this?" | `openlaw.search_caselaw` |
| "What is the 2026/27 cap?" | `90-key-figures-and-era-2025-tracker.md`, verified against GOV.UK |

### Configuration

Claude Desktop and other clients that support remote HTTP servers:

```json
{
  "mcpServers": {
    "openlaw": { "url": "https://openlawmcp.legalaispace.com/v1/mcp" },
    "lex":     { "url": "https://lex.lab.i.ai.gov.uk/mcp" }
  }
}
```

Hermes Agent (`~/.hermes/config.yaml`):

```yaml
mcp_servers:
  openlaw:
    url: https://openlawmcp.legalaispace.com/v1/mcp
    timeout: 180
    connect_timeout: 30
  lex:
    url: https://lex.lab.i.ai.gov.uk/mcp
    timeout: 180
    connect_timeout: 30
```

Clients that only speak stdio can bridge it: `npx -y mcp-remote https://openlawmcp.legalaispace.com/v1/mcp`.

## Coverage and known limits

- **Northern Ireland excluded** — separate legislation (Employment Rights (NI) Order 1996, Industrial Tribunals, LRA).
- **Scotland**: employment law is reserved, so the Acts apply; Scottish procedure and tribunals differ in places — flagged in `02-METHOD.md`.
- **ERA 2025 phase-in** runs to 2027 and beyond. Text is revised to 30 October 2026; later changes appear as prospective or as "changes not yet applied". Track them in `90-…`.
- **EHRC codes** (Employment Code of Practice, sexual harassment technical guidance) could not be scraped — consult equalityhumanrights.com.
- **Case law is summaries only.** Full judgments: Find Case Law (`caselaw.nationalarchives.gov.uk`, restricted bulk use) and BAILII. That is exactly what the MCP servers are for.
- **Rates change every April** — verify before quoting a figure.

## Updating

`99-update-tools/` regenerates the official-text folders from source: legislation.gov.uk `/data.xml` endpoints, the Acas sitemap, the GOV.UK Content API. Re-run every April (new rates) and after each ERA 2025 commencement order. See [`99-update-tools/README.md`](99-update-tools/README.md).

## Licence and attribution

- Legislation: legislation.gov.uk, The National Archives — Crown copyright, [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- Acas and GOV.UK content: Crown copyright, OGL v3.0.
- Written guides (`40-` to `90-`): original, published here under the same OGL terms.
- MCP servers are third-party services with their own terms; this repo only documents how to use them.

Corpus assembled to power a private French-language assistant ("Guy Fawkes"); extracted here for reuse. Corrections welcome as issues — with a source.
