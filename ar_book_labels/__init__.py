"""ar-book-labels: Generate printable Accelerated Reader book labels from Excel."""

__version__ = "0.3.0"

from ar_book_labels.generator import generate, read_books, build_html
from ar_book_labels.layout import Layout
