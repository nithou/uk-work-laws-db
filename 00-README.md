---
type: "master index"
corpus_date: "3 November 2026"
jurisdiction: "Great Britain (England, Wales, Scotland) — Northern Ireland excluded"
---

# Knowledge base — UK employment law bot (workers and workplace representatives)

Corpus built on 3 November 2026 for a bot (Claude project, RAG, vector index). All files are UTF-8 Markdown with a YAML header (source, URL, validity date) and one heading per section/regulation for clean chunking.

## Structure

| Folder | Content | Nature | Currency |
|---|---|---|---|
| `01-SYSTEM-PROMPT.md` | Instructions for the bot | Written | 11/2026 |
| `02-METHOD.md` | Sources hierarchy, employment status, Scotland, how to reason | Written | 11/2026 |
| `10-acts/` | **Full revised text** of 10 Acts: Employment Rights Act 1996, **Employment Rights Act 2025**, Equality Act 2010, TULRCA 1992, Employment Tribunals Act 1996, National Minimum Wage Act 1998, Employment Relations Act 1999, HSWA 1974, Protection from Harassment Act 1997, Employment Act 2002; SSCBA 1992 Parts XI–XII (SSP, SMP) | Official text (legislation.gov.uk) | Revised to 30 Oct 2026 for the main Acts |
| `11-regulations-and-rules/` | 32 statutory instruments: Working Time Regs, TUPE, NMW Regs, **Employment Tribunal Procedure Rules 2024**, early conciliation rules, family leave regs (maternity, paternity, adoption, shared parental, bereavement, neonatal, carer's), flexible working, part-time/fixed-term/agency workers, ICE Regs, SSP Regs, safety reps, **Increase of Limits Order 2026**, all ERA 2025 commencement regulations | Official text | Revised/made versions as at 11/2026 |
| `20-acas-codes-of-practice/` | Statutory Acas Codes: disciplinary & grievance, flexible working, time off for trade union duties, disclosure of information for collective bargaining, settlement agreements | Official | 11/2026 |
| `21-acas-advice/` | ~620 Acas advice pages (dismissal, redundancy, discrimination, pay, leave, early conciliation, representatives…) | Official guidance | 11/2026 |
| `22-govuk-guidance/` | ~135 GOV.UK guides (rights at work, pay, time off, dismissal, tribunals, trade unions) | Official guidance | 11/2026 |
| `40-guides/` | Practical guides from the worker's side: unfair dismissal, constructive dismissal, redundancy, discrimination & harassment, whistleblowing, pay & holiday, sickness, family leave & flexible working, contract changes & TUPE, settlement agreements, time limits, calculations | Written | 11/2026 |
| `50-tribunal/` | Early conciliation, ET1, case management, hearing, remedies, appeals; preparing a claim | Written | 11/2026 |
| `60-representatives/` | Guide for trade union reps, employee reps, health & safety reps, ICE, collective consultation, recognition and industrial action | Written | 11/2026 |
| `70-case-law/` | Leading cases by topic | Written | 11/2026 |
| `80-templates/` | Letters: grievance, appeal, flexible working, subject access, without prejudice, reps | Written | 11/2026 |
| `90-key-figures-and-era-2025-tracker.md` | 2026/27 rates and limits; Employment Rights Act 2025 implementation tracker | Written | 3 Nov 2026 |

## Source priority for the bot

1. Legislation (`10-`, `11-`) — authoritative. Watch the markers: `⟦still in force, to be replaced: …⟧` (old wording still applying for most purposes), `⟦partly in force / prospective: …⟧` (new wording in force only for limited purposes or not yet), `[PROSPECTIVE — not yet in force]`, and each Act's `_00_changes-not-yet-applied.md` file.
2. Statutory Codes (`20-`): tribunals must take them into account; failure to follow the Acas disciplinary and grievance Code can change awards by up to 25%.
3. Official guidance (`21-`, `22-`): accurate and current, but simplified.
4. Written guides (`40-` to `90-`): method and synthesis; if they conflict with legislation, the legislation wins.

## Origin and licence

- Legislation: legislation.gov.uk (The National Archives), Crown copyright, Open Government Licence v3.0.
- Acas and GOV.UK content: Crown copyright, Open Government Licence v3.0.
- Written guides: prepared for this corpus.

## Known limits

- **Northern Ireland** has separate legislation (Employment Rights (NI) Order 1996, Industrial Tribunals, Labour Relations Agency): not covered.
- **Employment Rights Act 2025** is being phased in until 2027 and beyond. The revised texts include changes in force up to 30 October 2026; later changes appear as prospective or as "changes not yet applied". See the tracker in `90-…`.
- **EHRC Employment Statutory Code of Practice** and the EHRC technical guidance on sexual harassment could not be downloaded (site blocks automated access): consult equalityhumanrights.com.
- **Case law**: summaries of leading cases only. For full judgments: Find Case Law (caselaw.nationalarchives.gov.uk) and BAILII. The Find Case Law licence restricts bulk computational use, hence no bulk import.
- Rates change every April: check `90-…` and GOV.UK for later dates.

## Updating

Scripts in `99-update-tools/` regenerate folders 10, 11, 20, 21 and 22 from legislation.gov.uk (`/data.xml` endpoints), the Acas sitemap and the GOV.UK Content API. Re-run each April and after each ERA 2025 commencement order.
