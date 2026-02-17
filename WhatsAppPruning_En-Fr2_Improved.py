#!/usr/bin/env python3
"""
WhatsApp Chat to HTML Converter – Whisper Edition (launcher).
Run this file or use: python -m whatsapp_archive
"""
import sys

# Optional: ensure optional deps are present before loading the package
try:
    import pytz
except ImportError:
    print("Error: 'pytz' library not found.")
    print("Please install it by running: pip install pytz")
    sys.exit(1)

try:
    from Crypto.Cipher import AES  # noqa: F401
    from Crypto.Random import get_random_bytes  # noqa: F401
except ImportError:
    print("Error: 'pycryptodome' library not found.")
    print("Please install it by running: pip install pycryptodome")
    sys.exit(1)

from whatsapp_archive.gui.main_window import main

if __name__ == "__main__":
    main()
