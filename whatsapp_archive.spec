# PyInstaller spec: single .exe (onefile), with icon.
# Run:  python build.py   (or:  pyinstaller whatsapp_archive.spec)

import os

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[os.curdir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'whatsapp_archive',
        'whatsapp_archive.gui.main_window',
        'whatsapp_archive.gui.worker',
        'whatsapp_archive.html_builder.builder',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WhatsAppArchive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico' if os.path.isfile('app.ico') else None,
)
