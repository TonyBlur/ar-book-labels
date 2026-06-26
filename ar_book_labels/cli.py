"""CLI entry point for ar-book-labels."""

import argparse
import json
import sys
from pathlib import Path

from ar_book_labels import __version__
from ar_book_labels.config import load_config, merge_configs, parse_label_size, parse_colors
from ar_book_labels.generator import generate, DEFAULT_COLUMNS
from ar_book_labels.layout import Layout


# =========================================================================
# Example configuration content (YAML) used by --generate-config
# =========================================================================

EXAMPLE_CONFIG_YAML = """\
# ar-book-labels Configuration File
# All values shown are defaults. CLI arguments override these values.

# Label size: preset name or custom "WxH" in mm
# Available presets: 50x30, 70x37, 63x38, 99x38
label_size: "50x30"

# Label dimensions (mm) - overridden by label_size preset
# label_w: 50
# label_h: 30
label_rx: 4            # Border radius (alias: radius)

# Page size: preset name or custom "WxH" in mm
# Available presets: A4, A5, A3, Letter, Legal, B5, B4
page_size: "A4"

# Manual grid override (optional)
# Format: "COLSxROWS" (e.g. "4x9", "3x7")
# Errors if grid doesn't fit on page.
# grid: "4x9"

# Page dimensions (mm) - overridden by page_size preset
page_w: 210            # A4 width
page_h: 297            # A4 height

# Spacing (mm)
col_gap: 2             # Gap between columns
row_gap: 0             # Gap between rows

# Margins (mm)
# Use 'margin' for uniform margin on all four sides,
# or 'margin_x' / 'margin_y' for per-axis control.
margin_x: 2            # Left/right margin
margin_y: 13.5         # Top/bottom margin
# margin: 13.5         # Uniform margin (overrides margin_x and margin_y)

# Typography
font: "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"

# Color scheme (replaces default AR colors)
# Format: "min-max:#HEX,min-max:#HEX,..."
# Uncomment and customise to override the default 12-level AR colour scheme:
# colors: "0.1-1.5:#FFD700,1.6-2.0:#2E8B57,2.1-2.5:#00008B,2.6-3.0:#DC143C,3.1-3.5:#FF69B4,3.6-4.0:#800080,4.1-4.5:#FF8C00,4.6-5.0:#00BFFF,5.1-5.5:#FF6600,5.6-6.0:#39FF14,6.1-6.5:#1C1C1C,6.6-99.0:#8B4513"

# Output options
bw: false              # Black-and-white mode
with_border: false     # Add printable cutting-guide border
"""

EXAMPLE_CONFIG_JSON = {
    "_comment": "ar-book-labels Configuration File. All values shown are defaults.",
    "label_size": "50x30",
    "label_rx": 4,
    "page_size": "A4",
    "page_w": 210,
    "page_h": 297,
    "col_gap": 2,
    "row_gap": 0,
    "margin_x": 2,
    "margin_y": 13.5,
    "font": "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif",
    "bw": False,
    "with_border": False,
}


def main():
    parser = argparse.ArgumentParser(
        prog="ar-book-labels",
        description="Generate printable Accelerated Reader book labels from an Excel or CSV file.",
    )
    parser.add_argument("input_file", nargs="?", help="Path to the Excel (.xlsx) or CSV (.csv) file")
    parser.add_argument(
        "-o", "--output", default="AR_Book_Labels.html",
        help="Output HTML file path (default: AR_Book_Labels.html)",
    )
    parser.add_argument(
        "-s", "--sheet", default=None,
        help="Sheet name to read (default: first sheet in the workbook)",
    )
    parser.add_argument(
        "--col-title", default=DEFAULT_COLUMNS["title"],
        help=f"Excel column name for book title (default: {DEFAULT_COLUMNS['title']})",
    )
    parser.add_argument(
        "--col-author", default=DEFAULT_COLUMNS["author"],
        help=f"Excel column name for author (default: {DEFAULT_COLUMNS['author']})",
    )
    parser.add_argument(
        "--col-level", default=DEFAULT_COLUMNS["level"],
        help=f"Excel column name for book level (default: {DEFAULT_COLUMNS['level']})",
    )
    parser.add_argument(
        "--col-points", default=DEFAULT_COLUMNS["points"],
        help=f"Excel column name for AR points (default: {DEFAULT_COLUMNS['points']})",
    )
    parser.add_argument(
        "--col-quiz", default=DEFAULT_COLUMNS["quiz"],
        help=f"Excel column name for quiz number (default: {DEFAULT_COLUMNS['quiz']})",
    )
    parser.add_argument(
        "--start-row", type=int, default=2,
        help="1-indexed row number where data begins (default: 2, i.e. row 1 is header)",
    )
    parser.add_argument(
        "--scale", type=int, default=1,
        help="Display scale factor for screen preview (default: 1)",
    )
    parser.add_argument(
        "--bw", action="store_true",
        help="Black-and-white mode: white circle with thin black outline, black level number",
    )
    parser.add_argument(
        "--with-border", action="store_true",
        help="Add a thin printable border around each label for manual cutting",
    )
    parser.add_argument(
        "--template", action="store_true",
        help="Copy the reference Excel template to the current directory and exit",
    )
    parser.add_argument(
        "--generate-config", nargs="?", const="STDOUT", default=None,
        metavar="OUTPUT_PATH",
        help=(
            "Generate an example configuration file and exit. "
            "If a path is given (e.g. my_config.yaml), writes to that file "
            "(format detected from extension: .yaml/.yml → YAML, .json → JSON). "
            "If no path is given, prints YAML to stdout."
        ),
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}",
    )

    # --- New layout arguments ------------------------------------------------
    parser.add_argument(
        "--label-size", default=None,
        help="Label size: preset name (50x30, 70x37, 63x38, 99x38) or WxH in mm (default: 50x30)",
    )
    parser.add_argument(
        "--page-size", default=None,
        help="Page size: preset name (A4, A5, A3, Letter, Legal, B5, B4) or WxH in mm (default: A4)",
    )
    parser.add_argument(
        "--col-gap", type=float, default=None,
        help="Column gap in mm (default: 2 for 50x30 preset)",
    )
    parser.add_argument(
        "--row-gap", type=float, default=None,
        help="Row gap in mm (default: 0)",
    )
    parser.add_argument(
        "--margin", type=float, default=None,
        help="Uniform page margin in mm for all four sides",
    )
    parser.add_argument(
        "--font", default=None,
        help="Font family for label text",
    )
    parser.add_argument(
        "--radius", type=float, default=None,
        help="Label border radius in mm (default: 4)",
    )
    parser.add_argument(
        "--colors", default=None,
        help='Colour scheme: "min-max:#HEX,min-max:#HEX,..." (replaces default AR colours)',
    )
    parser.add_argument(
        "--grid", default=None,
        help="Manual grid layout: COLSxROWS (e.g. 4x9, 3x7). Errors if grid doesn't fit on page.",
    )
    parser.add_argument(
        "--config", default=None,
        help="Path to a YAML or JSON configuration file",
    )

    args = parser.parse_args()

    # --- Handle --template and --generate-config (mutually exclusive intent) --
    if args.template:
        _copy_template()
        return

    if args.generate_config is not None:
        _generate_config(args.generate_config)
        return

    if not args.input_file:
        parser.error("the following arguments are required: input_file")

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)

    # T01: Auto-create parent directories for the output path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build column mapping from CLI args
    column_mapping = {
        "title": args.col_title,
        "author": args.col_author,
        "level": args.col_level,
        "points": args.col_points,
        "quiz": args.col_quiz,
    }

    # --- Build layout from CLI args + config file ---------------------------
    layout = _build_layout(args)

    try:
        n_books, n_pages, warnings = generate(
            file_path=str(input_path),
            output_path=str(output_path),
            sheet_name=args.sheet,
            column_mapping=column_mapping,
            start_row=args.start_row,
            display_scale=args.scale,
            bw=args.bw,
            with_border=args.with_border,
            layout=layout,
        )
    except KeyError as e:
        print(f"Error: sheet not found: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Print warnings to stderr
    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    if n_books == 0:
        print("Warning: no books found in the spreadsheet.", file=sys.stderr)
        sys.exit(0)

    print(f"Generated {n_books} labels ({n_pages} pages) -> {output_path}")


def _build_layout(args: argparse.Namespace) -> Layout:
    """Construct a Layout from CLI arguments and an optional config file.

    Priority: CLI args > config file > Layout defaults.
    """
    # 1. Collect explicitly-set CLI args into a dict
    cli_args: dict = {}
    if args.label_size is not None:
        cli_args["label_size"] = args.label_size
    if args.page_size is not None:
        cli_args["page_size"] = args.page_size
    if args.col_gap is not None:
        cli_args["col_gap"] = args.col_gap
    if args.row_gap is not None:
        cli_args["row_gap"] = args.row_gap
    if args.margin is not None:
        cli_args["margin"] = args.margin
    if args.font is not None:
        cli_args["font"] = args.font
    if args.radius is not None:
        cli_args["radius"] = args.radius
    if args.colors is not None:
        cli_args["colors"] = args.colors
    if args.grid is not None:
        cli_args["grid"] = args.grid

    # 2. Load config file (if specified)
    file_config: dict = {}
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        try:
            file_config = load_config(config_path)
        except (ImportError, ValueError) as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Merge: defaults (empty — Layout has its own) + file + CLI
    merged = merge_configs(cli_args, file_config, {})

    # 4. Parse colours string into level_colors list (if present)
    colors_str = merged.get("colors")
    if colors_str and isinstance(colors_str, str):
        try:
            merged["level_colors"] = parse_colors(colors_str)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # 5. Create Layout
    try:
        layout = Layout.from_config(merged)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    return layout


def _copy_template():
    """Copy the Excel template to the current working directory."""
    import shutil
    src = Path(__file__).parent / "templates" / "ar_template.xlsx"
    dst = Path.cwd() / "ar_template.xlsx"
    shutil.copy2(src, dst)
    print(f"Template copied to: {dst}")


def _generate_config(output_spec: str) -> None:
    """Generate an example configuration file.

    Parameters
    ----------
    output_spec:
        Either ``"STDOUT"`` (print YAML to stdout) or a file path.
        When a file path is given the format is auto-detected from the
        extension: ``.yaml``/``.yml`` → YAML, ``.json`` → JSON.
    """
    if output_spec == "STDOUT":
        sys.stdout.write(EXAMPLE_CONFIG_YAML)
        return

    dest = Path(output_spec)
    suffix = dest.suffix.lower()

    # Ensure parent directories exist
    dest.parent.mkdir(parents=True, exist_ok=True)

    if suffix in (".yaml", ".yml"):
        dest.write_text(EXAMPLE_CONFIG_YAML, encoding="utf-8")
    elif suffix == ".json":
        dest.write_text(
            json.dumps(EXAMPLE_CONFIG_JSON, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        # Default to YAML for unknown extensions
        dest.write_text(EXAMPLE_CONFIG_YAML, encoding="utf-8")

    print(f"Example config written to: {dest}")


if __name__ == "__main__":
    main()
