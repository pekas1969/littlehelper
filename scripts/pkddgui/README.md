# pkddgui.py

`pkddgui.py` is a Python-based graphical user interface that facilitates disk imaging and cloning operations using the `dd` command-line utility.

## Features

- **Disk/Partition to Image**: Create an image file from a selected disk or partition.
- **Image to Disk/Partition**: Restore a disk or partition from an image file.
- **Disk to Disk Cloning**: Clone one disk directly to another.
- **Dry Run Mode**: Preview the `dd` command without executing it.
- **Progress Monitoring**: Visual feedback during operations.
- **Safety Confirmation**: Prompt before executing potentially destructive actions.

## Usage

1. Run the script:

   ```bash
   python pkddgui.py
