"""CSV Profiler Module - Profile CSV files in a directory."""

import csv
import hashlib
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List
import sys

import chardet
import pandas as pd
import polars as pl
from InquirerPy import inquirer

sys.path.insert(0, str(Path(__file__).parent.parent))
from interface import MenuItem, MenuModule

logger = logging.getLogger("CSVProfiler")


class CSVProfilerService:
    """Service for profiling CSV files."""

    DEFAULT_DATA_DIR = Path("test_csvs")
    DEFAULT_REPORT_FILE = Path("csv_profile_report.parquet")
    DEFAULT_SAMPLE_SIZE = 32 * 1024

    def __init__(self):
        self.data_dir = self.DEFAULT_DATA_DIR
        self.report_file = self.DEFAULT_REPORT_FILE
        self.sample_size = self.DEFAULT_SAMPLE_SIZE
        self.csvkit_enabled = True

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def detect_encoding(self, file_path: Path) -> tuple:
        """Use chardet to determine encoding."""
        with open(file_path, "rb") as f:
            raw = f.read(self.sample_size)
        result = chardet.detect(raw)
        encoding = result.get("encoding") or "utf-8"
        confidence = result.get("confidence", 0)
        return encoding, confidence

    @staticmethod
    def try_pandas(file_path: Path, encoding: str) -> tuple:
        """Attempt to use pandas to read file."""
        try:
            df = pd.read_csv(file_path, encoding=encoding, on_bad_lines="skip")
            return True, len(df), len(df.columns), df.columns.tolist(), None
        except Exception as e:
            return False, None, None, None, str(e)

    @staticmethod
    def try_polars(file_path: Path, encoding: str) -> tuple:
        """Attempt to use polars to read file."""
        try:
            df = pl.read_csv(file_path, encoding=encoding, ignore_errors=True)
            return True, df.height, df.width, df.columns, None
        except Exception as e:
            return False, None, None, None, str(e)

    @staticmethod
    def try_python_csv(file_path: Path, encoding: str) -> tuple:
        """Attempt to use Python's csv module to read file."""
        try:
            with open(file_path, encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                row_count = sum(1 for _ in reader)
            return True, row_count, len(headers), headers, None
        except Exception as e:
            return False, None, None, None, str(e)

    @staticmethod
    def try_csvkit(file_path: Path) -> tuple:
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

    def profile_file(self, file_path: Path) -> dict:
        """Profile a single CSV file."""
        logger.info(f"Profiling {file_path.name}...")

        file_info = {
            "file_path": str(file_path),
            "file_size_bytes": file_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime),
            "sha256": self.compute_hash(file_path),
        }

        enc, conf = self.detect_encoding(file_path)
        file_info.update({"encoding": enc, "encoding_confidence": conf})

        for name, func in {
            "pandas": self.try_pandas,
            "polars": self.try_polars,
            "python_csv": self.try_python_csv,
        }.items():
            success, rows, cols, headers, err = func(file_path, enc)
            file_info.update({
                f"{name}_success": success,
                f"{name}_rows": rows,
                f"{name}_cols": cols,
                f"{name}_headers": headers,
                f"{name}_error": err,
            })

        if self.csvkit_enabled:
            success, rows, cols, err = self.try_csvkit(file_path)
            file_info.update({
                "csvkit_success": success,
                "csvkit_rows": rows,
                "csvkit_cols": cols,
                "csvkit_error": err,
            })

        return file_info

    def configure(self):
        """Interactive configuration."""
        print("\n=== CSV Profiler Configuration ===")

        use_defaults = inquirer.confirm(
            message="Use default settings?",
            default=True
        ).execute()

        if use_defaults:
            self.data_dir = self.DEFAULT_DATA_DIR
            self.report_file = self.DEFAULT_REPORT_FILE
            self.sample_size = self.DEFAULT_SAMPLE_SIZE
            self.csvkit_enabled = True
            logger.info("Using default configuration")
            return

        dir_input = inquirer.text(
            message="Data directory:",
            default=str(self.DEFAULT_DATA_DIR)
        ).execute()
        self.data_dir = Path(dir_input) if dir_input else self.DEFAULT_DATA_DIR

        report_input = inquirer.text(
            message="Report output file:",
            default=str(self.DEFAULT_REPORT_FILE)
        ).execute()
        self.report_file = Path(report_input) if report_input else self.DEFAULT_REPORT_FILE

        sample_input = inquirer.text(
            message="Sample size (bytes):",
            default=str(self.DEFAULT_SAMPLE_SIZE)
        ).execute()
        try:
            self.sample_size = int(sample_input) if sample_input else self.DEFAULT_SAMPLE_SIZE
        except ValueError:
            logger.warning("Invalid sample size, using default")
            self.sample_size = self.DEFAULT_SAMPLE_SIZE

        self.csvkit_enabled = inquirer.confirm(
            message="Enable csvkit?",
            default=True
        ).execute()

        print(f"\n✓ Configuration complete:")
        print(f"  Data dir: {self.data_dir}")
        print(f"  Report: {self.report_file}")
        print(f"  Sample size: {self.sample_size} bytes")
        print(f"  csvkit: {'enabled' if self.csvkit_enabled else 'disabled'}\n")

    def run_profile(self):
        """Run the profiling process."""
        if not self.data_dir.exists():
            logger.error(f"Directory not found: {self.data_dir}")
            print(f"❌ Error: Directory '{self.data_dir}' does not exist")
            input("Press Enter to continue...")
            return

        csv_files = list(self.data_dir.rglob("*.csv"))

        if not csv_files:
            logger.warning(f"No CSV files found in {self.data_dir}")
            print(f"⚠️  No CSV files found in {self.data_dir}")
            input("Press Enter to continue...")
            return

        print(f"\nFound {len(csv_files)} CSV file(s). Starting profile...\n")

        all_records = []
        for csv_file in csv_files:
            try:
                record = self.profile_file(csv_file)
                all_records.append(record)
            except Exception as e:
                logger.error(f"Failed profiling {csv_file}: {e}")
                print(f"❌ Failed: {csv_file.name} - {e}")

        if not all_records:
            logger.error("No files were successfully profiled")
            print("\n❌ No files were successfully profiled")
            input("Press Enter to continue...")
            return

        try:
            df = pl.DataFrame(all_records)
            df.write_parquet(self.report_file)
            logger.info(f"Report written to {self.report_file}")
            print(f"\n✅ Report written to {self.report_file}")
            print(f"   Profiled {len(all_records)} file(s)")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
            print(f"\n❌ Failed to write report: {e}")

        input("\nPress Enter to continue...")

    def quick_profile(self):
        """Quick profile with current settings."""
        print("\nUsing current settings:")
        print(f"  Data dir: {self.data_dir}")
        print(f"  Report: {self.report_file}\n")
        self.run_profile()

    def show_current_config(self):
        """Display current configuration."""
        print("\n=== Current Configuration ===")
        print(f"Data directory: {self.data_dir}")
        print(f"Report file: {self.report_file}")
        print(f"Sample size: {self.sample_size} bytes")
        print(f"csvkit: {'enabled' if self.csvkit_enabled else 'disabled'}")
        print(f"============================\n")
        input("Press Enter to continue...")


class CSVProfilerModule(MenuModule):
    """CSV Profiler menu module."""

    def __init__(self):
        self.service = CSVProfilerService()

    @property
    def name(self) -> str:
        return "CSV Profiler"

    def items(self) -> List[MenuItem]:
        return [
            MenuItem(
                id="quick",
                label="Quick Profile (current settings)",
                handler=self.service.quick_profile
            ),
            MenuItem(
                id="config",
                label="Configure Settings",
                handler=self.service.configure
            ),
            MenuItem(
                id="profile",
                label="Profile CSVs",
                handler=self.service.run_profile
            ),
            MenuItem(
                id="show",
                label="Show Current Config",
                handler=self.service.show_current_config
            ),
        ]
