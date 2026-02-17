"""Constants, version, and default settings."""
VERSION = "v2.0.1"

# File extensions
AUDIO_EXTENSIONS = (".mp3", ".m4a", ".ogg", ".opus", ".wav", ".aac")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".webm")

# Default timezone for parsing chat dates (user can override via settings)
DEFAULT_TIMEZONE = "America/New_York"

# Common timezones for the picker: (display_label, pytz key)
COMMON_TIMEZONES = [
    ("Eastern (US/Canada)", "America/New_York"),
    ("Central (US/Canada)", "America/Chicago"),
    ("Pacific (US/Canada)", "America/Los_Angeles"),
    ("UTC", "UTC"),
    ("Paris", "Europe/Paris"),
    ("London", "Europe/London"),
    ("Lomé / Lagos", "Africa/Lagos"),
    ("Johannesburg", "Africa/Johannesburg"),
    ("India", "Asia/Kolkata"),
    ("Tokyo", "Asia/Tokyo"),
]

# Whisper model options: (display_name, load_name_for_download, local_file_name or None)
WHISPER_MODELS = [
    ("Tiny (fastest, least accurate)", "tiny", None),
    ("Base", "base", None),
    ("Small", "small", None),
    ("Medium", "medium", None),
    ("Large (best, slowest)", "large", "large-v3.pt"),
]
