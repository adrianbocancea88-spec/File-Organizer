# File Organizer

A professional Python command-line application that organizes files inside a selected folder by file type.

## Features

- Scans a selected folder
- Creates these folders automatically:
  - `Images`
  - `PDF`
  - `Excel`
  - `Word`
  - `Videos`
  - `Others`
- Moves files into the correct folder
- Displays how many files were moved
- Creates a log file named `file_organizer.log`
- Handles duplicate file names safely
- Uses clean, function-based Python code

## Requirements

- Python 3.10 or newer
- No external Python packages are required

## Installation

No package installation is needed because the application uses only Python's standard library.

If you still want to run the requirements command, use:

```powershell
pip install -r requirements.txt
```

## Usage

Run the application and pass the folder you want to organize:

```powershell
python file_organizer.py "C:\Path\To\Your\Folder"
```

You can also run the application without a folder path:

```powershell
python file_organizer.py
```

When no folder path is provided, the app opens a folder picker when possible. If a folder picker is not available, it asks you to type the folder path.

## Example

Before organizing:

```text
Downloads
├── photo.jpg
├── invoice.pdf
├── report.docx
├── budget.xlsx
├── movie.mp4
└── notes.txt
```

After organizing:

```text
Downloads
├── Images
│   └── photo.jpg
├── PDF
│   └── invoice.pdf
├── Word
│   └── report.docx
├── Excel
│   └── budget.xlsx
├── Videos
│   └── movie.mp4
├── Others
│   └── notes.txt
└── file_organizer.log
```

## Duplicate File Handling

The application never overwrites existing files. If a file with the same name already exists in the destination folder, the moved file is renamed automatically.

Example:

```text
report.pdf
report (1).pdf
report (2).pdf
```

## Log File

Each run creates or updates this log file inside the selected folder:

```text
file_organizer.log
```

The log records when the organizer starts, which files were moved, duplicate renames, errors, and the final moved-file count.

## Notes

The scan is non-recursive. The app organizes files directly inside the selected folder and does not move files that are already inside subfolders.
