"""Tests for ar-book-labels generator."""

from ar_book_labels.generator import (
    get_level_color,
    get_badge_text_color,
    split_text_lines,
    read_books,
    build_html,
    LABELS_PER_PAGE,
)
from ar_book_labels.layout import Layout


# ---------------------------------------------------------------------------
# Original tests (backward compatibility)
# ---------------------------------------------------------------------------

def test_level_colors():
    assert get_level_color(1.0) == "#FFD700"  # yellow
    assert get_level_color(1.8) == "#2E8B57"  # green
    assert get_level_color(2.3) == "#00008B"  # dark blue
    assert get_level_color(2.8) == "#DC143C"  # red
    assert get_level_color(3.3) == "#FF69B4"  # pink
    assert get_level_color(3.8) == "#800080"  # purple
    assert get_level_color(4.3) == "#FF8C00"  # orange
    assert get_level_color(4.8) == "#00BFFF"  # light blue
    assert get_level_color(5.1) == "#FF6600"  # neon orange
    assert get_level_color(5.8) == "#39FF14"  # neon green
    assert get_level_color(6.3) == "#1C1C1C"  # black
    assert get_level_color(7.0) == "#8B4513"  # brown
    assert get_level_color(0.0) == "#999999"  # out of range → grey
    assert get_level_color("invalid") == "#999999"


def test_level_colors_custom():
    """get_level_color with a custom colour list."""
    custom = [(0.0, 3.0, "#111111"), (3.1, 99.0, "#EEEEEE")]
    assert get_level_color(2.0, colors=custom) == "#111111"
    assert get_level_color(5.0, colors=custom) == "#EEEEEE"
    assert get_level_color(0.0, colors=custom) == "#111111"


def test_badge_text_color():
    assert get_badge_text_color("#FFD700") == "#000000"  # yellow → black text
    assert get_badge_text_color("#39FF14") == "#000000"  # neon green → black text
    assert get_badge_text_color("#00008B") == "#FFFFFF"  # dark blue → white text
    assert get_badge_text_color("#1C1C1C") == "#FFFFFF"  # black → white text


def test_split_text_lines_single():
    assert split_text_lines("Short", 19) == ["Short"]
    assert split_text_lines("", 19) == [""]


def test_split_text_lines_wrap():
    result = split_text_lines("Diary of a Wimpy Kid: The Last Straw", 19)
    assert len(result) == 2
    assert result[0] == "Diary of a Wimpy"
    assert result[1] == "Kid: The Last Straw"


def test_split_text_lines_truncate():
    # This text needs 3 lines at 19 chars, so line 2 gets truncated
    result = split_text_lines("The Journey to the Center of the Earth is Great", 19)
    assert len(result) == 2
    assert result[0] == "The Journey to the"
    assert result[1].endswith("\u2026")  # ellipsis on truncated line 2


def test_split_text_lines_no_space():
    # Very long single word exceeding 2 lines
    result = split_text_lines("A" * 50, 19)
    assert len(result) == 2
    assert result[1].endswith("\u2026")


def test_build_html_empty():
    html = build_html([])
    assert "<!DOCTYPE html>" in html
    assert "AR Book Labels" in html
    assert "<svg" not in html  # no pages


def test_build_html_single_book():
    book = {
        "title": "Test Book",
        "author": "Test Author",
        "level": 3.5,
        "points": 5,
        "quiz": 12345,
    }
    html = build_html([book])
    assert "Test Book" in html
    assert "Test Author" in html
    assert "12345" in html
    assert html.count('<div class="page"') == 1


def test_build_html_multi_page():
    books = [
        {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "level": 2.0,
            "points": 1,
            "quiz": i,
        }
        for i in range(LABELS_PER_PAGE + 1)
    ]
    html = build_html(books)
    assert html.count('<div class="page"') == 2


# ---------------------------------------------------------------------------
# New tests: Layout-based API
# ---------------------------------------------------------------------------

def test_build_html_with_custom_layout():
    """build_html with a custom Layout should produce correct dimensions."""
    layout = Layout.from_config({"label_size": "70x37"})
    book = {
        "title": "Test Book",
        "author": "Test Author",
        "level": 3.5,
        "points": 5,
        "quiz": 12345,
    }
    html = build_html([book], layout=layout)
    # Page dimensions should match the layout
    assert 'width="210mm"' in html
    assert 'height="297mm"' in html
    # Label should be present
    assert "Test Book" in html
    assert "Test Author" in html


def test_build_html_with_custom_colors():
    """Custom level_colors should be used when provided."""
    custom_colors = [(0.0, 99.0, "#FF0000")]  # all red
    layout = Layout(level_colors=custom_colors)
    book = {
        "title": "Red Book",
        "author": "Author",
        "level": 3.0,
        "points": 1,
        "quiz": 100,
    }
    html = build_html([book], layout=layout)
    # The badge should use the custom colour
    assert '#FF0000' in html


def test_build_html_with_custom_font():
    """Custom font_family should appear in the SVG."""
    layout = Layout(font_family="Arial, sans-serif")
    book = {
        "title": "Font Test",
        "author": "Author",
        "level": 2.0,
        "points": 1,
        "quiz": 100,
    }
    html = build_html([book], layout=layout)
    assert "Arial, sans-serif" in html


def test_build_html_default_layout_backward_compat():
    """build_html() without layout should produce the same output as before."""
    book = {
        "title": "Compat Test",
        "author": "Author",
        "level": 2.0,
        "points": 1,
        "quiz": 100,
    }
    # Call without layout (backward compatible)
    html_no_layout = build_html([book])
    # Call with default Layout
    html_default_layout = build_html([book], layout=Layout())
    # They should be identical
    assert html_no_layout == html_default_layout


def test_build_html_page_count_with_custom_layout():
    """Page count should respect layout.labels_per_page."""
    layout = Layout.from_config({"label_size": "70x37"})  # 21 labels/page
    books = [
        {"title": f"Book {i}", "author": "A", "level": 2.0, "points": 1, "quiz": i}
        for i in range(22)  # 22 books → 2 pages (21 + 1)
    ]
    html = build_html(books, layout=layout)
    assert html.count('<div class="page"') == 2


def test_build_html_bw_mode_with_layout():
    """B&W mode should work correctly with a custom layout."""
    layout = Layout(label_w=70, label_h=37, margin_x=0, margin_y=0, col_gap=0, row_gap=0)
    book = {
        "title": "BW Test",
        "author": "Author",
        "level": 3.0,
        "points": 1,
        "quiz": 100,
    }
    html = build_html([book], bw=True, layout=layout)
    assert 'fill="white"' in html  # circle fill in bw mode
    assert 'stroke="black"' in html  # circle stroke in bw mode
