"""Small Business Content & Planning Vault: .xlsx (Google Sheets compatible),
Notion-importable CSVs, and a caption kit."""
import csv
import datetime as dt
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

GREEN, SOFT, INK = "2F6F5E", "E8F1EE", "1F2933"
HEAD = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
HFILL = PatternFill("solid", fgColor=GREEN)
SFILL = PatternFill("solid", fgColor=SOFT)
thin = Side(style="thin", color="D1D5DB")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

PILLARS = ["Educate", "Behind the scenes", "Social proof", "Offer / promo", "Personal story", "Engage / community"]
PLATFORMS = ["Instagram", "Facebook", "TikTok", "LinkedIn", "Pinterest", "Email", "Blog", "YouTube"]
STATUS = ["Idea", "Drafting", "Scheduled", "Posted"]

IDEAS = {
    "Educate": ["3 mistakes beginners make with {topic}", "How to {goal} in 5 steps", "Myth vs fact: {topic}", "A simple checklist for {goal}",
                "What I wish I knew before starting {topic}", "Quick tip: the fastest way to {goal}", "Beginner glossary: 5 {topic} terms explained",
                "Tool stack I use for {topic}", "Before/after: {goal}", "FAQ: your top question about {topic}", "Common {topic} objections, answered",
                "The 80/20 of {topic}", "Step-by-step walkthrough: {goal}", "Cheat sheet: {topic}", "Do this, not that: {topic}"],
    "Behind the scenes": ["A day in my workflow", "How we make {product}", "Desk/workspace tour", "A mistake I made this month and what it taught me",
                          "Sneak peek: what I'm building next", "Packing/delivering an order", "Tools I couldn't live without", "How I plan my week",
                          "Time-lapse of a project", "What a 'bad day' in business looks like", "Meet the team / meet me", "Where the idea for {product} came from",
                          "Raw numbers: this month's wins and flops", "How I price my work", "Studio/office morning routine"],
    "Social proof": ["Customer result spotlight", "Screenshot of a kind message (with permission)", "Case study: before and after",
                     "Review of the week", "3 things customers say about {product}", "User-generated content repost", "Milestone celebration",
                     "Testimonial carousel", "Question a customer asked, and my answer", "How {customer} used {product}", "Press / mention / shout-out",
                     "Numbers: orders, students, downloads to date", "Customer story in their own words", "Results in 30 days", "Why people come back"],
    "Offer / promo": ["Introducing {product}", "Bundle spotlight and savings", "Limited-time bonus", "Last chance reminder", "Who {product} is NOT for",
                      "What's inside {product}", "{product} in 60 seconds (demo)", "Gift guide featuring {product}", "FAQ about {product}",
                      "Compare: DIY vs {product}", "Early-bird price announcement", "New arrival", "Seasonal sale", "Free sample / lead magnet", "Waitlist open"],
    "Personal story": ["Why I started", "My biggest fear in business", "A lesson from my first customer", "What I'd tell my past self",
                       "Something I'm proud of this year", "The moment I almost quit", "My values and why they matter", "A book/podcast that changed my approach",
                       "How I got through a slow month", "What success looks like to me", "A small win today", "Hobby that fuels my work", "Gratitude post",
                       "Origin story of the logo/name", "Where I want to be in 12 months"],
    "Engage / community": ["This or that poll", "Ask me anything", "Caption this", "Fill in the blank: My favorite thing about {topic} is ___",
                           "What are you working on this week?", "Share your setup", "Vote: which design should I make next?", "Question box: your toughest {topic} problem",
                           "Tag someone who needs this", "Wins of the week thread", "Would you rather", "Hot take on {topic}", "Free resource round-up",
                           "Poll: what do you struggle with most?", "Giveaway / challenge"],
}

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


NICHES = {
    "fitness_coach": {
        "name": "Fitness & Wellness Coach Content Vault", "price": 29,
        "buyer": "personal trainers, health coaches and yoga teachers who market themselves online",
        "angle": "A year of content planning plus 90 post ideas written for fitness and wellness businesses.",
        "keywords": ["fitness content calendar", "personal trainer social media", "health coach planner", "wellness content ideas", "google sheets planner"],
        "settings": dict(brand="My Fitness Studio", topic="strength training", goal="build a consistent workout habit", product="my coaching program", customer="busy beginner"),
        "educate": ["3 form mistakes in {topic}", "How to {goal} in 10 minutes a day", "Myth vs fact: {topic}", "A simple weekly plan to {goal}", "What I tell every new client about {topic}",
                    "Warm-up routine before {topic}", "Common reasons people quit, and how to stay consistent", "Easy swaps: make any meal more balanced", "Mobility moves for desk workers", "Beginner glossary: 5 {topic} terms"]},
    "handmade_seller": {
        "name": "Handmade & Etsy Seller Content Vault", "price": 29,
        "buyer": "makers and small shop owners who sell handmade or digital goods",
        "angle": "A year of content planning plus 90 ideas for showing your process, products and packaging.",
        "keywords": ["etsy seller planner", "handmade business content calendar", "small shop social media", "maker content ideas", "google sheets planner"],
        "settings": dict(brand="My Shop", topic="handmade goods", goal="find gifts people love", product="my best-selling item", customer="gift shopper"),
        "educate": ["How {product} is made, step by step", "Care guide for {topic}", "How to choose the right {product}", "Gift guide: {goal}", "Materials I use and why",
                    "Packaging reveal: how orders ship", "How to style {product}", "Custom order: how it works", "Shop FAQ: shipping, returns, sizing", "Behind the design: what inspired {product}"]},
    "real_estate_agent": {
        "name": "Real Estate Agent Content Vault", "price": 34,
        "buyer": "real estate agents and brokers who need consistent local content",
        "angle": "A year of content planning plus 90 ideas for listings, local market updates and client education.",
        "keywords": ["real estate content calendar", "realtor social media planner", "real estate marketing ideas", "agent content ideas", "google sheets planner"],
        "settings": dict(brand="My Real Estate Team", topic="buying a home", goal="buy or sell with confidence", product="my listing service", customer="first-time buyer"),
        "educate": ["3 mistakes first-time buyers make in {topic}", "How to prepare your home to sell", "Local market update: what changed this month", "What is earnest money? (plain English)", "Neighborhood spotlight",
                    "Buyer checklist: before you tour", "How to read a listing", "Closing costs explained", "Staging tips that cost under $100", "FAQ: how long does {topic} really take?"]},
    "wedding_planner": {
        "name": "Wedding & Event Planner Content Vault", "price": 29,
        "buyer": "wedding and event planners who market on Instagram, Pinterest and email",
        "angle": "A year of content planning plus 90 ideas for real weddings, vendor tips and couple education.",
        "keywords": ["wedding planner content calendar", "event planner social media", "wedding business ideas", "planner content ideas", "google sheets planner"],
        "settings": dict(brand="My Event Studio", topic="wedding planning", goal="plan a stress-free wedding", product="my planning package", customer="engaged couple"),
        "educate": ["12-month {topic} timeline", "How to build a realistic wedding budget", "Questions to ask every vendor", "Real wedding spotlight: what worked", "Day-of timeline template",
                    "Seating chart tips", "Small wedding ideas that feel big", "Common {topic} mistakes", "Rain plan checklist", "How to {goal}: 5 steps"]},
    "freelance_designer": {
        "name": "Freelance Designer & Creative Content Vault", "price": 29,
        "buyer": "freelance designers, photographers and creative studios who need steady client leads",
        "angle": "A year of content planning plus 90 ideas for showcasing work, process and client results.",
        "keywords": ["freelancer content calendar", "designer social media planner", "creative business content", "portfolio content ideas", "google sheets planner"],
        "settings": dict(brand="My Creative Studio", topic="design", goal="get a better brand", product="my design package", customer="small business owner"),
        "educate": ["Before/after: {product} for a real client", "How I run a client project, step by step", "Design mistakes that cost small businesses customers", "How to brief a designer", "What {product} costs and why",
                    "Portfolio breakdown: the thinking behind one project", "Tools I use for {topic}", "Feedback that makes work better", "How to {goal} on a budget", "Contract and process basics for clients"]},
}


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font, cell.fill = HEAD, HFILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def readme(wb, title="Small Business Content & Planning Vault"):
    ws = wb.active
    ws.title = "START HERE"
    ws.sheet_view.showGridLines = False
    ws["B2"] = title
    ws["B2"].font = Font(bold=True, size=20, color=GREEN)
    lines = [
        ("1. Settings", "Type your business name, topic, product and year once. Idea Bank and Calendar update."),
        ("2. Idea Bank", "90 ready-to-post prompts across 6 content pillars. Filter by pillar or platform."),
        ("3. Content Calendar", "A full year, one tab per quarter-style layout: date, platform, pillar, status, caption."),
        ("4. Weekly Planner", "Top 3 priorities, daily blocks, habits, wins. Duplicate the tab each week."),
        ("5. Budget Tracker", "Monthly income and expenses with automatic totals and profit."),
        ("6. Post Tracker", "Log results (reach, likes, clicks, sales) and see engagement rate and best pillar."),
        ("", ""),
        ("Google Sheets", "File > Import > Upload > 'Replace spreadsheet'. Everything works, including dropdowns and formulas."),
        ("Notion", "Import the CSVs from the Notion_CSVs folder: Add > Import > CSV."),
        ("Tip", "Edit only the cream-coloured input cells. Gray/green cells contain formulas."),
    ]
    for i, (a, b) in enumerate(lines, 4):
        ws.cell(row=i, column=2, value=a).font = Font(bold=True)
        ws.cell(row=i, column=3, value=b).alignment = Alignment(wrap_text=True, vertical="top")
    widths(ws, [3, 22, 90])


def settings(wb, defaults=None):
    ws = wb.create_sheet("Settings")
    ws.sheet_view.showGridLines = False
    cream = PatternFill("solid", fgColor="FFF8E1")
    d = defaults or {}
    rows = [("Business name", d.get("brand", "My Business")), ("Main topic", d.get("topic", "my niche")), ("Goal customers want", d.get("goal", "get started")),
            ("Product / offer", d.get("product", "my signature offer")), ("Ideal customer", d.get("customer", "customer")), ("Year", dt.date.today().year + (1 if dt.date.today().month > 6 else 0))]
    ws["B2"] = "Settings (edit the cream cells)"
    ws["B2"].font = Font(bold=True, size=16, color=GREEN)
    for i, (k, v) in enumerate(rows, 4):
        ws.cell(row=i, column=2, value=k).font = Font(bold=True)
        c = ws.cell(row=i, column=3, value=v)
        c.fill, c.border = cream, BORDER
    widths(ws, [3, 24, 38])
    return ws


def idea_bank(wb, ideas=None):
    ideas = ideas or IDEAS
    ws = wb.create_sheet("Idea Bank")
    hdr = ["#", "Pillar", "Idea template", "Your version (auto-filled)", "Best platform", "Used?"]
    ws.append(hdr)
    style_header(ws, 1, len(hdr))
    n = 0
    plat_cycle = ["Instagram", "TikTok", "Facebook", "LinkedIn", "Pinterest", "Email"]
    for pillar, items in ideas.items():
        for it in items:
            n += 1
            r = n + 1
            f = (f'=SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(C{r},"{{topic}}",Settings!$C$5),'
                 f'"{{goal}}",Settings!$C$6),"{{product}}",Settings!$C$7),"{{customer}}",Settings!$C$8),"{{brand}}",Settings!$C$4)')
            ws.append([n, pillar, it, f, plat_cycle[n % len(plat_cycle)], "No"])
            for c in range(1, 7):
                ws.cell(row=r, column=c).border = BORDER
                ws.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"F2:F{n + 1}")
    ws.conditional_formatting.add(f"A2:F{n + 1}", CellIsRule(operator="equal", formula=['"Yes"'], fill=PatternFill("solid", bgColor="E5E7EB")) )
    ws.auto_filter.ref = f"A1:F{n + 1}"
    ws.freeze_panes = "A2"
    widths(ws, [5, 20, 48, 58, 16, 9])
    return n


def calendar(wb, year_cell="Settings!$C$9"):
    ws = wb.create_sheet("Content Calendar")
    hdr = ["Date", "Day", "Month", "Platform", "Pillar", "Idea / topic", "Caption", "Status", "Link"]
    ws.append(hdr)
    style_header(ws, 1, len(hdr))
    # 3 posts per week = 156 rows, formulas derive from the Settings year so the vault is reusable
    r = 2
    jan1 = '=DATE(Settings!$C$9,1,1)'
    pil = PILLARS
    for i in range(156):
        week, k = divmod(i, 3)
        offset = week * 7 + [0, 2, 4][k]  # Mon / Wed / Fri after first Monday logic below
        ws.cell(row=r, column=1, value=f"=DATE(Settings!$C$9,1,1)+MOD(7-WEEKDAY(DATE(Settings!$C$9,1,1),3),7)+{offset}")
        ws.cell(row=r, column=1).number_format = "ddd mmm d, yyyy"
        ws.cell(row=r, column=2, value=f'=TEXT(A{r},"dddd")')
        ws.cell(row=r, column=3, value=f'=TEXT(A{r},"mmmm")')
        ws.cell(row=r, column=4, value=PLATFORMS[[0, 1, 0][k] if k != 1 else 1])
        ws.cell(row=r, column=5, value=pil[i % len(pil)])
        ws.cell(row=r, column=8, value="Idea")
        for c in range(1, 10):
            ws.cell(row=r, column=c).border = BORDER
            ws.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    last = r - 1
    for col, vals in [("D", PLATFORMS), ("E", PILLARS), ("H", STATUS)]:
        dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{last}")
    for val, color in [("Posted", "C6EFCE"), ("Scheduled", "FFEB9C"), ("Drafting", "DDEBF7")]:
        ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(operator="equal", formula=[f'"{val}"'], fill=PatternFill("solid", bgColor=color)))
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:I{last}"
    widths(ws, [18, 12, 12, 14, 20, 38, 55, 12, 24])


def weekly(wb):
    ws = wb.create_sheet("Weekly Planner")
    ws.sheet_view.showGridLines = False
    ws["B2"] = "Weekly Planner"; ws["B2"].font = Font(bold=True, size=18, color=GREEN)
    ws["B3"] = "Week of:"; ws["C3"] = None
    ws["B5"] = "Top 3 priorities"; ws["B5"].font = Font(bold=True)
    for i in range(3):
        ws.cell(row=6 + i, column=2, value=f"{i + 1}.")
        ws.merge_cells(start_row=6 + i, start_column=3, end_row=6 + i, end_column=8)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ws.append([])
    hr = 10
    for j, h in enumerate(["Time block"] + days, 2):
        ws.cell(row=hr, column=j, value=h)
    for j in range(2, 10):
        c = ws.cell(row=hr, column=j); c.font, c.fill, c.border = HEAD, HFILL, BORDER
        c.alignment = Alignment(horizontal="center")
    blocks = ["Deep work (9-11)", "Admin / email (11-12)", "Content (1-3)", "Sales / outreach (3-4)", "Learning (4-5)"]
    for i, b in enumerate(blocks):
        ws.cell(row=hr + 1 + i, column=2, value=b).font = Font(bold=True)
        for j in range(2, 10):
            ws.cell(row=hr + 1 + i, column=j).border = BORDER
            ws.cell(row=hr + 1 + i, column=j).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[hr + 1 + i].height = 34
    hb = hr + len(blocks) + 3
    ws.cell(row=hb - 1, column=2, value="Habit tracker (type x)").font = Font(bold=True)
    for j, h in enumerate(days, 3):
        ws.cell(row=hb - 1, column=j, value=h[:3]).font = Font(bold=True)
    for i, h in enumerate(["Posted content", "Replied to messages", "Tracked money", "Moved / walked", "Learned something"]):
        ws.cell(row=hb + i, column=2, value=h)
        for j in range(3, 10):
            ws.cell(row=hb + i, column=j).border = BORDER
        ws.cell(row=hb + i, column=10, value=f'=COUNTIF(C{hb + i}:I{hb + i},"x")')
    ws.cell(row=hb - 1, column=10, value="Total").font = Font(bold=True)
    ws.cell(row=hb + 6, column=2, value="Wins this week").font = Font(bold=True)
    ws.merge_cells(start_row=hb + 7, start_column=2, end_row=hb + 9, end_column=9)
    widths(ws, [3, 26, 15, 15, 15, 15, 15, 15, 15, 8])


def budget(wb, income=None, expenses=None):
    ws = wb.create_sheet("Budget Tracker")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Monthly Budget Tracker"; ws["A1"].font = Font(bold=True, size=18, color=GREEN)
    hdr = ["Category"] + [m[:3] for m in MONTHS] + ["Total"]
    ws.append([]); ws.append(hdr)
    style_header(ws, 3, len(hdr))
    sections = [("INCOME", income or ["Product sales", "Services / clients", "Affiliate / other"]),
                ("EXPENSES", expenses or ["Software & tools", "Advertising", "Fees (platform, payment)", "Contractors", "Equipment", "Education", "Other"])]
    r = 4
    totals = {}
    for sec, items in sections:
        ws.cell(row=r, column=1, value=sec).font = Font(bold=True)
        for c in range(1, 15):
            ws.cell(row=r, column=c).fill = SFILL
        r += 1
        first = r
        for it in items:
            ws.cell(row=r, column=1, value=it)
            for c in range(2, 14):
                ws.cell(row=r, column=c).number_format = '$#,##0.00'
                ws.cell(row=r, column=c).border = BORDER
            ws.cell(row=r, column=14, value=f"=SUM(B{r}:M{r})").number_format = '$#,##0.00'
            r += 1
        ws.cell(row=r, column=1, value=f"Total {sec.lower()}").font = Font(bold=True)
        for c in range(2, 15):
            col = get_column_letter(c)
            cell = ws.cell(row=r, column=c, value=f"=SUM({col}{first}:{col}{r - 1})")
            cell.font, cell.number_format = Font(bold=True), '$#,##0.00'
        totals[sec] = r
        r += 2
    ws.cell(row=r, column=1, value="PROFIT").font = Font(bold=True, size=12)
    for c in range(2, 15):
        col = get_column_letter(c)
        cell = ws.cell(row=r, column=c, value=f"={col}{totals['INCOME']}-{col}{totals['EXPENSES']}")
        cell.font, cell.number_format = Font(bold=True), '$#,##0.00'
    ws.conditional_formatting.add(f"B{r}:N{r}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="B91C1C", bold=True)))
    ws.cell(row=r + 1, column=1, value="Profit margin")
    for c in range(2, 15):
        col = get_column_letter(c)
        ws.cell(row=r + 1, column=c, value=f'=IF({col}{totals["INCOME"]}=0,"",{col}{r}/{col}{totals["INCOME"]})').number_format = "0%"
    widths(ws, [28] + [11] * 12 + [13])
    ws.freeze_panes = "B4"
    return r


def tracker(wb):
    ws = wb.create_sheet("Post Tracker")
    hdr = ["Date", "Platform", "Pillar", "Topic", "Reach", "Likes", "Comments", "Shares", "Clicks", "Sales", "Engagement rate"]
    ws.append(hdr)
    style_header(ws, 1, len(hdr))
    for r in range(2, 202):
        ws.cell(row=r, column=11, value=f'=IF(E{r}=0,"",(F{r}+G{r}+H{r})/E{r})').number_format = "0.0%"
        for c in range(1, 12):
            ws.cell(row=r, column=c).border = BORDER
    for col, vals in [("B", PLATFORMS), ("C", PILLARS)]:
        dv = DataValidation(type="list", formula1='"' + ",".join(vals) + '"', allow_blank=True)
        ws.add_data_validation(dv); dv.add(f"{col}2:{col}201")
    # pillar summary
    ws["M1"], ws["N1"], ws["O1"], ws["P1"] = "Pillar", "Posts", "Avg engagement", "Sales"
    for c in "MNOP":
        ws[f"{c}1"].font, ws[f"{c}1"].fill = HEAD, HFILL
    for i, p in enumerate(PILLARS, 2):
        ws[f"M{i}"] = p
        ws[f"N{i}"] = f'=COUNTIF($C$2:$C$201,M{i})'
        ws[f"O{i}"] = f'=IFERROR(AVERAGEIF($C$2:$C$201,M{i},$K$2:$K$201),"")'
        ws[f"O{i}"].number_format = "0.0%"
        ws[f"P{i}"] = f'=SUMIF($C$2:$C$201,M{i},$J$2:$J$201)'
    ws["M9"], ws["N9"] = "Best pillar", '=IFERROR(INDEX(M2:M7,MATCH(MAX(O2:O7),O2:O7,0)),"")'
    ws["M9"].font = Font(bold=True)
    ws.freeze_panes = "A2"
    widths(ws, [12, 14, 20, 30, 9, 9, 10, 9, 9, 9, 14, 3, 20, 8, 15, 8])


def notion_csvs(outdir, ideas=None):
    ideas = ideas or IDEAS
    d = outdir / "Notion_CSVs"
    d.mkdir()
    with open(d / "Idea_Bank.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Idea", "Pillar", "Platform", "Status"])
        n = 0
        for p, items in ideas.items():
            for it in items:
                n += 1; w.writerow([it, p, PLATFORMS[n % 6], "Idea"])
    with open(d / "Content_Calendar.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Name", "Date", "Platform", "Pillar", "Status", "Caption"])
        start = dt.date(dt.date.today().year + 1, 1, 1)
        start += dt.timedelta(days=(7 - start.weekday()) % 7)
        for i in range(156):
            wk, k = divmod(i, 3)
            day = start + dt.timedelta(days=wk * 7 + [0, 2, 4][k])
            w.writerow([f"Post {i + 1}", day.isoformat(), PLATFORMS[[0, 1, 0][k]], PILLARS[i % 6], "Idea", ""])
    with open(d / "Weekly_Habits.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Habit", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        for h in ["Posted content", "Replied to messages", "Tracked money", "Moved / walked", "Learned something"]:
            w.writerow([h] + ["No"] * 7)
    (d / "HOW_TO_IMPORT.txt").write_text("In Notion: sidebar > Import > CSV. Repeat for each file. Change the Status/Platform/Pillar columns to Select properties after import.\n")


CAPTION_STARTERS = [
    "Here's the truth about {topic}:", "If you're struggling with {goal}, read this.", "Save this for later: {topic} edition.",
    "I used to think {topic} was complicated. Then I learned this.", "Stop scrolling. 30 seconds on {goal}.",
    "The one thing I'd change about how I approached {topic}:", "New from {brand}:", "Quick question for my {customer} people:",
    "Behind the scenes at {brand} today.", "Reminder: you do not need to be perfect to {goal}.",
]
CTAS = ["Save this post and send it to a friend.", "Comment 'YES' and I'll send the details.", "Link in bio.", "Reply and tell me what you'd add.",
        "Follow for more {topic} tips.", "DM me the word START.", "Tap the link to see what's inside.", "What's your biggest question? Drop it below."]


def caption_kit(outdir):
    lines = ["CAPTION KIT: swap {braces} with your own words. Mix any opener + body + CTA.\n", "OPENERS"]
    lines += [f"  {i + 1}. {s}" for i, s in enumerate(CAPTION_STARTERS)]
    lines += ["", "BODY FORMULAS",
              "  A. Problem > Why it happens > Fix > Result",
              "  B. Story (2 lines) > Lesson > How to apply it",
              "  C. 3 tips in a list, one line each",
              "  D. Before / After / How",
              "  E. Myth / Truth / Proof",
              "", "CALLS TO ACTION"]
    lines += [f"  {i + 1}. {s}" for i, s in enumerate(CTAS)]
    lines += ["", "HASHTAG BUCKETS (pick 3 + 3 + 3)", "  Niche (under 100k posts): your topic + city + audience",
              "  Mid (100k-1M): your category", "  Broad (1M+): small business, entrepreneur, creator", ""]
    (outdir / "Caption_Kit.txt").write_text("\n".join(lines))


def build(outdir, cfg, brief):
    outdir = Path(outdir)
    spec = cfg.get("spec") or {}
    ideas = None
    if spec.get("ideas"):  # niche ideas first, then the generic pool so the bank stays deep
        ideas = {p: list(spec["ideas"].get(p, [])) + IDEAS[p] for p in IDEAS}
    wb = Workbook()
    readme(wb, spec.get("title", "Small Business Content & Planning Vault"))
    settings(wb, spec.get("defaults"))
    idea_bank(wb, ideas)
    calendar(wb)
    weekly(wb)
    budget(wb, spec.get("income"), spec.get("expenses"))
    tracker(wb)
    wb.save(outdir / "Planning_Vault.xlsx")
    notion_csvs(outdir, ideas)
    caption_kit(outdir)
    (outdir / "README.txt").write_text("Open Planning_Vault.xlsx in Excel or upload to Google Sheets (File > Import). Notion CSVs are in Notion_CSVs.\n")
    return sorted(p for p in outdir.rglob("*") if p.is_file())


def validate(outdir):
    from openpyxl import load_workbook
    outdir, problems = Path(outdir), []
    f = outdir / "Planning_Vault.xlsx"
    if not f.exists():
        return ["Planning_Vault.xlsx missing"]
    wb = load_workbook(f)
    need = ["START HERE", "Settings", "Idea Bank", "Content Calendar", "Weekly Planner", "Budget Tracker", "Post Tracker"]
    for n in need:
        if n not in wb.sheetnames:
            problems.append(f"missing sheet {n}")
    if "Idea Bank" in wb.sheetnames and wb["Idea Bank"].max_row < 90:
        problems.append("Idea Bank has fewer than 90 ideas")
    if "Content Calendar" in wb.sheetnames and wb["Content Calendar"].max_row < 157:
        problems.append("calendar shorter than 156 posts")
    for n in ("Idea_Bank.csv", "Content_Calendar.csv", "Weekly_Habits.csv"):
        if not (outdir / "Notion_CSVs" / n).exists():
            problems.append(f"missing {n}")
    return problems
