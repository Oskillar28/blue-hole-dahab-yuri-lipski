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
        canv.drawString(2.2 * cm, 1.2 * cm, "El caso Yuri Lipski y el Blue Hole de Dahab · Estudio ampliado")
        canv.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"{doc.page}")
        canv.setStrokeColor(LINE); canv.line(2.2 * cm, 1.5 * cm, A4[0] - 2.2 * cm, 1.5 * cm)
    canv.restoreState()

doc = Doc(OUT, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
          title="El caso Yuri Lipski y el Blue Hole de Dahab", author="Óscar Ramírez Martín",
          subject="Estudio divulgativo ampliado: lugar, accidente, física del buceo y Tarek Omar")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=deco)])

# ======================= PORTADA =======================
story.append(Spacer(1, 1.2 * cm))
P("<font color='#d64545'>ESTUDIO DIVULGATIVO · EDICIÓN AMPLIADA</font>", "h3")
story.append(Paragraph("El caso Yuri Lipski<br/>y el Blue Hole de Dahab", ParagraphStyle("t", fontName="DVS-B", fontSize=30, leading=36, textColor=DEEP)))
story.append(Spacer(1, 6))
story.append(Paragraph("El lugar, su vida marina, la física de un accidente a 115 metros y el hombre que baja a buscar a los que no vuelven",
                       ParagraphStyle("st", fontName="DV", fontSize=13, leading=18, textColor=INK)))
story.append(Spacer(1, 0.6 * cm))
FIGURE("corte_blue_hole.png", 16, "Corte esquemático del Blue Hole (ilustración propia).")
story.append(Spacer(1, 0.4 * cm))
P("<b>Autor:</b> Óscar Ramírez Martín &nbsp;&nbsp;·&nbsp;&nbsp; <b>Fecha:</b> 31 de octubre de 2026 &nbsp;&nbsp;·&nbsp;&nbsp; <b>Licencia:</b> CC BY-SA 4.0")
BOX("<b>Nota de respeto.</b> Este estudio trata muertes reales. No enlaza ni reproduce la grabación de Yuri Lipski "
    "y no incluye fotografías de las víctimas. El objetivo es entender <b>por qué</b> ocurren estos accidentes y "
    "<b>cómo</b> se trabaja para recuperar a quienes no vuelven, para que no se repitan.")
story.append(PageBreak())

# ======================= ÍNDICE =======================
P("Índice", "h1")
toc = TableOfContents(); toc.levelStyles = [ss["toc1"], ss["toc2"]]; toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ======================= 1. ORIGEN =======================
H1("1. Origen y propósito del estudio")
P("El punto de partida es un clip del pódcast <b>The Wild Project</b> (canal de Jordi Wild), publicado el 30 de octubre de 2026 "
  "con el título <i>He Recorded His Own DEATH Underwater: The Terrifying Case of Yuri Lipski</i>. Forma parte del episodio #389, "
  "un especial de Halloween sobre casos reales de terror con Iván, del canal <b>Gran Misterio</b>. En la conversación aparece "
  "Tarek Omar, el buceador egipcio que recuperó el cuerpo de Lipski.")
P("Un pódcast de misterio busca impacto. Este estudio hace lo contrario: comprueba cada dato en varias fuentes, separa lo "
  "verificado de lo exagerado y explica la geografía, la ecología, la física y la fisiología que hay detrás. Cada término "
  "técnico se define en el texto y en el glosario final.")
H2("Cómo leer este documento")
B(["<b>Parte I · El lugar:</b> dónde está Dahab, cómo se formó el mar Rojo, qué es el Blue Hole y qué vida marina hay a cada profundidad.",
   "<b>Parte II · El accidente:</b> qué le pasó a Yuri Lipski, explicado con números.",
   "<b>Parte III · Tarek Omar:</b> quién es, qué recursos usa para subir los cuerpos y cómo debería hacerse una recuperación profunda.",
   "<b>Parte IV · Contexto:</b> otros casos, mitos, contraste de fuentes, glosario, lecciones y fuentes.",
   "Junto a los datos dudosos aparece un <b>nivel de confianza</b> de 0,0 (nada fiable) a 1,0 (comprobado)."])
BOX("<b>Sobre las fotografías.</b> El entorno donde se ha generado este PDF no permite descargar imágenes de Wikimedia "
    "Commons. Por eso las ilustraciones de esta edición (mapas, cortes, gráficas y esquemas) son <b>de elaboración propia</b>. "
    "Al final hay una <b>galería de fotos con licencia libre</b> con sus enlaces, lista para incorporarlas a una siguiente edición.",
    colors.HexColor("#fff4e5"), WARN)

H2("El caso en 30 segundos")
T([["Dato", "Valor más fiable", "Confianza"],
   ["Víctima", "Yuri Lipski, 22 años, instructor de buceo ruso-israelí", "0,9"],
   ["Fecha", "28 de abril de 2000", "0,9"],
   ["Lugar", "Blue Hole, ~10 km al norte de Dahab (Sinaí, Egipto), golfo de Aqaba", "1,0"],
   ["Profundidad del cuerpo", "~115 m (placa conmemorativa y testimonio de Tarek Omar)", "0,85"],
   ["Gas y equipo", "Aire comprimido en una botella de 12 L; ~12 kg de lastre; cámara en el casco", "0,8"],
   ["Duración de la grabación", "Unos 7 minutos (7:16 según Der Spiegel)", "0,85"],
   ["Recuperación", "Tarek Omar, al día siguiente, a petición de la madre", "0,85"],
   ["Límite del buceo recreativo", "40 m", "1,0"]], [4, 10.2, 2.2])
P("<b>En una frase:</b> un instructor joven bajó solo, con aire y una sola botella, a casi el triple de la profundidad "
  "recreativa. A esa profundidad el aire es a la vez narcótico, tóxico y muy difícil de respirar, y ya no pudo volver.")

# ======================= PARTE I =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PARTE I<br/>El lugar", ss["part"])); story.append(PageBreak())

H1("2. El mar Rojo: un océano que está naciendo")
P("Para entender el Blue Hole hay que empezar por el mar que lo contiene. El <b>mar Rojo</b> es un brazo del océano Índico "
  "situado entre África y la península arábiga. Se comunica con el océano solo por el sur, a través del estrecho de "
  "<b>Bab el-Mandeb</b> y el golfo de Adén. Al norte se divide en dos golfos separados por la península del Sinaí: el de "
  "<b>Suez</b> al oeste y el de <b>Aqaba</b> al este. En este último está Dahab.")
FIGURE("mapa_mar_rojo.png", 11.5, "Figura 1. El mar Rojo y la situación de Dahab. Ilustración propia con datos de costa de Natural Earth (dominio público).")
H2("Datos básicos")
T([["Característica", "Valor", "Qué significa"],
   ["Longitud", "~2.250 km", "Más o menos la distancia de Barcelona a Moscú"],
   ["Anchura máxima", "~355 km", "Es un mar largo y estrecho"],
   ["Profundidad media / máxima", "490 m / 2.730 m (fosa de Suakin)", "Mucho más hondo que el Mediterráneo occidental en su parte central"],
   ["Salinidad", "~36 ‰ en el sur a ~41 ‰ en el norte (media ~40 ‰)", "Uno de los mares más salados del mundo (el Atlántico ronda 35 ‰)"],
   ["Evaporación", "hasta ~2.050 mm al año", "Se evapora mucha agua y apenas entra agua dulce"],
   ["Temperatura superficial", "~26 °C en verano en el norte, ~30 °C en el sur", "Agua cálida todo el año"],
   ["Ríos que desembocan", "Ninguno importante", "Sin sedimentos: agua muy transparente"],
   ["Biodiversidad", "más de 1.200 especies de peces (~10 % endémicas) y más de 200 tipos de coral", "Endémico = que solo vive aquí"]],
  [4, 5.6, 6.8])
H2("Cómo se formó: un rift en marcha")
P("El mar Rojo existe porque la placa <b>arábiga</b> se está separando de la <b>africana</b>. Ese proceso, llamado "
  "<b>rift</b> (fractura y separación de la corteza), empezó hace unos 30–40 millones de años (Eoceno–Oligoceno). La "
  "separación continúa: en 2005, tras tres semanas de actividad tectónica en la zona de Afar, el rift se abrió unos 8 m de "
  "golpe. Los geólogos lo consideran un <b>océano en formación</b>: dentro de millones de años podría ser tan ancho como el "
  "Atlántico.")
H2("¿Por qué se llama «Rojo»?")
P("Hay dos explicaciones principales. La primera son las floraciones estacionales de una cianobacteria rojiza, "
  "<i>Trichodesmium erythraeum</i>, que tiñen la superficie. La segunda es que en varias lenguas antiguas los colores "
  "indicaban los puntos cardinales y el «rojo» designaba el sur. Ninguna está demostrada del todo (confianza 0,6).")

H1("3. El golfo de Aqaba: una falla bajo el agua")
P("El <b>golfo de Aqaba</b> es la rama nororiental del mar Rojo. Lo bordean cuatro países: <b>Egipto</b> (costa del Sinaí, "
  "donde están Taba, Nuweiba, Dahab y Sharm el-Sheij), <b>Israel</b> (Eilat), <b>Jordania</b> (Aqaba) y <b>Arabia Saudí</b> (Haql). "
  "Por el sur se comunica con el mar Rojo a través del estrecho de <b>Tirán</b>.")
FIGURE("mapa_golfo_aqaba.png", 11, "Figura 2. El golfo de Aqaba con Dahab y el Blue Hole. Ilustración propia con datos de costa de Natural Earth.")
T([["Característica", "Valor"],
   ["Longitud", "~160–188 km según dónde se mida"],
   ["Anchura", "~19–27 km"],
   ["Profundidad máxima", "~1.850 m (algunas fuentes dan ~1.700 m)"],
   ["Origen geológico", "Extremo sur de la <b>transformante del mar Muerto</b>, una gran falla de desgarre"],
   ["Cuencas profundas", "Tres cuencas de tracción (<i>pull-apart</i>): Elat, Aragonese y Dakar"],
   ["Sismicidad", "Terremoto del golfo de Aqaba de 1995, causado por uno de estos segmentos de falla"]], [5, 11.4])
H2("Qué significa todo esto")
P("Una <b>falla transformante</b> es una fractura donde dos bloques de corteza se deslizan lateralmente uno respecto al otro, "
  "como dos libros que se frotan de canto. En el golfo de Aqaba la falla no es una línea recta, sino varios tramos escalonados. "
  "Donde un tramo termina y el siguiente empieza, la corteza se estira y se hunde, formando una <b>cuenca de tracción</b>. "
  "Por eso el golfo es tan estrecho y tan profundo, y por eso a pocos metros de la orilla de Dahab el fondo cae en vertical "
  "a cientos de metros.")
BOX("<b>Razonamiento:</b> la geología explica la fama del Blue Hole. En muy pocos lugares del mundo se puede entrar al "
    "agua desde una playa, sin barco, y tener a pocos metros 100 m de profundidad en un pozo tranquilo y sin corriente. "
    "Esa facilidad de acceso es justamente lo que lo hace peligroso.")
H2("Corales que resisten el calor: el «refugio térmico»")
P("El golfo de Aqaba tiene uno de los arrecifes de coral más septentrionales del mundo y muy bien conservados. Los "
  "científicos han comprobado que sus corales soportan temperaturas muy por encima de su máximo de verano sin "
  "<b>blanquearse</b>. El blanqueamiento ocurre cuando el coral, estresado por el calor, expulsa las microalgas "
  "(<b>zooxantelas</b>) que viven en su interior y le dan alimento y color.")
P("La explicación más aceptada, propuesta por Maoz Fine y su equipo en 2013, es que los antepasados de estos corales "
  "colonizaron el mar Rojo después de la última glaciación entrando por el sur, por Bab el-Mandeb, donde el agua es muy "
  "caliente. Solo sobrevivieron los más resistentes al calor. Al llegar al norte, más fresco, viven lejos de su límite de "
  "temperatura máxima. Por eso se habla del golfo de Aqaba como un <b>refugio térmico</b> frente al cambio climático. Un "
  "estudio de 2021 (Bellworthy y Fine) añade un matiz: estos mismos corales viven cerca de su límite de <b>frío</b>, así que "
  "un invierno anómalo también les puede hacer daño.")
T([["Dato del entorno (Arabia Saudí, lista indicativa de la UNESCO, 2024)", "Valor"],
   ["Especies de coral", "más de 265"], ["Especies de peces", "unas 800"],
   ["Tiburones y rayas", "14 especies, entre ellas el pez guitarra de Halavi (en peligro crítico)"],
   ["Otros", "dugongos, tortugas verde y carey, cetáceos y aves marinas"],
   ["Hallazgo reciente", "Pozas de salmuera de NEOM a ~1.770 m, descubiertas en 2020"]], [9, 7.4])

H1("4. Dahab: de pueblo de pescadores a capital del buceo")
P("<b>Dahab</b> es una pequeña ciudad de la costa del Sinaí Sur, a unos 80 km al nordeste de Sharm el-Sheij. Su nombre "
  "significa <b>«oro»</b> en árabe, quizá por el color de la arena. Algunos estudiosos la identifican con el lugar llamado "
  "<i>Di-Zahav</i> («el del oro») en el Deuteronomio bíblico.")
H2("Datos de la ciudad")
T([["Aspecto", "Detalle"],
   ["Población", "~3.200 habitantes censados en 2023 (más población flotante de trabajadores y turistas)"],
   ["Barrios", "Masbat (norte, con el antiguo poblado beduino de Asalah), Mashraba (centro-sur) y Medina (suroeste)"],
   ["Clima", "Desértico cálido: julio ~35 °C de máxima, enero ~21 °C. Llueve unos 9 mm al año"],
   ["Temperatura del mar", "~21–22 °C en invierno y ~28–29 °C a finales de verano"],
   ["Economía", "Turismo, buceo, apnea, windsurf y kitesurf. Hay minerales en las rocas (rutilo, circón, oro)"],
   ["Centros de buceo", "En 2012 había unos 52 registrados, además de escuelas sin licencia"],
   ["Asistencia médica", "Centro médico hiperbárico con cámara de recompresión para seis pacientes"]], [3.6, 12.8])
H2("Breve historia")
B(["Durante siglos fue un lugar de pesca y de paso de los <b>beduinos</b> del Sinaí.",
   "De <b>1967 a 1979</b> el Sinaí estuvo ocupado por Israel. En esa época Dahab (llamada <i>Di-Zahav</i>) empezó a recibir "
   "viajeros y buceadores, y el Blue Hole se hizo famoso.",
   "Tras el tratado de paz de 1979 el Sinaí volvió a Egipto. Desde los años 80 Dahab creció como destino mochilero y de buceo, "
   "más tranquilo y barato que Sharm el-Sheij.",
   "En 2012, según Der Spiegel, el buceo era un negocio de descuento: un curso de iniciación costaba unos 200 € y una "
   "inmersión guiada, unos 25 €."])
H2("Por qué la gente va a Dahab")
N(["<b>Acceso desde la orilla.</b> Casi todos los puntos de buceo se alcanzan caminando desde la playa, sin barco.",
   "<b>Agua cálida, clara y tranquila,</b> con una visibilidad que suele rondar los 20–30 m.",
   "<b>Arrecifes sanos</b> a muy poca profundidad, ideales también para snorkel.",
   "<b>Profundidad muy cerca de la costa,</b> lo que atrae a buceadores técnicos y apneístas de todo el mundo.",
   "<b>Puntos famosos:</b> el Blue Hole y The Bells, el Canyon, el Eel Garden (jardín de anguilas), el Lighthouse y, más al "
   "norte, la zona protegida de Ras Abu Galum.",
   "<b>Ambiente</b> relajado, cafés beduinos al borde del agua y precios bajos."])

H1("5. El Blue Hole: anatomía de un pozo")
P("Un <b>blue hole</b> («agujero azul») es una <b>dolina submarina</b>: un pozo vertical abierto en roca caliza o en el "
  "arrecife. La mayoría se formaron durante las glaciaciones, cuando el nivel del mar estaba hasta unos 120 m más bajo. El "
  "agua de lluvia, ligeramente ácida, disolvía la roca y excavaba cavidades. Al subir el mar, quedaron inundadas. Visto "
  "desde arriba es un círculo azul oscuro rodeado de arrecife turquesa, porque el agua profunda absorbe todos los colores "
  "menos el azul.")
FIGURE("corte_blue_hole.png", 16, "Figura 2b. Corte esquemático del Blue Hole con el Arco, los límites de profundidad y dónde se encontraron algunas víctimas. Ilustración propia.")
T([["Elemento", "Medida", "Notas"],
   ["Diámetro de la boca", "~70–80 m", "En el techo del arrecife"],
   ["Fondo del pozo", "algo más de 100 m", "Las fuentes dan entre 94 y 130 m"],
   ["The Saddle («la silla»)", "~6–7 m", "Abertura somera hacia el mar; es la que usan los buceadores recreativos"],
   ["The Arch («el Arco»)", "techo a ~52–56 m", "Túnel que atraviesa el arrecife hacia el mar abierto"],
   ["Longitud del Arco", "~26 m", "Desde dentro parece medir menos de 10 m"],
   ["Suelo del Arco", "de ~102 a ~120 m", "Desciende hacia el lado del mar"],
   ["Fuera del Arco", "escalones de 130, 150, 250, 300 y ~800 m", "Sin un fondo que sirva de referencia"]], [4.4, 4, 8])
H2("Por qué engaña el Arco")
N(["<b>Es fácil pasarse.</b> La entrada no está en línea recta desde el pozo. Quien no la encuentra sigue bajando buscándola, y debajo no hay referencia.",
   "<b>Parece corto.</b> Con agua tan clara y la salida tan luminosa, el túnel parece de pocos metros, pero mide 26.",
   "<b>Suele entrar corriente</b> del mar hacia el pozo, lo que obliga a nadar contra ella y gastar más gas.",
   "<b>Es un techo.</b> Dentro no se puede subir en vertical (es un <i>entorno con techo</i>).",
   "<b>Está justo en el límite del aire.</b> Con aire, el oxígeno pasa a ser peligroso hacia los 56–57 m (ver §8.3), justo donde está el techo del Arco.",
   "<b>La luz engaña.</b> Hacia los 45 m vuelve a verse luz que entra por el túnel, sobre todo por la mañana. Es un espectáculo que atrae a quien no debería estar ahí."])
H2("Historia y leyenda")
P("Según Wikipedia, un grupo de buceadores israelíes dirigido por Alex Shell fue el primero en bucearlo con equipo moderno "
  "en 1968 y vio el Arco. Un reportaje egipcio (Masrawy, 2018) atribuye el descubrimiento a pilotos israelíes que lo vieron "
  "desde un helicóptero en 1962. Las dos versiones pueden ser compatibles: verlo desde el aire y bucearlo por primera vez "
  "son cosas distintas (confianza 0,6).")
P("Entre los beduinos circula la leyenda de una joven que se ahogó en el pozo para no casarse con quien no quería, y cuyo "
  "espíritu atraería a los buceadores. Tarek Omar, que conoce el fondo como nadie, la descarta: dice que nunca ha visto "
  "nada sobrenatural y que la causa de las muertes es casi siempre el propio buceador.")

H1("6. Qué vida marina encontramos")
P("Dahab no se visita por el Blue Hole profundo, sino por la <b>pared del arrecife</b> entre la superficie y los 30 m. Ahí "
  "está la mayor parte de la vida. La luz decide qué hay a cada profundidad: el agua absorbe primero el rojo (hacia 5 m), "
  "luego el naranja, el amarillo y el verde. Por debajo de ~40 m solo queda azul y la vida que necesita luz desaparece.")
FIGURE("zonas_vida.png", 16, "Figura 3. Qué se ve a cada profundidad en Dahab y cómo se apagan los colores. Ilustración propia.")
H2("Especies que es fácil ver")
T([["Especie (nombre común)", "Nombre científico", "Profundidad", "Cómo reconocerla y curiosidades"],
   ["Anthias o pez joya", "<i>Pseudanthias squamipinnis</i>", "3–30 m", "Nubes de pececillos naranjas y morados sobre el coral. Nacen hembras y algunas se convierten en machos."],
   ["Pez Napoleón", "<i>Cheilinus undulatus</i>", "5–60 m", "Puede superar 1,5 m. Azul verdoso con labios gruesos. En peligro según la UICN."],
   ["Pez payaso de Arabia", "<i>Amphiprion bicinctus</i>", "1–30 m", "Vive protegido entre los tentáculos de una anémona, que a él no le pica."],
   ["Pez mariposa del mar Rojo", "<i>Chaetodon paucifasciatus</i>", "2–30 m", "Endémico del mar Rojo y el golfo de Adén. Suele ir en pareja."],
   ["Cirujano sohal", "<i>Acanthurus sohal</i>", "0–10 m", "Rayado azul y negro, territorial. Tiene una «cuchilla» afilada junto a la cola."],
   ["Pez león", "<i>Pterois miles</i>", "1–50 m", "Aletas como plumas. Sus espinas son venenosas: mirar sin tocar."],
   ["Pez piedra", "<i>Synanceia verrucosa</i>", "0–30 m", "Camuflado como una roca. Es uno de los peces más venenosos del mundo."],
   ["Morena gigante", "<i>Gymnothorax javanicus</i>", "1–50 m", "Abre y cierra la boca para respirar, no para amenazar."],
   ["Raya de puntos azules", "<i>Taeniura lymma</i>", "1–30 m", "Sobre la arena entre corales. Tiene un aguijón en la cola."],
   ["Tortuga carey y tortuga verde", "<i>Eretmochelys imbricata</i>, <i>Chelonia mydas</i>", "1–40 m", "La carey come esponjas; la verde, algas y hierbas marinas. Ambas están amenazadas."],
   ["Jardín de anguilas", "<i>Gorgasia sillneri</i>", "10–40 m", "Cientos de anguilas jardineras que asoman de la arena (Eel Garden)."],
   ["Barracudas y jureles", "<i>Sphyraena</i>, <i>Caranx</i>", "azul abierto", "Depredadores que patrullan frente a la pared."],
   ["Peces y gambas limpiadores", "<i>Labroides dimidiatus</i>, otros", "5–30 m", "Limpian parásitos de otros peces. Hacia los 18 m hay una «estación de limpieza» famosa."],
   ["Dugongo (raro)", "<i>Dugong dugon</i>", "praderas someras", "Mamífero herbívoro amenazado. Se ve más al sur (Marsa Alam)."]],
  [3.4, 3.8, 1.9, 7.3])
H2("Corales y «vegetación»")
P("En el arrecife casi no hay plantas. Lo que parece vegetación son en su mayoría <b>animales</b> (corales y esponjas) y algas:")
B(["<b>Corales duros</b> (<i>Acropora</i>, <i>Porites</i>, <i>Stylophora</i>): construyen el arrecife con esqueletos de carbonato de calcio. Viven en simbiosis con las zooxantelas, que hacen la fotosíntesis.",
   "<b>Corales blandos</b> (<i>Sarcophyton</i>, <i>Sinularia</i>): flexibles y de colores, sin esqueleto rígido.",
   "<b>Coral de fuego</b> (<i>Millepora</i>): no es un coral verdadero. Pica al tocarlo.",
   "<b>Gorgonias</b> (abanicos de mar) y <b>coral negro</b>: más abundantes en la pared profunda (25–40 m).",
   "<b>Algas coralinas</b>: cementan el arrecife con una costra rosada.",
   "<b>Fanerógamas marinas</b> (plantas con flor, como <i>Halophila</i>): forman praderas en zonas arenosas someras y alimentan a tortugas y dugongos.",
   "<b>En tierra:</b> desierto con acacias y palmeras datileras (<i>Phoenix dactylifera</i>) en los oasis y los wadis."])
H2("La inmersión clásica: The Bells → Blue Hole")
P("Es la forma segura y recomendada de conocer el Blue Hole. Se hace desde la orilla, con titulación de 30 m (Advanced Open Water o equivalente):")
N(["Se camina unos 150 m desde el Blue Hole hasta <b>The Bells</b>, una grieta de unos 3 × 2 m en el arrecife.",
   "Se baja por una <b>chimenea</b> vertical. La luz entra por las rendijas. La chimenea se estrecha hacia los 23 m y se sale a mar abierto por una ventana a 26–28 m. (No hay que confundir el pequeño arco de The Bells con el Arco del Blue Hole.)",
   "Se recorre la <b>pared</b> con el arrecife a la derecha, subiendo poco a poco. Se ven corales negros, salientes cubiertos de coral duro, anthias, peces león y, hacia los 18 m, la estación de limpieza.",
   "A los 35–45 minutos se sube a 7–12 m y se cruza <b>la Saddle</b> para entrar en el Blue Hole.",
   "Se termina con la parada de seguridad dentro del pozo, donde también entrenan los apneístas."])
H2("Condiciones del agua")
T([["Parámetro", "Valor habitual"],
   ["Temperatura del agua", "~22 °C en enero y ~29 °C en agosto (neopreno de 3–5 mm en invierno)"],
   ["Visibilidad", "Normalmente 20–30 m"],
   ["Corriente", "Nula o ligera dentro del pozo; puede ser moderada en la pared y en el Arco"],
   ["Mejor época", "Primavera y otoño: agua templada y menos calor en tierra"]], [4.5, 11.9])
BOX("<b>Normas para el visitante:</b> no tocar ni pisar el coral, no dar de comer a los peces, controlar la flotabilidad cerca de "
    "la pared, no recoger conchas ni corales y usar protector solar respetuoso con el arrecife. Y, sobre todo, no bajar por "
    "debajo de la profundidad para la que se tiene titulación.")

# ======================= PARTE II =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PARTE II<br/>El accidente de Yuri Lipski", ss["part"])); story.append(PageBreak())

H1("7. Quién era y qué ocurrió")
P("<b>Yuri Lipski</b> era un instructor de buceo de 22 años, de origen ruso y residente en Israel. Viajó a Dahab con la "
  "intención de bucear el Blue Hole más allá de lo habitual. Según Tarek Omar, que lo conocía, Lipski le pidió que lo "
  "guiara. Omar le advirtió <b>dos veces</b> que no lo hiciera y le propuso unas dos semanas de entrenamiento previo. Lipski "
  "dijo que no tenía tiempo y buscó otro acompañante.")
BOX("<b>Razonamiento:</b> «instructor» no es lo mismo que «buceador técnico». Ser instructor recreativo significa dominar el "
    "equipo básico hasta 40 m. Bajar a 100 m exige otra formación, otros gases y otro equipo. Muchos accidentes del Blue Hole "
    "los sufren buceadores con experiencia que confían en ella fuera de su rango de formación.")
H2("Cronología reconstruida")
T([["Momento", "Qué pasó", "Fuente / confianza"],
   ["Días antes", "Omar le desaconseja la inmersión dos veces y le ofrece entrenar antes", "The Guardian, CairoScene · 0,9"],
   ["Preparación", "Se equipa con una botella de 12 L de aire, ~12 kg de plomo en el cinturón y cámara con baterías en el casco", "Der Spiegel (Omar) · 0,8"],
   ["Entrada", "Empieza a grabar al entrar en el pozo; al principio hay otros buceadores cerca", "Descripciones del vídeo · 0,8"],
   ["Descenso", "Se separa del grupo y sigue bajando solo, en agua azul, sin control", "Wikipedia, Der Spiegel · 0,9"],
   ["Fondo", "El ordenador marca 81,7 m, luego 85,3 m y 91,6 m al tocar el fondo; intenta inflar el chaleco sin éxito y levanta arena", "Der Spiegel · 0,8"],
   ["Final", "La imagen se queda fija; la grabación dura unos 7 minutos", "Der Spiegel · 0,85"],
   ["Día siguiente", "Tarek Omar recupera el cuerpo a ~115 m, boca abajo, y la cámara", "Wikipedia, Der Spiegel · 0,85"]], [2.6, 9.4, 4.4])
BOX("<b>Discrepancia interesante:</b> el ordenador de muñeca marcaba unos 92 m al tocar el fondo, pero el cuerpo se encontró "
    "hacia los 115 m. Hay varias explicaciones posibles: el fondo del pozo es una pendiente de arena y escombros, el cuerpo "
    "pudo deslizarse o ser arrastrado más abajo, o las cifras de una fuente están redondeadas. No hay forma de saberlo con "
    "seguridad (confianza 0,5).", colors.HexColor("#fff4e5"), WARN)
H2("Qué muestra la grabación")
P("(Descripción basada en fuentes escritas; este estudio no enlaza el vídeo.) Primero se ven paredes de arrecife y otros "
  "buceadores. Después solo agua azul y cada vez menos luz. El descenso es continuo, sin paradas. Al llegar al fondo la "
  "arena nubla la imagen y la respiración se acelera mucho. Hay intentos de inflar el chaleco y, según Wikipedia, llega a "
  "quitarse el regulador de la boca. Al final la cámara mira al fondo y la imagen se queda quieta. Varias fuentes señalan que "
  "la cinta no muestra con claridad el momento exacto de la muerte: el título «grabó su propia muerte» es una simplificación.")

H1("8. Por qué murió: la física del aire a 115 m")
P("Nadie puede saber qué pasaba por su cabeza. Pero la física del buceo permite calcular <b>qué le hacía el aire</b> a esa "
  "profundidad. Los cálculos de esta sección son propios, con fórmulas estándar, y se han comprobado con un programa en Python.")
H2("8.1 La presión (ley de Boyle)")
P("En el mar, cada 10 m de agua suman 1 bar de presión, y a eso se añade 1 bar de la atmósfera:")
P("<para alignment='center'><b>P<sub>absoluta</sub> (bar) = 1 + profundidad (m) / 10</b></para>")
P("Según la <b>ley de Boyle</b>, el volumen de un gas es inversamente proporcional a la presión.")
T([["Profundidad", "Presión absoluta", "1 L de aire de superficie ocupa…", "Densidad del aire"],
   ["0 m", "1 bar", "1 L", "1,2 g/L"], ["10 m", "2 bar", "0,5 L", "2,5 g/L"], ["40 m", "5 bar", "0,2 L", "6,1 g/L"],
   ["56 m", "6,6 bar", "0,15 L", "8,1 g/L"], ["<b>115 m</b>", "<b>12,5 bar</b>", "<b>0,08 L</b>", "<b>15,3 g/L</b>"]], [3.4, 3.6, 5, 4.4])
H2("8.2 Narcosis por nitrógeno")
P("El aire es un 79 % nitrógeno. Según la <b>ley de Dalton</b>, cada gas de una mezcla aporta su parte de la presión total "
  "(su <b>presión parcial</b>). Según la <b>ley de Henry</b>, cuanto mayor es esa presión parcial, más gas se disuelve en la "
  "sangre y los tejidos. A alta presión, el nitrógeno disuelto tiene un efecto <b>anestésico</b> sobre las neuronas, parecido "
  "al del alcohol: euforia, exceso de confianza, ideas fijas, lentitud y, a gran profundidad, alucinaciones y pérdida de "
  "conciencia. A 115 m la presión parcial del nitrógeno es de unos <b>9,9 bar</b>, frente a 0,79 bar en superficie.")
P("La regla informal de la <b>«ley del Martini»</b> compara cada 10 m por debajo de los 20 m con tomarse un martini. A 115 m "
  "serían unos <b>9–10 martinis</b>. La narcosis no duele ni avisa: quita justo la capacidad de darse cuenta del peligro. Su "
  "único remedio es subir, que era lo que Lipski no conseguía.")
H2("8.3 Toxicidad del oxígeno")
P("El oxígeno es <b>tóxico</b> para el sistema nervioso central cuando su presión parcial (ppO<sub>2</sub>) es demasiado alta. "
  "Puede provocar <b>convulsiones sin aviso</b>, y bajo el agua una convulsión casi siempre significa perder el regulador y "
  "ahogarse. El límite de trabajo recomendado es 1,4 bar y el máximo de contingencia, 1,6 bar. Con aire a 115 m: "
  "0,21 × 12,5 ≈ <b>2,6 bar</b>, casi el doble del máximo.")
P("La <b>profundidad máxima operativa (MOD)</b> del aire es 10 × (1,4 / 0,21 − 1) ≈ <b>56,7 m</b> (66 m con 1,6 bar). "
  "Der Spiegel fija en 56 m el límite crítico del aire, y el Arco empieza a 52–56 m. <b>El Arco está justo donde el aire "
  "empieza a ser tóxico.</b> Lipski estuvo unos 60 m más abajo. Omar contó a Der Spiegel que los espasmos que se ven en el "
  "vídeo le hacen pensar en una intoxicación por oxígeno.")
FIGURE("gases.png", 16, "Figura 4. Presión parcial de oxígeno y densidad del gas respirando aire o trimix 10/70. Cálculo propio.")
H2("8.4 Densidad del gas y dióxido de carbono")
P("A 12,5 bar el aire pesa unos <b>15 g/L</b>. Las recomendaciones de Anthony y Mitchell (2016) fijan como deseable un máximo "
  "de <b>5,2 g/L</b> y como límite absoluto <b>6,2 g/L</b>; con aire se alcanzan hacia los 32 y los 41 m. Un gas tan denso "
  "circula con turbulencias, cuesta mucho moverlo y el <b>CO<sub>2</sub> se acumula</b> (<b>hipercapnia</b>). El exceso de "
  "CO<sub>2</sub> da sensación de ahogo y ansiedad, <b>intensifica la narcosis</b> y <b>adelanta la toxicidad del oxígeno</b>.")
BOX("<b>El círculo vicioso:</b> gas denso → se acumula CO<sub>2</sub> → ahogo y pánico → respiración más rápida → más "
    "CO<sub>2</sub> y más gasto de aire → más pánico. Encaja con la respiración acelerada que describen quienes han analizado la grabación.")
H2("8.5 Consumo de gas: la botella se vacía 12,5 veces más rápido")
T([["Situación", "Consumo en superficie", "Consumo a 115 m", "Duración de 12 L a 200 bar (2.400 L)"],
   ["Relajado", "20 L/min", "250 L/min", "≈ 9,6 min"], ["Esfuerzo o estrés", "40 L/min", "500 L/min", "≈ 4,8 min"],
   ["Pánico", "60 L/min", "750 L/min", "≈ 3,2 min"]], [3.6, 4, 3.6, 5.2])
P("Aun con la botella llena no había gas para las <b>paradas de descompresión</b> que exige una inmersión así, ni siquiera "
  "para un ascenso lento. (Estimación propia: se desconoce su consumo personal y la presión real de la botella.)")
H2("8.6 Flotabilidad: por qué no pudo subir")
N(["<b>Exceso de lastre.</b> Según Omar, llevaba unos 12 kg de plomo, además de la botella, la cámara y las baterías.",
   "<b>El neopreno se aplasta.</b> El traje flota gracias a burbujas de gas en su interior. A 12,5 bar esas burbujas se comprimen y el traje pierde casi toda su flotabilidad.",
   "<b>Inflar el chaleco cuesta mucho gas.</b> Compensar 12 kg exige 12 L de gas a 115 m, es decir, unos 150 L de superficie sacados de una botella que ya se vaciaba deprisa.",
   "<b>Fallo de procedimiento.</b> Omar explica que el chaleco se reventó porque ya estaba lleno cuando intentó meterle más aire. Bajo narcosis y pánico es típico quedarse fijado en una sola acción en vez de soltar el lastre."])
BOX("<b>La trampa contraria:</b> si hubiera soltado el lastre habría subido sin control desde 115 m, con riesgo muy alto de "
    "<b>enfermedad descompresiva</b> grave o <b>sobreexpansión pulmonar</b>. A esa profundidad y con ese equipo no había "
    "ninguna salida segura. El error decisivo estuvo <b>antes de entrar al agua</b>.")
H1("9. La cadena de errores")
P("En seguridad se usa el <b>modelo del queso suizo</b>: un accidente casi nunca tiene una sola causa. Ocurre cuando se "
  "alinean los agujeros de varias capas de protección.")
FIGURE("cadena_errores.png", 16, "Figura 5. La cadena de errores del accidente. Ilustración propia.")
T([["Eslabón", "¿Comprobado?", "Confianza"],
   ["Rechazó el consejo y la formación de un experto", "Sí (Omar en The Guardian y CairoScene)", "0,9"],
   ["Aire en una sola botella de 12 L", "Sí (Omar en Der Spiegel; Wikipedia lo da por supuesto)", "0,85"],
   ["Descenso sin control", "Sí (grabación y profundidad del cuerpo)", "0,9"],
   ["~12 kg de lastre", "Testimonio directo de Omar en Der Spiegel", "0,8"],
   ["Narcosis severa", "Físicamente inevitable a esa profundidad", "0,95"],
   ["Toxicidad del oxígeno como causa directa", "Posible (opinión de Omar); no puede demostrarse", "0,55"],
   ["Acumulación de CO<sub>2</sub>", "Muy probable por la densidad del gas", "0,8"]], [7.4, 6.8, 2.2])

# ======================= PARTE III =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PARTE III<br/>Tarek Omar,<br/>el que baja a buscarlos", ss["part"])); story.append(PageBreak())

H1("10. Quién es Tarek Omar")
P("En el vídeo de The Wild Project se le presenta como el compañero o guía de Lipski. Es un matiz importante: según todas las "
  "fuentes, <b>Tarek Omar no buceó con Lipski</b>. Fue el experto local que le desaconsejó la inmersión y quien, al día "
  "siguiente, bajó a recuperar su cuerpo a petición de la familia.")
H2("Ficha biográfica")
T([["Aspecto", "Dato", "Fuente / confianza"],
   ["Nombre", "Tarek Omar (en la prensa egipcia, Tarek Omar El-Masry)", "Varias · 0,9"],
   ["Origen", "Beduino de la tribu Aulad Ali, nacido en un pueblo cerca de la frontera con Libia", "Der Spiegel 2012 · 0,8"],
   ["Edad", "47 años en 2012 y 52 en 2016–2018, así que nació hacia 1965–1966", "Der Spiegel, Masrawy, Al-Masry Al-Youm · 0,7"],
   ["Llegada a Dahab", "1989, buscando trabajo", "Der Spiegel · 0,8"],
   ["Inicio en el buceo", "Aprendió a bucear en 1992 e hizo de instructor desde 1995; la prensa egipcia sitúa su trabajo en el Blue Hole desde 1994", "Der Spiegel, Masrawy · 0,7"],
   ["Primeras recuperaciones", "Noviembre de 1997: los irlandeses Conor O'Regan y Martin Gara, abrazados a 102 m", "Der Spiegel · 0,9"],
   ["Récord de profundidad local", "209 m según Der Spiegel (2012); 220 m según Al-Masry Al-Youm (2016)", "0,6"],
   ["Escuela", "Abrió el primer centro de buceo técnico de Dahab", "Der Spiegel · 0,8"],
   ["Apodos", "«Sheikh de los buceadores», «Rey del Blue Hole», «Gigante de las profundidades», «el recolector de huesos», «The Elder Diver»", "Prensa egipcia e internacional · 0,9"],
   ["Cuerpos recuperados", "Dice que perdió la cuenta. Otras fuentes hablan de más de 20 (The Chronicle) o de 9 (Masrawy)", "0,5"],
   ["Precio", "No cobra por las recuperaciones; solo pide el coste del gas", "Der Spiegel · 0,8"]], [3.6, 8.6, 4.2])
H2("Su papel en el caso Lipski")
B(["Había visto a Lipski dos veces y lo describió como muy imprudente. Le aconsejó entrenar antes; Lipski respondió que no tenía tiempo.",
   "Recuperó el cuerpo a unos 115 m, boca abajo, junto con la cámara.",
   "La cámara estaba diseñada para unos 75 m y, aun así, funcionaba. La reprodujeron delante de la madre cuando ella le pidió ayuda para desmontar el equipo.",
   "Omar ha dicho que lamenta que la madre tenga para siempre esas imágenes y que, de haber sabido que existían, habría destruido la cinta.",
   "El padre, Alexander Lipski, le envió un certificado escrito en cinco idiomas agradeciéndole la peligrosa misión de recuperar a su hijo."])
H2("Lo que piensa del Blue Hole")
B(["Para él, el Blue Hole es una de las inmersiones más bonitas del mundo y no tiene nada sobrenatural.",
   "Su peligro es psicológico: <b>parece fácil</b> (agua cálida, sin corriente, buena visibilidad, se entra desde la playa) y por eso se subestima.",
   "Compara lo que ocurre allí con la masificación del Everest: gente sin preparación persiguiendo una cifra.",
   "Critica a quienes salen de fiesta hasta la madrugada y bajan al Blue Hole por la mañana buscando «el 100 mágico» en su ordenador.",
   "Insiste en que para bucear el Arco hace falta <b>trimix</b>, no aire, para reducir el «efecto martini»."])

H1("11. Cómo recupera los cuerpos: su método")
P("En la entrevista de Der Spiegel (2012), Omar explicó paso a paso cómo trabaja. Lo resumimos aquí con nuestras palabras y "
  "con la explicación técnica de cada paso.")
T([["Paso", "Qué hace Omar", "Por qué (explicación técnica)"],
   ["1. Investigar", "Pregunta qué equipo llevaba el fallecido: grosor del neopreno, cantidad de lastre, tipo de botella", "Con esos datos estima la flotabilidad del cuerpo y hacia dónde pudo derivar. Un cuerpo no cae recto como una piedra."],
   ["2. Último punto conocido", "Pregunta al compañero dónde y a qué profundidad lo vio por última vez", "Reduce el área de búsqueda. Es el «último punto conocido» de cualquier protocolo de búsqueda."],
   ["3. Avisar", "Su equipo informa a los turistas de que se va a recuperar un cuerpo y les pide que se aparten de lo que salga a superficie", "Seguridad, respeto a la víctima y a la familia."],
   ["4. Dejarse llevar", "Al llegar a la zona, se deja derivar como lo haría un cuerpo inerte", "Reproduce la trayectoria más probable siguiendo el relieve y la pendiente del fondo."],
   ["5. Asegurar", "La mayoría de los cuerpos están entre 100 y 120 m. Lo sujeta en brazos o lo ata a su propio cuerpo", "A esa profundidad solo dispone de unos <b>5 minutos</b> de fondo."],
   ["6. Subir hasta 40 m", "Asciende con el cuerpo", "Ascenso controlado: él sí necesita descomprimir."],
   ["7. Globo de elevación", "A unos 40 m, cuando ya ve la superficie, envía el cuerpo arriba con un globo de elevación", "El fallecido no necesita descompresión. Así Omar se libera del peso y puede hacer sus paradas con seguridad."],
   ["8. Descomprimir", "Se queda bajo el agua hasta unas 3 horas", "Paradas de descompresión largas tras una inmersión muy profunda. Cuando sale, el cuerpo ya está en tierra."],
   ["Plazo", "Intenta recuperar el cuerpo en 2–3 días y nunca más de 7", "La familia quiere un entierro; pasado ese tiempo el cuerpo se deteriora y es mejor dejarlo."]],
  [2.6, 6.4, 7.4])
FIGURE("perfil_recuperacion.png", 16, "Figura 6. Perfil ilustrativo de una recuperación a ~110 m, construido a partir de lo descrito por Omar. Los tiempos son aproximados.")
H2("Recursos y equipo que se necesitan")
T([["Recurso", "Para qué sirve"],
   ["Trimix como gas de fondo (O<sub>2</sub> + helio + N<sub>2</sub>)", "El helio sustituye a parte del nitrógeno (menos narcosis) y del oxígeno (sin toxicidad). Omar lo menciona expresamente."],
   ["Gases de descompresión (nitrox rico y O<sub>2</sub> puro)", "Aceleran la eliminación de gas inerte en las paradas. Cada botella se marca con su profundidad máxima."],
   ["Botellas dobles, de etapa o <b>rebreather</b>", "Llevar gas suficiente y de reserva. Un rebreather recicla el gas y permite inmersiones mucho más largas."],
   ["Ordenador de buceo multigás", "Calcula la descompresión real con los cambios de gas."],
   ["Globo de elevación y boya de superficie", "Subir el cuerpo de forma independiente y señalar la posición en superficie."],
   ["Cabos, carrete y cortador", "Guía de descenso, sujeción del cuerpo y salida si alguien se enreda."],
   ["Funda o bolsa para el cuerpo", "Respeto a la víctima y conservación de pruebas."],
   ["Equipo de superficie", "Vigilancia, comunicación, primeros auxilios, oxígeno y recogida del cuerpo."],
   ["Cámara hiperbárica", "En Dahab existe un centro hiperbárico con cámara para seis pacientes. En 2012 su director se quejaba de que había unos 30 minutos por pista de tierra desde el Blue Hole y de que no había ambulancia en el lugar."],
   ["Autoridades", "Policía y familia: hay que comunicar y documentar cada recuperación."]], [5.6, 10.8])

H1("12. Cómo debería hacerse una recuperación profunda")
P("Tarek Omar es un caso excepcional: un buceador con miles de horas en ese pozo concreto. Su método funciona en sus manos, "
  "pero tiene riesgos que la buena práctica intenta reducir. La regla de oro de cualquier equipo de rescate es "
  "<b>no crear más víctimas</b>: un cuerpo ya no se puede salvar, y la vida del buceador que lo busca sí.")
H2("Principios de buena práctica")
N(["<b>Decidir si merece la pena.</b> Recuperar un cuerpo es una operación de riesgo sin vida que salvar. Se valora con la familia y las autoridades. A veces lo correcto es no bajar, y la familia puede preferir que los restos se queden en el mar.",
   "<b>Planificación y roles.</b> Antes de entrar al agua se asignan funciones: buceador de recuperación, buceadores de apoyo en las paradas, responsable de superficie y comunicaciones.",
   "<b>Gases adecuados</b> (trimix y gases de descompresión), <b>con reserva</b>: la regla de los tercios o planes de gas más conservadores.",
   "<b>Búsqueda ordenada.</b> Partir del último punto conocido y usar patrones de búsqueda (en U, circulares o en líneas paralelas) con cabos de referencia.",
   "<b>Ascenso controlado del cuerpo.</b> El globo de elevación se dimensiona para el peso a subir. Por la ley de Boyle, un globo lleno a 40 m (5 bar) se expande cinco veces al llegar a superficie, así que hay que soltarlo lejos del buceador y nunca engancharse a él.",
   "<b>Evitar enredos.</b> Cabos cortos y ordenados, cortador siempre a mano y nada que cuelgue suelto.",
   "<b>Apoyo en la descompresión.</b> Buceadores de apoyo con gas extra en las paradas y una cámara hiperbárica preparada.",
   "<b>Respeto y documentación.</b> Tratar el cuerpo con dignidad, conservar el equipo para la investigación y entregarlo a las autoridades.",
   "<b>Cuidar a quien recupera.</b> Estas misiones dejan huella psicológica; Omar reconoce que aún le persigue el caso Lipski."])
H2("Una lección trágica: Dave Shaw (Sudáfrica, 2005)")
P("El caso de <b>Dave Shaw</b> muestra lo que puede salir mal. En enero de 2005 intentó recuperar el cuerpo de Deon Dreyer, un "
  "buceador muerto en 1994 en la cueva inundada de <b>Boesmansgat</b> (Sudáfrica), a <b>270 m</b>. Usaba un rebreather y varias "
  "mezclas de trimix, y llevaba una cámara para grabar la operación. Varias cosas fallaron a la vez:")
B(["El cuerpo de Dreyer flotaba, contra lo que se esperaba, porque dentro del traje seco se había transformado en <b>adipocira</b>, una sustancia jabonosa y ligera.",
   "Trabajando con las dos manos, Shaw no pudo colocar el cable de su linterna como hacía siempre, y los cabos de la bolsa del cuerpo se enredaron con él.",
   "El esfuerzo para soltarse, con un gas muy denso a esa profundidad, le provocó un fallo respiratorio (acumulación de CO<sub>2</sub>) y murió.",
   "Su amigo y buceador de apoyo, <b>Don Shirley</b>, estuvo a punto de morir y quedó con secuelas permanentes de equilibrio.",
   "Tres días después, al recoger los cabos, ambos cuerpos subieron enredados casi hasta la superficie."])
BOX("<b>Lecciones del caso Shaw para cualquier recuperación:</b> el estado del cuerpo puede sorprender, los cabos son un peligro "
    "mortal, el esfuerzo físico en profundidad dispara el CO<sub>2</sub> y siempre hace falta un plan para abortar la misión. "
    "Comparado con esto, el método de Omar de liberarse del cuerpo a 40 m con un globo es una forma sensata de reducir el "
    "tiempo de carga.")
H2("Comparación: método de Omar frente a protocolo ideal")
T([["Aspecto", "Método de Omar (2012)", "Protocolo recomendado"],
   ["Equipo humano", "Él solo en el fondo; equipo en superficie", "Buceador principal más apoyo en profundidad y en las paradas"],
   ["Tiempo de fondo", "~5 minutos", "Lo mínimo posible, planificado con margen"],
   ["Subida del cuerpo", "Lo carga hasta 40 m y lo envía con un globo", "Igual, con globo dimensionado y soltado lejos del buceador"],
   ["Descompresión", "Hasta ~3 h", "Con gas de reserva, apoyo y cámara hiperbárica preparada"],
   ["Conocimiento del lugar", "Excepcional: es su pozo desde hace 30 años", "Imprescindible un reconocimiento previo"],
   ["Riesgo principal", "Incidente en solitario a más de 100 m", "Reducido por la redundancia de personas y gas"]], [3.8, 6, 6.6])

# ======================= PARTE IV =======================
story.append(PageBreak()); story.append(Spacer(1, 7 * cm))
story.append(Paragraph("PARTE IV<br/>Contexto y conclusiones", ss["part"])); story.append(PageBreak())

H1("13. El «cementerio de buceadores»")
P("Junto al Blue Hole hay placas en la roca en memoria de buceadores fallecidos. En 2012 Der Spiegel contó 14. "
  "<b>No existe un registro oficial</b> y las cifras varían mucho:")
T([["Fuente", "Cifra", "Periodo"],
   ["Tarek Omar en Der Spiegel (2012)", "más de 130", "1997–2012 (unos 8 al año)"],
   ["Comunidad local y prensa turística", "hasta 200", "«en los últimos años»"],
   ["Undercurrent (2017)", "al menos 40 buceadores con botella", "desde 1980"],
   ["Placas en la costa (2012)", "14", "Solo las víctimas que tienen placa"]], [6.4, 5, 5])
P("Lo prudente es decir <b>«más de un centenar, sin cifra oficial»</b>. Las cifras altas probablemente incluyen ahogamientos de "
  "personas haciendo snorkel, ajenos al Arco.")
H2("Otros casos documentados")
T([["Año", "Persona", "Qué ocurrió"],
   ["1997", "Conor O'Regan y Martin Gara (Irlanda, 22 y 23 años)", "Encontrados abrazados a 102 m. Uno empezó a hundirse, el otro fue a ayudarle y ambos perdieron el conocimiento."],
   ["2000", "Yuri Lipski (22 años)", "El caso de este estudio, a ~115 m."],
   ["2011", "Igor Shalo (Rusia)", "Buceador técnico con unas 400 inmersiones. Bajó a 150 m con poca experiencia en descompresión, tuvo problemas respiratorios a 130 m y subió sin paradas. Murió en la inmersión número 401."],
   ["2017", "Stephen Keenan (Irlanda, 39 años)", "Buceador de seguridad de apnea. Murió tras rescatar a la campeona Alessia Zecchini en el Arco. Lo cuenta el documental de Netflix <i>The Deepest Breath</i> (2023)."]], [1.4, 5, 10])
BOX("<b>Lección del caso Shalo:</b> los buceadores técnicos también mueren. Él no bajó en vertical a la profundidad prevista, tocó "
    "fondo a 120 m (primer error), siguió hasta 150 m nadando sobre el fondo (segundo error, que le costó fuerzas, tiempo y gas) "
    "y, al sentir que se ahogaba, subió sin hacer las paradas. La disciplina importa tanto como el equipo.")

H1("14. Cómo se bucea el Arco de forma segura")
T([["Lo que hizo Lipski", "Lo que hace un buceador técnico"],
   ["Aire (21 % O<sub>2</sub>, 79 % N<sub>2</sub>)", "Trimix: menos nitrógeno (menos narcosis) y menos oxígeno (sin toxicidad)"],
   ["Una sola botella", "Dos botellas en la espalda más botellas de etapa y de descompresión"],
   ["Sin plan de gas", "Planificación con reservas (regla de los tercios)"],
   ["Solo", "En equipo, con un plan acordado y señales"],
   ["Descenso libre en el azul", "Descenso controlado con cabo guía y referencia de profundidad"],
   ["Sin descompresión", "Paradas planificadas con ordenador o tablas"],
   ["Titulación recreativa", "Titulación técnica (Tech 60 o superior) y experiencia progresiva"]], [6, 10.4])
H2("Aire frente a trimix a 115 m (cálculo propio)")
T([["Parámetro a 115 m", "Aire", "Trimix 10/70", "Comentario"],
   ["ppO<sub>2</sub>", "2,62 bar", "1,25 bar", "El trimix queda por debajo de 1,4 bar"],
   ["Profundidad narcótica equivalente (END)", "115 m", "~22 m", "Con trimix, la narcosis equivale a estar a unos 22 m con aire"],
   ["Densidad del gas", "15,3 g/L", "~6,5 g/L", "Incluso el trimix está al límite: por eso a esas profundidades se usa más helio o rebreather"]],
  [5.2, 2.6, 2.8, 5.8])
P("<b>END</b> (<i>equivalent narcotic depth</i>) indica a qué profundidad con aire equivale la narcosis de una mezcla. Para el "
  "trimix 10/70, que tiene un 20 % de nitrógeno: ppN<sub>2</sub> = 0,20 × 12,5 = 2,5 bar; con aire, eso ocurre a "
  "(2,5 / 0,79 − 1) × 10 ≈ 22 m.")

H1("15. Mitos frente a realidad")
T([["Mito", "Realidad", "Confianza"],
   ["«Hay algo sobrenatural en el Blue Hole»", "Omar, que conoce cada rincón, lo niega: las causas son humanas y físicas", "0,95"],
   ["«Tarek era su compañero de inmersión»", "No buceó con él: le desaconsejó la inmersión y luego recuperó su cuerpo", "0,9"],
   ["«Grabó el momento exacto de su muerte»", "Grabó el descenso y los minutos finales; el instante de la muerte no se ve con claridad", "0,7"],
   ["«Era un principiante»", "Era instructor, pero no buceador técnico", "0,9"],
   ["«Llevaba una botella de oxígeno»", "Llevaba aire comprimido. El oxígeno puro sería mortal a esa profundidad", "0,85"],
   ["«Se quedó sin aire y ya está»", "Lo más probable es una combinación de narcosis, CO<sub>2</sub>, oxígeno tóxico, exceso de lastre y pánico", "0,75"],
   ["«El Blue Hole es el lugar más peligroso del mundo»", "El pozo es un punto de buceo normal; el peligro es el Arco por debajo de 50 m", "0,9"],
   ["«Han muerto 200 personas»", "No hay registro oficial; las estimaciones van de 40 a 200", "0,8"],
   ["«Al final del vídeo lo ataca una anguila»", "Teoría publicada en GitHub en 2019 sin confirmación; probablemente pareidolia", "0,9 de que es falso"]], [5, 9, 2.4])

H1("16. Contraste de fuentes")
T([["Dato", "Versión A", "Versión B", "Conclusión"],
   ["Fecha", "28/04/2000 (Wikipedia, placa)", "08/04/2000 (blog)", "28 de abril"],
   ["Profundidad", "115 m (cuerpo, Omar)", "91,6 m (ordenador en el vídeo) / 111 m", "Tocó fondo hacia 92 m; el cuerpo estaba a ~115 m"],
   ["Techo del Arco", "52 m (Der Spiegel)", "55–56 m (Wikipedia)", "52–56 m según el punto de medida"],
   ["Descubrimiento", "1968, buceadores de Alex Shell", "1962, pilotos en helicóptero", "Avistamiento aéreo y primera inmersión, compatibles"],
   ["Récord de Omar", "209 m", "220 m", "Más de 200 m"],
   ["Cuerpos recuperados por Omar", "«Perdió la cuenta» / más de 20", "9", "Sin cifra fiable"],
   ["Quién pidió recuperarlo", "La madre", "El padre (blog)", "La madre lo pidió; el padre dio las gracias"],
   ["Muertes totales", "más de 130 en 15 años", "40 / 200", "Más de 100, sin registro oficial"]], [3.2, 4.4, 4.4, 4.4])

H1("17. Glosario técnico")
T([["Término", "Significado"],
   ["Adipocira", "Sustancia grasa y jabonosa que se forma en cuerpos que pasan mucho tiempo en agua fría. Puede hacer que floten."],
   ["Apnea (freediving)", "Buceo aguantando la respiración, sin botella."],
   ["Arco (The Arch)", "Túnel de ~26 m que une el Blue Hole con el mar abierto, con el techo a 52–56 m."],
   ["bar", "Unidad de presión. 1 bar es aproximadamente la presión de la atmósfera al nivel del mar."],
   ["Blanqueamiento de coral", "Pérdida de las microalgas (zooxantelas) del coral por estrés térmico. El coral se queda blanco y puede morir."],
   ["Blue hole", "Dolina submarina: pozo vertical en roca caliza o arrecife inundado al subir el mar."],
   ["Botella de etapa (stage)", "Botella extra colgada al costado con gas para una fase de la inmersión."],
   ["Buceo técnico", "Buceo más allá de 40 m, con gases especiales, descompresión obligatoria o entornos con techo."],
   ["Cámara hiperbárica", "Recinto presurizado para tratar la enfermedad descompresiva con oxígeno a presión."],
   ["Chaleco compensador (BCD)", "Chaleco que se infla con gas de la botella para ajustar la flotabilidad."],
   ["CO<sub>2</sub> / hipercapnia", "Exceso de dióxido de carbono en sangre: ahogo, ansiedad, confusión y pérdida de conciencia."],
   ["Cuenca de tracción (pull-apart)", "Depresión que se forma donde una falla de desgarre se escalona y la corteza se estira."],
   ["Densidad del gas", "Masa por litro del gas respirado. Sube con la profundidad y dificulta la respiración."],
   ["Descompresión", "Paradas durante el ascenso para eliminar el gas disuelto sin que forme burbujas."],
   ["Dolina", "Pozo o depresión formado por disolución de roca caliza."],
   ["END", "Profundidad narcótica equivalente: a qué profundidad con aire equivale la narcosis de una mezcla."],
   ["Endémico", "Que solo vive en una región concreta."],
   ["Enfermedad descompresiva (EDC)", "Lesiones por burbujas de gas en sangre y tejidos al subir demasiado rápido."],
   ["Entorno con techo", "Lugar donde no se puede subir en vertical: cuevas, pecios, túneles."],
   ["Falla transformante", "Fractura de la corteza donde dos bloques se deslizan lateralmente."],
   ["Globo de elevación (lift bag)", "Bolsa que se llena de gas bajo el agua para subir objetos o cuerpos."],
   ["Helio", "Gas inerte, ligero y casi sin efecto narcótico. Sustituye al nitrógeno en mezclas profundas."],
   ["Lastre", "Pesos de plomo para compensar la flotabilidad del cuerpo y del traje."],
   ["Ley de Boyle", "A temperatura constante, el volumen de un gas es inversamente proporcional a la presión."],
   ["Ley de Dalton", "La presión total de una mezcla es la suma de las presiones parciales de cada gas."],
   ["Ley de Henry", "La cantidad de gas disuelto en un líquido es proporcional a su presión parcial."],
   ["«Ley del Martini»", "Regla informal: un martini de narcosis por cada 10 m por debajo de 20 m."],
   ["Mesofótico", "Zona de poca luz, aproximadamente entre 30–40 m y 150 m."],
   ["MOD", "Profundidad máxima operativa: donde la ppO<sub>2</sub> de una mezcla supera el límite seguro."],
   ["Narcosis por nitrógeno", "Efecto anestésico del nitrógeno a alta presión. Parecido a la embriaguez; desaparece al subir."],
   ["Neopreno", "Material del traje con burbujas de gas; se comprime con la profundidad."],
   ["Nitrox", "Aire enriquecido con más del 21 % de oxígeno, útil a profundidades moderadas."],
   ["Pareidolia", "Tendencia a ver formas conocidas en imágenes difusas."],
   ["Presión parcial (ppO<sub>2</sub>, ppN<sub>2</sub>)", "Parte de la presión total que corresponde a un gas de la mezcla."],
   ["Rebreather (circuito cerrado)", "Equipo que recicla el gas exhalado, elimina el CO<sub>2</sub> y añade oxígeno."],
   ["Refugio térmico", "Zona donde los corales resisten mejor el calentamiento que en otros lugares."],
   ["Regulador", "Aparato que reduce la presión de la botella a la ambiente para respirar."],
   ["Rift", "Zona donde la corteza se fractura y separa; puede acabar formando un océano."],
   ["SAC", "Consumo de gas por minuto expresado en litros de superficie."],
   ["Saddle", "Abertura somera (~6 m) del Blue Hole hacia el mar."],
   ["Salinidad (‰)", "Gramos de sal por kilo de agua. El mar Rojo ronda 40 ‰."],
   ["Sobreexpansión pulmonar", "Rotura pulmonar por subir aguantando la respiración."],
   ["Tech 60", "Nivel de formación técnica para bucear hasta 60 m."],
   ["Toxicidad del oxígeno (SNC)", "Efecto tóxico del O<sub>2</sub> por encima de ~1,4–1,6 bar; puede causar convulsiones."],
   ["Trimix", "Mezcla de oxígeno, helio y nitrógeno para inmersiones profundas."],
   ["Zooxantelas", "Microalgas que viven dentro del coral y le dan alimento por fotosíntesis."]], [5, 11.4])

H1("18. Lecciones para cualquier buceador")
N(["<b>Bucea dentro de tu formación</b>, no de tu ego.",
   "<b>Nunca vayas solo</b> a profundidad, y menos con techo o sin fondo.",
   "<b>El aire tiene límite:</b> por el oxígeno, hacia 56–66 m; por la densidad del gas, ya hacia 32–41 m.",
   "<b>La narcosis no avisa.</b> Si notas algo raro, sube unos metros.",
   "<b>Lastre justo:</b> el exceso de plomo convierte cualquier problema en una emergencia.",
   "<b>Escucha a los expertos locales.</b> A Lipski le advirtieron dos veces.",
   "<b>Planifica el gas</b> con reservas para lo imprevisto.",
   "<b>La fama de un lugar no es una razón para bucearlo.</b>",
   "<b>Respeta el arrecife:</b> lo que hace especial a Dahab está entre 0 y 30 m."])

H1("19. Metodología, límites y nivel de confianza")
B(["Se ha dividido el tema en partes (lugar, ecología, accidente, física, recuperación, contexto) y cada dato se ha contrastado en al menos dos fuentes independientes cuando ha sido posible.",
   "Se han consultado fuentes en inglés, alemán (traducido), árabe y español.",
   "Los cálculos (presión, ppO<sub>2</sub>, MOD, END, densidad, consumo y flotabilidad) son propios y se han comprobado con un programa.",
   "Las ilustraciones son de elaboración propia. Los mapas usan datos de costa de Natural Earth (dominio público).",
   "Todo el texto es redacción propia. Las fuentes se citan al final y no se copian párrafos de ninguna.",
   "<b>Límites:</b> no se ha visto el vídeo de The Wild Project ni la grabación original; no hay autopsia publicada; varias cifras sobre Tarek Omar no coinciden entre fuentes."])
T([["Bloque", "Confianza"],
   ["Geografía, geología y ecología", "0,9"], ["Hechos básicos del accidente", "0,9"], ["Física y fisiología (cálculos)", "0,95"],
   ["Secuencia exacta del accidente", "0,65"], ["Causa concreta de la muerte", "0,6 (multifactorial, sin confirmar)"],
   ["Biografía de Tarek Omar", "0,75"], ["Método de recuperación de Omar", "0,8"], ["Cifras de víctimas", "0,5"]], [10, 6.4])

H1("20. Fuentes")
src = [
 "Wikipedia (en). <i>Blue Hole (Red Sea)</i>. https://en.wikipedia.org/wiki/Blue_Hole_(Red_Sea)",
 "Grossekathöfer, M. (13/07/2012). <i>The Blue Hole in the Red Sea Is the Deadliest Dive Site in the World</i>. Der Spiegel International. https://www.spiegel.de/international/zeitgeist/the-blue-hole-in-the-red-sea-is-the-deadliest-dive-site-in-the-world-a-844099.html",
 "Ghoneim, N. (20/10/2016). <i>Egyptian Diver Tarek Omar: The Keeper of Dahab's Divers' Cemetery</i>. CairoScene. https://cairoscene.com/lifestyle/egyptian-diver-tarek-omar-the-keeper-of-dahab-s-divers-cemetery",
 "Bower, E. (26/08/2017). <i>Top diver's death casts long shadow over deep beauty of the Blue Hole</i>. The Guardian. https://www.theguardian.com/world/2017/aug/26/blue-hole-red-sea-diver-death-stephen-keenan-dahab-egypt",
 "Al-Masry Al-Youm (14/10/2016). Reportaje sobre Tarek Omar, «Gigante de las profundidades» (en árabe). https://www.almasryalyoum.com/news/details/1592981",
 "Masrawy (29/09/2018). Reportaje sobre el «Sheikh de los buceadores» de Dahab (en árabe). https://www.masrawy.com/news/news_regions/details/2018/9/29/1435938",
 "Atlas Obscura / Slate (04/03/2014). <i>Diver's cemetery: the Blue Hole of Dahab</i>. https://www.slate.com/blogs/atlas_obscura/2014/03/04/diver_s_cemetery_the_blue_hole_of_dahab_on_the_red_sea_in_egypt.html",
 "Wikipedia (en). <i>Red Sea</i>, <i>Gulf of Aqaba</i>, <i>Dahab</i>, <i>Nitrogen narcosis</i>, <i>Dave Shaw</i>, <i>Stephen Keenan</i>.",
 "UNESCO. <i>Coral Reefs of the Gulf of Aqaba and the Red Sea in the Kingdom of Saudi Arabia</i> (lista indicativa, 2024). https://whc.unesco.org/en/tentativelists/6701/",
 "Bellworthy, J. y Fine, M. (2021). <i>Warming resistant corals from the Gulf of Aqaba live close to their cold-water bleaching threshold</i>. PeerJ 9:e11100. https://pmc.ncbi.nlm.nih.gov/articles/PMC8005291/",
 "Marine Insight. <i>Gulf of Aqaba facts</i>. https://www.marineinsight.com/gulf-of-aqaba-facts/",
 "Circle Divers. <i>Bells – Blue Hole dive site</i>. https://www.circledivers.com/diving-in-dahab/dive-sites/bells-blue-hole-dive-site-dahab",
 "Dive Planner Pro. <i>Blue Hole Dahab</i>. https://www.diveplannerpro.com/spots/eg/dahab/blue-hole-dahab-eg",
 "WorkSafe New Zealand. <i>Breathing oxygen and enriched mixtures while diving</i>.",
 "TDI. <i>Avoid CNS Oxygen Toxicity While Diving Nitrox</i>.",
 "DDRC Healthcare. <i>Gas Density and SCUBA</i> (resume a Anthony y Mitchell, 2016). https://www.ddrc.org/gas-density-and-scuba/",
 "Dressel Divers (2025). <i>Underwater Recovery at the Limit</i>. https://www.dresseldivers.com/blog/underwater-recovery/",
 "Undercurrent (2017). <i>Dangerous dive site</i>. Showcaves.com. <i>Blue Hole, Dahab</i>.",
 "The Wild Project (30/10/2026). <i>He Recorded His Own DEATH Underwater</i> (clip del episodio #389). https://www.youtube.com/watch?v=qArQMyX28PA",
 "Natural Earth / world-atlas (datos de costa para los mapas, dominio público).",
]
for s_ in src: story.append(Paragraph(s_, ss["bul"], bulletText="•"))

H1("21. Galería de fotos con licencia libre")
P("Estas fotografías de Wikimedia Commons tienen licencias libres (CC BY, CC BY-SA o dominio público) y pueden incluirse en "
  "una próxima edición citando al autor. Cada enlace lleva a la página con el autor y la licencia exactos.")
gal = [
 ["Vista del Blue Hole desde la costa", "Gustavo Gerdel · CC BY-SA 4.0", "File:Dahab_Blue_Hole.jpg"],
 ["Blue Hole visto desde arriba", "Petar Milošević · CC BY-SA 4.0", "File:Blue_Whole,_Dahab.jpg"],
 ["Plano del Blue Hole", "Usellermann · CC BY-SA 3.0 / GFDL", "File:Blue_Hole_map.png"],
 ["Buceador técnico bajo el Arco (2009)", "Tommi Salminen · CC BY-SA 3.0", "File:Dahab_Blue_Hole_Arc_2009.jpg"],
 ["Placas conmemorativas", "D T G · CC BY 3.0", "File:EGYPT_Dahab_Blue_Hole_memorials.JPG"],
 ["Apneístas en el Blue Hole (2006)", "Lars Plougmann · CC BY-SA 2.0", "File:Blue_Hole_Sinai-Free_Diving.jpg"],
 ["Buceador en lo alto de The Bells", "Ver página", "File:Diver_at_the_Top_of_The_Bells.jpg"],
 ["Playa de Dahab", "Ver página", "File:Dahab_Beach.jpg"],
 ["Costa de Dahab", "Ver página", "File:Dahab_shoreline.jpg"],
 ["Panorámica de Dahab", "Ver página", "File:Dahab_panorama.jpg"],
 ["Dahab desde el avión", "Ver página", "File:Dahab_from_airplane.jpg"],
 ["Jardín de anguilas", "Ver página", "File:Dahab_-_Eel_Garden.jpg"],
 ["Tortuga verde en Dahab", "Hatem Moushir · ver página", "File:Chelonia_mydas_at_Dahab_by_Hatem_Moushir.jpg"],
 ["Pez Napoleón en el mar Rojo", "Ver página", "File:Napoleon_(Cheilinus_undulatus)_im_Roten_Meer._DSCF1669WI.jpg"],
 ["Pez león en el mar Rojo", "Ver página", "File:Lion_fish_in_the_red_sea.jpg"],
 ["Anthias", "Ver página", "File:Anthia_goldfish.JPG"],
 ["Pez mariposa endémico", "Ver página", "File:Crown_Butterflyfish,_Chaetodon_paucifasciatus,_Red_Sea_(36204827650).jpg"],
 ["Raya de puntos azules", "Ver página", "File:Blue_spotted_stingray_in_the_red_sea.jpg"],
 ["Arrecife del golfo de Eilat", "Ver página", "File:Gulf_of_Eilat_(Red_Sea)_coral_reefs.jpg"],
 ["Buceador con trimix a 108 m", "Reginestein / A. Hache · CC BY-SA 3.0", "File:Plongeur_Trimix.jpg"],
 ["Chaleco compensador", "Mark.murphy · dominio público", "File:Bcd_-_stab.JPG"],
]
T([["Foto", "Autor y licencia", "Página en commons.wikimedia.org/wiki/…"]] + gal, [5.2, 4.6, 6.6])
P("<i>Este documento: texto e ilustraciones propias bajo licencia CC BY-SA 4.0.</i>")
story.append(Spacer(1, 1 * cm))
P("<para alignment='center'><i>En memoria de quienes no volvieron del Blue Hole.</i></para>")

doc.multiBuild(story)
print("PDF:", OUT)
