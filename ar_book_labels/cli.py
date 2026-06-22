"""CLI entry point for ar-book-labels."""

import argparse
import sys
from pathlib import Path

from ar_book_labels import __version__
from ar_book_labels.generator import generate


def main():
    parser = argparse.ArgumentParser(
        prog="ar-book-labels",
        description="Generate printable Accelerated Reader book labels from an Excel file.",
    )
    parser.add_argument("excel", nargs="?", help="Path to the Excel file (.xlsx)")
    parser.add_argument(
        "-o", "--output", default="AR_Book_Labels.html",
        help="Output HTML file path (default: AR_Book_Labels.html)",
    )
    parser.add_argument(
        "-s", "--sheet", default="Merged",
        help="Sheet name to read (default: Merged)",
    )
    parser.add_argument(
        "--no-filter", action="store_true",
        help="Include all rows, not just Match Status = Success",
    )
    parser.add_argument(
        "--scale", type=int, default=3,
        help="Display scale factor for screen preview (default: 3)",
    )
    parser.add_argument(
        "--template", action="store_true",
        help="Copy the reference Excel template to the current directory and exit",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    if args.template:
        _copy_template()
        return

    if not args.excel:
        parser.error("the following arguments are required: excel")

    excel_path = Path(args.excel)
    if not excel_path.exists():
        print(f"Error: file not found: {excel_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)

    try:
        n_books, n_pages = generate(
            excel_path=str(excel_path),
            output_path=str(output_path),
            sheet_name=args.sheet,
            filter_success=not args.no_filter,
            display_scale=args.scale,
        )
    except KeyError as e:
        print(f"Error: sheet not found: {e}", file=sys.stderr)
        sys.exit(1)

    if n_books == 0:
        print("Warning: no books found in the spreadsheet.", file=sys.stderr)
        sys.exit(0)

    print(f"Generated {n_books} labels ({n_pages} pages) -> {output_path}")


def _copy_template():
    import shutil
    src = Path(__file__).parent / "templates" / "ar_template.xlsx"
    dst = Path.cwd() / "ar_template.xlsx"
    shutil.copy2(src, dst)
    print(f"Template copied to: {dst}")


if __name__ == "__main__":
    main()
