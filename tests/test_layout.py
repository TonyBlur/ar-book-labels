"""Tests for ar_book_labels.layout module."""

import math
import pytest

from ar_book_labels.layout import Layout, PRESETS, _parse_label_size_value


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
