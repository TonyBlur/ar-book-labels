"""Tests for ar_book_labels.layout module."""

import math
import pytest

from ar_book_labels.layout import Layout, PRESETS, PAGE_PRESETS, _parse_label_size_value, _parse_page_size_value


# ---------------------------------------------------------------------------
# Default Layout (50×30 mm)
# ---------------------------------------------------------------------------

class TestDefaultLayout:
    """Verify that the default Layout reproduces the original 50×30 grid."""

    def test_grid_dimensions(self):
        layout = Layout()
        assert layout.cols == 4
        assert layout.rows == 9
        assert layout.labels_per_page == 36

    def test_cols_x(self):
        layout = Layout()
        expected = [2.0, 54.0, 106.0, 158.0]
        assert layout.cols_x == pytest.approx(expected, abs=1e-6)

    def test_rows_y(self):
        layout = Layout()
        expected = [13.5 + j * 30.0 for j in range(9)]
        assert layout.rows_y == pytest.approx(expected, abs=1e-6)

    def test_internal_coords_unchanged(self):
        """For 50×30, scale factors are 1.0 → internal coords match baseline."""
        layout = Layout()
        assert layout.cx == pytest.approx(11.0)
        assert layout.cy == pytest.approx(18.0)
        assert layout.cr == pytest.approx(6.5)
        assert layout.rx == pytest.approx(21.0)
        assert layout.vx == pytest.approx(34.0)
        assert layout.top_y == pytest.approx(4.0)
        assert layout.author_lh == pytest.approx(3.2)
        assert layout.title_lh == pytest.approx(3.6)
        assert layout.points_y == pytest.approx(17.2)
        assert layout.quiz_y == pytest.approx(21.7)


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

class TestPresets:
    """Verify grid dimensions for every preset."""

    def test_preset_50x30(self):
        layout = Layout.from_config({"label_size": "50x30"})
        assert layout.cols == 4
        assert layout.rows == 9
        assert layout.labels_per_page == 36

    def test_preset_70x37(self):
        layout = Layout.from_config({"label_size": "70x37"})
        assert layout.cols == 3
        assert layout.rows == 7
        assert layout.labels_per_page == 21

    def test_preset_63x38(self):
        layout = Layout.from_config({"label_size": "63x38"})
        assert layout.cols == 3
        assert layout.rows == 7
        assert layout.labels_per_page == 21

    def test_preset_99x38(self):
        layout = Layout.from_config({"label_size": "99x38"})
        assert layout.cols == 2
        assert layout.rows == 7
        assert layout.labels_per_page == 14

    def test_all_presets_have_positive_grid(self):
        for name in PRESETS:
            layout = Layout.from_config({"label_size": name})
            assert layout.cols >= 1, f"{name}: cols should be >= 1"
            assert layout.rows >= 1, f"{name}: rows should be >= 1"
            assert layout.labels_per_page == layout.cols * layout.rows


# ---------------------------------------------------------------------------
# Custom sizes
# ---------------------------------------------------------------------------

class TestCustomSize:
    """Verify behaviour with non-preset label sizes."""

    def test_custom_small_label(self):
        layout = Layout(label_w=25, label_h=15)
        # available_w = 210 - 2*2 = 206; cols = floor((206+2)/(25+2)) = floor(208/27) = 7
        assert layout.cols == 7
        assert layout.labels_per_page == layout.cols * layout.rows

    def test_custom_large_label(self):
        layout = Layout(label_w=100, label_h=50, margin_x=0, margin_y=0, col_gap=0, row_gap=0)
        assert layout.cols == 2  # floor(210/100) = 2
        assert layout.rows == 5  # floor(297/50) = 5


# ---------------------------------------------------------------------------
# Internal coordinate scaling
# ---------------------------------------------------------------------------

class TestInternalScaling:
    """Verify proportional scaling of internal coordinates."""

    def test_scale_x_only(self):
        """Double the width → cx, rx, vx should double."""
        layout = Layout(label_w=100, label_h=30)
        assert layout.cx == pytest.approx(22.0)
        assert layout.rx == pytest.approx(42.0)
        assert layout.vx == pytest.approx(68.0)

    def test_scale_y_only(self):
        """Double the height → cy, top_y, points_y, quiz_y should double."""
        layout = Layout(label_w=50, label_h=60)
        assert layout.cy == pytest.approx(36.0)
        assert layout.top_y == pytest.approx(8.0)
        assert layout.points_y == pytest.approx(34.4)
        assert layout.quiz_y == pytest.approx(43.4)

    def test_scale_both(self):
        """Scale both dimensions → cr uses average of x and y scales."""
        layout = Layout(label_w=100, label_h=60)
        scale_x = 100 / 50  # 2.0
        scale_y = 60 / 30   # 2.0
        expected_cr = 6.5 * ((scale_x + scale_y) / 2)  # 6.5 * 2.0 = 13.0
        assert layout.cr == pytest.approx(expected_cr)

    def test_scale_asymmetric(self):
        """Non-uniform scaling → cr uses arithmetic mean of scale factors."""
        layout = Layout(label_w=75, label_h=45)  # scale_x=1.5, scale_y=1.5
        expected_cr = 6.5 * 1.5
        assert layout.cr == pytest.approx(expected_cr)


# ---------------------------------------------------------------------------
# Centering
# ---------------------------------------------------------------------------

class TestCentering:
    """Verify that labels are centred horizontally on the page."""

    def test_default_centering(self):
        layout = Layout()
        # For 50x30 with margin_x=2, center_offset_x = 0 → labels start at x=2
        assert layout.cols_x[0] == pytest.approx(2.0)
        # Rightmost label edge: 158 + 50 = 208; page_w = 210; margin = 2
        right_edge = layout.cols_x[-1] + layout.label_w
        assert right_edge == pytest.approx(210.0 - layout.margin_x)

    def test_centered_preset_63x38(self):
        layout = Layout.from_config({"label_size": "63x38"})
        # 3 * 63 = 189; page_w = 210; offset = (210 - 189) / 2 = 10.5
        assert layout.cols_x[0] == pytest.approx(10.5)
        right_edge = layout.cols_x[-1] + layout.label_w
        assert right_edge == pytest.approx(210.0 - 10.5)

    def test_centered_preset_99x38(self):
        layout = Layout.from_config({"label_size": "99x38"})
        # 2 * 99 = 198; offset = (210 - 198) / 2 = 6.0
        assert layout.cols_x[0] == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# from_config
# ---------------------------------------------------------------------------

class TestFromConfig:
    """Verify the from_config factory method."""

    def test_empty_config(self):
        layout = Layout.from_config({})
        assert layout.label_w == 50.0
        assert layout.label_h == 30.0
        assert layout.cols == 4
        assert layout.rows == 9

    def test_preset_name(self):
        layout = Layout.from_config({"label_size": "70x37"})
        assert layout.label_w == 70.0
        assert layout.label_h == 37.0
        assert layout.cols == 3

    def test_custom_wxh(self):
        layout = Layout.from_config({"label_size": "80x40"})
        assert layout.label_w == 80.0
        assert layout.label_h == 40.0

    def test_invalid_label_size(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            Layout.from_config({"label_size": "abc"})

    def test_negative_label_size(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            Layout.from_config({"label_size": "-10x20"})

    def test_uniform_margin_override(self):
        layout = Layout.from_config({"margin": 10.0})
        assert layout.margin_x == pytest.approx(10.0)
        assert layout.margin_y == pytest.approx(10.0)

    def test_individual_margin_override(self):
        layout = Layout.from_config({"margin_x": 5.0, "margin_y": 8.0})
        assert layout.margin_x == pytest.approx(5.0)
        assert layout.margin_y == pytest.approx(8.0)

    def test_radius_alias(self):
        layout = Layout.from_config({"radius": 6.0})
        assert layout.label_rx == pytest.approx(6.0)

    def test_font_alias(self):
        layout = Layout.from_config({"font": "Arial, sans-serif"})
        assert layout.font_family == "Arial, sans-serif"

    def test_level_colors(self):
        colors = [(0.1, 5.0, "#FF0000"), (5.1, 99.0, "#00FF00")]
        layout = Layout.from_config({"level_colors": colors})
        assert layout.level_colors == colors

    def test_preset_with_override(self):
        """Preset values can be overridden by explicit config keys."""
        layout = Layout.from_config({
            "label_size": "50x30",
            "col_gap": 5.0,
        })
        assert layout.label_w == 50.0
        assert layout.col_gap == pytest.approx(5.0)

    def test_internal_coord_override(self):
        layout = Layout.from_config({"cx": 20.0, "cy": 25.0})
        assert layout.cx == pytest.approx(20.0)
        assert layout.cy == pytest.approx(25.0)


# ---------------------------------------------------------------------------
# _parse_label_size_value
# ---------------------------------------------------------------------------

class TestParseLabelSizeValue:
    """Verify the internal _parse_label_size_value helper."""

    def test_known_preset(self):
        result = _parse_label_size_value("50x30")
        assert result["label_w"] == 50.0
        assert result["label_h"] == 30.0
        assert "margin_x" in result  # preset includes spacing

    def test_custom_wxh(self):
        result = _parse_label_size_value("80x40")
        assert result == {"label_w": 80.0, "label_h": 40.0}

    def test_case_insensitive(self):
        result = _parse_label_size_value("80X40")
        assert result["label_w"] == 80.0

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            _parse_label_size_value("80x40x10")

    def test_non_numeric(self):
        with pytest.raises(ValueError):
            _parse_label_size_value("abc")


# ---------------------------------------------------------------------------
# Manual grid (--grid)
# ---------------------------------------------------------------------------

class TestManualGrid:
    """Verify manual grid override via --grid or config."""

    def test_manual_grid_basic(self):
        """Manual 3x5 grid with 50x30 labels."""
        layout = Layout(grid=(3, 5))
        assert layout.cols == 3
        assert layout.rows == 5
        assert layout.labels_per_page == 15

    def test_manual_grid_single_col(self):
        """Manual 1x9 grid fits with default margins."""
        layout = Layout(grid=(1, 9))
        assert layout.cols == 1
        assert layout.rows == 9

    def test_manual_grid_overrides_auto(self):
        """Manual grid should override auto-computed dimensions."""
        layout = Layout(grid=(2, 3))
        # Without grid, default 50x30 would be 4x9
        assert layout.cols == 2
        assert layout.rows == 3

    def test_manual_grid_horizontal_overflow(self):
        """Grid that exceeds page width should raise ValueError."""
        # 5 cols * 50mm = 250mm > 210mm page width (even with 0 margins)
        with pytest.raises(ValueError, match="too wide"):
            Layout(grid=(5, 1))

    def test_manual_grid_vertical_overflow(self):
        """Grid that exceeds page height should raise ValueError."""
        # 11 rows * 30mm = 330mm > 297mm page height (even with 0 margins)
        with pytest.raises(ValueError, match="too tall"):
            Layout(grid=(1, 11))

    def test_manual_grid_with_custom_margins(self):
        """Manual grid with tighter margins should work where default margins don't."""
        # 3 cols * 50mm + 2 gaps * 2mm = 154mm; with margin_x=5: available=200, fits
        # 9 rows * 30mm = 270mm; with margin_y=5: available=287, fits
        layout = Layout(grid=(3, 9), margin_x=5, margin_y=5)
        assert layout.cols == 3
        assert layout.rows == 9

    def test_manual_grid_from_config_string(self):
        """from_config should parse 'COLSxROWS' string format."""
        layout = Layout.from_config({"grid": "3x7"})
        assert layout.cols == 3
        assert layout.rows == 7

    def test_manual_grid_from_config_tuple(self):
        """from_config should accept (cols, rows) tuple."""
        layout = Layout.from_config({"grid": (2, 5)})
        assert layout.cols == 2
        assert layout.rows == 5

    def test_manual_grid_invalid_string(self):
        """Invalid grid string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid grid"):
            Layout.from_config({"grid": "abc"})

    def test_manual_grid_zero_cols(self):
        """Grid with 0 columns should raise ValueError."""
        with pytest.raises(ValueError, match="Grid dimensions must be at least 1x1"):
            Layout(grid=(0, 5))

    def test_manual_grid_zero_rows(self):
        """Grid with 0 rows should raise ValueError."""
        with pytest.raises(ValueError, match="Grid dimensions must be at least 1x1"):
            Layout(grid=(3, 0))

    def test_manual_grid_exact_fit(self):
        """Grid that exactly fits the page should work."""
        # 4 cols * 50mm + 3 gaps * 2mm = 206mm; available = 210 - 2*2 = 206mm → exact fit
        layout = Layout(grid=(4, 9))
        assert layout.cols == 4
        assert layout.rows == 9

    def test_manual_grid_centering(self):
        """Manual grid should still center labels horizontally."""
        layout = Layout(grid=(2, 1))
        # 2 cols * 50mm + 1 gap * 2mm = 102mm; available = 206mm
        # offset = (206 - 102) / 2 = 52mm; first label at 2 + 52 = 54mm
        assert layout.cols_x[0] == pytest.approx(54.0)

    def test_manual_grid_auto_shrink_margin_y(self):
        """Grid that needs more height should auto-shrink margin_y."""
        # 9 rows * 31mm = 279mm; default margin_y=13.5 → available=270mm (too small)
        # Auto-shrink: margin_y = (297 - 279) / 2 = 9mm
        layout = Layout(label_w=48, label_h=31, grid=(4, 9))
        assert layout.cols == 4
        assert layout.rows == 9
        assert layout.labels_per_page == 36
        assert layout.margin_y == pytest.approx(9.0)

    def test_manual_grid_auto_shrink_both_margins(self):
        """Grid that needs more space should auto-shrink both margins."""
        # 5 cols * 40mm + 4 gaps * 2mm = 208mm; default margin_x=2 → available=206mm (too small)
        # Auto-shrink: margin_x = (210 - 208) / 2 = 1mm
        # 9 rows * 31mm = 279mm; default margin_y=13.5 → available=270mm (too small)
        # Auto-shrink: margin_y = (297 - 279) / 2 = 9mm
        layout = Layout(label_w=40, label_h=31, grid=(5, 9))
        assert layout.cols == 5
        assert layout.rows == 9
        assert layout.margin_x == pytest.approx(1.0)
        assert layout.margin_y == pytest.approx(9.0)

    def test_manual_grid_no_shrink_if_fits(self):
        """Grid that fits with default margins should NOT change margins."""
        layout = Layout(grid=(3, 5))
        assert layout.margin_x == pytest.approx(2.0)   # unchanged
        assert layout.margin_y == pytest.approx(13.5)  # unchanged


# ---------------------------------------------------------------------------
# Page size presets
# ---------------------------------------------------------------------------

class TestPagePresets:
    """Verify page-size presets and custom page sizes."""

    def test_default_is_a4(self):
        layout = Layout()
        assert layout.page_w == pytest.approx(210.0)
        assert layout.page_h == pytest.approx(297.0)

    def test_a4_preset(self):
        layout = Layout.from_config({"page_size": "A4"})
        assert layout.page_w == pytest.approx(210.0)
        assert layout.page_h == pytest.approx(297.0)

    def test_letter_preset(self):
        layout = Layout.from_config({"page_size": "Letter"})
        assert layout.page_w == pytest.approx(215.9)
        assert layout.page_h == pytest.approx(279.4)

    def test_custom_page_size(self):
        layout = Layout.from_config({"page_size": "150x200"})
        assert layout.page_w == pytest.approx(150.0)
        assert layout.page_h == pytest.approx(200.0)

    def test_a5_preset_grid(self):
        """A5 (148x210) should fit fewer labels than A4."""
        layout_a5 = Layout.from_config({"page_size": "A5"})
        layout_a4 = Layout()
        assert layout_a5.labels_per_page < layout_a4.labels_per_page

    def test_a3_preset_grid(self):
        """A3 (297x420) should fit more labels than A4."""
        layout_a3 = Layout.from_config({"page_size": "A3"})
        layout_a4 = Layout()
        assert layout_a3.labels_per_page > layout_a4.labels_per_page

    def test_all_page_presets_positive_grid(self):
        for name in PAGE_PRESETS:
            layout = Layout.from_config({"page_size": name})
            assert layout.cols >= 1, f"{name}: cols should be >= 1"
            assert layout.rows >= 1, f"{name}: rows should be >= 1"

    def test_page_size_case_insensitive(self):
        layout1 = Layout.from_config({"page_size": "a4"})
        layout2 = Layout.from_config({"page_size": "A4"})
        assert layout1.page_w == layout2.page_w

    def test_invalid_page_size(self):
        with pytest.raises(ValueError, match="Invalid page size"):
            Layout.from_config({"page_size": "foobar"})

    def test_page_size_with_label_override(self):
        """page_size + label_size should combine correctly."""
        layout = Layout.from_config({"page_size": "A5", "label_size": "70x37"})
        assert layout.page_w == pytest.approx(148.0)
        assert layout.label_w == pytest.approx(70.0)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    """Verify that invalid/conflicting parameters raise clear errors."""

    def test_negative_label_w(self):
        with pytest.raises(ValueError, match="Label dimensions must be positive"):
            Layout(label_w=-10, label_h=30)

    def test_negative_label_h(self):
        with pytest.raises(ValueError, match="Label dimensions must be positive"):
            Layout(label_w=50, label_h=-5)

    def test_negative_col_gap(self):
        with pytest.raises(ValueError, match="Column gap must be >= 0"):
            Layout(col_gap=-1)

    def test_negative_row_gap(self):
        with pytest.raises(ValueError, match="Row gap must be >= 0"):
            Layout(row_gap=-2)

    def test_negative_margin_x(self):
        with pytest.raises(ValueError, match="Margins must be >= 0"):
            Layout(margin_x=-1)

    def test_negative_margin_y(self):
        with pytest.raises(ValueError, match="Margins must be >= 0"):
            Layout(margin_y=-3)

    def test_margins_exceed_page_width(self):
        """2 * margin_x >= page_w should error."""
        with pytest.raises(ValueError, match="Horizontal margins too large"):
            Layout(margin_x=106)  # 2*106 = 212 >= 210

    def test_margins_exceed_page_height(self):
        """2 * margin_y >= page_h should error."""
        with pytest.raises(ValueError, match="Vertical margins too large"):
            Layout(margin_y=149)  # 2*149 = 298 >= 297

    def test_label_too_wide_for_page(self):
        """Label wider than available space should error."""
        with pytest.raises(ValueError, match="Label width .* exceeds available width"):
            Layout(label_w=250, label_h=30)

    def test_label_too_tall_for_page(self):
        """Label taller than available space should error."""
        with pytest.raises(ValueError, match="Label height .* exceeds available height"):
            Layout(label_w=50, label_h=350)

    def test_label_fits_exactly(self):
        """Label that exactly matches available space should work."""
        # available_w = 210 - 2*0 = 210; label_w = 210 → fits exactly
        layout = Layout(label_w=210, label_h=297, margin_x=0, margin_y=0)
        assert layout.cols == 1
        assert layout.rows == 1

    def test_zero_page_width(self):
        with pytest.raises(ValueError, match="Page dimensions must be positive"):
            Layout(page_w=0, page_h=297)

    def test_zero_page_height(self):
        with pytest.raises(ValueError, match="Page dimensions must be positive"):
            Layout(page_w=210, page_h=0)

    def test_grid_with_label_too_wide(self):
        """Grid + label that exceeds page width should error."""
        # 3 cols * 100mm = 300mm > 210mm page width (even with 0 margins)
        with pytest.raises(ValueError, match="too wide"):
            Layout(label_w=100, label_h=30, grid=(3, 1))

    def test_small_page_large_label(self):
        """Small page with large label should error clearly."""
        with pytest.raises(ValueError, match="Label width .* exceeds available"):
            Layout(page_w=100, page_h=100, label_w=80, label_h=30, margin_x=15)


# ---------------------------------------------------------------------------
# _parse_page_size_value
# ---------------------------------------------------------------------------

class TestParsePageSizeValue:
    """Verify the _parse_page_size_value helper."""

    def test_a4_preset(self):
        w, h = _parse_page_size_value("A4")
        assert w == pytest.approx(210.0)
        assert h == pytest.approx(297.0)

    def test_letter_preset(self):
        w, h = _parse_page_size_value("Letter")
        assert w == pytest.approx(215.9)
        assert h == pytest.approx(279.4)

    def test_custom_wxh(self):
        w, h = _parse_page_size_value("150x200")
        assert w == pytest.approx(150.0)
        assert h == pytest.approx(200.0)

    def test_case_insensitive(self):
        w1, h1 = _parse_page_size_value("a4")
        w2, h2 = _parse_page_size_value("A4")
        assert w1 == w2 and h1 == h2

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid page size"):
            _parse_page_size_value("abc")

    def test_negative_dimensions(self):
        with pytest.raises(ValueError, match="Invalid page size"):
            _parse_page_size_value("-100x200")
