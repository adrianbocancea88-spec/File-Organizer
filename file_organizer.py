#!/usr/bin/env python3
"""
File Organizer Application

Scans a selected folder and moves each top-level file into one of these
automatically created folders: Images, PDF, Excel, Word, Videos, and Others.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Iterator


CATEGORY_EXTENSIONS: dict[str, set[str]] = {
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".heic",
        ".svg",
    },
    "PDF": {".pdf"},
    "Excel": {".xls", ".xlsx", ".xlsm", ".xlsb", ".ods", ".csv"},
    "Word": {".doc", ".docx", ".docm", ".dot", ".dotx", ".odt", ".rtf"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"},
}

CATEGORY_NAMES: tuple[str, ...] = ("Images", "PDF", "Excel", "Word", "Videos", "Others")
LOG_FILE_NAME = "file_organizer.log"


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the application."""
    parser = argparse.ArgumentParser(
        description="Organize files in a selected folder by file type."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        help="Folder to organize. If omitted, a folder picker or prompt is shown.",
    )
    return parser.parse_args()


def prompt_for_folder() -> str | None:
    """
    Ask the user to select a folder.

    A native folder picker is used when Tkinter is available. If the picker is
    cancelled or cannot open, the user can type the folder path in the terminal.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected_folder = filedialog.askdirectory(title="Select a folder to organize")
        root.destroy()

        if selected_folder:
            return selected_folder
    except Exception:
        # Console fallback keeps the app usable in environments without a GUI.
        pass

    entered_folder = input("Enter the folder path to organize: ").strip()
    return entered_folder or None


def get_selected_folder(folder_argument: str | None) -> Path:
    """Return a validated folder path from an argument, dialog, or prompt."""
    selected_folder = folder_argument or prompt_for_folder()

    if not selected_folder:
        raise ValueError("No folder was selected.")

    folder_path = Path(selected_folder).expanduser().resolve()

    if not folder_path.exists():
        raise FileNotFoundError(f"The folder does not exist: {folder_path}")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"The selected path is not a folder: {folder_path}")

    return folder_path


def create_category_folders(base_folder: Path) -> dict[str, Path]:
    """Create and return the category folders used by the organizer."""
    category_folders: dict[str, Path] = {}

    for category_name in CATEGORY_NAMES:
        category_folder = base_folder / category_name
        if category_folder.exists() and not category_folder.is_dir():
            raise FileExistsError(
                f"Cannot create category folder because a file already exists: {category_folder}"
            )

        category_folder.mkdir(exist_ok=True)
        category_folders[category_name] = category_folder

    return category_folders


def configure_logger(log_file: Path) -> logging.Logger:
    """Configure a file logger that records each organizer run."""
    logger = logging.getLogger("file_organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_category_for_file(file_path: Path) -> str:
    """Return the destination category name for a file."""
    file_extension = file_path.suffix.lower()

    for category_name, extensions in CATEGORY_EXTENSIONS.items():
        if file_extension in extensions:
            return category_name

    return "Others"


def get_available_destination_path(destination_path: Path) -> Path:
    """
    Return a destination path that does not overwrite an existing file.

    Example: report.pdf becomes report (1).pdf when report.pdf already exists.
    """
    if not destination_path.exists():
        return destination_path

    parent = destination_path.parent
    stem = destination_path.stem
    suffix = destination_path.suffix
    copy_number = 1

    while True:
        candidate_path = parent / f"{stem} ({copy_number}){suffix}"

        if not candidate_path.exists():
            return candidate_path

        copy_number += 1


def iter_files_to_organize(base_folder: Path, log_file: Path) -> Iterator[Path]:
    """Yield top-level files from the selected folder, excluding the log file."""
    log_file = log_file.resolve()

    for item in base_folder.iterdir():
        if item.is_file() and item.resolve() != log_file:
            yield item


def move_file(file_path: Path, category_folders: dict[str, Path], logger: logging.Logger) -> bool:
    """Move one file to its category folder and return whether it was moved."""
    category_name = get_category_for_file(file_path)
    destination_folder = category_folders[category_name]
    destination_path = get_available_destination_path(destination_folder / file_path.name)

    try:
        shutil.move(str(file_path), str(destination_path))
    except OSError as error:
        logger.exception("Failed to move '%s': %s", file_path, error)
        return False

    if destination_path.name == file_path.name:
        logger.info("Moved '%s' to '%s'.", file_path, destination_path)
    else:
        logger.info(
            "Moved '%s' to '%s' and renamed it to avoid a duplicate file name.",
            file_path,
            destination_path,
        )

    return True


def organize_folder(base_folder: Path) -> int:
    """
    Organize files in the selected folder and return the number of moved files.

    The scan is intentionally non-recursive: existing subfolders are left alone.
    """
    log_file = base_folder / LOG_FILE_NAME
    logger = configure_logger(log_file)

    logger.info("Started organizing folder: %s", base_folder)
    category_folders = create_category_folders(base_folder)

    moved_count = 0
    for file_path in iter_files_to_organize(base_folder, log_file):
        if move_file(file_path, category_folders, logger):
            moved_count += 1

    logger.info("Finished organizing folder. Files moved: %s", moved_count)
    return moved_count


def main() -> int:
    """Run the file organizer application."""
    try:
        arguments = parse_arguments()
        selected_folder = get_selected_folder(arguments.folder)
        moved_count = organize_folder(selected_folder)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Organization complete. Files moved: {moved_count}")
    print(f"Log file created at: {selected_folder / LOG_FILE_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
