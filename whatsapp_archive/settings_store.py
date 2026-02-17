"""Load/save user preferences to a JSON file in app data directory."""
import json
import os
from pathlib import Path

from whatsapp_archive.config import COMMON_TIMEZONES, DEFAULT_TIMEZONE, WHISPER_MODELS

# App data dir: e.g. %APPDATA%/WhatsAppArchiveBuilder on Windows
if os.name == "nt":
    _CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "WhatsAppArchiveBuilder"
else:
    _CONFIG_DIR = Path.home() / ".config" / "WhatsAppArchiveBuilder"

_CONFIG_FILE = _CONFIG_DIR / "settings.json"


def _defaults():
    return {
        "theme_dark": False,
        "lang": "en",
        "timezone_key": DEFAULT_TIMEZONE,
        "whisper_model_index": max(0, len(WHISPER_MODELS) - 1),
        "last_directory": str(Path.home()),
        "window_x": 100,
        "window_y": 100,
        "window_width": 650,
        "window_height": 600,
    }


def load_settings():
    """Load settings from disk. Returns a dict; missing keys use defaults."""
    defaults = _defaults()
    if not _CONFIG_FILE.exists():
        return defaults
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return defaults


def save_settings(settings: dict):
    """Write settings to disk. Only known keys are persisted."""
    defaults = _defaults()
    to_save = {k: settings.get(k, v) for k, v in defaults.items()}
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, indent=2)
