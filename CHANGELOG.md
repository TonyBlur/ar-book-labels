# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-06-26

### Added
- CSV input support: `read_books()` and `generate()` now accept `.csv` files alongside `.xlsx`.
- `--generate-config` CLI command to generate example configuration files in YAML or JSON format.
- `BookDict` `TypedDict` for strong typing of book data in `generator.py`.
- Output directory auto-creation: `generate()` now calls `Path.parent.mkdir(parents=True, exist_ok=True)` before writing.
- CLI integration tests (`tests/test_cli.py`) covering `--template`, `--generate-config`, `--bw`, `--with-border`, `--grid`, `--scale`, `--config`, custom column mapping, and error paths.
- CSV input tests (`tests/test_generator.py::TestCSVInput`) covering basic read, numeric conversion, missing columns, empty file, incomplete rows, custom columns, UTF-8 BOM, and end-to-end generate.
- Comprehensive tests for `generate()` function and error paths.
- `CHANGELOG.md` to track version history.
- Layout parameterization: `Layout` dataclass in `ar_book_labels.layout` with configurable label size, page size, margins, gaps, typography, and colours.
- Label-size presets: `50x30`, `70x37`, `63x38`, `99x38`.
- Page-size presets: `A4`, `A5`, `A3`, `Letter`, `Legal`, `B5`, `B4`.
- Manual grid override via `--grid COLSxROWS`.
- Configuration file support (`--config`) with YAML and JSON formats.
- `Layout.from_config()` factory method for building layouts from flat dictionaries.
- Automatic grid centreing on the page.
- Proportional scaling of internal label coordinates for non-50x30 label sizes.
- CLI flags: `--label-size`, `--page-size`, `--col-gap`, `--row-gap`, `--margin`, `--font`, `--radius`, `--colors`, `--grid`, `--config`.
- Configuration loading (`config.py`) with `load_config()`, `merge_configs()`, `parse_label_size()`, `parse_colors()`.
- `--with-border` CLI flag for printable cutting-guide borders around each label.
- README overhaul with detailed usage, configuration reference, and Chinese translation.

### Removed
- PDF output support (use browser Print → Save as PDF instead).
- Legacy module-level layout constants (`PAGE_W`, `PAGE_H`, `COLS_X`, `ROWS_Y`, `LABEL_W`, `LABEL_H`, `LABEL_RX`, `LABELS_PER_PAGE`, `FONT`, `CX`, `CY`, `CR`, `RX`, `VX`, `TOP_Y`, `AUTHOR_LH`, `TITLE_LH`, `POINTS_Y`, `QUIZ_Y`). Use `ar_book_labels.layout.Layout` attributes instead.

### Changed
- Generator and label SVG rendering now accept a `Layout` parameter.
- Column mapping now falls back to `DEFAULT_COLUMNS` dict instead of hardcoded strings.

## [0.1.3] - 2026-06-24

### Added
- `--with-border` CLI flag for printable cutting-guide borders around each label.

## [0.1.2] - 2026-06-24

### Fixed
- Restored centred `ROWS_Y` layout to ensure labels align correctly on the page.

## [0.1.1] - 2026-06-24

### Fixed
- Moved label content up 4 mm to correct print offset on physical printers.

## [0.1.0] - 2026-06-24

### Added
- Initial release of `ar-book-labels`.
- Generate printable AR (Accelerated Reader) book labels from Excel `.xlsx` files.
- SVG-based label rendering with ATOS level colour-coded badges.
- Black-and-white mode (`--bw`) for monochrome printing.
- `--template` CLI command to copy the reference Excel template.
- Configurable column mapping (`--col-title`, `--col-author`, `--col-level`, `--col-points`, `--col-quiz`).
- `--sheet` flag to select a specific worksheet.
- `--start-row` flag to skip header rows.
- `--scale` flag for screen preview zoom.
- Multi-page HTML output with `@media print` CSS for exact physical dimensions.
- PyPI package with `pip install ar-book-labels`.
- GitHub Actions workflow for automated PyPI publishing.
