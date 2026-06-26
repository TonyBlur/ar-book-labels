"""Configuration loading and merging for ar-book-labels.

Supports YAML (requires PyYAML) and JSON configuration files.  Configuration
values are merged with the following priority:

    CLI arguments  >  config file  >  defaults
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_config(path: str | Path) -> Dict[str, Any]:
    """Load a configuration file (YAML or JSON).

    Parameters
    ----------
    path:
        Path to a ``.yaml``, ``.yml``, or ``.json`` file.

    Returns
    -------
    dict
        Flat configuration dictionary.  Nested ``layout`` sections in YAML
        files are flattened to the top level.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ImportError
        If a YAML file is requested but PyYAML is not installed.
    ValueError
        If the file extension is not recognised.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "PyYAML is required to load YAML config files. "
                "Install it with: pip install ar-book-labels[yaml]"
            )
        with open(file_path, "r", encoding="utf-8") as fh:
            raw: Dict[str, Any] = yaml.safe_load(fh) or {}

    elif suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

    else:
        raise ValueError(
            f"Unsupported config format: '{suffix}'. Use .yaml, .yml, or .json."
        )

    return _flatten_config(raw)


def merge_configs(
    cli_args: Dict[str, Any],
    file_config: Dict[str, Any],
    defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge configuration sources with priority: CLI > file > defaults.

    Parameters
    ----------
    cli_args:
        Dictionary of CLI arguments (only keys the user explicitly set).
    file_config:
        Dictionary loaded from a config file.
    defaults:
        Optional dictionary of default values.

    Returns
    -------
    dict
        Merged configuration dictionary.
    """
    merged: Dict[str, Any] = dict(defaults) if defaults else {}

    # Overlay file config (non-None values only)
    for key, value in file_config.items():
        if value is not None:
            merged[key] = value

    # Overlay CLI args (non-None values only)
    for key, value in cli_args.items():
        if value is not None:
            merged[key] = value

    # If the CLI set --margin, propagate to margin_x and margin_y so that
    # the uniform CLI override wins over any per-axis values from the file.
    if cli_args.get("margin") is not None:
        merged["margin_x"] = cli_args["margin"]
        merged["margin_y"] = cli_args["margin"]

    return merged


def parse_label_size(size_str: str) -> Dict[str, Any]:
    """Parse a label-size string into a dict of layout parameters.

    Parameters
    ----------
    size_str:
        Either a preset name (e.g. ``"50x30"``) or a custom ``"WxH"`` string
        (e.g. ``"80x40"``).

    Returns
    -------
    dict
        At minimum ``{"label_w": float, "label_h": float}``.  Presets include
        additional spacing parameters (``col_gap``, ``row_gap``, ``margin_x``,
        ``margin_y``, ``label_rx``).

    Raises
    ------
    ValueError
        If *size_str* is not a valid preset or ``WxH`` format.
    """
    from ar_book_labels.layout import PRESETS, _parse_label_size_value

    return _parse_label_size_value(size_str)


def parse_colors(colors_str: str) -> List[Tuple[float, float, str]]:
    """Parse a colour-scheme string into a list of (low, high, hex) tuples.

    Format: ``"min-max:#HEX,min-max:#HEX,…"``

    Parameters
    ----------
    colors_str:
        Comma-separated list of ``min-max:#HEX`` ranges.

    Returns
    -------
    list[tuple[float, float, str]]
        Each tuple is ``(low_level, high_level, hex_colour)``.

    Raises
    ------
    ValueError
        If any segment does not match the expected format.
    """
    result: List[Tuple[float, float, str]] = []
    for segment in colors_str.split(","):
        segment = segment.strip()
        if not segment:
            continue
        try:
            range_part, colour = segment.split(":")
            low_str, high_str = range_part.split("-")
            result.append((float(low_str), float(high_str), colour.strip()))
        except (ValueError, AttributeError):
            raise ValueError(
                f"Invalid colour spec: '{segment}'. Expected format: 'min-max:#HEX'"
            )
    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _flatten_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a config dict that may have a nested ``layout`` section.

    Keys inside ``layout`` are promoted to the top level.  Top-level keys
    take precedence over ``layout`` keys when both exist.
    """
    flat: Dict[str, Any] = {}

    # Copy layout section first (lower priority)
    layout_section = raw.get("layout")
    if isinstance(layout_section, dict):
        for key, value in layout_section.items():
            flat[key] = value

    # Copy top-level keys (higher priority), skipping the 'layout' key itself
    for key, value in raw.items():
        if key != "layout":
            flat[key] = value

    # Map legacy YAML key names to canonical names
    _KEY_ALIASES = {
        "margin_top": "margin_y",
        "margin_bottom": "margin_y",
        "margin_left": "margin_x",
        "margin_right": "margin_x",
        "preset": "label_size",
        "paper_size": "page_size",
        "paper": "page_size",
    }
    for old_key, new_key in _KEY_ALIASES.items():
        if old_key in flat and new_key not in flat:
            flat[new_key] = flat.pop(old_key)

    return flat
