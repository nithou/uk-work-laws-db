import sys, re, os
sys.path.insert(0, "/home/claude/uk/scripts")
from clml2md import convert
OUT = "/home/claude/uk-employment-law-bot"
X = "/home/claude/uk/raw/xml/"
acts = [
 ("ukpga_1996_18", "era1996", "10-acts/employment-rights-act-1996"),
 ("ukpga_2025_36", "era2025", "10-acts/employment-rights-act-2025"),
 ("ukpga_2010_15", "eqa2010", "10-acts/equality-act-2010"),
 ("ukpga_1992_52", "tulrca1992", "10-acts/trade-union-labour-relations-consolidation-act-1992"),
 ("ukpga_1996_17", "eta1996", "10-acts/employment-tribunals-act-1996"),
 ("ukpga_1998_39", "nmwa1998", "10-acts/national-minimum-wage-act-1998"),
 ("ukpga_1999_26", "erela1999", "10-acts/employment-relations-act-1999"),
 ("ukpga_1974_37", "hswa1974", "10-acts/health-and-safety-at-work-act-1974"),
 ("ukpga_1997_40", "pha1997", "10-acts/protection-from-harassment-act-1997"),
 ("ukpga_2002_22", "ea2002", "10-acts/employment-act-2002"),
]
sis = [
 ("uksi_1998_1833", "wtr1998", "working-time-regulations-1998"),
 ("uksi_2006_246", "tupe2006", "tupe-regulations-2006"),
 ("uksi_2015_621", "nmwr2015", "national-minimum-wage-regulations-2015"),
 ("uksi_2024_1155", "etrules2024", "employment-tribunal-procedure-rules-2024"),
 ("uksi_2013_1237", "etconst2013", "employment-tribunals-constitution-regulations-2013"),
 ("uksi_2014_254", "earlyconc2014", "early-conciliation-regulations-2014"),
 ("uksi_1999_3312", "mpl1999", "maternity-and-parental-leave-regulations-1999"),
 ("uksi_2002_2788", "pal2002", "paternity-and-adoption-leave-regulations-2002"),
 ("uksi_2014_3050", "spl2014", "shared-parental-leave-regulations-2014"),
 ("uksi_2020_249", "pbl2020", "parental-bereavement-leave-regulations-2020"),
 ("uksi_2014_1398", "flex2014", "flexible-working-regulations-2014"),
 ("uksi_2000_1551", "ptw2000", "part-time-workers-regulations-2000"),
 ("uksi_2002_2034", "fte2002", "fixed-term-employees-regulations-2002"),
 ("uksi_2010_93", "awr2010", "agency-workers-regulations-2010"),
 ("uksi_2004_3426", "ice2004", "information-and-consultation-regulations-2004"),
 ("uksi_1982_894", "sspgen1982", "statutory-sick-pay-general-regulations-1982"),
 ("uksi_2024_251", "carers2024", "carers-leave-regulations-2024"),
 ("uksi_2025_375", "neonatal2025", "neonatal-care-leave-regulations-2025"),
 ("uksi_2026_310", "limits2026", "increase-of-limits-order-2026"),
 ("uksi_1977_500", "safetyreps1977", "safety-representatives-regulations-1977"),
 ("uksi_1996_1513", "hsconsult1996", "health-and-safety-consultation-regulations-1996"),
 ("uksi_2026_3", "era2025-comm1", "era-2025-commencement-regulations"),
 ("uksi_2026_323", "era2025-comm-2026-323", "era-2025-commencement-regulations"),
 ("uksi_2026_373", "era2025-comm-2026-373", "era-2025-commencement-regulations"),
 ("uksi_2026_559", "era2025-comm-2026-559", "era-2025-commencement-regulations"),
 ("uksi_2026_954", "era2025-comm-2026-954", "era-2025-commencement-regulations"),
 ("uksi_2026_1065", "era2025-comm-2026-1065", "era-2025-commencement-regulations"),
]
for f, short, d in acts:
    doc, w = convert(X + f + ".xml", os.path.join(OUT, d), short, "act")
    print(doc.title, doc.valid, len(w))
doc, w = convert(X + "ukpga_1992_4.xml", os.path.join(OUT, "10-acts/social-security-contributions-benefits-act-1992-ssp-smp"), "sscba1992", "act",
                 part_filter=lambda t: bool(re.match(r"Part (XI|XII)\b", t)) or t.startswith("Part XIIZ") or t.startswith("Part 12Z"))
print(doc.title, doc.valid, len(w))
for f, short, d in sis:
    doc, w = convert(X + f + ".xml", os.path.join(OUT, "11-regulations-and-rules", d), short, "si")
    print(doc.title, doc.valid, len(w))
