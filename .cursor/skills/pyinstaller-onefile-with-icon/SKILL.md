---
name: pyinstaller-onefile-with-icon
description: Adds a single-file executable build for Python desktop apps using PyInstaller with an optional generated icon. Use when the user wants one .exe (no extra files), a build script runnable from the IDE, and/or an icon for the executable.
---

# PyInstaller one-file build with icon

Use when the user wants: a **single .exe** (onefile), a **build script** they can Run from PyCharm (no commands), and an **icon** for the executable (generated or existing).

## Steps

### 1. Entry script at project root

Add `run.py` at the repo root so PyInstaller has one script to trace:

```python
"""Launcher for PyInstaller one-file build."""
from your_package.gui.main_window import main  # or wherever main() lives

if __name__ == "__main__":
    main()
```

### 2. Build-time requirements

Add `requirements-build.txt`:

```
pyinstaller>=6.0.0
Pillow>=10.0.0
```

User runs: `pip install -r requirements.txt -r requirements-build.txt` once.

### 3. Icon generation (optional)

Add `build_icon.py` that uses Pillow to draw and save an `.ico` (e.g. 256, 48, 32, 16). Save to `app.ico` in the project root. If the user prefers an existing icon, skip generation and point the spec at their `.ico`.

### 4. Spec file (onefile + icon)

Create `your_app.spec` (or reuse a name like `whatsapp_archive.spec`):

- **Analysis**: `script = ['run.py']`, `pathex=[os.curdir]`, add `hiddenimports` for the main package and GUI stack (e.g. `PySide6.QtCore`, `PySide6.QtGui`, `PySide6.QtWidgets`).
- **EXE**: `onefile=True` (no `COLLECT`), `console=False` for GUI apps, `icon='app.ico'` (or `None` if missing). Use `icon='app.ico' if os.path.isfile('app.ico') else None` so build works without an icon.

### 5. Build script

Add `build.py` at project root:

1. Generate icon: call `build_icon.generate_icon(Path('app.ico'))` (or skip if using existing icon). Catch errors so build can proceed without Pillow/icon.
2. Run PyInstaller: `subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', 'whatsapp_archive.spec'], cwd=ROOT)`.
3. Print the path to the produced exe (e.g. `dist/WhatsAppArchive.exe`).

User runs **build.py** from the IDE (e.g. PyCharm Run). Output is a single `.exe` in `dist/`.

## Checklist

- [ ] `run.py` imports and calls the app entry (e.g. `main()`).
- [ ] `requirements-build.txt` has `pyinstaller` and `Pillow` (if generating icon).
- [ ] Spec uses `run.py`, `pathex=[os.curdir]`, `hiddenimports` for package and Qt/GUI.
- [ ] EXE section has `onefile=True`, `console=False` for GUI, `icon='app.ico'` or conditional.
- [ ] `build.py` generates icon (if desired) then runs PyInstaller; handles missing icon/Pillow.

## Notes

- **Onefile** = one .exe; first startup can be slower (unpacking). For faster startup or easier debugging, use onedir (folder) instead.
- **Icon**: Generate with Pillow (build_icon.py) or supply an existing `.ico`; spec references it by path from project root.
