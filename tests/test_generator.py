"""Tests for ar-book-labels generator."""

from ar_book_labels.generator import (
    get_level_color,
    get_badge_text_color,
    split_text_lines,
    read_books,
    build_html,
    LABELS_PER_PAGE,
)


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
