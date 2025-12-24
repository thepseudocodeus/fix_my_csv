#!/usr/bin/env python3
"""
profiler.py creates a profile report for a directory of CSVs.
"""

import csv
import hashlib
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from webbrowser import get

import chardet
import pandas as pd
import polars as pl

# TODOs
# - [ ] TODO: create a file data structure
# - [ ] TODO: add dash to parsers
# - [ ] TODO: add spark to parsers


# --- Config ---
# Data structures
DATA_DIR = None
REPORT_FILE = None
DEFAULT_DATA_DIR = Path("test_csvs")
DEFAULT_REPORT_FILE = Path("csv_profile_report.parquet")
# Sample for determining encoding
SAMPLE_SIZE = None
CSVKIT_ENABLED = None
DEFAULT_SAMPLE_SIZE = 32 * 1024
DEFAULT_CSVKIT_ENABLED = True

CONVERSION_OPTIONS = {"pandas": 1, "polars": 2}

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def get_user_input(message: str) -> str:
    """Get user input from command line."""
    return input(message)


def compute_hash(file_path):
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def detect_encoding(file_path):
    """User chardet to determine encoding."""
    with open(file_path, "rb") as f:
        raw = f.read(SAMPLE_SIZE)
    result = chardet.detect(raw)
    return result.get("encoding", "unknown"), result.get("confidence", 0)


def try_pandas(file_path, encoding):
    """Attempt to use pandas to reach file"""
    try:
        df = pd.read_csv(file_path, encoding=encoding, on_bad_lines="skip")
        return True, len(df), len(df.columns), df.columns.tolist(), None
    except Exception as e:
        return False, None, None, None, str(e)


def try_polars(file_path, encoding):
    """Attempt to use polars to access file"""
    try:
        df = pl.read_csv(file_path, encoding=encoding, ignore_errors=True)
        return True, df.height, df.width, df.columns, None
    except Exception as e:
        return False, None, None, None, str(e)


def try_python_csv(file_path, encoding):
    """Attempt to use Python’s csv module to access file"""
    try:
        with open(file_path, encoding=encoding, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            row_count = sum(1 for _ in reader)
        return True, row_count, len(headers), headers, None
    except Exception as e:
        return False, None, None, None, str(e)


def try_csvkit(file_path):
    """Use csvkit csvstat to understand file."""
    try:
        result = subprocess.run(
            ["csvstat", str(file_path), "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            stats = json.loads(result.stdout)
            num_cols = len(stats)
            num_rows = stats[0]["row_count"] if stats else None
            return True, num_rows, num_cols, None
        else:
            return False, None, None, result.stderr
    except Exception as e:
        return False, None, None, str(e)


def profile_file(file_path):
    """Profile a single CSV file."""
    logging.info(f"Profiling {file_path.name} ...")

    file_info = {
        "file_path": str(file_path),
        "file_size_bytes": file_path.stat().st_size,
        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime),
        "sha256": compute_hash(file_path),
    }

    # Determine encoding
    enc, conf = detect_encoding(file_path)
    file_info.update({"encoding": enc, "encoding_confidence": conf})

    # Read file with different tools
    for name, func in {
        "pandas": try_pandas,
        "polars": try_polars,
        "python_csv": try_python_csv,
    }.items():
        success, rows, cols, headers, err = func(file_path, enc)
        file_info.update(
            {
                f"{name}_success": success,
                f"{name}_rows": rows,
                f"{name}_cols": cols,
                f"{name}_headers": headers,
                f"{name}_error": err,
            }
        )

    # Try csvkit
    if CSVKIT_ENABLED:
        success, rows, cols, err = try_csvkit(file_path)
        file_info.update(
            {
                "csvkit_success": success,
                "csvkit_rows": rows,
                "csvkit_cols": cols,
                "csvkit_error": err,
            }
        )

    return file_info


def init():
    """Initialize global variables."""
    global DATA_DIR, REPORT_FILE, SAMPLE_SIZE, CSVKIT_ENABLED

    use_defaults = get_user_input("Use defaults (y/n): ")
    if use_defaults.lower() == "y":
        return

    csvkit_enabled = get_user_input("Use csvkit (y/n): ")
    if csvkit_enabled.lower() == "y":
        CSVKIT_ENABLED = True
    else:
        CSVKIT_ENABLED = DEFAULT_CSVKIT_ENABLED

    dir = get_user_input("Data directory: ")
    if dir is not None:
        DATA_DIR = Path(dir)
    else:
        DATA_DIR = DEFAULT_DATA_DIR

    report_file = get_user_input("Report file: ")
    if report_file is not None:
        REPORT_FILE = Path(report_file)
    else:
        REPORT_FILE = DEFAULT_REPORT_FILE

    sample_size = get_user_input("Sample size: ")
    if sample_size is not None:
        SAMPLE_SIZE = int(sample_size)
    else:
        SAMPLE_SIZE = DEFAULT_SAMPLE_SIZE


def convert_to_dataframe(records, option="polars"):
    """Create a dataframe from a list of records."""
    if option == "polars":
        return pl.DataFrame(records)
    if option == "pandas":
        return pd.DataFrame(records)
    return None


def main():
    """Entry point."""
    # Initialize the global variables
    init()
    all_records = []
    for csv_file in DATA_DIR.rglob("*.csv"):
        try:
            record = profile_file(csv_file)
            all_records.append(record)
        except Exception as e:
            logging.error(f"Failed profiling {csv_file}: {e}")

    df = convert_to_dataframe(all_records, "polars")
    if df is None:
        logger.info("Failed to write report.")
        return

    df.write_parquet(REPORT_FILE)
    logging.info(f"✅ Report written to {REPORT_FILE}")


if __name__ == "__main__":
    main()
