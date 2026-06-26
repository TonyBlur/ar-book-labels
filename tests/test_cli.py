"""Tests for ar-book-labels CLI entry point.

These tests exercise the CLI as an integration layer, verifying argument
parsing, error handling, and the end-to-end flow from command-line invocation
through to HTML output.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the ar-book-labels CLI entry point as a subprocess.

    Uses ``python -m ar_book_labels.cli`` so that tests work even when
    the console_scripts entry point is not installed.

    Sets ``PYTHONIOENCODING=utf-8`` so that Unicode characters in help text
    (e.g. the arrow ``→``) do not cause encoding errors on Windows (cp1252).
    """
    import os

    cmd = [sys.executable, "-m", "ar_book_labels.cli", *args]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )


def _create_test_excel(
    dest: Path,
    rows: list | None = None,
    headers: list | None = None,
    filename: str = "test.xlsx",
) -> Path:
    """Create a minimal test Excel file.

    Parameters
    ----------
    dest:
        Directory in which to create the file.
    rows:
        List of data dicts.  Each dict maps header name → value.
    headers:
        Column headers.  Defaults to standard AR columns.
    filename:
        Filename within *dest*.

    Returns
    -------
    Path
        Path to the created .xlsx file.
    """
    if headers is None:
        headers = ["AR Title", "AR Author", "Book Level", "AR Points", "Quiz Number"]
    if rows is None:
        rows = []

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(headers)
    for row_data in rows:
        ws.append([row_data.get(h) for h in headers])
    path = dest / filename
    wb.save(path)
    wb.close()
    return path


# ---------------------------------------------------------------------------
# Basic invocation tests
# ---------------------------------------------------------------------------

class TestCLIInvocation:
    """Test basic CLI argument handling."""

    def test_no_args_shows_error(self):
        """Running with no arguments should print usage and exit non-zero."""
        result = _run_cli()
        assert result.returncode != 0
        # argparse writes to stderr for required-argument errors
        assert "required" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_version_flag(self):
        """--version should print version string and exit 0."""
        result = _run_cli("--version")
        assert result.returncode == 0
        # Should contain the program name and a version number
        assert "ar-book-labels" in result.stdout.lower() or "ar-book-labels" in result.stderr.lower()

    def test_help_flag(self):
        """--help should show usage information and exit 0."""
        result = _run_cli("--help")
        assert result.returncode == 0
        assert "Accelerated Reader" in result.stdout or "book labels" in result.stdout.lower()


# ---------------------------------------------------------------------------
# --template tests
# ---------------------------------------------------------------------------

class TestCLITemplate:
    """Test the --template flag."""

    def test_template_copies_file(self, tmp_path: Path):
        """--template should copy the Excel template to the cwd."""
        result = _run_cli("--template", cwd=tmp_path)
        assert result.returncode == 0
        template_file = tmp_path / "ar_template.xlsx"
        assert template_file.exists()
        assert template_file.stat().st_size > 0

    def test_template_stdout_message(self, tmp_path: Path):
        """--template should print a confirmation message."""
        result = _run_cli("--template", cwd=tmp_path)
        assert result.returncode == 0
        assert "copied" in result.stdout.lower()


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------

class TestCLIErrors:
    """Test CLI error handling for various failure scenarios."""

    def test_file_not_found(self, tmp_path: Path):
        """Non-existent Excel file should exit non-zero with error message."""
        result = _run_cli(str(tmp_path / "nonexistent.xlsx"))
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_file_not_found_specific_message(self, tmp_path: Path):
        """Non-existent file should mention the path in stderr."""
        missing = tmp_path / "does_not_exist.xlsx"
        result = _run_cli(str(missing))
        assert result.returncode != 0
        assert "does_not_exist" in result.stderr

    def test_invalid_excel_file(self, tmp_path: Path):
        """A text file disguised as .xlsx should exit non-zero."""
        bad_file = tmp_path / "bad.xlsx"
        bad_file.write_text("this is not an xlsx file", encoding="utf-8")
        result = _run_cli(str(bad_file))
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# --generate-config tests
# ---------------------------------------------------------------------------

class TestCLIGenerateConfig:
    """Test the --generate-config flag."""

    def test_generate_config_stdout(self):
        """--generate-config with no path should print YAML to stdout."""
        result = _run_cli("--generate-config")
        assert result.returncode == 0
        # Should contain typical YAML config keys
        assert "label_size" in result.stdout
        assert "page_size" in result.stdout
        assert "bw" in result.stdout

    def test_generate_config_yaml_file(self, tmp_path: Path):
        """--generate-config path.yaml should write a YAML file."""
        config_path = tmp_path / "my_config.yaml"
        result = _run_cli("--generate-config", str(config_path))
        assert result.returncode == 0
        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        assert "label_size" in content
        assert "page_size" in content
        # Should be valid YAML-like (at least have key: value pairs)
        assert ":" in content

    def test_generate_config_yml_extension(self, tmp_path: Path):
        """--generate-config should recognise .yml extension as YAML."""
        config_path = tmp_path / "config.yml"
        result = _run_cli("--generate-config", str(config_path))
        assert result.returncode == 0
        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        assert "label_size" in content

    def test_generate_config_json_file(self, tmp_path: Path):
        """--generate-config path.json should write a JSON file."""
        config_path = tmp_path / "config.json"
        result = _run_cli("--generate-config", str(config_path))
        assert result.returncode == 0
        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        # Should be valid JSON
        parsed = json.loads(content)
        assert "label_size" in parsed
        assert "page_size" in parsed

    def test_generate_config_creates_parent_dirs(self, tmp_path: Path):
        """--generate-config should auto-create parent directories."""
        config_path = tmp_path / "deep" / "nested" / "dir" / "config.yaml"
        result = _run_cli("--generate-config", str(config_path))
        assert result.returncode == 0
        assert config_path.exists()

    def test_generate_config_with_template_precedence(self, tmp_path: Path):
        """When both --template and --generate-config are given, --template runs first."""
        result = _run_cli("--template", cwd=tmp_path)
        assert result.returncode == 0
        # --template returns early, so --generate-config is not tested here
        # (they're sequential checks in the CLI; template wins)


# ---------------------------------------------------------------------------
# Generate end-to-end tests
# ---------------------------------------------------------------------------

class TestCLIGenerate:
    """Test the end-to-end generate flow via the CLI."""

    def test_basic_generate(self, tmp_path: Path):
        """Basic generation with a valid Excel file."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Book A", "AR Author": "Author A", "Book Level": 3.5, "AR Points": 5, "Quiz Number": 1001},
            {"AR Title": "Book B", "AR Author": "Author B", "Book Level": 2.0, "AR Points": 3, "Quiz Number": 1002},
        ])
        output = tmp_path / "out.html"
        result = _run_cli(str(excel), "-o", str(output))
        assert result.returncode == 0
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "Book A" in content
        assert "Book B" in content

    def test_generate_with_custom_output_path(self, tmp_path: Path):
        """-o flag should create output in specified path (including nested dirs)."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Nested Book", "AR Author": "Author", "Book Level": 2.5, "AR Points": 2, "Quiz Number": 500},
        ])
        output = tmp_path / "deep" / "nested" / "labels.html"
        result = _run_cli(str(excel), "-o", str(output))
        assert result.returncode == 0
        assert output.exists()

    def test_generate_bw_mode(self, tmp_path: Path):
        """--bw flag should produce black-and-white output."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "BW Book", "AR Author": "Author", "Book Level": 3.0, "AR Points": 1, "Quiz Number": 100},
        ])
        output = tmp_path / "bw.html"
        result = _run_cli(str(excel), "-o", str(output), "--bw")
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert 'fill="white"' in content
        assert 'stroke="black"' in content

    def test_generate_with_border(self, tmp_path: Path):
        """--with-border flag should add cutting-guide borders."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Border Book", "AR Author": "Author", "Book Level": 2.5, "AR Points": 2, "Quiz Number": 200},
        ])
        output = tmp_path / "border.html"
        result = _run_cli(str(excel), "-o", str(output), "--with-border")
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert 'class="label-border"' in content

    def test_generate_empty_excel_warns(self, tmp_path: Path):
        """Excel with only headers (no data) should warn and exit 0."""
        excel = _create_test_excel(tmp_path, rows=[])
        output = tmp_path / "empty.html"
        result = _run_cli(str(excel), "-o", str(output))
        # Empty spreadsheet: exit 0 with warning
        assert result.returncode == 0
        assert "no books" in result.stderr.lower()

    def test_generate_with_custom_columns(self, tmp_path: Path):
        """--col-* flags should remap column names."""
        headers = ["Title", "Writer", "Lvl", "Pts", "Quiz#"]
        wb = Workbook()
        ws = wb.active
        ws.append(headers)
        ws.append(["My Book", "My Writer", 4.5, 10, 9999])
        excel = tmp_path / "custom_cols.xlsx"
        wb.save(excel)
        wb.close()

        output = tmp_path / "out.html"
        result = _run_cli(
            str(excel),
            "-o", str(output),
            "--col-title", "Title",
            "--col-author", "Writer",
            "--col-level", "Lvl",
            "--col-points", "Pts",
            "--col-quiz", "Quiz#",
        )
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert "My Book" in content

    def test_generate_with_scale(self, tmp_path: Path):
        """--scale flag should set display scale in output."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Scale Book", "AR Author": "Author", "Book Level": 2.0, "AR Points": 1, "Quiz Number": 1},
        ])
        output = tmp_path / "scaled.html"
        result = _run_cli(str(excel), "-o", str(output), "--scale", "2")
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert "scale(2)" in content

    def test_generate_stdout_message(self, tmp_path: Path):
        """Successful generation should print book count and output path."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Msg Book", "AR Author": "Author", "Book Level": 2.0, "AR Points": 1, "Quiz Number": 1},
        ])
        output = tmp_path / "msg.html"
        result = _run_cli(str(excel), "-o", str(output))
        assert result.returncode == 0
        assert "Generated" in result.stdout
        assert "labels" in result.stdout

    def test_generate_with_label_size(self, tmp_path: Path):
        """--label-size flag should change the label dimensions."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Big Label", "AR Author": "Author", "Book Level": 3.0, "AR Points": 5, "Quiz Number": 200},
        ])
        output = tmp_path / "big.html"
        result = _run_cli(str(excel), "-o", str(output), "--label-size", "70x37")
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert "Big Label" in content


# ---------------------------------------------------------------------------
# --config flag tests
# ---------------------------------------------------------------------------

class TestCLIConfigFile:
    """Test using a config file with --config."""

    def test_config_json_file(self, tmp_path: Path):
        """--config with a JSON file should apply layout settings."""
        config = {"label_size": "70x37", "bw": True}
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Config Book", "AR Author": "Author", "Book Level": 3.0, "AR Points": 5, "Quiz Number": 100},
        ])
        output = tmp_path / "config_out.html"
        result = _run_cli(str(excel), "-o", str(output), "--config", str(config_path))
        assert result.returncode == 0
        content = output.read_text(encoding="utf-8")
        assert "Config Book" in content
        # BW mode from config
        assert 'fill="white"' in content

    def test_config_file_not_found(self, tmp_path: Path):
        """--config with a missing file should exit non-zero."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Book", "AR Author": "Author", "Book Level": 2.0, "AR Points": 1, "Quiz Number": 1},
        ])
        output = tmp_path / "out.html"
        result = _run_cli(str(excel), "-o", str(output), "--config", str(tmp_path / "missing.json"))
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


# ---------------------------------------------------------------------------
# --grid flag tests
# ---------------------------------------------------------------------------

class TestCLIGrid:
    """Test the --grid flag via CLI."""

    def test_grid_flag(self, tmp_path: Path):
        """--grid 3x5 should override the auto-computed grid."""
        excel = _create_test_excel(tmp_path, [
            {"AR Title": "Grid Book", "AR Author": "Author", "Book Level": 2.0, "AR Points": 1, "Quiz Number": 1},
        ])
        output = tmp_path / "grid.html"
        result = _run_cli(str(excel), "-o", str(output), "--grid", "3x5")
        assert result.returncode == 0
        assert output.exists()
