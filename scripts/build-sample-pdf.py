#!/usr/bin/env python3
"""
Build sample-roast.pdf — an anonymized 2-page sample audit report.

For $10, the deliverable should feel tight and consultative — not a
20-page deck. Two pages:
    1. The score + the 5 things to fix
    2. The full prioritized action list + a warm closing note

Run from repo root:
    python3 scripts/build-sample-pdf.py

Outputs: ./sample-roast.pdf
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

# ---------- Brand palette (mirrors index.html :root vars) ----------
CORAL    = HexColor('#FF6B6B')
PEACH    = HexColor('#FFB088')
SUNSHINE = HexColor('#FFD93D')
MINT     = HexColor('#6BCB77')
SKY      = HexColor('#4D96FF')
LAVENDER = HexColor('#B983FF')
CREAM    = HexColor('#FFF8F0')
INK      = HexColor('#2D1B3D')
INK_SOFT = HexColor('#5A4A6B')
WHITE    = HexColor('#FFFFFF')

PAGE_W, PAGE_H = letter   # 612 x 792 pts
M = 0.55 * 72             # margin

# ---------- helpers ----------
def wrap(text, font, size, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def header_strip(c, page_num):
    """Slim brand strip at top of each page."""
    h = 0.42 * 72
    # Coral top accent
    c.setFillColor(CORAL)
    c.rect(0, PAGE_H - 0.06 * 72, PAGE_W, 0.06 * 72, fill=1, stroke=0)
    # Cream strip
    c.setFillColor(CREAM)
    c.rect(0, PAGE_H - h, PAGE_W, h - 0.06 * 72, fill=1, stroke=0)
    # Brand
    c.setFillColor(INK)
    c.setFont("Times-Bold", 12)
    c.drawString(M, PAGE_H - 0.30 * 72, "On Site Roast")
    # Right-aligned context
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - M, PAGE_H - 0.30 * 72,
                      "example-saas.com  -  March 2026")
    return PAGE_H - h - 0.35 * 72  # next y

def footer(c, page_num, total):
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 8)
    c.drawString(M, 0.4 * 72, "Sample roast report  -  onsiteroast.com")
    c.drawRightString(PAGE_W - M, 0.4 * 72, f"Page {page_num} of {total}")

def pill(c, x, y, label, bg, fg=WHITE, font_size=8, height=14):
    pad = 6
    w = stringWidth(label, "Helvetica-Bold", font_size) + 2 * pad
    c.setFillColor(bg)
    c.roundRect(x, y, w, height, 7, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x + pad, y + 4, label)
    return w

def score_badge(c, x, y, w, h):
    """Big coral score block."""
    c.setFillColor(CORAL)
    c.roundRect(x, y, w, h, 12, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Times-Bold", 36)
    c.drawString(x + 14, y + h - 38, "6.4")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 14 + stringWidth("6.4", "Times-Bold", 36) + 6,
                 y + h - 24, "/ 10")
    c.setFont("Helvetica", 9)
    c.drawString(x + 14, y + 16, "Room to grow.")
    c.drawString(x + 14, y + 4,  "27 findings inside.")

def category_bars(c, x, y, w, cats):
    """Single-row strip of 5 mini category bars."""
    col_w = w / len(cats)
    bar_h = 6
    for i, (label, score) in enumerate(cats):
        cx = x + i * col_w
        # label
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx, y + 14, label)
        # score number
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 8)
        c.drawString(cx + col_w - 30, y + 14, f"{score}/10")
        # bar bg
        bar_w = col_w - 12
        c.setFillColor(CREAM)
        c.roundRect(cx, y, bar_w, bar_h, 3, fill=1, stroke=0)
        # bar fill
        color = MINT if score >= 7 else (SUNSHINE if score >= 6 else CORAL)
        c.setFillColor(color)
        c.roundRect(cx, y, (score / 10) * bar_w, bar_h, 3, fill=1, stroke=0)

def compact_finding(c, y, severity, color, title, body, framework, max_w):
    """Single condensed finding row. Returns new y."""
    pad = 10
    # left severity bar
    bar_x = M
    body_lines = wrap(body, "Helvetica", 9.5, max_w - 14)
    fw_lines = wrap(framework, "Helvetica-Oblique", 8, max_w - 14)
    title_h = 14
    body_h = len(body_lines) * 12
    fw_h = len(fw_lines) * 10
    block_h = pad + 16 + 2 + title_h + 4 + body_h + 4 + fw_h + pad

    # background
    c.setFillColor(CREAM)
    c.rect(bar_x + 4, y - block_h, max_w - 4, block_h, fill=1, stroke=0)
    # left color bar
    c.setFillColor(color)
    c.rect(bar_x, y - block_h, 4, block_h, fill=1, stroke=0)

    text_x = bar_x + 4 + pad
    # severity pill
    pill_y = y - pad - 14
    pill(c, text_x, pill_y, severity.upper(), color)
    # title
    c.setFillColor(INK)
    c.setFont("Times-Bold", 12)
    c.drawString(text_x, pill_y - title_h - 2, title)
    # body
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 9.5)
    yy = pill_y - title_h - 2 - 14
    for line in body_lines:
        c.drawString(text_x, yy, line)
        yy -= 12
    # framework
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica-Oblique", 8)
    yy -= 4
    for line in fw_lines:
        c.drawString(text_x, yy, line)
        yy -= 10

    return y - block_h - 8

# ---------- pages ----------
def page1(c):
    y = header_strip(c, 1)

    # Title row: big title left, score badge right
    c.setFillColor(INK)
    c.setFont("Times-Bold", 36)
    c.drawString(M, y - 28, "Your roast.")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 11)
    c.drawString(M, y - 46, "example-saas.com  -  5 things to fix first.")

    score_badge(c, PAGE_W - M - 2.0 * 72, y - 60, 2.0 * 72, 60)

    # Category bars
    cat_y = y - 90
    category_bars(c, M, cat_y, PAGE_W - 2 * M, [
        ("Heuristics",    5),
        ("Homepage",      7),
        ("UX writing",    6),
        ("UI design",     7),
        ("Accessibility", 5),
    ])

    # Findings section
    sec_y = cat_y - 30
    c.setFillColor(INK)
    c.setFont("Times-Bold", 16)
    c.drawString(M, sec_y, "What we would fix first")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 9.5)
    c.drawString(M, sec_y - 14,
                 "Five findings from the audit, ordered by impact. The full action list is on page 2.")

    # 5 findings
    yy = sec_y - 30
    max_w = PAGE_W - 2 * M
    findings = [
        ("High impact", CORAL,
         "Your headline tells, it doesn't show.",
         "\"All-in-one platform for teams\" is feature-led and vague. In the first 3 seconds, visitors do not know what problem you solve. Lead with the outcome - \"Ship product without weekly status meetings.\"",
         "C.L.E.A.R. Framework  -  Concise + Relevant"),
        ("High impact", CORAL,
         "Visibility of system status is weak.",
         "Form submissions do not confirm success or failure. Users click \"Sign up\" and wonder if anything happened - common cause of duplicate submissions and drop-off.",
         "Nielsen Heuristic #1  -  Visibility of system status"),
        ("High impact", CORAL,
         "Color contrast fails WCAG AA.",
         "Light gray on white (#A8A8A8 on #FFFFFF) is below the 4.5:1 ratio. Users with low vision and anyone reading outdoors on mobile will struggle. Darken to #595959 minimum.",
         "WCAG 2.1  -  Accessibility"),
        ("Medium", SUNSHINE,
         "Hero has four competing CTAs.",
         "Sign up, demo, watch video, contact sales - all primary-styled. Pick one. Single-CTA heroes outperform multi-CTA heroes by roughly 17%. Move the rest below the fold.",
         "C.L.E.A.R. Framework  -  Lucid"),
        ("Low effort win", MINT,
         "Strong social proof, hidden away.",
         "Customer logos and testimonials sit at the bottom. Move at least one trust signal above the fold - even a single \"Trusted by X teams\" line reduces first-impression friction.",
         "C.L.E.A.R. Framework  -  Reassuring"),
    ]
    for f in findings:
        yy = compact_finding(c, yy, *f, max_w=max_w)

    footer(c, 1, 2)

def page2(c):
    y = header_strip(c, 2)

    c.setFillColor(INK)
    c.setFont("Times-Bold", 30)
    c.drawString(M, y - 22, "Fix in this order.")
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 11)
    c.drawString(M, y - 40,
                 "Seven actions ranked by impact vs. effort. Start at the top - the wins compound.")

    actions = [
        ("1", "Rewrite the homepage headline",
         "HIGH IMPACT  -  LOW EFFORT",
         "Lead with the outcome users care about. Test 2-3 variants.", CORAL),
        ("2", "Surface one trust signal above the fold",
         "HIGH IMPACT  -  LOW EFFORT",
         "Customer logos or a testimonial - already designed, just move it.", CORAL),
        ("3", "Fix WCAG AA color contrast violations",
         "HIGH IMPACT  -  LOW EFFORT",
         "Darken body gray from #A8A8A8 to #595959. ~30 minutes of CSS.", CORAL),
        ("4", "Add inline form confirmation states",
         "HIGH IMPACT  -  MEDIUM EFFORT",
         "Replace silent submission with a success state and clear next step.", CORAL),
        ("5", "Cut the hero to one primary CTA",
         "MEDIUM IMPACT  -  LOW EFFORT",
         "Keep \"Start free trial\"; move others below the fold.", SUNSHINE),
        ("6", "Standardize the spacing scale",
         "MEDIUM IMPACT  -  MEDIUM EFFORT",
         "Lock to a 4- or 8-base spacing token across all components.", SUNSHINE),
        ("7", "Rewrite the generic CTA labels",
         "MEDIUM IMPACT  -  LOW EFFORT",
         "\"Submit\" -> \"Send my request\", etc. Specific verbs lift CTR 15-25%.", SUNSHINE),
    ]
    yy = y - 70
    for num, title, meta, desc, color in actions:
        # Number circle
        c.setFillColor(color)
        c.circle(M + 12, yy + 4, 13, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Times-Bold", 13)
        c.drawCentredString(M + 12, yy - 0, num)
        # Title
        c.setFillColor(INK)
        c.setFont("Times-Bold", 12)
        c.drawString(M + 32, yy + 8, title)
        # Meta
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(M + 32, yy - 6, meta)
        # Desc
        c.setFillColor(INK_SOFT)
        c.setFont("Helvetica", 9.5)
        c.drawString(M + 32, yy - 22, desc)
        yy -= 50

    # Closing note block
    box_y = yy - 8
    box_h = 1.5 * 72
    c.setFillColor(CREAM)
    c.roundRect(M, box_y - box_h, PAGE_W - 2 * M, box_h, 14, fill=1, stroke=0)

    c.setFillColor(INK)
    c.setFont("Times-Bold", 14)
    c.drawString(M + 16, box_y - 22, "A note before you go.")

    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 10)
    note_lines = [
        "These are the things we would fix first - not gospel, just the start of a conversation.",
        "Got a question on any finding? Reply to the email this came in. One round of clarifying",
        "questions is included, on the house. If a finding does not land for your business,",
        "ignore it - you know your users better than we do. Good luck out there.",
    ]
    ny = box_y - 38
    for line in note_lines:
        c.drawString(M + 16, ny, line)
        ny -= 13

    c.setFillColor(CORAL)
    c.setFont("Times-BoldItalic", 12)
    c.drawRightString(PAGE_W - M - 16, box_y - box_h + 14,
                      "- Your senior UX reviewer")

    footer(c, 2, 2)

# ---------- main ----------
def main():
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "sample-roast.pdf",
    )
    c = canvas.Canvas(out_path, pagesize=letter)
    c.setTitle("Sample Roast Report - example-saas.com")
    c.setAuthor("On Site Roast")
    c.setSubject("Sample UX audit (anonymized, 2 pages)")
    c.setCreator("On Site Roast")

    page1(c); c.showPage()
    page2(c); c.showPage()

    c.save()
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
