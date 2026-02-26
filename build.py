"""
Build a single .exe with PyInstaller (onefile) and a generated icon.
Run from project root (e.g. from PyCharm: Run build.py).
Output: dist/WhatsAppArchive.exe (or dist/WhatsApp Chat Archive.exe)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = ROOT / "whatsapp_archive.spec"
ICON = ROOT / "app.ico"


def main() -> None:
    # 1. Generate icon if Pillow is available
    if not ICON.exists() or " regen" in " ".join(sys.argv).lower():
        try:
            from build_icon import generate_icon
            generate_icon(ICON)
            print("Generated", ICON)
        except Exception as e:
            print("Icon generation skipped:", e)
            if not ICON.exists():
                print("Run: pip install Pillow  then run build.py again for an icon.")

    # 2. Run PyInstaller
    if not SPEC.exists():
        print("Missing", SPEC)
        sys.exit(1)
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", str(SPEC)]
    print("Running:", " ".join(cmd))
    r = subprocess.run(cmd, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(r.returncode)
    exe = ROOT / "dist" / "WhatsAppArchive.exe"
    if exe.exists():
        print("Done. Executable:", exe)
    else:
        print("Build finished. Check dist/ for the executable.")


if __name__ == "__main__":
    main()
