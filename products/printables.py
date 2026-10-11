"""Teacher & Homeschool printable bundle: 5 letter-size PDFs built with reportlab.
The sub plans and transcript use real fillable form fields."""
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

W, H = letter
INK, ACCENT, SOFT = HexColor("#1f2933"), HexColor("#2f6f5e"), HexColor("#e8f1ee")
M = 40


def header(c, title, sub=None):
    c.setFillColor(ACCENT)
    c.rect(0, H - 70, W, 70, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(M, H - 45, title)
    if sub:
        c.setFont("Helvetica", 10)
        c.drawString(M, H - 62, sub)
    c.setFillColor(INK)


def footer(c, text="Personal / classroom use. Print as many copies as you need."):
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HexColor("#6b7280"))
    c.drawCentredString(W / 2, 20, text)
    c.setFillColor(INK)


def field(c, name, x, y, w, h=16, multiline=False, size=10):
    c.acroForm.textfield(name=name, x=x, y=y, width=w, height=h, borderWidth=0.6,
                         borderColor=HexColor("#9ca3af"), fillColor=HexColor("#fafafa"),
                         textColor=INK, fontSize=size, forceBorder=True,
                         fieldFlags="multiline" if multiline else "")


def label(c, text, x, y, size=9, bold=True):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, text)


# ---------------------------------------------------------------- 1. Sub plans
def sub_plans(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    header(c, "Emergency Substitute Plans", "Fill in on screen or print. Keep a copy in the front office.")
    y = H - 100
    for i, (lab, w) in enumerate([("Teacher", 190), ("Grade / Subject", 150), ("Room", 90)]):
        pass
    label(c, "Teacher", M, y); field(c, "teacher", M, y - 20, 200)
    label(c, "Grade / Subject", M + 215, y); field(c, "grade", M + 215, y - 20, 150)
    label(c, "Room", M + 380, y); field(c, "room", M + 380, y - 20, 112)
    y -= 50
    label(c, "Office / Neighbor teacher", M, y); field(c, "office", M, y - 20, 240)
    label(c, "Phone / Ext.", M + 255, y); field(c, "phone", M + 255, y - 20, 237)
    y -= 50
    c.setFillColor(SOFT); c.rect(M, y - 6, W - 2 * M, 20, stroke=0, fill=1); c.setFillColor(INK)
    label(c, "DAILY SCHEDULE", M + 6, y, 10)
    y -= 26
    c.setFont("Helvetica-Bold", 8)
    for x, t in [(M, "Time"), (M + 85, "Subject / Activity"), (M + 300, "Instructions & materials")]:
        c.drawString(x, y, t)
    y -= 4
    for r in range(8):
        y -= 26
        field(c, f"t{r}", M, y, 80); field(c, f"a{r}", M + 85, y, 210); field(c, f"i{r}", M + 300, y, W - M - 300 - M)
    y -= 34
    for title, key, lines in [("Class routines (attendance, bathroom, dismissal)", "routines", 3),
                              ("Helpful students", "helpers", 2), ("Students with special needs / allergies", "needs", 2)]:
        label(c, title, M, y); y -= 4
        field(c, key, M, y - lines * 16, W - 2 * M, lines * 16, multiline=True); y -= lines * 16 + 22
    footer(c)
    c.showPage()
    # page 2: behavior + notes back to teacher
    header(c, "Substitute Plans - Page 2", "Emergency info, behavior plan and the sub's report back.")
    y = H - 100
    for title, key, h in [("Fire / lockdown procedures + meeting spot", "emerg", 60),
                          ("Behavior expectations & consequences", "behav", 60),
                          ("Where to find: lesson materials, seating chart, passes", "where", 50)]:
        label(c, title, M, y); y -= 4
        field(c, key, M, y - h, W - 2 * M, h, multiline=True); y -= h + 24
    c.setFillColor(SOFT); c.rect(M, y - 6, W - 2 * M, 20, stroke=0, fill=1); c.setFillColor(INK)
    label(c, "NOTES FOR THE TEACHER (substitute completes)", M + 6, y, 10)
    y -= 22
    for lab, key, h in [("Absent / tardy students", "absent", 40), ("Great helpers", "great", 40),
                        ("Behavior concerns", "concerns", 40), ("What got done / not done", "done", 60)]:
        label(c, lab, M, y); y -= 4
        field(c, key, M, y - h, W - 2 * M, h, multiline=True); y -= h + 20
    label(c, "Substitute name", M, y); field(c, "subname", M, y - 20, 240)
    label(c, "Date", M + 255, y); field(c, "subdate", M + 255, y - 20, 237)
    footer(c); c.save()


# ---------------------------------------------------------------- 2. Behavior charts
def behavior(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    # Page 1: weekly chart for one student
    header(c, "Weekly Behavior Chart", "Rate each period: 3 = great  2 = okay  1 = needs work")
    label(c, "Name: ______________________________", M, H - 100, 11)
    label(c, "Week of: ____________________", M + 330, H - 100, 11)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    goals = ["Followed directions", "Kept hands to self", "Used kind words", "Stayed on task", "Finished work", "Ready to learn"]
    x0, y0, cw, rh = M, H - 135, 85, 48
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(ACCENT); c.rect(x0, y0 - rh + 12, 150 + 5 * 64, rh - 12, stroke=0, fill=1); c.setFillColor(white)
    c.drawString(x0 + 8, y0 - 18, "My goals")
    for i, d in enumerate(days):
        c.drawCentredString(x0 + 150 + i * 64 + 32, y0 - 18, d)
    c.setFillColor(INK)
    for r, g in enumerate(goals):
        y = y0 - 80 - r * rh
        if r % 2 == 0:
            c.setFillColor(SOFT); c.rect(x0, y - 4, 150 + 5 * 64, rh, stroke=0, fill=1); c.setFillColor(INK)
        c.setFont("Helvetica", 10); c.drawString(x0 + 8, y + 18, g)
        for i in range(5):
            c.setStrokeColor(HexColor("#9ca3af")); c.circle(x0 + 150 + i * 64 + 32, y + 22, 15)
    c.setStrokeColor(INK)
    y = y0 - 80 - len(goals) * rh - 6
    label(c, "Daily reward goal: _____ points  |  Weekly reward: _________________________________", M, y, 10)
    label(c, "Teacher / parent comments", M, y - 28, 10)
    c.rect(M, y - 120, W - 2 * M, 80)
    footer(c); c.showPage()
    # Page 2: sticker / star chart
    header(c, "Star Reward Chart", "Color or sticker one star each time a goal is met.")
    label(c, "Name: ______________________    Goal: _________________________________", M, H - 100, 11)
    import math
    for row in range(8):
        for col in range(5):
            cx, cy = M + 50 + col * 95, H - 170 - row * 80
            pts = []
            for k in range(10):
                r = 28 if k % 2 == 0 else 12
                a = math.pi / 2 + k * math.pi / 5
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            p = c.beginPath(); p.moveTo(*pts[0])
            for q in pts[1:]: p.lineTo(*q)
            p.close(); c.setStrokeColor(ACCENT); c.setLineWidth(1.2); c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(INK); c.setLineWidth(1)
    label(c, "When all stars are earned, we celebrate with: ______________________________________", M, 50, 10)
    footer(c); c.save()


# ---------------------------------------------------------------- 3. Homeschool morning menu
def morning_menu(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    header(c, "Our Morning Menu", "Choose, do, and check off. Start your day on purpose.")
    sections = [("Must Do (the basics)", ["Make bed & get dressed", "Breakfast + brush teeth", "Morning chores", "Read-aloud / Bible / calendar time"]),
                ("Pick 2 (brain warm-ups)", ["Copywork or journaling", "Math facts practice", "Nature walk or stretching", "Silent reading (20 min)", "Memory work / poetry", "Music or art study"]),
                ("Pick 1 (kind & creative)", ["Write a thank-you note", "Draw something from the window", "Build with blocks or LEGO", "Help cook something", "Learn 5 words in a new language"])]
    y = H - 105
    for title, items in sections:
        c.setFillColor(SOFT); c.roundRect(M, y - 8, W - 2 * M, 24, 6, stroke=0, fill=1); c.setFillColor(INK)
        label(c, title, M + 10, y, 12); y -= 30
        for it in items:
            c.setStrokeColor(ACCENT); c.setLineWidth(1.4); c.roundRect(M + 8, y - 2, 13, 13, 3)
            c.setFont("Helvetica", 11); c.drawString(M + 32, y, it); y -= 24
        y -= 12
    c.setLineWidth(1); c.setStrokeColor(INK)
    label(c, "Today I am looking forward to: ___________________________________________", M, y, 10)
    label(c, "Date: ______________      Name: ______________________", M, y - 24, 10)
    footer(c); c.showPage()
    # Page 2: blank editable-by-hand menu
    header(c, "Morning Menu - Make Your Own", "Write your family's choices, then print copies for each child.")
    y = H - 110
    for title in ["Must Do", "Pick 2", "Pick 1", "Bonus"]:
        label(c, title, M, y, 12); y -= 8
        for _ in range(5 if title != "Bonus" else 3):
            c.line(M + 22, y - 12, W - M, y - 12); c.roundRect(M, y - 10, 13, 13, 3); y -= 26
        y -= 14
    footer(c); c.save()


# ---------------------------------------------------------------- 4. Attendance tracker
def attendance(path):
    c = canvas.Canvas(str(path), pagesize=(letter[1], letter[0]))
    PW, PH = letter[1], letter[0]
    for month in ["August / September", "October", "November", "December", "January", "February", "March", "April", "May / June"]:
        c.setFillColor(ACCENT); c.rect(0, PH - 60, PW, 60, stroke=0, fill=1); c.setFillColor(white)
        c.setFont("Helvetica-Bold", 20); c.drawString(M, PH - 38, f"Attendance - {month}")
        c.setFont("Helvetica", 9); c.drawString(M, PH - 52, "P = present   A = absent   T = tardy   E = excused   (circle weekends & holidays)")
        c.setFillColor(INK)
        x0, y0, nw, dw, rh = M, PH - 85, 130, 15.5, 17.6
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x0 + 3, y0 - 8, "Student")
        for d in range(31):
            c.drawCentredString(x0 + nw + d * dw + dw / 2, y0 - 8, str(d + 1))
        c.drawCentredString(x0 + nw + 31 * dw + 18, y0 - 8, "Abs")
        for r in range(28):
            y = y0 - 14 - r * rh
            if r % 2 == 0:
                c.setFillColor(SOFT); c.rect(x0, y - rh + 4, nw + 31 * dw + 36, rh, stroke=0, fill=1); c.setFillColor(INK)
            c.setStrokeColor(HexColor("#d1d5db")); c.setLineWidth(0.4)
            c.line(x0, y - rh + 4, x0 + nw + 31 * dw + 36, y - rh + 4)
        for d in range(32):
            xx = x0 + nw + d * dw
            c.line(xx, y0 - 14 + rh - 6 - 6, xx, y0 - 14 - 27 * rh - rh + 4)
        c.setStrokeColor(INK); c.setLineWidth(1)
        footer_text = "Personal / classroom use. Print as many copies as you need."
        c.setFont("Helvetica", 7.5); c.setFillColor(HexColor("#6b7280")); c.drawCentredString(PW / 2, 14, footer_text); c.setFillColor(INK)
        c.showPage()
    c.save()


# ---------------------------------------------------------------- 5. Homeschool transcript
def transcript(path):
    c = canvas.Canvas(str(path), pagesize=letter)
    header(c, "Homeschool High School Transcript", "Fillable. Type, save, print. GPA scale: A=4  B=3  C=2  D=1  F=0")
    y = H - 100
    label(c, "Student name", M, y); field(c, "student", M, y - 20, 220)
    label(c, "Date of birth", M + 235, y); field(c, "dob", M + 235, y - 20, 110)
    label(c, "Graduation date", M + 360, y); field(c, "grad", M + 360, y - 20, 132)
    y -= 48
    label(c, "School / Parent-teacher name", M, y); field(c, "school", M, y - 20, 320)
    label(c, "Address", M + 335, y); field(c, "addr", M + 335, y - 20, 157)
    y -= 56
    for yr, n in [("9th Grade", 1), ("10th Grade", 2)]:
        c.setFillColor(SOFT); c.rect(M, y - 6, W - 2 * M, 20, stroke=0, fill=1); c.setFillColor(INK)
        label(c, f"{yr}   Year: ", M + 6, y, 10); field(c, f"year{n}", M + 90, y - 4, 70, 14, size=9)
        y -= 20
        c.setFont("Helvetica-Bold", 8)
        for x, t in [(M, "Course"), (M + 280, "Credits"), (M + 340, "Grade"), (M + 400, "Points")]:
            c.drawString(x, y, t)
        for r in range(6):
            y -= 20
            field(c, f"c{n}_{r}", M, y, 270, 15, size=9); field(c, f"cr{n}_{r}", M + 280, y, 50, 15, size=9)
            field(c, f"g{n}_{r}", M + 340, y, 50, 15, size=9); field(c, f"p{n}_{r}", M + 400, y, 50, 15, size=9)
        y -= 34
    footer(c); c.showPage()
    header(c, "Homeschool High School Transcript - Page 2")
    y = H - 100
    for yr, n in [("11th Grade", 3), ("12th Grade", 4)]:
        c.setFillColor(SOFT); c.rect(M, y - 6, W - 2 * M, 20, stroke=0, fill=1); c.setFillColor(INK)
        label(c, f"{yr}   Year: ", M + 6, y, 10); field(c, f"year{n}", M + 90, y - 4, 70, 14, size=9)
        y -= 20
        c.setFont("Helvetica-Bold", 8)
        for x, t in [(M, "Course"), (M + 280, "Credits"), (M + 340, "Grade"), (M + 400, "Points")]:
            c.drawString(x, y, t)
        for r in range(6):
            y -= 20
            field(c, f"c{n}_{r}", M, y, 270, 15, size=9); field(c, f"cr{n}_{r}", M + 280, y, 50, 15, size=9)
            field(c, f"g{n}_{r}", M + 340, y, 50, 15, size=9); field(c, f"p{n}_{r}", M + 400, y, 50, 15, size=9)
        y -= 34
    label(c, "Cumulative GPA", M, y); field(c, "gpa", M, y - 20, 90)
    label(c, "Total credits", M + 110, y); field(c, "credits", M + 110, y - 20, 90)
    label(c, "Parent / administrator signature", M + 230, y); field(c, "sig", M + 230, y - 20, 262)
    y -= 56
    label(c, "Activities, honors, volunteer work", M, y); y -= 4
    field(c, "extras", M, y - 70, W - 2 * M, 70, multiline=True)
    footer(c); c.save()


# ======================================================================
# Data-driven packs (used by the weekly ideator). Spec types: table, weekly, seating
# ======================================================================
DAYS5 = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DAYS7 = DAYS5 + ["Sat", "Sun"]


def _new(path, landscape):
    c = canvas.Canvas(str(path), pagesize=(letter[1], letter[0]) if landscape else letter)
    return c, (letter[1], letter[0]) if landscape else (W, H)


def _head(c, pw, ph, title, sub):
    c.setFillColor(ACCENT); c.rect(0, ph - 70, pw, 70, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 22); c.drawString(M, ph - 45, title)
    if sub:
        c.setFont("Helvetica", 10); c.drawString(M, ph - 62, sub)
    c.setFillColor(INK)


def _foot(c, pw):
    c.setFont("Helvetica", 7.5); c.setFillColor(HexColor("#6b7280"))
    c.drawCentredString(pw / 2, 16, "Personal / classroom use. Print as many copies as you need."); c.setFillColor(INK)


def table_pdf(path, spec):
    land = spec.get("landscape", False)
    c, (pw, ph) = _new(path, land)
    cols, nrows, fill = spec["cols"], spec.get("rows", 20), spec.get("fillable", False)
    avail = pw - 2 * M
    tot = sum(w for _, w in cols)
    widths_ = [avail * w / tot for _, w in cols]
    pages = spec.get("pages", 1)
    for pg in range(pages):
        _head(c, pw, ph, spec["title"], spec.get("sub"))
        y = ph - 92
        for i, hf in enumerate(spec.get("header_fields", [])):
            x = M + i * (avail / max(len(spec["header_fields"]), 1))
            label(c, hf + ":", x, y, 10)
            c.line(x + 6 + len(hf) * 6, y - 2, x + avail / len(spec["header_fields"]) - 14, y - 2)
        y -= 22 if spec.get("header_fields") else 0
        rh = min(28, (y - 42) / (nrows + 1))
        x = M
        c.setFillColor(ACCENT); c.rect(M, y - rh, avail, rh, stroke=0, fill=1); c.setFillColor(white); c.setFont("Helvetica-Bold", 8.5)
        for (name, _), w in zip(cols, widths_):
            c.drawString(x + 4, y - rh + rh / 2 - 3, name); x += w
        c.setFillColor(INK)
        for r in range(nrows):
            top = y - rh * (r + 1)
            if r % 2 == 0:
                c.setFillColor(SOFT); c.rect(M, top - rh, avail, rh, stroke=0, fill=1); c.setFillColor(INK)
            c.setStrokeColor(HexColor("#cfd4d1")); c.setLineWidth(0.4); c.line(M, top - rh, M + avail, top - rh)
            x = M
            for ci, w in enumerate(widths_):
                c.line(x, top, x, top - rh)
                if fill:
                    field(c, f"f{pg}_{r}_{ci}", x + 1.5, top - rh + 1.5, w - 3, rh - 3, size=8)
                x += w
            c.line(x, top, x, top - rh)
        c.setStrokeColor(INK); c.setLineWidth(1)
        _foot(c, pw)
        c.showPage()
    c.save()


def weekly_pdf(path, spec):
    land = True
    c, (pw, ph) = _new(path, land)
    days = spec.get("days", DAYS7)
    _head(c, pw, ph, spec["title"], spec.get("sub"))
    y = ph - 92
    label(c, "Name: ____________________________", M, y, 10); label(c, "Week of: ________________", M + 300, y, 10)
    y -= 14
    rows = spec["rows"]
    lw = 110
    cw = (pw - 2 * M - lw) / len(days)
    rh = min(60, (y - 40) / (len(rows) + 1))
    c.setFillColor(ACCENT); c.rect(M, y - 24, pw - 2 * M, 24, stroke=0, fill=1); c.setFillColor(white); c.setFont("Helvetica-Bold", 10)
    for i, d in enumerate(days):
        c.drawCentredString(M + lw + i * cw + cw / 2, y - 16, d)
    c.setFillColor(INK)
    for r, name in enumerate(rows):
        top = y - 24 - r * rh
        if r % 2 == 0:
            c.setFillColor(SOFT); c.rect(M, top - rh, pw - 2 * M, rh, stroke=0, fill=1); c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9); c.drawString(M + 5, top - rh / 2 - 3, name)
        c.setStrokeColor(HexColor("#cfd4d1")); c.setLineWidth(0.4)
        c.line(M, top - rh, pw - M, top - rh)
        for i in range(len(days) + 1):
            xx = M + lw + i * cw
            c.line(xx, top, xx, top - rh)
        if spec.get("checks"):
            for i in range(len(days)):
                c.setStrokeColor(ACCENT); c.setLineWidth(1.2)
                c.roundRect(M + lw + i * cw + cw / 2 - 7, top - rh / 2 - 7, 14, 14, 3)
    c.setStrokeColor(INK); c.setLineWidth(1)
    _foot(c, pw); c.showPage(); c.save()


def seating_pdf(path, spec):
    c, (pw, ph) = _new(path, True)
    _head(c, pw, ph, spec["title"], spec.get("sub"))
    cols, rows = spec.get("cols", 6), spec.get("rows", 5)
    avail_w, avail_h = pw - 2 * M, ph - 150
    bw, bh = avail_w / cols, avail_h / rows
    c.setFillColor(SOFT); c.roundRect(pw / 2 - 90, ph - 100, 180, 20, 6, stroke=0, fill=1); c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9); c.drawCentredString(pw / 2, ph - 94, "FRONT OF ROOM / BOARD")
    for r in range(rows):
        for k in range(cols):
            x, y = M + k * bw + 5, ph - 112 - (r + 1) * bh + 5
            c.setStrokeColor(ACCENT); c.setLineWidth(1); c.roundRect(x, y, bw - 10, bh - 10, 6)
            field(c, f"s{r}_{k}", x + 6, y + (bh - 10) / 2 - 8, bw - 22, 16, size=9)
    c.setStrokeColor(INK)
    _foot(c, pw); c.showPage(); c.save()


RENDER = {"table": table_pdf, "weekly": weekly_pdf, "seating": seating_pdf}

PACKS = {
    "classroom_organizers": {
        "name": "Classroom Organizer Printable Bundle", "price": 16,
        "buyer": "classroom teachers who want planning, reading and parent-contact forms in one place",
        "angle": "Five editable-or-printable forms: weekly lesson planner, classroom jobs chart, reading log, student skills tracker and parent communication log.",
        "keywords": ["lesson plan template", "classroom jobs chart", "reading log printable", "parent communication log", "teacher organizer"],
        "files": {
            "1_Weekly_Lesson_Planner.pdf": ("table", dict(title="Weekly Lesson Planner", sub="Fillable. Type, save, print.", landscape=True, header_fields=["Teacher", "Week of", "Grade"], cols=[("Subject / Time", 1.6)] + [(d, 2) for d in DAYS5] + [("Notes", 1.6)], rows=8, fillable=True)),
            "2_Classroom_Jobs_Chart.pdf": ("table", dict(title="Classroom Jobs Chart", sub="Rotate weekly so every student gets a turn.", header_fields=["Class", "Month"], cols=[("Job", 2.2), ("What it involves", 3), ("Week 1", 1.5), ("Week 2", 1.5), ("Week 3", 1.5), ("Week 4", 1.5)], rows=14, fillable=True)),
            "3_Reading_Log.pdf": ("table", dict(title="Weekly Reading Log", sub="Read every day. Record it here.", header_fields=["Name", "Month"], cols=[("Date", 1.2), ("Title", 3.5), ("Pages", 1), ("Minutes", 1), ("Parent initials", 1.3)], rows=22)),
            "4_Student_Skills_Tracker.pdf": ("table", dict(title="Student Skills Tracker", sub="Mark: M = mastered, P = practicing, N = not yet.", landscape=True, header_fields=["Class", "Subject"], cols=[("Student", 2.6)] + [(f"Skill {i}", 1) for i in range(1, 9)] + [("Notes", 2)], rows=26, fillable=True)),
            "5_Parent_Communication_Log.pdf": ("table", dict(title="Parent Communication Log", sub="Keep a record of every contact.", landscape=True, header_fields=["School year"], cols=[("Date", 1.1), ("Student", 1.8), ("Contact", 1.8), ("Method", 1.2), ("Topic / summary", 4), ("Follow-up", 1.8)], rows=20, fillable=True)),
        }},
    "family_home": {
        "name": "Family Home Organizer Printable Bundle", "price": 14,
        "buyer": "busy families who want chores, meals and money lessons organised on paper",
        "angle": "Five printable pages: weekly chore chart, meal planner, family schedule, allowance tracker and grocery list.",
        "keywords": ["chore chart printable", "weekly meal planner", "family schedule printable", "allowance tracker", "family organizer"],
        "files": {
            "1_Weekly_Chore_Chart.pdf": ("weekly", dict(title="Weekly Chore Chart", sub="Check off each chore when it's done.", rows=["Make bed", "Tidy room", "Set table", "Clear dishes", "Feed pet", "Take out trash", "Laundry help", "Homework done"], days=DAYS7, checks=True)),
            "2_Weekly_Meal_Planner.pdf": ("weekly", dict(title="Weekly Meal Planner", sub="Plan once, shop once.", rows=["Breakfast", "Lunch", "Dinner", "Snack"], days=DAYS7)),
            "3_Family_Schedule.pdf": ("weekly", dict(title="Family Schedule", sub="Who is where, and when.", rows=["Mom", "Dad", "Child 1", "Child 2", "Child 3", "Reminders"], days=DAYS7)),
            "4_Allowance_Savings_Tracker.pdf": ("table", dict(title="Allowance & Savings Tracker", sub="Teach saving, spending and giving.", header_fields=["Name", "Weekly allowance"], cols=[("Date", 1.2), ("What for", 3), ("Earned", 1.2), ("Spent", 1.2), ("Saved", 1.2), ("Balance", 1.4)], rows=24, fillable=True)),
            "5_Grocery_List.pdf": ("table", dict(title="Grocery List", sub="Sort by store section to shop faster.", cols=[("Done", 0.8), ("Item", 4), ("Qty", 1), ("Section", 2)], rows=28, fillable=True)),
        }},
    "homeschool_year": {
        "name": "Homeschool Year Planner & Records Bundle", "price": 22,
        "buyer": "homeschool parents who need yearly planning and clear records",
        "angle": "Five fillable forms: year-at-a-glance, subject log, field trip log, books-read log and instructional hours log.",
        "keywords": ["homeschool planner", "homeschool records", "field trip log", "homeschool hours log", "books read log"],
        "files": {
            "1_Year_At_A_Glance.pdf": ("table", dict(title="Homeschool Year at a Glance", sub="Fillable. Plan your goals by month.", landscape=True, header_fields=["Student", "School year"], cols=[("Month", 1.4), ("Math", 2), ("Language Arts", 2), ("Science", 2), ("History / Social", 2), ("Other", 2), ("Field trips / events", 2)], rows=12, fillable=True)),
            "2_Subject_Weekly_Log.pdf": ("table", dict(title="Subject Weekly Log", sub="Record what you covered each day.", landscape=True, header_fields=["Student", "Week of"], cols=[("Subject", 2)] + [(d, 2.2) for d in DAYS5] + [("Hours", 1)], rows=8, fillable=True)),
            "3_Field_Trip_Log.pdf": ("table", dict(title="Field Trip & Experience Log", sub="Great for portfolios and records.", header_fields=["Student"], cols=[("Date", 1.2), ("Place", 2.5), ("Subject link", 2), ("What we learned", 4)], rows=18, fillable=True)),
            "4_Books_Read_Log.pdf": ("table", dict(title="Books Read Log", sub="Keep a running list for the year.", header_fields=["Student", "Year"], cols=[("Date finished", 1.4), ("Title", 3.5), ("Author", 2.4), ("Rating (1-5)", 1.2)], rows=26, fillable=True)),
            "5_Instructional_Hours_Log.pdf": ("table", dict(title="Instructional Hours Log", sub="Check your state's requirements; this tracks the totals.", header_fields=["Student", "Year"], cols=[("Month", 1.6), ("Days taught", 1.4), ("Hours taught", 1.4), ("Running total", 1.6), ("Notes", 3)], rows=12, fillable=True)),
        }},
    "teacher_binder": {
        "name": "Teacher Binder Essentials Printable Bundle", "price": 17,
        "buyer": "teachers building a back-to-school binder",
        "angle": "Five binder pages: fillable seating chart, hall pass log, missing assignments tracker, class roster and meeting notes.",
        "keywords": ["teacher binder", "seating chart template", "hall pass log", "missing assignment tracker", "class roster"],
        "files": {
            "1_Seating_Chart.pdf": ("seating", dict(title="Seating Chart", sub="Fillable. Type names, save, print.", cols=6, rows=5)),
            "2_Hall_Pass_Log.pdf": ("table", dict(title="Hall Pass Log", sub="Track who leaves and when.", header_fields=["Class", "Date"], cols=[("Student", 3), ("Destination", 2), ("Time out", 1.2), ("Time in", 1.2), ("Initials", 1)], rows=22, fillable=True)),
            "3_Missing_Assignments_Tracker.pdf": ("table", dict(title="Missing Assignments Tracker", sub="Check when turned in.", landscape=True, header_fields=["Class", "Quarter"], cols=[("Student", 3)] + [(f"Assign {i}", 1.1) for i in range(1, 11)] + [("Notes", 2)], rows=26, fillable=True)),
            "4_Class_Roster.pdf": ("table", dict(title="Class Roster & Contacts", sub="Keep private; store securely.", header_fields=["Class", "Year"], cols=[("#", 0.5), ("Student", 3), ("Guardian", 3), ("Phone / Email", 3), ("Notes", 3)], rows=28, fillable=True)),
            "5_Meeting_Notes.pdf": ("table", dict(title="Meeting Notes", sub="Parent, team and IEP/504 meeting notes.", header_fields=["Date", "Attendees"], cols=[("Topic", 3), ("Discussion", 5), ("Action / owner", 3), ("Due", 1.2)], rows=14, fillable=True)),
        }},
}


def build_pack(outdir, cfg, brief):
    pack = PACKS[cfg["pack"]]
    outdir = Path(outdir)
    for fname, (kind, spec) in pack["files"].items():
        RENDER[kind](outdir / fname, spec)
    listing = "\n".join(f"{n} - {s['title']}" + (" (fillable)" if s.get("fillable") or k == "seating" else "") for n, (k, s) in pack["files"].items())
    (outdir / "README.txt").write_text(f"{pack['name'].upper()}\n\n{listing}\n\nPrint at 100% / Actual size on US Letter. Fillable files open in Adobe Reader, Preview or any browser: type, save, print. Personal and classroom use.\n")
    return sorted(p for p in outdir.iterdir() if p.is_file())


FILES = {
    "1_Emergency_Sub_Plans.pdf": sub_plans,
    "2_Behavior_Charts.pdf": behavior,
    "3_Homeschool_Morning_Menu.pdf": morning_menu,
    "4_Attendance_Tracker.pdf": attendance,
    "5_Homeschool_Transcript.pdf": transcript,
}


def build(outdir, cfg, brief):
    if cfg.get("pack"):
        return build_pack(outdir, cfg, brief)
    outdir = Path(outdir)
    for name, fn in FILES.items():
        fn(outdir / name)
    (outdir / "README.txt").write_text(
        "TEACHER & HOMESCHOOL ESSENTIALS BUNDLE\n\n"
        "1_Emergency_Sub_Plans.pdf   - fillable (open in Adobe Reader, Preview or a browser, type, save)\n"
        "2_Behavior_Charts.pdf       - weekly chart + star reward chart (print)\n"
        "3_Homeschool_Morning_Menu.pdf - ready-made menu + blank menu (print)\n"
        "4_Attendance_Tracker.pdf    - 9 landscape monthly sheets, 28 students (print)\n"
        "5_Homeschool_Transcript.pdf - fillable 4-year transcript with GPA scale\n\n"
        "Print at 100% / Actual size on US Letter. Personal and classroom use.\n"
    )
    return sorted(p for p in outdir.iterdir() if p.is_file())


def validate(outdir):
    from pypdf import PdfReader
    problems, outdir = [], Path(outdir)
    pdfs = sorted(outdir.glob("*.pdf"))
    if len(pdfs) < 5:
        problems.append(f"expected 5 PDFs, found {len(pdfs)}")
    for f in pdfs:
        if f.stat().st_size < 2000:
            problems.append(f"{f.name} tiny")
            continue
        r = PdfReader(str(f))
        if len(r.pages) < 1:
            problems.append(f"{f.name} has no pages")
        if f.name.startswith(("1_Emergency", "5_Homeschool_Transcript")) and not r.get_fields():
            problems.append(f"{f.name} should be fillable but has no form fields")
    return problems
