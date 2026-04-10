"""
Weekly Planner PDF Generator for Amazon KDP
============================================
Produces a print-ready 8.5" x 11" interior PDF with:
  - Cover page
  - How-to-use page
  - Yearly goals page
  - 12 monthly overview pages
  - 52 weekly spread pages (Mon–Sun)
  - Notes pages at the back

KDP Interior Specs used:
  - Trim:    8.5" x 11"  (standard US Letter)
  - Bleed:   none (white background)
  - Margins: 0.75" outside, 0.875" gutter (inside) for up to ~200 pages
  - Fonts:   Helvetica family (built-in, no embed issues)
  - Color:   Black + one accent color (#2E4057 navy) — works B&W and color

Run:
    python3 weekly_planner.py
Output:
    weekly_planner_kdp.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
import calendar
import datetime

# ── Constants ────────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = letter          # 8.5 × 11 inches
GUTTER   = 0.875 * inch          # inside (binding) margin
OUTER    = 0.75  * inch          # outside margin
TOP_M    = 0.75  * inch
BOT_M    = 0.75  * inch

NAVY     = colors.HexColor("#2E4057")
SLATE    = colors.HexColor("#5C7A8A")
LIGHT_BG = colors.HexColor("#F5F7FA")
RULE     = colors.HexColor("#C8D4DC")
WHITE    = colors.white
BLACK    = colors.black

PLANNER_YEAR = 2026
PLANNER_TITLE = "MY WEEKLY PLANNER"
SUBTITLE = f"{PLANNER_YEAR}"

OUTPUT_FILE = "weekly_planner_kdp.pdf"


# ── Helper: alternating left/right margin for binding ────────────────────────

def left_margin(page_num):
    """Odd pages have binding on left; even pages on right."""
    return GUTTER if page_num % 2 == 1 else OUTER

def right_margin(page_num):
    return OUTER if page_num % 2 == 1 else GUTTER


# ── Canvas helpers ────────────────────────────────────────────────────────────

def draw_page_border(c, page_num):
    """Thin accent line at top of every interior page."""
    lm = left_margin(page_num)
    text_w = PAGE_W - lm - right_margin(page_num)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.line(lm, PAGE_H - TOP_M + 6, lm + text_w, PAGE_H - TOP_M + 6)

def draw_footer(c, page_num, label=""):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    c.setFont("Helvetica", 7)
    c.setFillColor(SLATE)
    # page number
    if page_num % 2 == 1:
        c.drawRightString(lm + text_w, BOT_M - 14, str(page_num))
    else:
        c.drawString(lm, BOT_M - 14, str(page_num))
    # center label
    if label:
        c.drawCentredString(PAGE_W / 2, BOT_M - 14, label)

def header_text(c, page_num, text, size=9):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    c.setFont("Helvetica", size)
    c.setFillColor(SLATE)
    c.drawCentredString(lm + text_w / 2, PAGE_H - TOP_M + 14, text)


# ── Page 1: Cover ─────────────────────────────────────────────────────────────

def draw_cover(c):
    c.saveState()

    # Full navy background
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Decorative horizontal band
    band_h = 1.8 * inch
    band_y = PAGE_H * 0.42
    c.setFillColor(colors.HexColor("#1A2840"))
    c.rect(0, band_y, PAGE_W, band_h, fill=1, stroke=0)

    # Thin accent lines
    c.setStrokeColor(colors.HexColor("#7EA8BE"))
    c.setLineWidth(1)
    c.line(0.6 * inch, band_y + band_h + 2, PAGE_W - 0.6 * inch, band_y + band_h + 2)
    c.line(0.6 * inch, band_y - 2,          PAGE_W - 0.6 * inch, band_y - 2)

    # Year in band
    c.setFillColor(colors.HexColor("#7EA8BE"))
    c.setFont("Helvetica", 38)
    c.drawCentredString(PAGE_W / 2, band_y + band_h / 2 - 15, SUBTITLE)

    # Main title
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_W / 2, band_y + band_h + 0.85 * inch, "MY")
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(PAGE_W / 2, band_y + band_h + 0.2 * inch + 0.4 * inch,
                        "WEEKLY")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(PAGE_W / 2, band_y + band_h + 0.2 * inch - 0.4 * inch,
                        "PLANNER")

    # Tagline below band
    c.setFillColor(colors.HexColor("#A8C4D4"))
    c.setFont("Helvetica-Oblique", 13)
    c.drawCentredString(PAGE_W / 2, band_y - 0.45 * inch,
                        "Plan · Focus · Achieve")

    # Bottom decoration: small dots
    dot_y = 1.1 * inch
    for i, dx in enumerate(range(-3, 4)):
        r = 5 if i == 3 else 3
        c.setFillColor(WHITE if i == 3 else colors.HexColor("#5C7A8A"))
        cx = PAGE_W / 2 + dx * 18
        c.circle(cx, dot_y, r, fill=1, stroke=0)

    # "Name / Year" label
    c.setFillColor(colors.HexColor("#5C7A8A"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 0.55 * inch, "NAME: ________________________________")

    c.restoreState()


# ── Page 2: How to Use ────────────────────────────────────────────────────────

def draw_how_to_use(c, page_num):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    y = PAGE_H - TOP_M

    draw_page_border(c, page_num)
    draw_footer(c, page_num, "HOW TO USE")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(lm + text_w / 2, y - 0.3 * inch, "HOW TO USE THIS PLANNER")

    c.setStrokeColor(NAVY)
    c.setLineWidth(1.5)
    c.line(lm, y - 0.45 * inch, lm + text_w, y - 0.45 * inch)

    sections = [
        ("MONTHLY OVERVIEW",
         "Each month begins with a calendar grid. Use it to note appointments, "
         "deadlines, and important dates at a glance. Color-code categories to "
         "quickly identify what's coming up."),
        ("WEEKLY SPREAD",
         "Each week opens with a Priority section — write your top 3 goals "
         "before filling in daily tasks. The daily columns give you space for "
         "a morning focus, scheduled tasks, and an evening reflection."),
        ("DAILY SECTIONS",
         "Every day has three zones:\n"
         "  • TOP PRIORITY — the one thing that must get done\n"
         "  • TASKS — your to-do list for the day\n"
         "  • NOTES — quick captures, ideas, or reminders"),
        ("HABIT TRACKER",
         "The weekly habit tracker lets you mark up to 7 habits each day. "
         "Write your habits in the left column and shade each box as you "
         "complete them."),
        ("NOTES PAGES",
         "Blank ruled notes pages at the back are perfect for brainstorming, "
         "meeting notes, or project planning."),
    ]

    y_pos = y - 0.75 * inch
    for title, body in sections:
        if y_pos < BOT_M + 0.5 * inch:
            break

        # Numbered bullet bar
        c.setFillColor(NAVY)
        c.roundRect(lm, y_pos - 0.02 * inch, text_w, 0.28 * inch, 4, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(lm + 0.12 * inch, y_pos + 0.06 * inch, title)

        y_pos -= 0.35 * inch

        # Body text — manual word-wrap
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 10)
        lines = _wrap(body, c, "Helvetica", 10, text_w - 0.25 * inch)
        for line in lines:
            c.drawString(lm + 0.12 * inch, y_pos, line)
            y_pos -= 0.18 * inch

        y_pos -= 0.2 * inch


def _wrap(text, c, font, size, max_w):
    """Simple word-wrapping that handles \\n."""
    c.setFont(font, size)
    result = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            result.append("")
            continue
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if c.stringWidth(test, font, size) <= max_w:
                current = test
            else:
                if current:
                    result.append(current)
                current = word
        if current:
            result.append(current)
    return result


# ── Page 3: Yearly Goals ──────────────────────────────────────────────────────

def draw_yearly_goals(c, page_num):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    y = PAGE_H - TOP_M

    draw_page_border(c, page_num)
    draw_footer(c, page_num, f"{PLANNER_YEAR} GOALS")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(lm + text_w / 2, y - 0.32 * inch, f"{PLANNER_YEAR}  GOALS & INTENTIONS")

    c.setStrokeColor(RULE)
    c.setLineWidth(1)
    c.line(lm, y - 0.48 * inch, lm + text_w, y - 0.48 * inch)

    categories = [
        "PERSONAL", "CAREER / BUSINESS", "HEALTH & FITNESS",
        "FINANCES", "RELATIONSHIPS", "LEARNING & GROWTH",
    ]

    box_w = (text_w - 0.15 * inch) / 2
    box_h = 1.65 * inch
    x_positions = [lm, lm + box_w + 0.15 * inch]
    y_start = y - 0.72 * inch

    for i, cat in enumerate(categories):
        col = i % 2
        row = i // 2
        bx = x_positions[col]
        by = y_start - row * (box_h + 0.15 * inch)

        # Box background
        c.setFillColor(LIGHT_BG)
        c.roundRect(bx, by - box_h, box_w, box_h, 5, fill=1, stroke=0)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.roundRect(bx, by - box_h, box_w, box_h, 5, fill=0, stroke=1)

        # Category header
        c.setFillColor(NAVY)
        c.roundRect(bx, by - 0.28 * inch, box_w, 0.28 * inch, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(bx + 0.1 * inch, by - 0.18 * inch, cat)

        # Writing lines
        line_y = by - 0.5 * inch
        line_spacing = 0.25 * inch
        n_lines = int((box_h - 0.38 * inch) / line_spacing)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        for _ in range(n_lines):
            c.line(bx + 0.12 * inch, line_y, bx + box_w - 0.12 * inch, line_y)
            line_y -= line_spacing

    # Word of the year
    wy = y_start - 3 * (box_h + 0.15 * inch) - 0.1 * inch
    c.setFillColor(NAVY)
    c.roundRect(lm, wy - 0.7 * inch, text_w, 0.7 * inch, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(lm + 0.15 * inch, wy - 0.22 * inch, "MY WORD OF THE YEAR:")
    c.setStrokeColor(colors.HexColor("#7EA8BE"))
    c.setLineWidth(0.8)
    c.line(lm + 1.85 * inch, wy - 0.22 * inch,
           lm + text_w - 0.15 * inch, wy - 0.22 * inch)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#A8C4D4"))
    c.drawString(lm + 0.15 * inch, wy - 0.50 * inch,
                 "WHY THIS WORD:")
    c.setStrokeColor(colors.HexColor("#7EA8BE"))
    c.line(lm + 1.55 * inch, wy - 0.50 * inch,
           lm + text_w - 0.15 * inch, wy - 0.50 * inch)


# ── Monthly Overview ──────────────────────────────────────────────────────────

MONTH_NAMES = [
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
]

def draw_monthly_overview(c, page_num, month_index):
    """month_index: 0-11"""
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    y = PAGE_H - TOP_M

    month_name = MONTH_NAMES[month_index]
    month_num  = month_index + 1
    draw_page_border(c, page_num)
    draw_footer(c, page_num, f"{month_name} {PLANNER_YEAR}")

    # Title banner
    c.setFillColor(NAVY)
    c.roundRect(lm, y - 0.55 * inch, text_w, 0.55 * inch, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(lm + text_w / 2, y - 0.36 * inch, month_name)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#A8C4D4"))
    c.drawRightString(lm + text_w - 0.15 * inch, y - 0.36 * inch,
                      str(PLANNER_YEAR))

    # Day-of-week headers
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    cell_w = text_w / 7
    header_y = y - 0.72 * inch
    for i, d in enumerate(days):
        bx = lm + i * cell_w
        c.setFillColor(SLATE)
        c.rect(bx, header_y - 0.22 * inch, cell_w, 0.22 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(bx + cell_w / 2, header_y - 0.15 * inch, d)

    # Calendar grid
    cal = calendar.monthcalendar(PLANNER_YEAR, month_num)
    cell_h = 0.88 * inch
    grid_y = header_y - 0.22 * inch

    for week in cal:
        grid_y -= cell_h
        for col, day in enumerate(week):
            bx = lm + col * cell_w
            # weekend shading
            fill_c = colors.HexColor("#EEF2F5") if col >= 5 else WHITE
            c.setFillColor(fill_c)
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.rect(bx, grid_y, cell_w, cell_h, fill=1, stroke=1)
            if day:
                c.setFillColor(NAVY if col < 5 else SLATE)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(bx + 0.07 * inch, grid_y + cell_h - 0.17 * inch, str(day))

    # Monthly notes & intentions section
    notes_y = grid_y - 0.2 * inch
    remaining = notes_y - (BOT_M + 0.1 * inch)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(lm, notes_y - 0.02 * inch, "MONTHLY INTENTIONS & NOTES")
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(lm, notes_y - 0.16 * inch, lm + text_w, notes_y - 0.16 * inch)

    line_y = notes_y - 0.36 * inch
    spacing = 0.22 * inch
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    while line_y > BOT_M + 0.15 * inch:
        c.line(lm, line_y, lm + text_w, line_y)
        line_y -= spacing


# ── Weekly Spread ─────────────────────────────────────────────────────────────

def week_dates(year, week_num):
    """Return list of 7 date objects Mon–Sun for ISO week week_num."""
    jan4 = datetime.date(year, 1, 4)
    start = jan4 - datetime.timedelta(days=jan4.isoweekday() - 1)
    monday = start + datetime.timedelta(weeks=week_num - 1)
    return [monday + datetime.timedelta(days=i) for i in range(7)]


def draw_weekly_spread(c, page_num, week_num):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    y = PAGE_H - TOP_M

    dates = week_dates(PLANNER_YEAR, week_num)
    date_range = f"{dates[0].strftime('%b %-d')} – {dates[6].strftime('%b %-d, %Y')}"

    draw_page_border(c, page_num)
    draw_footer(c, page_num, f"WEEK {week_num}")
    header_text(c, page_num, date_range, size=9)

    # ── Top section: Priorities + Habit Tracker ──────────────────────────────
    TOP_H = 1.55 * inch
    top_y = y - 0.15 * inch

    # Priorities box (left 45%)
    pri_w = text_w * 0.45
    c.setFillColor(LIGHT_BG)
    c.roundRect(lm, top_y - TOP_H, pri_w, TOP_H, 5, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.roundRect(lm, top_y - TOP_H, pri_w, TOP_H, 5, fill=0, stroke=1)

    c.setFillColor(NAVY)
    c.roundRect(lm, top_y - 0.27 * inch, pri_w, 0.27 * inch, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(lm + 0.1 * inch, top_y - 0.18 * inch, "TOP PRIORITIES THIS WEEK")

    for i in range(1, 4):
        ly = top_y - 0.27 * inch - i * 0.38 * inch
        c.setFillColor(NAVY)
        c.circle(lm + 0.17 * inch, ly + 0.08 * inch, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(lm + 0.17 * inch, ly + 0.04 * inch, str(i))
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(lm + 0.3 * inch, ly + 0.04 * inch,
               lm + pri_w - 0.1 * inch, ly + 0.04 * inch)

    # Habit Tracker box (right 52%)
    hab_x = lm + pri_w + 0.15 * inch
    hab_w = text_w - pri_w - 0.15 * inch
    c.setFillColor(LIGHT_BG)
    c.roundRect(hab_x, top_y - TOP_H, hab_w, TOP_H, 5, fill=1, stroke=0)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.roundRect(hab_x, top_y - TOP_H, hab_w, TOP_H, 5, fill=0, stroke=1)

    c.setFillColor(NAVY)
    c.roundRect(hab_x, top_y - 0.27 * inch, hab_w, 0.27 * inch, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(hab_x + 0.1 * inch, top_y - 0.18 * inch, "HABIT TRACKER")

    # Habit grid: 7 habits × 7 days
    day_abbr = ["M", "T", "W", "T", "F", "S", "S"]
    hab_label_w = 0.95 * inch
    box_size = (hab_w - hab_label_w - 0.12 * inch) / 7
    header_row_y = top_y - 0.27 * inch - 0.22 * inch

    # Day headers
    for di, d in enumerate(day_abbr):
        bx2 = hab_x + hab_label_w + di * box_size
        c.setFillColor(SLATE)
        c.rect(bx2, header_row_y, box_size, 0.2 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(bx2 + box_size / 2, header_row_y + 0.05 * inch, d)

    # Habit rows
    n_habits = 5
    row_h = (TOP_H - 0.27 * inch - 0.22 * inch - 0.06 * inch) / n_habits
    for hi in range(n_habits):
        row_y = header_row_y - (hi + 1) * row_h
        # label line
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.line(hab_x + 0.06 * inch, row_y + row_h / 2,
               hab_x + hab_label_w - 0.06 * inch, row_y + row_h / 2)
        # boxes
        for di in range(7):
            bx2 = hab_x + hab_label_w + di * box_size
            c.setStrokeColor(RULE)
            c.setLineWidth(0.5)
            c.rect(bx2, row_y, box_size, row_h, fill=0, stroke=1)

    # ── Daily columns ────────────────────────────────────────────────────────
    days_full = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    day_area_y = top_y - TOP_H - 0.12 * inch
    day_area_h = day_area_y - (BOT_M + 0.25 * inch)
    col_w = text_w / 7

    for di, (dname, date_obj) in enumerate(zip(days_full, dates)):
        cx = lm + di * col_w
        is_weekend = di >= 5

        # Column header
        hdr_h = 0.30 * inch
        c.setFillColor(SLATE if is_weekend else NAVY)
        c.rect(cx, day_area_y - hdr_h, col_w, hdr_h, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx + col_w / 2, day_area_y - hdr_h + hdr_h * 0.55, dname)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + col_w / 2, day_area_y - hdr_h + hdr_h * 0.18,
                            date_obj.strftime("%-m/%-d"))

        # Top priority mini-box
        tp_h = 0.26 * inch
        tp_y = day_area_y - hdr_h - tp_h
        c.setFillColor(colors.HexColor("#E8ECF0"))
        c.rect(cx, tp_y, col_w, tp_h, fill=1, stroke=0)
        c.setFillColor(SLATE)
        c.setFont("Helvetica-Bold", 5.5)
        c.drawString(cx + 0.04 * inch, tp_y + tp_h * 0.55, "TOP PRIORITY:")
        c.setStrokeColor(RULE)
        c.setLineWidth(0.4)
        c.line(cx + 0.04 * inch, tp_y + 0.05 * inch,
               cx + col_w - 0.04 * inch, tp_y + 0.05 * inch)

        # Task lines
        task_y = tp_y
        line_gap = 0.175 * inch
        c.setStrokeColor(RULE)
        c.setLineWidth(0.35)
        # vertical divider
        if di < 6:
            c.setStrokeColor(RULE)
            c.line(cx + col_w, day_area_y, cx + col_w, BOT_M + 0.25 * inch)

        line_y2 = task_y - line_gap
        while line_y2 > BOT_M + 0.3 * inch:
            # tiny checkbox
            cb = 0.065 * inch
            c.setStrokeColor(SLATE)
            c.setLineWidth(0.35)
            c.rect(cx + 0.04 * inch, line_y2 - cb / 2, cb, cb, fill=0, stroke=1)
            c.setStrokeColor(RULE)
            c.line(cx + 0.04 * inch + cb + 0.03 * inch, line_y2,
                   cx + col_w - 0.06 * inch, line_y2)
            line_y2 -= line_gap

    # Outer border for daily area
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.rect(lm, BOT_M + 0.25 * inch, text_w, day_area_y - (BOT_M + 0.25 * inch),
           fill=0, stroke=1)


# ── Notes page ───────────────────────────────────────────────────────────────

def draw_notes_page(c, page_num, label="NOTES"):
    lm = left_margin(page_num)
    rm = right_margin(page_num)
    text_w = PAGE_W - lm - rm
    y = PAGE_H - TOP_M

    draw_page_border(c, page_num)
    draw_footer(c, page_num, label)

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(lm + text_w / 2, y - 0.35 * inch, label)

    c.setStrokeColor(NAVY)
    c.setLineWidth(1.5)
    c.line(lm, y - 0.52 * inch, lm + text_w, y - 0.52 * inch)

    line_y = y - 0.80 * inch
    spacing = 0.27 * inch
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    while line_y > BOT_M + 0.15 * inch:
        c.line(lm, line_y, lm + text_w, line_y)
        line_y -= spacing


# ── Main ──────────────────────────────────────────────────────────────────────

def build_planner():
    c = canvas.Canvas(OUTPUT_FILE, pagesize=letter)
    c.setTitle(f"Weekly Planner {PLANNER_YEAR}")
    c.setAuthor("KDP Planner")
    c.setSubject("Printable Weekly Planner")

    page = 0

    # ── Cover (page 1) ───────────────────────────────────────────────────────
    draw_cover(c)
    c.showPage()
    page += 1

    # ── How to Use (page 2) ──────────────────────────────────────────────────
    page += 1
    draw_how_to_use(c, page)
    c.showPage()

    # ── Yearly Goals (page 3) ────────────────────────────────────────────────
    page += 1
    draw_yearly_goals(c, page)
    c.showPage()

    # ── Blank verso before first month (page 4 — even, back of goals) ───────
    page += 1
    draw_notes_page(c, page, "NOTES")
    c.showPage()

    # ── 12 Monthly Overviews ─────────────────────────────────────────────────
    for mi in range(12):
        page += 1
        draw_monthly_overview(c, page, mi)
        c.showPage()

        # blank verso / notes page facing the monthly overview
        page += 1
        draw_notes_page(c, page, f"NOTES — {MONTH_NAMES[mi]}")
        c.showPage()

    # ── 52 Weekly Spreads ────────────────────────────────────────────────────
    for w in range(1, 53):
        page += 1
        draw_weekly_spread(c, page, w)
        c.showPage()

    # ── Back matter: 8 Notes pages ──────────────────────────────────────────
    for i in range(1, 9):
        page += 1
        draw_notes_page(c, page, f"NOTES  ({i}/8)")
        c.showPage()

    c.save()
    print(f"Saved → {OUTPUT_FILE}  ({page} pages)")


if __name__ == "__main__":
    build_planner()
