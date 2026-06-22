"""Core label generation logic."""

import html as html_module
from pathlib import Path

from openpyxl import load_workbook

# ==================== AR Level Standard Colors ====================
LEVEL_COLORS = [
    (0.1, 1.5, "#FFD700"),   # yellow
    (1.6, 2.0, "#2E8B57"),   # green
    (2.1, 2.5, "#00008B"),   # dark blue
    (2.6, 3.0, "#DC143C"),   # red
    (3.1, 3.5, "#FF69B4"),   # pink
    (3.6, 4.0, "#800080"),   # purple
    (4.1, 4.5, "#FF8C00"),   # orange
    (4.6, 5.0, "#00BFFF"),   # light blue
    (5.1, 5.5, "#FF6600"),   # neon orange
    (5.6, 6.0, "#39FF14"),   # neon green
    (6.1, 6.5, "#1C1C1C"),   # black
    (6.6, 99.0, "#8B4513"),  # brown
]

# ==================== SVG Layout Constants ====================
COLS_X = [6.5, 78.5, 152.5, 224.5]
ROWS_Y = [20.5, 62.5, 104.5, 146.5, 188.5, 230.5, 272.5, 314.5, 356.5, 398.5, 440.5]
LABEL_H = 38
LABEL_RX = 11.5
LABELS_PER_PAGE = len(COLS_X) * len(ROWS_Y)  # 44

FONT = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"

# Circle position
CX, CY, CR = 12.5, 24, 8
# Right-side content
RX = 27
VX = 42
# Fixed Y positions
TOP_Y = 5.5
AUTHOR_LH = 4.0
TITLE_LH = 4.5
POINTS_Y = 22
QUIZ_Y = 28


def get_level_color(level):
    try:
        level = float(level)
    except (TypeError, ValueError):
        return "#999999"
    for low, high, color in LEVEL_COLORS:
        if low <= level <= high:
            return color
    return "#999999"


def get_badge_text_color(bg_color):
    light = {"#FFD700", "#39FF14"}
    return "#000000" if bg_color in light else "#FFFFFF"


def split_text_lines(text, max_chars_per_line):
    """Wrap text into at most 2 lines; truncate with ellipsis only if >2 lines."""
    text = str(text).strip()
    if not text:
        return [text]
    if len(text) <= max_chars_per_line:
        return [text]
    split_pos = text.rfind(" ", 0, max_chars_per_line)
    if split_pos == -1:
        split_pos = max_chars_per_line
    line1 = text[:split_pos].rstrip()
    remainder = text[split_pos:].lstrip()
    if len(remainder) <= max_chars_per_line:
        return [line1, remainder]
    return [line1, remainder[:max_chars_per_line - 1].rstrip() + "\u2026"]


def read_books(excel_path, sheet_name, filter_success=True):
    """Read book data from an Excel file."""
    wb = load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    headers = [h for h in rows[0] if h is not None]
    books = []
    for row in rows[1:]:
        vals = list(row[:len(headers)])
        if all(v is None for v in vals):
            continue
        book = dict(zip(headers, vals))
        if filter_success and book.get("Match Status") != "Success":
            continue
        if book.get("AR Title") is None:
            continue
        books.append(book)
    wb.close()
    return books


def _generate_label_svg(book):
    """Generate SVG markup for a single label."""
    title_raw = book.get("AR Title", "") or ""
    level = book.get("Book Level", 0)
    points = str(book.get("AR Points", ""))
    quiz = str(book.get("Quiz Number", ""))

    level_str = f"{float(level):.1f}" if isinstance(level, (int, float)) else str(level)
    badge_color = get_level_color(level)
    badge_text = get_badge_text_color(badge_color)

    author_raw = str(book.get("AR Author", "") or "").strip()
    author_display = html_module.escape(
        author_raw if len(author_raw) <= 23 else author_raw[:22].rstrip() + "\u2026"
    )
    title_lines = [html_module.escape(l) for l in split_text_lines(title_raw, 19)]
    title_start = TOP_Y + AUTHOR_LH + 0.5
    title_ys = [title_start + i * TITLE_LH for i in range(len(title_lines))]

    p = []
    p.append(f'<rect x="0" y="0" width="68" height="{LABEL_H}" rx="{LABEL_RX}" fill="#F1F1F1" stroke="black" stroke-width="0.5"/>')
    p.append(f'<circle cx="{CX}" cy="{CY}" r="{CR}" fill="{badge_color}"/>')
    p.append(f'<text x="{CX}" y="{TOP_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="5.5" font-weight="700" letter-spacing="0.3">AR</text>')
    p.append(f'<text x="{CX}" y="{CY + 2.5}" text-anchor="middle" fill="{badge_text}" font-family="{FONT}" font-size="6.5" font-weight="700">{level_str}</text>')
    p.append(f'<text x="{RX}" y="{TOP_Y}" dominant-baseline="hanging" fill="#555" font-family="{FONT}" font-size="3.3">{author_display}</text>')
    for y in title_ys:
        p.append(f'<text x="{RX}" y="{y}" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="4" font-weight="600">{title_lines[title_ys.index(y)]}</text>')
    p.append(f'<text x="{RX}" y="{POINTS_Y}" dominant-baseline="hanging" fill="#666" font-family="{FONT}" font-size="3.2">Points:</text>')
    p.append(f'<text x="{VX}" y="{POINTS_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="3.5" font-weight="700">{points}</text>')
    p.append(f'<text x="{RX}" y="{QUIZ_Y}" dominant-baseline="hanging" fill="#666" font-family="{FONT}" font-size="3.2">Quiz:</text>')
    p.append(f'<text x="{VX}" y="{QUIZ_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="3.5" font-weight="700">{quiz}</text>')

    return "<g>\n  " + "\n  ".join(p) + "\n</g>"


def build_html(books, display_scale=3):
    """Build a multi-page HTML document with SVG labels."""
    pages = []
    for i in range(0, len(books), LABELS_PER_PAGE):
        pages.append(books[i:i + LABELS_PER_PAGE])

    s = display_scale
    page_w = 300 * s
    page_h = 500 * s

    page_blocks = []
    for page_idx, page_books in enumerate(pages):
        labels_svg = ""
        for i, book in enumerate(page_books):
            row = i // len(COLS_X)
            col = i % len(COLS_X)
            x = COLS_X[col]
            y = ROWS_Y[row]
            labels_svg += f'<g transform="translate({x},{y})">{_generate_label_svg(book)}</g>\n'

        pb = ' style="page-break-after: always;"' if page_idx < len(pages) - 1 else ''
        page_blocks.append(f'''<div class="page"{pb}>
<svg width="{page_w}" height="{page_h}" viewBox="0 0 300 500" xmlns="http://www.w3.org/2000/svg">
<rect width="300" height="500" fill="white"/>
{labels_svg}
</svg>
</div>''')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AR Book Labels</title>
<style>
  @page {{ size: {page_w}px {page_h}px; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #e0e0e0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }}
  .page {{ width: {page_w}px; height: {page_h}px; margin: 10px auto; background: white; }}
  .page svg {{ display: block; }}
  @media print {{
    body {{ margin: 0; background: white; }}
    .page {{ margin: 0; page-break-after: always; }}
    .page:last-child {{ page-break-after: auto; }}
  }}
</style>
</head>
<body>
{"".join(page_blocks)}
</body>
</html>'''


def generate(excel_path, output_path, sheet_name="Merged",
             filter_success=True, display_scale=3):
    """High-level entry point: read Excel, generate labels, write HTML.

    Returns:
        tuple: (number_of_books, number_of_pages)
    """
    books = read_books(excel_path, sheet_name, filter_success=filter_success)
    if not books:
        html = build_html([], display_scale)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return 0, 0

    html = build_html(books, display_scale)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    n_pages = (len(books) + LABELS_PER_PAGE - 1) // LABELS_PER_PAGE
    return len(books), n_pages
