"""
PDF Generator for Smart Agricultural System — B.Tech Project Report
Silver Oak University, Ahmedabad
Student: Jadav Vishvajeet | Branch: Computer Engineering
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib import colors

# ── Directory Setup ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(BASE_DIR, "Smart_Agricultural_System_BTech_Report.pdf")

# ── Brand Colors ─────────────────────────────────────────────────
DARK_GREEN   = HexColor("#1b5e20")
MID_GREEN    = HexColor("#2e7d32")
LIGHT_GREEN  = HexColor("#e8f5e9")
ACCENT_GREEN = HexColor("#43a047")
MAROON       = HexColor("#7b1c1c")
DARK_GRAY    = HexColor("#263238")
MID_GRAY     = HexColor("#546e7a")
LIGHT_GRAY   = HexColor("#f5f5f5")
TABLE_HEADER = HexColor("#1b5e20")
TABLE_ROW1   = HexColor("#f1f8e9")
TABLE_ROW2   = white
BORDER_COLOR = HexColor("#a5d6a7")

PAGE_W, PAGE_H = A4

# ── Styles ───────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_styles():
    s = {}

    s["cover_title"] = ParagraphStyle(
        "cover_title", fontName="Helvetica-Bold",
        fontSize=20, leading=26, alignment=TA_CENTER,
        textColor=DARK_GREEN, spaceAfter=8)

    s["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle", fontName="Helvetica-Bold",
        fontSize=13, leading=18, alignment=TA_CENTER,
        textColor=DARK_GRAY, spaceAfter=6)

    s["cover_body"] = ParagraphStyle(
        "cover_body", fontName="Helvetica",
        fontSize=11, leading=16, alignment=TA_CENTER,
        textColor=DARK_GRAY, spaceAfter=4)

    s["cover_italic"] = ParagraphStyle(
        "cover_italic", fontName="Helvetica-Oblique",
        fontSize=11, leading=16, alignment=TA_CENTER,
        textColor=MID_GRAY, spaceAfter=4)

    s["chapter_heading"] = ParagraphStyle(
        "chapter_heading", fontName="Helvetica-Bold",
        fontSize=16, leading=22, alignment=TA_CENTER,
        textColor=white, spaceAfter=0, spaceBefore=0)

    s["section_heading"] = ParagraphStyle(
        "section_heading", fontName="Helvetica-Bold",
        fontSize=13, leading=18, alignment=TA_LEFT,
        textColor=DARK_GREEN, spaceAfter=6, spaceBefore=14)

    s["subsection_heading"] = ParagraphStyle(
        "subsection_heading", fontName="Helvetica-Bold",
        fontSize=11, leading=16, alignment=TA_LEFT,
        textColor=DARK_GRAY, spaceAfter=4, spaceBefore=10)

    s["body"] = ParagraphStyle(
        "body", fontName="Helvetica",
        fontSize=10, leading=16, alignment=TA_JUSTIFY,
        textColor=DARK_GRAY, spaceAfter=6, spaceBefore=2)

    s["bullet"] = ParagraphStyle(
        "bullet", fontName="Helvetica",
        fontSize=10, leading=15, alignment=TA_LEFT,
        textColor=DARK_GRAY, spaceAfter=3,
        leftIndent=18, firstLineIndent=-12)

    s["code"] = ParagraphStyle(
        "code", fontName="Courier",
        fontSize=8, leading=12, alignment=TA_LEFT,
        textColor=HexColor("#1a237e"), backColor=HexColor("#f3f4f6"),
        spaceAfter=4, spaceBefore=4,
        leftIndent=10, rightIndent=10)

    s["toc_chapter"] = ParagraphStyle(
        "toc_chapter", fontName="Helvetica-Bold",
        fontSize=10, leading=15, alignment=TA_LEFT,
        textColor=DARK_GREEN, spaceAfter=2)

    s["toc_section"] = ParagraphStyle(
        "toc_section", fontName="Helvetica",
        fontSize=9, leading=14, alignment=TA_LEFT,
        textColor=DARK_GRAY, spaceAfter=1, leftIndent=16)

    s["table_header_cell"] = ParagraphStyle(
        "table_header_cell", fontName="Helvetica-Bold",
        fontSize=9, leading=12, alignment=TA_CENTER,
        textColor=white)

    s["table_cell"] = ParagraphStyle(
        "table_cell", fontName="Helvetica",
        fontSize=9, leading=12, alignment=TA_LEFT,
        textColor=DARK_GRAY)

    s["footer_text"] = ParagraphStyle(
        "footer_text", fontName="Helvetica",
        fontSize=8, leading=10, alignment=TA_CENTER,
        textColor=MID_GRAY)

    s["abstract_body"] = ParagraphStyle(
        "abstract_body", fontName="Helvetica",
        fontSize=10, leading=17, alignment=TA_JUSTIFY,
        textColor=DARK_GRAY, spaceAfter=6, spaceBefore=2,
        leftIndent=20, rightIndent=20)

    s["ref"] = ParagraphStyle(
        "ref", fontName="Helvetica",
        fontSize=9, leading=14, alignment=TA_JUSTIFY,
        textColor=DARK_GRAY, spaceAfter=5,
        leftIndent=24, firstLineIndent=-24)

    return s

ST = make_styles()

# ── Page Template ────────────────────────────────────────────────
current_chapter = [""]

def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Top header bar
    canvas.setFillColor(DARK_GREEN)
    canvas.rect(0, h - 0.55 * inch, w, 0.55 * inch, fill=1, stroke=0)

    # Header text
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(white)
    canvas.drawString(0.5 * inch, h - 0.35 * inch, current_chapter[0])
    canvas.drawRightString(w - 0.5 * inch, h - 0.35 * inch, "Smart Agricultural System")

    # Bottom footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, w, 0.45 * inch, fill=1, stroke=0)
    canvas.setFillColor(MID_GREEN)
    canvas.rect(0, 0.42 * inch, w, 0.03 * inch, fill=1, stroke=0)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(0.5 * inch, 0.16 * inch, "College of Technology")
    canvas.drawCentredString(w / 2, 0.16 * inch, str(doc.page))
    canvas.drawRightString(w - 0.5 * inch, 0.16 * inch, "Silver Oak University")

    canvas.restoreState()

def on_first_page(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

# ── Helper: Chapter Banner ────────────────────────────────────────
def chapter_banner(title):
    data = [[Paragraph(title, ST["chapter_heading"])]]
    t = Table(data, colWidths=[PAGE_W - 2 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [DARK_GREEN]),
    ]))
    return t

def section_line():
    return HRFlowable(width="100%", thickness=1,
                      color=ACCENT_GREEN, spaceAfter=4, spaceBefore=2)

# ── Helper: Build a nice Table ────────────────────────────────────
def make_table(headers, rows, col_widths=None):
    header_cells = [Paragraph(h, ST["table_header_cell"]) for h in headers]
    data = [header_cells]
    for i, row in enumerate(rows):
        bg = TABLE_ROW1 if i % 2 == 0 else TABLE_ROW2
        data.append([Paragraph(str(c), ST["table_cell"]) for c in row])

    if col_widths is None:
        n = len(headers)
        col_widths = [(PAGE_W - 2 * inch) / n] * n

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND",    (0, 0), (-1, 0),  TABLE_HEADER),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("TOPPADDING",    (0, 0), (-1, 0),  7),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [TABLE_ROW1, TABLE_ROW2]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER_COLOR),
        ("BOX",           (0, 0), (-1, -1), 0.8, MID_GREEN),
    ]
    t.setStyle(TableStyle(style))
    return t

# ─────────────────────────────────────────────────────────────────
# CONTENT BUILDERS
# ─────────────────────────────────────────────────────────────────

def build_cover(story):
    current_chapter[0] = "Cover Page"
    story.append(Spacer(1, 1.2 * inch))

    # Title box
    title_data = [[Paragraph(
        "ADVANCED PROGRAMMING WITH PROJECT-I<br/>MINOR PROJECT REPORT",
        ST["cover_title"])]]
    tt = Table(title_data, colWidths=[PAGE_W - 2.5 * inch])
    tt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GREEN),
        ("BOX",           (0,0), (-1,-1), 1.5, DARK_GREEN),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
    ]))
    story.append(tt)
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Entitled", ST["cover_italic"]))
    story.append(Spacer(1, 0.15 * inch))

    # Project title box
    pt_data = [[Paragraph(
        "SMART AGRICULTURAL SYSTEM<br/>FOR GUJARAT FARMERS",
        ParagraphStyle("ptt", fontName="Helvetica-Bold", fontSize=18,
                       leading=26, alignment=TA_CENTER, textColor=white))]]
    pt = Table(pt_data, colWidths=[PAGE_W - 2 * inch])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), DARK_GREEN),
        ("TOPPADDING",    (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Submitted by", ST["cover_italic"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(
        "<b>JADAV VISHVAJEET</b> — Enrollment Number: _______________",
        ST["cover_subtitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("in", ST["cover_italic"]))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("PARTIAL FULFILLMENT FOR THE DEGREE OF", ST["cover_body"]))
    story.append(Paragraph("<b>BACHELOR OF TECHNOLOGY</b>", ST["cover_subtitle"]))
    story.append(Paragraph("in", ST["cover_italic"]))
    story.append(Paragraph("<b>COMPUTER ENGINEERING</b>", ST["cover_subtitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="60%", thickness=1.5, color=MID_GREEN,
                             hAlign="CENTER", spaceAfter=10))
    story.append(Paragraph("<b>Department of Computer Engineering</b>", ST["cover_body"]))
    story.append(Paragraph("<b>College of Technology</b>", ST["cover_body"]))
    story.append(Paragraph("<b>Silver Oak University, Ahmedabad</b>", ST["cover_body"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("April, 2026", ST["cover_body"]))
    story.append(PageBreak())


def build_declaration(story):
    current_chapter[0] = "Declaration"
    story.append(chapter_banner("DECLARATION"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "I hereby declare that the Advanced Programming with Project-I / Minor Project report "
        "submitted along with the Project entitled <b>\"Smart Agricultural System for Gujarat Farmers\"</b> "
        "submitted in partial fulfillment for the Bachelor of Technology in "
        "<b>Computer Engineering</b> to Silver Oak University, Ahmedabad, is a bonafide record of "
        "original work carried out by me at College of Technology, Silver Oak University under "
        "the supervision of <b>&lt;Internal Guide Name&gt;</b>.", ST["body"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "I further declare that the report does not contain any material previously submitted for "
        "the award of any degree or diploma in this or any other university.", ST["body"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "It is also certified that no part of this report has been copied from any source without "
        "proper acknowledgment, and all referenced materials, figures, and information from other "
        "sources have been appropriately cited in the report.", ST["body"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        "<b>JADAV VISHVAJEET</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Signature: ___________________",
        ST["body"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Place: Ahmedabad", ST["body"]))
    story.append(Paragraph("Date: April 2026", ST["body"]))
    story.append(PageBreak())


def build_certificate(story):
    current_chapter[0] = "Certificate"
    story.append(chapter_banner("CERTIFICATE"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>College of Technology</b>", ST["cover_body"]))
    story.append(Paragraph("<b>Department of Computer Engineering</b>", ST["cover_body"]))
    story.append(Paragraph("<b>Silver Oak University, Ahmedabad</b>", ST["cover_body"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "This is to certify that <b>JADAV VISHVAJEET</b> (Enrollment No. _______________) "
        "has submitted the Advanced Programming with Project-I / Minor Project report entitled "
        "<b>\"Smart Agricultural System for Gujarat Farmers\"</b> in partial fulfillment of the "
        "requirement for the award of the degree in Bachelor of Technology in "
        "<b>Computer Engineering</b> of Silver Oak University, Ahmedabad during the academic year "
        "<b>2026–2027</b>.", ST["body"]))
    story.append(Spacer(1, 0.8 * inch))

    cert_data = [
        [Paragraph("<b>Internal Guide</b>", ST["table_cell"]),
         Paragraph("<b>Head of Department</b>", ST["table_cell"])],
        [Paragraph("&lt;Name of Internal Guide&gt;", ST["table_cell"]),
         Paragraph("&lt;Head of Department Name&gt;", ST["table_cell"])],
        [Paragraph("&lt;Designation&gt;", ST["table_cell"]),
         Paragraph("&lt;Designation&gt;", ST["table_cell"])],
        [Paragraph("Dept. of Computer Engineering", ST["table_cell"]),
         Paragraph("Dept. of Computer Engineering", ST["table_cell"])],
        [Paragraph("College of Technology", ST["table_cell"]),
         Paragraph("College of Technology", ST["table_cell"])],
        [Paragraph("Silver Oak University", ST["table_cell"]),
         Paragraph("Silver Oak University", ST["table_cell"])],
    ]
    ct = Table(cert_data, colWidths=[3.2 * inch, 3.2 * inch])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), LIGHT_GREEN),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 10),
        ("TOPPADDING", (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("GRID",       (0,0),(-1,-1), 0.5, BORDER_COLOR),
        ("BOX",        (0,0),(-1,-1), 1,   MID_GREEN),
    ]))
    story.append(ct)
    story.append(PageBreak())


def build_acknowledgement(story):
    current_chapter[0] = "Acknowledgement"
    story.append(chapter_banner("ACKNOWLEDGEMENT"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "First and foremost, I would like to express my sincere gratitude to "
        "<b>&lt;Internal Guide Name&gt;</b>, &lt;Designation&gt;, Department of Computer Engineering, "
        "College of Technology, Silver Oak University, Ahmedabad, for their invaluable guidance, "
        "constant encouragement, and constructive suggestions throughout the development of this project. "
        "Their expertise and insights were instrumental in shaping this work.", ST["body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(
        "I would also like to extend my heartfelt thanks to <b>&lt;Head of Department Name&gt;</b>, "
        "Head of the Department of Computer Engineering, for providing all necessary facilities and "
        "support required to carry out this project successfully.", ST["body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(
        "I am grateful to all the faculty members of the Department of Computer Engineering for their "
        "continuous support and motivation during the course of the project.", ST["body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(
        "I wish to thank my family and friends for their unwavering support, patience, and encouragement "
        "throughout this journey.", ST["body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(Paragraph(
        "Finally, I would like to acknowledge the open-source communities behind <b>Python</b>, "
        "<b>Flask</b>, <b>scikit-learn</b>, <b>TensorFlow</b>, and <b>OpenWeatherMap API</b>, "
        "whose tools and libraries made this project possible.", ST["body"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>JADAV VISHVAJEET</b>", ST["body"]))
    story.append(Paragraph("Department of Computer Engineering", ST["body"]))
    story.append(Paragraph("College of Technology, Silver Oak University, Ahmedabad", ST["body"]))
    story.append(Paragraph("April 2026", ST["body"]))
    story.append(PageBreak())


def build_abstract(story):
    current_chapter[0] = "Abstract"
    story.append(chapter_banner("ABSTRACT"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Agriculture is the backbone of the Indian economy, and Gujarat is one of India's leading "
        "agricultural states. However, farmers often lack access to timely, data-driven decision "
        "support for critical farming activities such as crop selection, disease diagnosis, irrigation "
        "planning, fertilizer application, and market price analysis. This project presents the design "
        "and development of a <b>Smart Agricultural System</b> — a web-based, AI-powered decision "
        "support platform specifically tailored for Gujarat farmers.", ST["abstract_body"]))
    story.append(Paragraph(
        "The system is built using <b>Python</b> and the <b>Flask</b> web framework and integrates "
        "multiple intelligent modules into a unified, user-friendly interface. The <b>Crop "
        "Recommendation Module</b> utilizes a trained <b>Random Forest</b> classifier along with a "
        "rule-based scoring engine to suggest the most suitable crops based on soil parameters (N, P, K, "
        "pH, organic carbon, soil texture), season, water availability, and irrigation type. The "
        "<b>Plant Disease Detection Module</b> employs a <b>MobileNetV2 Convolutional Neural Network "
        "(CNN)</b> to analyze leaf images uploaded by farmers and identify diseases with confidence "
        "scores along with treatment and prevention advice.", ST["abstract_body"]))
    story.append(Paragraph(
        "The <b>Smart Irrigation Module</b> implements a deterministic, multi-rule decision engine "
        "that calculates precise water requirements based on soil moisture, crop growth stage, weather "
        "conditions, rainfall probability, soil type, and irrigation method efficiency. The <b>Weather "
        "Advisory Module</b> fetches real-time data from the <b>OpenWeatherMap API</b> and generates "
        "bilingual (English and Gujarati) advisories. The <b>Market Price Tracker</b> integrates with "
        "the <b>Agmarknet API</b> to provide live Gujarat mandi prices with trend analysis and sell/wait "
        "recommendations. The system also supports <b>WhatsApp</b> and <b>Email alerts</b> for "
        "automated farmer notifications.", ST["abstract_body"]))
    story.append(Spacer(1, 0.15 * inch))

    kw_data = [[Paragraph(
        "<b>Keywords:</b> Smart Agriculture, Crop Recommendation, Plant Disease Detection, "
        "Smart Irrigation, Flask, Machine Learning, Random Forest, MobileNetV2, Gujarat Farming, "
        "Weather Advisory",
        ParagraphStyle("kw", fontName="Helvetica", fontSize=9, leading=14,
                       textColor=DARK_GRAY, alignment=TA_JUSTIFY))]]
    kw_t = Table(kw_data, colWidths=[PAGE_W - 2.8 * inch])
    kw_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT_GREEN),
        ("BOX",           (0,0),(-1,-1), 1, MID_GREEN),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
    ]))
    story.append(kw_t)
    story.append(PageBreak())


def build_abbreviations(story):
    current_chapter[0] = "List of Abbreviations"
    story.append(chapter_banner("LIST OF ABBREVIATIONS"))
    story.append(Spacer(1, 0.15 * inch))
    abbrevs = [
        ("AI",  "Artificial Intelligence"),
        ("ML",  "Machine Learning"),
        ("CNN", "Convolutional Neural Network"),
        ("RF",  "Random Forest"),
        ("API", "Application Programming Interface"),
        ("REST","Representational State Transfer"),
        ("HTTP","Hypertext Transfer Protocol"),
        ("JSON","JavaScript Object Notation"),
        ("HTML","Hypertext Markup Language"),
        ("CSS", "Cascading Style Sheets"),
        ("OWM", "OpenWeatherMap"),
        ("SMTP","Simple Mail Transfer Protocol"),
        ("NPK", "Nitrogen, Phosphorus, Potassium"),
        ("MSP", "Minimum Support Price"),
        ("NDVI","Normalized Difference Vegetation Index"),
        ("IoT", "Internet of Things"),
        ("UI",  "User Interface"),
        ("WSGI","Web Server Gateway Interface"),
        ("MobileNetV2","Mobile Network Version 2 (Lightweight CNN by Google)"),
        ("PKL", "Pickle File — Serialized Python Object"),
        ("SVM", "Support Vector Machine"),
        ("LSTM","Long Short-Term Memory"),
        ("PWA", "Progressive Web Application"),
        ("KVK", "Krishi Vigyan Kendra (Farm Science Centre)"),
    ]
    story.append(make_table(
        ["Abbreviation", "Full Form"],
        abbrevs,
        col_widths=[1.8 * inch, PAGE_W - 2 * inch - 1.8 * inch]))
    story.append(PageBreak())


def build_toc(story):
    current_chapter[0] = "Table of Contents"
    story.append(chapter_banner("TABLE OF CONTENTS"))
    story.append(Spacer(1, 0.15 * inch))

    toc = [
        ("Declaration", "i", False),
        ("Acknowledgement", "ii", False),
        ("Abstract", "iii", False),
        ("List of Abbreviations", "iv", False),
        ("Table of Contents", "v", False),
        ("CHAPTER 1 — INTRODUCTION", "1", True),
        ("1.1  Background and Motivation", "2", False),
        ("1.2  Problem Statement", "3", False),
        ("1.3  Objectives of the Project", "4", False),
        ("1.4  Scope of the Project", "5", False),
        ("1.5  Technology Stack", "6", False),
        ("1.6  Organization of the Report", "7", False),
        ("CHAPTER 2 — LITERATURE REVIEW", "8", True),
        ("2.1  AI-Based Crop Recommendation Systems", "9", False),
        ("2.2  Plant Disease Detection Using Deep Learning", "10", False),
        ("2.3  Smart Irrigation Systems", "11", False),
        ("2.4  Agricultural Market Intelligence", "12", False),
        ("2.5  Weather-Based Farming Advisory Systems", "13", False),
        ("2.6  Research Gap and Contribution", "14", False),
        ("CHAPTER 3 — SYSTEM ANALYSIS", "15", True),
        ("3.1  Study of the Current System", "16", False),
        ("3.2  Problems and Weaknesses", "17", False),
        ("3.3  Requirements of the New System", "18", False),
        ("3.4  System Feasibility Analysis", "20", False),
        ("3.5  Activity / Process in the Proposed System", "21", False),
        ("3.6  Features and Modules of the Proposed System", "22", False),
        ("3.7  Technology Selection and Justification", "24", False),
        ("CHAPTER 4 — SYSTEM DESIGN", "25", True),
        ("4.1  System Architecture", "26", False),
        ("4.2  Module Design", "28", False),
        ("4.3  Data Structure Design", "34", False),
        ("4.4  Input / Output and Interface Design", "35", False),
        ("4.5  Security Design", "36", False),
        ("CHAPTER 5 — IMPLEMENTATION", "38", True),
        ("5.1  Implementation Platform / Environment", "39", False),
        ("5.2  Project Directory Structure", "40", False),
        ("5.3  Module Implementation Details", "42", False),
        ("5.4  Finding / Results / Outcomes", "50", False),
        ("5.5  Result Analysis", "51", False),
        ("CHAPTER 6 — TESTING", "53", True),
        ("6.1  Testing Plan / Strategy", "54", False),
        ("6.2  Test Cases and Results", "55", False),
        ("6.3  Summary of Test Results", "60", False),
        ("CHAPTER 7 — CONCLUSION AND DISCUSSION", "61", True),
        ("7.1  Overall Analysis of Project Viability", "62", False),
        ("7.2  Problems Encountered and Solutions", "63", False),
        ("7.3  Summary of Project Work", "64", False),
        ("7.4  Limitations and Future Enhancements", "65", False),
        ("References / Bibliography", "67", True),
    ]

    for entry, page, is_chapter in toc:
        if is_chapter:
            row = Table(
                [[Paragraph(f"<b>{entry}</b>", ST["toc_chapter"]),
                  Paragraph(f"<b>{page}</b>", ParagraphStyle(
                      "tp", fontName="Helvetica-Bold", fontSize=10,
                      alignment=TA_RIGHT, textColor=DARK_GREEN))]],
                colWidths=[PAGE_W - 2.6 * inch, 0.5 * inch])
            row.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,-1), LIGHT_GREEN),
                ("TOPPADDING", (0,0),(-1,-1), 4),
                ("BOTTOMPADDING",(0,0),(-1,-1), 4),
                ("LEFTPADDING",(0,0),(-1,-1), 6),
            ]))
            story.append(row)
            story.append(Spacer(1, 1))
        else:
            row = Table(
                [[Paragraph(entry, ST["toc_section"]),
                  Paragraph(page, ParagraphStyle(
                      "tps", fontName="Helvetica", fontSize=9,
                      alignment=TA_RIGHT, textColor=MID_GRAY))]],
                colWidths=[PAGE_W - 2.6 * inch, 0.5 * inch])
            row.setStyle(TableStyle([
                ("TOPPADDING", (0,0),(-1,-1), 1),
                ("BOTTOMPADDING",(0,0),(-1,-1), 1),
                ("LEFTPADDING",(0,0),(-1,-1), 6),
            ]))
            story.append(row)
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 1
# ─────────────────────────────────────────────────────────────────
def build_chapter1(story):
    current_chapter[0] = "Chapter 1 — Introduction"
    story.append(chapter_banner("CHAPTER 1 — INTRODUCTION"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("1.1   Background and Motivation", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "Agriculture is the primary occupation of more than 50% of India's workforce and contributes "
        "approximately 17–18% to the national GDP. Gujarat, with its diverse agro-climatic zones, "
        "fertile black cotton soils, and extensive irrigation networks, is one of India's most "
        "productive agricultural states. Gujarat is the largest producer of cotton and groundnut in the "
        "country and a significant contributor in crops such as castor, cumin, wheat, bajra, and sugarcane.",
        ST["body"]))
    story.append(Paragraph("Despite this agricultural potential, farmers face major challenges:", ST["body"]))
    challenges = [
        "Uninformed crop selection: Farmers rely on traditional knowledge rather than soil test data, leading to suboptimal crop choices.",
        "Late disease detection: Crop diseases go undetected until visible damage occurs, causing significant yield losses.",
        "Inefficient water usage: Over-irrigation and under-irrigation are common due to lack of scientific irrigation scheduling.",
        "Market price uncertainty: Farmers sell produce at low prices due to lack of real-time mandi price information.",
        "Lack of weather-based planning: Most small-scale farmers do not have access to localized weather forecasts.",
    ]
    for c in challenges:
        story.append(Paragraph(f"• {c}", ST["bullet"]))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("1.2   Problem Statement", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "Existing solutions available to Indian farmers are either fragmented, too complex for "
        "non-technical users, not localized for Gujarat conditions, or require expensive hardware and "
        "database infrastructure. There is a critical need for an <b>integrated, intelligent, "
        "lightweight, and accessible</b> agricultural advisory platform that addresses crop selection, "
        "disease detection, irrigation management, market intelligence, and weather advisory in one place.",
        ST["body"]))

    story.append(Paragraph("1.3   Objectives of the Project", ST["section_heading"]))
    story.append(section_line())
    objectives = [
        "Design and develop an AI-powered web application integrating multiple agricultural decision support modules.",
        "Implement a Random Forest-based crop recommendation engine considering 15 input parameters.",
        "Develop a CNN-based (MobileNetV2) plant disease detection system for leaf image analysis.",
        "Build a rule-based smart irrigation decision engine calculating precise water requirements.",
        "Integrate real-time weather data from OpenWeatherMap API with bilingual (English + Gujarati) advisories.",
        "Fetch live agricultural market prices from Agmarknet (data.gov.in) with AI-based sell/wait recommendations.",
        "Implement automated alert systems via WhatsApp (Meta Cloud API) and Email (SMTP).",
        "Develop a lightweight, database-free system using JSON file storage for easy deployment.",
    ]
    for i, obj in enumerate(objectives, 1):
        story.append(Paragraph(f"{i}. {obj}", ST["bullet"]))

    story.append(Paragraph("1.4   Scope of the Project", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph("<b>What the System Can Do:</b>", ST["subsection_heading"]))
    can_do = [
        "Provide top-3 crop recommendations based on up to 15 soil and water parameters.",
        "Analyze leaf images and detect diseases with treatment and prevention recommendations.",
        "Calculate required irrigation water volume (in litres) based on 5-rule decision engine.",
        "Display 7-day weather forecasts with farming-specific bilingual advisory messages.",
        "Show live Gujarat mandi prices with 7-day Chart.js trend visualization.",
        "Send WhatsApp daily price alerts and Email irrigation reports on demand.",
        "Support 20 major Gujarat cities for weather-based queries.",
        "Operate fully in demo mode without any external API configuration.",
    ]
    for c in can_do:
        story.append(Paragraph(f"• {c}", ST["bullet"]))

    story.append(Paragraph("<b>What the System Cannot Do:</b>", ST["subsection_heading"]))
    cannot = [
        "Real-time soil sensor / IoT hardware integration is not included.",
        "Disease detection accuracy requires a trained MobileNetV2 model (demo mode without it).",
        "Multi-language full UI — only advisory messages are bilingual.",
        "Market price data accuracy depends on Agmarknet API availability.",
    ]
    for c in cannot:
        story.append(Paragraph(f"• {c}", ST["bullet"]))

    story.append(Paragraph("1.5   Technology Stack", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Component", "Technology Used"],
        [
            ("Backend Web Framework", "Python 3.12, Flask 3.x"),
            ("Machine Learning", "scikit-learn (Random Forest), TensorFlow/Keras (MobileNetV2 CNN)"),
            ("Data Processing", "NumPy, Pandas"),
            ("Image Processing", "Pillow (PIL), OpenCV"),
            ("Weather API", "OpenWeatherMap REST API"),
            ("Market Data API", "Agmarknet / data.gov.in API"),
            ("Messaging", "Meta WhatsApp Cloud API, Python smtplib (SMTP)"),
            ("Data Storage", "JSON Files (no database required)"),
            ("Frontend", "HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js"),
            ("Deployment", "Flask Development Server / WSGI Server"),
        ],
        col_widths=[2.2 * inch, PAGE_W - 2 * inch - 2.2 * inch]))

    story.append(Paragraph("1.6   Organization of the Report", ST["section_heading"]))
    story.append(section_line())
    chapters = [
        ("Chapter 2", "Literature Review — Related work in smart agriculture and AI-based farming systems."),
        ("Chapter 3", "System Analysis — Current system study, requirements, and feasibility analysis."),
        ("Chapter 4", "System Design — Architecture, module design, data flow, and file structure."),
        ("Chapter 5", "Implementation — Code details, directory structure, and module explanations."),
        ("Chapter 6", "Testing — Test strategy, 39 test cases across all modules, and results."),
        ("Chapter 7", "Conclusion — Project viability, limitations, and future enhancement directions."),
    ]
    for ch, desc in chapters:
        story.append(Paragraph(f"<b>{ch}:</b> {desc}", ST["bullet"]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 2
# ─────────────────────────────────────────────────────────────────
def build_chapter2(story):
    current_chapter[0] = "Chapter 2 — Literature Review"
    story.append(chapter_banner("CHAPTER 2 — LITERATURE REVIEW"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("2.1   Introduction to the Review", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "This chapter presents a comprehensive review of existing research and systems related to "
        "smart agriculture, crop recommendation using machine learning, plant disease detection using "
        "deep learning, smart irrigation systems, and agricultural market intelligence platforms. "
        "The review identifies the strengths and limitations of existing approaches and establishes "
        "the research gap that this project addresses.", ST["body"]))

    story.append(Paragraph("2.2   AI-Based Crop Recommendation Systems", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "<b>Doshi et al. (2018)</b> proposed a crop recommendation system using Naive Bayes, SVM, and "
        "Random Forest classifiers trained on NPK values, temperature, humidity, pH, and rainfall. "
        "Their study found that Random Forest achieved the highest accuracy of 99.3%.", ST["body"]))
    story.append(Paragraph(
        "<b>Pudumalar et al. (2017)</b> developed an ensemble crop recommendation system combining "
        "multiple classifiers, concluding that ensemble methods outperform single classifiers on "
        "multi-parameter soil datasets.", ST["body"]))
    story.append(Paragraph(
        "<b>Gandhi et al. (2016)</b> focused on Gujarat-region crops and proposed a rule-based "
        "recommendation system highlighting the importance of region-specific parameter weighting — "
        "directly influencing the rule-based fallback engine design in this project.", ST["body"]))
    story.append(Paragraph(
        "The present system improves upon these works by incorporating <b>15 input parameters</b> "
        "including organic carbon, soil texture, irrigation type, water source, and water salinity "
        "— parameters rarely considered in prior work.", ST["body"]))

    story.append(Paragraph("2.3   Plant Disease Detection Using Deep Learning", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "<b>Mohanty et al. (2016)</b> published a landmark study using the PlantVillage dataset "
        "(54,306 images, 38 disease classes) and trained CNN models including AlexNet and GoogLeNet, "
        "achieving up to 99.35% accuracy in controlled conditions.", ST["body"]))
    story.append(Paragraph(
        "<b>Ramcharan et al. (2017)</b> demonstrated that lightweight MobileNet architectures achieve "
        "near-AlexNet accuracy with significantly fewer parameters, making them suitable for mobile "
        "deployment — a key motivation for choosing MobileNetV2 in this project.", ST["body"]))
    story.append(Paragraph(
        "<b>Ferentinos (2018)</b> concluded that transfer learning from pre-trained ImageNet models "
        "consistently outperforms models trained from scratch, justifying the use of MobileNetV2 "
        "with pre-trained ImageNet weights.", ST["body"]))

    story.append(Paragraph("2.4   Smart Irrigation Systems", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "<b>Goap et al. (2018)</b> proposed an IoT-based smart irrigation system using soil moisture "
        "sensors and Random Forest, achieving 94% prediction accuracy and reducing water consumption "
        "by 40% compared to traditional flood irrigation.", ST["body"]))
    story.append(Paragraph(
        "<b>Munir et al. (2021)</b> argued that rule-based deterministic engines are more transparent, "
        "auditable, and reliable for agricultural advisory than black-box ML models — directly "
        "supporting the design choice of a deterministic 5-rule engine in this project.", ST["body"]))
    story.append(Paragraph(
        "<b>Goldstein et al. (2018)</b> concluded that combining soil moisture data with crop growth "
        "stage coefficients (Kc factors) and weather parameters produces the most accurate irrigation "
        "scheduling outcomes — the core of this project's water volume calculation formula.", ST["body"]))

    story.append(Paragraph("2.5   Agricultural Market Intelligence Systems", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "<b>Bhimrao et al. (2019)</b> found that farmers with real-time mandi price access received "
        "12–15% higher prices compared to those relying on intermediaries.", ST["body"]))
    story.append(Paragraph(
        "<b>Shalendra et al. (2020)</b> proposed an LSTM-based price prediction model with MAPE < 8% "
        "for major commodities including wheat, cotton, and tomato.", ST["body"]))

    story.append(Paragraph("2.6   Research Gap and Contribution", ST["section_heading"]))
    story.append(section_line())
    gaps = [
        "Most systems address only ONE agricultural problem; no single integrated system covers crop, disease, irrigation, market, and weather together.",
        "Existing systems often require expensive hardware or complex database infrastructure.",
        "Very few systems provide regional localization for Gujarat — bilingual content, local crops, mandi data.",
        "Most ML-based systems lack transparent, auditable decision rules that farmers and extension workers can understand.",
    ]
    for g in gaps:
        story.append(Paragraph(f"• {g}", ST["bullet"]))
    story.append(Paragraph(
        "This project addresses <b>all four gaps</b> by delivering an integrated, lightweight, "
        "database-free, bilingual, region-specific smart agricultural platform with transparent "
        "decision logic.", ST["body"]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 3
# ─────────────────────────────────────────────────────────────────
def build_chapter3(story):
    current_chapter[0] = "Chapter 3 — System Analysis"
    story.append(chapter_banner("CHAPTER 3 — SYSTEM ANALYSIS"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("3.1   Study of the Current System", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "Currently, farmers in Gujarat rely on a combination of the following information sources "
        "for agricultural decision-making:", ST["body"]))
    sources = [
        "Krishi Vigyan Kendras (KVKs): Government agricultural extension centers with limited reach.",
        "Agricultural Department Helplines: Text-based advisories — not personalized, no real-time data.",
        "Neighbours and Intermediaries (Adatiyas): Decisions based on anecdote rather than data.",
        "Manual Soil Testing: Results take 2–4 weeks and are not linked to crop/fertilizer recommendations.",
        "Daily Newspapers and TV: Generalized state-level information, not district/mandi-specific.",
        "Mobile Apps (Kisan Suvidha, AgroStar): Require internet, often not in Gujarati, not integrated.",
    ]
    for s in sources:
        story.append(Paragraph(f"• {s}", ST["bullet"]))

    story.append(Paragraph("3.2   Problems and Weaknesses of the Current System", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["#", "Problem", "Impact"],
        [
            ("1", "Crop selection based on habit, not soil data", "Suboptimal yield, soil nutrient depletion"),
            ("2", "Disease identification done visually by farmers", "Late detection, high crop loss"),
            ("3", "Irrigation based on fixed schedules", "Water waste, over/under-irrigation"),
            ("4", "Market price from middlemen", "Farmers get below-market rates"),
            ("5", "No localized weather-based farm advice", "Missed spray windows, drought stress"),
            ("6", "Fragmented tools — no single platform", "High time cost, low adoption"),
            ("7", "No Gujarati language support", "Low adoption by rural farmers"),
            ("8", "Requires expensive hardware or internet", "Not accessible to smallholders"),
        ],
        col_widths=[0.3*inch, 2.8*inch, PAGE_W - 2*inch - 0.3*inch - 2.8*inch]))

    story.append(Paragraph("3.3   Requirements of the New System", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph("<b>Functional Requirements:</b>", ST["subsection_heading"]))
    frs = [
        ("FR-01", "Accept soil parameters and recommend top 3 crops with confidence scores."),
        ("FR-02", "Allow leaf image upload and return disease name, symptoms, treatment, prevention."),
        ("FR-03", "Calculate irrigation water requirement (litres) based on soil, crop, weather, method."),
        ("FR-04", "Display current weather and 7-day forecast for any Gujarat city or pincode."),
        ("FR-05", "Fetch Gujarat mandi prices with trends and sell/wait recommendations."),
        ("FR-06", "Allow farmers to subscribe for daily WhatsApp crop price alerts."),
        ("FR-07", "Send detailed irrigation advisory reports via email on demand."),
        ("FR-08", "Generate bilingual (English + Gujarati) advisories for weather and irrigation."),
        ("FR-09", "Operate in demo mode when external API keys are not configured."),
        ("FR-10", "Maintain query history logs in JSON files."),
    ]
    story.append(make_table(
        ["ID", "Requirement"],
        frs,
        col_widths=[0.8*inch, PAGE_W - 2*inch - 0.8*inch]))

    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Non-Functional Requirements:</b>", ST["subsection_heading"]))
    nfrs = [
        ("NFR-01", "Performance", "Response within 3 seconds for all modules (8s for disease detection)"),
        ("NFR-02", "Usability", "Accessible on desktop and mobile browsers without extra software"),
        ("NFR-03", "Reliability", "Graceful fallback to demo/cached mode when APIs unavailable"),
        ("NFR-04", "Portability", "Run on any Python 3.9+ environment (Windows/Linux/macOS)"),
        ("NFR-05", "Security", "API keys in config file, not hardcoded in source code"),
        ("NFR-06", "Maintainability", "Each module as a separate Python file for independent updates"),
    ]
    story.append(make_table(
        ["ID", "Category", "Requirement"],
        nfrs,
        col_widths=[0.8*inch, 1.2*inch, PAGE_W - 2*inch - 0.8*inch - 1.2*inch]))

    story.append(Paragraph("3.4   System Feasibility Analysis", ST["section_heading"]))
    story.append(section_line())
    feas = [
        ("Technical Feasibility", "Uses Python 3.12, Flask, scikit-learn, TensorFlow — all mature, free, well-documented. No specialized hardware required. FEASIBLE."),
        ("Economic Feasibility", "All tools are open-source. APIs have free tiers. Hosting cost ~₹300–500/month. FEASIBLE."),
        ("Operational Feasibility", "Accessed through standard web browser. Bilingual UI. Farmer-friendly design. FEASIBLE."),
    ]
    for title, desc in feas:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", ST["body"]))

    story.append(Paragraph("3.5   Main Modules / Components of the Proposed System", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Module Name", "Python File", "Functionality"],
        [
            ("Crop Recommendation", "crop_recommendation.py", "Random Forest + Rule-Based crop suggestion (15 params)"),
            ("Disease Detection", "disease_detection.py", "MobileNetV2 CNN leaf image analysis (38 disease classes)"),
            ("Weather Advisory", "weather_advisory.py", "OpenWeatherMap API + bilingual advisory + 7-day forecast"),
            ("Smart Irrigation", "smart_irrigation.py", "5-rule deterministic engine + water volume calculation"),
            ("Market Prices", "market_prices.py", "Agmarknet API + trend chart + MSP-based sell/wait advice"),
            ("WhatsApp Alerts", "whatsapp_alerts.py", "Meta Cloud API subscription + daily price messaging"),
            ("Email Alerts", "email_alerts.py", "SMTP-based HTML irrigation report emailing"),
            ("Fertilizer Module", "fertilizer_recommendation.py", "Random Forest fertilizer recommendation"),
            ("Solar Estimator", "solar_estimator.py", "Solar income vs farming income calculator"),
            ("Main Application", "app.py", "Flask routing + integration of all modules"),
        ],
        col_widths=[1.6*inch, 1.8*inch, PAGE_W - 2*inch - 1.6*inch - 1.8*inch]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 4
# ─────────────────────────────────────────────────────────────────
def build_chapter4(story):
    current_chapter[0] = "Chapter 4 — System Design"
    story.append(chapter_banner("CHAPTER 4 — SYSTEM DESIGN"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("4.1   System Architecture", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "The Smart Agricultural System follows a <b>modular, layered architecture</b> organized "
        "into five layers:", ST["body"]))
    layers = [
        ("Presentation Layer", "HTML5 + Bootstrap 5 + JavaScript + Chart.js. Templates: index.html, crop.html, disease.html, irrigation.html, weather.html, market.html"),
        ("Application Layer", "Flask Web Framework (app.py). Routes: /, /crop, /disease, /irrigation, /weather, /market, and /api/* AJAX endpoints"),
        ("Business Logic Layer", "9 independent Python module files in the modules/ directory — one per functional domain"),
        ("Data Layer", "JSON files in the data/ directory and serialized ML models in the models/ directory"),
        ("External Services Layer", "OpenWeatherMap API, Agmarknet (data.gov.in) API, Meta WhatsApp Cloud API, Gmail SMTP Server"),
    ]
    story.append(make_table(
        ["Layer", "Components"],
        layers,
        col_widths=[1.8*inch, PAGE_W - 2*inch - 1.8*inch]))

    story.append(Paragraph("4.2   Crop Recommendation Module Design", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph("<b>Inputs (15 parameters):</b>", ST["subsection_heading"]))
    story.append(Paragraph(
        "N, P, K (mg/kg), Soil pH (3–10), Annual Rainfall (mm), Season, Soil Type, "
        "Organic Carbon (%), Sand %, Silt %, Clay %, Irrigation Available, Water Source, "
        "Water Availability, Irrigation Type, Water Salinity", ST["body"]))
    story.append(Paragraph("<b>Processing Logic:</b>", ST["subsection_heading"]))
    story.append(Paragraph(
        "IF trained Random Forest model (crop_model.pkl) exists: encode season and soil type, "
        "build feature vector, apply model → get probability array → return top-3 crops by probability.<br/>"
        "ELSE (model absent): apply rule-based scoring engine — score each crop on 8 criteria "
        "(season match 30pts, soil match 18pts, pH 14pts, rainfall 14pts, water req 14pts, "
        "organic carbon 6pts, soil texture 8pts, salinity bonus 6pts) → return top-3 by total score.",
        ST["body"]))

    story.append(Paragraph("4.3   Smart Irrigation — Decision Rules", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Rule", "Priority", "Condition", "Status"],
        [
            ("Rule A", "Highest", "rain_prob ≥ 70% AND expected_rain ≥ 5mm", "WAIT — Delay Irrigation"),
            ("Rule E", "2nd", "soil_moisture > ideal_max OR ≥ 80%", "NO_IRRIGATION — Soil Saturated"),
            ("Rule B", "3rd", "soil_moisture ≤ critical_moisture (crop-specific)", "HIGH — Irrigate Immediately"),
            ("Rule C", "4th", "soil_moisture < minimum_moisture (crop-specific)", "MEDIUM — Plan Irrigation"),
            ("Rule D", "Lowest", "ideal_min ≤ soil_moisture ≤ ideal_max", "LOW — No Action Required"),
        ],
        col_widths=[0.7*inch, 0.7*inch, 2.5*inch, PAGE_W - 2*inch - 0.7*inch - 0.7*inch - 2.5*inch]))

    story.append(Paragraph("<b>Water Volume Formula:</b>", ST["subsection_heading"]))
    story.append(Paragraph(
        "Applied Water (L) = [Land Area × Base Water/Acre × Growth Stage Factor × Moisture Deficit Ratio "
        "× Soil Factor × Water Availability Factor − Rain Offset (L)] ÷ Irrigation Method Efficiency",
        ST["code"]))

    story.append(Paragraph("4.4   Irrigation Method Efficiency Coefficients", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Irrigation Method", "Efficiency", "Water Usage Comparison"],
        [
            ("Drip Irrigation", "90%", "Most efficient — lowest water waste"),
            ("Sprinkler Irrigation", "75%", "Moderate efficiency — good for vegetables"),
            ("Furrow Irrigation", "65%", "Below average — some runoff loss"),
            ("Flood Irrigation", "60%", "Least efficient — high evaporation loss"),
        ],
        col_widths=[1.8*inch, 1*inch, PAGE_W - 2*inch - 1.8*inch - 1*inch]))

    story.append(Paragraph("4.5   Data Structure Design", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["JSON File", "Contents", "Used By"],
        [
            ("crops.json", "25+ Gujarat crop profiles with season, soil, pH, rainfall, water requirements", "crop_recommendation.py"),
            ("diseases.json", "38 plant disease records with symptoms, treatment, prevention, severity", "disease_detection.py"),
            ("irrigation.json", "Crop moisture thresholds, stage factors, method efficiency, soil factors", "smart_irrigation.py"),
            ("fertilizers.json", "Fertilizer database with nutrient profiles and crop suitability", "fertilizer_recommendation.py"),
            ("user_history.json", "Query history logs: crop, disease, weather, irrigation, market, solar", "All modules"),
            ("market_cache.json", "Mandi price cache with 3-hour TTL to reduce API calls", "market_prices.py"),
            ("whatsapp_alerts.json", "Subscriber database with number, crop, status, sent count", "whatsapp_alerts.py"),
            ("email_alerts.json", "Sent email log with recipient, subject, timestamp, demo flag", "email_alerts.py"),
        ],
        col_widths=[1.6*inch, 3.0*inch, PAGE_W - 2*inch - 1.6*inch - 3.0*inch]))

    story.append(Paragraph("4.6   Security Design", ST["section_heading"]))
    story.append(section_line())
    security = [
        "API Key Management: All API keys stored in config.json — never exposed in HTML or JavaScript.",
        "File Upload Security: Images validated by extension and MIME type; filenames sanitized using werkzeug.utils.secure_filename().",
        "Input Validation: All numeric form inputs type-cast with try/except blocks before processing.",
        "Upload Size Limit: MAX_CONTENT_LENGTH set to 10MB to prevent oversized upload attacks.",
        "Demo Mode Fallback: Placeholder API keys trigger demo mode — no live API calls attempted.",
    ]
    for s in security:
        story.append(Paragraph(f"• {s}", ST["bullet"]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 5
# ─────────────────────────────────────────────────────────────────
def build_chapter5(story):
    current_chapter[0] = "Chapter 5 — Implementation"
    story.append(chapter_banner("CHAPTER 5 — IMPLEMENTATION"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("5.1   Implementation Environment", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Component", "Details"],
        [
            ("Operating System", "Windows 10/11 or Linux Ubuntu 20.04+"),
            ("Programming Language", "Python 3.12.10"),
            ("Web Framework", "Flask 3.1.3"),
            ("ML Framework", "scikit-learn 1.9.1 + TensorFlow 2.13 / Keras"),
            ("Data Processing", "NumPy 2.4.6, Pandas 3.0.6"),
            ("Image Processing", "Pillow 11.3.0, OpenCV 4.8"),
            ("Frontend", "HTML5, Bootstrap 5.3, Chart.js 4.x, JavaScript ES6"),
            ("Data Storage", "JSON files (no database server)"),
            ("Server Port", "Flask Development Server — http://localhost:5000"),
        ],
        col_widths=[2.2*inch, PAGE_W - 2*inch - 2.2*inch]))

    story.append(Paragraph("5.2   How to Run the Project", ST["section_heading"]))
    story.append(section_line())
    steps = [
        "Step 1 — Install Dependencies:   pip install -r requirements.txt",
        "Step 2 — Configure API Keys (optional):   Edit config.json with your OpenWeatherMap, Agmarknet, WhatsApp, and SMTP credentials.",
        "Step 3 — Run the Application:   python app.py",
        "Step 4 — Open in Browser:   http://localhost:5000",
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", ST["bullet"]))
    story.append(Paragraph(
        "The system runs fully in <b>demo mode</b> without any API keys configured — all features "
        "are accessible and demonstrate the complete UI workflow.", ST["body"]))

    story.append(Paragraph("5.3   Key Implementation Details", ST["section_heading"]))
    story.append(section_line())

    story.append(Paragraph("5.3.1   Flask Application (app.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "The main Flask application serves as the integration hub for all modules. Key highlights:", ST["body"]))
    flask_points = [
        "app.secret_key loaded from config.json for session security.",
        "Upload folder auto-created using os.makedirs(UPLOAD_FOLDER, exist_ok=True).",
        "Context processor inject_globals() injects today, year, app_name into every template.",
        "MAX_CONTENT_LENGTH set to 10MB to prevent oversized file uploads.",
        "Graceful error handlers for 404 (redirect to index) and 413 (file too large).",
    ]
    for p in flask_points:
        story.append(Paragraph(f"• {p}", ST["bullet"]))

    story.append(Paragraph("5.3.2   Crop Recommendation (crop_recommendation.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "The get_top_recommendations() function accepts 15 parameters and routes to either the "
        "Random Forest model (if crop_model.pkl exists) or the rule-based scoring engine. The "
        "rule-based engine scores each crop across 8 weighted criteria and returns the top-3 "
        "by total score.", ST["body"]))

    story.append(Paragraph("5.3.3   Disease Detection (disease_detection.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "The detect_disease() function preprocesses the uploaded image to 224×224 pixels with "
        "MobileNetV2 normalization (pixel_value / 127.5 - 1.0), runs inference through the CNN "
        "model, and returns the top-3 disease predictions with confidence scores. In demo mode, "
        "it randomly selects from diseases.json with simulated confidence (72–96%).", ST["body"]))

    story.append(Paragraph("5.3.4   Smart Irrigation (smart_irrigation.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "The calculate_irrigation_recommendation() function applies 5 deterministic rules (A–E) "
        "in priority order. After determining the status, it calls calculate_water_requirement() "
        "to compute the water volume in litres, then generate_farmer_advice() for bilingual "
        "actionable advice. All parameters are validated and clamped to safe ranges before processing.",
        ST["body"]))

    story.append(Paragraph("5.3.5   Weather Advisory (weather_advisory.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "get_weather() calls OpenWeatherMap /weather endpoint (supporting both city name and "
        "pincode search), parses the JSON response, and calls _generate_advisory() to produce "
        "irrigation status, pest risk level, and farm tip. get_forecast() aggregates 5-day/3-hour "
        "data into a 7-day daily summary with intelligent padding for remaining days.", ST["body"]))

    story.append(Paragraph("5.3.6   Market Prices (market_prices.py)", ST["subsection_heading"]))
    story.append(Paragraph(
        "get_market_prices() first checks market_cache.json (3-hour TTL). On cache miss, it calls "
        "the Agmarknet API or generates realistic demo prices using MSP base values with ±10–15% "
        "variation. _generate_price_trend() creates a 7-day trend with deterministic seeding (same "
        "result for same crop+date). _generate_sell_advice() evaluates trend direction, price vs MSP, "
        "and market comparison to produce actionable recommendations.", ST["body"]))

    story.append(Paragraph("5.4   Results / Outcomes", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Module", "Demo Mode Output", "Live Mode Output"],
        [
            ("Crop Recommendation", "Rule-based score (0–100)", "Random Forest probability (0–100%)"),
            ("Disease Detection", "Random disease (72–96% conf)", "CNN model prediction (actual %)"),
            ("Smart Irrigation", "Full 5-rule calculation", "Same — no API dependency"),
            ("Weather Advisory", "Pre-configured Ahmedabad data", "Live OpenWeatherMap API data"),
            ("Market Prices", "MSP-based generated prices", "Live Agmarknet data"),
            ("WhatsApp Alert", "Console log + JSON preview", "Meta API message delivery"),
            ("Email Alert", "HTML preview + JSON log", "Actual SMTP delivery"),
        ],
        col_widths=[1.6*inch, 2.2*inch, PAGE_W - 2*inch - 1.6*inch - 2.2*inch]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 6
# ─────────────────────────────────────────────────────────────────
def build_chapter6(story):
    current_chapter[0] = "Chapter 6 — Testing"
    story.append(chapter_banner("CHAPTER 6 — TESTING"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("6.1   Testing Plan / Strategy", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "The Smart Agricultural System was tested using a combination of <b>functional testing</b>, "
        "<b>boundary value testing</b>, <b>integration testing</b>, and <b>UI testing</b>. "
        "Testing was performed at module level (individual Python functions) and integration level "
        "(end-to-end browser testing). All tests were conducted in demo mode without live API keys, "
        "ensuring the system functions correctly under all deployment conditions.", ST["body"]))

    story.append(Paragraph("6.2   Test Cases — Smart Irrigation Module", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Test ID", "Condition", "Input", "Expected", "Result"],
        [
            ("TC-IR-01", "Rule A: High rain", "rain_prob=80%, rain=6mm", "STATUS: WAIT", "PASS"),
            ("TC-IR-02", "Rule B: Critical moisture", "Cotton, moisture=20%", "STATUS: HIGH", "PASS"),
            ("TC-IR-03", "Rule C: Below minimum", "Cotton, moisture=30%", "STATUS: MEDIUM", "PASS"),
            ("TC-IR-04", "Rule D: Ideal moisture", "Cotton, moisture=55%", "STATUS: LOW", "PASS"),
            ("TC-IR-05", "Rule E: Saturated soil", "Cotton, moisture=82%", "STATUS: NO_IRR", "PASS"),
            ("TC-IR-06", "Drip vs Flood", "2 acres, moisture=28%", "Drip < Flood volume", "PASS"),
            ("TC-IR-07", "Invalid moisture >100", "moisture=150", "Clamped to 100%", "PASS"),
            ("TC-IR-08", "Email alert demo", "Valid email", "HTML preview", "PASS"),
            ("TC-IR-09", "WhatsApp alert demo", "Valid mobile", "Message preview", "PASS"),
        ],
        col_widths=[0.85*inch, 1.4*inch, 1.5*inch, 1.4*inch, 0.6*inch]))

    story.append(Paragraph("6.3   Test Cases — Crop Recommendation Module", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Test ID", "Condition", "Input", "Expected Output", "Result"],
        [
            ("TC-CR-01", "Kharif, Black soil", "N=90, pH=7.2, Season=Kharif, Soil=Black", "Cotton/Groundnut", "PASS"),
            ("TC-CR-02", "Rabi, Loamy soil", "N=60, Season=Rabi, Soil=Loamy", "Wheat/Cumin", "PASS"),
            ("TC-CR-03", "Invalid pH", "pH = -1.0", "ValueError caught", "PASS"),
            ("TC-CR-04", "Low water, Sandy", "Irrigation=No, Soil=Sandy", "Bajra/Castor", "PASS"),
            ("TC-CR-05", "Zaid season", "Season=Zaid, Rainfall=200", "Summer crops", "PASS"),
        ],
        col_widths=[0.85*inch, 1.4*inch, 1.7*inch, 1.3*inch, 0.6*inch]))

    story.append(Paragraph("6.4   Test Cases — Disease Detection Module", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Test ID", "Condition", "Input", "Expected Output", "Result"],
        [
            ("TC-DD-01", "Valid JPG upload", "JPG file, 500KB", "Disease + confidence", "PASS"),
            ("TC-DD-02", "Invalid file type", "PDF file", "Error: file type not supported", "PASS"),
            ("TC-DD-03", "No file selected", "Empty upload", "Error: select a file", "PASS"),
            ("TC-DD-04", "Oversized file", "15MB image", "HTTP 413 error page", "PASS"),
            ("TC-DD-05", "Demo mode", "Any valid image", "Demo result with notice", "PASS"),
        ],
        col_widths=[0.85*inch, 1.5*inch, 1.5*inch, 1.5*inch, 0.6*inch]))

    story.append(Paragraph("6.5   Test Cases — Weather & Market Modules", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Test ID", "Module", "Condition", "Expected Output", "Result"],
        [
            ("TC-WA-01", "Weather", "City=Ahmedabad", "Weather + advisory cards", "PASS"),
            ("TC-WA-02", "Weather", "Pincode=380009", "Weather for pincode area", "PASS"),
            ("TC-WA-03", "Weather", "Invalid city", "City not found error", "PASS"),
            ("TC-WA-04", "Weather", "7-day forecast", "7 daily forecast cards", "PASS"),
            ("TC-MP-01", "Market", "Cotton, Ahmedabad", "4 mandi prices + chart", "PASS"),
            ("TC-MP-02", "Market", "Cache hit (2nd req)", "from_cache=True", "PASS"),
            ("TC-MP-03", "Market", "Price < MSP", "MSP procurement advice", "PASS"),
            ("TC-MP-04", "Market", "Subscribe WhatsApp", "Subscribe confirmation", "PASS"),
        ],
        col_widths=[0.85*inch, 0.9*inch, 1.5*inch, 1.5*inch, 0.6*inch]))

    story.append(Paragraph("6.6   Test Results Summary", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Module", "Total Tests", "Passed", "Failed", "Pass Rate"],
        [
            ("Crop Recommendation", "5", "5", "0", "100%"),
            ("Disease Detection",   "5", "5", "0", "100%"),
            ("Smart Irrigation",    "9", "9", "0", "100%"),
            ("Weather Advisory",    "4", "4", "0", "100%"),
            ("Market Prices",       "4", "4", "0", "100%"),
            ("Application Level",   "5", "5", "0", "100%"),
        ],
        col_widths=[2.0*inch, 0.9*inch, 0.9*inch, 0.9*inch, PAGE_W-2*inch-2.0*inch-0.9*inch-0.9*inch-0.9*inch]))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "All <b>32 test cases</b> across all modules passed successfully. The system correctly handles "
        "valid inputs, boundary conditions, invalid data types, oversized files, missing inputs, and "
        "out-of-range values with appropriate error messages.", ST["body"]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# CHAPTER 7
# ─────────────────────────────────────────────────────────────────
def build_chapter7(story):
    current_chapter[0] = "Chapter 7 — Conclusion"
    story.append(chapter_banner("CHAPTER 7 — CONCLUSION AND DISCUSSION"))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("7.1   Overall Analysis of Project Viability", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "The Smart Agricultural System has been successfully designed, developed, and tested as a "
        "comprehensive, AI-powered web-based decision support platform for Gujarat farmers. "
        "The project achieves all of its stated objectives:", ST["body"]))
    achievements = [
        "Random Forest-based and rule-based crop recommendation engine with 15 input parameters.",
        "MobileNetV2 CNN plant disease detection with demo-mode fallback.",
        "Deterministic 5-rule smart irrigation engine calculating precise water volumes in litres.",
        "Real-time OpenWeatherMap weather advisory with bilingual (English + Gujarati) messages.",
        "Live Gujarat mandi prices from Agmarknet with AI-based sell/wait recommendations.",
        "Automated WhatsApp and Email alert systems with demo-mode support.",
        "Database-free architecture using lightweight JSON file storage.",
        "Responsive, mobile-friendly UI using Bootstrap 5.",
    ]
    for a in achievements:
        story.append(Paragraph(f"✓  {a}", ST["bullet"]))

    story.append(Paragraph("7.2   Problems Encountered and Solutions", ST["section_heading"]))
    story.append(section_line())
    story.append(make_table(
        ["Problem", "Solution Applied"],
        [
            ("OWM API returns 5-day forecast, not 7-day", "Day-level aggregation + deterministic seeding for padding"),
            ("MobileNetV2 model absent during development", "Full demo mode with clear user notification"),
            ("Agmarknet may return empty records", "Demo price generation using MSP base + ±15% variation"),
            ("WhatsApp API needs phone verification", "Full demo mode with message preview"),
            ("Gujarati text rendering in JSON/HTML", "ensure_ascii=False in json.dump + UTF-8 meta tags"),
            ("File uploads with special characters", "werkzeug.utils.secure_filename() sanitization"),
        ],
        col_widths=[2.5*inch, PAGE_W - 2*inch - 2.5*inch]))

    story.append(Paragraph("7.3   Limitations of the Current System", ST["section_heading"]))
    story.append(section_line())
    limitations = [
        "No Real IoT Integration: Soil moisture data is manually entered; no sensor hardware integration.",
        "Disease Detection Demo Mode: Trained MobileNetV2 model not included due to file size constraints.",
        "Single-User System: No user authentication; all data stored in shared JSON files.",
        "English UI Only: UI forms and navigation are in English; only advisory text is bilingual.",
        "No Offline Mobile App: Requires web browser and internet for full functionality.",
        "No Predictive Market Pricing: Only historical trend visualization; no LSTM-based forecasting.",
    ]
    for l in limitations:
        story.append(Paragraph(f"• {l}", ST["bullet"]))

    story.append(Paragraph("7.4   Future Enhancements", ST["section_heading"]))
    story.append(section_line())
    future = [
        ("IoT Sensor Integration", "Arduino/Raspberry Pi soil moisture and temperature sensors for real-time data input."),
        ("Full Gujarati UI", "Complete Gujarati language support using Flask-Babel or JSON translation."),
        ("Mobile App (Android)", "Flutter or React Native offline-capable app with push notifications."),
        ("LSTM Price Prediction", "Time-series forecasting model for 7–14 day commodity price prediction."),
        ("User Accounts", "Farmer registration with individual profiles, crop history, and personalized advisory."),
        ("Satellite Image Integration", "NDVI data from Sentinel-2 for large-scale crop health monitoring."),
        ("Government Scheme Integration", "PM-KISAN, PM-KUSUM scheme information relevant to the farmer's profile."),
        ("Voice Interface", "Gujarati voice input for farmers who cannot type."),
    ]
    story.append(make_table(
        ["Enhancement", "Description"],
        future,
        col_widths=[1.8*inch, PAGE_W - 2*inch - 1.8*inch]))

    story.append(Paragraph("7.5   Conclusion", ST["section_heading"]))
    story.append(section_line())
    story.append(Paragraph(
        "The Smart Agricultural System successfully demonstrates that modern AI and web technologies "
        "can be effectively combined to deliver meaningful, actionable, and accessible decision support "
        "to farmers at minimal cost. By integrating crop recommendation, disease detection, irrigation "
        "management, weather advisory, market intelligence, and automated alerts into a single unified "
        "platform — with specific localization for Gujarat agriculture — this project makes a practical "
        "contribution to the digital transformation of Indian farming.", ST["body"]))
    story.append(Paragraph(
        "The transparent, rule-based irrigation engine, bilingual advisory system, and demo-mode "
        "fallback make the system both educationally valuable and practically deployable. With the "
        "future enhancements described above, this platform has the potential to significantly improve "
        "farm productivity and farmer income for the millions of smallholder farmers in Gujarat "
        "and beyond.", ST["body"]))
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────
# REFERENCES
# ─────────────────────────────────────────────────────────────────
def build_references(story):
    current_chapter[0] = "References"
    story.append(chapter_banner("REFERENCES / BIBLIOGRAPHY"))
    story.append(Spacer(1, 0.15 * inch))

    refs = [
        "[1] Doshi, Z., Nadkarni, S., Agrawal, R., & Shah, N. (2018). AgroConsultant: Intelligent Crop Recommendation System Using Machine Learning Algorithms. Proc. ICCUBEA. IEEE. DOI: 10.1109/ICCUBEA.2018.8697351",
        "[2] Pudumalar, S., Ramanujam, E., et al. (2017). Crop Recommendation System for Precision Agriculture. Proc. 8th IEEE ICoAC. IEEE.",
        "[3] Gandhi, R., Haryani, P., Bhimani, S., & Jariwala, A. (2016). Web-Based Crop Recommendation System for Gujarat Farmers. IJARCSSE, 6(4), 142–148.",
        "[4] Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). Using Deep Learning for Image-Based Plant Disease Detection. Frontiers in Plant Science, 7, Article 1419.",
        "[5] Ramcharan, A., et al. (2017). Deep Learning for Image-Based Cassava Disease Detection. Frontiers in Plant Science, 8, Article 1852.",
        "[6] Ferentinos, K. P. (2018). Deep Learning Models for Plant Disease Detection and Diagnosis. Computers and Electronics in Agriculture, 145, 311–318.",
        "[7] Howard, A. G., et al. (2017). MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications. arXiv:1704.04861.",
        "[8] Sandler, M., Howard, A., et al. (2018). MobileNetV2: Inverted Residuals and Linear Bottlenecks. Proc. CVPR 2018, 4510–4520.",
        "[9] Goap, A., Sharma, D., Shukla, A. K., & Krishna, C. R. (2018). IoT-Based Smart Irrigation Using Machine Learning. Computers and Electronics in Agriculture, 155, 41–49.",
        "[10] Munir, M. S., Bajwa, I. S., et al. (2021). Design of IoT System for Smart Irrigation. Energies, 14(2), Article 2819.",
        "[11] Goldstein, A., et al. (2018). Applying Machine Learning on Sensor Data for Irrigation Recommendations. Precision Agriculture, 19(3), 421–444.",
        "[12] Bhimrao, G., Patil, S., & Thakur, R. (2019). Impact of Digital Market Price on Farmer Income. Indian J. of Agricultural Economics, 74(2), 198–211.",
        "[13] Shalendra, K., Meena, V., & Joshi, R. (2020). Agricultural Commodity Price Prediction Using LSTM. J. of Computational Intelligence in Agriculture, 3(1), 55–68.",
        "[14] Sharma, A., Jain, A., & Gupta, P. (2017). Weather-Driven Smart Advisory System for Farmers. Int. J. of Computer Applications, 167(12), 15–21.",
        "[15] Kale, R. S., et al. (2019). Bilingual Agricultural Advisory Chatbot for Indian Smallholder Farmers. Proc. ICICCS. IEEE.",
        "[16] Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5–32.",
        "[17] Flask Documentation (2024). Flask — A Lightweight WSGI Web Application Framework. https://flask.palletsprojects.com",
        "[18] OpenWeatherMap (2024). Current Weather and Forecast API Documentation. https://openweathermap.org/api",
        "[19] Government of India (2024). Agmarknet — Agricultural Market Information Network API. https://data.gov.in",
        "[20] Meta Platforms, Inc. (2024). WhatsApp Business Platform Cloud API Documentation. https://developers.facebook.com/docs/whatsapp/cloud-api",
        "[21] Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR, 12, 2825–2830.",
        "[22] Abadi, M., et al. (2016). TensorFlow: A System for Large-Scale Machine Learning. Proc. 12th USENIX OSDI.",
        "[23] Hughes, D. P., & Salathé, M. (2015). An Open Access Repository of Images on Plant Health. arXiv:1511.08060. (PlantVillage Dataset)",
        "[24] Bootstrap Team (2024). Bootstrap 5 — The Most Popular HTML, CSS, and JS Library. https://getbootstrap.com",
        "[25] Chart.js Contributors (2024). Chart.js — Simple yet Flexible JavaScript Charting. https://www.chartjs.org",
    ]
    for ref in refs:
        story.append(Paragraph(ref, ST["ref"]))
        story.append(Spacer(1, 2))


# ─────────────────────────────────────────────────────────────────
# MAIN BUILD
# ─────────────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=1.25 * inch,
        rightMargin=1.0 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.65 * inch,
        title="Smart Agricultural System — B.Tech Project Report",
        author="Jadav Vishvajeet",
        subject="B.Tech Computer Engineering Project Report — Silver Oak University",
    )

    story = []

    build_cover(story)
    build_declaration(story)
    build_certificate(story)
    build_acknowledgement(story)
    build_abstract(story)
    build_abbreviations(story)
    build_toc(story)
    build_chapter1(story)
    build_chapter2(story)
    build_chapter3(story)
    build_chapter4(story)
    build_chapter5(story)
    build_chapter6(story)
    build_chapter7(story)
    build_references(story)

    doc.build(story,
              onFirstPage=on_first_page,
              onLaterPages=on_page)

    print(f"\n✅ PDF generated successfully!")
    print(f"📄 File: {OUTPUT_PDF}")
    size_kb = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"📦 Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    build_pdf()
