"""Ilustraciones propias para el estudio Lipski / Blue Hole (matplotlib)."""
import json, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch, Rectangle, FancyArrowPatch
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
GEO = sys.argv[2] if len(sys.argv) > 2 else "region.geojson"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titleweight": "bold", "axes.titlesize": 12})
SEA = "#cfe6f2"; LAND = "#efe6d4"; COAST = "#8a7a5c"; INK = "#1f2d3a"
DEEP = "#0b3d5c"; ACC = "#d64545"; WARN = "#f08a24"; OK = "#2f8f5b"

feats = json.load(open(GEO))["features"]

def draw_land(ax):
    for f in feats:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = np.array(poly[0])
            ax.add_patch(Polygon(ring, closed=True, fc=LAND, ec=COAST, lw=0.5))

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------- 1. Mapa general: mar Rojo ----------
fig, ax = plt.subplots(figsize=(6.2, 7))
ax.set_facecolor(SEA); draw_land(ax)
ax.set_xlim(31, 45); ax.set_ylim(11.5, 31)
ax.set_aspect(1 / np.cos(np.radians(21)))
lab = dict(color=INK, fontsize=9, ha="center")
for t, x, y in [("EGYPT", 31.8, 25.5), ("SUDAN", 33.6, 18.5), ("ERITREA", 38.3, 15.2),
                ("SAUDI ARABIA", 41.8, 23.5), ("YEMEN", 43.6, 15.3), ("JORDAN", 36.9, 30.4)]:
    ax.text(x, y, t, fontweight="bold", **lab)
ax.text(38.2, 20.3, "RED SEA", color=DEEP, fontsize=13, fontweight="bold", rotation=-58, ha="center")
ax.text(33.0, 28.7, "Sinai", color=INK, fontsize=9, style="italic", ha="center")
ax.text(32.3, 29.9, "Gulf of\nSuez", color=DEEP, fontsize=7.5, ha="center")
ax.text(35.4, 27.4, "Gulf of\nAqaba", color=DEEP, fontsize=7.5, ha="left")
ax.text(43.6, 12.2, "Bab el-Mandeb", color=DEEP, fontsize=7.5, ha="center")
ax.add_patch(Rectangle((33.9, 27.8), 1.2, 1.8, fill=False, ec=ACC, lw=1.6))
ax.plot(34.537, 28.572, "o", color=ACC, ms=5)
ax.annotate("Dahab · Blue Hole", (34.537, 28.572), (36.2, 29.4), fontsize=8.5, color=ACC,
            arrowprops=dict(arrowstyle="-", color=ACC, lw=0.8))
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.set_title("The Red Sea and the location of Dahab")
ax.grid(color="white", lw=0.5)
save(fig, "mapa_mar_rojo")

# ---------- 2. Zoom: golfo de Aqaba ----------
fig, ax = plt.subplots(figsize=(6.2, 7.4))
ax.set_facecolor(SEA); draw_land(ax)
ax.set_xlim(33.85, 35.25); ax.set_ylim(27.65, 29.65)
ax.set_aspect(1 / np.cos(np.radians(28.6)))
pts = [("Eilat", 34.95, 29.56, "r"), ("Aqaba", 35.0, 29.53, "R"), ("Taba", 34.89, 29.49, "l"),
       ("Nuweiba", 34.66, 28.98, "l"), ("Ras Abu Galum", 34.56, 28.70, "l"),
       ("Dahab", 34.513, 28.494, "l"), ("Sharm el-Sheikh", 34.33, 27.91, "l"), ("Haql", 34.95, 29.29, "r")]
for n, x, y, side in pts:
    ax.plot(x, y, "o", color=INK, ms=3.5)
    ha = "right" if side == "l" else "left"
    dx = -0.03 if side == "l" else 0.03
    ax.text(x + dx, y, n, fontsize=8.5, ha=ha, va="center", color=INK)
ax.plot(34.537, 28.572, "*", color=ACC, ms=14, mec="white")
ax.annotate("BLUE HOLE\n28.57° N · 34.54° E", (34.537, 28.572), (34.85, 28.45), fontsize=9,
            color=ACC, fontweight="bold", arrowprops=dict(arrowstyle="->", color=ACC, lw=1))
ax.text(34.48, 27.98, "Strait\nof Tiran", fontsize=8, color=DEEP, ha="center", style="italic")
ax.text(34.88, 28.75, "Gulf of Aqaba\nmax. depth ~1,850 m", fontsize=9, color=DEEP,
        ha="center", fontweight="bold", rotation=62)
ax.text(34.15, 28.95, "SINAI\n(Egypt)", fontsize=10, color=INK, fontweight="bold", ha="center")
ax.text(35.12, 28.25, "SAUDI\nARABIA", fontsize=9, color=INK, fontweight="bold", ha="center")
ax.set_title("Gulf of Aqaba: Dahab and the Blue Hole")
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.grid(color="white", lw=0.5)
# escala 20 km
km = 20 / (111.32 * np.cos(np.radians(28.6)))
ax.plot([33.92, 33.92 + km], [27.72, 27.72], color=INK, lw=3)
ax.text(33.92 + km / 2, 27.75, "20 km", ha="center", fontsize=8)
save(fig, "mapa_golfo_aqaba")

# ---------- 3. Corte del Blue Hole ----------
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlim(-60, 175); ax.set_ylim(140, -12)
# agua por profundidad (gradiente)
for i in range(140):
    c = plt.cm.Blues(0.25 + 0.7 * i / 140)
    ax.axhspan(i, i + 1, color=c, lw=0)
ax.axhspan(-12, 0, color="#f7fbff", lw=0)
# arrecife / roca
rock = "#b9a27a"
left = [(-60, 0), (-40, 0), (-35, 20), (-25, 60), (-18, 100), (-10, 140), (-60, 140)]
ax.add_patch(Polygon(left, fc=rock, ec="#7a6648"))
floor = [(-30, 140), (-25, 104), (0, 100), (30, 103), (45, 100), (60, 105), (95, 102), (121, 120), (125, 140)]
ax.add_patch(Polygon(floor, fc="#d8c79a", ec="#7a6648"))
# bloque de arrecife entre el pozo y el mar: arriba la Saddle (6 m), abajo el Arco (52-56 m)
ax.add_patch(Polygon([(95, 6), (121, 6), (121, 56), (95, 52)], fc=rock, ec="#7a6648"))
ax.annotate("", (95, 3), (121, 3), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
ax.text(108, -4, "The Saddle (~6 m)", ha="center", fontsize=8.5, color=INK)
# etiquetas
ax.text(30, -4, "Sinkhole · Ø ~70–80 m", ha="center", fontsize=9, color=INK, fontweight="bold")
ax.text(155, -4, "Open sea", ha="center", fontsize=9, color=INK, fontweight="bold")
ax.annotate("", (95, 61), (121, 64), arrowprops=dict(arrowstyle="<->", color="#ffd166", lw=1.8))
ax.text(108, 72, "ARCH · 26 m tunnel\nceiling at 52–56 m", ha="center", fontsize=8.5, color="white", fontweight="bold")
ax.axhline(40, color=OK, ls="--", lw=1.2); ax.text(-58, 38.5, "40 m · recreational limit", color="white", fontsize=8.5, fontweight="bold")
ax.axhline(56.7, color=WARN, ls="--", lw=1.2); ax.text(-58, 55.2, "56.7 m · O₂ in air exceeds 1.4 bar", color="white", fontsize=8.5, fontweight="bold")
ax.plot(10, 115, "X", color=ACC, ms=11, mec="white")
ax.text(14, 112, "Yuri Lipski\n~115 m", color="white", fontsize=9, fontweight="bold")
ax.plot(-5, 102, "o", color="#ffd166", ms=7, mec=INK)
ax.text(-3, 95, "O'Regan and Gara\n(1997) 102 m", color="white", fontsize=8)
ax.text(150, 128, "→ 800–1,000 m", color="white", fontsize=8.5, ha="center")
ax.set_ylabel("Depth (m)"); ax.set_xlabel("Approximate horizontal distance (m) · schematic, not to exact scale")
ax.set_title("Schematic cross-section of the Dahab Blue Hole")
save(fig, "corte_blue_hole")

# ---------- 4. Zonas de profundidad, luz y vida ----------
import textwrap
fig = plt.figure(figsize=(9.5, 8.2))
axL = fig.add_axes([0.07, 0.05, 0.16, 0.88]); axR = fig.add_axes([0.25, 0.05, 0.74, 0.88])
axL.set_ylim(125, 0); axL.set_xlim(0, 1)
for i in range(125):
    axL.axhspan(i, i + 1, color=plt.cm.Blues(0.2 + 0.75 * i / 125), lw=0)
light = [("R", 5, "#d62828"), ("N", 15, "#f77f00"), ("A", 25, "#fcbf49"), ("V", 40, "#4caf50")]
for k, (n, dd, c) in enumerate(light):
    axL.plot([0.12 + k * 0.17] * 2, [0, dd], color=c, lw=6, solid_capstyle="butt")
axL.text(0.5, 50, "Red light\nfades by\n~5 m, orange\nby ~15 m,\nyellow by\n~25 m and\ngreen by\n~40 m. Below,\nonly blue\nremains.", fontsize=7, ha="center", va="top", color=INK,
         bbox=dict(fc="white", ec="none", alpha=0.75))
axL.set_xticks([]); axL.set_ylabel("Depth (m)")
axL.axhline(40, color=OK, ls="--", lw=1.2); axL.axhline(55, color=WARN, ls="--", lw=1.2)
axL.plot(0.5, 115, "X", color=ACC, ms=10, mec="white")
axR.set_xlim(0, 1); axR.set_ylim(5, 0); axR.axis("off")
zones = [
    (0, 10, "Shallow reef and lagoon", "Hard corals (Acropora, Porites, Stylophora), fire coral, Red Sea clownfish in their anemones, butterflyfish (Chaetodon paucifasciatus, endemic), sohal surgeonfish, sea urchins and blue-spotted rays on the sand. This is the snorkelling zone."),
    (10, 30, "Reef wall (recreational zone)", "Clouds of orange anthias, Napoleon wrasse, giant morays, lionfish, stonefish, hawksbill and green turtles, cornetfish and groupers. Barracuda and trevally in the blue. Sea fans and soft corals."),
    (30, 40, "Deep wall", "Black coral, gorgonian fans and sponges. Fewer but larger fish. 40 m is the limit of recreational diving."),
    (40, 60, "Upper mesophotic zone: the ARCH", "Dim blue light. Flat corals adapted to catch little light. The Arch ceiling is here (52–56 m) and, at 56.7 m, air starts to become toxic."),
    (60, 125, "Twilight and sandy bottom", "Almost no light. Few reef fish; occasionally a passing shark or pelagic fish. Sand and debris on the bottom. Lipski came to rest at about 115 m."),
]
cols = ["#e8f4fa", "#d3eaf5", "#bcdcee", "#9cc6e2", "#7aa9cf"]
for i, (top, bot, title, desc) in enumerate(zones):
    y0 = i + 0.06
    axR.add_patch(FancyBboxPatch((0.03, y0), 0.95, 0.86, boxstyle="round,pad=0.01", fc=cols[i], ec="#8fb0c8", transform=axR.transData))
    axR.text(0.06, y0 + 0.12, f"{top}–{bot} m · {title}", fontsize=10.5, fontweight="bold", va="top", color=DEEP)
    axR.text(0.06, y0 + 0.36, textwrap.fill(desc, 86), fontsize=8.6, va="top", color=INK)
    # conector desde la columna de profundidad
    yl = (top + bot) / 2
    con = matplotlib.patches.ConnectionPatch((1, yl), (0.03, y0 + 0.43), "data", "data", axesA=axL, axesB=axR, color="#8899aa", lw=0.8)
    fig.add_artist(con)
fig.suptitle("What you see at each depth in Dahab", fontweight="bold", fontsize=13, y=0.985)
save(fig, "zonas_vida")

# ---------- 5. ppO2 y densidad: aire vs trimix ----------
d = np.linspace(0, 120, 241); P = 1 + d / 10
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
a1.plot(d, 0.21 * P, color=ACC, lw=2.2, label="Air (21% O₂)")
a1.plot(d, 0.10 * P, color=OK, lw=2.2, label="Trimix 10/70 (10% O₂)")
a1.axhline(1.4, color=WARN, ls="--"); a1.axhline(1.6, color=ACC, ls=":")
a1.text(2, 1.45, "1.4 bar (working limit)", fontsize=8, color=WARN); a1.text(2, 1.65, "1.6 bar (maximum)", fontsize=8, color=ACC)
a1.axvline(115, color="#555", lw=0.8); a1.text(113, 0.15, "115 m", rotation=90, fontsize=8, ha="right")
a1.set_xlabel("Depth (m)"); a1.set_ylabel("ppO₂ (bar)"); a1.set_title("Oxygen: when it becomes toxic")
a1.legend(fontsize=8, loc="upper left"); a1.grid(alpha=0.3)
rho_air = 1.225; rho_tmx = 0.10 * 1.429 + 0.70 * 0.1786 + 0.20 * 1.2506
a2.plot(d, rho_air * P, color=ACC, lw=2.2, label="Air")
a2.plot(d, rho_tmx * P, color=OK, lw=2.2, label="Trimix 10/70")
a2.axhline(5.2, color=WARN, ls="--"); a2.axhline(6.2, color=ACC, ls=":")
a2.text(2, 5.4, "5.2 g/L (recommended)", fontsize=8, color=WARN); a2.text(2, 6.5, "6.2 g/L (maximum)", fontsize=8, color=ACC)
a2.axvline(115, color="#555", lw=0.8)
a2.set_xlabel("Depth (m)"); a2.set_ylabel("Gas density (g/L)"); a2.set_title("Density: how hard it is to breathe")
a2.legend(fontsize=8, loc="upper left"); a2.grid(alpha=0.3)
fig.tight_layout(); save(fig, "gases")

# ---------- 6. Perfil de una misión de recuperación ----------
fig, ax = plt.subplots(figsize=(9.5, 4.6))
t = [0, 6, 11, 14, 20, 26, 32, 40, 52, 70, 95, 125, 160, 180, 182]
z = [0, 110, 110, 70, 40, 40, 30, 21, 15, 12, 9, 6, 6, 3, 0]
ax.plot(t, z, color=DEEP, lw=2.4)
ax.fill_between(t, z, 0, color=SEA, alpha=0.6)
ax.set_ylim(120, -8); ax.set_xlim(-3, 186)
notes = [(10, 75, "1. Fast descent\nalong the guideline"), (14, 113, "2. ~5 min on the bottom: locate and secure"),
         (30, 44, "3. At ~40 m: a lift bag\nsends the body to the surface"), (58, 27, "4. Decompression stops with gas switches"),
         (120, 15, "5. Long final stop on pure O₂"), (150, -3, "Surface ~3 h later")]
for x, y, s_ in notes:
    ax.text(x, y, s_, fontsize=8.5, color=INK, bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
ax.plot(20, 40, "o", color=WARN, ms=9, mec=INK)
ax.set_xlabel("Time (min)"); ax.set_ylabel("Depth (m)")
ax.set_title("Profile of a recovery at ~110 m (illustrative, based on Tarek Omar's description)", fontsize=11)
ax.grid(alpha=0.3)
save(fig, "perfil_recuperacion")

# ---------- 7. Cadena de errores ----------
fig, ax = plt.subplots(figsize=(10, 3.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
steps = ["Rejects training\nand advice", "Air instead\nof trimix", "A single\n12 L cylinder", "No buddy\nat depth",
         "12 kg of lead\n+ camera", "Uncontrolled\ndescent", "Narcosis + toxic\nO₂ + CO₂", "Panic and\nfixation", "Drowning"]
cols = ["#e9eef3"] * 6 + [ACC, WARN, INK]
pos = [(0.1 + i * 2.0, 1.85) for i in range(5)] + [(8.1 - i * 2.0, 0.25) for i in range(4)]
for i, (s_, c) in enumerate(zip(steps, cols)):
    x, y = pos[i]
    ax.add_patch(FancyBboxPatch((x, y), 1.7, 0.95, boxstyle="round,pad=0.04", fc=c, ec="#8899aa"))
    ax.text(x + 0.85, y + 0.475, s_, ha="center", va="center", fontsize=8.6,
            color="white" if c in (ACC, INK, WARN) else INK, fontweight="bold")
    if i < len(steps) - 1:
        x2, y2 = pos[i + 1]
        if y2 == y:
            a, b = ((x + 1.74, y + 0.475), (x2 - 0.04, y + 0.475)) if x2 > x else ((x - 0.04, y + 0.475), (x2 + 1.74, y + 0.475))
        else:
            a, b = (x + 0.85, y - 0.05), (x2 + 0.85, y2 + 0.99)
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color="#556", lw=1.3))
ax.set_title("The chain of errors (Swiss cheese model)")
save(fig, "cadena_errores")
print("ok")
