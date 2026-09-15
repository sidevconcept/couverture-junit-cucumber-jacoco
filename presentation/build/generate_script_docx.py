#!/usr/bin/env python3
"""Génère une version Word imprimable de SCRIPT.md (le script de présentation),
pour l'avoir sur papier pendant le talk. Parse SCRIPT.md directement — pas de
contenu dupliqué à la main, donc pas de désynchronisation possible avec le
markdown source."""

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path("/Users/sidneycohen/dev/projects/couverture-code")
SCRIPT_MD = ROOT / "SCRIPT.md"
OUT = ROOT / "presentation" / "SCRIPT-conference-imprimable.docx"

NAVY = RGBColor(0x16, 0x28, 0x44)
INK = RGBColor(0x22, 0x22, 0x22)
MUTED = RGBColor(0x60, 0x60, 0x60)
GOLD = RGBColor(0x8A, 0x5A, 0x10)

# Regroupement des slides par bloc (pour les sauts de page), aligné sur le
# tableau de minutage de SCRIPT.md.
BLOCK_STARTS = {1: "Accroche + agenda", 5: "Le problème", 6: "La stack",
                8: "JUnit", 10: "Cucumber", 12: "Le match + bascule",
                14: "Jacoco (théorie + captures)", 19: "En direct",
                20: "Bonus SonarQube", 24: "Excuses + retour d'expérience",
                26: "Conclusion"}


def set_margins(doc, cm=2.0):
    for section in doc.sections:
        section.top_margin = Cm(cm)
        section.bottom_margin = Cm(cm)
        section.left_margin = Cm(cm)
        section.right_margin = Cm(cm)


def shade_paragraph(paragraph, hex_color="F2EFE7"):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)


def add_border(paragraph, color="C7B98A"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "4")
        el.set(qn("w:color"), color)
        pBdr.append(el)
    pPr.append(pBdr)


def style_base(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11.5)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.2


def add_heading(doc, text, level=1, color=NAVY, size=None, space_before=14):
    h = doc.add_heading(level=level)
    h.paragraph_format.space_before = Pt(space_before)
    h.paragraph_format.space_after = Pt(6)
    run = h.add_run(text)
    run.font.color.rgb = color
    if size:
        run.font.size = Pt(size)
    run.font.bold = True
    return h


def add_para(doc, text, italic=False, bold=False, size=11.5, color=INK,
             align=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.italic = italic
    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return p


def add_code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    shade_paragraph(p, "16283E")
    for i, line in enumerate(text.split("\n")):
        if i:
            p.add_run().add_break()
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0xE3, 0xE8, 0xF0)
    return p


def add_spoken(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.right_indent = Cm(0.4)
    shade_paragraph(p, "F6F3EA")
    add_border(p)
    for i, line in enumerate(text.split("\n")):
        if i:
            p.add_run().add_break()
        run = p.add_run(line)
        run.font.size = Pt(12)
        run.font.color.rgb = INK
    return p


def add_page_break(doc):
    doc.add_page_break()


def parse_slide_block(raw):
    """Sépare un bloc de slide en : titre, didascalies (italique), texte dit,
    blocs de code, et lignes soupape/alerte."""
    lines = raw.strip("\n").split("\n")
    title = lines[0].strip()
    body = "\n".join(lines[1:]).strip("\n")
    return title, body


def render_body(doc, body):
    # Isole les blocs ``` ... ``` (code) du reste.
    parts = re.split(r"```(?:bash)?\n(.*?)\n```", body, flags=re.S)
    in_quote = False
    for i, part in enumerate(parts):
        if i % 2 == 1:
            add_code(doc, part.strip("\n"))
            in_quote = False
            continue
        chunk = part.strip("\n")
        if not chunk:
            continue
        # Sépare les didascalies *(...)*, les alertes ⏱️, les sous-titres
        # "### ..." et le texte "parlé" — une réplique « ... » peut s'étaler
        # sur plusieurs paragraphes séparés par une ligne vide.
        for segment in re.split(r"\n\n+", chunk):
            segment = segment.strip()
            if not segment:
                continue
            if segment.startswith("### "):
                add_para(doc, segment[4:].strip(), bold=True, color=GOLD, size=12.5, space_after=4)
                in_quote = False
            elif segment.startswith("*(") and segment.endswith(")*"):
                add_para(doc, segment.strip("*()"), italic=True, color=MUTED, size=10.5)
            elif segment.startswith("⏱️"):
                add_para(doc, segment.replace("**", ""), bold=True, color=GOLD, size=11)
            elif segment.startswith("«") or in_quote:
                text = segment.lstrip("«").rstrip("»").replace("**", "").strip()
                add_spoken(doc, text)
                in_quote = not segment.rstrip().endswith("»")
            else:
                add_para(doc, segment.replace("**", ""), size=11)


def build():
    raw = SCRIPT_MD.read_text(encoding="utf-8")

    doc = Document()
    set_margins(doc)
    style_base(doc)

    # ---- page de garde --------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = title_p.add_run("La couverture de code, sans blabla")
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.color.rgb = NAVY

    add_para(doc, "Script de présentation — support papier", size=13, color=MUTED, space_after=2)
    add_para(doc, "Conférence ~60 minutes (+ questions) · support : couverture-code-conference.pptx (28 slides)",
              size=10.5, color=MUTED, space_after=14)

    add_para(doc,
             "Ce script est un guide, pas un texte à réciter mot pour mot. Les blagues "
             "entre « » sont des propositions — gardez celles qui vous ressemblent, jetez "
             "les autres sans remords.",
             italic=True, size=10.5, color=MUTED)
    add_para(doc,
             "Une bonne partie des vannes sont désormais aussi écrites sur les slides "
             "elles-mêmes. Rien n'empêche de les dire à voix haute en plus.",
             italic=True, size=10.5, color=MUTED, space_after=14)

    # ---- tableau de minutage ---------------------------------------------
    add_heading(doc, "Minutage indicatif", level=1, size=15, space_before=4)
    table_rows = re.findall(r"^\|(.+)\|$", raw, flags=re.M)[1:]  # skip header
    table_rows = [r for r in table_rows if not set(r.strip()) <= {"-", "|", " "}]
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, label in enumerate(["Bloc", "Slides", "Durée", "Cumulé"]):
        hdr[i].text = label
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(10)
    for row in table_rows:
        cells = [c.strip().replace("**", "") for c in row.split("|")]
        row_cells = table.add_row().cells
        for i, val in enumerate(cells[:4]):
            row_cells[i].text = val
            for p in row_cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)

    add_para(doc,
             "74 minutes de contenu pour un créneau d'1h : deux soupapes de sécurité "
             "(⏱️, repérées plus bas) permettent de ramener pile à l'heure en cas de retard.",
             italic=True, size=10, color=MUTED, space_after=4)

    add_page_break(doc)

    # ---- corps : un bloc par slide ----------------------------------------
    slide_blocks = re.split(r"\n## (Slide .+?)\n", raw)[1:]  # alterne titre, corps
    for i in range(0, len(slide_blocks), 2):
        title = slide_blocks[i].strip()
        body = slide_blocks[i + 1] if i + 1 < len(slide_blocks) else ""
        m = re.match(r"Slide (\d+)", title)
        num = int(m.group(1)) if m else None
        if num in BLOCK_STARTS:
            if num != 1:
                add_page_break(doc)
            add_heading(doc, BLOCK_STARTS[num].upper(), level=1, size=13, color=GOLD, space_before=0)
        add_heading(doc, title, level=2, size=15)
        render_body(doc, body.split("\n---")[0])

    # ---- notes de régie -----------------------------------------------
    notes_match = re.search(r"## Notes de régie\n(.*)$", raw, flags=re.S)
    if notes_match:
        add_page_break(doc)
        add_heading(doc, "Notes de régie", level=1, size=15, color=GOLD)
        for line in notes_match.group(1).strip().split("\n- "):
            line = line.strip().lstrip("-").strip()
            if not line:
                continue
            add_para(doc, "• " + line.replace("**", ""), size=11)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()
