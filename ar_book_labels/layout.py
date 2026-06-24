"""Layout configuration and grid computation for AR book labels.

Provides the ``Layout`` dataclass that encapsulates all physical and typographic
parameters needed to position labels on an A4 page.  Grid positions and internal
label coordinates are computed automatically from the high-level parameters.
"""

import dataclasses
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Baseline dimensions (50×30 mm label) used for proportional scaling.
# All internal coordinate constants below correspond to the values that were
# hand-tuned for the original 50×30 layout.
# ---------------------------------------------------------------------------
_BASELINE_W: float = 50.0
_BASELINE_H: float = 30.0

_BASE_CX: float = 11.0       # Badge circle center x
_BASE_CY: float = 18.0       # Badge circle center y
_BASE_CR: float = 6.5        # Badge circle radius
_BASE_RX: float = 21.0       # Right-side text area x start
_BASE_VX: float = 34.0       # Points/Quiz value x (center anchor)
_BASE_TOP_Y: float = 4.0     # Top text baseline y
_BASE_AUTHOR_LH: float = 3.2 # Author line height
_BASE_TITLE_LH: float = 3.6  # Title line height
_BASE_POINTS_Y: float = 17.2 # Points row y
_BASE_QUIZ_Y: float = 21.7   # Quiz row y


# ---------------------------------------------------------------------------
# Preset configurations.
#
# Each preset provides the complete set of spacing parameters that yield the
# documented grid (cols × rows).  The ``margin_x`` value is chosen so that
# the resulting columns fit exactly on a 210 mm-wide A4 page.
# ---------------------------------------------------------------------------
PRESETS: Dict[str, Dict[str, Any]] = {
    "50x30": {
        "label_w": 50.0, "label_h": 30.0, "label_rx": 4.0,
        "col_gap": 2.0, "row_gap": 0.0,
        "margin_x": 2.0, "margin_y": 13.5,
    },
    "70x37": {
        "label_w": 70.0, "label_h": 37.0, "label_rx": 4.0,
        "col_gap": 0.0, "row_gap": 0.0,
        "margin_x": 0.0, "margin_y": 13.5,
    },
    "63x38": {
        "label_w": 63.0, "label_h": 38.1, "label_rx": 4.0,
        "col_gap": 0.0, "row_gap": 0.0,
        "margin_x": 0.0, "margin_y": 13.5,
    },
    "99x38": {
        "label_w": 99.0, "label_h": 38.0, "label_rx": 4.0,
        "col_gap": 0.0, "row_gap": 0.0,
        "margin_x": 0.0, "margin_y": 13.5,
    },
}


@dataclass
class Layout:
    """Complete layout specification for AR book labels.

    All spatial values are in **millimetres**.  Internal label coordinates
    (badge circle position, text baselines, etc.) are derived automatically
    from ``label_w`` and ``label_h`` via :meth:`compute_internal`, using the
    original 50×30 mm layout as the proportional baseline.

    Grid positions (``cols_x``, ``rows_y``) are computed by
    :meth:`compute_grid` so that labels are centred horizontally on the page.
    """

    # -- Page dimensions (mm) ------------------------------------------------
    page_w: float = 210.0
    page_h: float = 297.0

    # -- Label dimensions (mm) -----------------------------------------------
    label_w: float = 50.0
    label_h: float = 30.0
    label_rx: float = 4.0   # Border radius

    # -- Spacing (mm) --------------------------------------------------------
    col_gap: float = 2.0    # Gap between columns
    row_gap: float = 0.0    # Gap between rows
    margin_x: float = 2.0   # Left/right page margin
    margin_y: float = 13.5  # Top/bottom page margin

    # -- Typography ----------------------------------------------------------
    font_family: str = (
        "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
    )

    # -- Colors --------------------------------------------------------------
    # ``None`` means use the module-level ``LEVEL_COLORS`` default.
    level_colors: Optional[List[Tuple[float, float, str]]] = None

    # -- Internal label coordinates (computed by compute_internal) ------------
    cx: float = _BASE_CX
    cy: float = _BASE_CY
    cr: float = _BASE_CR
    rx: float = _BASE_RX
    vx: float = _BASE_VX
    top_y: float = _BASE_TOP_Y
    author_lh: float = _BASE_AUTHOR_LH
    title_lh: float = _BASE_TITLE_LH
    points_y: float = _BASE_POINTS_Y
    quiz_y: float = _BASE_QUIZ_Y

    # -- Computed grid (set by compute_grid) ---------------------------------
    cols_x: List[float] = field(default_factory=list)
    rows_y: List[float] = field(default_factory=list)
    cols: int = 0
    rows: int = 0
    labels_per_page: int = 0

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------
    def __post_init__(self) -> None:
        """Compute derived values after initialisation."""
        self.compute_internal()
        self.compute_grid()

    # -----------------------------------------------------------------------
    # Computation helpers
    # -----------------------------------------------------------------------
    def compute_internal(self) -> None:
        """Scale internal label coordinates proportionally from 50×30 baseline.

        The baseline constants (``_BASE_CX``, ``_BASE_CY``, …) were tuned for a
        50 mm × 30 mm label.  For other sizes we scale linearly so that the
        visual proportions are preserved.
        """
        scale_x: float = self.label_w / _BASELINE_W
        scale_y: float = self.label_h / _BASELINE_H

        self.cx = _BASE_CX * scale_x
        self.cy = _BASE_CY * scale_y
        self.cr = _BASE_CR * ((scale_x + scale_y) / 2.0)
        self.rx = _BASE_RX * scale_x
        self.vx = _BASE_VX * scale_x
        self.top_y = _BASE_TOP_Y * scale_y
        self.author_lh = _BASE_AUTHOR_LH * scale_y
        self.title_lh = _BASE_TITLE_LH * scale_y
        self.points_y = _BASE_POINTS_Y * scale_y
        self.quiz_y = _BASE_QUIZ_Y * scale_y

    def compute_grid(self) -> None:
        """Compute the grid of label origin positions on the page.

        After this call the following attributes are set:

        * ``cols`` / ``rows`` — number of columns / rows
        * ``cols_x`` / ``rows_y`` — x / y origin of each column / row
        * ``labels_per_page`` — ``cols * rows``

        Labels are centred horizontally on the page when the available width
        is not an exact multiple of ``(label_w + col_gap)``.
        """
        available_w: float = self.page_w - 2.0 * self.margin_x
        available_h: float = self.page_h - 2.0 * self.margin_y

        self.cols = max(1, int(math.floor(
            (available_w + self.col_gap) / (self.label_w + self.col_gap)
        )))
        self.rows = max(1, int(math.floor(
            (available_h + self.row_gap) / (self.label_h + self.row_gap)
        )))

        # Horizontal centre offset so that the block of labels is centred.
        center_offset_x: float = (
            available_w - self.cols * (self.label_w + self.col_gap) + self.col_gap
        ) / 2.0

        self.cols_x = [
            self.margin_x + center_offset_x + i * (self.label_w + self.col_gap)
            for i in range(self.cols)
        ]
        self.rows_y = [
            self.margin_y + j * (self.label_h + self.row_gap)
            for j in range(self.rows)
        ]

        self.labels_per_page = self.cols * self.rows

    # -----------------------------------------------------------------------
    # Factory
    # -----------------------------------------------------------------------
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Layout":
        """Create a :class:`Layout` from a flat configuration dictionary.

        The dictionary may contain any combination of the following keys:

        * ``label_size`` — preset name (e.g. ``"50x30"``) or ``"WxH"`` string
        * ``label_w``, ``label_h``, ``label_rx`` — label dimensions
        * ``col_gap``, ``row_gap`` — inter-label spacing
        * ``margin`` — uniform margin (sets both ``margin_x`` and ``margin_y``)
        * ``margin_x``, ``margin_y`` — per-axis margins (override ``margin``)
        * ``radius`` — alias for ``label_rx``
        * ``font``, ``font_family`` — font family string
        * ``page_w``, ``page_h`` — page dimensions
        * ``level_colors`` — list of ``(low, high, hex)`` tuples
        * ``cx``, ``cy``, ``cr``, ``rx``, ``vx``, ``top_y``, ``author_lh``,
          ``title_lh``, ``points_y``, ``quiz_y`` — explicit internal coords
          that override proportional scaling

        Parameters
        ----------
        config:
            Flat dictionary of configuration values.  ``None`` values are
            ignored.

        Returns
        -------
        Layout
            A fully-initialised layout with computed grid and internal coords.
        """
        layout_kwargs: Dict[str, Any] = {}

        # --- 1. Load preset if label_size is specified -----------------------
        label_size = config.get("label_size")
        if label_size is not None:
            preset = _parse_label_size_value(str(label_size))
            layout_kwargs.update(preset)

        # --- 2. Apply explicit scalar overrides ------------------------------
        _SCALAR_KEYS = (
            "page_w", "page_h", "label_w", "label_h", "label_rx",
            "col_gap", "row_gap", "margin_x", "margin_y",
        )
        for key in _SCALAR_KEYS:
            if key in config and config[key] is not None:
                layout_kwargs[key] = float(config[key])

        # Aliases
        if config.get("radius") is not None:
            layout_kwargs["label_rx"] = float(config["radius"])

        # Font (string, not float)
        if config.get("font_family") is not None:
            layout_kwargs["font_family"] = str(config["font_family"])
        if config.get("font") is not None:
            layout_kwargs["font_family"] = str(config["font"])

        # --- 3. Uniform margin (applied AFTER individual margins) ------------
        if config.get("margin") is not None:
            m = float(config["margin"])
            layout_kwargs["margin_x"] = m
            layout_kwargs["margin_y"] = m

        # --- 4. Colors -------------------------------------------------------
        if config.get("level_colors") is not None:
            layout_kwargs["level_colors"] = config["level_colors"]

        # --- 5. Filter to valid dataclass fields and create instance ---------
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: v for k, v in layout_kwargs.items() if k in valid_fields}
        layout = cls(**filtered)

        # --- 6. Override internal coords if explicitly provided ---------------
        _INTERNAL_KEYS = (
            "cx", "cy", "cr", "rx", "vx", "top_y",
            "author_lh", "title_lh", "points_y", "quiz_y",
        )
        for key in _INTERNAL_KEYS:
            if key in config and config[key] is not None:
                setattr(layout, key, float(config[key]))

        return layout


# ---------------------------------------------------------------------------
# Helpers (module-private)
# ---------------------------------------------------------------------------

def _parse_label_size_value(size_str: str) -> Dict[str, Any]:
    """Resolve a label-size string to a dict of layout parameters.

    Parameters
    ----------
    size_str:
        Either a preset name (e.g. ``"50x30"``) or a custom ``"WxH"`` string.

    Returns
    -------
    dict
        At minimum ``{"label_w": …, "label_h": …}``.  Presets include
        additional spacing parameters.

    Raises
    ------
    ValueError
        If *size_str* is neither a known preset nor a valid ``WxH`` string.
    """
    if size_str in PRESETS:
        return dict(PRESETS[size_str])

    try:
        parts = size_str.lower().split("x")
        if len(parts) != 2:
            raise ValueError
        w, h = float(parts[0]), float(parts[1])
        if w <= 0 or h <= 0:
            raise ValueError
        return {"label_w": w, "label_h": h}
    except (ValueError, AttributeError):
        raise ValueError(
            f"Invalid label size: '{size_str}'. "
            f"Use a preset ({', '.join(sorted(PRESETS.keys()))}) "
            f"or format WxH (e.g. '70x37')."
        )
