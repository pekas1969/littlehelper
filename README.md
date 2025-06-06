# System Administration Helper Scripts

This repository is a curated collection of useful scripts for system administration tasks. The goal is to provide tools that simplify and automate common administrative operations.

## Scripts

Installer:
- **install_littlehelper.py**: The main install script.

Console tools:
- **pk_init_git_repo.sh**: A simple Bash script to quickly initialize a local Git repository.
- **pksendmail.py**: A simple script to send emails via console, supports multiple accounts

Graphical tools:
- **pkddgui.py**: A graphical user interface for disk imaging and cloning operations using `dd`.
- **pkmangui.py**: A simple Manpage Viewer built with Python and PyQt6.

## Installation

You can either use the installer to manage the scripts, or manually copy individual ones.

### 🔧 Option 1: Install via `install_littlehelper.py`

1. Make sure you have **Python 3.7+**, **pip** and **pyyaml termcolor requests** installed.
   Otherwise install Python and python-pip (or python3-pip, depends on your distribution) first, then
   ```bash
   pip install pyyaml termcolor requests
   ```
2. Download and run the install script from this repository:
   ```bash
   python3 install_littlehelper.py
   ```
3. The installer will:
   - Download the list of available scripts from GitHub.
   - Compare them with locally installed versions.
   - Offer you the option to install, update, or uninstall scripts.
   - Ask whether to install globally (`/usr/local/bin`) or for the current user (`~/.local/bin`).

📌 **Important:**
- For GUI scripts like `pkddgui.py` and `pkmangui.py`, make sure `PyQt6` is installed:
   ```bash
   pip install PyQt6
   ```
- The installer checks the version from the script's first line (`#version=...`) and compares it to the version in `scripts.yaml`.

### 📁 Option 2: Manual Installation

You can manually install scripts from the `scripts/` subfolders in the repository:

1. Navigate to the desired script's folder (e.g., `scripts/pkmangui/`).
2. Copy the main script (e.g., `pkmangui.py`) to your desired path:
   ```bash
   cp pkddgui.py ~/.local/bin/
   chmod +x ~/.local/bin/pkddgui.py
   ```
3. Make sure the target directory is in your `PATH`.

💡 **Note:**
- The install script assumes manually installed scripts are located in:
   - `~/.local/bin` (user installation)
   - `/usr/local/bin` (system-wide installation)
- It uses these paths to detect installed scripts for version comparison and uninstallation.

## Contact

Peter Kasparak  
[peter.kasparak@gmail.com](mailto:peter.kasparak@gmail.com)
