#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera los 4 CV ATS y la 5ª variante híbrida a partir de cv_data.json.

Uso:
    python build_cvs.py

Salida (en la carpeta de este script):
    CV_Ethan_Moreno_Soporte_IT.pdf
    CV_Ethan_Moreno_Frontend.pdf
    CV_Ethan_Moreno_DotNet.pdf
    CV_Ethan_Moreno_General.pdf
    CV_Ethan_Moreno_Hibrido.pdf
    preview/<nombre>.png

Requisitos ya disponibles en el entorno: reportlab 5.1.0, PyMuPDF.
Los 4 ATS: una sola columna, fuentes Helvetica estándar, sin foto, sin
tablas, A4 y una página. El híbrido añade la foto y usa Helvetica con
paleta violeta, sin tablas ni dos columnas. Cuerpo >= 9,5 pt en todos.
"""

import io
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, PageTemplate, Paragraph, SimpleDocTemplate, Spacer,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATA_PATH = os.path.join(HERE, "cv_data.json")
PREVIEW_DIR = os.path.join(HERE, "preview")

BODY_PT = 10.0
# Interlineado ampliado de 12.3 a 14.0 pt: sigue cabiendo en 1 pagina A4
# en las 4 variantes (verificado con PyMuPDF el 26/11/2026).
BODY_LEAD = 14.0
MIN_PT = 9.5

HEADINGS = [
    "PERFIL",
    "COMPETENCIAS TÉCNICAS",
    "EXPERIENCIA PRÁCTICA",
    "PROYECTOS DESTACADOS",
    "FORMACIÓN",
    "CERTIFICACIONES",
    "IDIOMAS",
]

OLD_EMAIL = "ethanmogolock"
NEW_EMAIL = "ethan.moreno.dev@gmail.com"

# --- 5ª variante: híbrido con foto (mismo texto literal que "general") ------
HIBRIDO_NAME = "CV_Ethan_Moreno_Hibrido.pdf"
HIBRIDO_PHOTO = os.path.join(PARENT, "assets", "ethan.jpg")
HIBRIDO_INK = HexColor("#16121e")
HIBRIDO_SECONDARY = HexColor("#4a4557")
HIBRIDO_VIOLET = HexColor("#6a4c9c")
HIBRIDO_LIGHT = HexColor("#c4a9ff")
H_LEFT = 16 * mm
H_RIGHT = 16 * mm
H_TOP = 14 * mm
H_BOTTOM = 13 * mm
H_HEADER_W = 132 * mm          # ~74 % del ancho útil, a la izquierda de la foto
H_PHOTO_SIDE = 28 * mm
H_GAP = 5 * mm
H_BODY_TOP = H_TOP + H_PHOTO_SIDE + H_GAP

# Salida byte-a-byte reproducible (sin marcas de fecha hora en el PDF).
rl_config.invariant = 1


def styles():
    base = getSampleStyleSheet()["Normal"]
    base.fontName = "Helvetica"
    base.alignment = TA_LEFT
    base.textColor = "#000000"
    return {
        "name": ParagraphStyle(
            "name", parent=base, fontName="Helvetica-Bold", fontSize=16,
            leading=18, spaceAfter=1,
        ),
        "title": ParagraphStyle(
            "title", parent=base, fontName="Helvetica-Bold", fontSize=10.5,
            leading=13, spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "contact", parent=base, fontSize=9.6, leading=11.8, spaceAfter=0,
        ),
        "heading": ParagraphStyle(
            "heading", parent=base, fontName="Helvetica-Bold", fontSize=10.5,
            leading=12.5, spaceBefore=7, spaceAfter=2.5,
        ),
        "body": ParagraphStyle(
            "body", parent=base, fontSize=BODY_PT, leading=BODY_LEAD,
            spaceAfter=2.5,
        ),
        "item": ParagraphStyle(
            "item", parent=base, fontSize=BODY_PT, leading=BODY_LEAD,
            spaceAfter=3.5,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base, fontSize=9.6, leading=11.8,
            spaceBefore=6, spaceAfter=0,
        ),
    }


def labeled(text):
    """Pone en negrita la etiqueta antes de los dos puntos, sin alterar el texto."""
    safe = escape(text)
    pos = safe.find(": ")
    if pos == -1:
        return safe
    return "<b>%s</b>%s" % (safe[: pos + 1], safe[pos + 1 :])


def item(label, text, st):
    return Paragraph(
        "<b>%s</b><br/>%s" % (escape(label), escape(text)), st["item"]
    )


def build_story(data, variant_key, st):
    variant = data["variants"][variant_key]
    story = []

    # El nombre es el primer flowable: garantiza que el ATS lo extraiga primero.
    story.append(Paragraph(escape(data["name"]), st["name"]))

    title = data["titles"][variant["title_key"]]
    story.append(Paragraph(escape(title), st["title"]))
    story.append(
        Paragraph("<br/>".join(escape(line) for line in data["contact_lines"]), st["contact"])
    )

    story.append(Paragraph("PERFIL", st["heading"]))
    story.append(Paragraph(escape(data["profiles"][variant["profile_key"]]), st["body"]))

    story.append(Paragraph("COMPETENCIAS TÉCNICAS", st["heading"]))
    for key in variant["skills_order"]:
        story.append(Paragraph(labeled(data["skills"][key]), st["body"]))

    story.append(Paragraph("EXPERIENCIA PRÁCTICA", st["heading"]))
    for entry in data["experience"]:
        story.append(item(entry["label"], entry["text"], st))

    story.append(Paragraph("PROYECTOS DESTACADOS", st["heading"]))
    for entry in data["projects"]:
        story.append(item(entry["label"], entry["text"], st))

    story.append(Paragraph("FORMACIÓN", st["heading"]))
    for line in data["education"]:
        story.append(Paragraph(escape(line), st["body"]))

    story.append(Paragraph("CERTIFICACIONES", st["heading"]))
    for line in data["certifications"]:
        story.append(Paragraph(escape(line), st["body"]))

    story.append(Paragraph("IDIOMAS", st["heading"]))
    story.append(Paragraph(escape(data["languages"]), st["body"]))

    story.append(Spacer(1, 1))
    story.append(Paragraph(escape(data["footer"]), st["footer"]))
    return story


def generate(data, variant_key):
    out_path = os.path.join(HERE, data["variants"][variant_key]["output"])
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=13 * mm,
        title=data["titles"][data["variants"][variant_key]["title_key"]],
        author=data["name"],
        subject="CV ATS",
    )
    doc.build(build_story(data, variant_key, styles()))
    return out_path


def verify_and_preview(pdf_path):
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    try:
        text = doc[0].get_text()  # sin sort=True: orden real de extracción
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        sizes = []
        for block in doc[0].get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    sizes.append(span["size"])
        result = {
            "file": os.path.basename(pdf_path),
            "pages": doc.page_count,
            "a4": (round(doc[0].rect.width, 1), round(doc[0].rect.height, 1)),
            "first_line": lines[0] if lines else "",
            "email_count": text.count(NEW_EMAIL),
            "old_email_count": text.count(OLD_EMAIL),
            "headings": [h for h in HEADINGS if h not in text],
            "min_font_pt": round(min(sizes), 2) if sizes else None,
        }
        if result["pages"] != 1:
            raise RuntimeError("%s: esperaba 1 página, tiene %d" % (pdf_path, result["pages"]))
        if not result["first_line"].startswith("ETHAN MORENO"):
            raise RuntimeError("%s: primera línea inesperada: %r" % (pdf_path, result["first_line"]))
        if result["email_count"] != 1 or result["old_email_count"] != 0:
            raise RuntimeError("%s: correo incorrecto" % pdf_path)
        if result["headings"]:
            raise RuntimeError("%s: faltan encabezados %s" % (pdf_path, result["headings"]))
        if result["min_font_pt"] is not None and result["min_font_pt"] < MIN_PT - 0.01:
            raise RuntimeError("%s: cuerpo por debajo de %s pt" % (pdf_path, MIN_PT))

        os.makedirs(PREVIEW_DIR, exist_ok=True)
        png = os.path.join(
            PREVIEW_DIR, os.path.splitext(os.path.basename(pdf_path))[0] + ".png"
        )
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
        pix.save(png)
        result["preview"] = png
        return result
    finally:
        doc.close()


class HybridRule(Flowable):
    """Regla fina de acento claro; no es una tabla ni una segunda columna."""

    def __init__(self, width):
        Flowable.__init__(self)
        self.width = width
        self.height = 2.5

    def draw(self):
        self.canv.setFillColor(HIBRIDO_LIGHT)
        self.canv.rect(0, 0, self.width, 2.5, stroke=0, fill=1)


def hibrido_styles():
    base = getSampleStyleSheet()["Normal"]
    base.fontName = "Helvetica"
    base.alignment = TA_LEFT
    base.textColor = HIBRIDO_INK
    return {
        "heading": ParagraphStyle(
            "h-heading", parent=base, fontName="Helvetica-Bold", fontSize=12,
            leading=14, textColor=HIBRIDO_VIOLET, spaceBefore=5, spaceAfter=1,
        ),
        "body": ParagraphStyle(
            "h-body", parent=base, fontSize=10.5, leading=13.2, spaceAfter=1.5,
        ),
        "item": ParagraphStyle(
            "h-item", parent=base, fontSize=10.5, leading=13.2, spaceAfter=2.5,
        ),
        "footer": ParagraphStyle(
            "h-footer", parent=base, fontSize=10, leading=12.5,
            spaceBefore=4, spaceAfter=0,
        ),
    }


def hibrido_story(data, st, width):
    """Mismos 7 encabezados y textos literales de la variante general."""
    general = data["variants"]["general"]
    story = []
    for heading in HEADINGS:
        story.append(Paragraph(heading, st["heading"]))
        story.append(HybridRule(width))
        if heading == "PERFIL":
            story.append(Paragraph(escape(data["profiles"][general["profile_key"]]), st["body"]))
        elif heading == "COMPETENCIAS TÉCNICAS":
            for key in general["skills_order"]:
                story.append(Paragraph(labeled(data["skills"][key]), st["body"]))
        elif heading == "EXPERIENCIA PRÁCTICA":
            for entry in data["experience"]:
                story.append(item(entry["label"], entry["text"], st))
        elif heading == "PROYECTOS DESTACADOS":
            for entry in data["projects"]:
                story.append(item(entry["label"], entry["text"], st))
        elif heading == "FORMACIÓN":
            for line in data["education"]:
                story.append(Paragraph(escape(line), st["body"]))
        elif heading == "CERTIFICACIONES":
            for line in data["certifications"]:
                story.append(Paragraph(escape(line), st["body"]))
        elif heading == "IDIOMAS":
            story.append(Paragraph(escape(data["languages"]), st["body"]))
    story.append(Spacer(1, 1))
    story.append(Paragraph(escape(data["footer"]), st["footer"]))
    return story


def hibrido_photo():
    """Recorta el retrato a 1:1 con PyMuPDF (sin dependencias nuevas)."""
    import pymupdf as fitz
    if not os.path.isfile(HIBRIDO_PHOTO):
        raise RuntimeError("falta la foto: %s" % HIBRIDO_PHOTO)
    doc = fitz.open(HIBRIDO_PHOTO)
    try:
        page = doc[0]
        side = min(page.rect.width, page.rect.height)
        top = (page.rect.height - side) / 2 - 40  # ligero ajuste hacia el rostro
        top = max(0.0, min(top, page.rect.height - side))
        pix = page.get_pixmap(clip=fitz.Rect(0, top, side, top + side), alpha=False)
        return ImageReader(io.BytesIO(pix.tobytes("png")))
    finally:
        doc.close()


def generate_hibrido(data):
    out_path = os.path.join(HERE, HIBRIDO_NAME)
    width, height = A4
    photo_x = width - H_RIGHT - H_PHOTO_SIDE
    photo_y = height - H_TOP - H_PHOTO_SIDE
    reader = hibrido_photo()

    def on_page(canv, doc):
        canv.saveState()
        # La foto va arriba a la derecha; el texto de cabecera ocupa el 74 % izq.
        canv.drawImage(reader, photo_x, photo_y, H_PHOTO_SIDE, H_PHOTO_SIDE,
                       preserveAspectRatio=True, anchor="c", mask="auto")
        canv.setFillColor(HIBRIDO_LIGHT)
        canv.rect(H_LEFT, photo_y - 2 * mm, H_HEADER_W, 2.5, stroke=0, fill=1)

        canv.setFillColor(HIBRIDO_INK)
        canv.setFont("Helvetica-Bold", 23)
        y = height - H_TOP - 23
        canv.drawString(H_LEFT, y, data["name"])
        canv.setFillColor(HIBRIDO_VIOLET)
        canv.setFont("Helvetica", 10.5)
        canv.drawString(H_LEFT, y - 16, data["titles"][data["variants"]["general"]["title_key"]])
        # Contacto en el cuerpo real de la página (no en encabezado/pie del PDF).
        canv.setFillColor(HIBRIDO_SECONDARY)
        canv.setFont("Helvetica", 9.6)
        yy = y - 32
        for line in data["contact_lines"]:
            canv.drawString(H_LEFT, yy, line)
            yy -= 13
        canv.restoreState()

    doc = BaseDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=H_LEFT,
        rightMargin=H_RIGHT,
        topMargin=H_BODY_TOP,
        bottomMargin=H_BOTTOM,
        title=data["titles"][data["variants"]["general"]["title_key"]],
        author=data["name"],
        subject="CV híbrido con foto",
    )
    frame = Frame(
        H_LEFT, H_BOTTOM, width - H_LEFT - H_RIGHT, height - H_BOTTOM - H_BODY_TOP,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cuerpo",
    )
    doc.addPageTemplates(PageTemplate(id="hibrido", frames=[frame], onPage=on_page))
    doc.build(hibrido_story(data, hibrido_styles(), width - H_LEFT - H_RIGHT))
    return out_path


def verify_hibrido(pdf_path):
    import pymupdf as fitz

    doc = fitz.open(pdf_path)
    try:
        page = doc[0]
        text = page.get_text()  # sin sort=True
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        info = page.get_text("dict")
        spans = [sp for b in info["blocks"] for ln in b.get("lines", []) for sp in ln["spans"]]
        sizes = [sp["size"] for sp in spans]
        column_x = {
            round(min(sp["bbox"][0] for sp in ln["spans"]), 1)
            for b in info["blocks"] for ln in b.get("lines", [])
        }
        rects = [r for img in page.get_images(full=True) for r in page.get_image_rects(img[0])]
        result = {
            "file": os.path.basename(pdf_path),
            "pages": doc.page_count,
            "a4": (round(page.rect.width, 1), round(page.rect.height, 1)),
            "first_line": lines[0] if lines else "",
            "email_line3": lines[2] if len(lines) > 2 else "",
            "email_count": text.count(NEW_EMAIL),
            "old_email_count": text.count(OLD_EMAIL),
            "columns": len(column_x),
            "min_font_pt": round(min(sizes), 2) if sizes else None,
            "images": len(page.get_images(full=True)),
            "image_top_right": all(r.x0 > page.rect.width / 2 and r.y1 < page.rect.height / 3
                                   for r in rects) and len(rects) == 1,
            "tables": len(page.find_tables().tables),
            "missing_headings": [h for h in HEADINGS if text.count(h) != 1],
        }
        if result["pages"] != 1:
            raise RuntimeError("%s: esperaba 1 página, tiene %d" % (pdf_path, result["pages"]))
        if not result["first_line"].startswith("ETHAN MORENO"):
            raise RuntimeError("%s: primera línea inesperada: %r" % (pdf_path, result["first_line"]))
        if NEW_EMAIL not in result["email_line3"]:
            raise RuntimeError("%s: el correo no está en la línea 3" % pdf_path)
        if result["email_count"] != 1 or result["old_email_count"] != 0:
            raise RuntimeError("%s: correo incorrecto" % pdf_path)
        if result["columns"] != 1:
            raise RuntimeError("%s: se detectaron %d columnas de texto" % (pdf_path, result["columns"]))
        if result["min_font_pt"] is None or result["min_font_pt"] < MIN_PT - 0.01:
            raise RuntimeError("%s: fuente por debajo de %s pt" % (pdf_path, MIN_PT))
        if not result["image_top_right"]:
            raise RuntimeError("%s: la foto no está arriba a la derecha" % pdf_path)
        if result["tables"] != 0:
            raise RuntimeError("%s: hay tablas" % pdf_path)
        if result["missing_headings"]:
            raise RuntimeError("%s: faltan encabezados %s" % (pdf_path, result["missing_headings"]))

        os.makedirs(PREVIEW_DIR, exist_ok=True)
        png = os.path.join(PREVIEW_DIR, os.path.splitext(HIBRIDO_NAME)[0] + ".png")
        pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72), alpha=False)
        pix.save(png)
        result["preview"] = png
        return result
    finally:
        doc.close()


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for variant_key in data["variants"]:
        pdf = generate(data, variant_key)
        result = verify_and_preview(pdf)
        print(
            "%(file)s | páginas=%(pages)d | A4=%(a4)s | primera=%(first_line)r | "
            "email=%(email_count)d | antiguo=%(old_email_count)d | "
            "min=%(min_font_pt)s pt | preview=%(preview)s" % result
        )
    hibrido = verify_hibrido(generate_hibrido(data))
    print(
        "%(file)s | páginas=%(pages)d | A4=%(a4)s | primera=%(first_line)r | "
        "línea3=%(email_line3)r | email=%(email_count)d | antiguo=%(old_email_count)d | "
        "columnas=%(columns)d | min=%(min_font_pt)s pt | imgs=%(images)d | "
        "tablas=%(tables)d | 7 encabezados=%(headings_ok)s | preview=%(preview)s"
        % dict(hibrido, headings_ok=(not hibrido["missing_headings"]))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
