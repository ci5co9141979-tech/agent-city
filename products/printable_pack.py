"""Generic printable pack builder (spec-driven) with a small library of page types."""
import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .printables import ACCENT, INK, SOFT, M, footer, header, label

W, H = letter
GREY = HexColor("#9ca3af")


def name_date(c, y=None):
    y = y or H - 98
    c.setFont("Helvetica-Bold", 10)
    c.drawString(M, y, "Name: ______________________________")
    c.drawString(W - M - 190, y, "Date: ____________________")
    return y - 22


def p_log(c, p):
    header(c, p["title"], p.get("sub"))
    y = name_date(c) - 4
    cols = p["cols"]  # [(name, weight)]
    tw = sum(w for _, w in cols)
    widths = [(W - 2 * M) * w / tw for _, w in cols]
    c.setFillColor(ACCENT); c.rect(M, y - 22, W - 2 * M, 22, stroke=0, fill=1); c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.5)
    x = M
    for (n, _), wd in zip(cols, widths):
        c.drawString(x + 4, y - 15, n); x += wd
    c.setFillColor(INK)
    rows = p.get("rows", 22)
    rh = (y - 22 - 50) / rows
    for r in range(rows):
        yy = y - 22 - (r + 1) * rh
        if r % 2 == 0:
            c.setFillColor(SOFT); c.rect(M, yy, W - 2 * M, rh, stroke=0, fill=1); c.setFillColor(INK)
        c.setStrokeColor(HexColor("#d1d5db")); c.setLineWidth(0.5); c.line(M, yy, W - M, yy)
    x = M
    for wd in widths[:-1]:
        x += wd
        c.line(x, y - 22, x, y - 22 - rows * rh)
    c.setStrokeColor(INK)
    footer(c); c.showPage()


def p_checklist(c, p):
    header(c, p["title"], p.get("sub"))
    y = name_date(c) - 8
    for sec in p["sections"]:
        if y < 110:
            footer(c); c.showPage(); header(c, p["title"] + " (cont.)"); y = H - 100
        c.setFillColor(SOFT); c.roundRect(M, y - 6, W - 2 * M, 22, 5, stroke=0, fill=1); c.setFillColor(INK)
        label(c, sec["h"], M + 8, y, 11); y -= 28
        for it in sec["items"]:
            c.setStrokeColor(ACCENT); c.setLineWidth(1.3); c.roundRect(M + 8, y - 2, 13, 13, 3)
            c.setFont("Helvetica", 11); c.drawString(M + 32, y, it); y -= 23
        y -= 12
    c.setStrokeColor(INK); c.setLineWidth(1)
    footer(c); c.showPage()


def p_grid(c, p):
    """items (rows) x columns (days or custom)."""
    header(c, p["title"], p.get("sub"))
    y = name_date(c) - 6
    cols = p["cols"]
    items = p["items"]
    lw = 180
    cw = min(60 if p.get("circles", True) else 110, (W - 2 * M - lw) / len(cols))
    rows = max(len(items), p.get("min_rows", 0))
    rh = min(46, (y - 70) / (rows + 1))
    c.setFillColor(ACCENT); c.rect(M, y - rh, lw + cw * len(cols), rh, stroke=0, fill=1); c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M + 8, y - rh / 2 - 3, p.get("first", "Task"))
    for i, col in enumerate(cols):
        c.drawCentredString(M + lw + cw * i + cw / 2, y - rh / 2 - 3, str(col))
    c.setFillColor(INK)
    for r in range(rows):
        yy = y - rh * (r + 2)
        if r % 2 == 0:
            c.setFillColor(SOFT); c.rect(M, yy, lw + cw * len(cols), rh, stroke=0, fill=1); c.setFillColor(INK)
        if r < len(items):
            c.setFont("Helvetica", 10); c.drawString(M + 8, yy + rh / 2 - 3, items[r])
        c.setStrokeColor(GREY); c.setLineWidth(0.6)
        for i in range(len(cols)):
            cx = M + lw + cw * i + cw / 2
            if p.get("circles", True):
                c.circle(cx, yy + rh / 2, min(11, rh / 2 - 3))
            else:
                c.rect(cx - cw / 2 + 2, yy + 2, cw - 4, rh - 4)
    c.setStrokeColor(INK); c.setLineWidth(1)
    footer(c); c.showPage()


def p_seating(c, p):
    header(c, p["title"], p.get("sub"))
    name_date(c)
    rows, cols = p.get("rows", 5), p.get("cols", 6)
    gx, gy = (W - 2 * M) / cols, (H - 260) / rows
    c.setFillColor(SOFT); c.roundRect(W / 2 - 80, H - 150, 160, 28, 6, stroke=0, fill=1); c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10); c.drawCentredString(W / 2, H - 140, "FRONT / TEACHER DESK")
    for r in range(rows):
        for k in range(cols):
            x, y = M + k * gx + 5, H - 190 - (r + 1) * gy + 8
            c.setStrokeColor(ACCENT); c.setLineWidth(1); c.roundRect(x, y, gx - 10, gy - 16, 6)
    c.setStrokeColor(INK)
    footer(c); c.showPage()


def p_lined(c, p):
    header(c, p["title"], p.get("sub"))
    y = name_date(c)
    for prompt in p.get("prompts", []):
        label(c, prompt, M, y - 6, 10); y -= 28
        for _ in range(p.get("lines_each", 3)):
            c.setStrokeColor(GREY); c.setLineWidth(0.6); c.line(M, y, W - M, y); y -= 24
        y -= 8
    c.setStrokeColor(INK)
    while y > 70 and p.get("fill", True) and not p.get("prompts"):
        c.setStrokeColor(GREY); c.setLineWidth(0.6); c.line(M, y, W - M, y); y -= 26
    footer(c); c.showPage()


def p_month(c, p):
    header(c, p["title"], p.get("sub"))
    c.setFont("Helvetica-Bold", 11); c.drawString(M, H - 96, "Month: ____________________    Year: ________")
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    cw, top = (W - 2 * M) / 7, H - 112
    rh = (top - 70) / 6
    c.setFillColor(ACCENT); c.rect(M, top - 20, W - 2 * M, 20, stroke=0, fill=1); c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    for i, d in enumerate(days):
        c.drawCentredString(M + cw * i + cw / 2, top - 14, d)
    c.setStrokeColor(GREY); c.setLineWidth(0.6)
    for r in range(6):
        for k in range(7):
            c.rect(M + k * cw, top - 20 - (r + 1) * rh, cw, rh)
    c.setStrokeColor(INK)
    footer(c); c.showPage()


def p_weekly(c, p):
    header(c, p["title"], p.get("sub"))
    y = name_date(c) - 4
    days = p.get("days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    rows = p["rows"]
    lw = 105
    cw = (W - 2 * M - lw) / len(days)
    rh = (y - 70) / (len(rows) + 1)
    c.setFillColor(ACCENT); c.rect(M, y - 24, W - 2 * M, 24, stroke=0, fill=1); c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(M + 8, y - 16, p.get("first", "Subject"))
    for i, d in enumerate(days):
        c.drawCentredString(M + lw + cw * i + cw / 2, y - 16, d)
    c.setFillColor(INK)
    rh = (y - 24 - 96) / len(rows)
    for r, name in enumerate(rows):
        yy = y - 24 - (r + 1) * rh
        if r % 2 == 0:
            c.setFillColor(SOFT); c.rect(M, yy, W - 2 * M, rh, stroke=0, fill=1); c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.5); c.drawString(M + 8, yy + rh / 2 - 3, name)
        c.setStrokeColor(GREY); c.setLineWidth(0.5)
        for k in range(len(days) + 1):
            c.line(M + lw + cw * k if k else M + lw, yy, M + lw + cw * k if k else M + lw, yy + rh)
        c.line(M, yy, W - M, yy)
    c.setStrokeColor(INK)
    label(c, p.get("footer_label", "Notes / reminders"), M, 74, 9)
    c.setStrokeColor(GREY); c.line(M, 50, W - M, 50); c.line(M, 62, W - M, 62)
    footer(c); c.showPage()


PAGE_TYPES = {"log": p_log, "checklist": p_checklist, "grid": p_grid, "seating": p_seating,
              "lined": p_lined, "month": p_month, "weekly": p_weekly}


def build(outdir, cfg, brief):
    spec, outdir = cfg["spec"], Path(outdir)
    for f in spec["files"]:
        c = canvas.Canvas(str(outdir / f["file"]), pagesize=letter)
        c.setTitle(f["file"].rsplit(".", 1)[0].replace("_", " "))
        for page in f["pages"]:
            PAGE_TYPES[page["type"]](c, page)
        c.save()
    (outdir / "README.txt").write_text(
        f"{spec['pack_name'].upper()}\n\n" + "\n".join(f"{f['file']} - {len(f['pages'])} page(s)" for f in spec["files"])
        + "\n\nPrint at 100% / Actual size on US Letter. Personal and classroom/homeschool use.\n")
    return sorted(p for p in outdir.iterdir() if p.is_file())


def validate(outdir, cfg=None):
    from pypdf import PdfReader
    spec = cfg["spec"] if cfg else None
    outdir, problems = Path(outdir), []
    pdfs = sorted(outdir.glob("*.pdf"))
    if not pdfs:
        return ["no PDFs"]
    for f in pdfs:
        r = PdfReader(str(f))
        text = " ".join((pg.extract_text() or "") for pg in r.pages)
        if f.stat().st_size < 1500 or not r.pages:
            problems.append(f"{f.name} empty")
        elif len(text.strip()) < 20:
            problems.append(f"{f.name} has no text")
    if spec:
        want = {f["file"]: len(f["pages"]) for f in spec["files"]}
        for n, pages in want.items():
            f = outdir / n
            if f.exists() and len(PdfReader(str(f)).pages) < pages:
                problems.append(f"{n}: page overflow/underflow")
    return problems
