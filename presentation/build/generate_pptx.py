#!/usr/bin/env python3
"""Génère la présentation de conférence (pptx) - palette bleu marine / tons doux.
Version étendue (~1h, avec captures d'écran réelles) — passe "UI dynamique +
humour sur les slides" : les vannes qui vivaient seulement dans SCRIPT.md sont
maintenant visibles à l'écran, plus quelques tampons/badges pivotés et des
transitions de diapo pour casser la monotonie d'un deck qui défile trop sagement."""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
from lxml import etree

# ---------------------------------------------------------------- palette --
NAVY_DARK   = RGBColor(0x0B, 0x1D, 0x36)   # fond des slides "navy"
NAVY_MED    = RGBColor(0x18, 0x33, 0x59)   # cartes sur fond navy
NAVY_TEXT   = RGBColor(0x16, 0x28, 0x44)   # texte titre sur fond clair
CREAM       = RGBColor(0xF4, 0xF1, 0xE9)   # fond clair, doux pour les yeux
CREAM_CARD  = RGBColor(0xEA, 0xE6, 0xDA)   # cartes sur fond clair
INK         = RGBColor(0x33, 0x3A, 0x47)   # texte de corps sur fond clair
LIGHT_TEXT  = RGBColor(0xEF, 0xEC, 0xE3)   # texte sur fond navy
MUTED       = RGBColor(0x8B, 0x93, 0xA1)   # texte secondaire / légendes
GOLD        = RGBColor(0xC7, 0x9A, 0x52)   # accent principal (barres, puces, fonds sombres)
TEAL        = RGBColor(0x5C, 0x8C, 0x86)   # accent secondaire (tests)
TERRACOTTA  = RGBColor(0xBF, 0x6F, 0x5D)   # accent alerte douce (gap de couverture)
SAGE        = RGBColor(0x83, 0x9B, 0x74)   # accent "ok" doux (vert cassé, pas criard)

# Variantes "texte sur fond clair" des accents ci-dessus : mêmes teintes mais
# assombries pour rester lisibles sur CREAM/CREAM_CARD (contraste WCAG AA,
# >= 4.5:1 — les versions vives ci-dessus tombent autour de 2.3-3.3:1 sur
# fond crème et ne doivent servir qu'à des éléments non-textuels : barres,
# puces, pastilles).
MUTED_ON_LIGHT = RGBColor(0x5E, 0x66, 0x74)
GOLD_ON_LIGHT  = RGBColor(0x8A, 0x65, 0x30)
TEAL_ON_LIGHT  = RGBColor(0x35, 0x5C, 0x57)
TERRA_ON_LIGHT = RGBColor(0x8F, 0x45, 0x36)

# Variante de MUTED pour du texte posé sur une carte NAVY_MED (plutôt que sur
# NAVY_DARK) : MUTED tout court y retombe sous 4.5:1, celle-ci les repasse au-dessus.
MUTED_ON_DARK_CARD = RGBColor(0x9B, 0xA3, 0xB1)

_LIGHT_SAFE = {GOLD: GOLD_ON_LIGHT, TEAL: TEAL_ON_LIGHT, TERRACOTTA: TERRA_ON_LIGHT, MUTED: MUTED_ON_LIGHT}


def on_light(color):
    """Variante lisible d'une couleur d'accent quand elle sert de texte sur fond clair."""
    return _LIGHT_SAFE.get(color, color)

# Polices garanties présentes sans Office installé (vérifié sur cette
# machine : Calibri/Consolas sont absentes de macOS et retombent sur une
# police serif de repli au rendu — mauvaise surprise le jour J). Helvetica
# Neue et Menlo sont livrées avec macOS.
FONT = "Helvetica Neue"
FONT_MONO = "Menlo"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

SCREENSHOTS = "/Users/sidneycohen/dev/projects/couverture-code/presentation/screenshots"


def new_pres():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank(prs):
    layout = prs.slide_layouts[6]
    return prs.slides.add_slide(layout)


def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, left, top, width, height, color, line_color=None, line_w=None, shape=MSO_SHAPE.RECTANGLE):
    shp = slide.shapes.add_shape(shape, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(1)
    shp.shadow.inherit = False
    return shp


def textbox(slide, left, top, width, height, text, size, color, bold=False, italic=False,
            align=PP_ALIGN.LEFT, font=FONT, anchor=MSO_ANCHOR.TOP, line_spacing=1.0, spacing_after=0):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0

    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(spacing_after)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
        run.font.name = font
    return box


def eyebrow(slide, left, top, text, color=GOLD, dark=False):
    if not dark:
        color = on_light(color)
    textbox(slide, left, top, Inches(10), Inches(0.4), text.upper(), 13, color, bold=True, font=FONT)


def picture(slide, path, left, top, width, frame_color=CREAM_CARD, pad_in=0.05):
    w, h = Image.open(path).size
    height = Emu(int(width * h / w))
    pad = Inches(pad_in)
    rect(slide, Emu(int(left - pad)), Emu(int(top - pad)), Emu(int(width + 2 * pad)), Emu(int(height + 2 * pad)), frame_color)
    slide.shapes.add_picture(path, left, top, width=width, height=height)
    return height


def stamp(slide, left, top, width, height, text, fill, text_color, rotation=0, size=13,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_color=None):
    """Petit badge « tampon », pivoté, pour les clins d'œil visuels — le seul
    endroit du deck où on s'autorise une forme un peu bavarde plutôt qu'une
    barre d'accent silencieuse. À utiliser avec parcimonie : l'effet marche
    parce qu'il est rare."""
    shp = slide.shapes.add_shape(shape, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = Pt(1.25)
    shp.shadow.inherit = False
    shp.rotation = rotation
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text.upper()
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = text_color
    run.font.name = FONT
    return shp


def ghost_number(slide, left, top, text, size=260, color=NAVY_MED):
    """Chiffre géant en fond, très peu contrasté — pur repère typographique
    décoratif façon affiche, jamais lu comme du texte informatif (donc pas
    soumis aux règles de contraste WCAG)."""
    textbox(slide, left, top, Inches(4.5), Inches(3.5), text, size, color, bold=True)


_counter = [0]


def skip_footer():
    """Pour les slides titre/merci qui n'affichent pas de numero mais comptent quand meme."""
    _counter[0] += 1


def footer(slide, total, dark=False):
    _counter[0] += 1
    color = MUTED if dark else MUTED_ON_LIGHT
    textbox(slide, Inches(12.2), Inches(7.08), Inches(0.9), Inches(0.3),
            f"{_counter[0]:02d} / {total:02d}", 10, color, align=PP_ALIGN.RIGHT)
    textbox(slide, Inches(0.55), Inches(7.08), Inches(5.5), Inches(0.3),
            "COUVERTURE DE CODE — QUARKUS · JUNIT · CUCUMBER · JACOCO", 8, color)


def side_bar(slide, color=NAVY_DARK):
    rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, color)


def dot_grid(slide, x0, y0, rows=5, cols=6, color=GOLD):
    for row in range(rows):
        for col in range(cols):
            d = Inches(0.09)
            x = x0 + col * Inches(0.32)
            y = y0 + row * Inches(0.32)
            rect(slide, x, y, d, d, color, shape=MSO_SHAPE.OVAL)


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def add_transition(slide, kind="fade", speed="fast"):
    """Injecte un <p:transition> dans le XML de la slide (python-pptx n'a pas
    d'API haut niveau pour ça). C'est ce qui fait qu'en cliquant en vrai
    devant la salle, les slides s'enchaînent plutôt que de sauter sèchement —
    le seul levier de « dynamisme » qui se voit uniquement en mode
    présentation, pas sur un export PNG statique."""
    sld = slide._element
    csld = sld.find(f"{{{P_NS}}}cSld")
    idx = list(sld).index(csld) + 1
    transition = etree.Element(f"{{{P_NS}}}transition")
    transition.set("spd", speed)
    etree.SubElement(transition, f"{{{P_NS}}}{kind}")
    sld.insert(idx, transition)


TOTAL_SLIDES = 28
prs = new_pres()

# ============================================================ 1. TITRE ====
s = blank(prs)
bg(s, NAVY_DARK)
dot_grid(s, Inches(10.6), Inches(0.6))
rect(s, Inches(0.9), Inches(2.35), Inches(0.09), Inches(1.9), GOLD)
eyebrow(s, Inches(1.15), Inches(1.95), "Conférence technique (ou thérapie de groupe)", dark=True)
textbox(s, Inches(1.15), Inches(2.4), Inches(10.5), Inches(1.9),
        "La couverture de code,\nsans blabla", 46, LIGHT_TEXT, bold=True, line_spacing=1.02)
textbox(s, Inches(1.15), Inches(4.15), Inches(10.7), Inches(0.6),
        "Quarkus  ·  JUnit  ·  Cucumber  ·  Jacoco  ·  (un peu de Sonar en bonus)", 18, GOLD)
textbox(s, Inches(1.15), Inches(4.75), Inches(10.5), Inches(0.5),
        "Où l'on découvre que « 100 % de couverture » ne veut pas dire « 0 bug ».", 13.5, RGBColor(0xC8, 0xCF, 0xDA), italic=True)
textbox(s, Inches(1.15), Inches(6.55), Inches(8), Inches(0.5),
        "Ton nom — Date de la conférence", 13, MUTED)
stamp(s, Inches(10.15), Inches(5.55), Inches(2.35), Inches(0.85), "100% authentique",
      GOLD, NAVY_DARK, rotation=354, size=13.5)
skip_footer()
add_transition(s, kind="fade")

# ==================================================== 2. QUI SUIS-JE ======
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.7), "Avant de commencer")
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Qui suis-je ?", 32, NAVY_TEXT, bold=True)

bio = [
    ("Développeur Java", "Suffisamment d'années pour avoir déjà tout cassé au moins une fois. Deux, si on compte la prod.", GOLD),
    ("Écrit des tests", "Un ratio tests / code que je ne montrerai à personne — j'ai aussi un Utils.java de 2000 lignes qui préfère qu'on ne l'interroge pas.", TEAL),
    ("Ici pour une raison précise", "Vous convaincre de regarder VOTRE rapport de couverture. Le vrai. Pas celui que vous imaginez.", TERRACOTTA),
]
cx = Inches(0.9)
cw = Inches(3.62)
gap = Inches(0.28)
for i, (title, body, accent) in enumerate(bio):
    left = cx + i * (cw + gap)
    rect(s, left, Inches(2.55), cw, Inches(3.4), CREAM_CARD)
    rect(s, left, Inches(2.55), cw, Inches(0.09), accent)
    textbox(s, left + Inches(0.32), Inches(2.9), cw - Inches(0.6), Inches(0.8), title, 17, NAVY_TEXT, bold=True, line_spacing=1.1)
    textbox(s, left + Inches(0.32), Inches(3.75), cw - Inches(0.6), Inches(2.0), body, 13, INK, line_spacing=1.2)
stamp(s, Inches(6.75), Inches(2.32), Inches(1.55), Inches(0.55), "confidentiel",
      NAVY_DARK, GOLD, rotation=8, size=11.5)
textbox(s, Inches(0.9), Inches(6.25), Inches(11), Inches(0.4),
        "(personnalisez cette slide avec votre vraie bio avant le jour J)", 11, MUTED_ON_LIGHT, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 3. ICEBREAKER =======
s = blank(prs)
bg(s, NAVY_DARK)
ghost_number(s, Inches(9.3), Inches(2.7), "?", 300, NAVY_MED)
eyebrow(s, Inches(0.9), Inches(0.6), "Sondage (sans jugement)", dark=True)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Levez la main si...", 32, LIGHT_TEXT, bold=True)

items = [
    "...vous avez déjà écrit un test juste pour faire plaisir à la CI.",
    "...vous avez déjà vu 100 % de couverture sur un fichier plein de bugs.",
    "...vous ne savez pas, là, maintenant, ce que couvrent VOS tests.",
]
top = Inches(2.3)
for i, line in enumerate(items):
    rect(s, Inches(0.9), top + Inches(0.06), Inches(0.32), Inches(0.32), GOLD, shape=MSO_SHAPE.OVAL)
    textbox(s, Inches(1.55), top, Inches(10.6), Inches(0.75), line, 19, LIGHT_TEXT, line_spacing=1.15)
    top += Inches(1.05)

textbox(s, Inches(0.9), Inches(5.9), Inches(10.6), Inches(0.5),
        "Pas de jugement. Enfin... un peu.", 15, GOLD, italic=True)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ==================================================== 4. AGENDA ===========
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.7), "Au programme")
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Une heure, quatre outils, zéro slide inutile (promis)", 27, NAVY_TEXT, bold=True)

agenda = [
    ("1", "Le problème", "Pourquoi une suite de tests toute verte ne prouve absolument rien", "5 min"),
    ("2", "La stack", "JUnit, Cucumber, Quarkus, Jacoco — qui fait quoi (et qui ne fait pas le café)", "10 min"),
    ("3", "Démo : le projet", "Un agenda malin, ses tests, ses angles morts", "10 min"),
    ("4", "Le rapport qui ne ment pas", "Jacoco en direct, JUnit contre Cucumber", "15 min"),
    ("5", "Bonus : SonarQube", "Le même rapport, dans un vrai dashboard (spoiler : pas SOAR)", "10 min"),
    ("6", "Ce qu'on retient", "Et deux pièges qu'on a vraiment pris en pleine figure", "5 min"),
]
top = Inches(2.35)
row_h = Inches(0.72)
for num, title, sub, dur in agenda:
    textbox(s, Inches(0.9), top, Inches(0.55), Inches(0.6), num, 20, GOLD_ON_LIGHT, bold=True)
    textbox(s, Inches(1.55), top - Inches(0.02), Inches(7.6), Inches(0.4), title, 16, NAVY_TEXT, bold=True)
    textbox(s, Inches(1.55), top + Inches(0.32), Inches(8.6), Inches(0.35), sub, 11.5, INK)
    textbox(s, Inches(10.6), top + Inches(0.06), Inches(1.6), Inches(0.4), dur, 13, MUTED_ON_LIGHT, align=PP_ALIGN.RIGHT)
    top += row_h
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 5. LE CONSTAT =======
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.7), "Le constat")
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "On a des tests. On n'a toujours aucune idée de ce qu'ils font.", 29, NAVY_TEXT, bold=True)

cards = [
    ("01", "On écrit des tests", "JUnit, Cucumber : les suites tournent au vert à chaque build. On est très fiers. À raison, d'ailleurs.", TEAL),
    ("02", "On ne sait pas ce qu'ils couvrent", "Quelles classes ? Quelles branches ? Une CI verte suffit largement à calmer tout le monde.", GOLD),
    ("03", "Les angles morts restent invisibles", "Jusqu'au bug en prod, dans le code qu'aucun test n'a jamais exécuté. Généralement un vendredi. Toujours un vendredi.", TERRACOTTA),
]
cx = Inches(0.9)
cw = Inches(3.62)
gap = Inches(0.28)
for i, (num, title, body, accent) in enumerate(cards):
    left = cx + i * (cw + gap)
    rect(s, left, Inches(2.65), cw, Inches(3.6), CREAM_CARD)
    rect(s, left, Inches(2.65), cw, Inches(0.09), accent)
    textbox(s, left + Inches(0.32), Inches(3.0), cw - Inches(0.6), Inches(0.7), num, 30, on_light(accent), bold=True)
    textbox(s, left + Inches(0.32), Inches(3.75), cw - Inches(0.6), Inches(1.0), title, 17, NAVY_TEXT, bold=True, line_spacing=1.05)
    textbox(s, left + Inches(0.32), Inches(4.65), cw - Inches(0.6), Inches(1.45), body, 13, INK, line_spacing=1.15)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 6. LA STACK =========
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.6), "La stack technique")
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Quatre outils, quatre questions différentes", 30, NAVY_TEXT, bold=True)

tools = [
    ("JUnit 5", "« La logique métier fait-elle ce qu'elle doit ? »\nTests unitaires ciblés, rapides — le genre d'ami qui vous dit direct que votre code est nul, sans détour.", GOLD),
    ("Cucumber", "« Le comportement attendu est-il respecté ? »\nScénarios Gherkin lisibles — le seul test que votre chef de projet pourra théoriquement relire.", TEAL),
    ("Quarkus", "« Comment tout ça tourne ensemble ? »\nLe framework qui démarre l'appli et pilote les tests — le collègue qui organise tout sans qu'on lui demande.", SAGE),
    ("Jacoco", "« Qu'est-ce qui a vraiment été exécuté ? »\nL'instrument de mesure — celui qui ne ment jamais, contrairement à votre estimation à l'oral.", TERRACOTTA),
]
gx, gy = Inches(0.9), Inches(2.05)
gw, gh = Inches(5.62), Inches(2.35)
gapx, gapy = Inches(0.28), Inches(0.25)
for i, (name, desc, accent) in enumerate(tools):
    col = i % 2
    row = i // 2
    left = gx + col * (gw + gapx)
    top = gy + row * (gh + gapy)
    rect(s, left, top, gw, gh, CREAM_CARD)
    rect(s, left, top, Inches(0.09), gh, accent)
    textbox(s, left + Inches(0.35), top + Inches(0.22), gw - Inches(0.6), Inches(0.55), name, 22, NAVY_TEXT, bold=True)
    textbox(s, left + Inches(0.35), top + Inches(0.85), gw - Inches(0.6), Inches(1.4), desc, 13, INK, line_spacing=1.2)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ============================================== 7. LE PROJET DEMO =========
s = blank(prs)
bg(s, NAVY_DARK)
eyebrow(s, Inches(0.9), Inches(0.6), "Le terrain de jeu", color=GOLD, dark=True)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Un agenda malin", 32, LIGHT_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.68), Inches(10.8), Inches(0.7),
        "Une API Quarkus qui planifie des événements, détecte les conflits d'horaire,\n"
        "génère des récurrences, et glisse une citation du jour — parce qu'une démo a le droit d'être un peu sympa.", 14, RGBColor(0xC8, 0xCF, 0xDA), line_spacing=1.2)


def box(slide, left, top, width, height, title, subtitle, accent):
    rect(slide, left, top, width, height, NAVY_MED)
    rect(slide, left, top, width, Inches(0.07), accent)
    textbox(slide, left + Inches(0.22), top + Inches(0.18), width - Inches(0.4), Inches(0.4), title, 14, LIGHT_TEXT, bold=True)
    textbox(slide, left + Inches(0.22), top + Inches(0.6), width - Inches(0.4), Inches(0.6), subtitle, 10.5, MUTED_ON_DARK_CARD, line_spacing=1.1)


top1 = Inches(2.5)
box(s, Inches(0.9), top1, Inches(4.2), Inches(1.05), "CalendarResource", "Couche REST — JSON in/out", GOLD)
rect(s, Inches(3.0), Inches(3.55), Inches(0.04), Inches(0.35), MUTED)

top2 = Inches(3.95)
services = [
    ("EventService", "création + recherche", TEAL),
    ("RecurrenceService", "quotidien / hebdo / mensuel", SAGE),
    ("HolidayService", "jours fériés", TERRACOTTA),
    ("QuoteOfTheDayService", "citation du jour", GOLD),
]
sw = Inches(2.62)
for i, (name, sub, accent) in enumerate(services):
    left = Inches(0.9) + i * (sw + Inches(0.14))
    box(s, left, top2, sw, Inches(1.05), name, sub, accent)

rect(s, Inches(2.15), Inches(5.0), Inches(0.04), Inches(0.35), MUTED)
box(s, Inches(0.9), Inches(5.35), Inches(4.2), Inches(0.9), "ConflictDetector", "logique pure — aucune dépendance", TEAL)

textbox(s, Inches(6.3), Inches(5.4), Inches(6.1), Inches(1.3),
        "Aucune base de données : le sujet du jour, c'est la couverture\nde tests — pas Hibernate. On se recentre.",
        12.5, MUTED, italic=True, line_spacing=1.2)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ==================================================== 8. ZOOM JUNIT =======
s = blank(prs)
bg(s, CREAM)
rect(s, Inches(0), Inches(0), Inches(0.18), SLIDE_H, GOLD)
eyebrow(s, Inches(0.9), Inches(0.7), "Zoom — JUnit", color=GOLD)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Le microscope", 32, NAVY_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.95), Inches(10.9), Inches(0.9),
        "JUnit teste une unité de code isolée — une méthode, une classe — sans lancer\n"
        "toute l'application. C'est rapide, précis, et ça ne pardonne rien.",
        15, INK, line_spacing=1.3)

feat = [
    ("Rapide", "Des milliers de tests en quelques secondes. Votre café, lui, met plus longtemps.", TEAL),
    ("Isolé", "Pas de serveur, pas de réseau, pas de surprise. Le rêve, quoi.", GOLD),
    ("Technique", "Pensé par et pour les développeurs. Personne d'autre ne relira jamais un assertEquals.", TERRACOTTA),
]
cw = Inches(3.62)
for i, (t, d, accent) in enumerate(feat):
    left = Inches(0.9) + i * (cw + Inches(0.28))
    rect(s, left, Inches(3.25), cw, Inches(1.55), CREAM_CARD)
    rect(s, left, Inches(3.25), Inches(0.08), Inches(1.55), accent)
    textbox(s, left + Inches(0.3), Inches(3.5), cw - Inches(0.5), Inches(0.4), t, 16, NAVY_TEXT, bold=True)
    textbox(s, left + Inches(0.3), Inches(3.9), cw - Inches(0.5), Inches(0.85), d, 12.5, INK, line_spacing=1.15)

textbox(s, Inches(0.9), Inches(5.45), Inches(10.9), Inches(0.9),
        "Dans notre agenda malin : ConflictDetector, RecurrenceService — de la logique\n"
        "pure, testée sans jamais démarrer Quarkus.", 14, INK, italic=True, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 9. JUNIT CODE =======
s = blank(prs)
bg(s, CREAM)
side_bar(s, GOLD)
eyebrow(s, Inches(0.9), Inches(0.6), "JUnit — en action", color=GOLD)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Viser juste, vite", 30, NAVY_TEXT, bold=True)

code = (
    '@Test\n'
    'void deuxEvenementsQuiSeTouchentNeSontPasEnConflit() {\n'
    '    Event a = eventAt("a", 9, 10);\n'
    '    Event b = eventAt("b", 10, 11);\n\n'
    '    assertFalse(detector.isConflicting(a, b));\n'
    '}'
)
rect(s, Inches(0.9), Inches(2.05), Inches(11.5), Inches(3.0), NAVY_DARK)
textbox(s, Inches(1.25), Inches(2.3), Inches(10.9), Inches(2.5), code, 15.5, RGBColor(0xE3, 0xE8, 0xF0),
        font=FONT_MONO, line_spacing=1.25)

textbox(s, Inches(0.9), Inches(5.4), Inches(10.8), Inches(1.2),
        "ConflictDetectorTest : 4 tests, 4 cas limites — chevauchement, contact exact,\n"
        "séparation nette, et réflexivité (oui, on vérifie qu'un événement n'est pas en\n"
        "conflit avec lui-même — sinon, c'est un problème existentiel, pas un bug).",
        13.5, INK, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 10. ZOOM CUCUMBER ======
s = blank(prs)
bg(s, CREAM)
rect(s, Inches(0), Inches(0), Inches(0.18), SLIDE_H, TEAL)
eyebrow(s, Inches(0.9), Inches(0.7), "Zoom — Cucumber", color=TEAL)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Le grand angle", 32, NAVY_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.95), Inches(10.9), Inches(0.9),
        "Cucumber teste le comportement observable, de bout en bout, en français\n"
        "lisible. Le même texte sert de spec fonctionnelle ET de test automatisé.",
        15, INK, line_spacing=1.3)

feat = [
    ("Lisible", "Même un product owner peut le relire (et le corriger). Sensation forte garantie.", GOLD),
    ("Bout en bout", "Passe par la vraie API REST, pas un mock. Comme un vrai client, en moins énervé.", TEAL),
    ("Fonctionnel", "Décrit ce que fait le produit, pas comment. Ça change des tickets Jira écrits un vendredi soir.", TERRACOTTA),
]
cw = Inches(3.62)
for i, (t, d, accent) in enumerate(feat):
    left = Inches(0.9) + i * (cw + Inches(0.28))
    rect(s, left, Inches(3.25), cw, Inches(1.55), CREAM_CARD)
    rect(s, left, Inches(3.25), Inches(0.08), Inches(1.55), accent)
    textbox(s, left + Inches(0.3), Inches(3.5), cw - Inches(0.5), Inches(0.4), t, 16, NAVY_TEXT, bold=True)
    textbox(s, left + Inches(0.3), Inches(3.9), cw - Inches(0.5), Inches(0.85), d, 12.5, INK, line_spacing=1.15)

textbox(s, Inches(0.9), Inches(5.45), Inches(10.9), Inches(0.9),
        "Dans notre agenda malin : la création d'événement, la détection de conflit,\n"
        "le signalement d'un jour férié — trois scénarios, en français.", 14, INK, italic=True, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 11. CUCUMBER CODE ======
s = blank(prs)
bg(s, CREAM)
side_bar(s, TEAL)
eyebrow(s, Inches(0.9), Inches(0.6), "Cucumber — en action", color=TEAL)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Le scénario que tout le monde comprend", 28, NAVY_TEXT, bold=True)

gherkin = (
    'Scénario: Refus d\'un événement qui chevauche un\n'
    '          événement existant\n\n'
    '  Étant donné que j\'ai déjà l\'événement "Comité de\n'
    '  pilotage" de "14:00" à "15:00" le "2026-09-15"\n'
    '  Quand je crée l\'événement "Revue de code" de\n'
    '  "14:30" à "15:30" le "2026-09-15"\n'
    '  Alors la création est refusée pour cause de\n'
    '  conflit d\'horaire'
)
rect(s, Inches(0.9), Inches(2.05), Inches(11.5), Inches(3.4), NAVY_DARK)
textbox(s, Inches(1.25), Inches(2.28), Inches(10.9), Inches(3.0), gherkin, 14.5, RGBColor(0xE3, 0xE8, 0xF0),
        font=FONT_MONO, line_spacing=1.2)

textbox(s, Inches(0.9), Inches(5.7), Inches(10.8), Inches(0.85),
        "Vous remarquerez que même le scénario de test sait qu'un comité de pilotage\n"
        "prend toute la place dans l'agenda. Ça, c'est du réalisme métier.", 14, INK, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 12. LE MATCH ===========
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.7), "Le clash (amical)")
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "JUnit vs Cucumber : qui gagne ?", 30, NAVY_TEXT, bold=True)

col_w = Inches(5.4)
left1 = Inches(0.9)
left2 = Inches(6.6)
rect(s, left1, Inches(2.3), col_w, Inches(3.6), CREAM_CARD)
rect(s, left1, Inches(2.3), col_w, Inches(0.09), GOLD)
textbox(s, left1 + Inches(0.35), Inches(2.6), col_w - Inches(0.6), Inches(0.5), "JUnit", 22, NAVY_TEXT, bold=True)
for i, line in enumerate(["Rapide", "Isolé", "Technique", "Pour les devs"]):
    textbox(s, left1 + Inches(0.35), Inches(3.3) + Inches(0.55) * i, col_w - Inches(0.6), Inches(0.5), "— " + line, 15, INK)

rect(s, left2, Inches(2.3), col_w, Inches(3.6), CREAM_CARD)
rect(s, left2, Inches(2.3), col_w, Inches(0.09), TEAL)
textbox(s, left2 + Inches(0.35), Inches(2.6), col_w - Inches(0.6), Inches(0.5), "Cucumber", 22, NAVY_TEXT, bold=True)
for i, line in enumerate(["Lisible", "Bout en bout", "Fonctionnel", "Pour tout le monde"]):
    textbox(s, left2 + Inches(0.35), Inches(3.3) + Inches(0.55) * i, col_w - Inches(0.6), Inches(0.5), "— " + line, 15, INK)

stamp(s, Inches(6.0), Inches(3.85), Inches(0.9), Inches(0.55), "match nul",
      NAVY_DARK, LIGHT_TEXT, rotation=352, size=11.5, line_color=CREAM)

textbox(s, Inches(0.9), Inches(6.15), Inches(11), Inches(0.6),
        "Spoiler : il n'y a pas de gagnant. Le seul qui gagne, c'est le code — testé sous deux angles.",
        14, GOLD_ON_LIGHT, italic=True, bold=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 13. BASCULE DEMO 1 =====
s = blank(prs)
bg(s, NAVY_DARK)
dot_grid(s, Inches(0.7), Inches(1.0), rows=3, cols=10)
rect(s, Inches(6.5565), Inches(2.5), Inches(0.22), Inches(0.22), TERRACOTTA, shape=MSO_SHAPE.OVAL)
textbox(s, Inches(0.9), Inches(3.0), Inches(11.5), Inches(1.4),
        "EN DIRECT", 48, LIGHT_TEXT, bold=True, align=PP_ALIGN.CENTER)
textbox(s, Inches(0.9), Inches(4.2), Inches(11.5), Inches(0.6),
        "(on arrête PowerPoint. direction le terminal, pour de vrai — fermez Slack pendant qu'on y est)",
        15, GOLD, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="cut")

# ================================================= 14. ZOOM JACOCO ========
s = blank(prs)
bg(s, CREAM)
side_bar(s, TERRACOTTA)
eyebrow(s, Inches(0.9), Inches(0.7), "Zoom — Jacoco", color=TERRACOTTA)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Un agent qui espionne le bytecode (légalement)", 27, NAVY_TEXT, bold=True)

steps_j = [
    ("1", "Au démarrage de la JVM", "Un agent Java (-javaagent) s'attache et instrumente chaque classe chargée."),
    ("2", "Pendant les tests", "Chaque ligne, chaque branche exécutée est comptée — en silence, sans ralentir grand-chose. Un espion discret."),
    ("3", "À l'arrêt de la JVM", "Tout est vidé dans un fichier .exec. Puis jacoco-maven-plugin le transforme en rapport HTML/XML/CSV."),
]
top = Inches(2.35)
for num, t, d in steps_j:
    rect(s, Inches(0.9), top, Inches(0.65), Inches(0.65), NAVY_DARK)
    textbox(s, Inches(0.9), top, Inches(0.65), Inches(0.65), num, 22, GOLD, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, Inches(1.75), top - Inches(0.02), Inches(10), Inches(0.4), t, 16, NAVY_TEXT, bold=True)
    textbox(s, Inches(1.75), top + Inches(0.36), Inches(10), Inches(0.6), d, 12.5, INK, line_spacing=1.2)
    top += Inches(1.15)

textbox(s, Inches(0.9), Inches(6.0), Inches(10.9), Inches(0.5),
        "Non, ce n'est pas de l'espionnage industriel. C'est juste un agent très curieux, payé en aucune façon.",
        13.5, TERRA_ON_LIGHT, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 15. JACOCO OVERVIEW ====
s = blank(prs)
bg(s, CREAM)
side_bar(s, TERRACOTTA)
eyebrow(s, Inches(0.9), Inches(0.6), "Jacoco — le rapport", color=TERRACOTTA)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.7),
        "Pas une maquette Figma. Le vrai rapport.", 28, NAVY_TEXT, bold=True)
picture(s, f"{SCREENSHOTS}/jacoco-overview.png", Inches(0.9), Inches(1.95), Inches(11.5))
textbox(s, Inches(0.9), Inches(4.4), Inches(11), Inches(0.6),
        "Vrai export HTML, généré il y a quelques heures, par la commande qu'on vient de lancer. Pas d'entourloupe.",
        13, MUTED_ON_LIGHT, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 16. JACOCO PREUVE ======
s = blank(prs)
bg(s, CREAM)
side_bar(s, TERRACOTTA)
eyebrow(s, Inches(0.55), Inches(0.35), "Jacoco — la preuve", color=TERRACOTTA)
textbox(s, Inches(0.55), Inches(0.68), Inches(9.6), Inches(0.55),
        "La branche MENSUELLE, prise en flagrant délit", 24, NAVY_TEXT, bold=True)
stamp(s, Inches(10.2), Inches(0.35), Inches(2.75), Inches(1.1), "Bissextile !",
      NAVY_DARK, GOLD, rotation=350, size=12, shape=MSO_SHAPE.EXPLOSION2)
picture(s, f"{SCREENSHOTS}/jacoco-recurrence-source.png", Inches(1.97), Inches(1.35), Inches(9.4))
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 17. JUNIT VS CUC JACOCO=
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.55), "Jacoco", color=TERRACOTTA)
textbox(s, Inches(0.9), Inches(0.9), Inches(11), Inches(0.8),
        "Ce que les tests ont vraiment touché", 28, NAVY_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.58), Inches(11), Inches(0.4),
        "Mesure réelle, extraite du build — couverture de lignes, JUnit contre Cucumber", 13, MUTED_ON_LIGHT, italic=True)

leg_top = Inches(2.0)
rect(s, Inches(0.9), leg_top, Inches(0.32), Inches(0.18), GOLD_ON_LIGHT)
textbox(s, Inches(1.3), leg_top - Inches(0.03), Inches(2), Inches(0.3), "JUnit (unitaire)", 12, NAVY_TEXT, bold=True)
rect(s, Inches(3.3), leg_top, Inches(0.32), Inches(0.18), TEAL)
textbox(s, Inches(3.7), leg_top - Inches(0.03), Inches(3), Inches(0.3), "Cucumber (intégration)", 12, NAVY_TEXT, bold=True)

data = [
    ("CalendarResource", 0, 58),
    ("HolidayService", 0, 93),
    ("RecurrenceService", 78, 4),
    ("ConflictDetector", 100, 75),
    ("EventService", 88, 88),
    ("RecurrenceRequest (DTO)", 0, 0),
]
chart_left = Inches(3.7)
chart_w = Inches(8.0)
row_h = Inches(0.62)
bar_h = Inches(0.2)
top0 = Inches(2.48)
for i, (name, pct_junit, pct_cuc) in enumerate(data):
    top = top0 + i * row_h
    textbox(s, Inches(0.9), top + Inches(0.1), Inches(2.65), Inches(0.4), name, 12, NAVY_TEXT, align=PP_ALIGN.RIGHT)

    rect(s, chart_left, top, chart_w, bar_h, CREAM_CARD)
    barw = Emu(int(chart_w * max(pct_junit, 1) / 100))
    rect(s, chart_left, top, barw, bar_h, GOLD_ON_LIGHT)
    textbox(s, chart_left + chart_w + Inches(0.1), top - Inches(0.03), Inches(0.7), Inches(0.3),
            f"{pct_junit}%", 11, NAVY_TEXT, bold=True)

    top2v = top + bar_h + Inches(0.05)
    rect(s, chart_left, top2v, chart_w, bar_h, CREAM_CARD)
    barw2 = Emu(int(chart_w * max(pct_cuc, 1) / 100))
    rect(s, chart_left, top2v, barw2, bar_h, TEAL)
    textbox(s, chart_left + chart_w + Inches(0.1), top2v - Inches(0.03), Inches(0.7), Inches(0.3),
            f"{pct_cuc}%", 11, NAVY_TEXT, bold=True)

textbox(s, Inches(0.9), Inches(6.28), Inches(11), Inches(0.35),
        "JUnit couvre la logique métier ; Cucumber couvre la couche REST — presque aucun recouvrement.",
        12, MUTED_ON_LIGHT, italic=True)
textbox(s, Inches(0.9), Inches(6.58), Inches(11), Inches(0.35),
        "Mention spéciale à RecurrenceRequest : 0 % partout. Personne n'y a jamais touché. Personne.",
        12, TERRA_ON_LIGHT, italic=True, bold=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 18. TERMINAL ===========
s = blank(prs)
bg(s, NAVY_DARK)
eyebrow(s, Inches(0.9), Inches(0.55), "Sans ouvrir de navigateur", color=GOLD, dark=True)
textbox(s, Inches(0.9), Inches(0.9), Inches(11), Inches(0.8),
        "Le récap, direct dans le terminal", 28, LIGHT_TEXT, bold=True)
picture(s, f"{SCREENSHOTS}/terminal-mock.png", Inches(2.42), Inches(1.7), Inches(8.5), frame_color=NAVY_MED)
textbox(s, Inches(0.9), Inches(6.75), Inches(11.5), Inches(0.4),
        "coverage-summary.sh fait le café à votre place : rouge, orange, vert, classe par classe.",
        12.5, MUTED, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 19. EN DIRECT ==========
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.6), "En direct")
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Trois commandes, un radar complet", 30, NAVY_TEXT, bold=True)

steps = [
    ("1", "./mvnw test", "Build + JUnit + Cucumber + 3 rapports Jacoco générés automatiquement."),
    ("2", "./scripts/coverage-summary.sh", "Le récap coloré JUnit / Cucumber / global, côte à côte, dans le terminal."),
    ("3", "open target/jacoco-report/index.html", "Le détail ligne par ligne — et les variantes -junit / -cucumber pour comparer."),
]
top = Inches(2.1)
for num, cmd, desc in steps:
    rect(s, Inches(0.9), top, Inches(0.75), Inches(1.1), NAVY_DARK)
    textbox(s, Inches(0.9), top, Inches(0.75), Inches(1.1), num, 26, GOLD, bold=True,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, Inches(1.85), top + Inches(0.06), Inches(10.3), Inches(0.5), cmd, 18, NAVY_TEXT, bold=True, font=FONT_MONO)
    textbox(s, Inches(1.85), top + Inches(0.55), Inches(10.3), Inches(0.5), desc, 13, INK)
    top += Inches(1.4)

textbox(s, Inches(0.9), Inches(6.4), Inches(11), Inches(0.4),
        "Rien d'exotique, rien à installer de plus que ce qu'on a déjà dans le pom.xml.",
        13, MUTED_ON_LIGHT, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 20. BONUS SONAR ========
s = blank(prs)
bg(s, NAVY_DARK)
eyebrow(s, Inches(0.9), Inches(0.6), "Bonus (promis, pas SOAR)", color=GOLD, dark=True)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Et dans un vrai dashboard ?", 30, LIGHT_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.68), Inches(10.8), Inches(0.5),
        "Les deux mêmes rapports Jacoco XML, importés tels quels dans SonarQube.",
        14, RGBColor(0xC8, 0xCF, 0xDA))

stats = [
    ("77,7 %", "couverture globale"),
    ("82 %", "lignes"),
    ("65 %", "branches"),
]
sw = Inches(3.62)
sx = Inches(0.9)
for i, (value, label) in enumerate(stats):
    left = sx + i * (sw + Inches(0.28))
    rect(s, left, Inches(2.5), sw, Inches(1.7), NAVY_MED)
    rect(s, left, Inches(2.5), sw, Inches(0.07), GOLD)
    textbox(s, left, Inches(2.78), sw, Inches(0.75), value, 40, GOLD, bold=True, align=PP_ALIGN.CENTER)
    textbox(s, left, Inches(3.55), sw, Inches(0.4), label, 13, MUTED_ON_DARK_CARD, align=PP_ALIGN.CENTER)

textbox(s, Inches(0.9), Inches(4.55), Inches(10.8), Inches(0.35),
        "Mesure réelle, obtenue en lançant l'analyse sur ce projet — pas une maquette.",
        12, MUTED, italic=True)

rect(s, Inches(0.9), Inches(5.05), Inches(11.5), Inches(1.15), NAVY_MED)
textbox(s, Inches(1.2), Inches(5.28), Inches(10.9), Inches(0.7),
        "docker compose -f sonarqube/docker-compose.yml up -d\n"
        "./mvnw test sonar:sonar -Dsonar.token=<ton_token>",
        14.5, RGBColor(0xE3, 0xE8, 0xF0), font=FONT_MONO, line_spacing=1.3)

textbox(s, Inches(0.9), Inches(6.45), Inches(10.8), Inches(0.4),
        "SonarQube Community en local — aucun compte SonarCloud, aucune dépendance réseau pendant le talk.",
        12.5, MUTED)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 21. SONAR DASHBOARD ====
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.55), "SonarQube — dashboard")
textbox(s, Inches(0.9), Inches(0.9), Inches(11), Inches(0.7),
        "Coverage 77,7 %, en vrai, dans l'interface", 26, NAVY_TEXT, bold=True)
picture(s, f"{SCREENSHOTS}/sonar-overview.png", Inches(3.02), Inches(1.7), Inches(7.3))
textbox(s, Inches(0.9), Inches(6.45), Inches(11.5), Inches(0.4),
        "Sonar ne mesure rien lui-même : il relit ce que Jacoco a déjà dit et fait semblant d'avoir tout calculé.",
        12.5, MUTED_ON_LIGHT, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 22. SONAR MEASURES =====
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.55), "SonarQube — mesures")
textbox(s, Inches(0.9), Inches(0.9), Inches(11), Inches(0.7),
        "Le détail, fichier par fichier", 26, NAVY_TEXT, bold=True)
picture(s, f"{SCREENSHOTS}/sonar-coverage-list.png", Inches(3.02), Inches(1.7), Inches(7.3))
textbox(s, Inches(0.9), Inches(6.45), Inches(11.5), Inches(0.4),
        "Mêmes pourcentages que dans notre terminal. Même vérité, vitrine plus chère.",
        12.5, MUTED_ON_LIGHT, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 23. SONAR CODE =========
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.55), Inches(0.35), "SonarQube — la preuve, encore")
textbox(s, Inches(0.55), Inches(0.68), Inches(11.8), Inches(0.55),
        "Même branche rouge, autre outil", 24, NAVY_TEXT, bold=True)
picture(s, f"{SCREENSHOTS}/sonar-code-drilldown.png", Inches(2.87), Inches(1.3), Inches(7.6))
textbox(s, Inches(0.9), Inches(6.25), Inches(11.5), Inches(0.4),
        "Pas un artefact d'un outil bizarre : un fait sur votre code, confirmé deux fois de suite.",
        12.5, MUTED_ON_LIGHT, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 24. LES EXCUSES ========
s = blank(prs)
bg(s, CREAM)
side_bar(s, TERRACOTTA)
eyebrow(s, Inches(0.9), Inches(0.7), "Confessions collectives", color=TERRACOTTA)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(1.1),
        "Le best-of des excuses pour ne pas tester", 28, NAVY_TEXT, bold=True)

excuses = [
    ("« Ça marche sur ma machine. »", "Votre machine n'ira pas en prod avec vous. Elle ne peut pas témoigner."),
    ("« On testera après le sprint. »", "Le sprint suivant aussi. Et celui d'après. À ce rythme, on teste au démantèlement."),
    ("« C'est trop simple pour bugger. »", "Neuf incidents de prod sur dix commencent exactement comme ça."),
    ("« Le stagiaire a dit que ça passait. »", "Un mardi après-midi ensoleillé, à la main, une seule fois."),
    ("« 100 % de couverture, on n'a plus besoin de relire. »", "La couverture mesure ce qui a été EXÉCUTÉ. Pas ce qui a été VÉRIFIÉ."),
]
top = Inches(2.3)
row_h = Inches(0.78)
for i, (excuse, retort) in enumerate(excuses):
    textbox(s, Inches(0.9), top + Inches(0.04), Inches(0.6), Inches(0.5), f"{i+1:02d}", 16, TERRA_ON_LIGHT, bold=True)
    textbox(s, Inches(1.6), top, Inches(10.7), Inches(0.4), excuse, 15, NAVY_TEXT, bold=True)
    textbox(s, Inches(1.6), top + Inches(0.36), Inches(10.7), Inches(0.4), retort, 11.5, MUTED_ON_LIGHT, italic=True)
    top += row_h

textbox(s, Inches(0.9), Inches(6.35), Inches(11.3), Inches(0.65),
        "Spoiler : aucune de ces cinq phrases n'a jamais empêché un incendie en prod. Pas une seule. "
        "J'ai vérifié. Enfin... je crois.",
        13, TERRA_ON_LIGHT, italic=True, bold=True, line_spacing=1.15)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 25. RETOUR D'XP ========
s = blank(prs)
bg(s, NAVY_DARK)
eyebrow(s, Inches(0.9), Inches(0.6), "Retour d'expérience", color=GOLD, dark=True)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Deux pièges qu'on a vraiment eus en préparant cette conf", 24, LIGHT_TEXT, bold=True)

stories = [
    ("Le QuarkusClassLoader fantôme",
     "Deux exécutions Surefire, deux agents Jacoco... et pourtant tout à 0 %. Coupable : "
     "l'extension quarkus-jacoco mesure le code CDI toute seule, dans son coin, sans prévenir personne.",
     GOLD),
    ("L'accent qui a cassé Gherkin",
     "« Fonctionnalite » sans accent ne veut RIEN dire pour un parseur Gherkin en français. "
     "Un é manquant, et Cucumber devient aussi utile qu'un GPS sans signal.",
     TEAL),
]
top = Inches(2.15)
for title, body, accent in stories:
    rect(s, Inches(0.9), top, Inches(11.5), Inches(1.95), NAVY_MED)
    rect(s, Inches(0.9), top, Inches(0.09), Inches(1.95), accent)
    textbox(s, Inches(1.25), top + Inches(0.22), Inches(10.9), Inches(0.45), title, 18, LIGHT_TEXT, bold=True)
    textbox(s, Inches(1.25), top + Inches(0.72), Inches(10.9), Inches(1.1), body, 13, MUTED_ON_DARK_CARD, line_spacing=1.3)
    top += Inches(2.25)

textbox(s, Inches(0.9), Inches(6.75), Inches(11), Inches(0.4),
        "Le seul avantage qu'on a eu sur vous : un rapport de couverture pour le prouver noir sur blanc.",
        13, GOLD, italic=True)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 26. A RETENIR ==========
s = blank(prs)
bg(s, NAVY_DARK)
eyebrow(s, Inches(0.9), Inches(0.6), "À retenir", color=GOLD, dark=True)
textbox(s, Inches(0.9), Inches(0.95), Inches(11), Inches(0.9),
        "Ce qu'il faut retenir", 32, LIGHT_TEXT, bold=True)
stamp(s, Inches(10.75), Inches(0.55), Inches(1.65), Inches(0.6), "tl;dr",
      GOLD, NAVY_DARK, rotation=6, size=14)

points = [
    ("Un test vert ne dit pas ce qu'il a vérifié.", "La couverture, si."),
    ("JUnit et Cucumber répondent à deux questions différentes.", "« Ça marche ? » contre « c'est le bon comportement ? »"),
    ("Le rapport de couverture n'est pas un objectif.", "C'est un radar : il montre où regarder en premier."),
    ("Un outil ne remplace pas la question qu'on ne s'est pas posée.", "Ni Jacoco, ni Sonar, ni celui d'après."),
]
top = Inches(2.15)
for i, (line1, line2) in enumerate(points):
    textbox(s, Inches(0.9), top, Inches(1.2), Inches(1.1), f"{i+1:02d}", 30, GOLD, bold=True)
    textbox(s, Inches(2.2), top + Inches(0.02), Inches(9.8), Inches(0.55), line1, 17, LIGHT_TEXT, bold=True)
    textbox(s, Inches(2.2), top + Inches(0.55), Inches(9.8), Inches(0.5), line2, 13.5, MUTED)
    top += Inches(1.25)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 27. POUR ALLER PLUS LOIN
s = blank(prs)
bg(s, CREAM)
side_bar(s)
eyebrow(s, Inches(0.9), Inches(0.7), "Pour la suite")
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(0.65),
        "Si vous voulez creuser", 30, NAVY_TEXT, bold=True)
textbox(s, Inches(0.9), Inches(1.72), Inches(11), Inches(0.4),
        "Code et scripts, en clair. Le reste (mes doutes existentiels sur plusMonths()) reste entre moi et mon terminal.",
        12.5, MUTED_ON_LIGHT, italic=True)

links = [
    ("Le dépôt de ce projet", "github.com/sidevconcept/couverture-junit-cucumber-jacoco", GOLD),
    ("Guide Quarkus + Jacoco", "quarkus.io/guides/tests-with-coverage", TEAL),
    ("Extension Cucumber pour Quarkus", "docs.quarkiverse.io/quarkus-cucumber", SAGE),
    ("SonarQube Community", "docs.sonarsource.com", TERRACOTTA),
]
top = Inches(2.55)
for title, url, accent in links:
    rect(s, Inches(0.9), top + Inches(0.08), Inches(0.14), Inches(0.14), accent, shape=MSO_SHAPE.OVAL)
    textbox(s, Inches(1.3), top, Inches(10.6), Inches(0.4), title, 16, NAVY_TEXT, bold=True)
    textbox(s, Inches(1.3), top + Inches(0.38), Inches(10.6), Inches(0.4), url, 13, INK, font=FONT_MONO)
    top += Inches(1.0)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 28. MERCI ==============
s = blank(prs)
bg(s, NAVY_DARK)
dot_grid(s, Inches(0.7), Inches(5.3), rows=3)
textbox(s, Inches(0.9), Inches(2.4), Inches(8.3), Inches(1.4), "Merci.", 52, LIGHT_TEXT, bold=True)
textbox(s, Inches(0.95), Inches(3.55), Inches(8.3), Inches(0.5), "Questions ?", 22, GOLD)
textbox(s, Inches(0.95), Inches(4.15), Inches(8.3), Inches(0.9),
        "(et si quelqu'un me dit « chez nous on a 100 % de couverture »,\nje réponds déjà : sur quelle branche ?)",
        13.5, RGBColor(0xC8, 0xCF, 0xDA), italic=True, line_spacing=1.25)
textbox(s, Inches(0.95), Inches(6.55), Inches(8.3), Inches(0.5),
        "https://github.com/sidevconcept/couverture-junit-cucumber-jacoco  —  sidev.concept06@gmail.com",
        12, MUTED)

# QR code vers le depot — genere par presentation/build/generate_qr.py,
# stocke dans presentation/screenshots/ comme les autres visuels du support.
textbox(s, Inches(9.9), Inches(2.2), Inches(2.1), Inches(0.35), "Scanne-moi", 13, GOLD, bold=True, align=PP_ALIGN.CENTER)
picture(s, f"{SCREENSHOTS}/qr-github.png", Inches(9.7), Inches(2.6), Inches(2.5), frame_color=CREAM)
skip_footer()
add_transition(s, kind="fade")

OUT ="/Users/sidneycohen/dev/projects/couverture-code/presentation/couverture-code-conference.pptx"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("saved", OUT, "-", _counter[0], "slides numbered")
