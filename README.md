# ar-book-labels

English | **[简体中文](README.zh.md)**

Generate printable [Accelerated Reader](https://www.renaissance.com/accelerated-reader/) book labels from an Excel spreadsheet. Labels include book title, author, AR level (with standard color coding), points, and quiz number — formatted for sticker-style printing and sticking on books.

## Features

- **Standard AR color coding**: 12 color ranges from yellow (0.1–1.5) to brown (6.6+)
- **Print-ready HTML output**: 4 columns x 11 rows = 44 labels per page, `@page` CSS for direct printing
- **Smart text truncation**: Titles wrap to 2 lines with ellipsis; authors on 1 line
- **Author-first layout**: Author name appears above title for easy shelf sorting
- **Screen preview**: SVG viewBox scaling for crisp browser preview
- **Template included**: Reference Excel template with sample data and column documentation

## Installation

```bash
pip install ar-book-labels
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

## CLI Usage

```
ar-book-labels <excel> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `excel` | Path to the Excel file (.xlsx) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output` | `AR_Book_Labels.html` | Output HTML file path |
| `-s, --sheet` | `Merged` | Sheet name to read |
| `--col-title` | `AR Title` | Excel column name for book title |
| `--col-author` | `AR Author` | Excel column name for author |
| `--col-level` | `Book Level` | Excel column name for book level |
| `--col-points` | `AR Points` | Excel column name for AR points |
| `--col-quiz` | `Quiz Number` | Excel column name for quiz number |
| `--start-row` | `2` | 1-indexed row where data begins (1 = header row) |
| `--scale` | `3` | Display scale factor for screen preview |
| `--template` | — | Copy the reference Excel template to cwd and exit |
| `-V, --version` | — | Show version and exit |

### Examples

```bash
# Basic usage
ar-book-labels my_books.xlsx

# Custom output path and sheet name
ar-book-labels my_books.xlsx -o output/labels.html -s "Book Data"

# Custom column names (if your Excel uses different headers)
ar-book-labels my_books.xlsx --col-title "Title" --col-author "Author Name" --col-level "Level"

# Custom start row (e.g. data starts on row 3)
ar-book-labels my_books.xlsx --start-row 3

# Copy the template for reference
ar-book-labels --template
```

## Excel Format

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

## Development

### Setup

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Project Structure

```
ar-book-labels/
  ar_book_labels/
    __init__.py        # Package metadata and public API
    generator.py       # Core label generation logic
    cli.py             # CLI entry point (argparse)
    __main__.py        # python -m ar_book_labels support
    templates/
      ar_template.xlsx # Reference Excel template
  tests/
    test_generator.py  # Unit tests
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
- No external dependencies beyond `openpyxl`
- Keep the generator logic self-contained and testable

## License

MIT — see [LICENSE](LICENSE) for details.
