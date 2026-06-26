# ar-book-labels

English | **[简体中文](README.zh.md)**

Generate printable [Accelerated Reader](https://www.renaissance.com/accelerated-reader/) book labels from an Excel spreadsheet. Labels include book title, author, AR level (with standard color coding), points, and quiz number — formatted for sticker-style printing and sticking on books.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
  - [Options](#options)
  - [Examples](#examples)
- [Label Size Presets](#label-size-presets)
- [Page Size Presets](#page-size-presets)
- [Configuration File](#configuration-file)
- [Input Format (Excel & CSV)](#input-format-excel--csv)
- [AR Level Color Chart](#ar-level-color-chart)
- [Custom Color Scheme](#custom-color-scheme)
- [Development](#development)
- [License](#license)

## Features

- **Flexible label sizing**: 4 built-in presets (50x30, 70x37, 63x38, 99x38) or custom dimensions via `--label-size`
- **Multiple page sizes**: 7 presets (A4, A5, A3, Letter, Legal, B5, B4) or custom dimensions via `--page-size`
- **Auto grid layout**: Columns, rows, and centering are computed automatically from label size
- **Manual grid override**: Specify exact columns × rows with `--grid` (e.g. `4x9`)
- **Customizable spacing**: Column gap (`--col-gap`), row gap (`--row-gap`), and page margin (`--margin`)
- **CSV & Excel input**: Read book data from `.csv` or `.xlsx` files (auto-detected by extension)
- **Standard AR color coding**: 12 color ranges from yellow (0.1–1.5) to brown (6.6+)
- **Custom color scheme**: Override AR colors with `--colors`
- **Black-and-white mode**: `--bw` for ink-saving printing
- **Cutting-guide border**: `--with-border` adds a thin printable border for manual cutting
- **Typography control**: Custom font family (`--font`) and border radius (`--radius`)
- **YAML/JSON config**: Reusable configuration files via `--config`
- **Config generation**: `--generate-config` creates an example config file to get started quickly
- **Smart text truncation**: Titles wrap to 2 lines with ellipsis; authors on 1 line
- **Author-first layout**: Author name appears above title for easy shelf sorting
- **Print-ready HTML**: `@page` CSS for direct printing; screen preview via `--scale`
- **Template included**: Reference Excel template with sample data and column documentation

## Installation

```bash
pip install ar-book-labels
```

For YAML config file support:

```bash
pip install ar-book-labels[yaml]
```

Or install from source:

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
pip install -e .
```

## Quick Start

1. **Get the template** (optional — if you don't have an Excel file yet):

```bash
ar-book-labels --template
```

This copies `ar_template.xlsx` to your current directory. Fill it with your book data.

2. **Generate labels**:

```bash
ar-book-labels books.xlsx -o labels.html
```

3. **Open** `labels.html` in a browser to preview, then print (Ctrl/Cmd+P).

   > **Print tip**: In the browser print dialog, choose **"Actual size"** (or **"No margins"** / **"None"** for margins) to prevent the browser from auto-adding page margins that shift label positions. The HTML already declares `@page { margin: 0 }`; adding browser margins on top causes misalignment.

## CLI Usage

```
ar-book-labels <excel> [options]
```

### Options

#### Input & Output

| Option | Default | Description |
|--------|---------|-------------|
| `excel` | — | Path to the Excel (.xlsx) or CSV (.csv) file |
| `-o, --output` | `AR_Book_Labels.html` | Output HTML file path |
| `-s, --sheet` | first sheet | Sheet name to read (defaults to first sheet, Excel only) |
| `--start-row` | `2` | 1-indexed row where data begins (1 = header row) |
| `--generate-config` | — | Generate an example config file and exit (YAML or JSON based on extension) |
| `--template` | — | Copy the reference Excel template to cwd and exit |
| `-V, --version` | — | Show version and exit |

#### Column Mapping

| Option | Default | Description |
|--------|---------|-------------|
| `--col-title` | `AR Title` | Excel column name for book title |
| `--col-author` | `AR Author` | Excel column name for author |
| `--col-level` | `Book Level` | Excel column name for book level |
| `--col-points` | `AR Points` | Excel column name for AR points |
| `--col-quiz` | `Quiz Number` | Excel column name for quiz number |

#### Layout

| Option | Default | Description |
|--------|---------|-------------|
| `--label-size` | `50x30` | Label size: preset name (`50x30`, `70x37`, `63x38`, `99x38`) or `WxH` in mm |
| `--page-size` | `A4` | Page size: preset name (`A4`, `A5`, `A3`, `Letter`, `Legal`, `B5`, `B4`) or `WxH` in mm |
| `--grid` | auto | Manual grid layout: `COLSxROWS` (e.g. `4x9`, `3x7`). Errors if grid doesn't fit on page |
| `--col-gap` | `2` | Column gap in mm |
| `--row-gap` | `0` | Row gap in mm |
| `--margin` | `13.5` | Uniform page margin in mm for all four sides |
| `--radius` | `4` | Label border radius in mm |

#### Appearance

| Option | Default | Description |
|--------|---------|-------------|
| `--scale` | `1` | Display scale factor for screen preview |
| `--bw` | — | Black-and-white mode: white circle with thin black outline, black level number |
| `--with-border` | — | Add a thin printable border around each label for manual cutting |
| `--font` | Segoe UI, system-ui, ... | Font family for label text |
| `--colors` | AR standard 12 ranges | Custom color scheme (see [Custom Color Scheme](#custom-color-scheme)) |

#### Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--config` | — | Path to a YAML or JSON configuration file |

### Examples

```bash
# Basic usage (default 50x30mm labels)
ar-book-labels my_books.xlsx

# CSV input (auto-detected by extension)
ar-book-labels my_books.csv -o labels.html

# Generate an example config file
ar-book-labels --generate-config my_config.yaml
ar-book-labels --generate-config my_config.json

# Custom output path and sheet name
ar-book-labels my_books.xlsx -o output/labels.html -s "Book Data"

# Larger labels (70x37mm, 21 per page)
ar-book-labels my_books.xlsx --label-size 70x37

# Avery 5160 compatible labels
ar-book-labels my_books.xlsx --label-size 63x38

# Custom dimensions with wider gaps
ar-book-labels my_books.xlsx --label-size 60x40 --col-gap 3 --row-gap 2

# Letter paper (US)
ar-book-labels my_books.xlsx --page-size Letter

# A5 paper with manual 2×5 grid
ar-book-labels my_books.xlsx --page-size A5 --grid 2x5

# Manual grid layout (4 columns × 9 rows)
ar-book-labels my_books.xlsx --grid 4x9

# Custom page size (WxH in mm)
ar-book-labels my_books.xlsx --page-size 150x200

# Tighter margins (10mm)
ar-book-labels my_books.xlsx --margin 10

# Custom font (e.g. for Chinese titles)
ar-book-labels my_books.xlsx --font "Noto Sans SC, sans-serif"

# Square corners
ar-book-labels my_books.xlsx --radius 0

# Custom color scheme
ar-book-labels my_books.xlsx --colors "0.1-2.0:#FFD700,2.1-4.0:#2E8B57,4.1-6.0:#DC143C,6.1-99:#8B4513"

# Black-and-white mode with border
ar-book-labels my_books.xlsx --bw --with-border

# Use a config file
ar-book-labels my_books.xlsx --config ar-book-labels.yaml

# Copy the template for reference
ar-book-labels --template
```

## Label Size Presets

| Preset | Dimensions | Labels/Page | Grid | Notes |
|--------|-----------|-------------|------|-------|
| `50x30` | 50mm × 30mm | 36 | 4 × 9 | Default. Compact labels. |
| `70x37` | 70mm × 37mm | 21 | 3 × 7 | Medium labels, more space for long titles. |
| `63x38` | 63mm × 38.1mm | 21 | 3 × 7 | Avery 5160/8160 compatible. |
| `99x38` | 99mm × 38mm | 14 | 2 × 7 | Extra large labels. |

Custom sizes are also supported: `--label-size WxH` where W and H are in millimeters.

When using a custom or preset size, the grid (columns, rows) is calculated automatically and labels are centered horizontally on the page.

## Page Size Presets

| Preset | Dimensions (W × H) | Notes |
|--------|-------------------|-------|
| `A4` | 210mm × 297mm | Default. Standard international paper. |
| `A5` | 148mm × 210mm | Half of A4. Fewer labels per page. |
| `A3` | 297mm × 420mm | Double A4. More labels per page. |
| `Letter` | 215.9mm × 279.4mm | US standard. Slightly wider and shorter than A4. |
| `Legal` | 215.9mm × 355.6mm | US legal. Taller than Letter. |
| `B5` | 176mm × 250mm | Common in Japan and some European countries. |
| `B4` | 250mm × 353mm | Larger format. |

Custom page sizes are also supported: `--page-size WxH` where W and H are in millimeters.

When the label grid doesn't fit the chosen page size (e.g. too-wide labels on a small page), the tool reports a clear error with suggestions for fixing it.

## Configuration File

For reusable settings, create a YAML or JSON config file:

```yaml
# ar-book-labels.yaml
label_size: "50x30"
page_size: "A4"        # A4, A5, A3, Letter, Legal, B5, B4, or WxH
# grid: "4x9"          # Manual grid override (COLSxROWS)
col_gap: 2
row_gap: 0
margin: 13.5
font: "'Segoe UI', system-ui, sans-serif"
radius: 4
bw: false
with_border: false
# colors: "0.1-1.5:#FFD700,1.6-2.0:#2E8B57,..."
```

```bash
ar-book-labels my_books.xlsx --config ar-book-labels.yaml
```

**Priority**: CLI arguments > config file > defaults.

An example config file is available at [`ar_labels_config.example.yaml`](ar_labels_config.example.yaml).

YAML support requires the optional `pyyaml` dependency:

```bash
pip install ar-book-labels[yaml]
```

JSON config files work without any extra dependencies.

## Input Format (Excel & CSV)

The tool accepts both Excel (`.xlsx`) and CSV (`.csv`) files. The format is auto-detected from the file extension.

The spreadsheet must contain these columns (default names shown; use `--col-*` options to map custom names):

| Internal Key | Default Column | Type | Description |
|--------------|----------------|------|-------------|
| `title` | `AR Title` | text | Book title |
| `author` | `AR Author` | text | Author name |
| `level` | `Book Level` | number | AR ATOS level (e.g. 5.1) |
| `points` | `AR Points` | number | Points value |
| `quiz` | `Quiz Number` | number/text | Quiz ID |

Rows with missing required fields are skipped with a warning printed to stderr.

Use `ar-book-labels --template` to get a pre-formatted template with sample data.

## AR Level Color Chart

| Level Range | Color | Hex |
|-------------|-------|-----|
| 0.1 – 1.5 | Yellow | `#FFD700` |
| 1.6 – 2.0 | Green | `#2E8B57` |
| 2.1 – 2.5 | Dark Blue | `#00008B` |
| 2.6 – 3.0 | Red | `#DC143C` |
| 3.1 – 3.5 | Pink | `#FF69B4` |
| 3.6 – 4.0 | Purple | `#800080` |
| 4.1 – 4.5 | Orange | `#FF8C00` |
| 4.6 – 5.0 | Light Blue | `#00BFFF` |
| 5.1 – 5.5 | Neon Orange | `#FF6600` |
| 5.6 – 6.0 | Neon Green | `#39FF14` |
| 6.1 – 6.5 | Black | `#1C1C1C` |
| 6.6+ | Brown | `#8B4513` |

## Custom Color Scheme

Override the default AR color scheme with `--colors`:

```bash
ar-book-labels my_books.xlsx --colors "0.1-2.0:#FFD700,2.1-4.0:#2E8B57,4.1-6.0:#DC143C,6.1-99:#8B4513"
```

Format: `min-max:#HEX,min-max:#HEX,...`

- Each range is `min-max:#HEX` (level range → color)
- Ranges are separated by commas
- Ranges should cover the full level spectrum (0.1–99)
- In black-and-white mode (`--bw`), custom colors are ignored

## Development

### Setup

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[yaml,dev]"
```

### Project Structure

```
ar-book-labels/
  ar_book_labels/
    __init__.py        # Package metadata and public API
    layout.py          # Layout dataclass + grid computation
    config.py          # Config loading (YAML/JSON) + merging
    generator.py       # Core label generation logic
    cli.py             # CLI entry point (argparse)
    __main__.py        # python -m ar_book_labels support
    templates/
      ar_template.xlsx # Reference Excel template
  tests/
    test_layout.py     # Layout computation tests
    test_config.py     # Config loading tests
    test_generator.py  # Generator tests
  ar_labels_config.example.yaml  # Example config file
  pyproject.toml       # Build configuration (setuptools)
  LICENSE              # MIT License
  README.md            # This file (English)
  README.zh.md         # 中文文档
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Building & Publishing

```bash
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

### Automated Publishing (GitHub Actions)

This project uses a GitHub Actions workflow to automatically publish to PyPI when a new release is created:

1. Bump the version in `pyproject.toml`
2. Create a new release on GitHub (via the web UI or `gh release create`)
3. The `publish.yml` workflow will automatically build the package and publish it to PyPI using [trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC — no API token needed)

**Prerequisites**: Configure a [Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) on PyPI for the `ar-book-labels` project, linking it to the `TonyBlur/ar-book-labels` repository and the `pypi` environment.

### Code Style

- Python 3.8+
- Minimal external dependencies (`openpyxl` required, `pyyaml` optional)
- Keep the generator logic self-contained and testable

## License

MIT — see [LICENSE](LICENSE) for details.
