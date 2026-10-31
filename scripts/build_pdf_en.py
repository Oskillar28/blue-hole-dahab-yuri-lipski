# -*- coding: utf-8 -*-
"""Genera el estudio ampliado en PDF (reportlab)."""
import sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, KeepTogether, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

FIG = sys.argv[1] if len(sys.argv) > 1 else "figs"
OUT = sys.argv[2] if len(sys.argv) > 2 else "estudio.pdf"
PHOTOS = sys.argv[3] if len(sys.argv) > 3 else None  # carpeta opcional con fotos reales

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", F + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", F + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DVS", F + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DVS-B", F + "DejaVuSerif-Bold.ttf"))
from reportlab.lib.fonts import addMapping
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B"); addMapping("DV", 0, 1, "DV-I"); addMapping("DV", 1, 1, "DV-BI")

DEEP = colors.HexColor("#0b3d5c"); ACC = colors.HexColor("#d64545"); INK = colors.HexColor("#1f2d3a")
SOFT = colors.HexColor("#eaf3f8"); LINE = colors.HexColor("#a9c3d3"); WARN = colors.HexColor("#f08a24")

ss = {
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.6, leading=13.6, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=5),
    "h1": ParagraphStyle("h1", fontName="DVS-B", fontSize=17, leading=21, textColor=DEEP, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=12, leading=15, textColor=DEEP, spaceBefore=9, spaceAfter=4),
    "h3": ParagraphStyle("h3", fontName="DV-B", fontSize=10.2, leading=13, textColor=INK, spaceBefore=6, spaceAfter=2),
    "part": ParagraphStyle("part", fontName="DVS-B", fontSize=24, leading=30, textColor=DEEP, alignment=TA_CENTER),
    "cap": ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=10.5, textColor=colors.HexColor("#4a5a68"), alignment=TA_CENTER, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8.2, leading=10.6, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=8.2, leading=10.6, textColor=colors.white),
    "bul": ParagraphStyle("bul", fontName="DV", fontSize=9.6, leading=13.4, leftIndent=14, bulletIndent=4, textColor=INK, spaceAfter=2),
    "note": ParagraphStyle("note", fontName="DV", fontSize=9, leading=12.6, textColor=INK),
    "toc1": ParagraphStyle("toc1", fontName="DV-B", fontSize=10, leading=15, textColor=DEEP),
    "toc2": ParagraphStyle("toc2", fontName="DV", fontSize=9, leading=12.5, leftIndent=14, textColor=INK),
}

story = []
def P(t, st="body"): story.append(Paragraph(t, ss[st]))
def H1(t): story.append(CondPageBreak(5 * cm)); p = Paragraph(t, ss["h1"]); p._toc = (0, t); story.append(p)
def H2(t): story.append(CondPageBreak(3.5 * cm)); p = Paragraph(t, ss["h2"]); p._toc = (1, t); story.append(p)
def H3(t): P(t, "h3")
def B(items):
    for it in items: story.append(Paragraph(it, ss["bul"], bulletText="•"))
    story.append(Spacer(1, 4))
def N(items):
    for i, it in enumerate(items, 1): story.append(Paragraph(it, ss["bul"], bulletText=f"{i}."))
    story.append(Spacer(1, 4))
def BOX(t, color=SOFT, edge=DEEP):
    tb = Table([[Paragraph(t, ss["note"])]], colWidths=[16.4 * cm])
    tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color), ("LINEBEFORE", (0, 0), (0, -1), 3, edge),
                            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(Spacer(1, 3)); story.append(tb); story.append(Spacer(1, 7))
def T(rows, widths, head=True):
    data = [[Paragraph(str(c), ss["cellb"] if (head and r == 0) else ss["cell"]) for c in row] for r, row in enumerate(rows)]
    tb = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if head else 0)
    sty = [("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if head: sty += [("BACKGROUND", (0, 0), (-1, 0), DEEP)]
    for r in range(1 if head else 0, len(rows)):
        if r % 2 == 0: sty.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f4f8fb")))
    tb.setStyle(TableStyle(sty)); story.append(tb); story.append(Spacer(1, 8))
def FIGURE(name, width_cm, cap, folder=None):
    path = os.path.join(folder or FIG, name)
    if not os.path.exists(path): return False
    w, h = PILImage.open(path).size
    W = width_cm * cm; H = W * h / w
    if H > 21 * cm: H = 21 * cm; W = H * w / h
    story.append(KeepTogether([Image(path, width=W, height=H), Paragraph(cap, ss["cap"])]))
    return True
def PHOTO(fname, width_cm, cap):
    """Inserta una foto real si existe en la carpeta de fotos."""
    if PHOTOS and os.path.exists(os.path.join(PHOTOS, fname)):
        FIGURE(fname, width_cm, cap, PHOTOS)

class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "_toc"):
            lvl, txt = f._toc
            key = "k%d" % id(f)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt.replace("<br/>", " "), key, level=lvl)
            self.notify("TOCEntry", (lvl, txt, self.page, key))

def deco(canv, doc):
    canv.saveState()
    if doc.page > 1:
        canv.setFont("DV", 7.5); canv.setFillColor(colors.HexColor("#6b7c8a"))
        canv.drawString(2.2 * cm, 1.2 * cm, "The Yuri Lipski Case and the Dahab Blue Hole · Extended study")
        canv.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"{doc.page}")
        canv.setStrokeColor(LINE); canv.line(2.2 * cm, 1.5 * cm, A4[0] - 2.2 * cm, 1.5 * cm)
    canv.restoreState()

doc = Doc(OUT, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
          title="The Yuri Lipski Case and the Dahab Blue Hole", author="Óscar Ramírez Martín",
          subject="Extended popular-science study: the place, the accident, diving physics and Tarek Omar")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=deco)])

# ======================= COVER =======================
story.append(Spacer(1, 1.2 * cm))
P("<font color='#d64545'>POPULAR-SCIENCE STUDY · EXTENDED EDITION</font>", "h3")
story.append(Paragraph("The Yuri Lipski Case<br/>and the Dahab Blue Hole", ParagraphStyle("t", fontName="DVS-B", fontSize=30, leading=36, textColor=DEEP)))
story.append(Spacer(1, 6))
story.append(Paragraph("The place, its marine life, the physics of an accident at 115 metres, and the man who goes down to bring back those who never return",
                       ParagraphStyle("st", fontName="DV", fontSize=13, leading=18, textColor=INK)))
story.append(Spacer(1, 0.6 * cm))
FIGURE("corte_blue_hole.png", 16, "Schematic cross-section of the Blue Hole (author's own illustration).")
story.append(Spacer(1, 0.4 * cm))
P("<b>Author:</b> Óscar Ramírez Martín &nbsp;&nbsp;·&nbsp;&nbsp; <b>Date:</b> 31 October 2026 &nbsp;&nbsp;·&nbsp;&nbsp; <b>Licence:</b> CC BY-SA 4.0")
BOX("<b>A note of respect.</b> This study deals with real deaths. It does not link to or reproduce Yuri Lipski's footage "
    "and contains no photographs of the victims. The aim is to understand <b>why</b> these accidents happen and "
    "<b>how</b> people work to recover those who do not come back, so that they are not repeated.")
story.append(PageBreak())

# ======================= CONTENTS =======================
P("Contents", "h1")
toc = TableOfContents(); toc.levelStyles = [ss["toc1"], ss["toc2"]]; toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ======================= 1. ORIGIN =======================
H1("1. Origin and purpose of the study")
P("The starting point is a clip from the Spanish podcast <b>The Wild Project</b> (Jordi Wild's channel), published on 30 October 2026 "
  "under the title <i>He Recorded His Own DEATH Underwater: The Terrifying Case of Yuri Lipski</i>. It is part of episode #389, "
  "a Halloween special on true horror stories with Iván from the <b>Gran Misterio</b> channel. The conversation mentions "
  "Tarek Omar, the Egyptian diver who recovered Lipski's body.")
P("A mystery podcast is built for impact. This study does the opposite: it checks every fact against several sources, separates "
  "what is verified from what is exaggerated, and explains the geography, ecology, physics and physiology behind the case. Every "
  "technical term is defined in the text and in the final glossary.")
H2("How to read this document")
B(["<b>Part I · The place:</b> where Dahab is, how the Red Sea formed, what the Blue Hole is and what marine life lives at each depth.",
   "<b>Part II · The accident:</b> what happened to Yuri Lipski, explained with numbers.",
   "<b>Part III · Tarek Omar:</b> who he is, what resources he uses to bring bodies to the surface and how a deep recovery should be done.",
   "<b>Part IV · Context:</b> other cases, myths, cross-checking of sources, glossary, lessons and sources.",
   "Uncertain facts carry a <b>confidence level</b> from 0.0 (unreliable) to 1.0 (verified)."])
BOX("<b>About the photographs.</b> The environment used to generate this PDF cannot download images from Wikimedia "
    "Commons, so the illustrations in this edition (maps, cross-sections, charts and diagrams) are the <b>author's own work</b>. "
    "At the end there is a <b>gallery of freely licensed photos</b> with their links, ready to be added to a future edition.",
    colors.HexColor("#fff4e5"), WARN)

H2("The case in 30 seconds")
T([["Fact", "Most reliable value", "Confidence"],
   ["Victim", "Yuri Lipski, 22, Russian-Israeli diving instructor", "0.9"],
   ["Date", "28 April 2000", "0.9"],
   ["Place", "Blue Hole, ~10 km north of Dahab (Sinai, Egypt), Gulf of Aqaba", "1.0"],
   ["Depth of the body", "~115 m (memorial plaque and Tarek Omar's account)", "0.85"],
   ["Gas and equipment", "Compressed air in a 12 L cylinder; ~12 kg of lead; helmet camera", "0.8"],
   ["Length of the footage", "About 7 minutes (7:16 according to Der Spiegel)", "0.85"],
   ["Recovery", "Tarek Omar, the next day, at the mother's request", "0.85"],
   ["Recreational diving limit", "40 m", "1.0"]], [4, 10.2, 2.2])
P("<b>In one sentence:</b> a young instructor went down alone, on air and with a single cylinder, to almost three times the "
  "recreational depth limit. At that depth air is narcotic, toxic and very hard to breathe all at once, and he could not come back.")

# ======================= PART I =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PART I<br/>The place", ss["part"])); story.append(PageBreak())

H1("2. The Red Sea: an ocean being born")
P("To understand the Blue Hole we have to start with the sea around it. The <b>Red Sea</b> is an arm of the Indian Ocean "
  "between Africa and the Arabian Peninsula. It connects to the ocean only in the south, through the "
  "<b>Bab el-Mandeb</b> strait and the Gulf of Aden. In the north it splits into two gulfs separated by the Sinai Peninsula: "
  "the <b>Gulf of Suez</b> to the west and the <b>Gulf of Aqaba</b> to the east. Dahab lies on the latter.")
FIGURE("mapa_mar_rojo.png", 11.5, "Figure 1. The Red Sea and the location of Dahab. Author's own illustration using Natural Earth coastline data (public domain).")
H2("Key facts")
T([["Feature", "Value", "What it means"],
   ["Length", "~2,250 km", "Roughly the distance from Barcelona to Moscow"],
   ["Maximum width", "~355 km", "A long, narrow sea"],
   ["Mean / maximum depth", "490 m / 2,730 m (Suakin Trough)", "Much deeper than it looks"],
   ["Salinity", "~36 ‰ in the south to ~41 ‰ in the north (mean ~40 ‰)", "One of the saltiest seas in the world (the Atlantic is about 35 ‰)"],
   ["Evaporation", "up to ~2,050 mm a year", "A lot of water evaporates and almost no fresh water flows in"],
   ["Surface temperature", "~26 °C in summer in the north, ~30 °C in the south", "Warm water all year round"],
   ["Rivers flowing in", "None of any size", "No sediment: very clear water"],
   ["Biodiversity", "more than 1,200 fish species (~10% endemic) and over 200 types of coral", "Endemic = found only here"]],
  [4, 5.6, 6.8])
H2("How it formed: a rift in progress")
P("The Red Sea exists because the <b>Arabian</b> plate is pulling away from the <b>African</b> plate. This process, called "
  "<b>rifting</b> (the crust fracturing and separating), began some 30–40 million years ago (Eocene–Oligocene) and is still "
  "going on: in 2005, after three weeks of tectonic activity in the Afar region, the rift opened by about 8 m in one go. "
  "Geologists regard it as an <b>ocean in the making</b>: in millions of years it could be as wide as the Atlantic.")
H2("Why is it called \"Red\"?")
P("There are two main explanations. The first is the seasonal blooms of a reddish cyanobacterium, "
  "<i>Trichodesmium erythraeum</i>, that tint the surface. The second is that in several ancient languages colours "
  "stood for the points of the compass and \"red\" meant south. Neither is fully proven (confidence 0.6).")

H1("3. The Gulf of Aqaba: a fault under the water")
P("The <b>Gulf of Aqaba</b> is the north-eastern arm of the Red Sea. Four countries border it: <b>Egypt</b> (the Sinai coast, "
  "with Taba, Nuweiba, Dahab and Sharm el-Sheikh), <b>Israel</b> (Eilat), <b>Jordan</b> (Aqaba) and <b>Saudi Arabia</b> (Haql). "
  "In the south it connects to the Red Sea through the <b>Strait of Tiran</b>.")
FIGURE("mapa_golfo_aqaba.png", 11, "Figure 2. The Gulf of Aqaba with Dahab and the Blue Hole. Author's own illustration using Natural Earth coastline data.")
T([["Feature", "Value"],
   ["Length", "~160–188 km depending on how it is measured"],
   ["Width", "~19–27 km"],
   ["Maximum depth", "~1,850 m (some sources give ~1,700 m)"],
   ["Geological origin", "Southern end of the <b>Dead Sea Transform</b>, a major strike-slip fault"],
   ["Deep basins", "Three <i>pull-apart</i> basins: Elat, Aragonese and Dakar"],
   ["Seismic activity", "The 1995 Gulf of Aqaba earthquake, caused by one of these fault segments"]], [5, 11.4])
H2("What this means")
P("A <b>transform fault</b> is a fracture where two blocks of crust slide sideways past each other, like two books rubbing "
  "along their spines. In the Gulf of Aqaba the fault is not one straight line but several stepped segments. Where one segment "
  "ends and the next begins, the crust is stretched and sinks, forming a <b>pull-apart basin</b>. That is why the gulf is so "
  "narrow and so deep, and why, a few metres off Dahab's shore, the seabed drops vertically for hundreds of metres.")
BOX("<b>Reasoning:</b> geology explains the Blue Hole's fame. In very few places in the world can you walk into the water "
    "from a beach, without a boat, and have 100 m of depth a few metres away in a calm sinkhole with no current. That ease of "
    "access is exactly what makes it dangerous.")
H2("Heat-resistant corals: the \"thermal refuge\"")
P("The Gulf of Aqaba has some of the northernmost and best-preserved coral reefs in the world. Scientists have shown that "
  "its corals withstand temperatures well above their summer maximum without <b>bleaching</b>. Bleaching happens when a "
  "heat-stressed coral expels the microalgae (<b>zooxanthellae</b>) living inside it that give it food and colour.")
P("The most accepted explanation, put forward by Maoz Fine and colleagues in 2013, is that the ancestors of these corals "
  "colonised the Red Sea after the last ice age by entering from the south, through Bab el-Mandeb, where the water is very "
  "warm. Only the most heat-tolerant survived. In the cooler north they now live far from their upper temperature limit, which "
  "is why the Gulf of Aqaba is described as a <b>thermal refuge</b> from climate change. A 2021 study (Bellworthy and Fine) adds "
  "a nuance: the same corals live close to their <b>cold</b> limit, so an unusually cold winter can also harm them.")
T([["Regional facts (Saudi Arabia, UNESCO tentative list, 2024)", "Value"],
   ["Coral species", "more than 265"], ["Fish species", "about 800"],
   ["Sharks and rays", "14 species, including the critically endangered Halavi guitarfish"],
   ["Others", "dugongs, green and hawksbill turtles, cetaceans and seabirds"],
   ["Recent discovery", "NEOM brine pools at ~1,770 m, discovered in 2020"]], [9, 7.4])

H1("4. Dahab: from fishing village to diving capital")
P("<b>Dahab</b> is a small town on the coast of South Sinai, about 80 km north-east of Sharm el-Sheikh. Its name means "
  "<b>\"gold\"</b> in Arabic, perhaps because of the colour of its sand. Some scholars identify it with the place called "
  "<i>Di-Zahav</i> (\"of gold\") in the biblical book of Deuteronomy.")
H2("Town facts")
T([["Aspect", "Detail"],
   ["Population", "~3,200 registered residents in 2023 (plus a floating population of workers and tourists)"],
   ["Districts", "Masbat (north, including the old Bedouin village of Asalah), Mashraba (centre-south) and Medina (south-west)"],
   ["Climate", "Hot desert: July highs ~35 °C, January highs ~21 °C. About 9 mm of rain a year"],
   ["Sea temperature", "~21–22 °C in winter and ~28–29 °C in late summer"],
   ["Economy", "Tourism, scuba diving, freediving, windsurfing and kitesurfing. Minerals in the rocks (rutile, zircon, gold)"],
   ["Dive centres", "About 52 registered in 2012, plus unlicensed schools"],
   ["Medical care", "Hyperbaric medical centre with a recompression chamber for six patients"]], [3.6, 12.8])
H2("A brief history")
B(["For centuries it was a fishing spot and a stopping place for the <b>Bedouin</b> of the Sinai.",
   "From <b>1967 to 1979</b> the Sinai was occupied by Israel. During that time Dahab (called <i>Di-Zahav</i>) began to attract "
   "travellers and divers, and the Blue Hole became famous.",
   "After the 1979 peace treaty the Sinai returned to Egypt. From the 1980s Dahab grew as a backpacker and diving destination, "
   "quieter and cheaper than Sharm el-Sheikh.",
   "In 2012, according to Der Spiegel, diving was a discount business: a beginners' course cost about €200 and a guided dive "
   "about €25."])
H2("Why people go to Dahab")
N(["<b>Shore access.</b> Almost every dive site is reached on foot from the beach, without a boat.",
   "<b>Warm, clear, calm water,</b> with visibility usually around 20–30 m.",
   "<b>Healthy reefs</b> at very shallow depths, ideal for snorkelling too.",
   "<b>Depth very close to shore,</b> which draws technical divers and freedivers from all over the world.",
   "<b>Famous sites:</b> the Blue Hole and The Bells, the Canyon, the Eel Garden, the Lighthouse and, further north, the "
   "Ras Abu Galum protected area.",
   "<b>Atmosphere:</b> relaxed, with Bedouin cafés at the water's edge and low prices."])

H1("5. The Blue Hole: anatomy of a sinkhole")
P("A <b>blue hole</b> is a <b>submarine sinkhole</b>: a vertical shaft in limestone or reef rock. Most formed during the ice "
  "ages, when sea level was up to about 120 m lower. Slightly acidic rainwater dissolved the rock and carved out cavities, "
  "which flooded when the sea rose again. From above it looks like a dark blue circle ringed by turquoise reef, because deep "
  "water absorbs every colour except blue.")
FIGURE("corte_blue_hole.png", 16, "Figure 2b. Schematic cross-section of the Blue Hole, showing the Arch, the depth limits and where some victims were found. Author's own illustration.")
T([["Feature", "Size", "Notes"],
   ["Diameter of the opening", "~70–80 m", "In the top of the reef"],
   ["Bottom of the sinkhole", "just over 100 m", "Sources give 94 to 130 m"],
   ["The Saddle", "~6–7 m", "Shallow opening to the sea, used by recreational divers"],
   ["The Arch", "ceiling at ~52–56 m", "Tunnel through the reef to the open sea"],
   ["Length of the Arch", "~26 m", "From inside it looks less than 10 m long"],
   ["Floor of the Arch", "from ~102 to ~120 m", "Slopes down towards the sea side"],
   ["Outside the Arch", "steps at 130, 150, 250, 300 and ~800 m", "No bottom to use as a reference"]], [4.4, 4, 8])
H2("Why the Arch is deceptive")
N(["<b>It is easy to overshoot.</b> The entrance is not in a straight line from the sinkhole. Divers who miss it keep descending to look for it, and below there is no reference.",
   "<b>It looks short.</b> With such clear water and a bright exit, the tunnel seems a few metres long, but it is 26 m.",
   "<b>A current often flows in</b> from the sea towards the sinkhole, forcing divers to swim against it and use more gas.",
   "<b>It is an overhead environment.</b> Inside, you cannot ascend vertically.",
   "<b>It sits right at the limit for air.</b> On air, oxygen becomes dangerous at around 56–57 m (see §8.3), exactly where the Arch ceiling is.",
   "<b>The light is deceptive.</b> At about 45 m light reappears through the tunnel, especially in the morning. It is a spectacle that lures people who should not be there."])
H2("History and legend")
P("According to Wikipedia, a group of Israeli divers led by Alex Shell was the first to dive it with modern equipment in "
  "1968 and saw the Arch. An Egyptian report (Masrawy, 2018) credits Israeli pilots who spotted it from a helicopter in 1962. "
  "The two versions can both be true: spotting it from the air and diving it for the first time are different things "
  "(confidence 0.6).")
P("Among the Bedouin there is a legend of a young woman who drowned herself in the sinkhole to avoid marrying a man she did "
  "not want, and whose spirit lures divers down. Tarek Omar, who knows the bottom better than anyone, rejects it: he says he "
  "has never seen anything supernatural and that the cause of the deaths is almost always the diver.")

H1("6. What marine life you will find")
P("People do not visit Dahab for the deep Blue Hole but for the <b>reef wall</b> between the surface and 30 m. That is where "
  "most of the life is. Light decides what lives at each depth: water absorbs red first (at about 5 m), then orange, yellow "
  "and green. Below ~40 m only blue remains and life that depends on light disappears.")
FIGURE("zonas_vida.png", 16, "Figure 3. What you see at each depth in Dahab and how colours fade. Author's own illustration.")
H2("Species that are easy to spot")
T([["Species (common name)", "Scientific name", "Depth", "How to recognise it and fun facts"],
   ["Anthias (sea goldie)", "<i>Pseudanthias squamipinnis</i>", "3–30 m", "Clouds of small orange and purple fish over the coral. Born female; some later turn male."],
   ["Napoleon wrasse", "<i>Cheilinus undulatus</i>", "5–60 m", "Can exceed 1.5 m. Blue-green with thick lips. Listed as Endangered by the IUCN."],
   ["Red Sea clownfish", "<i>Amphiprion bicinctus</i>", "1–30 m", "Lives protected among the tentacles of an anemone, which does not sting it."],
   ["Red Sea butterflyfish", "<i>Chaetodon paucifasciatus</i>", "2–30 m", "Endemic to the Red Sea and Gulf of Aden. Usually seen in pairs."],
   ["Sohal surgeonfish", "<i>Acanthurus sohal</i>", "0–10 m", "Blue and black stripes, territorial. Has a sharp \"blade\" near the tail."],
   ["Lionfish", "<i>Pterois miles</i>", "1–50 m", "Feather-like fins. Its spines are venomous: look, don't touch."],
   ["Stonefish", "<i>Synanceia verrucosa</i>", "0–30 m", "Camouflaged as a rock. One of the most venomous fish in the world."],
   ["Giant moray", "<i>Gymnothorax javanicus</i>", "1–50 m", "Opens and closes its mouth to breathe, not to threaten."],
   ["Blue-spotted ribbontail ray", "<i>Taeniura lymma</i>", "1–30 m", "On the sand between corals. Has a sting in its tail."],
   ["Hawksbill and green turtles", "<i>Eretmochelys imbricata</i>, <i>Chelonia mydas</i>", "1–40 m", "Hawksbills eat sponges; green turtles eat algae and seagrass. Both are threatened."],
   ["Garden eels", "<i>Gorgasia sillneri</i>", "10–40 m", "Hundreds of eels poking out of the sand (Eel Garden)."],
   ["Barracuda and trevally", "<i>Sphyraena</i>, <i>Caranx</i>", "open blue", "Predators patrolling in front of the wall."],
   ["Cleaner fish and shrimps", "<i>Labroides dimidiatus</i>, others", "5–30 m", "Remove parasites from other fish. There is a famous \"cleaning station\" at about 18 m."],
   ["Dugong (rare)", "<i>Dugong dugon</i>", "shallow seagrass", "Threatened herbivorous mammal. More often seen further south (Marsa Alam)."]],
  [3.4, 3.8, 1.9, 7.3])
H2("Corals and \"vegetation\"")
P("There are almost no plants on the reef. Most of what looks like vegetation is actually <b>animals</b> (corals and sponges) and algae:")
B(["<b>Hard corals</b> (<i>Acropora</i>, <i>Porites</i>, <i>Stylophora</i>): build the reef with calcium carbonate skeletons. They live in symbiosis with zooxanthellae, which photosynthesise.",
   "<b>Soft corals</b> (<i>Sarcophyton</i>, <i>Sinularia</i>): flexible and colourful, with no rigid skeleton.",
   "<b>Fire coral</b> (<i>Millepora</i>): not a true coral. It stings if touched.",
   "<b>Gorgonians</b> (sea fans) and <b>black coral</b>: more common on the deep wall (25–40 m).",
   "<b>Coralline algae</b>: cement the reef with a pink crust.",
   "<b>Seagrasses</b> (flowering plants such as <i>Halophila</i>): form meadows in shallow sandy areas and feed turtles and dugongs.",
   "<b>On land:</b> desert with acacias and date palms (<i>Phoenix dactylifera</i>) in oases and wadis."])
H2("The classic dive: The Bells → Blue Hole")
P("This is the safe, recommended way to see the Blue Hole. It is done from the shore and requires certification to 30 m (Advanced Open Water or equivalent):")
N(["Walk about 150 m from the Blue Hole to <b>The Bells</b>, a crack in the reef roughly 3 × 2 m.",
   "Descend through a vertical <b>chimney</b>, with light filtering through the gaps. The chimney narrows at about 23 m and you exit to the open sea through a window at 26–28 m. (The small arch at The Bells must not be confused with the Arch of the Blue Hole.)",
   "Follow the <b>wall</b> with the reef on your right, rising slowly. You will see black corals, overhangs covered in hard coral, anthias, lionfish and, at about 18 m, the cleaning station.",
   "After 35–45 minutes, rise to 7–12 m and cross <b>the Saddle</b> into the Blue Hole.",
   "Finish with your safety stop inside the sinkhole, where freedivers also train."])
H2("Water conditions")
T([["Parameter", "Typical value"],
   ["Water temperature", "~22 °C in January and ~29 °C in August (3–5 mm wetsuit in winter)"],
   ["Visibility", "Usually 20–30 m"],
   ["Current", "None or light inside the sinkhole; can be moderate on the wall and in the Arch"],
   ["Best season", "Spring and autumn: mild water and less heat on land"]], [4.5, 11.9])
BOX("<b>Rules for visitors:</b> do not touch or stand on the coral, do not feed the fish, control your buoyancy near the wall, "
    "do not collect shells or coral and use reef-safe sunscreen. Above all, do not go deeper than your certification allows.")

# ======================= PART II =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PART II<br/>Yuri Lipski's accident", ss["part"])); story.append(PageBreak())

H1("7. Who he was and what happened")
P("<b>Yuri Lipski</b> was a 22-year-old diving instructor of Russian origin living in Israel. He travelled to Dahab intending "
  "to dive the Blue Hole beyond the usual limits. According to Tarek Omar, who knew him, Lipski asked him to guide the dive. "
  "Omar warned him <b>twice</b> not to do it and suggested about two weeks of training first. Lipski said he did not have the "
  "time and found someone else to go with.")
BOX("<b>Reasoning:</b> \"instructor\" is not the same as \"technical diver\". A recreational instructor masters basic equipment "
    "down to 40 m. Going to 100 m requires different training, different gases and different equipment. Many Blue Hole accidents "
    "involve experienced divers who rely on that experience outside the range they were trained for.")
H2("Reconstructed timeline")
T([["When", "What happened", "Source / confidence"],
   ["Days before", "Omar advises him twice against the dive and offers to train him first", "The Guardian, CairoScene · 0.9"],
   ["Preparation", "He kits up with a 12 L cylinder of air, ~12 kg of lead on his belt and a helmet camera with batteries", "Der Spiegel (Omar) · 0.8"],
   ["Entry", "He starts filming as he enters the sinkhole; at first other divers are nearby", "Descriptions of the video · 0.8"],
   ["Descent", "He separates from the group and keeps going down alone, in the blue, out of control", "Wikipedia, Der Spiegel · 0.9"],
   ["Bottom", "His computer shows 81.7 m, then 85.3 m and 91.6 m as he touches bottom; he tries in vain to inflate his BCD and stirs up sand", "Der Spiegel · 0.8"],
   ["End", "The image freezes; the footage lasts about 7 minutes", "Der Spiegel · 0.85"],
   ["Next day", "Tarek Omar recovers the body at ~115 m, face down, together with the camera", "Wikipedia, Der Spiegel · 0.85"]], [2.6, 9.4, 4.4])
BOX("<b>An interesting discrepancy:</b> the wrist computer read about 92 m when he touched bottom, but the body was found at "
    "about 115 m. Possible explanations: the floor of the sinkhole is a slope of sand and debris, the body may have slid or been "
    "moved further down, or one source's figures are rounded. There is no way to know for sure (confidence 0.5).",
    colors.HexColor("#fff4e5"), WARN)
H2("What the footage shows")
P("(Description based on written sources; this study does not link to the video.) First come reef walls and other divers. "
  "Then only blue water and less and less light. The descent is continuous, with no stops. On reaching the bottom, sand clouds "
  "the image and his breathing speeds up sharply. There are attempts to inflate the BCD and, according to Wikipedia, he even "
  "removes the regulator from his mouth. In the end the camera faces the bottom and the image goes still. Several sources note "
  "that the tape does not clearly show the exact moment of death: the title \"he filmed his own death\" is a simplification.")

H1("8. Why he died: the physics of air at 115 m")
P("Nobody can know what was going through his mind. But diving physics lets us calculate <b>what the air was doing to him</b> "
  "at that depth. The calculations in this section are the author's own, using standard formulas, and were checked with a Python program.")
H2("8.1 Pressure (Boyle's law)")
P("In the sea, every 10 m of water adds 1 bar of pressure, on top of 1 bar from the atmosphere:")
P("<para alignment='center'><b>P<sub>absolute</sub> (bar) = 1 + depth (m) / 10</b></para>")
P("Under <b>Boyle's law</b>, the volume of a gas is inversely proportional to its pressure.")
T([["Depth", "Absolute pressure", "1 L of surface air takes up…", "Density of air"],
   ["0 m", "1 bar", "1 L", "1.2 g/L"], ["10 m", "2 bar", "0.5 L", "2.5 g/L"], ["40 m", "5 bar", "0.2 L", "6.1 g/L"],
   ["56 m", "6.6 bar", "0.15 L", "8.1 g/L"], ["<b>115 m</b>", "<b>12.5 bar</b>", "<b>0.08 L</b>", "<b>15.3 g/L</b>"]], [3.4, 3.6, 5, 4.4])
H2("8.2 Nitrogen narcosis")
P("Air is 79% nitrogen. Under <b>Dalton's law</b>, each gas in a mixture contributes its share of the total pressure (its "
  "<b>partial pressure</b>). Under <b>Henry's law</b>, the higher that partial pressure, the more gas dissolves in blood and "
  "tissue. At high pressure, dissolved nitrogen has an <b>anaesthetic</b> effect on neurons, similar to alcohol: euphoria, "
  "overconfidence, fixation, slowness and, at great depth, hallucinations and loss of consciousness. At 115 m the partial "
  "pressure of nitrogen is about <b>9.9 bar</b>, versus 0.79 bar at the surface.")
P("The informal <b>\"Martini's law\"</b> compares every 10 m below 20 m to drinking one martini. At 115 m that would be "
  "about <b>9–10 martinis</b>. Narcosis does not hurt or warn you: it removes exactly the ability to notice the danger. Its only "
  "remedy is to ascend, which is what Lipski could not do.")
H2("8.3 Oxygen toxicity")
P("Oxygen is <b>toxic</b> to the central nervous system when its partial pressure (ppO<sub>2</sub>) is too high. It can cause "
  "<b>convulsions without warning</b>, and underwater a convulsion almost always means losing the regulator and drowning. The "
  "recommended working limit is 1.4 bar and the contingency maximum is 1.6 bar. On air at 115 m: 0.21 × 12.5 ≈ "
  "<b>2.6 bar</b>, almost twice the maximum.")
P("The <b>maximum operating depth (MOD)</b> of air is 10 × (1.4 / 0.21 − 1) ≈ <b>56.7 m</b> (66 m at 1.6 bar). "
  "Der Spiegel puts the critical limit for air at 56 m, and the Arch begins at 52–56 m. <b>The Arch is exactly where air "
  "starts to become toxic.</b> Lipski was about 60 m deeper. Omar told Der Spiegel that the twitching seen in the video makes "
  "him think of oxygen poisoning.")
FIGURE("gases.png", 16, "Figure 4. Partial pressure of oxygen and gas density breathing air or trimix 10/70. Author's own calculation.")
H2("8.4 Gas density and carbon dioxide")
P("At 12.5 bar, air weighs about <b>15 g/L</b>. The recommendations of Anthony and Mitchell (2016) set a preferred maximum of "
  "<b>5.2 g/L</b> and an absolute limit of <b>6.2 g/L</b>; on air these are reached at about 32 and 41 m. Such a dense gas flows "
  "turbulently, takes great effort to move, and <b>CO<sub>2</sub> builds up</b> (<b>hypercapnia</b>). Excess "
  "CO<sub>2</sub> causes breathlessness and anxiety, <b>intensifies narcosis</b> and <b>brings oxygen toxicity on sooner</b>.")
BOX("<b>The vicious circle:</b> dense gas → CO<sub>2</sub> builds up → breathlessness and panic → faster breathing → more "
    "CO<sub>2</sub> and more gas used → more panic. This fits the rapid breathing described by those who have analysed the footage.")
H2("8.5 Gas consumption: the cylinder empties 12.5 times faster")
T([["Situation", "Surface consumption", "Consumption at 115 m", "Duration of 12 L at 200 bar (2,400 L)"],
   ["Relaxed", "20 L/min", "250 L/min", "≈ 9.6 min"], ["Effort or stress", "40 L/min", "500 L/min", "≈ 4.8 min"],
   ["Panic", "60 L/min", "750 L/min", "≈ 3.2 min"]], [3.6, 4, 3.6, 5.2])
P("Even with a full cylinder there was not enough gas for the <b>decompression stops</b> such a dive requires, nor even for a "
  "slow ascent. (Author's estimate: his personal consumption and actual cylinder pressure are unknown.)")
H2("8.6 Buoyancy: why he could not ascend")
N(["<b>Too much lead.</b> According to Omar, he wore about 12 kg of lead, plus the cylinder, the camera and the batteries.",
   "<b>Neoprene gets crushed.</b> A wetsuit floats thanks to gas bubbles inside it. At 12.5 bar those bubbles are compressed and the suit loses almost all its buoyancy.",
   "<b>Inflating the BCD takes a lot of gas.</b> Offsetting 12 kg requires 12 L of gas at 115 m, about 150 surface litres taken from a cylinder that was already emptying fast.",
   "<b>A procedural error.</b> Omar explains that the BCD burst because it was already full when Lipski tried to pump more air into it. Under narcosis and panic it is typical to fixate on a single action instead of dropping the weights."])
BOX("<b>The opposite trap:</b> had he dropped his weights, he would have shot up uncontrollably from 115 m, with a very high "
    "risk of severe <b>decompression sickness</b> or <b>pulmonary barotrauma</b>. At that depth and with that equipment there "
    "was no safe way out. The decisive error was made <b>before he entered the water</b>.")
H1("9. The chain of errors")
P("Safety science uses the <b>Swiss cheese model</b>: an accident almost never has a single cause. It happens when the holes "
  "in several layers of protection line up.")
FIGURE("cadena_errores.png", 16, "Figure 5. The chain of errors behind the accident. Author's own illustration.")
T([["Link", "Verified?", "Confidence"],
   ["He rejected an expert's advice and training", "Yes (Omar in The Guardian and CairoScene)", "0.9"],
   ["Air in a single 12 L cylinder", "Yes (Omar in Der Spiegel; Wikipedia assumes it)", "0.85"],
   ["Uncontrolled descent", "Yes (footage and depth of the body)", "0.9"],
   ["~12 kg of lead", "Omar's direct testimony in Der Spiegel", "0.8"],
   ["Severe narcosis", "Physically unavoidable at that depth", "0.95"],
   ["Oxygen toxicity as a direct cause", "Possible (Omar's view); cannot be proven", "0.55"],
   ["CO<sub>2</sub> build-up", "Very likely given the gas density", "0.8"]], [7.4, 6.8, 2.2])

# ======================= PART III =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PART III<br/>Tarek Omar,<br/>the man who goes down for them", ss["part"])); story.append(PageBreak())

H1("10. Who Tarek Omar is")
P("In The Wild Project video he is presented as Lipski's buddy or guide. That is an important nuance: according to every "
  "source, <b>Tarek Omar did not dive with Lipski</b>. He was the local expert who advised him against the dive and who, the "
  "next day, went down to recover his body at the family's request.")
H2("Profile")
T([["Aspect", "Fact", "Source / confidence"],
   ["Name", "Tarek Omar (in the Egyptian press, Tarek Omar El-Masry)", "Several · 0.9"],
   ["Origin", "Bedouin of the Aulad Ali tribe, born in a village near the Libyan border", "Der Spiegel 2012 · 0.8"],
   ["Age", "47 in 2012 and 52 in 2016–2018, so born around 1965–1966", "Der Spiegel, Masrawy, Al-Masry Al-Youm · 0.7"],
   ["Arrival in Dahab", "1989, looking for work", "Der Spiegel · 0.8"],
   ["Start in diving", "Learned to dive in 1992 and worked as an instructor from 1995; the Egyptian press dates his work at the Blue Hole from 1994", "Der Spiegel, Masrawy · 0.7"],
   ["First recoveries", "November 1997: the Irish divers Conor O'Regan and Martin Gara, found in each other's arms at 102 m", "Der Spiegel · 0.9"],
   ["Local depth record", "209 m according to Der Spiegel (2012); 220 m according to Al-Masry Al-Youm (2016)", "0.6"],
   ["School", "Opened the first technical diving centre in Dahab", "Der Spiegel · 0.8"],
   ["Nicknames", "\"Sheikh of the divers\", \"King of the Blue Hole\", \"Giant of the depths\", \"the bone collector\", \"The Elder Diver\"", "Egyptian and international press · 0.9"],
   ["Bodies recovered", "He says he lost count. Other sources say more than 20 (The Chronicle) or 9 (Masrawy)", "0.5"],
   ["Fee", "He charges nothing for recoveries; he only asks for the cost of the gas", "Der Spiegel · 0.8"]], [3.6, 8.6, 4.2])
H2("His role in the Lipski case")
B(["He had met Lipski twice and described him as very reckless. He advised him to train first; Lipski replied that he did not have time.",
   "He recovered the body at about 115 m, face down, together with the camera.",
   "The camera was rated to about 75 m and yet it still worked. They played it in front of the mother when she asked him to help take the equipment apart.",
   "Omar has said he regrets that the mother will forever have those images and that, had he known the footage existed, he would have destroyed the tape.",
   "The father, Alexander Lipski, sent him a certificate written in five languages thanking him for the dangerous mission of recovering his son."])
H2("What he thinks of the Blue Hole")
B(["For him, the Blue Hole is one of the most beautiful dives in the world and there is nothing supernatural about it.",
   "Its danger is psychological: <b>it looks easy</b> (warm water, no current, good visibility, entry from the beach), so people underestimate it.",
   "He compares what happens there to the crowds on Everest: unprepared people chasing a number.",
   "He criticises those who party until the early hours and then dive the Blue Hole in the morning in search of \"the magic 100\" on their computer.",
   "He insists that diving the Arch requires <b>trimix</b>, not air, to reduce the \"martini effect\"."])

H1("11. How he recovers bodies: his method")
P("In his interview with Der Spiegel (2012), Omar explained step by step how he works. It is summarised here in our own words, "
  "with a technical explanation of each step.")
T([["Step", "What Omar does", "Why (technical explanation)"],
   ["1. Investigate", "Asks what equipment the dead diver had: wetsuit thickness, amount of lead, type of cylinder", "With this he estimates the body's buoyancy and where it may have drifted. A body does not fall straight down like a stone."],
   ["2. Last known point", "Asks the buddy where and at what depth the diver was last seen", "Narrows the search area. This is the \"last known point\" of any search protocol."],
   ["3. Warn", "His team tells the tourists that a body is about to be recovered and asks them to keep away from whatever comes to the surface", "Safety, and respect for the victim and the family."],
   ["4. Drift", "When he reaches the area, he lets himself drift as a lifeless body would", "Reproduces the most likely path along the relief and slope of the bottom."],
   ["5. Secure", "Most bodies lie between 100 and 120 m. He holds the body in his arms or ties it to himself", "At that depth he has only about <b>5 minutes</b> of bottom time."],
   ["6. Ascend to 40 m", "Rises with the body", "Controlled ascent: he does need to decompress."],
   ["7. Lift bag", "At about 40 m, once he can see the surface, he sends the body up with a lift bag", "The dead diver needs no decompression. Omar frees himself of the weight and can do his stops safely."],
   ["8. Decompress", "Stays underwater for up to about 3 hours", "Long decompression stops after a very deep dive. By the time he surfaces, the body is already ashore."],
   ["Time frame", "Tries to recover the body within 2–3 days and never more than 7", "The family wants a burial; after that the body deteriorates and it is better left where it is."]],
  [2.6, 6.4, 7.4])
FIGURE("perfil_recuperacion.png", 16, "Figure 6. Illustrative profile of a recovery at ~110 m, based on Omar's description. Times are approximate.")
H2("Resources and equipment needed")
T([["Resource", "What it is for"],
   ["Trimix as bottom gas (O<sub>2</sub> + helium + N<sub>2</sub>)", "Helium replaces part of the nitrogen (less narcosis) and of the oxygen (no toxicity). Omar mentions it explicitly."],
   ["Decompression gases (rich nitrox and pure O<sub>2</sub>)", "Speed up the elimination of inert gas during the stops. Each cylinder is marked with its maximum depth."],
   ["Twin cylinders, stages or a <b>rebreather</b>", "Carry enough gas plus a reserve. A rebreather recycles gas and allows much longer dives."],
   ["Multi-gas dive computer", "Calculates the real decompression with gas switches."],
   ["Lift bag and surface marker buoy", "Send the body up independently and mark the position at the surface."],
   ["Lines, reel and cutter", "Descent guide, securing the body, and a way out if someone gets entangled."],
   ["Body bag or cover", "Respect for the victim and preservation of evidence."],
   ["Surface team", "Lookout, communication, first aid, oxygen and receiving the body."],
   ["Hyperbaric chamber", "Dahab has a hyperbaric centre with a chamber for six patients. In 2012 its director complained that it was about 30 minutes by dirt road from the Blue Hole and that there was no ambulance on site."],
   ["Authorities", "Police and family: each recovery has to be reported and documented."]], [5.6, 10.8])

H1("12. How a deep recovery should be done")
P("Tarek Omar is an exceptional case: a diver with thousands of hours in that particular sinkhole. His method works in his "
  "hands, but it carries risks that best practice tries to reduce. The golden rule of any rescue team is <b>never create more "
  "victims</b>: a body can no longer be saved, but the diver searching for it can.")
H2("Principles of best practice")
N(["<b>Decide whether it is worth it.</b> Recovering a body is a risky operation with no life to save. The decision is made with the family and the authorities. Sometimes the right choice is not to go down, and the family may prefer the remains to stay in the sea.",
   "<b>Planning and roles.</b> Before entering the water, roles are assigned: recovery diver, support divers at the stops, surface supervisor and communications.",
   "<b>The right gases</b> (trimix and decompression gases), <b>with reserves</b>: the rule of thirds or more conservative gas plans.",
   "<b>A methodical search.</b> Start from the last known point and use search patterns (U-shaped, circular or parallel lines) with reference lines.",
   "<b>Controlled ascent of the body.</b> The lift bag is sized for the weight to be raised. Because of Boyle's law, a bag filled at 40 m (5 bar) expands fivefold by the time it reaches the surface, so it must be released away from the diver and never clipped to him.",
   "<b>Avoid entanglement.</b> Short, tidy lines, a cutter always at hand and nothing dangling loose.",
   "<b>Support during decompression.</b> Support divers with extra gas at the stops and a hyperbaric chamber on standby.",
   "<b>Respect and documentation.</b> Treat the body with dignity, keep the equipment for the investigation and hand it over to the authorities.",
   "<b>Look after the recovery diver.</b> These missions leave psychological scars; Omar admits the Lipski case still haunts him."])
H2("A tragic lesson: Dave Shaw (South Africa, 2005)")
P("The case of <b>Dave Shaw</b> shows what can go wrong. In January 2005 he tried to recover the body of Deon Dreyer, a diver "
  "who died in 1994 in the flooded cave of <b>Boesmansgat</b> (South Africa), at <b>270 m</b>. He used a rebreather and several "
  "trimix blends, and carried a camera to film the operation. Several things went wrong at once:")
B(["Contrary to expectations, Dreyer's body floated, because inside his drysuit it had turned into <b>adipocere</b>, a light, soap-like substance.",
   "Working with both hands, Shaw could not position his torch cable as he normally did, and the lines of the body bag became entangled with it.",
   "The effort of freeing himself, breathing very dense gas at that depth, caused respiratory failure (CO<sub>2</sub> build-up) and he died.",
   "His friend and support diver, <b>Don Shirley</b>, nearly died too and was left with permanent balance problems.",
   "Three days later, as the team was retrieving their lines, both bodies came up entangled almost to the surface."])
BOX("<b>Lessons from the Shaw case for any recovery:</b> the state of the body can be surprising, lines are a deadly hazard, "
    "physical effort at depth drives CO<sub>2</sub> up, and there must always be a plan to abort the mission. Compared with "
    "this, Omar's method of freeing himself from the body at 40 m with a lift bag is a sensible way to cut the time spent carrying it.")
H2("Comparison: Omar's method versus the ideal protocol")
T([["Aspect", "Omar's method (2012)", "Recommended protocol"],
   ["Team", "Alone on the bottom; team at the surface", "Main diver plus support at depth and at the stops"],
   ["Bottom time", "~5 minutes", "As short as possible, planned with a margin"],
   ["Raising the body", "Carries it to 40 m and sends it up with a lift bag", "The same, with a properly sized bag released away from the diver"],
   ["Decompression", "Up to ~3 h", "With reserve gas, support and a hyperbaric chamber on standby"],
   ["Knowledge of the site", "Exceptional: his own sinkhole for 30 years", "Prior reconnaissance is essential"],
   ["Main risk", "An incident while alone at over 100 m", "Reduced by redundancy of people and gas"]], [3.8, 6, 6.6])

# ======================= PART IV =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PART IV<br/>Context and conclusions", ss["part"])); story.append(PageBreak())

H1("13. The \"divers' cemetery\"")
P("Next to the Blue Hole there are plaques set into the rock in memory of divers who died. In 2012 Der Spiegel counted 14. "
  "<b>There is no official record</b> and the figures vary widely:")
T([["Source", "Figure", "Period"],
   ["Tarek Omar in Der Spiegel (2012)", "more than 130", "1997–2012 (about 8 a year)"],
   ["Local community and travel press", "up to 200", "\"in recent years\""],
   ["Undercurrent (2017)", "at least 40 scuba divers", "since 1980"],
   ["Plaques on the shore (2012)", "14", "Only victims with a plaque"]], [6.4, 5, 5])
P("The prudent statement is <b>\"more than a hundred, with no official figure\"</b>. The higher figures probably include "
  "snorkellers who drowned for reasons unrelated to the Arch.")
H2("Other documented cases")
T([["Year", "Person", "What happened"],
   ["1997", "Conor O'Regan and Martin Gara (Ireland, 22 and 23)", "Found in each other's arms at 102 m. One began to sink, the other went to help, and both lost consciousness."],
   ["2000", "Yuri Lipski (22)", "The case in this study, at ~115 m."],
   ["2011", "Igor Shalo (Russia)", "Technical diver with about 400 dives. He went to 150 m with little decompression experience, got into breathing trouble at 130 m and ascended without stopping. He died on his 401st dive."],
   ["2017", "Stephen Keenan (Ireland, 39)", "Freediving safety diver. He died after rescuing champion Alessia Zecchini in the Arch. The story is told in the Netflix documentary <i>The Deepest Breath</i> (2023)."]], [1.4, 5, 10])
BOX("<b>Lesson from the Shalo case:</b> technical divers die too. He did not descend vertically to his planned depth, hit the "
    "bottom at 120 m (first mistake), carried on to 150 m swimming over the bottom (second mistake, which cost him strength, time "
    "and gas) and, when he felt he was suffocating, ascended without making his stops. Discipline matters as much as equipment.")

H1("14. How the Arch is dived safely")
T([["What Lipski did", "What a technical diver does"],
   ["Air (21% O<sub>2</sub>, 79% N<sub>2</sub>)", "Trimix: less nitrogen (less narcosis) and less oxygen (no toxicity)"],
   ["A single cylinder", "Twin back-mounted cylinders plus stage and decompression cylinders"],
   ["No gas plan", "Planning with reserves (rule of thirds)"],
   ["Alone", "As a team, with an agreed plan and signals"],
   ["Free descent in the blue", "Controlled descent with a guideline and depth reference"],
   ["No decompression", "Stops planned with a computer or tables"],
   ["Recreational certification", "Technical certification (Tech 60 or higher) and progressive experience"]], [6, 10.4])
H2("Air versus trimix at 115 m (author's calculation)")
T([["Parameter at 115 m", "Air", "Trimix 10/70", "Comment"],
   ["ppO<sub>2</sub>", "2.62 bar", "1.25 bar", "Trimix stays below 1.4 bar"],
   ["Equivalent narcotic depth (END)", "115 m", "~22 m", "On trimix, narcosis is like being at about 22 m on air"],
   ["Gas density", "15.3 g/L", "~6.5 g/L", "Even trimix is at the limit, which is why deeper dives use more helium or rebreathers"]],
  [5.2, 2.6, 2.8, 5.8])
P("<b>END</b> (equivalent narcotic depth) is the depth on air that produces the same narcosis as a given mix. For trimix 10/70, "
  "which is 20% nitrogen: ppN<sub>2</sub> = 0.20 × 12.5 = 2.5 bar; on air, that happens at (2.5 / 0.79 − 1) × 10 ≈ 22 m.")

H1("15. Myths versus reality")
T([["Myth", "Reality", "Confidence"],
   ["\"There is something supernatural about the Blue Hole\"", "Omar, who knows every corner, denies it: the causes are human and physical", "0.95"],
   ["\"Tarek was his dive buddy\"", "He did not dive with him: he advised against the dive and later recovered the body", "0.9"],
   ["\"He filmed the exact moment of his death\"", "He filmed the descent and his final minutes; the moment of death is not clearly visible", "0.7"],
   ["\"He was a beginner\"", "He was an instructor, but not a technical diver", "0.9"],
   ["\"He was carrying an oxygen tank\"", "He was breathing compressed air. Pure oxygen would be lethal at that depth", "0.85"],
   ["\"He simply ran out of air\"", "Most likely a combination of narcosis, CO<sub>2</sub>, toxic oxygen, too much lead and panic", "0.75"],
   ["\"The Blue Hole is the most dangerous place in the world\"", "The sinkhole is an ordinary dive site; the danger is the Arch below 50 m", "0.9"],
   ["\"200 people have died there\"", "There is no official record; estimates range from 40 to 200", "0.8"],
   ["\"An eel attacks him at the end of the video\"", "Theory posted on GitHub in 2019 with no confirmation; probably pareidolia", "0.9 that it is false"]], [5, 9, 2.4])

H1("16. Cross-checking sources")
T([["Fact", "Version A", "Version B", "Conclusion"],
   ["Date", "28/04/2000 (Wikipedia, plaque)", "08/04/2000 (blog)", "28 April"],
   ["Depth", "115 m (body, Omar)", "91.6 m (computer in the video) / 111 m", "Touched bottom at about 92 m; the body was at ~115 m"],
   ["Arch ceiling", "52 m (Der Spiegel)", "55–56 m (Wikipedia)", "52–56 m depending on where it is measured"],
   ["Discovery", "1968, Alex Shell's divers", "1962, pilots in a helicopter", "Aerial sighting and first dive; both can be true"],
   ["Omar's record", "209 m", "220 m", "More than 200 m"],
   ["Bodies recovered by Omar", "\"Lost count\" / more than 20", "9", "No reliable figure"],
   ["Who asked for the recovery", "The mother", "The father (blog)", "The mother asked; the father thanked him"],
   ["Total deaths", "more than 130 in 15 years", "40 / 200", "More than 100, no official record"]], [3.2, 4.4, 4.4, 4.4])

H1("17. Technical glossary")
T([["Term", "Meaning"],
   ["Adipocere", "A fatty, soap-like substance that forms in bodies left for a long time in cold water. It can make them float."],
   ["Arch", "~26 m tunnel joining the Blue Hole to the open sea, with its ceiling at 52–56 m."],
   ["bar", "Unit of pressure. 1 bar is roughly atmospheric pressure at sea level."],
   ["BCD (buoyancy compensator)", "Vest inflated with gas from the cylinder to adjust buoyancy."],
   ["Blue hole", "Submarine sinkhole: a vertical shaft in limestone or reef, flooded when the sea rose."],
   ["Boyle's law", "At constant temperature, the volume of a gas is inversely proportional to its pressure."],
   ["Coral bleaching", "Loss of a coral's microalgae (zooxanthellae) through heat stress. The coral turns white and may die."],
   ["CO<sub>2</sub> / hypercapnia", "Excess carbon dioxide in the blood: breathlessness, anxiety, confusion and loss of consciousness."],
   ["Dalton's law", "The total pressure of a mixture is the sum of the partial pressures of each gas."],
   ["Decompression", "Stops during the ascent to eliminate dissolved gas without it forming bubbles."],
   ["Decompression sickness (DCS)", "Injury from gas bubbles in blood and tissue after ascending too fast."],
   ["END", "Equivalent narcotic depth: the depth on air that produces the same narcosis as a given mix."],
   ["Endemic", "Found only in a particular region."],
   ["Freediving", "Diving on a single held breath, without a cylinder."],
   ["Gas density", "Mass per litre of breathing gas. It rises with depth and makes breathing harder."],
   ["Helium", "Inert, light gas with almost no narcotic effect. Replaces nitrogen in deep mixes."],
   ["Henry's law", "The amount of gas dissolved in a liquid is proportional to its partial pressure."],
   ["Hyperbaric chamber", "Pressurised chamber used to treat decompression sickness with oxygen under pressure."],
   ["Lift bag", "Bag filled with gas underwater to raise objects or bodies."],
   ["\"Martini's law\"", "Informal rule: one martini's worth of narcosis for every 10 m below 20 m."],
   ["Mesophotic", "Low-light zone, roughly from 30–40 m down to 150 m."],
   ["MOD", "Maximum operating depth: where the ppO<sub>2</sub> of a mix exceeds the safe limit."],
   ["Nitrogen narcosis", "Anaesthetic effect of nitrogen at high pressure. Similar to drunkenness; it disappears on ascent."],
   ["Neoprene", "Wetsuit material containing gas bubbles; it compresses with depth."],
   ["Nitrox", "Air enriched with more than 21% oxygen, useful at moderate depths."],
   ["Overhead environment", "A place where you cannot ascend vertically: caves, wrecks, tunnels."],
   ["Oxygen toxicity (CNS)", "Toxic effect of O<sub>2</sub> above ~1.4–1.6 bar; it can cause convulsions."],
   ["Pareidolia", "The tendency to see familiar shapes in blurry images."],
   ["Partial pressure (ppO<sub>2</sub>, ppN<sub>2</sub>)", "The share of the total pressure due to one gas in the mix."],
   ["Pull-apart basin", "Depression formed where a strike-slip fault steps over and the crust is stretched."],
   ["Pulmonary barotrauma", "Lung rupture from ascending while holding your breath."],
   ["Rebreather (closed circuit)", "Equipment that recycles exhaled gas, removes CO<sub>2</sub> and adds oxygen."],
   ["Regulator", "Device that reduces cylinder pressure to ambient pressure so you can breathe."],
   ["Rift", "Zone where the crust fractures and separates; it can eventually form an ocean."],
   ["SAC", "Surface air consumption: gas used per minute expressed in surface litres."],
   ["Saddle", "Shallow opening (~6 m) from the Blue Hole to the sea."],
   ["Salinity (‰)", "Grams of salt per kilogram of water. The Red Sea is about 40 ‰."],
   ["Sinkhole", "Shaft or depression formed by the dissolution of limestone."],
   ["Tech 60", "Technical diving certification level for dives to 60 m."],
   ["Thermal refuge", "Area where corals withstand warming better than elsewhere."],
   ["Transform fault", "Fracture in the crust where two blocks slide sideways past each other."],
   ["Trimix", "A mix of oxygen, helium and nitrogen for deep dives."],
   ["Zooxanthellae", "Microalgae living inside coral that feed it through photosynthesis."]], [5, 11.4])

H1("18. Lessons for any diver")
N(["<b>Dive within your training</b>, not your ego.",
   "<b>Never go deep alone</b>, least of all in an overhead environment or where there is no bottom.",
   "<b>Air has limits:</b> because of oxygen, at around 56–66 m; because of gas density, already at around 32–41 m.",
   "<b>Narcosis gives no warning.</b> If something feels wrong, ascend a few metres.",
   "<b>Weight yourself correctly:</b> too much lead turns any problem into an emergency.",
   "<b>Listen to local experts.</b> Lipski was warned twice.",
   "<b>Plan your gas</b> with reserves for the unexpected.",
   "<b>A site's fame is not a reason to dive it.</b>",
   "<b>Respect the reef:</b> what makes Dahab special is between 0 and 30 m."])

H1("19. Method, limitations and confidence")
B(["The topic was broken down into parts (place, ecology, accident, physics, recovery, context) and every fact was checked against at least two independent sources wherever possible.",
   "Sources in English, German (translated), Arabic and Spanish were consulted.",
   "The calculations (pressure, ppO<sub>2</sub>, MOD, END, density, consumption and buoyancy) are the author's own and were checked with a program.",
   "The illustrations are the author's own work. The maps use Natural Earth coastline data (public domain).",
   "All the text is original writing. Sources are cited at the end and no paragraphs are copied from any of them.",
   "<b>Limitations:</b> neither The Wild Project video nor the original footage could be viewed; no autopsy has been published; several figures about Tarek Omar differ between sources."])
T([["Block", "Confidence"],
   ["Geography, geology and ecology", "0.9"], ["Basic facts of the accident", "0.9"], ["Physics and physiology (calculations)", "0.95"],
   ["Exact sequence of the accident", "0.65"], ["Specific cause of death", "0.6 (multifactorial, unconfirmed)"],
   ["Biography of Tarek Omar", "0.75"], ["Omar's recovery method", "0.8"], ["Death toll", "0.5"]], [10, 6.4])

H1("20. Sources")
src = [
 "Wikipedia. <i>Blue Hole (Red Sea)</i>. https://en.wikipedia.org/wiki/Blue_Hole_(Red_Sea)",
 "Grossekathöfer, M. (13/07/2012). <i>The Blue Hole in the Red Sea Is the Deadliest Dive Site in the World</i>. Der Spiegel International. https://www.spiegel.de/international/zeitgeist/the-blue-hole-in-the-red-sea-is-the-deadliest-dive-site-in-the-world-a-844099.html",
 "Ghoneim, N. (20/10/2016). <i>Egyptian Diver Tarek Omar: The Keeper of Dahab's Divers' Cemetery</i>. CairoScene. https://cairoscene.com/lifestyle/egyptian-diver-tarek-omar-the-keeper-of-dahab-s-divers-cemetery",
 "Bower, E. (26/08/2017). <i>Top diver's death casts long shadow over deep beauty of the Blue Hole</i>. The Guardian. https://www.theguardian.com/world/2017/aug/26/blue-hole-red-sea-diver-death-stephen-keenan-dahab-egypt",
 "Al-Masry Al-Youm (14/10/2016). Report on Tarek Omar, \"Giant of the depths\" (in Arabic). https://www.almasryalyoum.com/news/details/1592981",
 "Masrawy (29/09/2018). Report on the \"Sheikh of the divers\" of Dahab (in Arabic). https://www.masrawy.com/news/news_regions/details/2018/9/29/1435938",
 "Atlas Obscura / Slate (04/03/2014). <i>Diver's cemetery: the Blue Hole of Dahab</i>. https://www.slate.com/blogs/atlas_obscura/2014/03/04/diver_s_cemetery_the_blue_hole_of_dahab_on_the_red_sea_in_egypt.html",
 "Wikipedia. <i>Red Sea</i>, <i>Gulf of Aqaba</i>, <i>Dahab</i>, <i>Nitrogen narcosis</i>, <i>Dave Shaw</i>, <i>Stephen Keenan</i>.",
 "UNESCO. <i>Coral Reefs of the Gulf of Aqaba and the Red Sea in the Kingdom of Saudi Arabia</i> (tentative list, 2024). https://whc.unesco.org/en/tentativelists/6701/",
 "Bellworthy, J. and Fine, M. (2021). <i>Warming resistant corals from the Gulf of Aqaba live close to their cold-water bleaching threshold</i>. PeerJ 9:e11100. https://pmc.ncbi.nlm.nih.gov/articles/PMC8005291/",
 "Marine Insight. <i>Gulf of Aqaba facts</i>. https://www.marineinsight.com/gulf-of-aqaba-facts/",
 "Circle Divers. <i>Bells – Blue Hole dive site</i>. https://www.circledivers.com/diving-in-dahab/dive-sites/bells-blue-hole-dive-site-dahab",
 "Dive Planner Pro. <i>Blue Hole Dahab</i>. https://www.diveplannerpro.com/spots/eg/dahab/blue-hole-dahab-eg",
 "WorkSafe New Zealand. <i>Breathing oxygen and enriched mixtures while diving</i>.",
 "TDI. <i>Avoid CNS Oxygen Toxicity While Diving Nitrox</i>.",
 "DDRC Healthcare. <i>Gas Density and SCUBA</i> (summarising Anthony and Mitchell, 2016). https://www.ddrc.org/gas-density-and-scuba/",
 "Dressel Divers (2025). <i>Underwater Recovery at the Limit</i>. https://www.dresseldivers.com/blog/underwater-recovery/",
 "Undercurrent (2017). <i>Dangerous dive site</i>. Showcaves.com. <i>Blue Hole, Dahab</i>.",
 "The Wild Project (30/10/2026). <i>He Recorded His Own DEATH Underwater</i> (clip from episode #389). https://www.youtube.com/watch?v=qArQMyX28PA",
 "Natural Earth / world-atlas (coastline data for the maps, public domain).",
]
for s_ in src: story.append(Paragraph(s_, ss["bul"], bulletText="•"))

H1("21. Gallery of freely licensed photos")
P("These Wikimedia Commons photos carry free licences (CC BY, CC BY-SA or public domain) and can be included in a future "
  "edition with attribution. Each link leads to the page with the exact author and licence.")
gal = [
 ["View of the Blue Hole from the shore", "Gustavo Gerdel · CC BY-SA 4.0", "File:Dahab_Blue_Hole.jpg"],
 ["The Blue Hole from above", "Petar Milošević · CC BY-SA 4.0", "File:Blue_Whole,_Dahab.jpg"],
 ["Plan of the Blue Hole", "Usellermann · CC BY-SA 3.0 / GFDL", "File:Blue_Hole_map.png"],
 ["Technical diver under the Arch (2009)", "Tommi Salminen · CC BY-SA 3.0", "File:Dahab_Blue_Hole_Arc_2009.jpg"],
 ["Memorial plaques", "D T G · CC BY 3.0", "File:EGYPT_Dahab_Blue_Hole_memorials.JPG"],
 ["Freedivers in the Blue Hole (2006)", "Lars Plougmann · CC BY-SA 2.0", "File:Blue_Hole_Sinai-Free_Diving.jpg"],
 ["Diver at the top of The Bells", "See page", "File:Diver_at_the_Top_of_The_Bells.jpg"],
 ["Dahab beach", "See page", "File:Dahab_Beach.jpg"],
 ["Dahab shoreline", "See page", "File:Dahab_shoreline.jpg"],
 ["Dahab panorama", "See page", "File:Dahab_panorama.jpg"],
 ["Dahab from the air", "See page", "File:Dahab_from_airplane.jpg"],
 ["Eel Garden", "See page", "File:Dahab_-_Eel_Garden.jpg"],
 ["Green turtle in Dahab", "Hatem Moushir · see page", "File:Chelonia_mydas_at_Dahab_by_Hatem_Moushir.jpg"],
 ["Napoleon wrasse in the Red Sea", "See page", "File:Napoleon_(Cheilinus_undulatus)_im_Roten_Meer._DSCF1669WI.jpg"],
 ["Lionfish in the Red Sea", "See page", "File:Lion_fish_in_the_red_sea.jpg"],
 ["Anthias", "See page", "File:Anthia_goldfish.JPG"],
 ["Endemic butterflyfish", "See page", "File:Crown_Butterflyfish,_Chaetodon_paucifasciatus,_Red_Sea_(36204827650).jpg"],
 ["Blue-spotted ray", "See page", "File:Blue_spotted_stingray_in_the_red_sea.jpg"],
 ["Gulf of Eilat coral reef", "See page", "File:Gulf_of_Eilat_(Red_Sea)_coral_reefs.jpg"],
 ["Trimix diver at 108 m", "Reginestein / A. Hache · CC BY-SA 3.0", "File:Plongeur_Trimix.jpg"],
 ["Buoyancy compensator", "Mark.murphy · public domain", "File:Bcd_-_stab.JPG"],
]
T([["Photo", "Author and licence", "Page at commons.wikimedia.org/wiki/…"]] + gal, [5.2, 4.6, 6.6])
P("<i>This document: original text and illustrations under the CC BY-SA 4.0 licence. Spanish edition available in the same repository.</i>")
story.append(Spacer(1, 1 * cm))
P("<para alignment='center'><i>In memory of those who never came back from the Blue Hole.</i></para>")

doc.multiBuild(story)
print("PDF:", OUT)
