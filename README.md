# 📤 Transfer.it CLI

A command-line tool to upload files to [Transfer.it](https://transfer.it) and get download links automatically.

## ✨ Features

- Upload single or multiple files
- Multiple files can be uploaded as a single link or separate links
- Progress tracking (10% increments)
- Automatic download link retrieval
- Links saved to `.link.txt` files
- Supports large files (tested with 10GB+)
- Headless browser automation (runs in background)

## 📦 Installation

### Prerequisites
- Python 3.7+

### Setup

```bash
# Clone the repository
git clone https://github.com/propjoe-tr/transfer-it.git
cd transfer-it

# Install dependencies
pip install -r requirements.txt

# Install Chromium browser
playwright install chromium
```

## 🚀 Usage

### Single File
```bash
python transferit.py myfile.zip
```

### Multiple Files (Single Link)
All files will be bundled under one download link:
```bash
python transferit.py file1.zip file2.pdf file3.mp4
```

### Multiple Files (Separate Links)
Each file gets its own download link:
```bash
python transferit.py --separate file1.zip file2.pdf file3.mp4
```

## 📋 Output Example

```
============================================================
[*] Transfer.it Upload Tool
============================================================
[*] Total files: 2
[*] Mode: All files under single link
============================================================

[*] Browser starting...

------------------------------------------------------------
[*] Total 2 files will be uploaded together
[*] Total size: 1.50 GB (1536.00 MB)
------------------------------------------------------------
  1. video.mp4 (1024.00 MB)
  2. document.pdf (512.00 MB)
------------------------------------------------------------

[*] Connecting to Transfer.it...
[*] Selecting files...
[*] Starting transfer...
[*] Upload in progress...

   [*] Progress: 10% | Elapsed: 1m 30s
   [*] Progress: 20% | Elapsed: 3m 0s
   ...
   [+] Progress 100% - Upload complete!

[+] Upload complete!
[*] Waiting for link button...
[*] Getting link...
[+] Link received!
[*] https://transfer.it/t/abc123xyz
[+] Link saved: multiple_files_1234567890.link.txt

============================================================
[*] SUMMARY
============================================================
[+] Success: All files uploaded

[*] Download Link:
    https://transfer.it/t/abc123xyz
============================================================
```

## 📁 Link Files

After each upload, a `.link.txt` file is created with details:

**Single file:** `filename.ext.link.txt`
```
File: video.mp4
Size: 1024.00 MB
Link: https://transfer.it/t/abc123xyz
Date: 2026-01-16 21:30:45
```

**Multiple files:** `multiple_files_timestamp.link.txt`
```
Total files: 3
Total size: 2.50 GB
Link: https://transfer.it/t/abc123xyz
Date: 2026-01-16 21:30:45

Files:
  1. video.mp4 (1024.00 MB)
  2. document.pdf (512.00 MB)
  3. image.png (1024.00 MB)
```

## ⚙️ How It Works

This tool uses [Playwright](https://playwright.dev/) for browser automation to:

1. Open Transfer.it in a headless Chromium browser
2. Select and upload files
3. Monitor upload progress via console logs
4. Wait for completion
5. Extract the download link
6. Save link to a text file

Transfer.it uses MEGA.nz infrastructure for file storage with client-side encryption.

## 📝 Requirements

- `playwright` - Browser automation

See `requirements.txt` for details.

## ⚠️ Limitations

- Requires internet connection
- Upload speed depends on your connection
- File size limits depend on Transfer.it's policies
- Links expire according to Transfer.it's retention policy

## 🔧 Troubleshooting

### "Chromium not found"
```bash
playwright install chromium
```

### "pip not recognized"
```bash
python -m pip install -r requirements.txt
```

### Upload stuck
- Check your internet connection
- Try with a smaller file first
- Run with visible browser for debugging (change `headless=True` to `headless=False` in code)

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## ⚡ Disclaimer

This tool is for educational purposes. Please respect Transfer.it's terms of service and use responsibly.

---
