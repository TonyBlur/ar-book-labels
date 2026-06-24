"""Tests for ar_book_labels.config module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from ar_book_labels.config import load_config, merge_configs, parse_label_size, parse_colors


# ---------------------------------------------------------------------------
# parse_label_size
# ---------------------------------------------------------------------------

class TestParseLabelSize:

    def test_preset_50x30(self):
        result = parse_label_size("50x30")
        assert result["label_w"] == 50.0
        assert result["label_h"] == 30.0
        assert "col_gap" in result

    def test_preset_70x37(self):
        result = parse_label_size("70x37")
        assert result["label_w"] == 70.0
        assert result["label_h"] == 37.0

    def test_custom_wxh(self):
        result = parse_label_size("80x40")
        assert result == {"label_w": 80.0, "label_h": 40.0}

    def test_custom_wxh_decimal(self):
        result = parse_label_size("63.5x38.1")
        assert result["label_w"] == pytest.approx(63.5)
        assert result["label_h"] == pytest.approx(38.1)

    def test_invalid_string(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            parse_label_size("abc")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            parse_label_size("80x40x10")

    def test_negative_size(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            parse_label_size("-10x20")

    def test_zero_size(self):
        with pytest.raises(ValueError, match="Invalid label size"):
            parse_label_size("0x20")


# ---------------------------------------------------------------------------
# parse_colors
# ---------------------------------------------------------------------------

class TestParseColors:

    def test_single_range(self):
        result = parse_colors("0.1-1.5:#FFD700")
        assert result == [(0.1, 1.5, "#FFD700")]

    def test_multiple_ranges(self):
        result = parse_colors("0.1-1.5:#FFD700,1.6-2.0:#2E8B57")
        assert len(result) == 2
        assert result[0] == (0.1, 1.5, "#FFD700")
        assert result[1] == (1.6, 2.0, "#2E8B57")

    def test_full_ar_scheme(self):
        colors_str = (
            "0.1-1.5:#FFD700,1.6-2.0:#2E8B57,2.1-2.5:#00008B,"
            "2.6-3.0:#DC143C,3.1-3.5:#FF69B4,3.6-4.0:#800080,"
            "4.1-4.5:#FF8C00,4.6-5.0:#00BFFF,5.1-5.5:#FF6600,"
            "5.6-6.0:#39FF14,6.1-6.5:#1C1C1C,6.6-99.0:#8B4513"
        )
        result = parse_colors(colors_str)
        assert len(result) == 12
        assert result[0] == (0.1, 1.5, "#FFD700")
        assert result[-1] == (6.6, 99.0, "#8B4513")

    def test_whitespace_handling(self):
        result = parse_colors(" 0.1-1.5:#FFD700 , 1.6-2.0:#2E8B57 ")
        assert len(result) == 2

    def test_invalid_format_missing_colon(self):
        with pytest.raises(ValueError, match="Invalid colour spec"):
            parse_colors("0.1-1.5#FFD700")

    def test_invalid_format_missing_dash(self):
        with pytest.raises(ValueError, match="Invalid colour spec"):
            parse_colors("0.1:1.5:#FFD700")

    def test_empty_string_segments(self):
        result = parse_colors("0.1-1.5:#FFD700,,1.6-2.0:#2E8B57")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# merge_configs
# ---------------------------------------------------------------------------

class TestMergeConfigs:

    def test_empty_merge(self):
        result = merge_configs({}, {}, {})
        assert result == {}

    def test_defaults_only(self):
        result = merge_configs({}, {}, {"label_w": 50})
        assert result == {"label_w": 50}

    def test_file_overrides_defaults(self):
        result = merge_configs({}, {"label_w": 70}, {"label_w": 50})
        assert result["label_w"] == 70

    def test_cli_overrides_file(self):
        result = merge_configs(
            {"label_w": 99},
            {"label_w": 70},
            {"label_w": 50},
        )
        assert result["label_w"] == 99

    def test_none_values_ignored(self):
        result = merge_configs(
            {"label_w": None},
            {"label_h": 37},
            {"label_w": 50, "label_h": 30},
        )
        assert result["label_w"] == 50  # default preserved
        assert result["label_h"] == 37  # file value applied

    def test_margin_propagation(self):
        """CLI --margin should set both margin_x and margin_y."""
        result = merge_configs(
            {"margin": 10.0},
            {},
            {},
        )
        assert result["margin_x"] == 10.0
        assert result["margin_y"] == 10.0

    def test_margin_overrides_file_margins(self):
        """CLI --margin should override per-axis margins from file."""
        result = merge_configs(
            {"margin": 10.0},
            {"margin_x": 2.0, "margin_y": 13.5},
            {},
        )
        assert result["margin_x"] == 10.0
        assert result["margin_y"] == 10.0

    def test_file_margins_without_cli_margin(self):
        """File per-axis margins should be preserved when CLI has no --margin."""
        result = merge_configs(
            {},
            {"margin_x": 5.0, "margin_y": 8.0},
            {},
        )
        assert result["margin_x"] == 5.0
        assert result["margin_y"] == 8.0


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:

    def test_load_json(self, tmp_path):
        config = {"label_size": "70x37", "col_gap": 3}
        path = tmp_path / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        result = load_config(path)
        assert result["label_size"] == "70x37"
        assert result["col_gap"] == 3

    def test_load_yaml(self, tmp_path):
        yaml_content = 'label_size: "70x37"\ncol_gap: 3\n'
        path = tmp_path / "config.yaml"
        path.write_text(yaml_content, encoding="utf-8")
        try:
            result = load_config(path)
            assert result["label_size"] == "70x37"
            assert result["col_gap"] == 3
        except ImportError:
            pytest.skip("PyYAML not installed")

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_unsupported_format(self, tmp_path):
        path = tmp_path / "config.txt"
        path.write_text("hello", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported config format"):
            load_config(path)

    def test_flatten_nested_layout(self, tmp_path):
        """Nested 'layout' section should be flattened to top level."""
        config = {
            "layout": {
                "label_w": 70,
                "label_h": 37,
            },
            "bw": True,
        }
        path = tmp_path / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        result = load_config(path)
        assert result["label_w"] == 70
        assert result["label_h"] == 37
        assert result["bw"] is True

    def test_top_level_overrides_layout_section(self, tmp_path):
        config = {
            "layout": {"label_w": 70},
            "label_w": 99,
        }
        path = tmp_path / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        result = load_config(path)
        assert result["label_w"] == 99  # top-level wins

    def test_legacy_key_mapping(self, tmp_path):
        """Legacy YAML keys should be mapped to canonical names."""
        config = {
            "margin_top": 13.5,
            "margin_left": 2.0,
            "preset": "50x30",
        }
        path = tmp_path / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        result = load_config(path)
        assert result["margin_y"] == 13.5
        assert result["margin_x"] == 2.0
        assert result["label_size"] == "50x30"
        # Original keys should be removed
        assert "margin_top" not in result
        assert "margin_left" not in result
        assert "preset" not in result
