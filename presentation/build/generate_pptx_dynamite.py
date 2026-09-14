#!/usr/bin/env python3
"""Génère « Couverture Dynamite » — remix visuel du même deck de conférence
(couverture-code-conference.pptx), même contenu / mêmes 28 slides, mais une
UI complètement redessinée pour être plus vivante à l'écran : diagonales,
stickers pivotés, bulles de BD pour les punchlines, halftone, fenêtres
« navigateur » pour les captures d'écran. Palette plus saturée que l'édition
officielle (navy marine + cream) mais toujours pensée pour un vidéoprojecteur
de salle de conférence, pas un écran de designer.

Ne touche jamais à generate_pptx.py ni à couverture-code-conference.pptx —
fichier de sortie distinct, script distinct."""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
from lxml import etree

# ---------------------------------------------------------------- palette --
INK          = RGBColor(0x0C, 0x11, 0x1F)   # fond sombre, quasi noir-marine
INK_CARD     = RGBColor(0x17, 0x1F, 0x33)   # cartes sur fond INK
INK_CARD_HI  = RGBColor(0x20, 0x2A, 0x44)   # carte "surélevée" (ombre portée simulée)
PAPER        = RGBColor(0xFB, 0xF6, 0xEA)   # fond clair, crème chaud
PAPER_CARD   = RGBColor(0xF1, 0xE9, 0xD5)   # carte sur fond clair
PAPER_CARD_HI= RGBColor(0xE7, 0xDC, 0xC1)
TXT_DARK     = RGBColor(0x18, 0x1D, 0x2B)   # texte de corps sur fond clair
TXT_LIGHT    = RGBColor(0xF3, 0xEE, 0xE0)   # texte sur fond sombre
MUTED_D      = RGBColor(0x9A, 0xA1, 0xB5)   # texte secondaire sur fond sombre
MUTED_L      = RGBColor(0x5C, 0x62, 0x72)   # texte secondaire sur fond clair

AMBER   = RGBColor(0xF0, 0xA7, 0x2E)   # JUnit
TEAL    = RGBColor(0x2E, 0xB0, 0xA0)   # Cucumber
LIME    = RGBColor(0x9C, 0xC2, 0x4C)   # Quarkus
CORAL   = RGBColor(0xF0, 0x5A, 0x46)   # Jacoco / alerte
MARKER  = RGBColor(0xFF, 0xD2, 0x3F)   # jaune surligneur — signal "vanne"
INKY_BLUE = RGBColor(0x3E, 0x6B, 0xE0) # accent froid, liens / secondaire

# variantes texte-sûres (>=4.5:1) pour poser ces accents sur PAPER/PAPER_CARD
AMBER_ON_LIGHT = RGBColor(0x8A, 0x5A, 0x10)
TEAL_ON_LIGHT  = RGBColor(0x1B, 0x6E, 0x62)
LIME_ON_LIGHT  = RGBColor(0x54, 0x6E, 0x22)
CORAL_ON_LIGHT = RGBColor(0xA8, 0x33, 0x22)
MARKER_ON_LIGHT= RGBColor(0x7A, 0x5C, 0x00)
INKY_ON_LIGHT  = RGBColor(0x22, 0x40, 0x9C)
MUTED_ON_CARD_HI = RGBColor(0xB0, 0xB7, 0xC8)   # texte secondaire sur INK_CARD_HI

_LIGHT_SAFE = {AMBER: AMBER_ON_LIGHT, TEAL: TEAL_ON_LIGHT, LIME: LIME_ON_LIGHT,
               CORAL: CORAL_ON_LIGHT, MARKER: MARKER_ON_LIGHT, INKY_BLUE: INKY_ON_LIGHT,
               MUTED_D: MUTED_L}


def on_light(color):
    return _LIGHT_SAFE.get(color, color)


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


def rect(slide, left, top, width, height, color, line_color=None, line_w=None,
         shape=MSO_SHAPE.RECTANGLE, rotation=0):
    shp = slide.shapes.add_shape(shape, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line_color is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line_color
        shp.line.width = line_w or Pt(1)
    shp.shadow.inherit = False
    if rotation:
        shp.rotation = rotation
    return shp


def raised_card(slide, left, top, width, height, fill, shadow_color, offset=0.09, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    """Carte avec une « ombre portée » simulée par une seconde forme décalée
    en dessous — le seul moyen fiable de donner une impression de profondeur
    en pptx sans dépendre du rendu d'ombre natif (capricieux à l'export)."""
    off = Inches(offset)
    rect(slide, Emu(int(left + off)), Emu(int(top + off)), width, height, shadow_color, shape=shape)
    return rect(slide, left, top, width, height, fill, shape=shape)


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


def headline(slide, left, top, width, height, parts, size, align=PP_ALIGN.LEFT,
             font=FONT, line_spacing=1.02, anchor=MSO_ANCHOR.TOP):
    """Titre multi-couleurs : parts = [(texte, couleur, bold), ...], concaténés
    sur la même ligne — sert à faire ressortir un mot-clé (souvent la vanne)
    directement dans le titre plutôt que dans une légende à part."""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for text, color, bold in parts:
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font
    return box


def eyebrow(slide, left, top, text, color=MARKER, dark=False):
    c = color if dark else on_light(color)
    textbox(slide, left, top, Inches(10), Inches(0.4), text.upper(), 12.5, c, bold=True, font=FONT)


def section_tag(slide, text, accent, dark):
    """Étiquette « chapitre » en haut à gauche : petit ruban pivoté au lieu
    d'un simple mot en majuscules — signature visuelle du deck, présente sur
    (presque) toutes les slides pour ancrer où on en est."""
    fill = accent
    txt = INK if dark else INK
    tag = rect(slide, Inches(-0.18), Inches(0.42), Inches(2.35), Inches(0.46), fill,
               shape=MSO_SHAPE.PARALLELOGRAM, rotation=0)
    tf = tag.text_frame
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text.upper()
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = txt
    run.font.name = FONT


def picture(slide, path, left, top, width, frame_color=None, pad_in=0.0):
    w, h = Image.open(path).size
    height = Emu(int(width * h / w))
    if frame_color is not None and pad_in:
        pad = Inches(pad_in)
        rect(slide, Emu(int(left - pad)), Emu(int(top - pad)), Emu(int(width + 2 * pad)), Emu(int(height + 2 * pad)), frame_color)
    slide.shapes.add_picture(path, left, top, width=width, height=height)
    return height


def browser_frame(slide, path, left, top, width, chrome_color=INK, bar_h_in=0.34):
    """Capture d'écran encadrée dans une fausse fenêtre de navigateur (barre +
    3 pastilles façon feux de circulation) : renforce le gag « c'est un vrai
    export, pas une maquette Figma » en la faisant ressembler à un vrai
    navigateur ouvert, pas à une image collée sur la slide."""
    w, h = Image.open(path).size
    img_h = Emu(int(width * h / w))
    bar_h = Inches(bar_h_in)
    rect(slide, left, top, width, bar_h, chrome_color, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    rect(slide, left, Emu(int(top + bar_h / 2)), width, Emu(int(bar_h / 2)), chrome_color)
    dots = [CORAL, AMBER, RGBColor(0x5B, 0xC2, 0x6B)]
    for i, c in enumerate(dots):
        d = Inches(0.11)
        rect(slide, Emu(int(left + Inches(0.18) + i * Inches(0.22))), Emu(int(top + bar_h / 2 - d / 2)),
             d, d, c, shape=MSO_SHAPE.OVAL)
    slide.shapes.add_picture(path, left, Emu(int(top + bar_h)), width=width, height=img_h)
    rect(slide, left, Emu(int(top + bar_h)), width, img_h, RGBColor(0, 0, 0),
         line_color=chrome_color, line_w=Pt(1.5))
    slide.shapes[-1].fill.background()
    return Emu(int(img_h + bar_h))


def speech_bubble(slide, left, top, width, height, text, fill=MARKER, text_color=INK,
                   size=13.5, tail="bl", bold=True, italic=False):
    """Bulle de BD pour les punchlines : rectangle arrondi + petit triangle
    « queue ». Réservée aux phrases qui doivent se lire comme une réplique,
    pas comme une légende — l'humour du deck se voit d'un coup d'œil, sans
    lire le texte."""
    bub = rect(slide, left, top, width, height, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = bub.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.14)
    tf.margin_bottom = Inches(0.14)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.line_spacing = 1.15
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = text_color
    run.font.name = FONT
    tri = Inches(0.28)
    if tail == "bl":
        tx, ty, rot = left + Inches(0.35), top + height - Inches(0.02), 180
    elif tail == "br":
        tx, ty, rot = left + width - Inches(0.63), top + height - Inches(0.02), 180
    elif tail == "tl":
        tx, ty, rot = left + Inches(0.35), top - Inches(0.26), 0
    else:
        tx, ty, rot = left + width - Inches(0.63), top - Inches(0.26), 0
    t = rect(slide, tx, ty, tri, tri, fill, shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
    t.rotation = rot


def sticker_circle(slide, cx, cy, d, text, fill, text_color, rotation=-8, size=14, sub=None):
    """Badge rond « autocollant », pivoté, avec ombre portée simulée — utilisé
    pour les numéros et les tampons ponctuels."""
    off = Inches(0.06)
    rect(slide, Emu(int(cx - d / 2 + off)), Emu(int(cy - d / 2 + off)), d, d, INK, shape=MSO_SHAPE.OVAL)
    c = rect(slide, Emu(int(cx - d / 2)), Emu(int(cy - d / 2)), d, d, fill, shape=MSO_SHAPE.OVAL)
    c.rotation = rotation
    tf = c.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = text_color
    run.font.name = FONT
    if sub:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run()
        r2.text = sub
        r2.font.size = Pt(size * 0.5)
        r2.font.color.rgb = text_color
        r2.font.name = FONT


def chip(slide, left, top, text, fill, text_color, size=11):
    w = Inches(0.32 + 0.0135 * size * len(text))
    h = Inches(0.34)
    c = rect(slide, left, top, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = c.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = text_color
    run.font.name = FONT
    return w


def dot_grid(slide, x0, y0, rows=5, cols=6, color=MARKER, d_in=0.09, gap_in=0.32, shrink=False):
    for row in range(rows):
        for col in range(cols):
            size = d_in * (1 - 0.55 * (col / max(cols - 1, 1))) if shrink else d_in
            d = Inches(size)
            x = x0 + Inches(col * gap_in)
            y = y0 + Inches(row * gap_in)
            rect(slide, x, y, d, d, color, shape=MSO_SHAPE.OVAL)


def code_window(slide, left, top, width, height, code, dark=INK, txt=RGBColor(0xE7, 0xEC, 0xF5), size=15):
    rect(slide, left, top, width, height, dark, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    bar_h = Inches(0.4)
    dots = [CORAL, AMBER, RGBColor(0x5B, 0xC2, 0x6B)]
    for i, c in enumerate(dots):
        d = Inches(0.12)
        rect(slide, Emu(int(left + Inches(0.22) + i * Inches(0.24))), Emu(int(top + bar_h / 2 - d / 2)),
             d, d, c, shape=MSO_SHAPE.OVAL)
    textbox(slide, left + Inches(0.35), top + bar_h + Inches(0.12), width - Inches(0.7), height - bar_h - Inches(0.2),
            code, size, txt, font=FONT_MONO, line_spacing=1.25)


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def add_transition(slide, kind="fade", speed="fast", direction=None):
    sld = slide._element
    csld = sld.find(f"{{{P_NS}}}cSld")
    idx = list(sld).index(csld) + 1
    transition = etree.Element(f"{{{P_NS}}}transition")
    transition.set("spd", speed)
    child = etree.SubElement(transition, f"{{{P_NS}}}{kind}")
    if direction:
        child.set("dir", direction)
    sld.insert(idx, transition)


_counter = [0]


def skip_footer():
    _counter[0] += 1


def footer(slide, total, dark=False):
    _counter[0] += 1
    txt_color = MUTED_D if dark else MUTED_L
    pill_bg = INK_CARD if dark else PAPER_CARD
    pill = rect(slide, Inches(12.25), Inches(7.02), Inches(0.78), Inches(0.36), pill_bg,
                shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tf = pill.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = f"{_counter[0]:02d}/{total:02d}"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = txt_color
    run.font.name = FONT
    textbox(slide, Inches(0.55), Inches(7.1), Inches(6.5), Inches(0.3),
            "COUVERTURE DYNAMITE — QUARKUS · JUNIT · CUCUMBER · JACOCO", 8, txt_color)


def side_bar(slide, color):
    rect(slide, Inches(0), Inches(0), Inches(0.2), SLIDE_H, color)


TOTAL_SLIDES = 28
prs = new_pres()

# ============================================================ 1. TITRE ====
s = blank(prs)
bg(s, INK)
band = rect(s, Inches(9.6), Inches(-1.2), Inches(6.2), Inches(10), INK_CARD, shape=MSO_SHAPE.PARALLELOGRAM)
dot_grid(s, Inches(10.55), Inches(0.55), rows=6, cols=5, color=MARKER, shrink=True)
rect(s, Inches(1.0), Inches(2.25), Inches(0.1), Inches(2.05), MARKER)
eyebrow(s, Inches(1.25), Inches(1.82), "Conférence technique (ou thérapie de groupe)", dark=True, color=MARKER)
headline(s, Inches(1.2), Inches(2.35), Inches(10.5), Inches(1.9),
         [("La couverture de code,\n", TXT_LIGHT, True), ("sans blabla", MARKER, True)], 46, line_spacing=1.05)
textbox(s, Inches(1.25), Inches(4.25), Inches(10.7), Inches(0.6),
        "Quarkus  ·  JUnit  ·  Cucumber  ·  Jacoco  ·  (un peu de Sonar en bonus)", 18, AMBER)
textbox(s, Inches(1.25), Inches(4.85), Inches(10.5), Inches(0.5),
        "Où l'on découvre que « 100 % de couverture » ne veut pas dire « 0 bug ».", 13.5, RGBColor(0xC9, 0xCE, 0xDC), italic=True)
textbox(s, Inches(1.25), Inches(6.55), Inches(8), Inches(0.5), "Ton nom — Date de la conférence", 13, MUTED_D)
sticker_circle(s, Inches(11.3), Inches(5.85), Inches(1.7), "100%\nauthentique", MARKER, INK, rotation=-10, size=13)
skip_footer()
add_transition(s, kind="fade")

# ==================================================== 2. QUI SUIS-JE ======
s = blank(prs)
bg(s, PAPER)
side_bar(s, AMBER)
section_tag(s, "Avant de commencer", AMBER, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1), "Qui suis-je ?", 32, TXT_DARK, bold=True)

bio = [
    ("Développeur Java", "Suffisamment d'années pour avoir déjà tout cassé au moins une fois. Deux, si on compte la prod.", AMBER),
    ("Écrit des tests", "Un ratio tests / code que je ne montrerai à personne — j'ai aussi un Utils.java de 2000 lignes qui préfère qu'on ne l'interroge pas.", TEAL),
    ("Ici pour une raison précise", "Vous convaincre de regarder VOTRE rapport de couverture. Le vrai. Pas celui que vous imaginez.", CORAL),
]
cx, cw, gap = Inches(0.9), Inches(3.58), Inches(0.28)
for i, (title, body, accent) in enumerate(bio):
    left = cx + i * (cw + gap)
    raised_card(s, left, Inches(2.62), cw, Inches(3.35), PAPER_CARD, PAPER_CARD_HI)
    rect(s, left, Inches(2.62), cw, Inches(0.1), accent)
    textbox(s, left + Inches(0.32), Inches(2.98), cw - Inches(0.6), Inches(0.8), title, 17, TXT_DARK, bold=True, line_spacing=1.1)
    textbox(s, left + Inches(0.32), Inches(3.82), cw - Inches(0.6), Inches(1.95), body, 13, TXT_DARK, line_spacing=1.2)
speech_bubble(s, Inches(6.2), Inches(2.1), Inches(2.0), Inches(0.62), "confidentiel", fill=INK, text_color=MARKER,
              size=12.5, tail="br")
textbox(s, Inches(0.9), Inches(6.35), Inches(11), Inches(0.4),
        "(personnalisez cette slide avec votre vraie bio avant le jour J)", 11, MUTED_L, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 3. ICEBREAKER =======
s = blank(prs)
bg(s, INK)
textbox(s, Inches(9.1), Inches(2.1), Inches(4.2), Inches(3.6), "?", 300, INK_CARD, bold=True)
section_tag(s, "Sondage (sans jugement)", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), "Levez la main si...", 32, TXT_LIGHT, bold=True)

items = [
    "...vous avez déjà écrit un test juste pour faire plaisir à la CI.",
    "...vous avez déjà vu 100 % de couverture sur un fichier plein de bugs.",
    "...vous ne savez pas, là, maintenant, ce que couvrent VOS tests.",
]
top = Inches(2.4)
for i, line in enumerate(items):
    sticker_circle(s, Inches(1.22), top + Inches(0.22), Inches(0.55), str(i + 1), MARKER, INK, rotation=-6, size=15)
    textbox(s, Inches(1.75), top, Inches(10.4), Inches(0.75), line, 19, TXT_LIGHT, line_spacing=1.15)
    top += Inches(1.1)

speech_bubble(s, Inches(0.9), Inches(6.0), Inches(4.6), Inches(0.75),
              "Pas de jugement. Enfin... un peu.", fill=MARKER, text_color=INK, tail="tl", italic=True)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ==================================================== 4. AGENDA ===========
s = blank(prs)
bg(s, PAPER)
side_bar(s, AMBER)
section_tag(s, "Au programme", AMBER, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1),
        "Une heure, quatre outils, zéro slide inutile (promis)", 26, TXT_DARK, bold=True)

agenda = [
    ("1", "Le problème", "Pourquoi une suite de tests toute verte ne prouve absolument rien", "5 min", CORAL),
    ("2", "La stack", "JUnit, Cucumber, Quarkus, Jacoco — qui fait quoi (et qui ne fait pas le café)", "10 min", AMBER),
    ("3", "Démo : le projet", "Un agenda malin, ses tests, ses angles morts", "10 min", TEAL),
    ("4", "Le rapport qui ne ment pas", "Jacoco en direct, JUnit contre Cucumber", "15 min", LIME),
    ("5", "Bonus : SonarQube", "Le même rapport, dans un vrai dashboard (spoiler : pas SOAR)", "10 min", INKY_BLUE),
    ("6", "Ce qu'on retient", "Et deux pièges qu'on a vraiment pris en pleine figure", "5 min", CORAL),
]
top = Inches(2.42)
row_h = Inches(0.68)
for num, title, sub, dur, accent in agenda:
    rect(s, Inches(0.9), top + Inches(0.02), Inches(0.06), Inches(0.5), accent)
    textbox(s, Inches(1.15), top, Inches(0.55), Inches(0.6), num, 19, on_light(accent), bold=True)
    textbox(s, Inches(1.75), top - Inches(0.02), Inches(7.6), Inches(0.4), title, 15.5, TXT_DARK, bold=True)
    textbox(s, Inches(1.75), top + Inches(0.3), Inches(8.6), Inches(0.35), sub, 11, TXT_DARK)
    chip(s, Inches(11.0), top + Inches(0.05), dur, PAPER_CARD, MUTED_L, size=10.5)
    top += row_h
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 5. LE CONSTAT =======
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Le constat", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1),
        "On a des tests. On n'a toujours aucune idée de ce qu'ils font.", 27, TXT_DARK, bold=True)

cards = [
    ("01", "On écrit des tests", "JUnit, Cucumber : les suites tournent au vert à chaque build. On est très fiers. À raison, d'ailleurs.", TEAL),
    ("02", "On ne sait pas ce qu'ils couvrent", "Quelles classes ? Quelles branches ? Une CI verte suffit largement à calmer tout le monde.", AMBER),
    ("03", "Les angles morts restent invisibles", "Jusqu'au bug en prod, dans le code qu'aucun test n'a jamais exécuté. Généralement un vendredi. Toujours un vendredi.", CORAL),
]
cx, cw, gap = Inches(0.9), Inches(3.58), Inches(0.28)
for i, (num, title, body, accent) in enumerate(cards):
    left = cx + i * (cw + gap)
    rot = -2 if i == 1 else (2 if i == 2 else 0)
    card = raised_card(s, left, Inches(2.7), cw, Inches(3.55), PAPER_CARD, PAPER_CARD_HI)
    card.rotation = rot
    rect(s, left, Inches(2.7), cw, Inches(0.1), accent)
    textbox(s, left + Inches(0.32), Inches(3.05), cw - Inches(0.6), Inches(0.7), num, 28, on_light(accent), bold=True)
    textbox(s, left + Inches(0.32), Inches(3.75), cw - Inches(0.6), Inches(1.0), title, 16.5, TXT_DARK, bold=True, line_spacing=1.05)
    textbox(s, left + Inches(0.32), Inches(4.6), cw - Inches(0.6), Inches(1.5), body, 12.5, TXT_DARK, line_spacing=1.15)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 6. LA STACK =========
s = blank(prs)
bg(s, PAPER)
side_bar(s, TEAL)
section_tag(s, "La stack technique", TEAL, dark=False)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(0.9),
        "Quatre outils, quatre questions différentes", 28, TXT_DARK, bold=True)

tools = [
    ("JUnit 5", "« La logique métier fait-elle ce qu'elle doit ? »\nTests unitaires ciblés, rapides — le genre d'ami qui vous dit direct que votre code est nul, sans détour.", AMBER),
    ("Cucumber", "« Le comportement attendu est-il respecté ? »\nScénarios Gherkin lisibles — le seul test que votre chef de projet pourra théoriquement relire.", TEAL),
    ("Quarkus", "« Comment tout ça tourne ensemble ? »\nLe framework qui démarre l'appli et pilote les tests — le collègue qui organise tout sans qu'on lui demande.", LIME),
    ("Jacoco", "« Qu'est-ce qui a vraiment été exécuté ? »\nL'instrument de mesure — celui qui ne ment jamais, contrairement à votre estimation à l'oral.", CORAL),
]
gx, gy = Inches(0.9), Inches(2.15)
gw, gh = Inches(5.58), Inches(2.28)
gapx, gapy = Inches(0.3), Inches(0.24)
for i, (name, desc, accent) in enumerate(tools):
    col, row = i % 2, i // 2
    left, top = gx + col * (gw + gapx), gy + row * (gh + gapy)
    raised_card(s, left, top, gw, gh, PAPER_CARD, PAPER_CARD_HI)
    rect(s, left, top, Inches(0.1), gh, accent)
    chip(s, left + Inches(0.32), top + Inches(0.2), name, accent, INK, size=13)
    textbox(s, left + Inches(0.35), top + Inches(0.82), gw - Inches(0.65), Inches(1.35), desc, 12.5, TXT_DARK, line_spacing=1.2)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ============================================== 7. LE PROJET DEMO =========
s = blank(prs)
bg(s, INK)
section_tag(s, "Le terrain de jeu", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(0.9), "Un agenda malin", 30, TXT_LIGHT, bold=True)
textbox(s, Inches(0.9), Inches(1.75), Inches(10.8), Inches(0.7),
        "Une API Quarkus qui planifie des événements, détecte les conflits d'horaire,\n"
        "génère des récurrences, et glisse une citation du jour — parce qu'une démo a le droit d'être un peu sympa.",
        13.5, RGBColor(0xC9, 0xCE, 0xDC), line_spacing=1.2)


def box(slide, left, top, width, height, title, subtitle, accent):
    raised_card(slide, left, top, width, height, INK_CARD, INK_CARD_HI)
    rect(slide, left, top, width, Inches(0.08), accent)
    textbox(slide, left + Inches(0.22), top + Inches(0.18), width - Inches(0.4), Inches(0.4), title, 13.5, TXT_LIGHT, bold=True)
    textbox(slide, left + Inches(0.22), top + Inches(0.58), width - Inches(0.4), Inches(0.6), subtitle, 10.5, MUTED_ON_CARD_HI, line_spacing=1.1)


top1 = Inches(2.55)
box(s, Inches(0.9), top1, Inches(4.15), Inches(1.0), "CalendarResource", "Couche REST — JSON in/out", MARKER)
rect(s, Inches(2.97), Inches(3.6), Inches(0.05), Inches(0.35), MUTED_D)

top2 = Inches(4.05)
services = [
    ("EventService", "création + recherche", TEAL),
    ("RecurrenceService", "quotidien / hebdo / mensuel", LIME),
    ("HolidayService", "jours fériés", CORAL),
    ("QuoteOfTheDayService", "citation du jour", AMBER),
]
sw = Inches(2.58)
for i, (name, sub, accent) in enumerate(services):
    left = Inches(0.9) + i * (sw + Inches(0.14))
    box(s, left, top2, sw, Inches(1.0), name, sub, accent)

rect(s, Inches(2.1), Inches(5.05), Inches(0.05), Inches(0.35), MUTED_D)
box(s, Inches(0.9), Inches(5.4), Inches(4.15), Inches(0.85), "ConflictDetector", "logique pure — aucune dépendance", TEAL)

speech_bubble(s, Inches(6.5), Inches(5.15), Inches(5.9), Inches(1.15),
              "Aucune base de données : le sujet du jour, c'est la couverture de\ntests — pas Hibernate. On se recentre.",
              fill=MARKER, text_color=INK, tail="tl", size=12.5, italic=True, bold=False)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ==================================================== 8. ZOOM JUNIT =======
s = blank(prs)
bg(s, PAPER)
side_bar(s, AMBER)
section_tag(s, "Zoom — JUnit", AMBER, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1), "Le microscope", 32, TXT_DARK, bold=True)
textbox(s, Inches(0.9), Inches(2.05), Inches(10.9), Inches(0.9),
        "JUnit teste une unité de code isolée — une méthode, une classe — sans lancer\n"
        "toute l'application. C'est rapide, précis, et ça ne pardonne rien.", 15, TXT_DARK, line_spacing=1.3)

feat = [
    ("Rapide", "Des milliers de tests en quelques secondes. Votre café, lui, met plus longtemps.", TEAL),
    ("Isolé", "Pas de serveur, pas de réseau, pas de surprise. Le rêve, quoi.", AMBER),
    ("Technique", "Pensé par et pour les développeurs. Personne d'autre ne relira jamais un assertEquals.", CORAL),
]
cw = Inches(3.58)
for i, (t, d, accent) in enumerate(feat):
    left = Inches(0.9) + i * (cw + Inches(0.28))
    raised_card(s, left, Inches(3.35), cw, Inches(1.55), PAPER_CARD, PAPER_CARD_HI)
    rect(s, left, Inches(3.35), Inches(0.08), Inches(1.55), accent)
    textbox(s, left + Inches(0.3), Inches(3.58), cw - Inches(0.5), Inches(0.4), t, 16, TXT_DARK, bold=True)
    textbox(s, left + Inches(0.3), Inches(3.98), cw - Inches(0.5), Inches(0.85), d, 12, TXT_DARK, line_spacing=1.15)

textbox(s, Inches(0.9), Inches(5.55), Inches(10.9), Inches(0.9),
        "Dans notre agenda malin : ConflictDetector, RecurrenceService — de la logique\n"
        "pure, testée sans jamais démarrer Quarkus.", 14, TXT_DARK, italic=True, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ==================================================== 9. JUNIT CODE =======
s = blank(prs)
bg(s, PAPER)
side_bar(s, AMBER)
section_tag(s, "JUnit — en action", AMBER, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), "Viser juste, vite", 30, TXT_DARK, bold=True)

code = (
    '@Test\n'
    'void deuxEvenementsQuiSeTouchentNeSontPasEnConflit() {\n'
    '    Event a = eventAt("a", 9, 10);\n'
    '    Event b = eventAt("b", 10, 11);\n\n'
    '    assertFalse(detector.isConflicting(a, b));\n'
    '}'
)
code_window(s, Inches(0.9), Inches(2.15), Inches(11.5), Inches(3.0), code, size=15)

textbox(s, Inches(0.9), Inches(5.5), Inches(10.8), Inches(1.2),
        "ConflictDetectorTest : 4 tests, 4 cas limites — chevauchement, contact exact,\n"
        "séparation nette, et réflexivité (oui, on vérifie qu'un événement n'est pas en\n"
        "conflit avec lui-même — sinon, c'est un problème existentiel, pas un bug).",
        13.5, TXT_DARK, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 10. ZOOM CUCUMBER ======
s = blank(prs)
bg(s, PAPER)
side_bar(s, TEAL)
section_tag(s, "Zoom — Cucumber", TEAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1), "Le grand angle", 32, TXT_DARK, bold=True)
textbox(s, Inches(0.9), Inches(2.05), Inches(10.9), Inches(0.9),
        "Cucumber teste le comportement observable, de bout en bout, en français\n"
        "lisible. Le même texte sert de spec fonctionnelle ET de test automatisé.", 15, TXT_DARK, line_spacing=1.3)

feat = [
    ("Lisible", "Même un product owner peut le relire (et le corriger). Sensation forte garantie.", AMBER),
    ("Bout en bout", "Passe par la vraie API REST, pas un mock. Comme un vrai client, en moins énervé.", TEAL),
    ("Fonctionnel", "Décrit ce que fait le produit, pas comment. Ça change des tickets Jira écrits un vendredi soir.", CORAL),
]
cw = Inches(3.58)
for i, (t, d, accent) in enumerate(feat):
    left = Inches(0.9) + i * (cw + Inches(0.28))
    raised_card(s, left, Inches(3.35), cw, Inches(1.55), PAPER_CARD, PAPER_CARD_HI)
    rect(s, left, Inches(3.35), Inches(0.08), Inches(1.55), accent)
    textbox(s, left + Inches(0.3), Inches(3.58), cw - Inches(0.5), Inches(0.4), t, 16, TXT_DARK, bold=True)
    textbox(s, left + Inches(0.3), Inches(3.98), cw - Inches(0.5), Inches(0.85), d, 12, TXT_DARK, line_spacing=1.15)

textbox(s, Inches(0.9), Inches(5.55), Inches(10.9), Inches(0.9),
        "Dans notre agenda malin : la création d'événement, la détection de conflit,\n"
        "le signalement d'un jour férié — trois scénarios, en français.", 14, TXT_DARK, italic=True, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 11. CUCUMBER CODE ======
s = blank(prs)
bg(s, PAPER)
side_bar(s, TEAL)
section_tag(s, "Cucumber — en action", TEAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9),
        "Le scénario que tout le monde comprend", 26, TXT_DARK, bold=True)

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
code_window(s, Inches(0.9), Inches(2.15), Inches(11.5), Inches(3.4), gherkin, size=14)

textbox(s, Inches(0.9), Inches(5.8), Inches(10.8), Inches(0.85),
        "Vous remarquerez que même le scénario de test sait qu'un comité de pilotage\n"
        "prend toute la place dans l'agenda. Ça, c'est du réalisme métier.", 14, TXT_DARK, line_spacing=1.25)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 12. LE MATCH ===========
s = blank(prs)
bg(s, PAPER)
side_bar(s, MARKER)
section_tag(s, "Le clash (amical)", MARKER, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1),
        "JUnit vs Cucumber : qui gagne ?", 28, TXT_DARK, bold=True)

col_w = Inches(5.35)
left1, left2 = Inches(0.9), Inches(6.55)
c1 = raised_card(s, left1, Inches(2.4), col_w, Inches(3.55), PAPER_CARD, PAPER_CARD_HI)
c1.rotation = -1.5
rect(s, left1, Inches(2.4), col_w, Inches(0.1), AMBER)
textbox(s, left1 + Inches(0.35), Inches(2.72), col_w - Inches(0.6), Inches(0.5), "JUnit", 22, TXT_DARK, bold=True)
for i, line in enumerate(["Rapide", "Isolé", "Technique", "Pour les devs"]):
    textbox(s, left1 + Inches(0.35), Inches(3.4) + Inches(0.52) * i, col_w - Inches(0.6), Inches(0.5), "— " + line, 15, TXT_DARK)

c2 = raised_card(s, left2, Inches(2.4), col_w, Inches(3.55), PAPER_CARD, PAPER_CARD_HI)
c2.rotation = 1.5
rect(s, left2, Inches(2.4), col_w, Inches(0.1), TEAL)
textbox(s, left2 + Inches(0.35), Inches(2.72), col_w - Inches(0.6), Inches(0.5), "Cucumber", 22, TXT_DARK, bold=True)
for i, line in enumerate(["Lisible", "Bout en bout", "Fonctionnel", "Pour tout le monde"]):
    textbox(s, left2 + Inches(0.35), Inches(3.4) + Inches(0.52) * i, col_w - Inches(0.6), Inches(0.5), "— " + line, 15, TXT_DARK)

sticker_circle(s, Inches(6.4), Inches(2.4), Inches(0.95), "MATCH\nNUL", INK, MARKER, rotation=-8, size=11)

speech_bubble(s, Inches(0.9), Inches(6.2), Inches(11.4), Inches(0.65),
              "Spoiler : il n'y a pas de gagnant. Le seul qui gagne, c'est le code — testé sous deux angles.",
              fill=MARKER, text_color=INK, tail="tl", size=13.5)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 13. BASCULE DEMO 1 =====
s = blank(prs)
bg(s, INK)
dot_grid(s, Inches(0.7), Inches(1.0), rows=3, cols=10, color=INK_CARD)
rect(s, Inches(6.47), Inches(2.5), Inches(0.4), Inches(0.4), CORAL, shape=MSO_SHAPE.OVAL)
textbox(s, Inches(0.9), Inches(3.05), Inches(11.5), Inches(1.4), "EN DIRECT", 50, TXT_LIGHT, bold=True, align=PP_ALIGN.CENTER)
speech_bubble(s, Inches(2.9), Inches(4.35), Inches(7.5), Inches(0.75),
              "on arrête PowerPoint. direction le terminal, pour de vrai — fermez Slack pendant qu'on y est",
              fill=MARKER, text_color=INK, tail="tl", size=13.5, italic=True)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="cut")

# ================================================= 14. ZOOM JACOCO ========
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Zoom — Jacoco", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1),
        "Un agent qui espionne le bytecode (légalement)", 25, TXT_DARK, bold=True)

steps_j = [
    ("1", "Au démarrage de la JVM", "Un agent Java (-javaagent) s'attache et instrumente chaque classe chargée."),
    ("2", "Pendant les tests", "Chaque ligne, chaque branche exécutée est comptée — en silence, sans ralentir grand-chose. Un espion discret."),
    ("3", "À l'arrêt de la JVM", "Tout est vidé dans un fichier .exec. Puis jacoco-maven-plugin le transforme en rapport HTML/XML/CSV."),
]
top = Inches(2.4)
for num, t, d in steps_j:
    sticker_circle(s, Inches(1.22), top + Inches(0.32), Inches(0.65), num, CORAL, INK, rotation=-6, size=20)
    textbox(s, Inches(1.75), top, Inches(10), Inches(0.4), t, 16, TXT_DARK, bold=True)
    textbox(s, Inches(1.75), top + Inches(0.38), Inches(10), Inches(0.6), d, 12.5, TXT_DARK, line_spacing=1.2)
    top += Inches(1.15)

speech_bubble(s, Inches(0.9), Inches(6.05), Inches(11.4), Inches(0.65),
              "Non, ce n'est pas de l'espionnage industriel. C'est juste un agent très curieux, payé en aucune façon.",
              fill=MARKER, text_color=INK, tail="tl", size=13, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 15. JACOCO OVERVIEW ====
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Jacoco — le rapport", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.7),
        "Pas une maquette Figma. Le vrai rapport.", 26, TXT_DARK, bold=True)
browser_frame(s, f"{SCREENSHOTS}/jacoco-overview.png", Inches(0.9), Inches(2.05), Inches(11.5))
textbox(s, Inches(0.9), Inches(6.4), Inches(11), Inches(0.5),
        "Vrai export HTML, généré il y a quelques heures, par la commande qu'on vient de lancer. Pas d'entourloupe.",
        12.5, MUTED_L, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 16. JACOCO PREUVE ======
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Jacoco — la preuve", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(9.0), Inches(0.55),
        "La branche MENSUELLE, prise en flagrant délit", 22, TXT_DARK, bold=True)
sticker_circle(s, Inches(11.55), Inches(1.05), Inches(1.55), "Bissextile !", MARKER, INK, rotation=-10, size=13)
browser_frame(s, f"{SCREENSHOTS}/jacoco-recurrence-source.png", Inches(2.87), Inches(1.9), Inches(7.6))
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 17. JUNIT VS CUC JACOCO=
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Jacoco", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.7), "Ce que les tests ont vraiment touché", 26, TXT_DARK, bold=True)
textbox(s, Inches(0.9), Inches(1.78), Inches(11), Inches(0.4),
        "Mesure réelle, extraite du build — couverture de lignes, JUnit contre Cucumber", 12.5, MUTED_L, italic=True)

leg_top = Inches(2.2)
chip(s, Inches(0.9), leg_top, "JUnit (unitaire)", AMBER, INK, size=11)
chip(s, Inches(2.95), leg_top, "Cucumber (intégration)", TEAL, INK, size=11)

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
row_h = Inches(0.58)
bar_h = Inches(0.19)
top0 = Inches(2.68)
for i, (name, pct_junit, pct_cuc) in enumerate(data):
    top = top0 + i * row_h
    textbox(s, Inches(0.9), top + Inches(0.09), Inches(2.65), Inches(0.4), name, 11.5, TXT_DARK, align=PP_ALIGN.RIGHT)

    rect(s, chart_left, top, chart_w, bar_h, PAPER_CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    barw = Emu(int(chart_w * max(pct_junit, 3) / 100))
    rect(s, chart_left, top, barw, bar_h, AMBER, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    textbox(s, chart_left + chart_w + Inches(0.1), top - Inches(0.02), Inches(0.7), Inches(0.3), f"{pct_junit}%", 10.5, TXT_DARK, bold=True)

    top2v = top + bar_h + Inches(0.045)
    rect(s, chart_left, top2v, chart_w, bar_h, PAPER_CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    barw2 = Emu(int(chart_w * max(pct_cuc, 3) / 100))
    rect(s, chart_left, top2v, barw2, bar_h, TEAL, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    textbox(s, chart_left + chart_w + Inches(0.1), top2v - Inches(0.02), Inches(0.7), Inches(0.3), f"{pct_cuc}%", 10.5, TXT_DARK, bold=True)

textbox(s, Inches(0.9), Inches(6.15), Inches(11), Inches(0.32),
        "JUnit couvre la logique métier ; Cucumber couvre la couche REST — presque aucun recouvrement.",
        11.5, MUTED_L, italic=True)
speech_bubble(s, Inches(0.9), Inches(6.5), Inches(11.4), Inches(0.6),
              "Mention spéciale à RecurrenceRequest : 0 % partout. Personne n'y a jamais touché. Personne.",
              fill=MARKER, text_color=INK, tail="tl", size=12, bold=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 18. TERMINAL ===========
s = blank(prs)
bg(s, INK)
section_tag(s, "Sans ouvrir de navigateur", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.05), Inches(11), Inches(0.8), "Le récap, direct dans le terminal", 26, TXT_LIGHT, bold=True)
picture(s, f"{SCREENSHOTS}/terminal-mock.png", Inches(2.67), Inches(1.85), Inches(8.0), frame_color=INK_CARD, pad_in=0.05)
textbox(s, Inches(0.9), Inches(6.8), Inches(11.5), Inches(0.4),
        "coverage-summary.sh fait le café à votre place : rouge, orange, vert, classe par classe.",
        12.5, MUTED_D, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 19. EN DIRECT ==========
s = blank(prs)
bg(s, PAPER)
side_bar(s, LIME)
section_tag(s, "En direct", LIME, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), "Trois commandes, un radar complet", 28, TXT_DARK, bold=True)

steps = [
    ("1", "./mvnw test", "Build + JUnit + Cucumber + 3 rapports Jacoco générés automatiquement."),
    ("2", "./scripts/coverage-summary.sh", "Le récap coloré JUnit / Cucumber / global, côte à côte, dans le terminal."),
    ("3", "open target/jacoco-report/index.html", "Le détail ligne par ligne — et les variantes -junit / -cucumber pour comparer."),
]
top = Inches(2.25)
for num, cmd, desc in steps:
    sticker_circle(s, Inches(1.28), top + Inches(0.42), Inches(0.85), num, LIME, INK, rotation=-6, size=26)
    textbox(s, Inches(1.95), top + Inches(0.06), Inches(10.2), Inches(0.5), cmd, 17, TXT_DARK, bold=True, font=FONT_MONO)
    textbox(s, Inches(1.95), top + Inches(0.55), Inches(10.2), Inches(0.5), desc, 12.5, TXT_DARK)
    top += Inches(1.45)

textbox(s, Inches(0.9), Inches(6.5), Inches(11), Inches(0.4),
        "Rien d'exotique, rien à installer de plus que ce qu'on a déjà dans le pom.xml.", 12.5, MUTED_L, italic=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 20. BONUS SONAR ========
s = blank(prs)
bg(s, INK)
section_tag(s, "Bonus (promis, pas SOAR)", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), "Et dans un vrai dashboard ?", 28, TXT_LIGHT, bold=True)
textbox(s, Inches(0.9), Inches(1.85), Inches(10.8), Inches(0.5),
        "Les deux mêmes rapports Jacoco XML, importés tels quels dans SonarQube.", 13.5, RGBColor(0xC9, 0xCE, 0xDC))

stats = [("77,7 %", "couverture globale", MARKER), ("82 %", "lignes", AMBER), ("65 %", "branches", TEAL)]
sw, sx = Inches(3.58), Inches(0.9)
for i, (value, label, accent) in enumerate(stats):
    left = sx + i * (sw + Inches(0.28))
    raised_card(s, left, Inches(2.65), sw, Inches(1.65), INK_CARD, INK_CARD_HI)
    rect(s, left, Inches(2.65), sw, Inches(0.08), accent)
    textbox(s, left, Inches(2.9), sw, Inches(0.75), value, 36, accent, bold=True, align=PP_ALIGN.CENTER)
    textbox(s, left, Inches(3.62), sw, Inches(0.4), label, 12.5, MUTED_ON_CARD_HI, align=PP_ALIGN.CENTER)

textbox(s, Inches(0.9), Inches(4.65), Inches(10.8), Inches(0.35),
        "Mesure réelle, obtenue en lançant l'analyse sur ce projet — pas une maquette.", 11.5, MUTED_D, italic=True)

code_window(s, Inches(0.9), Inches(5.15), Inches(11.5), Inches(1.1),
            "docker compose -f sonarqube/docker-compose.yml up -d\n"
            "./mvnw test sonar:sonar -Dsonar.token=<ton_token>", size=13.5)

textbox(s, Inches(0.9), Inches(6.5), Inches(10.8), Inches(0.4),
        "SonarQube Community en local — aucun compte SonarCloud, aucune dépendance réseau pendant le talk.", 12, MUTED_D)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 21. SONAR DASHBOARD ====
s = blank(prs)
bg(s, PAPER)
side_bar(s, INKY_BLUE)
section_tag(s, "SonarQube — dashboard", INKY_BLUE, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.7), "Coverage 77,7 %, en vrai, dans l'interface", 24, TXT_DARK, bold=True)
browser_frame(s, f"{SCREENSHOTS}/sonar-overview.png", Inches(3.37), Inches(1.95), Inches(6.6))
textbox(s, Inches(0.9), Inches(6.55), Inches(11.5), Inches(0.4),
        "Sonar ne mesure rien lui-même : il relit ce que Jacoco a déjà dit et fait semblant d'avoir tout calculé.",
        12, MUTED_L, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 22. SONAR MEASURES =====
s = blank(prs)
bg(s, PAPER)
side_bar(s, INKY_BLUE)
section_tag(s, "SonarQube — mesures", INKY_BLUE, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.7), "Le détail, fichier par fichier", 24, TXT_DARK, bold=True)
browser_frame(s, f"{SCREENSHOTS}/sonar-coverage-list.png", Inches(3.37), Inches(1.95), Inches(6.6))
textbox(s, Inches(0.9), Inches(6.55), Inches(11.5), Inches(0.4),
        "Mêmes pourcentages que dans notre terminal. Même vérité, vitrine plus chère.",
        12, MUTED_L, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 23. SONAR CODE =========
s = blank(prs)
bg(s, PAPER)
side_bar(s, INKY_BLUE)
section_tag(s, "SonarQube — la preuve, encore", INKY_BLUE, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11.8), Inches(0.55), "Même branche rouge, autre outil", 22, TXT_DARK, bold=True)
browser_frame(s, f"{SCREENSHOTS}/sonar-code-drilldown.png", Inches(3.37), Inches(1.9), Inches(6.6))
textbox(s, Inches(0.9), Inches(6.55), Inches(11.5), Inches(0.4),
        "Pas un artefact d'un outil bizarre : un fait sur votre code, confirmé deux fois de suite.",
        12, MUTED_L, italic=True, align=PP_ALIGN.CENTER)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 24. LES EXCUSES ========
s = blank(prs)
bg(s, PAPER)
side_bar(s, CORAL)
section_tag(s, "Confessions collectives", CORAL, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(1.1), "Le best-of des excuses pour ne pas tester", 26, TXT_DARK, bold=True)

excuses = [
    ("« Ça marche sur ma machine. »", "Votre machine n'ira pas en prod avec vous. Elle ne peut pas témoigner."),
    ("« On testera après le sprint. »", "Le sprint suivant aussi. Et celui d'après. À ce rythme, on teste au démantèlement."),
    ("« C'est trop simple pour bugger. »", "Neuf incidents de prod sur dix commencent exactement comme ça."),
    ("« Le stagiaire a dit que ça passait. »", "Un mardi après-midi ensoleillé, à la main, une seule fois."),
    ("« 100 % de couverture, on n'a plus besoin de relire. »", "La couverture mesure ce qui a été EXÉCUTÉ. Pas ce qui a été VÉRIFIÉ."),
]
top = Inches(2.35)
row_h = Inches(0.72)
for i, (excuse, retort) in enumerate(excuses):
    chip(s, Inches(0.9), top + Inches(0.02), f"{i+1:02d}", CORAL, INK, size=11)
    textbox(s, Inches(1.85), top, Inches(10.5), Inches(0.4), excuse, 14.5, TXT_DARK, bold=True)
    textbox(s, Inches(1.85), top + Inches(0.35), Inches(10.5), Inches(0.4), retort, 11, MUTED_L, italic=True)
    top += row_h

speech_bubble(s, Inches(0.9), Inches(6.35), Inches(11.5), Inches(0.7),
              "Spoiler : aucune de ces cinq phrases n'a jamais empêché un incendie en prod. Pas une seule. "
              "J'ai vérifié. Enfin... je crois.", fill=MARKER, text_color=INK, tail="tl", size=12.5, bold=True)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 25. RETOUR D'XP ========
s = blank(prs)
bg(s, INK)
section_tag(s, "Retour d'expérience", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9),
        "Deux pièges qu'on a vraiment eus en préparant cette conf", 22, TXT_LIGHT, bold=True)

stories = [
    ("Le QuarkusClassLoader fantôme",
     "Deux exécutions Surefire, deux agents Jacoco... et pourtant tout à 0 %. Coupable : "
     "l'extension quarkus-jacoco mesure le code CDI toute seule, dans son coin, sans prévenir personne.",
     AMBER),
    ("L'accent qui a cassé Gherkin",
     "« Fonctionnalite » sans accent ne veut RIEN dire pour un parseur Gherkin en français. "
     "Un é manquant, et Cucumber devient aussi utile qu'un GPS sans signal.",
     TEAL),
]
top = Inches(2.3)
for title, body, accent in stories:
    raised_card(s, Inches(0.9), top, Inches(11.5), Inches(1.9), INK_CARD, INK_CARD_HI)
    rect(s, Inches(0.9), top, Inches(0.1), Inches(1.9), accent)
    textbox(s, Inches(1.3), top + Inches(0.2), Inches(10.9), Inches(0.45), title, 17, TXT_LIGHT, bold=True)
    textbox(s, Inches(1.3), top + Inches(0.68), Inches(10.9), Inches(1.1), body, 12.5, MUTED_ON_CARD_HI, line_spacing=1.3)
    top += Inches(2.25)

textbox(s, Inches(0.9), Inches(6.78), Inches(11), Inches(0.4),
        "Le seul avantage qu'on a eu sur vous : un rapport de couverture pour le prouver noir sur blanc.",
        12.5, MARKER, italic=True)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 26. A RETENIR ==========
s = blank(prs)
bg(s, INK)
section_tag(s, "À retenir", MARKER, dark=True)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), "Ce qu'il faut retenir", 30, TXT_LIGHT, bold=True)
sticker_circle(s, Inches(11.75), Inches(1.0), Inches(1.15), "tl;dr", MARKER, INK, rotation=6, size=13)

points = [
    ("Un test vert ne dit pas ce qu'il a vérifié.", "La couverture, si."),
    ("JUnit et Cucumber répondent à deux questions différentes.", "« Ça marche ? » contre « c'est le bon comportement ? »"),
    ("Le rapport de couverture n'est pas un objectif.", "C'est un radar : il montre où regarder en premier."),
    ("Un outil ne remplace pas la question qu'on ne s'est pas posée.", "Ni Jacoco, ni Sonar, ni celui d'après."),
]
top = Inches(2.35)
for i, (line1, line2) in enumerate(points):
    sticker_circle(s, Inches(1.35), top + Inches(0.32), Inches(0.75), str(i + 1), MARKER, INK, rotation=-6, size=22)
    textbox(s, Inches(2.2), top + Inches(0.02), Inches(9.8), Inches(0.55), line1, 16.5, TXT_LIGHT, bold=True)
    textbox(s, Inches(2.2), top + Inches(0.53), Inches(9.8), Inches(0.5), line2, 12.5, MUTED_D)
    top += Inches(1.2)
footer(s, TOTAL_SLIDES, dark=True)
add_transition(s, kind="fade")

# ================================================= 27. POUR ALLER PLUS LOIN
s = blank(prs)
bg(s, PAPER)
side_bar(s, LIME)
section_tag(s, "Pour la suite", LIME, dark=False)
textbox(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.65), "Si vous voulez creuser", 28, TXT_DARK, bold=True)
textbox(s, Inches(0.9), Inches(1.82), Inches(11), Inches(0.4),
        "Code et scripts, en clair. Le reste (mes doutes existentiels sur plusMonths()) reste entre moi et mon terminal.",
        12, MUTED_L, italic=True)

links = [
    ("Le dépôt de ce projet", "github.com/sidevconcept/couverture-junit-cucumber-jacoco", AMBER),
    ("Guide Quarkus + Jacoco", "quarkus.io/guides/tests-with-coverage", TEAL),
    ("Extension Cucumber pour Quarkus", "docs.quarkiverse.io/quarkus-cucumber", LIME),
    ("SonarQube Community", "docs.sonarsource.com", CORAL),
]
top = Inches(2.6)
for title, url, accent in links:
    rect(s, Inches(0.9), top + Inches(0.06), Inches(0.16), Inches(0.16), accent, shape=MSO_SHAPE.OVAL)
    textbox(s, Inches(1.3), top, Inches(10.6), Inches(0.4), title, 16, TXT_DARK, bold=True)
    textbox(s, Inches(1.3), top + Inches(0.38), Inches(10.6), Inches(0.4), url, 12.5, TXT_DARK, font=FONT_MONO)
    top += Inches(0.98)
footer(s, TOTAL_SLIDES)
add_transition(s, kind="fade")

# ================================================= 28. MERCI ==============
s = blank(prs)
bg(s, INK)
dot_grid(s, Inches(0.7), Inches(5.3), rows=3, color=INK_CARD)
headline(s, Inches(0.9), Inches(2.4), Inches(8.3), Inches(1.4), [("Merci.", TXT_LIGHT, True)], 52)
textbox(s, Inches(0.95), Inches(3.6), Inches(8.3), Inches(0.5), "Questions ?", 22, MARKER)
speech_bubble(s, Inches(0.95), Inches(4.25), Inches(7.6), Inches(1.0),
              "et si quelqu'un me dit « chez nous on a 100 % de couverture », je réponds déjà : sur quelle branche ?",
              fill=MARKER, text_color=INK, tail="tl", size=13, italic=True)
textbox(s, Inches(0.95), Inches(6.6), Inches(8.3), Inches(0.5),
        "https://github.com/sidevconcept/couverture-junit-cucumber-jacoco  —  sidev.concept06@gmail.com", 11.5, MUTED_D)

textbox(s, Inches(9.9), Inches(2.15), Inches(2.1), Inches(0.35), "Scanne-moi", 13, MARKER, bold=True, align=PP_ALIGN.CENTER)
picture(s, f"{SCREENSHOTS}/qr-github.png", Inches(9.7), Inches(2.55), Inches(2.5), frame_color=PAPER, pad_in=0.08)
skip_footer()
add_transition(s, kind="fade")

OUT = "/Users/sidneycohen/dev/projects/couverture-code/presentation/couverture-code-conference-dynamite.pptx"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("saved", OUT, "-", _counter[0], "slides numbered")
