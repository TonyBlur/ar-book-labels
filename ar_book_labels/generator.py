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
# Page (A4 portrait, units in mm)
PAGE_W = 210
PAGE_H = 297

# Grid: 4 columns x 9 rows = 36 labels per page
COLS_X = [2, 54, 106, 158]
ROWS_Y = [13.5, 43.5, 73.5, 103.5, 133.5, 163.5, 193.5, 223.5, 253.5]
LABEL_W = 50
LABEL_H = 30
LABEL_RX = 4
LABELS_PER_PAGE = len(COLS_X) * len(ROWS_Y)  # 36

FONT = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"

# Default column names (matching the template)
DEFAULT_COLUMNS = {
    "title": "AR Title",
    "author": "AR Author",
    "level": "Book Level",
    "points": "AR Points",
    "quiz": "Quiz Number",
}
REQUIRED_FIELDS = ["title", "author", "level", "points", "quiz"]

# Label internal coordinates (50 wide x 30 high, units in mm)
CX, CY, CR = 11, 18, 6.5       # Badge circle: cx=11, cy=18(下移2), bottom=24.5
RX = 21                        # Right-side text area x start
VX = 34                        # Points/Quiz value x (center anchor, 右移4)
TOP_Y = 4                      # Top text baseline/start y
AUTHOR_LH = 3.2                # Author line height
TITLE_LH = 3.6                 # Title line height
POINTS_Y = 17.2                # Points row (下移2)
QUIZ_Y = 21.7                  # Quiz row (下移2); bottom ≈ 24.5 = circle bottom


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


def read_books(excel_path, sheet_name, columns=None, start_row=2):
    """Read book data from an Excel file.

    Args:
        excel_path: Path to the .xlsx file.
        sheet_name: Name of the sheet to read.
        columns: Dict mapping internal keys to Excel column names.
                 Missing keys fall back to DEFAULT_COLUMNS.
        start_row: 1-indexed row number where data begins (1 = header row).

    Returns:
        tuple: (books_list, warnings_list)
    """
    cols = {**DEFAULT_COLUMNS, **(columns or {})}
    wb = load_workbook(excel_path, read_only=True, data_only=True)
    if sheet_name is None:
        ws = wb.worksheets[0]
    else:
        ws = wb[sheet_name]
    actual_sheet_name = ws.title
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(h) for h in rows[0] if h is not None]

    # Check that required columns exist in the sheet
    missing_cols = []
    for key in REQUIRED_FIELDS:
        if cols[key] not in headers:
            missing_cols.append(f"{key} ('{cols[key]}')")
    if missing_cols:
        wb.close()
        raise ValueError(
            f"Columns not found in sheet '{actual_sheet_name}': {', '.join(missing_cols)}.\n"
            f"Available columns: {', '.join(headers)}\n"
            f"Use --col-* options to map your column names."
        )

    books = []
    warnings = []
    data_rows = rows[start_row - 1:]  # start_row is 1-indexed
    for i, row in enumerate(data_rows):
        row_num = start_row + i
        vals = list(row[:len(headers)])
        if all(v is None for v in vals):
            continue
        raw = dict(zip(headers, vals))

        # Validate required fields
        missing = []
        for key in REQUIRED_FIELDS:
            val = raw.get(cols[key])
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(cols[key])
        if missing:
            warnings.append(f"Row {row_num}: skipped — missing: {', '.join(missing)}")
            continue

        books.append({
            "title": raw[cols["title"]],
            "author": raw[cols["author"]],
            "level": raw[cols["level"]],
            "points": raw[cols["points"]],
            "quiz": raw[cols["quiz"]],
        })

    wb.close()
    return books, warnings


def _generate_label_svg(book, bw=False):
    """Generate SVG markup for a single label.

    Args:
        book: Dict with title, author, level, points, quiz.
        bw: When True, render in black-and-white mode — white circle with a
            thin black outline and a black level number. When False (default),
            use the standard AR color-coded badge.

    Returns:
        SVG markup string for the label (a ``<g>`` element).
    """
    title_raw = book.get("title", "") or ""
    level = book.get("level", 0)
    points = str(book.get("points", ""))
    quiz = str(book.get("quiz", ""))

    level_str = f"{float(level):.1f}" if isinstance(level, (int, float)) else str(level)
    badge_color = get_level_color(level)
    badge_text = get_badge_text_color(badge_color)

    # bw mode overrides the badge fill/outline and the level number color.
    circle_fill = "white" if bw else badge_color
    circle_stroke = ' stroke="black" stroke-width="0.3"' if bw else ""
    level_fill = "black" if bw else badge_text

    author_raw = str(book.get("author", "") or "").strip()
    author_display = html_module.escape(
        author_raw if len(author_raw) <= 17 else author_raw[:16].rstrip() + "\u2026"
    )
    title_lines = [html_module.escape(l) for l in split_text_lines(title_raw, 14)]
    title_start = TOP_Y + AUTHOR_LH + 0.5
    title_ys = [title_start + i * TITLE_LH for i in range(len(title_lines))]

    p = []
    p.append(f'<rect class="label-outline" x="0" y="0" width="{LABEL_W}" height="{LABEL_H}" rx="{LABEL_RX}" fill="none"/>')
    p.append(f'<circle cx="{CX}" cy="{CY}" r="{CR}" fill="{circle_fill}"{circle_stroke}/>')
    p.append(f'<text x="{CX}" y="{TOP_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="4.5" font-weight="700" letter-spacing="0.3">ATOS</text>')
    p.append(f'<text x="{CX}" y="{CY + 2.5}" text-anchor="middle" fill="{level_fill}" font-family="{FONT}" font-size="5.5" font-weight="700">{level_str}</text>')
    p.append(f'<text x="{RX}" y="{TOP_Y}" dominant-baseline="hanging" fill="#555" font-family="{FONT}" font-size="2.6">{author_display}</text>')
    for y in title_ys:
        p.append(f'<text x="{RX}" y="{y}" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="3.2" font-weight="600">{title_lines[title_ys.index(y)]}</text>')
    p.append(f'<text x="{RX}" y="{POINTS_Y}" dominant-baseline="hanging" fill="#666" font-family="{FONT}" font-size="2.5">Points:</text>')
    p.append(f'<text x="{VX}" y="{POINTS_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="2.8" font-weight="700">{points}</text>')
    p.append(f'<text x="{RX}" y="{QUIZ_Y}" dominant-baseline="hanging" fill="#666" font-family="{FONT}" font-size="2.5">Quiz:</text>')
    p.append(f'<text x="{VX}" y="{QUIZ_Y}" text-anchor="middle" dominant-baseline="hanging" fill="black" font-family="{FONT}" font-size="2.8" font-weight="700">{quiz}</text>')

    return "<g>\n  " + "\n  ".join(p) + "\n</g>"


def build_html(books, display_scale=1, bw=False):
    """Build a multi-page HTML document with SVG labels.

    Page dimensions are in millimetres (A4 portrait: 210mm x 297mm) so that
    printing is 1:1.  On screen, each page is enlarged via CSS ``transform:
    scale(display_scale)``; ``@media print`` resets the transform to guarantee
    exact physical dimensions.

    Args:
        books: List of book dicts.
        display_scale: Scale factor for screen preview.
        bw: When True, render labels in black-and-white mode.
    """
    pages = []
    for i in range(0, len(books), LABELS_PER_PAGE):
        pages.append(books[i:i + LABELS_PER_PAGE])

    s = display_scale

    page_blocks = []
    for page_idx, page_books in enumerate(pages):
        labels_svg = ""
        for i, book in enumerate(page_books):
            row = i // len(COLS_X)
            col = i % len(COLS_X)
            x = COLS_X[col]
            y = ROWS_Y[row]
            labels_svg += f'<g transform="translate({x},{y})">{_generate_label_svg(book, bw=bw)}</g>\n'

        pb = ' style="page-break-after: always;"' if page_idx < len(pages) - 1 else ''
        page_blocks.append(f'''<div class="page"{pb}>
<svg width="{PAGE_W}mm" height="{PAGE_H}mm" viewBox="0 0 {PAGE_W} {PAGE_H}" xmlns="http://www.w3.org/2000/svg">
<rect width="{PAGE_W}" height="{PAGE_H}" fill="white"/>
{labels_svg}
</svg>
</div>''')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AR Book Labels</title>
<style>
  @page {{ size: {PAGE_W}mm {PAGE_H}mm; margin: 0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #e0e0e0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }}
  .page {{
    width: {PAGE_W}mm;
    height: {PAGE_H}mm;
    margin: 0 auto;
    margin-bottom: calc(10px + {PAGE_H}mm * ({s} - 1));
    background: white;
    transform: scale({s});
    transform-origin: top center;
  }}
  .page svg {{ display: block; }}
  .label-outline {{
    fill: none;
    stroke: #999999;
    stroke-width: 0.2;
    stroke-dasharray: 1.2, 1.2;
  }}
  @media print {{
    body {{ margin: 0; background: white; }}
    .page {{
      transform: none;
      margin: 0 !important;
      page-break-after: always;
    }}
    .page:last-child {{ page-break-after: auto; }}
    .label-outline {{ stroke: none; }}
  }}
</style>
</head>
<body>
{"".join(page_blocks)}
</body>
</html>'''


def generate(excel_path, output_path, sheet_name=None,
             column_mapping=None, start_row=2, display_scale=1, bw=False):
    """High-level entry point: read Excel, generate labels, write HTML.

    Args:
        excel_path: Path to the .xlsx file.
        output_path: Output HTML file path.
        sheet_name: Sheet name to read; None means the first sheet.
        column_mapping: Optional dict mapping internal keys to Excel column names.
        start_row: 1-indexed row number where data begins.
        display_scale: Scale factor for screen preview.
        bw: When True, render labels in black-and-white mode (white circle,
            thin black outline, black level number).

    Returns:
        tuple: (number_of_books, number_of_pages, warnings_list)
    """
    books, warnings = read_books(
        excel_path, sheet_name, columns=column_mapping, start_row=start_row
    )
    if not books:
        html = build_html([], display_scale, bw=bw)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return 0, 0, warnings

    html = build_html(books, display_scale, bw=bw)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    n_pages = (len(books) + LABELS_PER_PAGE - 1) // LABELS_PER_PAGE
    return len(books), n_pages, warnings
